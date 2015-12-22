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


class TerrainPntsTrans:
    """Transitional terrain points class for storing terrain points position and normal per variant index and node index.
    This storage shall be use to collect&store terrain points in PIP importer and then used it in PIM importer.
    """

    class Entry:
        def __init__(self, variant_i, node_i):
            self.variant_i = variant_i
            self.node_i = node_i

        def __eq__(self, other):
            return self.variant_i == other.variant_i and self.node_i == other.node_i

    @staticmethod
    def __stringfy_key__(position):
        """Creates string key from position vector.

        NOTE: currently matching is done on milimeter precision, because
        better precision in some cases didn't recover all of the points.

        :param position:
        :type position: mathutils.Vector | tuple
        :return: string representation of position
        :rtype: str
        """
        return "%.3f;%.3f;%.3f" % (position[0], position[1], position[2])

    def __init__(self):
        """Creates class instance of terrain points transitional structure.
        """

        self.__storage = {}
        """:type: dict[str, list[TerrainPoints.Entry]]"""

    def add(self, variant_index, node_index, position, normal):
        """Adds new terrain point to storage.

        :param variant_index: variant index for which terrain point shall be added
        :type variant_index: int
        :param node_index: node index for which terrain point shall be added
        :type node_index: int
        :param position: position of terrain point
        :type position: Vector
        :param normal: normal of terrain point
        :type normal: Vector
        """

        # just ignore normal, for now matching by position is enough
        if normal:
            pass

        key = TerrainPntsTrans.__stringfy_key__(position)
        if key not in self.__storage:
            self.__storage[key] = []

        # save only unique position points
        tp_entry = TerrainPntsTrans.Entry(variant_index, node_index)
        if tp_entry not in self.__storage[key]:
            self.__storage[key].append(tp_entry)

    def get(self, position):
        """Get terrain points for given position.

        :param position: position for which terrain points shall be returned
        :type position: mathutils.Vector | tuple
        :return: list of terrain points entries on given location
        :rtype: list[TerrainPntsTrans.Entry]
        """

        key = self.__stringfy_key__(position)
        if key in self.__storage:
            return self.__storage[key]
        else:
            return []
