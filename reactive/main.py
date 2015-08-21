from charmhelpers.core.hookenv import status_set
from charmhelpers.core.unitdata import kv
from charmhelpers.fetch import apt_install
from charmhelpers.fetch import filter_installed_packages

from charms.reactive import hook

try:
    from local import PACKAGES
except ImportError:
    PACKAGES = []


db = kv()


@hook('install')
def install_packages():
    if PACKAGES and not db.get('installed'):
        status_set('maintenance', 'Installing packages')
        apt_install(filter_installed_packages(PACKAGES))
        db.set('installed', True)
