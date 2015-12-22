from os import path
from mathutils import Vector, Quaternion
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.exp.pip.curve import Curve
from io_scs_tools.exp.pip.globall import Globall
from io_scs_tools.exp.pip.header import Header
from io_scs_tools.exp.pip.intersection import Intersection
from io_scs_tools.exp.pip.map_point import MapPoint
from io_scs_tools.exp.pip.node import Node
from io_scs_tools.exp.pip.semaphore import Semaphore
from io_scs_tools.exp.pip.sign import Sign
from io_scs_tools.exp.pip.spawn_point import SpawnPoint
from io_scs_tools.exp.pip.trigger_point import TriggerPoint
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.utils.convert import get_scs_transformation_components as _get_scs_transformation_components
from io_scs_tools.utils.name import tokenize_name as _tokenize_name
from io_scs_tools.utils.printout import lprint


def __sort_locators_by_type__(locator_list):
    """Sorts prefab locators by the type.

    :param locator_list:
    :type locator_list:
    :return: lists: control nodes, navigation points, signs, spawn points, semaphores, map points, trigger points
    :rtype: tuple[dict[str, bpy.types.Object]]
    """

    control_node_locs = {}
    nav_point_locs = {}
    sign_locs = {}
    spawn_point_locs = {}
    semaphore_locs = {}
    map_point_locs = {}
    trigger_point_locs = {}

    for loc in locator_list:
        if loc.scs_props.locator_prefab_type == "Control Node":
            control_node_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Navigation Point":
            nav_point_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Sign":
            sign_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Spawn Point":
            spawn_point_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Traffic Semaphore":
            semaphore_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Map Point":
            map_point_locs[loc.name] = loc
        elif loc.scs_props.locator_prefab_type == "Trigger Point":
            trigger_point_locs[loc.name] = loc
        else:
            lprint("D Unknown prefab locator type: %r, ignoring it!", (loc.scs_props.locator_prefab_type,))

    return control_node_locs, nav_point_locs, sign_locs, spawn_point_locs, semaphore_locs, map_point_locs, trigger_point_locs


def __get_curve__(pip_curves, index, locator_name):
    """Gets curve class instance entry from given input dictonary. If the entry is not present,
    entry is firstly created in dictionary and then returned.

    :param pip_curves: input dictionary of curve class instances
    :type pip_curves: dict[int, io_scs_tools.exp.pip.curve.Curve]
    :param index: index of curve we are looking for
    :type index: int
    :param locator_name: start locator name
    :type locator_name: str
    :return: curve class instance
    :rtype: io_scs_tools.exp.pip.curve.Curve
    """
    if index not in pip_curves:

        pip_curves[index] = Curve(index, _tokenize_name(locator_name), locator_name)

    return pip_curves[index]


def __get_map_point__(pip_map_points, locator_name):
    """Gets map point class instance entry from given input dictionary. If the entry is not present,
    entry is firstly created in dictionary and then returned.

    :param pip_map_points: input dictionary of map point class instances
    :type pip_map_points: dict[str, io_scs_tools.exp.pip.map_point.MapPoint
    :param locator_name: name of the locator for which map point shall be returned
    :type locator_name: str
    :return: map point class instance
    :rtype: io_scs_tools.exp.pip.map_point.MapPoint
    """
    if locator_name not in pip_map_points:

        pip_map_points[locator_name] = MapPoint(len(pip_map_points), locator_name)

    return pip_map_points[locator_name]


def __get_trigger_point__(pip_trigger_points, locator_name):
    """Gets trigger point class instance entry from given input dictionary. If the entry is not present,
    entry is firstly created in dictionary and then returned.

    :param pip_trigger_points: input dictionary of trigger point class instances
    :type pip_trigger_points: dict[str, io_scs_tools.exp.pip.trigger_point.TriggerPoint
    :param locator_name: name of the locator for which trigger point shall be returned
    :type locator_name: str
    :return: map point class instance
    :rtype: io_scs_tools.exp.pip.trigger_point.TriggerPoint
    """
    if locator_name not in pip_trigger_points:

        pip_trigger_points[locator_name] = TriggerPoint(len(pip_trigger_points), locator_name)

    return pip_trigger_points[locator_name]


def execute(dirpath, filename, prefab_locator_list, offset_matrix, used_terrain_points):
    """Exports PIP file from given locator list.

    :param prefab_locator_list:
    :type prefab_locator_list: list of bpy.types.Object
    :param dirpath: directory export path
    :type dirpath: str
    :param filename: name of PIP file
    :type filename: str
    :param offset_matrix: offset matrix for locators
    :type offset_matrix: mathutils.Matrix
    :param used_terrain_points: terrain points transitional structure for accessing terrain points stored during PIM export
    :type used_terrain_points: io_scs_tools.exp.transition_structs.terrain_points.TerrainPntsTrans
    :return: True if successfull; otherwise False
    :rtype: bool
    """

    # CLEANUP CONNECTIONS DATA
    _connections_group_wrapper.cleanup_on_export()

    print("\n************************************")
    print("**      SCS PIP Exporter          **")
    print("**      (c)2015 SCS Software      **")
    print("************************************\n")

    (control_node_locs,
     nav_point_locs,
     sign_locs,
     spawn_point_locs,
     semaphore_locs,
     map_point_locs,
     trigger_point_locs) = __sort_locators_by_type__(prefab_locator_list)

    pip_header = Header(2, filename)
    pip_global = Globall()

    pip_nodes = {}
    """:type: dict[int,Node]"""
    pip_curves = {}
    """:type: dict[int, Curve]"""
    pip_signs = []
    """:type: list[Sign]"""
    pip_spawn_points = []
    """:type: list[SpawnPoint]"""
    pip_semaphores = []
    """:type: list[Semaphore]"""
    pip_map_points = {}
    """:type: dict[str, MapPoint]"""
    pip_trigger_points = {}
    """:type: dict[str, TriggerPoint]"""
    pip_intersections = [{}, {}, {}]
    """:type: list[dict[str, list[Intersection]]]"""

    # nodes creation
    for locator in control_node_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        curr_node_i = int(locator_scs_props.locator_prefab_con_node_index)
        if curr_node_i not in pip_nodes:

            pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
            rot = Quaternion(rot) * Vector((0, 0, -1))

            # create node with position and direction
            cn = Node(curr_node_i, pos, rot)

            # add terrain points
            terrain_points = used_terrain_points.get(curr_node_i)
            for variant_i in terrain_points:

                # ensure variant entry for no terrain points case
                cn.ensure_variant(variant_i)

                for tp_entry in terrain_points[variant_i]:

                    cn.add_terrain_point(tp_entry.position, tp_entry.normal, variant_i)

            pip_nodes[curr_node_i] = cn
        else:
            lprint("W Multiple Control Nodes with same index detected, only one per index will be exported!\n\t   "
                   "Check Control Nodes in SCS Game Object with Root: %r", (filename,))

    # curves creation
    curves_dict = _connections_group_wrapper.get_curves(nav_point_locs.values())
    for key, curve_entry in curves_dict.items():

        loc0 = nav_point_locs[curves_dict[key].start]
        loc0_scs_props = loc0.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""
        loc1 = nav_point_locs[curves_dict[key].end]
        loc1_scs_props = loc1.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create curve and set properties
        curve = __get_curve__(pip_curves, curve_entry.index, loc0.name)

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * loc0.matrix_world)
        curve.set_start(pos, rot)
        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * loc1.matrix_world)
        curve.set_end(pos, rot)

        curve.set_input_boundaries(loc0_scs_props)
        curve.set_output_boundaries(loc1_scs_props)

        curve.set_flags(loc0.scs_props, True)
        curve.set_flags(loc1.scs_props, False)

        curve.set_semaphore_id(int(loc0_scs_props.locator_prefab_np_traffic_semaphore))
        curve.set_traffic_rule(loc1_scs_props.locator_prefab_np_traffic_rule)

        # set next/prev curves
        for next_key in curve_entry.next_curves:

            next_curve = __get_curve__(pip_curves, curves_dict[next_key].index, curves_dict[next_key].start)

            assert curve.add_next_curve(next_curve)

        for prev_key in curve_entry.prev_curves:

            prev_curve = __get_curve__(pip_curves, curves_dict[prev_key].index, curves_dict[prev_key].start)

            assert curve.add_prev_curve(prev_curve)

        # sync nodes input lanes
        boundary_node_i = curve.get_input_node_index()
        if 0 <= boundary_node_i < _PL_consts.PREFAB_NODE_COUNT_MAX:

            if boundary_node_i in pip_nodes:

                assert pip_nodes[boundary_node_i].set_input_lane(curve.get_input_lane_index(), curve.get_index())

            else:

                lprint("E None existing Boundary Node with index: %s used in Navigation Point: %r",
                       (boundary_node_i, loc0.name,))

        # sync nodes output lanes
        boundary_node_i = curve.get_output_node_index()
        if 0 <= boundary_node_i < _PL_consts.PREFAB_NODE_COUNT_MAX:

            if boundary_node_i in pip_nodes:

                assert pip_nodes[boundary_node_i].set_output_lane(curve.get_output_lane_index(), curve.get_index())

            else:

                lprint("E None existing Boundary Node with index: %s used in Navigation Point: %r",
                       (boundary_node_i, loc1.name,))

    Curve.prepare_curves(pip_curves.values())

    # signs creation
    for locator in sign_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create sign and set properties
        sign = Sign(locator.name, locator_scs_props.scs_part)

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
        sign.set_position(pos)
        sign.set_rotation(rot)

        if ":" in locator_scs_props.locator_prefab_sign_model:
            sign.set_model(locator_scs_props.locator_prefab_sign_model.split(":")[1].strip())
        else:
            lprint("W Invalid Sign Model: %r on locator: %r",
                   (locator_scs_props.locator_prefab_sign_model, locator.name))

        pip_signs.append(sign)

    # spawn points creation
    for locator in spawn_point_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create spawn point and set properties
        spawn_point = SpawnPoint(locator.name)

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
        spawn_point.set_position(pos)
        spawn_point.set_rotation(rot)

        spawn_point.set_type(int(locator_scs_props.locator_prefab_spawn_type))

        pip_spawn_points.append(spawn_point)

    # semaphores creation
    for locator in semaphore_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create semaphore and set properties
        semaphore = Semaphore(int(locator_scs_props.locator_prefab_tsem_type))

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
        semaphore.set_position(pos)
        semaphore.set_rotation(rot)

        semaphore.set_semaphore_id(int(locator_scs_props.locator_prefab_tsem_id))

        if ":" in locator_scs_props.locator_prefab_tsem_profile:
            semaphore.set_profile(locator_scs_props.locator_prefab_tsem_profile.split(":")[1].strip())
        else:
            lprint("W Invalid Profile: %r on Traffic Semaphore locator: %r",
                   (locator_scs_props.locator_prefab_tsem_profile, locator.name))

        semaphore.set_intervals((locator_scs_props.locator_prefab_tsem_gs,
                                 locator_scs_props.locator_prefab_tsem_os1,
                                 locator_scs_props.locator_prefab_tsem_rs,
                                 locator_scs_props.locator_prefab_tsem_os2))
        semaphore.set_cycle(locator_scs_props.locator_prefab_tsem_cyc_delay)

        pip_semaphores.append(semaphore)

    # map points creation
    for locator in map_point_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create map point and set properties
        map_point = __get_map_point__(pip_map_points, locator.name)

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
        map_point.set_position(pos)

        map_point.set_flags(locator_scs_props)

        for neighbour_name in _connections_group_wrapper.get_neighbours(locator):

            assert map_point.add_neighbour(__get_map_point__(pip_map_points, neighbour_name))

    MapPoint.test_map_points(pip_map_points.values())
    MapPoint.auto_generate_map_points(pip_map_points, pip_nodes)

    # trigger points creation
    for locator in trigger_point_locs.values():

        locator_scs_props = locator.scs_props
        """:type: io_scs_tools.properties.object.ObjectSCSTools"""

        # create trigger point and set properties
        trigger_point = __get_trigger_point__(pip_trigger_points, locator.name)

        pos, rot, scale = _get_scs_transformation_components(offset_matrix.inverted() * locator.matrix_world)
        trigger_point.set_position(pos)

        if ":" in locator_scs_props.locator_prefab_tp_action:
            trigger_point.set_action(locator_scs_props.locator_prefab_tp_action.split(":")[1].strip())
        else:
            lprint("W Invalid Action: %r on Trigger Point locator: %r",
                   (locator_scs_props.locator_prefab_tp_action, locator.name))

        trigger_point.set_trigger_range(locator_scs_props.locator_prefab_tp_range)
        trigger_point.set_reset_delay(locator_scs_props.locator_prefab_tp_reset_delay)
        trigger_point.set_flags(locator_scs_props)

        for neighbour_name in _connections_group_wrapper.get_neighbours(locator):

            assert trigger_point.add_neighbour(__get_trigger_point__(pip_trigger_points, neighbour_name))

    TriggerPoint.prepare_trigger_points(pip_trigger_points.values())

    # intersections creation
    for c0_i, c0 in enumerate(pip_curves.values()):
        for c1_i, c1 in enumerate(pip_curves.values()):

            if c1_i <= c0_i:  # only search each pair of curves once
                continue

            # get the intersection point and curves coefficient positions
            intersect_p, c0_pos, c1_pos = Intersection.get_intersection(c0, c1)

            if intersect_p:

                intersect_p_str = str(intersect_p)  # Format: '<Vector (0.0000, 0.0000, 0.0000)>'

                is_start = c0_pos == 0 and c0_pos == c1_pos
                is_end = c1_pos == 1 and c0_pos == c1_pos

                if is_start:
                    inter_type = 0  # fork
                elif is_end:
                    inter_type = 1  # joint
                else:
                    inter_type = 2  # cross

                    # if there is indication of cross intersection filter out intersections with common fork and joint
                    # NOTE: this condition might not be sufficient, so if anyone will have problems,
                    # this is the point that has to be improved
                    if Intersection.have_common_fork(c0, c1) or Intersection.have_common_joint(c0, c1):
                        continue

                # calculate radius for the same directions on curves
                forward_radius = Intersection.get_intersection_radius(c0, c1, c0_pos, c1_pos, 1, 1)
                backward_radius = Intersection.get_intersection_radius(c0, c1, c0_pos, c1_pos, -1, -1)
                final_radius = max(forward_radius, backward_radius)

                # special calculations only for cross intersections
                if inter_type == 2:

                    # calculate radius also for opposite directions
                    final_radius = max(final_radius, Intersection.get_intersection_radius(c0, c1, c0_pos, c1_pos, 1, -1))
                    final_radius = max(final_radius, Intersection.get_intersection_radius(c0, c1, c0_pos, c1_pos, -1, 1))

                    # calculate position of intersection point on curves with better precision
                    c0_pos = c0.get_closest_point(intersect_p)
                    c1_pos = c1.get_closest_point(intersect_p)

                    lprint("D Found cross intersection point: %r", (intersect_p,))

                # creating intersection class instances
                intersection = Intersection(c0.get_index(), c0.get_ui_name(), c0_pos * c0.get_length())
                intersection1 = Intersection(c1.get_index(), c1.get_ui_name(), c1_pos * c1.get_length())

                # init list of intersections for current intersecting point
                if intersect_p_str not in pip_intersections[inter_type]:
                    pip_intersections[inter_type][intersect_p_str] = []

                # append intersections to list and calculate new siblings
                new_siblings = 2
                if intersection not in pip_intersections[inter_type][intersect_p_str]:
                    pip_intersections[inter_type][intersect_p_str].append(intersection)
                else:
                    del intersection
                    new_siblings -= 1

                if intersection1 not in pip_intersections[inter_type][intersect_p_str]:
                    pip_intersections[inter_type][intersect_p_str].append(intersection1)
                else:
                    del intersection1
                    new_siblings -= 1

                # always set flags on first entry in current intersection point list
                # this way siblings count is getting updated properly
                pip_intersections[inter_type][intersect_p_str][0].set_flags(is_start, is_end, new_siblings)

                # update radius on all of intersection in the same intersecting point
                for inter in pip_intersections[inter_type][intersect_p_str]:
                    inter.set_radius(pip_intersections[inter_type][intersect_p_str][0].get_radius())
                    inter.set_radius(final_radius)

    # create container
    pip_container = [pip_header.get_as_section(), pip_global.get_as_section()]

    for node in pip_nodes.values():
        pip_container.append(node.get_as_section())

    for curve_key in sorted(pip_curves):
        pip_container.append(pip_curves[curve_key].get_as_section())

    for sign in pip_signs:
        pip_container.append(sign.get_as_section())

    for spawn_point in pip_spawn_points:
        pip_container.append(spawn_point.get_as_section())

    for semaphore in pip_semaphores:
        pip_container.append(semaphore.get_as_section())

    for map_point in pip_map_points.values():
        pip_container.append(map_point.get_as_section())

    for trigger_point in pip_trigger_points.values():
        pip_container.append(trigger_point.get_as_section())

    for inter_type in range(3):
        for intersect_p_str in pip_intersections[inter_type]:
            for intersection in pip_intersections[inter_type][intersect_p_str]:
                pip_container.append(intersection.get_as_section())

    # write to file
    ind = "    "
    pip_filepath = path.join(dirpath, str(filename + ".pip"))
    result = _pix_container.write_data_to_file(pip_container, pip_filepath, ind)
    return result
