# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2015: SCS Software


from collections import OrderedDict


class PartsTrans:
    """Transitional parts class for storing used parts during export.
    This storage shall be use to collect&store parts in PIM, PIC and PIP exporter and then use it in PIT exporter.
    """

    def __init__(self):
        """Creates class instance of parts transitional structure.
        """
        self.__storage = OrderedDict()
        """:type: collections.OrderedDict[str, int]"""

    def add(self, part_name):
        """Adds part to storage.

        :param part_name: part name
        :type part_name: str
        """
        self.__storage[part_name] = 1

    def count(self):
        """Number of currently stored parts in transitional structure.

        :return: number of currently stored parts
        :rtype: int
        """
        return len(self.__storage)

    def is_present(self, part_name):
        """Tells if given part is present in storage.

        :return: True if present; False otherwise
        :rtype: bool
        """
        return part_name in self.__storage

    def get_as_list(self):
        """Get stored part names list.

        :return: stored part names list
        :rtype: list[str]
        """
        return list(self.__storage.keys())
