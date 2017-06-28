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
from mathutils import Vector
from mathutils.geometry import distance_point_to_plane
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.exp.pip.node_stream import Stream
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.math import get_distance
from io_scs_tools.utils.printout import lprint


class Node:
    _NORMAL_KEY = "nor"
    _POSITION_KEY = "pos"

    __global_node_counter = 0
    __global_tp_counter = 0
    __global_tp_variant_counter = 0

    @staticmethod
    def reset_counter():
        Node.__global_node_counter = 0
        Node.__global_tp_counter = 0
        Node.__global_tp_variant_counter = 0

    @staticmethod
    def get_global_node_count():
        return Node.__global_node_counter

    @staticmethod
    def get_global_tp_count():
        return Node.__global_tp_counter

    @staticmethod
    def get_global_tp_variant_count():
        return Node.__global_tp_variant_counter

    def __init__(self, index, position, direction):
        """Constructs Node for PIP.

        :param index: index of node in PIP file
        :type index: int
        :param position: global position of the locator in SCS coordinates
        :type position: tuple | Vector
        :param direction: absolute rotation of the locator in SCS coordinates
        :type direction: tuple | Vector
        """

        self.__index = index
        self.__position = position
        self.__direction = direction
        self.__input_lanes = [-1] * _PL_consts.PREFAB_LANE_COUNT_MAX
        self.__output_lanes = [-1] * _PL_consts.PREFAB_LANE_COUNT_MAX

        self.__terrain_point_count = 0
        self.__terrain_point_variant_count = 0

        self.__stream_count = 0
        self.__tp_streams = OrderedDict()
        """:type : dict[str, Stream]"""

        self.__tp_per_variant = {}  # saving terrain points per variant index, it gets converted to streams when requesting section
        """:type : dict[int,list[tuple]]"""

        Node.__global_node_counter += 1

        # report maximum node count reach point
        if Node.get_global_node_count() > _PL_consts.PREFAB_NODE_COUNT_MAX:
            lprint("W More than maximum allowed number (max: %s) of Control Nodes will be exported, expect problems in game!",
                   (_PL_consts.PREFAB_NODE_COUNT_MAX,))

    def __prepare_streams__(self):
        """Converts terrain points from variant mapped indices to PIP streams and stores them.
        """

        # first prepare terrain points for export
        self.__prepare_terrain_points__()

        # ensure empty streams
        pos_stream = Stream(Stream.Types.POSITION)
        nor_stream = Stream(Stream.Types.NORMAL)
        variant_stream = Stream(Stream.Types.VARIANT_BLOCK)

        # add points to stream per variant index so terrain points for each variant are saved in one chunk
        #
        # NOTE: apply sorting so we get sorted variant indices from 0 to 0+,
        # because variant index is presented with stream entry index which also goes from 0 to 0+
        for variant_i in sorted(self.__tp_per_variant):  #

            terrain_points = self.__tp_per_variant[variant_i]

            tp_start_index_per_variant = pos_stream.get_size()
            tp_count_per_variant = 0

            for tp in terrain_points:
                pos_stream.add_entry(tp[0])
                nor_stream.add_entry(tp[1])

                tp_count_per_variant += 1

            # add to variant block stream if variant index is real
            if variant_i >= 0:

                if variant_i != variant_stream.get_size():
                    lprint("D Variants block indicies are mixed up in node with index %s, expect problems in game!",
                           (self.__index,))

                variant_stream.add_entry((tp_start_index_per_variant, tp_count_per_variant))

        # finally store stream in node instance
        if pos_stream.get_size() > 0:
            self.__tp_streams[Stream.Types.POSITION] = pos_stream
            self.__tp_streams[Stream.Types.NORMAL] = nor_stream

        if variant_stream.get_size() > 0:
            self.__tp_streams[Stream.Types.VARIANT_BLOCK] = variant_stream

    def __prepare_terrain_points__(self):
        """Reverses the order of terrain points if last point is closer to the node in it's forward direction.
        """

        for variant_index in self.__tp_per_variant:

            # now if tail is closer to node on it's forward axis, we reverse list
            plane_co = Vector(self.__position)
            plane_no = Vector(self.__direction)

            head_distance = distance_point_to_plane(self.__tp_per_variant[variant_index][0][0], plane_co, plane_no)
            tail_distance = distance_point_to_plane(self.__tp_per_variant[variant_index][-1][0], plane_co, plane_no)

            if not (head_distance <= tail_distance - 0.001):  # 0.001 taken from Maya exporter
                self.__tp_per_variant[variant_index].reverse()

    def set_input_lane(self, index, curve_index):
        """Set the curve index for given input lane.

        NOTE: there is no safety check for curve index, so if curve won't exist
        in PIP file data will be invalid

        :param index: index of lane (0 - inner most)
        :type index: int
        :param curve_index: curve index in exported data
        :type curve_index: int
        :return: True if input lane is properly set; False if lane index is out of range
        :rtype: bool
        """

        if index < 0 or index >= _PL_consts.PREFAB_LANE_COUNT_MAX:
            lprint("D Input lane index out of range, expected [0-%s]; got index: %s", (_PL_consts.PREFAB_LANE_COUNT_MAX, index,))
            return False

        if self.__input_lanes[index] != -1:
            lprint("W Multiple curves use Boundary: 'Input - Lane %s' on Boundary Node: %s, only one will be used!",
                   (index, self.__index))

        self.__input_lanes[index] = curve_index
        return True

    def set_output_lane(self, index, curve_index):
        """Set the curve index for given output lane.

        NOTE: there is no safety check for curve index, so if curve won't exist
        in PIP file data will be invalid

        :param index: index of lane (0 - inner most)
        :type index: int
        :param curve_index: curve index in exported data
        :type curve_index: int
        :return: True if outpuit lane is properly set; False if lane index is out of range
        :rtype: bool
        """

        if index < 0 or index >= _PL_consts.PREFAB_LANE_COUNT_MAX:
            lprint("D Output lane index out of range, expected [0-%s]; got index: %s", (_PL_consts.PREFAB_LANE_COUNT_MAX, index,))
            return False

        if self.__output_lanes[index] != -1:
            lprint("W Multiple curves use Boundary: 'Output - Lane %s' on Boundary Node: %s, only one will be used!",
                   (index, self.__index))

        self.__output_lanes[index] = curve_index
        return True

    def add_terrain_point(self, position, normal, variant_index=-1):
        """Adds terrain point to node.

        :param position: position of terrain point
        :type position: tuple | Vector
        :param normal: normal of terrain point
        :type normal: tuple | Vector
        :param variant_index: index of variant from PIT file
        :type variant_index: int
        """

        self.ensure_variant(variant_index)

        # if no position and normal interrupt, also global count remains the same
        if position is None and normal is None:
            return

        # find nearest existing terrain point
        i = 0
        smallest_dist = float("inf")
        smallest_dist_i = 0
        tp_count = len(self.__tp_per_variant[variant_index])
        while i < tp_count:

            pos, normal = self.__tp_per_variant[variant_index][i]
            curr_distance = get_distance(position, pos)
            if curr_distance < smallest_dist:
                smallest_dist = curr_distance
                smallest_dist_i = i

            i += 1

        # depending on distance to closest, previous and next terrain point insert it so that points are sorted already
        if tp_count < 2:  # no terrain points yet or just one just put it at the end

            insert_i = tp_count

        elif smallest_dist_i == 0:  # the nearest is first just put it at start or behind the first one

            next_tp = self.__tp_per_variant[variant_index][smallest_dist_i + 1]
            closest_tp = self.__tp_per_variant[variant_index][smallest_dist_i]

            if get_distance(next_tp[0], position) < get_distance(closest_tp[0], next_tp[0]):
                insert_i = 1
            else:
                insert_i = 0

        elif smallest_dist_i == tp_count - 1:  # last is the nearest put it at the back or before last one

            prev_tp = self.__tp_per_variant[variant_index][smallest_dist_i - 1]
            closest_tp = self.__tp_per_variant[variant_index][smallest_dist_i]

            if get_distance(prev_tp[0], position) < get_distance(closest_tp[0], prev_tp[0]):
                insert_i = smallest_dist_i
            else:
                insert_i = smallest_dist_i + 1

        else:

            # now this is a tricky one: once nearest point is in the middle.
            # With that in mind take previous and next existing points and calculate to which new point is closer.
            # After that also compare distance of next/previous to closest which gives us final answer
            # either point should be inserted before or after closest point.

            prev_tp = self.__tp_per_variant[variant_index][smallest_dist_i - 1]
            closest_tp = self.__tp_per_variant[variant_index][smallest_dist_i]
            next_tp = self.__tp_per_variant[variant_index][smallest_dist_i + 1]

            prev_tp_dist = get_distance(prev_tp[0], position)
            next_tp_dist = get_distance(next_tp[0], position)

            if next_tp_dist < prev_tp_dist and next_tp_dist < get_distance(closest_tp[0], next_tp[0]):
                insert_i = smallest_dist_i + 1
            elif prev_tp_dist > get_distance(closest_tp[0], prev_tp[0]):
                insert_i = smallest_dist_i + 1
            else:
                insert_i = smallest_dist_i

        self.__tp_per_variant[variant_index].insert(insert_i, (position, normal))

        Node.__global_tp_counter += 1

    def ensure_variant(self, variant_index):
        """This ensures variant entry in _VARIANT_BLOCK stream.
        Calling this will result in exporting variant block even
        if no terrain points will be added for this variant

        :param variant_index: index of variant from PIT file
        :type variant_index: int
        """

        if variant_index not in self.__tp_per_variant:
            self.__tp_per_variant[variant_index] = []

            # increment global counter only if actual variant index is passed
            if variant_index >= 0:
                Node.__global_tp_variant_counter += 1

    def get_position(self):
        """Gets node position.

        :return: tuple with node position
        :rtype: tuple[float]
        """
        return tuple(self.__position)

    def get_as_section(self):
        """Get node information represented with SectionData structure class.

        :return: packed node as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        # prepare streams for section representation
        self.__prepare_streams__()

        # update counters
        if Stream.Types.POSITION in self.__tp_streams:
            self.__terrain_point_count = self.__tp_streams[Stream.Types.POSITION].get_size()

        if Stream.Types.VARIANT_BLOCK in self.__tp_streams:
            self.__terrain_point_variant_count = self.__tp_streams[Stream.Types.VARIANT_BLOCK].get_size()

        self.__stream_count = len(self.__tp_streams)

        section = _SectionData("Node")
        section.props.append(("Index", self.__index))
        section.props.append(("Position", ["&&", self.__position]))
        section.props.append(("Direction", ["&&", self.__direction]))
        section.props.append(("InputLanes", ["ii", tuple(self.__input_lanes)]))
        section.props.append(("OutputLanes", ["ii", tuple(self.__output_lanes)]))
        section.props.append(("", ""))  # empty line
        section.props.append(("TerrainPointCount", self.__terrain_point_count))

        if Stream.Types.VARIANT_BLOCK in self.__tp_streams:
            section.props.append(("TerrainPointVariantCount", self.__terrain_point_variant_count))

        section.props.append(("StreamCount", self.__stream_count))

        for stream in self.__tp_streams.values():
            section.sections.append(stream.get_as_section())

        return section
