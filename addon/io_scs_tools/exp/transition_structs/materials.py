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


class MaterialsTrans:
    """Transitional materials class for storing used materials during export.
    This storage shall be use to collect&store materials in PIM exporter and then use it in PIT exporter.
    """

    def __init__(self):
        """Creates class instance of materials transitional structure.
        """
        self.__storage = OrderedDict()
        """:type: collections.OrderedDict[str, bpy.types.Material]"""

    def add(self, material_name, material):
        """Adds material to storage.

        :param material_name: material name
        :type material_name: str
        :param material: Blender material
        :type material: bpy.types.Material
        """

        if material_name not in self.__storage:
            self.__storage[material_name] = material

    def get_as_pairs(self):
        """Returns stored materials as list of pairs.

        :return: stored materials as list of pairs
        :rtype: list[tuple[str, bpy.types.Material | None]]
        """

        pairs = []

        for material_name in self.__storage:
            pairs.append((material_name, self.__storage[material_name]))

        return pairs
