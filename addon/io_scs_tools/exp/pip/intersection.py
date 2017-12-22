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

# Copyright (C) 2015-2017: SCS Software

from mathutils import Vector
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import math as _math_utils


class Intersection:
    __global_intersection_counter = 0

    @staticmethod
    def reset_counter():
        Intersection.__global_intersection_counter = 0

    @staticmethod
    def get_global_intersection_count():
        return Intersection.__global_intersection_counter

    @staticmethod
    def have_common_fork(curve1, curve2):
        """Checks if given curves have common fork.

        :param curve1: first curve
        :type curve1: io_scs_tools.exp.pip.curve.Curve
        :param curve2: second curve
        :type curve2: io_scs_tools.exp.pip.curve.Curve
        :return: True if they have common fork; False otherwise
        :rtype: bool
        """

        curve1_parents = curve1.get_all_next_prev_curves(False).keys()
        curve2_parents = curve2.get_all_next_prev_curves(False).keys()

        for c1_parent in curve1_parents:

            for c2_parent in curve2_parents:

                if c1_parent == c2_parent:
                    return True

        return False

    @staticmethod
    def have_common_joint(curve1, curve2):
        """Checks if given curves have common joint.

        :param curve1: first curve
        :type curve1: io_scs_tools.exp.pip.curve.Curve
        :param curve2: second curve
        :type curve2: io_scs_tools.exp.pip.curve.Curve
        :return: True if they have common fork; False otherwise
        :rtype: bool
        """

        curve1_parents = curve1.get_all_next_prev_curves(True).keys()
        curve2_parents = curve2.get_all_next_prev_curves(True).keys()

        for c1_parent in curve1_parents:

            for c2_parent in curve2_parents:

                if c1_parent == c2_parent:
                    return True

        return False

    @staticmethod
    def get_intersection(curve1, curve2):
        """Checks if given curves intersects and returns point of intersection
        and positions on the curve, where they intersects.

        :param curve1: first curve
        :type curve1: io_scs_tools.exp.pip.curve.Curve
        :param curve2: second curve
        :type curve2: io_scs_tools.exp.pip.curve.Curve
        :return: intersection point and position coefs where on curves that happend or None if not found
        :rtype: (mathutils.Vector, float, float) | (None, float, float)
        """

        length1 = curve1.get_length()
        length2 = curve2.get_length()

        # prevent zero division error as curves can't really intersect if one of them doesn't really exist
        if length1 == 0 or length2 == 0:
            return None, -1, -1

        curve1_p1, curve1_t1 = curve1.get_start()
        curve1_p2, curve1_t2 = curve1.get_end()

        curve2_p1, curve2_t1 = curve2.get_start()
        curve2_p2, curve2_t2 = curve2.get_end()

        return _curve_utils.curves_intersect(curve1_p1, curve1_t1, curve1_p2, curve1_t2, length1,
                                             curve2_p1, curve2_t1, curve2_p2, curve2_t2, length2,
                                             part_count=_PL_consts.CURVE_STEPS_COUNT)

    @staticmethod
    def get_intersection_radius(curve1, curve2, curve1_pos_coef, curve2_pos_coef, curve1_direction=1, curve2_direction=1):
        """Get needed radius for reaching safe point when moving on curves in desired direction.
        In forst case full radius is returned which is the point where curve has no ancestors/children anymore.

        :param curve1: first curve
        :type curve1: io_scs_tools.exp.pip.curve.Curve
        :param curve2: second curve
        :type curve2: io_scs_tools.exp.pip.curve.Curve
        :param curve1_pos_coef: position coeficient of first curve for intersection point
        :type curve1_pos_coef: float
        :param curve2_pos_coef: position coeficient of second curve for intersection point
        :type curve2_pos_coef: float
        :param curve1_direction: first curve scaning direction (forward scaning: 1; backward scaning: -1)
        :type curve1_direction: int
        :param curve2_direction: second curve scaning direction (forward scaning: 1; backward scaning: -1)
        :type curve2_direction: int
        :return: radius; 0 if curves have same fork/joint, depending on their direction
        :rtype: int
        """

        steps = (0.1, 0.1)  # size of the step on curve in each iteration

        curr_c = [curve1, curve2]  # current curves
        curr_pos = [curr_c[0].get_length() * curve1_pos_coef, curr_c[1].get_length() * curve2_pos_coef]  # current curves positions

        # first point and tangent vectors for both curves
        curve_p1 = [Vector(), Vector()]
        curve_t1 = [Vector(), Vector()]

        # second point and tangent vectors for both curves
        curve_p2 = [Vector(), Vector()]
        curve_t2 = [Vector(), Vector()]

        curve_directions = (curve1_direction, curve2_direction)  # stepping directions for both curves

        # current radius and distance between curves
        radius = 0
        distance = 0

        # advance until distance is meet
        while distance <= _PL_consts.SAFE_DISTANCE:

            # get data for both curves
            for i in range(2):

                # go to next position on curve
                old_curr_pos = curr_pos[i]
                if curve_directions[i] == 1:
                    curr_pos[i] = min(curr_pos[i] + steps[i], curr_c[i].get_length())
                else:
                    curr_pos[i] = max(0, curr_pos[i] - steps[i])

                # if we reached end of the curve, try to get on next/previous one or exit
                if old_curr_pos == curr_pos[i]:

                    # step out if no next/previous possible curve
                    if len(curr_c[i].get_next_prev_curves(curve_directions[i] == 1)) < 1:
                        return radius

                    curr_c[i] = curr_c[i].get_next_prev_curves(curve_directions[i] == 1)[0]

                    if curve_directions[i] == 1:
                        curr_pos[i] = min(steps[i], curr_c[i].get_length())
                    else:
                        curr_pos[i] = max(0, curr_c[i].get_length() - steps[i])

                curve_p1[i], curve_t1[i] = curr_c[i].get_start()
                curve_p2[i], curve_t2[i] = curr_c[i].get_end()

            # extra check if curves have same fork/joint;
            # then calculated radius has to be ignored therefore return zero radius
            next_prev_c1 = curr_c[0].get_next_prev_curves(curve_directions[i] == 1)
            next_prev_c2 = curr_c[1].get_next_prev_curves(curve_directions[i] == 1)

            if len(next_prev_c1) == 1 and len(next_prev_c2) == 1:
                if next_prev_c1[0] == next_prev_c2[0]:
                    return 0

            # if everything is okay finally calculate curve points, distance and radius
            curr_p1 = _curve_utils.smooth_curve_position(curve_p1[0], curve_t1[0], curve_p2[0], curve_t2[0], curr_pos[0] / curr_c[0].get_length())
            curr_p2 = _curve_utils.smooth_curve_position(curve_p1[1], curve_t1[1], curve_p2[1], curve_t2[1], curr_pos[1] / curr_c[1].get_length())

            distance = _math_utils.get_distance(curr_p1, curr_p2)
            radius += steps[0]

        return radius

    def __eq__(self, other):
        return (self.__inter_curve_id == other.__inter_curve_id and
                self.__inter_position == other.__inter_position)

    def __init__(self, curve_id, curve_ui_name, position):
        """Constructs intersection class instance for PIP file.

        :param curve_id: index of the intersecting curve from PIP file
        :type curve_id: int
        :param curve_ui_name: UI name of starting locator (used for debug only)
        :type curve_ui_name: str
        :param position: position of intersecting point on the curve [0.0 - 1.0]
        :type position: float
        """
        self.__inter_curve_id = curve_id
        self.__inter_position = position
        self.__inter_radius = 0
        self.__flags = 0

        self.__tmp_sibling_count = 0
        self.__tmp_curve_ui_name = curve_ui_name

        Intersection.__global_intersection_counter += 1

    def __del__(self):
        """Destructor used to decrement global number of intersections.
        """
        Intersection.__global_intersection_counter -= 1

    def set_flags(self, is_start, is_end, is_split_sharp, siblings_increment):
        """Set flags upon given input for intersection.

        NOTE: set flags on first intersection only from the array of same intersections

        :param is_start: True if this intersection is fork
        :type is_start: bool
        :param is_end: True if this intersection is joint
        :type is_end: bool
        :param is_split_sharp: True if this intersetion is split cross and has to sharp angle between curves
        :type is_split_sharp: bool
        :param siblings_increment: number of sibling intersections ( same intersections different curve id)
        :type siblings_increment: int
        """

        self.__flags = 0

        if is_start:
            self.__flags |= _PL_consts.PIF.TYPE_START

        if is_end:
            self.__flags |= _PL_consts.PIF.TYPE_END

        if is_split_sharp:
            self.__flags |= _PL_consts.PIF.TYPE_CROSS_SHARP

        self.__tmp_sibling_count += siblings_increment

        self.__flags |= (self.__tmp_sibling_count << _PL_consts.PIF.SIBLING_COUNT_SHIFT)

    def set_radius(self, new_radius):
        """Set radius to intersection if given value is greater then already existing one.

        :param new_radius: lowest distance between intersection point and safe distance (4 m)
        :type new_radius: float
        """

        self.__inter_radius = max(self.__inter_radius, new_radius)

    def get_radius(self):
        """Get internal radius.

        :return: radius
        :rtype: float
        """
        return self.__inter_radius

    def get_as_section(self):
        """Get trigger point information represented with SectionData structure class.

        :return: packed TriggerPoint as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Intersection")
        section.props.append(("#", "curve start locator: %r" % self.__tmp_curve_ui_name))
        section.props.append(("InterCurveID", self.__inter_curve_id))
        section.props.append(("InterPosition", float("%.6f" % self.__inter_position)))
        section.props.append(("InterRadius", float("%.6f" % self.__inter_radius)))
        section.props.append(("Flags", self.__flags))

        return section
