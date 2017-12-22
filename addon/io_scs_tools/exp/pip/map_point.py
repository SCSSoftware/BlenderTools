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

# Copyright (C) 2017: SCS Software

from math import tan, acos
from mathutils import Vector
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class MapPoint:
    __global_map_point_counter = 0

    @staticmethod
    def reset_counter():
        MapPoint.__global_map_point_counter = 0

    @staticmethod
    def get_global_map_point_count():
        return MapPoint.__global_map_point_counter

    @staticmethod
    def auto_generate_map_points(pip_map_points, pip_nodes):
        """Automatically generates base navigation map points,
        either because prefab doesn't have map points at all or
        because we need simple representation for base navigation

        :param pip_map_points: dictonary of already created map point
        :type pip_map_points: dict[str, MapPoint]
        :param pip_nodes: dictionary of nodes used in this prefab
        :type pip_nodes: dict[int, io_scs_tools.exp.pip.node.Node]
        """

        mp_list = []
        """:type: list[io_scs_tools.exp.pip.map_point.MapPoint]"""

        node_count = len(pip_nodes)

        # if only two nodes then - 2 extra map points connected directly
        # otherwise create one extra middle point
        if node_count == 2:

            for i in range(2):
                mp_list.append(MapPoint(len(pip_map_points) + i, "autogen:" + str(i)))

                mp_list[i].set_position(pip_nodes[i].get_position())
                mp_list[i].set_autogen_flags(i, pip_map_points.values())

            mp_list[0].add_neighbour(mp_list[1])
            mp_list[1].add_neighbour(mp_list[0])

        elif node_count >= 3:

            center = Vector()
            aligned_x = None
            aligned_z = None
            middle_p = MapPoint(len(pip_map_points) + node_count, "autogen:" + str(node_count))

            for i in range(node_count):
                mp_list.append(MapPoint(len(pip_map_points) + i, "autogen:" + str(i)))

                curr_n_pos = Vector(pip_nodes[i].get_position())
                next_n_pos = Vector(pip_nodes[(i + 1) % node_count].get_position())

                # try to calculate extra alignment for prefabs with 3 nodes
                if node_count == 3:
                    # if two nodes have similar X coordinate then use aligned coordinate
                    if abs(curr_n_pos.x - next_n_pos.x) < 0.2:
                        aligned_x = (curr_n_pos.x + next_n_pos.x) / 2

                    # if two nodes have similar Z coordinate then use aligned coordinate
                    if abs(curr_n_pos.z - next_n_pos.z) < 0.2:
                        aligned_z = (curr_n_pos.z + next_n_pos.z) / 2

                center += curr_n_pos

                mp_list[i].set_position(curr_n_pos)
                mp_list[i].set_autogen_flags(i, pip_map_points.values())

                # add neighbours
                middle_p.add_neighbour(mp_list[i])
                mp_list[i].add_neighbour(middle_p)

            # calculate final position of middle point
            center /= node_count
            if aligned_x is not None:
                center.x = aligned_x

            if aligned_z is not None:
                center.z = aligned_z

            middle_p.set_position(center)
            middle_p.set_autogen_middle_flags(mp_list)

            # add extra middle point
            mp_list.append(middle_p)

        for map_point in mp_list:

            # store generated map points just by first free integer index
            # as this map points won't be accessed in pip map point dictionary
            i = 0
            while str(i) in pip_map_points:
                i += 1

            pip_map_points[str(i)] = map_point

    @staticmethod
    def calc_segment_extensions(pip_map_points):
        """Calculates segment extensions visual flags for given map points.

        :param pip_map_points: iterable of map points
        :type pip_map_points: collections.Iterable[MapPoint]
        """

        for mp in pip_map_points:

            neighbours = mp.get_neighbours()

            if len(neighbours) < 2:
                continue

            if mp.get_nav_flags() & _PL_consts.MPNF.NAV_NODE_START:
                continue

            for nb1_i, nb1 in enumerate(neighbours):

                dir1 = (Vector(nb1.get_position()) - Vector(mp.get_position())).normalized()

                for i in range(nb1_i + 1, len(neighbours)):

                    nb2 = neighbours[i]
                    dir2 = (Vector(mp.get_position()) - Vector(nb2.get_position())).normalized()
                    mid_vec = (dir1 + dir2).normalized()

                    mid_dot = min(1.0, max(-1.0, dir1.dot(mid_vec)))
                    _tan = tan(acos(mid_dot))

                    ext_flag = int(min(1.0, max(0.0, _tan)) * _PL_consts.MPVF.ROAD_EXT_VALUE_MASK)
                    old_ext_flag = mp.get_visual_flags() & _PL_consts.MPVF.ROAD_EXT_VALUE_MASK

                    if ext_flag and old_ext_flag:
                        mp.set_visual_flag_and(~_PL_consts.MPVF.ROAD_EXT_VALUE_MASK)
                        mp.set_visual_flag_or(min(ext_flag, old_ext_flag))
                    else:
                        mp.set_visual_flag_or(ext_flag)

    @staticmethod
    def test_map_points(pip_map_points):
        """Test map points for validity and print out warnings/errors.
        This has to be called after all map points are created.

        :param pip_map_points: iterable of map points
        :type pip_map_points: collections.Iterable[MapPoint]
        """

        for map_point in pip_map_points:

            is_polygon = map_point.get_visual_flags() & _PL_consts.MPVF.ROAD_SIZE_MASK == _PL_consts.MPVF.ROAD_SIZE_MANUAL
            if is_polygon:

                if map_point.get_nav_flags() != 0:
                    lprint("E Map point %r set as polygon can not have Assigned Node or Destination Nodes",
                           (map_point.get_ui_name(),))

                prev_mp = None
                curr_mp = map_point
                map_point_color = ((map_point.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR1) |
                                   (map_point.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR2) |
                                   (map_point.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR3))

                for i in range(4):

                    curr_neighbours = curr_mp.get_neighbours()
                    if len(curr_neighbours) != 2:
                        lprint("E Polygon map point must have 2 neighbours. Found: %s on map point: %r!",
                               (len(curr_neighbours), curr_mp.get_ui_name()))
                        break

                    new_mp = curr_neighbours[0] if curr_neighbours[0] != prev_mp else curr_neighbours[1]

                    # new map point is not polygon
                    new_mp_is_polygon = new_mp.get_visual_flags() & _PL_consts.MPVF.ROAD_SIZE_MASK == _PL_consts.MPVF.ROAD_SIZE_MANUAL
                    if not new_mp_is_polygon:
                        lprint("W Map point %r is not marked as polygon, but it's connected to polygon!",
                               (new_mp.get_ui_name(),))

                    # new map point is not the same color
                    new_mp_color = ((new_mp.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR1) |
                                    (new_mp.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR2) |
                                    (new_mp.get_visual_flags() & _PL_consts.MPVF.CUSTOM_COLOR3))
                    if new_mp_color != map_point_color:
                        lprint(str("W Map point polygon has assigned more colors, polygon may not be properly colored!"
                                   "\n\t   Check map point: %r"), (new_mp.get_ui_name(),))

                    prev_mp = curr_mp
                    curr_mp = new_mp

                    if curr_mp == map_point and (i == 2 or i == 3):
                        break

                else:  # if valid polygon found (no brake was executed), check if it's really quad
                    if curr_mp != map_point:
                        lprint(str("E Invalid map point polygon detected (only separated quads/tris supported)!"
                                   "\n\t   Check map point: %r"), (map_point.get_ui_name(),))

    def __init__(self, index, ui_name):
        """Constructs MapPoint class instance for PIP file.

        :param index: index  of map point in PIP file
        :param index: int
        :param ui_name: name of the locator used for this map point (only used for debug purpuses)
        :type ui_name: str
        """

        self.__index = index
        self.__map_visual_flags = 0
        self.__map_nav_flags = 0
        self.__position = (0.,) * 3
        self.__neighbours = [-1] * _PL_consts.PREFAB_NODE_COUNT_MAX

        self.__tmp_ui_name = ui_name
        self.__tmp_neighbours = []  # store neighbour instances temporarly

        MapPoint.__global_map_point_counter += 1

    def set_visual_flag_and(self, value):
        """Apply AND binary operator with given value

        :param value: integer which should be applied with AND operator
        :type value: int
        """
        self.__map_visual_flags &= value

    def set_visual_flag_or(self, value):
        """Apply OR binary operator with given value

        :param value: integer which should be applied with OR operator
        :type value: int
        """
        self.__map_visual_flags |= value

    def set_visual_flag(self, scs_props):
        """Sets visual flag to map point.

        :param scs_props: scs props from locator of map point
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        self.__map_visual_flags = 0

        # road over
        if scs_props.locator_prefab_mp_road_over:
            self.__map_visual_flags |= _PL_consts.MPVF.ROAD_OVER

        # no outline
        if scs_props.locator_prefab_mp_no_outline:
            self.__map_visual_flags |= _PL_consts.MPVF.NO_OUTLINE

        # no arrow
        if scs_props.locator_prefab_mp_no_arrow:
            self.__map_visual_flags |= _PL_consts.MPVF.NO_ARROW

        # road size
        self.__map_visual_flags |= int(scs_props.locator_prefab_mp_road_size)

        # road offset
        self.__map_visual_flags |= int(scs_props.locator_prefab_mp_road_offset)

        # custom color
        self.__map_visual_flags |= int(scs_props.locator_prefab_mp_custom_color)

    def set_nav_flag(self, scs_props):
        """Sets navigation flag to map point.

        :param scs_props: scs props from locator of map point
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        self.__map_nav_flags = 0

        # prefab exit
        if scs_props.locator_prefab_mp_prefab_exit:
            self.__map_nav_flags |= _PL_consts.MPNF.PREFAB_EXIT

        # assigned node
        if int(scs_props.locator_prefab_mp_assigned_node) > 0:

            self.__map_nav_flags |= (int(scs_props.locator_prefab_mp_assigned_node) | _PL_consts.MPNF.NAV_NODE_START)

        else:  # otherwise try to set destination nodes

            for dest_node_index in scs_props.locator_prefab_mp_dest_nodes:
                self.__map_nav_flags |= (1 << int(dest_node_index))

    def set_flags(self, scs_props):
        """Set visual and navigation flags.

        :param scs_props: scs props from locator of map point
        :type scs_props: io_scs_tools.properties.object.ObjectSCSTools
        """

        self.set_visual_flag(scs_props)
        self.set_nav_flag(scs_props)

    def set_autogen_flags(self, node_index, original_points):
        """Set flags to autogenerated map point.

        :param node_index: index of the node to which this map point belongs
        :type node_index: int
        :param original_points: iterable of original user created map points
        :type original_points: collections.Iterable[MapPoint]
        """

        self.__map_nav_flags = 0
        self.__map_visual_flags = 0

        node_index_flag = 1 << node_index
        nav_flags = (node_index_flag | _PL_consts.MPNF.NAV_NODE_START)

        self.__map_nav_flags = nav_flags | _PL_consts.MPNF.NAV_BASE

        # setting road size and road offset masks from user created points
        self.__map_visual_flags = _PL_consts.MPVF.ROAD_SIZE_AUTO

        for orig_mp in original_points:

            if orig_mp.get_nav_flags() & nav_flags == nav_flags:

                self.__map_visual_flags = orig_mp.get_visual_flags() & (_PL_consts.MPVF.ROAD_SIZE_MASK |
                                                                        _PL_consts.MPVF.ROAD_OFFSET_MASK)
                break

    def set_autogen_middle_flags(self, auto_gen_points):
        """Set flags to autogenerated middle map point.

        :param auto_gen_points: autogenerated points withoout middle point
        :type auto_gen_points: collections.Iterable[MapPoint]
        """

        self.__map_nav_flags = 0
        self.__map_visual_flags = 0

        # search the largest road size and offset from all neighbours
        for i, autogen_mp in enumerate(auto_gen_points):

            self.__map_nav_flags |= (1 << i) | _PL_consts.MPNF.NAV_BASE

            nb_road_size = autogen_mp.get_visual_flags() & _PL_consts.MPVF.ROAD_SIZE_MASK
            nb_offset = autogen_mp.get_visual_flags() & _PL_consts.MPVF.ROAD_OFFSET_MASK

            if nb_road_size < _PL_consts.MPVF.ROAD_SIZE_MANUAL:

                road_size = self.__map_visual_flags & _PL_consts.MPVF.ROAD_SIZE_MASK
                offset = self.__map_visual_flags & _PL_consts.MPVF.ROAD_OFFSET_MASK

                # clear road size and offset mask bits
                self.__map_visual_flags &= ~(_PL_consts.MPVF.ROAD_SIZE_MASK | _PL_consts.MPVF.ROAD_OFFSET_MASK)

                self.__map_visual_flags |= max(nb_road_size, road_size)
                self.__map_visual_flags |= max(nb_offset, offset)

        # if still not set set it as auto
        if self.__map_visual_flags == 0:
            self.__map_visual_flags = _PL_consts.MPVF.ROAD_SIZE_AUTO

    def set_position(self, position):
        """Sets position of map point.

        NOTE: for game Y component is set to 0, as all map points shall be on zero height

        :param position: position of map point
        :type position: tuple | mathutils.Vector
        """

        if len(position) != 3:
            lprint("D Trying to set invalid position (%s) on Map Point %r; ignoring it.",
                   (position, self.__tmp_ui_name))
            return

        self.__position = (position[0], 0.0, position[2])

    def add_neighbour(self, map_point):
        """Sets given map point index as neigbour.

        :param map_point: neighbour map point
        :type map_point: MapPoint
        :return: True if neighbour can be added; otherwise False
        :rtype: bool
        """

        i = 0
        while i < _PL_consts.PREFAB_NODE_COUNT_MAX and self.__neighbours[i] != -1:
            i += 1

        if i >= _PL_consts.PREFAB_NODE_COUNT_MAX:
            lprint("D Map point neighbours overflow on locator: %s", (self.__tmp_ui_name,))
            return False

        self.__neighbours[i] = map_point.get_index()

        self.__tmp_neighbours.append(map_point)
        return True

    def get_index(self):
        """Gets index of the map point.

        :return: index of map point
        :rtype: int
        """
        return self.__index

    def get_position(self):
        """Gets position of the map point

        :return: position of map point
        :rtype: tuple[float]
        """
        return self.__position

    def get_nav_flags(self):
        """Gets navigation flags of the map point.

        :return: navigation flags
        :rtype: int
        """
        return self.__map_nav_flags

    def get_visual_flags(self):
        """Gets visual flags of the map point.

        :return: visual flags
        :rtype: int
        """
        return self.__map_visual_flags

    def get_neighbours(self):
        """Gets neighbours of this map point.

        :return: list of neighbour map points
        :rtype: list[MapPoint]
        """
        return self.__tmp_neighbours

    def get_ui_name(self):
        """Get UI name of this map point.

        :return: UI name
        :rtype: str
        """
        return self.__tmp_ui_name

    def get_as_section(self):
        """Get map point information represented with SectionData structure class.

        :return: packed map point as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("MapPoint")
        section.props.append(("Index", self.__index))
        section.props.append(("MapVisualFlags", self.__map_visual_flags))
        section.props.append(("MapNavFlags", self.__map_nav_flags))
        section.props.append(("Position", ["&&", tuple(self.__position)]))
        section.props.append(("Neighbours", ["ii", tuple(self.__neighbours)]))

        return section
