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


from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class TriggerPoint:
    __global_trigger_point_counter = 0

    @staticmethod
    def reset_counter():
        TriggerPoint.__global_trigger_point_counter = 0

    @staticmethod
    def get_global_trigger_point_count():
        return TriggerPoint.__global_trigger_point_counter

    @staticmethod
    def prepare_trigger_points(triggers_l):
        """Prepares given trigger points for get_as_section call.
        This will calculate proper TriggerID's on all trigger points.

        :param triggers_l: list of trigger points which shall be prepared
        :type triggers_l: collections.Iterable[TriggerPoint]
        """

        triggers_count = 0

        for trigger_point in triggers_l:

            if trigger_point.get_trigger_id() != -1:
                continue

            if trigger_point.is_flag_set(_PL_consts.TPF.SPHERE):
                trigger_point.set_trigger_id(triggers_count)
                triggers_count += 1
                continue

            trigger_point.set_trigger_id(triggers_count)
            triggers_count += 1

            current = trigger_point
            neighbour = current.get_1st_neighbour()
            while neighbour != trigger_point:

                if neighbour is None:
                    lprint("W Trigger point %r has less then 2 neighbours, expect problems in game!",
                           (current.get_ui_name(),))
                    break

                if neighbour.is_flag_set(_PL_consts.TPF.SPHERE):
                    lprint("W Trigger point %r is set as 'Sphere Trigger' and shouldn't be connected, expect problems in game!",
                           (neighbour.get_ui_name(),))

                neighbour.set_trigger_id(current.get_trigger_id())

                if neighbour.get_1st_neighbour() != current:
                    current = neighbour
                    neighbour = neighbour.get_1st_neighbour()
                else:
                    current = neighbour
                    neighbour = neighbour.get_2nd_neighbour()

    def __init__(self, index, ui_name):
        """Constructs TriggerPoint class instance for PIP file.

        :param index: index of trigger point in PIP file
        :type index: int
        :param ui_name: trigger point locator name (used for debug only)
        :type ui_name: str
        """

        self.__index = index
        self.__trigger_id = -1
        self.__trigger_action = ""
        self.__trigger_range = 0.0
        self.__trigger_reset_delay = 0.0
        self.__trigger_reset_dist = 0.0  # unused in game
        self.__flags = 0
        self.__position = (0.,) * 3
        self.__neighbours = [-1, ] * _PL_consts.TP_NEIGHBOURS_COUNT_MAX

        self.__tmp_ui_name = ui_name
        self.__tmp_neighbours = []
        """:type : list[TriggerPoint]"""

        TriggerPoint.__global_trigger_point_counter += 1

    def set_trigger_id(self, trigger_id):
        """Sets trigger ID.

        :param trigger_id: trigger ID
        :type trigger_id: int
        """
        self.__trigger_id = trigger_id

    def set_action(self, action):
        """Sets trigger action to trigger point.

        :param action: trigger action
        :type action: str
        """
        self.__trigger_action = action

    def set_trigger_range(self, trigger_range):
        """Sets trigger range.

        :param trigger_range: range distance of the trigger
        :type trigger_range: float
        """
        self.__trigger_range = trigger_range

    def set_reset_delay(self, reset_delay):
        """Sets reset delay.

        :param reset_delay: delay after which trigger is reset
        :type reset_delay: float
        """
        self.__trigger_reset_delay = reset_delay

    def set_flags(self, scs_props):
        """Sets flags to trigger point from given locator properties.

        :param scs_props:
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        self.__flags = 0

        # trigger manual
        if scs_props.locator_prefab_tp_manual_activ:
            self.__flags |= _PL_consts.TPF.MANUAL

        # trigger sphere
        if scs_props.locator_prefab_tp_sphere_trigger:
            self.__flags |= _PL_consts.TPF.SPHERE

        # trigger partial
        if scs_props.locator_prefab_tp_partial_activ:
            self.__flags |= _PL_consts.TPF.PARTIAL

        # trigger one time
        if scs_props.locator_prefab_tp_onetime_activ:
            self.__flags |= _PL_consts.TPF.ONETIME

    def set_position(self, position):
        """Sets position of the trigger point.

        :param position: position of trigger point
        :type position: tuple | mathutils.Vector
        """
        self.__position = position

    def add_neighbour(self, trigger_point):
        """Sets given trigger point index as neigbour.

        :param trigger_point: neighbour trigger point
        :type trigger_point: TriggerPoint
        :return: True if neighbour can be added; otherwise False
        :rtype: bool
        """

        if len(self.__tmp_neighbours) >= _PL_consts.TP_NEIGHBOURS_COUNT_MAX:
            lprint("D Trigger point neighbours overflow on locator: %s", (self.__tmp_ui_name,))
            return False

        self.__neighbours[len(self.__tmp_neighbours)] = trigger_point.get_index()

        self.__tmp_neighbours.append(trigger_point)
        return True

    def get_index(self):
        """Gets index of the trigger point.

        :return: index of trigger point
        :rtype: int
        """
        return self.__index

    def get_trigger_id(self):
        """Gets trigger ID from trigger point.

        :return: trigger ID
        :rtype: int
        """
        return self.__trigger_id

    def get_1st_neighbour(self):
        """Gets first neighbour of trigger point.

        :return: trigger point if neighbour exists; None otherwise
        :rtype: None | TriggerPoint
        """

        if len(self.__tmp_neighbours) > 0:
            return self.__tmp_neighbours[0]

        return None

    def get_2nd_neighbour(self):
        """Gets second neighbour of trigger point.

        :return: trigger point if neighbour exists; None otherwise
        :rtype: None | TriggerPoint
        """

        if len(self.__tmp_neighbours) > 1:
            return self.__tmp_neighbours[1]

        return None

    def get_ui_name(self):
        """Gets UI name of trigger point.

        :return: UI name
        :rtype: str
        """
        return self.__tmp_ui_name

    def is_flag_set(self, mask):
        """Tells if given masked flag is set.

        :param mask: flag mask
        :type mask: int
        :return: True if flag is set; otherwise False
        :rtype: bool
        """
        return self.__flags & mask != 0

    def get_as_section(self):
        """Get trigger point information represented with SectionData structure class.

        :return: packed TriggerPoint as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("TriggerPoint")
        section.props.append(("Index", self.__index))
        section.props.append(("TriggerID", self.__trigger_id))
        section.props.append(("TriggerAction", self.__trigger_action))
        section.props.append(("TriggerRange", self.__trigger_range))
        section.props.append(("TriggerResetDelay", self.__trigger_reset_delay))
        section.props.append(("TriggerResetDist", self.__trigger_reset_dist))
        section.props.append(("Flags", self.__flags))
        section.props.append(("Position", ["&&", tuple(self.__position)]))
        section.props.append(("Neighbours", ["ii", tuple(self.__neighbours)]))

        return section
