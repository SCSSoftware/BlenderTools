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

import math
from io_scs_tools.consts import PrefabLocators as _PL_consts


class TerrainPntsTrans:
    """Transitional terrain points class for storing terrain points position and normal per variant index and node index.
    This storage shall be use to collect&store terrain points in PIM exporter and then use it in PIP exporter.
    """

    class Entry:
        def __init__(self, position, normal):
            self.position = position
            self.normal = normal

        def __eq__(self, other):
            distance = math.sqrt(pow(self.position[0] - other.position[0], 2) +
                                 pow(self.position[1] - other.position[1], 2) +
                                 pow(self.position[2] - other.position[2], 2))
            return distance < _PL_consts.TERRAIN_POINTS_MIN_DISTANCE

    def __init__(self):
        """Creates class instance of terrain points transitional structure.
        """

        self.__storage = {}
        """:type: dict[str, list[TerrainPntsTrans.Entry]]"""

    def add(self, variant_index, node_index, position, normal):
        """Adds new terrain point to storage.

        :param variant_index:
        :type variant_index: int
        :param node_index:
        :type node_index: int
        :param position:
        :type position: Vector
        :param normal:
        :type normal: Vector
        """

        key = str(variant_index) + ":" + str(node_index)
        if key not in self.__storage:
            self.__storage[key] = []

        # save only unique position points
        tp_entry = TerrainPntsTrans.Entry(position, normal)
        if tp_entry not in self.__storage[key]:
            self.__storage[key].append(tp_entry)

    def ensure_entry(self, variant_index, node_index):
        """Ensures that variant in given node is present.

        :param variant_index:
        :type variant_index:
        :param node_index:
        :type node_index:
        :return:
        :rtype:
        """

        key = str(variant_index) + ":" + str(node_index)
        if key not in self.__storage:
            self.__storage[key] = []

    def get(self, node_index):
        """Get terrain point for given node index.

        :param node_index: node index for which terrain points shall be returned
        :type node_index: int
        :return: dictionary of terrain points entries per variants
        :rtype: dict[int, list[TerrainPntsTrans.Entry]]
        """

        tp_dict = {}

        for key in self.__storage:

            variant_i, node = key.split(":")
            if int(node) == node_index:

                tp_dict[int(variant_i)] = self.__storage[key]

        return tp_dict
