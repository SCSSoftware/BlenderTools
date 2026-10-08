# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2015: SCS Software


from io_scs_tools.internals.structure import SectionData as _SectionData


class SpawnPoint:
    __global_spawn_point_counter = 0

    @staticmethod
    def reset_counter():
        SpawnPoint.__global_spawn_point_counter = 0

    @staticmethod
    def get_global_spawn_point_count():
        return SpawnPoint.__global_spawn_point_counter

    def __init__(self, name):
        """Constructs SpawnPoint class instance for PIP file.

        :param name: name of the spawn point
        :type name: str
        """

        self.__name = name
        self.__position = (0.,) * 3
        self.__rotation = (1.,) + (0.,) * 3
        self.__type = 0  # NONE
        self.__flags = 0  # NONE

        SpawnPoint.__global_spawn_point_counter += 1

    def set_position(self, position):
        """Sets position of spawn point.

        :param position: position of the sign
        :type position: tuple | mathutils.Vector
        """
        self.__position = position

    def set_rotation(self, rotation):
        """Sets rotation of spawn point.

        :param rotation: rotation of the sign
        :type rotation: tuple | mathutils.Quaternion
        """
        self.__rotation = rotation

    def set_type(self, sp_type):
        """Set type of spawn point.

        NOTE: there is no safety check if value is valid,
        make sure that prefab locator properties are synced with PSP_* consts.

        :param sp_type: integer type of spawn point
        :type sp_type: int
        """
        self.__type = sp_type

    def set_flags(self, sp_flags):
        """Set flags of spawn point.

        NOTE: there is no safety check if value is valid,
        make sure that prefab locator properties are synced with PSPCF_* consts.

        :param sp_flags: integer flags of spawn point
        :type sp_flags: int
        """

        # depot type
        self.__flags |= int(sp_flags.locator_prefab_custom_depot_type)

        # parking difficulty
        self.__flags |= int(sp_flags.locator_prefab_custom_parking_difficulty)

        # lenght
        self.__flags |= int(sp_flags.locator_prefab_custom_lenght)

        # rule
        self.__flags |= int(sp_flags.locator_prefab_custom_rule)

    def get_as_section(self):
        """Get spawn point information represented with SectionData structure class.

        :return: packed SpawnPoint as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("SpawnPoint")
        section.props.append(("Name", self.__name))
        section.props.append(("Position", ["&&", tuple(self.__position)]))
        section.props.append(("Rotation", ["&&", tuple(self.__rotation)]))
        section.props.append(("Type", self.__type))
        section.props.append(("Flags", self.__flags))

        return section
