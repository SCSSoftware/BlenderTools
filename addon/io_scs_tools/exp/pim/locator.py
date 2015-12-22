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

# Copyright (C) 2013-2014: SCS Software

from io_scs_tools.internals.structure import SectionData as _SectionData


class Locator:
    __index = -1
    __name = ""
    __hookup = ""
    __position = None
    __rotation = None
    __scale = None

    __global_locator_counter = 0

    @staticmethod
    def reset_counter():
        Locator.__global_locator_counter = 0

    @staticmethod
    def get_global_locator_count():
        return Locator.__global_locator_counter

    def __init__(self, index, name, hookup):
        """Constructor for locator.
        NOTE: position, rotation and scale has to be set with methods
        :param index: index of locator in PIM file
        :type index: int
        :param name: name of the locator
        :type name: str
        :param hookup: hookup of the locator
        :type hookup: str
        """
        self.__index = index
        self.__name = name
        self.__hookup = hookup

        Locator.__global_locator_counter += 1

    def set_position(self, position):
        """Sets position of the locator.
        :param position: global position of the locator in SCS coordinates
        :type position: tuple | Vector
        """
        self.__position = position

    def set_rotation(self, rotation):
        """Sets rotation of the locator.
        :param rotation: absolute rotation of the locator in SCS coordinates
        :type rotation: tuple | Quaternion
        """
        self.__rotation = rotation

    def set_scale(self, scale):
        """Sets scale of the locator.
        :param scale: scale of the locator in SCS coordinates
        :type scale: tuple | Vector
        """
        self.__scale = scale

    def get_index(self):
        return self.__index

    def get_as_section(self):
        """Gets locator represented with SectionData structure class.
        :return: packed locator as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Locator")
        section.props.append(("Name", self.__name))
        if self.__hookup and self.__hookup != "":
            section.props.append(("Hookup", self.__hookup))
        section.props.append(("Index", self.__index))
        section.props.append(("Position", ["&&", self.__position]))
        section.props.append(("Rotation", ["&&", self.__rotation]))
        section.props.append(("Scale", ["&&", self.__scale]))

        return section
