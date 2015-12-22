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

from mathutils import Quaternion, Vector

from io_scs_tools.internals.structure import SectionData as _SectionData


class Bezier:
    class BezierPoint:
        def __init__(self, position, rotation, is_start=True):
            """Constructs start or end of Bezier curve

            :param position: position of the point
            :type position: tuple | Vector
            :param rotation: rotation of the point
            :type rotation: tuple | Quaternion
            :param is_start: if True Start point will be created; otherwise End point will be created
            :type is_start: bool
            """
            self.__type = "Start" if is_start else "End"
            self.__position = position
            self.__rotation = rotation

        def get_pos_rot(self):
            """Gets position and rotation as a tuple.

            :return: tuple of position and rotation
            :rtype: tuple[mathutils.Vector, mathutils.Quaternion]
            """
            return Vector(self.__position), Quaternion(self.__rotation)

        def get_as_section(self):
            """Get Bezier point information represented with SectionData structure class.

            :return: packed Bezier point as section data
            :rtype: io_scs_tools.internals.structure.SectionData
            """

            section = _SectionData(self.__type)
            section.props.append(("Position", ["&&", tuple(self.__position)]))
            section.props.append(("Rotation", ["&&", tuple(self.__rotation)]))

            return section

    def __init__(self):
        """Constructs Bezier curve representation.

        """
        self.__start = self.BezierPoint((0.,) * 3, (1.,) + (0.,) * 3)
        self.__end = self.BezierPoint((0.,) * 3, (1.,) + (0.,) * 3, is_start=False)

    def set_start(self, position, rotation):
        """Set start point of Bezier curve

        :param position: position represented with tuple (size:3) or Vector
        :type position: tuple | Vector
        :param rotation: rotation represented with tuple (size:4) or Vector
        :type rotation: tuple | Quaternion
        """
        self.__start = self.BezierPoint(position, rotation)

    def set_end(self, position, rotation):
        """Set end point of Bezier curve

        :param position: position represented with tuple (size:3) or Vector
        :type position: tuple | Vector
        :param rotation: rotation represented with tuple (size:4) or Vector
        :type rotation: tuple | Quaternion
        """
        self.__end = self.BezierPoint(position, rotation, is_start=False)

    def get_start(self):
        """Get start point position and rotation tuple.

        :return: tuple of position and rotation (position, rotation)
        :rtype: tuple[mathutils.Vector, mathutils.Quaternion]
        """
        return self.__start.get_pos_rot()

    def get_end(self):
        """Get end point position and rotation tuple.

        :return: tuple of position and rotation (position, rotation)
        :rtype: tuple[mathutils.Vector, mathutils.Quaternion]
        """
        return self.__end.get_pos_rot()

    def get_as_section(self):
        """Get Bezier information represented with SectionData structure class.

        :return: packed Bezier as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Bezier")
        section.sections.append(self.__start.get_as_section())
        section.sections.append(self.__end.get_as_section())

        return section
