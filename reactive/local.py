import os
import re
import shutil
import subprocess

from charmhelpers.core.hookenv import charm_dir
from charmhelpers.core.hookenv import close_port
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import unit_private_ip

from charmhelpers.core.host import chownr
from charmhelpers.core.host import service_restart
from charmhelpers.core.host import service_stop

from charmhelpers.core.reactive import hook
from charmhelpers.core.reactive import when
from charmhelpers.core.reactive import when_not
from charmhelpers.core.reactive import when_file_changed

from charmhelpers.core.unitdata import kv

from charmhelpers.fetch import apt_install
from charmhelpers.fetch import install_remote

config = config()
db = kv()

DB_NAME = 'cbo'
DB_ROLE = 'cbo'

APT_PKGS = ('make',)

APP_DIR = '/opt/cloud-benchmarks'
APP_INI_SRC = os.path.join(APP_DIR, 'production.ini')
APP_INI_DEST = '/etc/cloudbenchmarks.ini'
APP_USER = 'ubuntu'
APP_GROUP = 'ubuntu'

SERVICE = 'cloudbenchmarks'

UPSTART_FILE = '{}.conf'.format(SERVICE)
UPSTART_SRC = os.path.join(charm_dir(), 'files', UPSTART_FILE)
UPSTART_DEST = os.path.join('/etc/init', UPSTART_FILE)


@hook('config-changed')
def install():
    if db.get('repo') != config['repo']:
        status_set('maintenance', 'Installing app')
        apt_install(APT_PKGS)
        tmp_dir = install_remote(config['repo'], dest='/tmp', depth=1)
        shutil.rmtree(APP_DIR, ignore_errors=True)
        log('Moving app source from {} to {}'.format(
            tmp_dir, APP_DIR))
        shutil.move(tmp_dir, APP_DIR)
        subprocess.check_call('make .venv'.split(), cwd=APP_DIR)
        shutil.copyfile(UPSTART_SRC, UPSTART_DEST)
        chownr(APP_DIR, APP_USER, APP_GROUP)
        db.set('repo', config['repo'])

    if config.changed('port'):
        open_port(config['port'])
        if config.previous('port'):
            close_port(config.previous('port'))


@when('website.available')
def configure_website(http):
    http.configure(unit_private_ip(), config['port'])


@when('db.database.available')
def render_ini(pgsql):
    db_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
        pgsql.user(),
        pgsql.password(),
        pgsql.host(),
        pgsql.port(),
        pgsql.database(),
    )

    ini = ''
    with open(APP_INI_SRC, 'r') as f:
        ini = f.read()
        ini = re.sub(
            r'(sqlalchemy.url\s*=)(.*)',
            r'\1 ' + db_uri, ini)
        ini = re.sub(
            r'(port\s*=)(.*)',
            r'\1 ' + str(config['port']), ini)

    with open(APP_INI_DEST, 'w') as f:
        f.write(ini)
    chownr(APP_INI_DEST, APP_USER, APP_GROUP)


@when_not('db.database.available')
def stop_service():
    service_stop(SERVICE)
    status_set('waiting', 'Waiting for database')


@when_file_changed(APP_INI_DEST)
def restart_service():
    service_restart(SERVICE)
    status_set('active', 'Serving on port {port}'.format(**config))
