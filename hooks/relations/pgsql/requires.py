#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charmhelpers.core.reactive import RelationBase
from charmhelpers.core.reactive import hook
from charmhelpers.core.reactive import scopes


class PostgreSQLClient(RelationBase):
    # We only expect a single pgsql server to be related.  Additionally, if
    # there are multiple units, it would be for replication purposes only,
    # so we would expect a leader to provide our connection info, or at least
    # for all pgsql units to agree on the connection info.  Thus, we use a
    # global conversation scope in which all services and units share the
    # same conversation.
    scope = scopes.GLOBAL

    # These remote data fields will be automatically mapped to accessors
    # with a basic documentation string provided.
    auto_accessors = ['host', 'port', 'database', 'user', 'password',
                      'schema_user', 'schema_password']

    @hook('{requires:pgsql}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.connected')
        if self.connection_string():
            self.set_state('{relation_name}.database.available')

    @hook('{requires:pgsql}-relation-{broken,departed}')
    def departed(self):
        self.remove_state('{relation_name}.connected')
        self.remove_state('{relation_name}.database.available')

    def request_roles(self, *roles):
        """
        Tell Postgres to provide our user with a certain set of roles.

        :param list roles: One or more role names to give this service's user.
        """
        self.set_remote('roles', ','.join(roles))

    def change_database_name(self, dbname):
        """
        Tell Postgres to provide us with a database with a specific name.

        :param str dbname: New name for the database to use.
        """
        self.set_remote('database', dbname)

    def connection_string(self):
        """
        Get the connection string, if available, or None.
        """
        data = {
            'host': self.host(),
            'port': self.port(),
            'database': self.database(),
            'user': self.user(),
            'password': self.password(),
        }
        if all(data.values()):
            return str.format(
                'host={host} port={port} dbname={database} '
                'user={user} password={password}',
                **data)
        return None
