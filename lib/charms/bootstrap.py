import os
import sys
import shutil
from glob import glob
from subprocess import check_call


def bootstrap_charm_deps():
    venv = os.path.abspath('../.venv')
    vbin = os.path.join(venv, 'bin')
    vpip = os.path.join(vbin, 'pip')
    vpy = os.path.join(vbin, 'python')
    if os.path.exists('wheelhouse/.bootstrapped'):
        from charms import layer
        cfg = layer.options('basic')
        if cfg['use_venv'] and '.venv' not in sys.executable:
            # activate the venv
            os.environ['PATH'] = ':'.join([vbin, os.environ['PATH']])
            reload_interpreter(vpy)
        return
    # bootstrap wheelhouse
    if os.path.exists('wheelhouse'):
        apt_install(['python3-pip', 'python3-yaml'])
        from charms import layer
        cfg = layer.options('basic')
        # include packages defined in layer.yaml
        apt_install(cfg['packages'])
        # if we're using a venv, set it up
        if cfg['use_venv']:
            apt_install(['python-virtualenv'])
            cmd = ['virtualenv', '--python=python3', venv]
            if cfg['include_system_packages']:
                cmd.append('--system-site-packages')
            check_call(cmd)
            os.environ['PATH'] = ':'.join([vbin, os.environ['PATH']])
            pip = vpip
        else:
            pip = 'pip3'
            # save a copy of system pip to prevent `pip3 install -U pip` from changing it
            if os.path.exists('/usr/bin/pip'):
                shutil.copy2('/usr/bin/pip', '/usr/bin/pip.save')
        # need newer pip, to fix spurious Double Requirement error https://github.com/pypa/pip/issues/56
        check_call([pip, 'install', '-U', '--no-index', '-f', 'wheelhouse', 'pip'])
        # install the rest of the wheelhouse deps
        check_call([pip, 'install', '-U', '--no-index', '-f', 'wheelhouse'] + glob('wheelhouse/*'))
        if not cfg['use_venv']:
            # restore system pip to prevent `pip3 install -U pip` from changing it
            if os.path.exists('/usr/bin/pip.save'):
                shutil.copy2('/usr/bin/pip.save', '/usr/bin/pip')
                os.remove('/usr/bin/pip.save')
        # flag us as having already bootstrapped so we don't do it again
        open('wheelhouse/.bootstrapped', 'w').close()
        # Ensure that the newly bootstrapped libs are available.
        # Note: this only seems to be an issue with namespace packages.
        # Non-namespace-package libs (e.g., charmhelpers) are available
        # without having to reload the interpreter. :/
        reload_interpreter(vpy if cfg['use_venv'] else sys.argv[0])


def reload_interpreter(python):
    os.execle(python, python, sys.argv[0], os.environ)


def apt_install(packages):
    if isinstance(packages, (str, bytes)):
        packages = [packages]

    env = os.environ.copy()

    if 'DEBIAN_FRONTEND' not in env:
        env['DEBIAN_FRONTEND'] = 'noninteractive'

    cmd = ['apt-get',
           '--option=Dpkg::Options::=--force-confold',
           '--assume-yes',
           'install']
    check_call(cmd + packages, env=env)
