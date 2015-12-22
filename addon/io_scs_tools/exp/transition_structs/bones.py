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


class BonesTrans:
    """Transitional bones class for storing used bones during export.
    This storage shall be use to collect&store bones in PIM exporter and then use it in PIS exporter.
    """

    def __init__(self):
        """Creates class instance of bones transitional structure.
        """
        self.__storage = OrderedDict()
        """:type: collections.OrderedDict[str, int]"""

    def add(self, bone_name):
        """Adds bone to storage.

        :param bone_name: bone name
        :type bone_name: str
        """
        self.__storage[bone_name] = 1

    def are_present(self):
        """Tells if there is any bones saved in storage.

        :return: True if there is any bones; False otherwise
        :rtype: bool
        """
        return len(self.__storage) > 0

    def get_as_list(self):
        """Get stored bones names list.

        :return: stored bones names list
        :rtype: list[str]
        """
        return list(self.__storage.keys())
