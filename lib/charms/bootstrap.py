import os
import sys
from glob import glob
from subprocess import check_call


def bootstrap_charm_deps():
    if os.path.exists('wheelhouse/.bootstrapped'):
        return
    # bootstrap wheelhouse
    if os.path.exists('wheelhouse'):
        check_call(['apt-get', 'install', '-yq', 'python3-pip'])
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
