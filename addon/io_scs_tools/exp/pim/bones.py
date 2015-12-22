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

# Copyright (C) 2013-2015: SCS Software

from collections import OrderedDict
from io_scs_tools.internals.structure import SectionData as _SectionData


class Bones:
    __bones = OrderedDict()  # list of all bone names used in game object ( order should be the same as in PIS file )

    __global_bones_counter = 0

    @staticmethod
    def reset_counter():
        Bones.__global_bones_counter = 0

    @staticmethod
    def get_global_bones_count():
        return Bones.__global_bones_counter

    def __init__(self):
        """Initalize new bones instance for PIM file.
        """
        self.__bones = OrderedDict()

    def add_bone(self, bone_name):
        """Adds bone name to bone list.
        WARNING: if bone with the names is already on the list it won't be added
        :param bone_name:
        :type bone_name:
        :return: True if bone was successfully added to list; False otherwise
        :rtype: bool
        """

        if bone_name not in self.__bones:
            self.__bones[bone_name] = len(self.__bones)
            Bones.__global_bones_counter += 1
            return True

        return False

    def get_bone_index(self, bone_name):
        """Gets bone index by bone name.
        NOTE: This shall be used when reading vertex groups weights for vertex.

        :param bone_name: name of the bone for which index should be returned
        :type bone_name: str
        :return: index of the bone; if not found -1 is returned
        :rtype: int
        """

        if bone_name not in self.__bones:
            return -1

        return self.__bones[bone_name]

    def get_as_section(self):
        """Gets bones information represented with SectionData structure class.
        :return: packed bones names as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Bones")

        for bone_name in self.__bones.keys():
            section.data.append(("__string__", bone_name))

        return section
