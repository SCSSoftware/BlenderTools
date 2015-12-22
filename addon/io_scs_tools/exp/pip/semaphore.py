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


class Semaphore:
    __global_semaphore_counter = 0

    @staticmethod
    def reset_counter():
        Semaphore.__global_semaphore_counter = 0

    @staticmethod
    def get_global_semaphore_count():
        return Semaphore.__global_semaphore_counter

    def __init__(self, tsem_type):
        """Construct Semaphore class instance for PIP file.

        NOTE: there is no safety check for semaphore type,
        make sure that prefab locator properties are synced with TST_* consts.

        :param tsem_type: type of semaphore
        :type tsem_type: int
        """
        self.__position = (0.,) * 3
        self.__rotation = (1.,) + (0.,) * 3
        self.__type = tsem_type
        self.__semaphore_id = 0
        self.__intervals = (0.,) * 4
        self.__cycle = 0.
        self.__profile = ""

        Semaphore.__global_semaphore_counter += 1

    def set_position(self, position):
        """Sets position of the semaphore.

        :param position: position of the semaphore
        :type position: tuple | mathutils.Vector
        """
        self.__position = position

    def set_rotation(self, rotation):
        """Sets rotation of the semaphore.

        :param rotation: rotation of the semaphore
        :type rotation: tuple | mathutils.Quaternion
        """
        self.__rotation = rotation

    def set_semaphore_id(self, semaphore_id):
        """Sets ID of the semaphore.

        :param semaphore_id: ID of semaphore
        :type semaphore_id: int
        :return: True if succesfully set id, False if id value is smaller then 0
        :rtype: bool
        """

        if semaphore_id >= 0:
            self.__semaphore_id = semaphore_id
            return True
        else:
            return False

    def set_intervals(self, intervals):
        """Sets working intervals for semaphore.

        :param intervals: tuple of 4 float values
        :type intervals: tuple[float]
        """
        self.__intervals = intervals

    def set_cycle(self, cycle):
        """Sets cycle value for semaphore.

        :param cycle: cycle delay value
        :type cycle: float
        """
        self.__cycle = cycle

    def set_profile(self, profile):
        """Sets profile to semaphore.

        :param profile: semaphore profile
        :type profile: str
        """
        self.__profile = profile

    def get_as_section(self):
        """Get semaphore information represented with SectionData structure class.

        :return: packed Semaphore as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Semaphore")
        section.props.append(("Position", ["&&", tuple(self.__position)]))
        section.props.append(("Rotation", ["&&", tuple(self.__rotation)]))
        section.props.append(("Type", self.__type))
        section.props.append(("SemaphoreID", self.__semaphore_id))
        section.props.append(("Intervals", ["&&", tuple(self.__intervals)]))
        section.props.append(("Cycle", ["&", (self.__cycle,)]))
        section.props.append(("Profile", self.__profile))

        return section
