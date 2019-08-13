import charmhelpers
import charms.reactive as reactive


@reactive.when_not('non-existent-flag')
def status_set():
    charmhelpers.core.hookenv.status_set('active', 'Unit is ready')
