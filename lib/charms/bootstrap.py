import os
import sys
from glob import glob
from subprocess import check_call


def bootstrap_charm_deps():
    if os.path.exists('wheelhouse/.bootstrapped'):
        return
    # bootstrap wheelhouse
    if os.path.exists('wheelhouse'):
        apt_install(['python3-pip', 'python3-yaml'])
        # install packages defined in layer.yaml
        install_charm_deps()
        # need newer pip, to fix spurious Double Requirement error https://github.com/pypa/pip/issues/56
        check_call(['pip3', 'install', '-U', '--no-index', '-f', 'wheelhouse', 'pip'])
        # install the rest of the wheelhouse deps
        check_call(['pip3', 'install', '-U', '--no-index', '-f', 'wheelhouse'] + glob('wheelhouse/*'))
        # flag us as having already bootstrapped so we don't do it again
        open('wheelhouse/.bootstrapped', 'w').close()
        # Ensure that the newly bootstrapped libs are available.
        # Note: this only seems to be an issue with namespace packages.
        # Non-namespace-package libs (e.g., charmhelpers) are available
        # without having to reload the interpreter. :/
        os.execl(sys.argv[0], sys.argv[0])


def install_charm_deps():
    from charms import layer

    cfg = layer.options('basic')
    apt_install(cfg.get('packages', []))


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
