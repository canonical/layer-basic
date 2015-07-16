# Copyright 2014-2015 Canonical Limited.
#
# This file is part of charm-helpers.
#
# charm-helpers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3 as
# published by the Free Software Foundation.
#
# charm-helpers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import subprocess
from distutils.util import strtobool
from imp import load_source

from charmhelpers.core import hookenv
from charmhelpers.core import unitdata
from charmhelpers.cli import cmdline


REACTIVE_LOG_INVOKE = strtobool(os.environ.get('REACTIVE_LOG_INVOKE', 'False'))
IN_DISPATCH = False
STATE_QUEUE = {
    'set': {},
    'remove': [],
}


@cmdline.subcommand()
@cmdline.no_output
def set_state(state, value=None):
    """Set the given state as active, optionally associating with a relation"""
    STATE_QUEUE['set'][state] = value
    if not IN_DISPATCH:
        _commit_states()


@cmdline.subcommand()
@cmdline.no_output
def remove_state(state):
    """Remove / deactivate a state"""
    STATE_QUEUE['remove'].append(state)
    if not IN_DISPATCH:
        _commit_states()


def _commit_states():
    unitdata.kv().update(STATE_QUEUE['set'], prefix='reactive.states.')
    unitdata.kv().unsetrange(STATE_QUEUE['remove'], prefix='reactive.states.')
    STATE_QUEUE['set'] = {}
    STATE_QUEUE['remove'] = []


@cmdline.subcommand()
def get_states():
    """Return a mapping of all active states to their values"""
    return unitdata.kv().getrange('reactive.states.', strip=True) or {}


def get_state(state, default=None):
    """Return the value associated with an active state, or None"""
    return unitdata.kv().get('reactive.states.%s' % state, default)


@cmdline.subcommand()
@cmdline.test_command
def all_states(*desired_states):
    """Assert that all desired_states are active"""
    active_states = get_states()
    return all(state in active_states for state in desired_states)


@cmdline.subcommand()
@cmdline.test_command
def any_states(*desired_states):
    """Assert that any of the desired_states are active"""
    active_states = get_states()
    return any(state in active_states for state in desired_states)


@cmdline.subcommand()
@cmdline.test_command
def any_hook(*hook_patterns):
    """
    Assert that the currently executing hook matches one of the given patterns.

    Each pattern will match one or more hooks, and can use the following
    special syntax:

      * ``db-relation-{joined,changed}`` can be used to match multiple hooks
        (in this case, ``db-relation-joined`` and ``db-relation-changed``).
      * ``{provides:mysql}-relation-joined`` can be used to match a relation
        hook by the role and interface instead of the relation name.  The role
        must be one of ``provides``, ``requires``, or ``peer``.
      * The previous two can be combined, of course: ``{provides:mysql}-relation-{joined,changed}``
    """
    current_hook = hookenv.hook_name()

    # expand {role:interface} patterns
    i_pat = re.compile(r'{([^:}]+):([^}]+)}')
    hook_patterns = _expand_replacements(i_pat, hookenv.role_and_interface_to_relations, hook_patterns)

    # expand {A,B,C,...} patterns
    c_pat = re.compile(r'{((?:[^:,}]+,?)+)}')
    hook_patterns = _expand_replacements(c_pat, lambda v: v.split(','), hook_patterns)

    return current_hook in hook_patterns


def _expand_replacements(pat, subf, values):
    while any(pat.search(r) for r in values):
        new_values = []
        for value in values:
            m = pat.search(value)
            if not m:
                new_values.append(value)
                continue
            whole_match = m.group(0)
            selected_groups = m.groups()
            for replacement in subf(*selected_groups):
                # have to replace one match at a time, or we'll lose combinations
                # e.g., '{A,B}{A,B}' would turn to ['AA', 'BB'] instead of
                # ['A{A,B}', 'B{A,B}'] -> ['AA', 'AB', 'BA', 'BB']
                new_values.append(value.replace(whole_match, replacement, 1))
        values = new_values
    return values


class Handler(object):
    """
    Class representing a reactive state handler.
    """
    _HANDLERS = []

    def __init__(self, predicate, action, args_source=None):
        """
        Create a new Handler.

        :param func predicate: The predicate to call to determine if the Handler
            should be invoked
        :param func action: Callback that is called when invoking the Handler
        :param func args_source: Optional callback that generates args for the action
        """
        self.predicate = predicate
        self.action = action
        self.args_source = args_source

    def _invocation_id(self):
        return "%s:%s:%s" % (self.action.__code__.co_filename,
                             self.action.__code__.co_firstlineno,
                             self.action.__code__.co_name)

    def invoke(self):
        """
        Conditionally invoke the handler, assuming its predicate passes and it
        has not been invoked during the current dispatch.
        """
        args = list(self.args_source()) if self.args_source else []
        _id = self._invocation_id()
        if not was_invoked(_id) and self.predicate():
            self.action(*args)
            set_invoked(_id)

    @classmethod
    def register(cls, predicate, action, args_source=None):
        "Register a handler with the given predicate and action."
        cls._HANDLERS.append(cls(predicate, action, args_source))

    @classmethod
    def get_handlers(cls):
        "Retrieve a copy of the list of currently registered Handlers."
        return list(cls._HANDLERS)

    @classmethod
    def clear(cls):
        "Clear all currently registered Handlers."
        cls._HANDLERS = []

    @classmethod
    def decorator(cls, predicate, args_source=None):
        """
        Register the decorated action with the given predicate and optional args.

        If ``args_source`` is given, it will be called just prior to invoking
        the action and should return a list which will be passed to the action
        as positional arguments.
        """
        def _decorator(action):
            cls.register(predicate, action, args_source)
            return action
        return _decorator


class ReinvokingHandler(Handler):
    """
    A variant Handler that reinvokes any time the predicate passes, even if
    it has been invoked previously during the current dispatch.
    """
    def invoke(self):
        """
        Conditionally invoke the handler, assuming its predicate passes.
        """
        args = list(self.args_source()) if self.args_source else []
        if self.predicate():
            self.action(*args)


class ExternalHandler(ReinvokingHandler):
    """
    A variant Handler for external executable actions (such as bash scripts),
    which also does not perform any reinvocation gating checks.
    """
    def __init__(self, filepath):
        self.args_source = lambda: []  # no args
        self.predicate = lambda: True  # always invoke
        self.filepath = filepath

    def action(self):
        """
        Execute the external handler, which should perform its own predicate
        and reinvocation checking.
        """
        # flush to ensure external process can see states as they currently
        # are, and write states (flush releases lock)
        unitdata.kv().flush()
        subprocess.check_call([self.filepath], env=os.environ)

    @classmethod
    def register(cls, filepath):
        "Register a handler with the given predicate and action."
        Handler._HANDLERS.append(ExternalHandler(filepath))


def stable_state():
    """
    Returns a generator that returns True until the set of invoked reactive
    handlers is unchanged between two subsequent calls.
    """
    old_invoked = None
    while True:
        invoked = unitdata.kv().getrange('reactive.invoked.') or {}
        new_invoked = set(invoked.keys())
        yield new_invoked == old_invoked
        old_invoked = new_invoked


def was_invoked(handler_id):
    """
    Check whether a handler has already been invoked during this
    run of :func:`dispatch`.

    :param str handler_id: An ID for this handler, which is unique to the
        handler but persistent across calls.
    """
    key = 'reactive.invoked.%s' % handler_id
    return unitdata.kv().get(key, False)


def set_invoked(handler_id):
    """
    Indicate that a handler has been invoked.

    :param str handler_id: An ID for this handler, which is unique to the
        handler but persistent across calls.
    """
    if REACTIVE_LOG_INVOKE:
        hookenv.log('Reactive handler invoked: %s' % handler_id)
    key = 'reactive.invoked.%s' % handler_id
    unitdata.kv().set(key, True)


def _clear_invoked():
    unitdata.kv().unsetrange(prefix='reactive.invoked.')


def dispatch():
    """
    Dispatch any registered handlers.
    """
    global IN_DISPATCH
    IN_DISPATCH = True
    stable = stable_state()
    while not next(stable):
        for handler in Handler.get_handlers():
            handler.invoke()
        _commit_states()
    _clear_invoked()
    IN_DISPATCH = False


def discover():
    """
    Discover handlers based on convention.

    Handlers can be decorated functions in Python files, or they can be
    executables which use the CLI to interact with the state.  Any files
    under ``$CHARM_DIR/hooks/reactive/`` and ``$CHARM_DIR/hooks/relations/``
    (recursively) will be considered.

    Note that executables may be invoked multiple times for a given call
    to :func:`dispatch`.  Thus, they should use :func:`was_invoked` and
    :func:`set_invoked` (or the Bash helpers in ``reactive.sh``) to gate
    blocks of code that should only be triggered once.
    """
    for search_dir in ('relations', 'reactive'):
        search_path = os.path.join(hookenv.charm_dir(), 'hooks', search_dir)
        for dirpath, dirnames, filenames in os.walk(search_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                _register_handlers_from_file(filepath)


def _register_handlers_from_file(filepath):
    if filepath.endswith('.py'):
        modname = 'juju_%s' % filepath.replace('/', '_').replace('.py', '')
        if modname not in sys.modules:
            load_source(modname, filepath)
    elif os.access(filepath, os.X_OK):
        ExternalHandler.register(filepath)
