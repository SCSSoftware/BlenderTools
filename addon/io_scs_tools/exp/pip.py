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

# Copyright (C) 2013-2014: SCS Software

import bpy
from mathutils import Vector
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_tools_version as _get_tools_version
from io_scs_tools.utils.info import get_blender_version as _get_blender_version


def _fill_header_section(file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 2))
    blender_version, blender_build = _get_blender_version()
    section.props.append(("Source", "Blender " + blender_version + blender_build + ", SCS Blender Tools: " + str(_get_tools_version())))
    section.props.append(("Type", "Prefab"))
    section.props.append(("Name", file_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(nodes, terrain_points, signs, spawn_points, traffic_lights, nav_curves, map_points, trigger_points,
                         nav_curves_intersections):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("NodeCount", nodes))
    section.props.append(("TerrainPointCount", terrain_points))
    section.props.append(("NavCurveCount", nav_curves))
    section.props.append(("SignCount", signs))
    section.props.append(("SpawnPointCount", spawn_points))
    section.props.append(("SemaphoreCount", traffic_lights))
    section.props.append(("MapPointCount", map_points))
    section.props.append(("TriggerPointCount", trigger_points))
    section.props.append(("IntersectionCount", nav_curves_intersections))
    return section


def _fill_node_sections(data_list, offset_matrix):
    """Fills up "Node" sections."""
    sections = []
    for item in data_list:
        section = _SectionData("Node")
        section.props.append(("Index", int(item.scs_props.locator_prefab_con_node_index)))
        loc = _convert_utils.convert_location_to_scs(item.location, offset_matrix)
        section.props.append(("Position", ["&&", loc]))
        direction = _convert_utils.scs_to_blend_matrix().inverted() * (item.matrix_world.to_quaternion() * Vector((0, 1, 0)))
        section.props.append(("Direction", ["&&", direction]))
        # print('p_locator_lanes: %s' % item.scs_props.p_locator_lanes)

        # lane_input_values = []
        # lane_output_values = []
        # for lane_num in range(item.scs_props.p_locator_lanes):
        # if lane_num:
        # lane_input_values.append(lane_num)
        # lane_output_values.append(lane_num)
        # else:
        # lane_input_values.append(-1)
        # lane_output_values.append(-1)
        section.props.append(("InputLanes", ["ii", (-1, -1, -1, -1, -1, -1, -1, -1)]))
        # section.props.append(("InputLanes", lane_input_values))
        section.props.append(("OutputLanes", ["ii", (-1, -1, -1, -1, -1, -1, -1, -1)]))
        # section.props.append(("OutputLanes", lane_output_values))
        section.props.append(("TerrainPointCount", 0))
        section.props.append(("StreamCount", 0))
        section.props.append(("", ""))
        # section.props.append(("__EMPTY_LINE__", 0))
        sections.append(section)
    return sections


def _fill_sign_sections(data_list, scs_sign_model_inventory):
    """Fills up "Sign" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("Sign")
        section.props.append(("Name", _name_utils.tokenize_name(item.name)))
        loc, qua, sca = _convert_utils.get_scs_transformation_components(item.matrix_world)
        section.props.append(("Position", ["&&", loc]))
        section.props.append(("Rotation", ["&&", qua]))
        if item.scs_props.locator_prefab_sign_model:
            model = scs_sign_model_inventory[item.scs_props.locator_prefab_sign_model].item_id
        else:
            model = ""
        section.props.append(("Model", model))
        section.props.append(("Part", item.scs_props.scs_part))
        sections.append(section)
    return sections


def _fill_spawn_point_sections(data_list):
    """Fills up "Spawn Point" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("SpawnPoint")
        section.props.append(("Name", _name_utils.tokenize_name(item.name)))
        loc, qua, sca = _convert_utils.get_scs_transformation_components(item.matrix_world)
        section.props.append(("Position", ["&&", loc]))
        section.props.append(("Rotation", ["&&", qua]))
        section.props.append(("Type", int(item.scs_props.locator_prefab_spawn_type)))
        sections.append(section)
    return sections


def _fill_semaphore_sections(data_list, scs_tsem_profile_inventory):
    """Fills up "Traffic Semaphore" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        # section = data_structures.section_data("TrafficLight")
        section = _SectionData("Semaphore")
        loc, qua, sca = _convert_utils.get_scs_transformation_components(item.matrix_world)
        section.props.append(("Position", ["&&", loc]))
        section.props.append(("Rotation", ["&&", qua]))
        section.props.append(("Type", int(item.scs_props.locator_prefab_tsem_type)))
        if item.scs_props.locator_prefab_tsem_id == 'none':
            item_id = -1
        else:
            item_id = int(item.scs_props.locator_prefab_tsem_id)
        section.props.append(("SemaphoreID", item_id))
        if item.scs_props.locator_prefab_tsem_type == '6':
            section.props.append(("Intervals", ["&&", (
                item.scs_props.locator_prefab_tsem_gm, item.scs_props.locator_prefab_tsem_om1, item.scs_props.locator_prefab_tsem_rm,
                item.scs_props.locator_prefab_tsem_om1)]))
        else:
            section.props.append(("Intervals", ["&&", (
                item.scs_props.locator_prefab_tsem_gs, item.scs_props.locator_prefab_tsem_os1, item.scs_props.locator_prefab_tsem_rs,
                item.scs_props.locator_prefab_tsem_os2)]))
        section.props.append(("Cycle", ["&", (item.scs_props.locator_prefab_tsem_cyc_delay, )]))
        # section.props.append(("Model", item.scs_props.locator_prefab_tsem_model))
        # section.props.append(("Profile", item.scs_props.locator_prefab_tsem_profile))
        if item.scs_props.locator_prefab_tsem_profile:
            profile = scs_tsem_profile_inventory[item.scs_props.locator_prefab_tsem_profile].item_id
        else:
            profile = ""
        section.props.append(("Profile", profile))
        sections.append(section)
    return sections


def _fill_nav_curve_sections(nav_point_list, offset_matrix):
    """Fills up (navigation) "Curve" sections."""

    _INDEX = "index"
    _START = "start"
    _END = "end"
    _PREV_CURVES = "prev_curves"
    _NEXT_CURVES = "next_curves"

    curves_dict = _connections_group_wrapper.get_curves(nav_point_list, _INDEX, _START, _END, _NEXT_CURVES, _PREV_CURVES)

    # prepare empty sections for curves so it can be later placed directly on right index
    sections = [_SectionData("Dummy")] * len(curves_dict)
    for connection_key in curves_dict.keys():

        curve = curves_dict[connection_key]

        start_loc = bpy.data.objects[curve[_START]]
        end_loc = bpy.data.objects[curve[_END]]

        section = _SectionData("Curve")
        section.props.append(("Index", curve[_INDEX]))
        section.props.append(("Name", _name_utils.tokenize_name(curve[_START])))
        section.props.append(("", ""))
        section.props.append(("#", "Flags:"))
        section.props.append(("Flags", _get_np_flags(start_loc, end_loc)))
        section.props.append(("", ""))
        section.props.append(("LeadsToNodes", 0))  # TODO SIMON: make it happen when you know what it means

        speed_limit = _get_np_speed_limit(start_loc)
        if speed_limit:
            section.props.append(("", ""))
            section.props.append(("SpeedLimit", ["&", ]))

        traffic_light = _get_np_traffic_light_id(start_loc)
        if traffic_light != -1:
            section.props.append(("", ""))
            section.props.append(("TrafficLightID", ))

        section.props.append(("", ""))
        section.props.append(("NextCurves", ["ii", _get_np_prev_next_curves(curves_dict, curve[_NEXT_CURVES], _INDEX)]))
        section.props.append(("PrevCurves", ["ii", _get_np_prev_next_curves(curves_dict, curve[_PREV_CURVES], _INDEX)]))
        section.props.append(("", ""))
        section.props.append(("Length", ["&", (_get_np_length(start_loc, end_loc), )]))
        section.props.append(("", ""))
        bezier_section = _SectionData("Bezier")

        # START NODE
        start_section = _SectionData("Start")
        loc = _convert_utils.convert_location_to_scs(start_loc.location, offset_matrix)
        start_section.props.append(("Position", ["&&", loc]))
        direction_vector = _convert_utils.scs_to_blend_matrix().inverted() * (start_loc.matrix_world.to_quaternion() * Vector((0, 1, 0)))
        start_section.props.append(("Direction", ["&&", (direction_vector[0], direction_vector[1], direction_vector[2])]))

        # END NODE
        end_section = _SectionData("End")
        loc = _convert_utils.convert_location_to_scs(end_loc.location, offset_matrix)
        end_section.props.append(("Position", ["&&", loc]))
        direction_vector = _convert_utils.scs_to_blend_matrix().inverted() * (end_loc.matrix_world.to_quaternion() * Vector((0, 1, 0)))
        end_section.props.append(("Direction", ["&&", (direction_vector[0], direction_vector[1], direction_vector[2])]))

        bezier_section.sections.append(start_section)
        bezier_section.sections.append(end_section)
        section.sections.append(bezier_section)

        # make sure that current section is placed on right place
        sections[curve[_INDEX]] = section

    return sections


def _fill_nav_curve_intersections_sections(nav_curve_sections):
    # for nav_curve_section in nav_curve_sections:
    # print(' > nav_curve_sections: %s' % str(nav_curve_section))
    curve_dict = _curve_utils.compute_curve_intersections(nav_curve_sections)
    sections = []
    for data_dict in curve_dict:
        # if dict == 'START':
        # if dict == 'END':
        # if dict == 'CROSS':
        for rec in curve_dict[data_dict]:
            name = "__name__"
            index = None
            nav_curve_section = rec[0]
            '''
            NOTE: skipped because currently not supported
            curve_to_test = rec[1]
            '''
            curve_intersect = rec[2]
            # print('%r - curve_to_test: %s - curve_intersect: %s' % (dict, str(curve_to_test), str(curve_intersect)))
            for prop in nav_curve_section.props:
                # print(' prop: %r - val: %s' % (str(prop[0]), str(prop[1])))
                if prop[0] == "":
                    pass
                elif prop[0] == "Name":
                    name = prop[1]
                elif prop[0] == "Index":
                    index = prop[1]
            section = _SectionData("Intersection")
            section.props.append(("#", str("Curve '" + name + "'")))
            section.props.append(("InterCurveID", index))
            section.props.append(("InterPosition", float(curve_intersect)))
            section.props.append(("InterRadius", float(0)))
            section.props.append(("Flags", 0))
            sections.append(section)
    return sections


def _fill_map_point_sections(mp_locators, offset_matrix):
    """Fills up "Map Point" sections."""
    sections = []

    # print('map_loc_connection_list: %s' % str(map_loc_connection_list))
    for loc_obj in mp_locators:
        section = _SectionData("MapPoint")
        section.props.append(("MapVisualFlags", _get_mp_visual_flags(loc_obj)))
        section.props.append(("MapNavFlags", _get_mp_nav_flags(loc_obj)))

        loc = _convert_utils.convert_location_to_scs(loc_obj.location, offset_matrix)
        loc.y = 0  # Y location for map points should always be exported as zero
        section.props.append(("Position", ["&&", loc]))
        section.props.append(("Neighbours", ["ii", _get_mp_neigbours(mp_locators, loc_obj)]))

        sections.append(section)
    return sections


def _fill_trigger_point_sections(tp_locators, offset_matrix):
    """Fills up "Trigger Point" sections."""
    sections = []
    for loc_index, loc_obj in enumerate(tp_locators):
        section = _SectionData("TriggerPoint")
        section.props.append(("TriggerID", loc_index))
        section.props.append(("TriggerAction", loc_obj.scs_props.locator_prefab_tp_action))
        section.props.append(("TriggerRange", loc_obj.scs_props.locator_prefab_tp_range))
        section.props.append(("TriggerResetDelay", loc_obj.scs_props.locator_prefab_tp_reset_delay))
        section.props.append(("TriggerResetDist", 0.0))  # constant
        section.props.append(("Flags", 0))
        loc = _convert_utils.convert_location_to_scs(loc_obj.location, offset_matrix)
        section.props.append(("Position", ["&&", loc]))
        section.props.append(("Neighbours", ["ii", _get_tp_neigbours(tp_locators, loc_obj)]))
        sections.append(section)
    return sections


def _locator_prefab_tsem_activation(item):
    """Takes a traffic light object and returns a bitflag number of its activation type."""
    number = 0
    tsem_activation = int(item.scs_props.locator_prefab_tsem_activation)
    if tsem_activation == 'auto':
        number |= 0x0000  # Automatic Timed
    if tsem_activation == 'man':
        number |= 0x0001  # Manual Timed
    if tsem_activation == 'dis':
        number |= 0x0002  # Mover Distance
    # activation_type_mask = 0x00FF
    # ai_only              = 0x0100
    return number


def _get_np_flags(start_obj, end_obj):
    """Takes start and end navigation curve nodes and returns a bitflag number."""
    number = 0
    if start_obj.scs_props.locator_prefab_np_stopper:
        number |= 0x00000001
    if start_obj.scs_props.locator_prefab_np_low_prior and end_obj.scs_props.locator_prefab_np_low_prior:
        number |= 0x00000002
    if end_obj.scs_props.locator_prefab_np_allowed_veh == 'to':
        number |= 0x00000004  # Trucks Only
    if start_obj.scs_props.locator_prefab_np_blinker == 'rb':
        number |= 0x00000008  # Right Blinker
    if start_obj.scs_props.locator_prefab_np_blinker == 'lb':
        number |= 0x00000010  # Left Blinker
    if start_obj.scs_props.locator_prefab_np_crossroad and end_obj.scs_props.locator_prefab_np_crossroad:
        number |= 0x00000200
    if end_obj.scs_props.locator_prefab_np_allowed_veh == 'nt':
        number |= 0x00000400  # No Trucks
    if start_obj.scs_props.locator_prefab_np_tl_activ:
        number |= 0x00000800
    if end_obj.scs_props.locator_prefab_np_allowed_veh == 'po':
        number |= 0x00001000  # Player Only
    if end_obj.scs_props.locator_prefab_np_low_probab:
        number |= 0x00002000
    if start_obj.scs_props.locator_prefab_np_ig_blink_prior:
        number |= 0x00004000
    if start_obj.scs_props.locator_prefab_np_add_priority:
        number |= 0x00008000  # Additive Priority
    # if start_obj.scs_props.locator_prefab_np_priority_mask == 'mask': number |= 0x000F0000 ## PRIORITY MASK
    return number


def _get_np_leads_to_nodes(nav_curve_table):
    # Now for the more difficult part. Every curve leads to the same nodes as it's child curves.
    # So we have to propagate the leads_to_nodes state from the output nodes back to the input nodes.
    # This can be done in O(n) time, right? But it's too complicated for me.
    # Let's try it with this stupid O(n^2) algorithm. Traverse all curves and copy the leads_to_state from the child
    # to parent curve. Repeat it until the information reaches the input nodes (n times - where the n is the number
    # of the curves - in the worst scenario).

    # for (unsigned zz = 0; zz < global_nav_curve_count; ++zz) {
    # for (unsigned i = 0; i < global_nav_curve_count; ++i) {
    # for (unsigned j = 0; j < prism::NAVIGATION_NEXT_PREV_MAX; ++j) {
    # prism::u32 next = nav_curves[i].next_curves[j];
    # if (next != prism::NILU) {
    # nav_curves[i].leads_to_nodes |= nav_curves[next].leads_to_nodes;
    # }
    # }
    # }
    # }

    # for zz in enumerate(nav_curve_table):
    # for i in enumerate(nav_curve_table):
    # for j in enumerate(NAVIGATION_NEXT_PREV_MAX):
    # next_node = nav_curves[i].next_curves[j]
    # if next_node != -1:
    # nav_curves[i].leads_to_nodes |= nav_curves[next_node].leads_to_nodes

    leads_to_nodes_dict = {}
    for curve in nav_curve_table:
        leads_to_nodes_dict[curve] = 0

    for prnt_curve in nav_curve_table:
        for chld_curve in nav_curve_table:
            next_prnt_curves = nav_curve_table[prnt_curve]["next_curves"]
            # next_chld_curves = nav_curve_table[chld_curve]["next_curves"]
            # print("prnt_curve %s: %s\nchld_curve %s: %s\n" % (str(prnt_curve), str(next_prnt_curves), str(chld_curve), str(next_chld_curves)))
            if chld_curve in next_prnt_curves:
                # print('  ch: %s - par: %s\n' % (str(chld_curve), str(next_prnt_curves)))
                leads_to_nodes_dict[prnt_curve] += 1

    for item in leads_to_nodes_dict:
        print("  %s: %s" % (str(item), str(leads_to_nodes_dict[item])))

    return leads_to_nodes_dict  # TODO: NOT CORRECT RESULTS !!!


def _get_np_speed_limit(obj):
    result = None

    if abs(obj.scs_props.locator_prefab_np_speed_limit) < 0.001:
        result = obj.scs_props.locator_prefab_np_speed_limit

    return result


def _get_np_traffic_light_id(obj):
    result = int(obj.scs_props.locator_prefab_np_traffic_light)
    return result


def _get_np_length(start_obj, end_obj):
    point1 = Vector(start_obj.location)
    tang1 = start_obj.matrix_world.to_quaternion() * Vector((0, 1, 0))
    point2 = Vector(end_obj.location)
    tang2 = end_obj.matrix_world.to_quaternion() * Vector((0, 1, 0))
    result = _curve_utils.compute_smooth_curve_length(point1, tang1, point2, tang2, 300)
    return result


def _get_np_prev_next_curves(curves_dict, prev_or_next_curves_keys, index_key):
    next_curves = []
    for prev_or_next_curve in prev_or_next_curves_keys:
        next_curves.append(curves_dict[prev_or_next_curve][index_key])  # fill up actual curve index

    while len(next_curves) < 4:
        next_curves.append(-1)

    return next_curves


def _get_mp_visual_flags(item):
    number = 0
    if item.scs_props.locator_prefab_mp_road_size == 'ow':
        number |= 0x00000000  # One Way
    elif item.scs_props.locator_prefab_mp_road_size == '1 lane':
        number |= 0x00000100  # 1 - Lane
    elif item.scs_props.locator_prefab_mp_road_size == '2 lane':
        number |= 0x00000200  # 2 - Lane
    elif item.scs_props.locator_prefab_mp_road_size == '3 lane':
        number |= 0x00000300  # 3 - Lane
    elif item.scs_props.locator_prefab_mp_road_size == '4 lane':
        number |= 0x00000400  # 4 - Lane
    elif item.scs_props.locator_prefab_mp_road_size == 'poly':
        number |= 0x00000D00  # Manual = Polygon (???)
    elif item.scs_props.locator_prefab_mp_road_size == 'auto':
        number |= 0x00000E00  # Auto
    # if item.scs_props.locator_prefab_mp_road_size == 'mask': number |= 0x00000F00  # SIZE MASK

    if item.scs_props.locator_prefab_mp_road_offset == '0m':
        number |= 0x00000000  # 0m
    if item.scs_props.locator_prefab_mp_road_offset == '1m':
        number |= 0x00001000  # 1m
    if item.scs_props.locator_prefab_mp_road_offset == '2m':
        number |= 0x00002000  # 2m
    if item.scs_props.locator_prefab_mp_road_offset == '5m':
        number |= 0x00003000  # 5m
    if item.scs_props.locator_prefab_mp_road_offset == '10m':
        number |= 0x00004000  # 10m
    if item.scs_props.locator_prefab_mp_road_offset == '15m':
        number |= 0x00005000  # 15m
    if item.scs_props.locator_prefab_mp_road_offset == '20m':
        number |= 0x00006000  # 20m
    if item.scs_props.locator_prefab_mp_road_offset == '25m':
        number |= 0x00007000  # 25m
    # if item.scs_props.locator_prefab_mp_road_offset == 'mask': number |= 0x0000F000  # OFFSET MASK

    if item.scs_props.locator_prefab_mp_road_over:
        number |= 0x00010000

    if item.scs_props.locator_prefab_mp_custom_color == 'light':
        number |= 0x00020000  # Light
    if item.scs_props.locator_prefab_mp_custom_color == 'dark':
        number |= 0x00040000  # Dark
    if item.scs_props.locator_prefab_mp_custom_color == 'green':
        number |= 0x00080000  # Green

    if item.scs_props.locator_prefab_mp_no_outline:
        number |= 0x00100000
    if item.scs_props.locator_prefab_mp_no_arrow:
        number |= 0x00200000

    # road_size_one_way       = 0x00000000
    # road_size_1_lane        = 0x00000100
    # road_size_2_lane        = 0x00000200
    # road_size_3_lane        = 0x00000300
    # road_size_4_lane        = 0x00000400
    # road_size_manual        = 0x00000D00
    # road_size_auto          = 0x00000E00
    # road_size_mask          = 0x00000F00

    # road_offset_0           = 0x00000000
    # road_offset_1           = 0x00001000
    # road_offset_2           = 0x00002000
    # road_offset_5           = 0x00003000
    # road_offset_10          = 0x00004000
    # road_offset_15          = 0x00005000
    # road_offset_20          = 0x00006000
    # road_offset_25          = 0x00007000
    # road_offset_mask        = 0x0000F000

    # road_ext_value_mask     = 0x000000FF

    # road_over               = 0x00010000

    # custom_color1           = 0x00020000
    # custom_color2           = 0x00040000
    # custom_color3           = 0x00080000

    # no_outline              = 0x00100000
    # no_arrow                = 0x00200000

    return number


def _get_mp_nav_flags(item):
    number = 0
    if item.scs_props.locator_prefab_mp_assigned_node == 'none':
        number |= 0x00000000  # None

    if item.scs_props.locator_prefab_mp_des_nodes_0:
        number |= 0x00000001  # 0
    if item.scs_props.locator_prefab_mp_des_nodes_1:
        number |= 0x00000002  # 1
    if item.scs_props.locator_prefab_mp_des_nodes_2:
        number |= 0x00000004  # 2
    if item.scs_props.locator_prefab_mp_des_nodes_3:
        number |= 0x00000008  # 3
    # if item.scs_props.locator_prefab_mp_des_nodes_4: number |= 0x00000010  # 4
    # if item.scs_props.locator_prefab_mp_des_nodes_5: number |= 0x00000020  # 5
    # if item.scs_props.locator_prefab_mp_des_nodes_6: number |= 0x00000040  # 6

    if item.scs_props.locator_prefab_mp_des_nodes_ct:
        number |= 0x00000080  # Custom target

    # if item.scs_props.locator_prefab_mp_assigned_node == 'all': number |= 0x000000FF  # All

    # if item.scs_props.... == 'mask': number |= 0x000000FF  # MASK (???)

    if item.scs_props.locator_prefab_mp_assigned_node not in ('none', 'all'):
        number |= 0x00000100

    if item.scs_props.locator_prefab_mp_prefab_exit:
        number |= 0x00000400

    # nav_node_0              = 0x00000001
    # nav_node_1              = 0x00000002
    # nav_node_2              = 0x00000004
    # nav_node_3              = 0x00000008
    # nav_node_4              = 0x00000010
    # nav_node_5              = 0x00000020
    # nav_node_6              = 0x00000040
    #
    # nav_node_custom_target  = 0x00000080
    #
    # nav_node_all            = 0x000000FF
    #
    # nav_node_mask           = 0x000000FF
    #
    # nav_node_start          = 0x00000100
    #
    # nav_base                = 0x00000200
    #
    # prefab_exit             = 0x00000400

    return number


def _get_mp_neigbours(mp_list, loc_obj):
    """Gets the neigbours indexes of given Map Point locators. Indexes are gotten from
    given map point list

    :param mp_list: list of map point locators which will be written in file
    :type mp_list: list of bpy.types.Object
    :param loc_obj: map point locator for which we want to get the neighbours
    :type loc_obj: bpy.types.Object
    :return: indexes of neighbour locators
    :rtype: list
    """

    neigbours = []

    for neigbour in _connections_group_wrapper.get_neighbours(loc_obj):
        # get the actual index of the neighbour MapPoint section in sections list
        neigbours.append(mp_list.index(bpy.data.objects[neigbour]))

    # fill up empty neighbours
    while len(neigbours) < 6:
        neigbours.append(-1)

    return neigbours


def _get_tp_neigbours(tp_list, loc_obj):
    """Gets the neigbours indexes of given Trigger Point locators. Indexes are gotten from
    given trigger point list

    :param tp_list: list of trigger point locators which will be written in file
    :type tp_list: list of bpy.types.Object
    :param loc_obj: trigger point locator for which we want to get the neighbours
    :type loc_obj: bpy.types.Object
    :return: indexes of neighbour locators
    :rtype: list
    """

    neigbours = []

    for neigbour in _connections_group_wrapper.get_neighbours(loc_obj):
        # get the actual index of the neighbour MapPoint section in sections list
        neigbours.append(tp_list.index(bpy.data.objects[neigbour]))

    # fill up empty neighbours
    while len(neigbours) < 2:
        neigbours.append(-1)

    return neigbours


def export(prefab_locator_list, filepath, filename, offset_matrix):
    scs_globals = _get_scs_globals()

    # CLEANUP CONNECTIONS DATA
    _connections_group_wrapper.cleanup_on_export()

    print("\n************************************")
    print("**      SCS PIP Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    node_list = []
    terrain_point_list = []
    sign_list = []
    spawn_point_list = []
    traffic_light_list = []
    nav_point_list = []
    map_point_list = []
    trigger_point_list = []
    for locator in prefab_locator_list:
        # print('locator: "%s"' % str(locator.scs_props.locator_prefab_type))
        if locator.scs_props.locator_prefab_type == 'Control Node':
            node_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Sign':
            sign_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Spawn Point':
            spawn_point_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Traffic Semaphore':
            traffic_light_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Navigation Point':
            nav_point_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Map Point':
            map_point_list.append(locator)
        elif locator.scs_props.locator_prefab_type == 'Trigger Point':
            trigger_point_list.append(locator)

    # DATA CREATION
    header_section = _fill_header_section(filename, scs_globals.sign_export)
    node_sections = _fill_node_sections(node_list, offset_matrix)
    sign_sections = _fill_sign_sections(sign_list, scs_globals.scs_sign_model_inventory)
    spawn_point_sections = _fill_spawn_point_sections(spawn_point_list)
    traffic_light_sections = _fill_semaphore_sections(traffic_light_list, scs_globals.scs_tsem_profile_inventory)
    nav_curve_sections = _fill_nav_curve_sections(nav_point_list, offset_matrix)
    map_point_sections = _fill_map_point_sections(map_point_list, offset_matrix)
    trigger_point_sections = _fill_trigger_point_sections(trigger_point_list, offset_matrix)
    # nav_curve_intersections_sections = _fill_nav_curve_intersections_sections(nav_curve_sections)
    global_section = _fill_global_section(
        len(node_list),
        len(terrain_point_list),
        len(sign_list),
        len(spawn_point_list),
        len(traffic_light_list),
        len(nav_curve_sections),
        len(map_point_list),
        len(trigger_point_list),
        0  # len(nav_curve_intersections_sections)
    )

    # DATA ASSEMBLING
    pip_container = [header_section, global_section]
    for section in node_sections:
        pip_container.append(section)
    for section in nav_curve_sections:
        pip_container.append(section)
    for section in sign_sections:
        pip_container.append(section)
    for section in spawn_point_sections:
        pip_container.append(section)
    for section in traffic_light_sections:
        pip_container.append(section)
    for section in map_point_sections:
        pip_container.append(section)
    for section in trigger_point_sections:
        pip_container.append(section)
    # for section in nav_curve_intersections_sections:
    # pip_container.append(section)

    # FILE EXPORT
    ind = "    "
    pip_filepath = str(filepath + ".pip")
    result = _pix_container.write_data_to_file(pip_container, pip_filepath, ind)

    # print("************************************")
    return result