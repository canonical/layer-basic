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

from charmhelpers.cli import cmdline


class RelationBase(object):
    @classmethod
    def from_name(cls, relation_name):
        """
        Find relation implementation in the current charm, based on the
        name of the relation.

        :return: A Relation instance, or None
        """
        return None


@cmdline.subcommand()
def relation_call(relation_name, method, *args):
    """Invoke a method on the class implementing a relation"""
    relation = RelationBase.from_name(relation_name)
    return getattr(relation, method)(*args)
