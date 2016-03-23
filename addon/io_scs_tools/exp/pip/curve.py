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

from mathutils import Vector, Quaternion
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.exp.pip.curve_bezier import Bezier
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils.printout import lprint


class Curve:
    __NODE_DIR_LEN_COEF = 0.33333333333
    """Coeficient for calculating curve direction vectors."""

    __global_curve_counter = 0

    @staticmethod
    def reset_counter():
        Curve.__global_curve_counter = 0

    @staticmethod
    def get_global_curve_count():
        return Curve.__global_curve_counter

    @staticmethod
    def prepare_curves(curves_l):
        """Calculates lengths and leads to nodes variables for given curves.
        Should be used before calling get_as_section() on curves class instances.

        :param curves_l: list of curves to prepare
        :type curves_l: collections.Iterable[Curve]
        """

        for curve in curves_l:

            # first calculate length
            pos0, dir0 = curve.get_start(cartes_tang=False)
            pos1, dir1 = curve.get_end(cartes_tang=False)

            for i in range(4):  # converge to actual length with four iterations
                curr_dir0 = Vector(dir0 * Vector((0, 0, -1)) * Curve.__NODE_DIR_LEN_COEF * curve.get_length())
                curr_dir1 = Vector(dir1 * Vector((0, 0, -1)) * Curve.__NODE_DIR_LEN_COEF * curve.get_length())

                new_length = _curve_utils.compute_smooth_curve_length(pos0, curr_dir0, pos1, curr_dir1, _PL_consts.CURVE_MEASURE_STEPS)
                curve.set_length(new_length)

            # second calculate leads to nodes
            if curve.is_inbound():
                curve.calc_leads_to_nodes_forward(0)

        # report invalid curves
        invalid_curves = []
        """:type : list[Curve]"""
        for curve in curves_l:

            if not curve.is_valid():
                invalid_curves.append(curve)

        if len(invalid_curves) > 0:
            msg = ("W Connections with loose ends detected, expect problems in game.\n\t   "
                   "Check connections with starting Navigation Points:\n\t   [")

            for curve in invalid_curves:
                msg += "'" + curve.get_ui_name() + "', "

            msg = msg[:-2] + "]"
            lprint(msg)

    def __lt__(self, other):
        return self.__index < other.get_index()

    def __eq__(self, other):
        return self.__index == other.get_index()

    def __init__(self, index, name, ui_name):
        """Constructs curve class representation for PIP file.

        NOTE: creating this classes also saves instance to array in static variable,
        for calculation of curve length and leads to nodes flag.
        So don't make temporary instances of this class.

        :param index: index of curve
        :type index: int
        :param name: name of the curve
        :type name: str
        :param name: ui name of the curve ('start_locator_name->end_locator_name')
        :type name: str
        """
        self.__index = index
        self.__name = name

        self.__flags = 0

        self.__leads_to_nodes = 0

        self.__traffic_rule = None

        self.__sempahore_id = None

        self.__next_curves = [-1] * _PL_consts.NAVIGATION_NEXT_PREV_MAX
        self.__prev_curves = [-1] * _PL_consts.NAVIGATION_NEXT_PREV_MAX

        self.__length = 0

        self.__bezier = Bezier()

        self.__tmp_ui_name = ui_name  # name for reporting invalid curves
        self.__tmp_start_flags = 0  # temporary store flags for start point
        self.__tmp_end_flags = 0  # temporary store flags for end point
        self.__tmp_next_curves = []  # temporary store next curve class instances for actual usage in preparation stage
        """:type : list[Curve]"""
        self.__tmp_prev_curves = []  # temporary store prev curve class instances for actual usage in preparation stage
        """:type : list[Curve]"""

        self.__tmp_start_lane_i = -1  # index of boundary lane, used for calculating leads to nodes flag
        self.__tmp_end_lane_i = -1  # index of boundary lane, used for calculating leads to nodes flag
        self.__tmp_start_node_i = -1  # index of the node that start of this curve belongs to
        self.__tmp_end_node_i = -1  # index of the node that start of this curve belongs to

        Curve.__global_curve_counter += 1

    def set_output_boundaries(self, scs_props):
        """Sets prefab leaving/output lane and node index.

        :param scs_props: scs props from end prefab locator used in this curve
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        boundary_lane = int(scs_props.locator_prefab_np_boundary)
        boundary_node = int(scs_props.locator_prefab_np_boundary_node)

        # calculate actual boundary lane index
        if boundary_lane > 0:

            if _PL_consts.PREFAB_LANE_COUNT_MAX < boundary_lane <= _PL_consts.PREFAB_LANE_COUNT_MAX * 2:

                self.__tmp_end_lane_i = boundary_lane - 1 - _PL_consts.PREFAB_LANE_COUNT_MAX

                if 0 <= boundary_node < _PL_consts.PREFAB_NODE_COUNT_MAX:

                    self.__tmp_end_node_i = boundary_node

                else:

                    lprint("D Given input node index in curve(index: %s) is invalid: %s. Ignoring it.",
                           (self.__index, boundary_node))

            else:

                lprint("D Given output lane boundary index in curve(index: %s) is invalid: %s. Ignoring it.",
                       (self.__index, boundary_lane))

    def set_input_boundaries(self, scs_props):
        """Sets prefab entry/input lane and node index.

        :param scs_props: scs props from start prefab locator used in this curve
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        boundary_lane = int(scs_props.locator_prefab_np_boundary)
        boundary_node = int(scs_props.locator_prefab_np_boundary_node)

        # calculate actual boundary lane index
        if boundary_lane > 0:

            if boundary_lane <= _PL_consts.PREFAB_LANE_COUNT_MAX:

                self.__tmp_start_lane_i = boundary_lane - 1

                if 0 <= boundary_node < _PL_consts.PREFAB_NODE_COUNT_MAX:

                    self.__tmp_start_node_i = boundary_node

                else:

                    lprint("D Given input node index in curve(index: %s) is invalid: %s. Ignoring it.",
                           (self.__index, boundary_node))

            else:

                lprint("D Given output lane boundary index in curve(index: %s) is invalid: %s. Ignoring it.",
                       (self.__index, boundary_lane))

    def set_flags(self, scs_props, to_start=False):
        """Sets flags to curve start point or curve end point and calculates curve common flag variable.

        :param scs_props: scs props from prefab locator used in this curve
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        :param to_start: if True flags are saved in start point; otherwise flags are saved in end point
        :type to_start: bool
        """

        flags = 0

        # intersection priority
        flags |= (int(scs_props.locator_prefab_np_priority_modifier) << _PL_consts.PNCF.PRIORITY_SHIFT) & _PL_consts.PNCF.PRIORITY_MASK

        # additive priority
        if scs_props.locator_prefab_np_add_priority:
            flags |= _PL_consts.PNCF.ADDITIVE_PRIORITY

        # limit displacement
        if scs_props.locator_prefab_np_limit_displace:
            flags |= _PL_consts.PNCF.LIMIT_DISPLACEMENT

        # blinker
        flags |= int(scs_props.locator_prefab_np_blinker)

        # low probability
        if scs_props.locator_prefab_np_low_probab:
            flags |= _PL_consts.PNCF.LOW_PROBABILITY

        # allowed vehicles
        flags |= int(scs_props.locator_prefab_np_allowed_veh)

        if to_start:
            self.__tmp_start_flags = flags
        else:
            self.__tmp_end_flags = flags

        # update common curve flags variable
        self.__flags = self.__tmp_start_flags & self.__tmp_end_flags
        self.__flags |= (self.__tmp_start_flags & _PL_consts.PNCF.START_NAV_POINT_FLAGS)
        self.__flags |= (self.__tmp_end_flags & _PL_consts.PNCF.END_NAV_POINT_FLAGS)

    def set_length(self, value):
        """Set curve length.

        :param value: curve length
        :type value: float
        """
        self.__length = value

    def set_traffic_rule(self, traffic_rule):
        """Set traffic rule for this curve.

        :param traffic_rule: traffic rule string
        :type traffic_rule: str
        """
        self.__traffic_rule = traffic_rule

    def set_semaphore_id(self, semaphore_id):
        """Set sempahore ID  to curve.

        :param semaphore_id: id of semaphore on this curve
        :type semaphore_id: int
        :return: True if succesfully set id, False if id value is smaller then 0
        :rtype: bool
        """

        if semaphore_id >= 0:
            self.__sempahore_id = semaphore_id
            return True
        else:
            return False

    def add_next_curve(self, curve):
        """Adds next curve.

        :param curve: next curve instance
        :type curve: Curve
        :return: True if next curve is properly set; False if next curves array is already full
        :rtype: bool
        """

        if len(self.__tmp_next_curves) >= _PL_consts.NAVIGATION_NEXT_PREV_MAX:
            lprint("D Navigation point next curve overflow on curve with index: %s;", (self.__index,))
            return False

        self.__next_curves[len(self.__tmp_next_curves)] = curve.get_index()

        self.__tmp_next_curves.append(curve)
        return True

    def add_prev_curve(self, curve):
        """Adds previous curve.

        :param curve: previous curve instance
        :type curve: Curve
        :return: True if previous curve is properly set; False if previous curves array is already full
        :rtype: bool
        """

        if len(self.__tmp_prev_curves) >= _PL_consts.NAVIGATION_NEXT_PREV_MAX:
            lprint("D Navigation point previous curve overflow on curve with index: %s;", (self.__index,))
            return False

        self.__prev_curves[len(self.__tmp_prev_curves)] = curve.get_index()

        self.__tmp_prev_curves.append(curve)
        return True

    def set_start(self, position, rotation):
        """Set start point of curve

        :param position: position represented with tuple (size:3) or Vector
        :type position: tuple | Vector
        :param rotation: rotation represented with tuple (size:4) or Vector
        :type rotation: tuple | Quaternion
        """
        self.__bezier.set_start(position, rotation)

    def set_end(self, position, rotation):
        """Set end point of curve

        :param position: position represented with tuple (size:3) or Vector
        :type position: tuple | Vector
        :param rotation: rotation represented with tuple (size:4) or Vector
        :type rotation: tuple | Quaternion
        """
        self.__bezier.set_end(position, rotation)

    def get_start(self, cartes_tang=True):
        """Get start point position and rotation tuple.

        NOTE: when using cartes, length of the curve must be already calculated

        :param cartes_tang: create cartesian representation of SCS curve
        :type cartes_tang: bool
        :return: tuple of position and rotation (position, rotation)
        :rtype: tuple[mathutils.Vector, mathutils.Vector | mathutils.Quaternion]
        """

        position, rotation = self.__bezier.get_start()

        if cartes_tang:
            rotation = rotation * Vector((0, 0, -1)) * Curve.__NODE_DIR_LEN_COEF * self.get_length()

        return position, rotation

    def get_end(self, cartes_tang=True):
        """Get end point position and rotation tuple.

        NOTE: when using cartes, length of the curve must be already calculated

        :param cartes_tang: create cartesian representation of SCS curve
        :type cartes_tang: bool
        :return: tuple of position and rotation (position, rotation)
        :rtype: tuple[mathutils.Vector, mathutils.Vector | mathutils.Quaternion]
        """

        position, rotation = self.__bezier.get_end()

        if cartes_tang:
            rotation = rotation * Vector((0, 0, -1)) * Curve.__NODE_DIR_LEN_COEF * self.get_length()

        return position, rotation

    def get_length(self):
        """Get length of the curve.

        :return: curve length
        :rtype: float
        """
        return self.__length

    def get_index(self):
        """Gets curve index.

        :return: curve index
        :rtype: int
        """
        return self.__index

    def get_ui_name(self):
        """Gets UI name of the curve.

        :return: ui name
        :rtype: str
        """
        return self.__tmp_ui_name

    def get_output_node_index(self):
        """Gets output node index.

        :return: node index if it's properly set; -1 otherwise
        :rtype: int
        """
        return self.__tmp_end_node_i

    def get_input_node_index(self):
        """Gets input node index.

        :return: node index if it's properly set; -1 otherwise
        :rtype: int
        """
        return self.__tmp_start_node_i

    def get_output_lane_index(self):
        """Gets output lane index.

        :return: lane index if it's properly set; -1 otherwise
        :rtype: int
        """
        return self.__tmp_end_lane_i

    def get_input_lane_index(self):
        """Gets input lane index.

        :return: lane index if it's properly set; -1 otherwise
        :rtype: int
        """
        return self.__tmp_start_lane_i

    def get_leads_to_nodes(self):
        """Gets current leads to nodes flag value from the curve.

        :return: current leads to nodes flag
        :rtype: int
        """
        return self.__leads_to_nodes

    def get_next_prev_curves(self, next_curves):
        """Returns list of next or previus curves depending on parameter.

        :param next_curves: True for next curves; False for prev curves
        :type next_curves: bool
        :return: list of next/previous curves
        :rtype: list[Curve]
        """
        if next_curves:
            return self.__tmp_next_curves
        else:
            return self.__tmp_prev_curves

    def get_all_next_prev_curves(self, next_curves, all_next_prev=None, depth=5):
        """Gets all next or previous curves to given depth. Default 5.

        :param next_curves: True for next curves; False for previous curves
        :type next_curves: bool
        :param all_next_prev: dictionary of already found next/prev curves where key is curve index and value is the curve object itself
        :type all_next_prev: dict[int, Curve]
        :param depth: depth of searching for common curve (taken from PIP exporter
        :type depth: int
        :return: all next/prev curves
        :rtype: dict[int, Curve]
        """

        depth -= 1

        if depth <= 0:
            return all_next_prev

        if all_next_prev is None:
            all_next_prev = {}

        for next_prev in self.get_next_prev_curves(next_curves):

            if next_prev.get_index() not in all_next_prev:
                all_next_prev[next_prev.get_index()] = next_prev
                all_next_prev = next_prev.get_all_next_prev_curves(next_curves, all_next_prev, depth)

        return all_next_prev

    def get_closest_point(self, point, iterations=_PL_consts.CURVE_CLOSEST_POINT_ITER):
        """Get's closest point on the curve to given point.

        NOTE: length of the curve must be already calculated.

        :param point: point to which closest curve point will be calculated
        :type point: mathutils.Vector
        :param iterations: number of iterastion for halving algorithm
        :type iterations: int
        :return: curve position coeficient of the closest point (0.0 - 1.0)
        :rtype: float
        """

        curve_p1, curve_t1 = self.get_start()
        curve_p2, curve_t2 = self.get_end()

        interval = (0, 0.5, 1)

        while iterations > 0:

            curr_p = _curve_utils.smooth_curve(curve_p1, curve_t1, curve_p2, curve_t2, interval[0])
            p1_distance = _math_utils.get_distance(curr_p, point)

            curr_p = _curve_utils.smooth_curve(curve_p1, curve_t1, curve_p2, curve_t2, interval[2])
            p3_distance = _math_utils.get_distance(curr_p, point)

            if p1_distance < p3_distance:
                interval = (interval[0], (interval[0] + interval[1]) / 2, interval[1])
            else:
                interval = (interval[1], (interval[1] + interval[2]) / 2, interval[2])

            iterations -= 1

        return interval[1]

    def is_inbound(self):
        """Returns true if this curve is starting curve.

        :return: True if curve is inbound; False otherwise
        :rtype: bool
        """
        return self.__tmp_start_lane_i != -1 and self.__tmp_start_node_i != -1

    def is_valid(self):
        """Returns true if curve is valid.

        NOTE: make sure calc_leads_to_nodes_forward is called before,
        because without calculated leads to nodes we don't know if it's valid or not

        :return: True if curve is valid; False otherwise
        :rtype: bool
        """

        return self.__leads_to_nodes > 0

    def calc_leads_to_nodes_forward(self, ancestor_leads_to_nodes, already_visited=None):
        """Calculate leads to nodes recursive in forward direction.

        NOTE: this should be called only on input nodes once before get_as_section call

        :param ancestor_leads_to_nodes: all ancestors curves leads to nodes flags
        :type ancestor_leads_to_nodes: int
        :param already_visited: curves indices dictionary of already visited curves by this recursion
        :type already_visited: dict[int, int]
        :return: it's own calculated leads to nodes flag (used in recursion)
        :rtype: int
        """

        if already_visited is None:
            already_visited = {}

        # make sure to add self to already visited
        already_visited[self.__index] = 1

        end_mask = _PL_consts.PNLF.END_NODE_MASK | _PL_consts.PNLF.END_LANE_MASK
        start_mask = _PL_consts.PNLF.START_NODE_MASK | _PL_consts.PNLF.START_LANE_MASK

        self.__leads_to_nodes |= ancestor_leads_to_nodes & start_mask

        if self.__tmp_start_lane_i >= 0 and self.__tmp_start_node_i >= 0:

            self.__leads_to_nodes |= 1 << (self.__tmp_start_node_i + _PL_consts.PNLF.START_NODE_SHIFT)
            self.__leads_to_nodes |= 1 << (self.__tmp_start_lane_i + _PL_consts.PNLF.START_LANE_SHIFT)

        if self.__tmp_end_lane_i >= 0 and self.__tmp_end_node_i >= 0:

            self.__leads_to_nodes |= 1 << (self.__tmp_end_node_i + _PL_consts.PNLF.END_NODE_SHIFT)
            self.__leads_to_nodes |= 1 << (self.__tmp_end_lane_i + _PL_consts.PNLF.END_LANE_SHIFT)

        # recursively calculate leads to nodes and collect flag values on all middle nodes
        for next_c in self.__tmp_next_curves:

            # stop following the path if next curve was already visited
            if next_c.get_index() not in already_visited:

                child_c_leads_to_nodes = next_c.calc_leads_to_nodes_forward(self.__leads_to_nodes, already_visited)
                self.__leads_to_nodes |= child_c_leads_to_nodes & end_mask

            else:  # as next curve was already visited pickup leads to nodes directly from it

                self.__leads_to_nodes |= next_c.get_leads_to_nodes() & end_mask

        return self.__leads_to_nodes

    def get_as_section(self):
        """Get curve information represented with SectionData structure class.

        :return: packed curve as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        __EMPTY_LINE__ = ("", "")

        section = _SectionData("Curve")
        section.props.append(("Index", self.__index))
        section.props.append(("#", "start locator: %r" % self.__tmp_ui_name))
        section.props.append(("Name", self.__name))
        section.props.append(__EMPTY_LINE__)
        section.props.append(("Flags", self.__flags))
        section.props.append(__EMPTY_LINE__)
        section.props.append(("LeadsToNodes", self.__leads_to_nodes))

        if self.__traffic_rule is not None and self.__traffic_rule != "":
            section.props.append(__EMPTY_LINE__)
            section.props.append(("TrafficRule", self.__traffic_rule))

        if self.__sempahore_id is not None and self.__sempahore_id != -1:
            section.props.append(__EMPTY_LINE__)
            section.props.append(("SemaphoreID", self.__sempahore_id))

        section.props.append(__EMPTY_LINE__)
        section.props.append(("NextCurves", ["ii", tuple(self.__next_curves)]))
        section.props.append(("PrevCurves", ["ii", tuple(self.__prev_curves)]))
        section.props.append(__EMPTY_LINE__)
        section.props.append(("Length", ["&", (self.__length,)]))
        section.props.append(__EMPTY_LINE__)

        section.sections.append(self.__bezier.get_as_section())

        return section
