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


from io_scs_tools.internals.structure import SectionData as _SectionData


class Sign:
    __global_sign_counter = 0

    @staticmethod
    def reset_counter():
        Sign.__global_sign_counter = 0

    @staticmethod
    def get_global_sign_count():
        return Sign.__global_sign_counter

    def __init__(self, name, part):
        """Constructs Sing class instance for PIP file.

        :param name: name of the sign
        :type name: str
        :param part: part name to which this sign belongs to
        :type part: str
        """

        self.__name = name
        self.__position = (0.,) * 3
        self.__rotation = (1.,) + (0.,) * 3
        self.__model = ""
        self.__part = part

        Sign.__global_sign_counter += 1

    def set_position(self, position):
        """Sets position of the sign.

        :param position: position of the sign
        :type position: tuple | mathutils.Vector
        """
        self.__position = position

    def set_rotation(self, rotation):
        """Sets rotation of the sign.

        :param rotation: rotation of the sign
        :type rotation: tuple | mathutils.Quaternion
        """
        self.__rotation = rotation

    def set_model(self, model):
        """Sets model of the sign.

        :param model: sign model name
        :type model: str
        """
        self.__model = model

    def get_as_section(self):
        """Get sign information represented with SectionData structure class.

        :return: packed Sign as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Sign")
        section.props.append(("Name", self.__name))
        section.props.append(("Position", ["&&", tuple(self.__position)]))
        section.props.append(("Rotation", ["&&", tuple(self.__rotation)]))
        section.props.append(("Model", self.__model))
        section.props.append(("Part", self.__part))

        return section
