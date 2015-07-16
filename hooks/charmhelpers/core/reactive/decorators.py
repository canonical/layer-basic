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

from functools import wraps

from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import unitdata
from charmhelpers.cli import cmdline
from charmhelpers.core.reactive.bus import Handler
from charmhelpers.core.reactive.bus import ReinvokingHandler
from charmhelpers.core.reactive.bus import any_hook
from charmhelpers.core.reactive.bus import all_states
from charmhelpers.core.reactive.bus import get_states
from charmhelpers.core.reactive.bus import was_invoked
from charmhelpers.core.reactive.bus import set_invoked
from charmhelpers.core.reactive.relations import RelationBase


def hook(*hook_patterns):
    """
    Register the decorated function to run when the current hook matches any of
    the ``hook_patterns``.

    The hook patterns can use the ``{interface:...}`` and ``{A,B,...}`` syntax
    supported by `any_hook`.

    If the hook is a relation hook, an instance of that relation class will be
    passed in to the decorated function.

    For example, to match any joined or changed hook for any relation using the
    ``mysql`` interface::

        class MySQLRelation(RelationBase):
            @hook('{interface:mysql}-relation-{joined,changed}')
            def joined_or_changed(self):
                pass

    This can be used from Bash using the ``reactive.sh`` helpers::

        source `which reactive.sh`

        hook '{interface:mysql}-relation-{joined,changed}'; then
            chlp relation_call $JUJU_RELATION handle_relation
        kooh

    The Bash helper uses the `any_hook` ``chlp`` command, and the above is
    exactly equivalent to::

        source `which reactive.sh`

        if chlp any_hook '{interface:mysql}-relation-{joined,changed}'; then
            chlp relation_call $JUJU_RELATION handle_relation
        kooh
    """
    return Handler.decorator(
        lambda: any_hook(*hook_patterns),
        lambda: filter(None, [RelationBase.from_name(hookenv.relation_type())]))


@cmdline.subcommand()
@cmdline.test_command
def hook_cli(block_id, *hook_patterns):
    """
    CLI version of the hook decorator.
    """
    if not was_invoked(block_id) and any_hook(*hook_patterns):
        set_invoked(block_id)
        return True
    return False


def when(*desired_states):
    """
    Register the decorated function to run when all ``desired_states`` are active.

    If a state is associated with a relation, an instance of that relation
    class will be passed in to the decorated function.

    This can be used from Bash using the ``reactive.sh`` helpers::

        source `which reactive.sh`

        when db.ready cache.ready; then
            db_dsn=$(state_relation_call db.ready uri)
            cache_uri=$(state_relation_call cache.ready uri)
            chlp render_template db_dsn=$db_dsn cache_uri=$cache_uri
        nehw

    The Bash helper uses the :func:`when_cli` ``chlp`` command, and the above is
    exactly equivalent to::

        source `which reactive.sh`

        if chlp when_cli db.ready cache.ready; then
            db_dsn=$(state_relation_call db.ready uri)
            cache_uri=$(state_relation_call cache.ready uri)
            chlp render_template db_dsn=$db_dsn cache_uri=$cache_uri
        fi
    """
    return Handler.decorator(
        lambda: all_states(*desired_states),
        lambda: filter(None, map(RelationBase.from_state, desired_states)))


@cmdline.subcommand()
@cmdline.test_command
def when_cli(block_id, *desired_states):
    """
    CLI version of the when decorator.

    Evaluates to true (exit 0) if all of the ``desired_states`` are active,
    as per :func:`~charmhelpers.core.reactive.bus.all_states`, and if it
    has not evaluated to true for the given ``block_id`` already for this
    round of dispatch.

    :param str block_id: Any unique identifier for the block, such as the
        filename and line number of the start of the block.
    :param list desired_states: List of states that should be active.
    """
    if not was_invoked(block_id) and all_states(*desired_states):
        set_invoked(block_id)
        return True
    return False


def when_not(*desired_states):
    """
    Register the decorated function to run when **not** all desired_states are active.

    If a state is associated with a relation, an instance of that relation
    class will be passed in to the decorated function.

    This can be used from Bash using the ``reactive.sh`` helpers::

        source `which reactive.sh`

        when_not db.ready cache.ready; then
            db_dsn=$(state_relation_call db.ready uri)
            cache_uri=$(state_relation_call cache.ready uri)
            chlp render_template db_dsn=$db_dsn cache_uri=$cache_uri
        nehw

    The Bash helper uses the `all_states` ``chlp`` command, and the above is
    exactly equivalent to::

        source `which reactive.sh`

        if ! chlp all_states db.ready cache.ready; then
            db_dsn=$(state_relation_call db.ready uri)
            cache_uri=$(state_relation_call cache.ready uri)
            chlp render_template db_dsn=$db_dsn cache_uri=$cache_uri
        fi
    """
    return Handler.decorator(lambda: not all_states(*desired_states))


@cmdline.subcommand()
@cmdline.test_command
def when_not_cli(block_id, *desired_states):
    """
    CLI version of the when_not decorator.
    """
    if not was_invoked(block_id) and not all_states(*desired_states):
        set_invoked(block_id)
        return True
    return False


def not_until(*desired_states):
    def _decorator(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            active_states = get_states()
            missing_states = [state for state in desired_states if state not in active_states]
            if missing_states:
                func_id = "%s:%s:%s" % (func.__code__.co_filename,
                                        func.__code__.co_firstlineno,
                                        func.__code__.co_name)
                hookenv.log('%s called before state%s: %s' % (
                    func_id,
                    's' if len(missing_states) > 1 else '',
                    ', '.join(missing_states)), hookenv.WARNING)
            return func(*args, **kwargs)
        return _wrapped
    return _decorator


def when_file_changed(*filenames, **kwargs):
    """
    Register the decorated function to run when one or more files have changed.

    :param list filenames: The names of one or more files to check for changes.
    :param str hash_type: The type of hash to use for determining if a file has
        changed.  Defaults to 'md5'.  Must be given as a kwarg.
    """
    def any_changed():
        changed = False
        for filename in filenames:
            old_hash = unitdata.kv().get('reactive.when_file_changed.%s' % filename)
            new_hash = host.file_hash(filename, hash_type=kwargs.get('hash_type', 'md5'))
            if old_hash != new_hash:
                unitdata.kv().set('reactive.when_file_changed.%s' % filename, new_hash)
                changed = True  # mark as changed, but keep updating hashes
        return changed

    return ReinvokingHandler.decorator(
        any_changed,
        lambda: [])
