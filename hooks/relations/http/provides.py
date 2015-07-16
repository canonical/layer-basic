from charmhelpers.core.reactive import hook
from charmhelpers.core.reactive import RelationBase
from charmhelpers.core.reactive import scopes


class HttpProvides(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:http}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:http}-relation-{broken,departed}')
    def broken(self):
        self.remove_state('{relation_name}.available')

    def configure(self, hostname, port):
        relation_info = {
            'hostname': hostname,
            'port': port,
        }
        self.set_remote(**relation_info)
