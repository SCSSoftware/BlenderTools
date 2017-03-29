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
from io_scs_tools.utils.printout import lprint


class PartsTrans:
    """Transitional parts class for storing used parts during export.

    This storage shall be used to store parts from SCS Root part inventory. Morover users
    should be added to each part during collecting of all object to export.
    Once exporters asks for list of parts, only the parts with at least one user will be returned.
    """

    def __init__(self, part_inventory):
        """Creates class instance of parts transitional structure.
        :param part_inventory: part inventory for SCS Root object
        :type part_inventory: list[io_scs_tools.properties.object.ObjectPartInventoryItem]
        """
        self.__storage = OrderedDict()
        """:type: collections.OrderedDict[str, int]"""
        self.__default_part = ""

        for i, part in enumerate(part_inventory):
            self.__storage[part.name] = 0
            if i == 0:
                self.__default_part = part.name

        # if given part inventory won't have any parts inside, then we have to fallback to default part
        # and properly report the issue
        if self.__default_part == "":
            self.__default_part = "defaultpart"
            lprint("E Parts can't be properly constructed, 'defaultpart' will be used for export!\n\t   "
                   "However issue should be addressed to developer...")

    def is_present(self, part_name):
        """Tells if given part is present in storage.

        :param part_name: name of the part to search for
        :type part_name: str
        :return: True if present; False otherwise
        :rtype: bool
        """
        return part_name in self.__storage

    def add_user(self, obj):
        """Adds user to validated object part.
        In case that object part doesn't exists in storage, default part get's a user

        :param obj: mesh or locator blender object from which part should be taken
        :type obj: bpy.types.Object
        """

        part_name = self.ensure_part(obj, suppress_warning=True)

        self.__storage[part_name] += 1

    def ensure_part(self, obj, suppress_warning=False):
        """Ensures and returns part for the given mesh or locator object.
        If part of the object is not preset in internal parts dictionary,
        then default part is returned and invalid part name is properly reported to log.

        :param obj: mesh or locator blender object from which part should be taken
        :type obj: bpy.types.Object
        :param suppress_warning: flag for suppressing the warning from being raised
        :type suppress_warning: bool
        :return: part name of the object or default part if object part name is invalid
        :rtype: str
        """
        part_name = obj.scs_props.scs_part

        if not self.is_present(part_name):
            if not suppress_warning:
                lprint("W Invalid part name %r detected on object %r, using first available for export: %r!"
                       "Select object and try to assign part again.",
                       (part_name, obj.name, self.__default_part))
            part_name = self.__default_part

        return part_name

    def get_as_list(self):
        """Get stored part names list with at least one user.

        Parts without user shouldn't be exported thus are not returned by this method.

        :return: stored part names list
        :rtype: list[str]
        """

        part_list = []

        for part_name in self.__storage:
            if self.__storage[part_name] > 0:
                part_list.append(part_name)

        return part_list
