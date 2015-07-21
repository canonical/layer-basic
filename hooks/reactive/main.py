from reactive import local

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.reactive import hook
from charmhelpers.core.unitdata import kv

from charmhelpers.fetch import apt_install
from charmhelpers.fetch import apt_purge
from charmhelpers.fetch import filter_installed_packages


db = kv()


@hook('install')
def install_packages():
    if not db.get('installed'):
        status_set('maintenance', 'Installing packages')
        apt_install(filter_installed_packages(local.PACKAGES))
        db.set('installed', True)


@hook('stop')
def uninstall_packages():
    if db.get('installed'):
        status_set('maintenance', 'Purging packages')
        apt_purge(local.PACKAGES)
        db.unset('installed')
