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

import math
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.connections.wrappers import group as _group_connections_wrapper
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.printout import handle_unused_arg


def _print_locator_result(loc, loc_type, name):
    if loc:
        lprint('I %s locator "%s" created.', (loc_type, name))
    else:
        lprint('E %s locator "%s" creation failed!', (loc_type, name))


def _get_header(pip_container):
    """Receives PIP container and returns all its Header properties in its own variables.
    For any item that fails to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pip_container:
        if section.type == "Header":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "FormatVersion":
                    format_version = prop[1]
                elif prop[0] == "Source":
                    source = prop[1]
                elif prop[0] == "Type":
                    f_type = prop[1]
                elif prop[0] == "Name":
                    f_name = prop[1]
                elif prop[0] == "SourceFilename":
                    source_filename = prop[1]
                elif prop[0] == "Author":
                    author = prop[1]
                else:
                    lprint('\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, f_name, source_filename, author


def _get_global(pip_container):
    """Receives PIP container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    node_count = terrain_point_count = nav_curve_count = sign_count = spawn_point_count = \
        traffic_light_count = map_point_count = trigger_point_count = intersection_count = None
    for section in pip_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "NodeCount":
                    node_count = prop[1]
                elif prop[0] == "TerrainPointCount":
                    terrain_point_count = prop[1]
                elif prop[0] == "NavCurveCount":
                    nav_curve_count = prop[1]
                elif prop[0] == "SignCount":
                    sign_count = prop[1]
                elif prop[0] == "SpawnPointCount":
                    spawn_point_count = prop[1]
                elif prop[0] == "TrafficLightCount":
                    traffic_light_count = prop[1]
                elif prop[0] == "MapPointCount":
                    map_point_count = prop[1]
                elif prop[0] == "TriggerPointCount":
                    trigger_point_count = prop[1]
                elif prop[0] == "IntersectionCount":
                    intersection_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return (node_count,
            terrain_point_count,
            nav_curve_count,
            sign_count,
            spawn_point_count,
            traffic_light_count,
            map_point_count,
            trigger_point_count,
            intersection_count)


def _get_node_properties(section):
    """Receives a Node section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    node_name = node_index = node_position = node_direction = node_input_lanes = \
        node_output_lanes = node_terpoint_count = node_stream_count = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            node_name = prop[1]
        elif prop[0] == "Index":
            node_index = prop[1]
        elif prop[0] == "Position":
            node_position = prop[1]
        elif prop[0] == "Direction":
            node_direction = prop[1]
        elif prop[0] == "InputLanes":
            node_input_lanes = prop[1]
        elif prop[0] == "OutputLanes":
            node_output_lanes = prop[1]
        elif prop[0] in ("TerPointCount", "TerrainPointCount"):
            node_terpoint_count = prop[1]
        elif prop[0] == "StreamCount":
            node_stream_count = prop[1]
        else:
            lprint('\nW Unknown property in "Node" data: "%s"!', prop[0])
    return (node_name,
            node_index,
            node_position,
            node_direction,
            node_input_lanes,
            node_output_lanes,
            node_terpoint_count,
            node_stream_count)


def _get_sign_properties(section):
    """Receives a Sign section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    sign_name = sign_position = sign_rotation = sign_model = sign_part = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            sign_name = prop[1]
        elif prop[0] == "Position":
            sign_position = prop[1]
        elif prop[0] == "Rotation":
            sign_rotation = prop[1]
        elif prop[0] == "Model":
            sign_model = prop[1]
        elif prop[0] == "Part":
            sign_part = prop[1]
        else:
            lprint('\nW Unknown property in "Sign" data: "%s"!', prop[0])
    return sign_name, sign_position, sign_rotation, sign_model, sign_part


def _get_spawn_properties(section):
    """Receives a Spawn section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    spawn_name = spawn_position = spawn_rotation = spawn_type = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            spawn_name = prop[1]
        elif prop[0] == "Position":
            spawn_position = prop[1]
        elif prop[0] == "Rotation":
            spawn_rotation = prop[1]
        elif prop[0] == "Type":
            spawn_type = prop[1]
        else:
            lprint('\nW Unknown property in "Spawn" data: "%s"!', prop[0])
    return spawn_name, spawn_position, spawn_rotation, spawn_type


def _get_t_light_properties(section):
    """Receives a Traffic Semaphore section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    tsem_name = tsem_position = tsem_rotation = tsem_type = tsem_id = \
        tsem_intervals = tsem_cycle = tsem_model = tsem_profile = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            tsem_name = prop[1]
        elif prop[0] == "Position":
            tsem_position = prop[1]
        elif prop[0] == "Rotation":
            tsem_rotation = prop[1]
        elif prop[0] == "Type":
            tsem_type = prop[1]
        elif prop[0] == "SemaphoreID":
            tsem_id = prop[1]  # former "TrafficLightID"
        elif prop[0] == "Intervals":
            tsem_intervals = prop[1]
        elif prop[0] == "Cycle":
            tsem_cycle = prop[1]
        elif prop[0] == "Model":
            tsem_model = prop[1]
        elif prop[0] == "Profile":
            tsem_profile = prop[1]
        else:
            lprint('\nW Unknown property in "Traffic Semaphore" data: "%s"!', prop[0])
    return (tsem_name,
            tsem_position,
            tsem_rotation,
            tsem_type,
            tsem_id,
            tsem_intervals,
            tsem_cycle,
            tsem_model,
            tsem_profile)


def _get_curve_properties(section):
    """Receives a Curve section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    cur_name = cur_index = cur_flags = cur_leads_to_nodes = cur_speed_limit = cur_traffic_light_id = \
        cur_next_curves = cur_prev_curves = cur_length = bezier_start_pos = bezier_start_dir = \
        bezier_start_qua = bezier_end_pos = bezier_end_dir = bezier_end_qua = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            cur_index = prop[1]
        elif prop[0] == "Name":
            cur_name = prop[1]
        elif prop[0] == "Flags":
            cur_flags = prop[1]
        elif prop[0] == "LeadsToNodes":
            cur_leads_to_nodes = prop[1]
        elif prop[0] == "SpeedLimit":
            cur_speed_limit = prop[1]
        elif prop[0] in ("TrafficLightID", "SemaphoreID"):
            cur_traffic_light_id = prop[1]  # former "TrafficLightID"
        elif prop[0] == "NextCurves":
            cur_next_curves = prop[1]
        elif prop[0] == "PrevCurves":
            cur_prev_curves = prop[1]
        elif prop[0] == "Length":
            cur_length = prop[1]
        else:
            lprint('\nW Unknown property in "Curve" data: "%s"!', prop[0])
    for bez_sect in section.sections:
        if bez_sect.type == 'Bezier':
            for sect in bez_sect.sections:
                # print(' * SECT(%s) - %s' % (str(bez_sect.type), str(sect.type)))
                if sect.type == 'Start':
                    for prop in sect.props:
                        # print('   PROP: %s' % str(prop))
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "Position":
                            bezier_start_pos = prop[1]
                        elif prop[0] == "Direction":
                            bezier_start_dir = prop[1]
                        elif prop[0] == "Rotation":
                            bezier_start_qua = prop[1]
                        else:
                            lprint('\nW Unknown property in "Curve.%s.%s" data: "%s"!', (sect.type, bez_sect.type, prop[0]))
                elif sect.type == 'End':
                    for prop in sect.props:
                        # print('   PROP: %s' % str(prop))
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "Position":
                            bezier_end_pos = prop[1]
                        elif prop[0] == "Direction":
                            bezier_end_dir = prop[1]
                        elif prop[0] == "Rotation":
                            bezier_end_qua = prop[1]
                        else:
                            lprint('\nW Unknown property in "Curve.%s.%s" data: "%s"!', (sect.type, bez_sect.type, prop[0]))
                else:
                    lprint('\nW Unknown section "%s" in "Curve.%s" data!', (sect.type, bez_sect.type))
        else:
            lprint('\nW Unknown section "%s" in "Curve" data!', bez_sect.type)
    return (cur_name,
            cur_index,
            cur_flags,
            cur_leads_to_nodes,
            cur_speed_limit,
            cur_traffic_light_id,
            cur_next_curves,
            cur_prev_curves,
            cur_length,
            bezier_start_pos,
            bezier_start_dir,
            bezier_start_qua,
            bezier_end_pos,
            bezier_end_dir,
            bezier_end_qua)


def _get_map_point_properties(section):
    """Receives a Map Point section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    map_name = map_visual_flags = map_nav_flags = map_position = map_neighbours = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            map_name = prop[1]
        elif prop[0] == "MapVisualFlags":
            map_visual_flags = prop[1]
        elif prop[0] == "MapNavFlags":
            map_nav_flags = prop[1]
        elif prop[0] == "Position":
            map_position = prop[1]
        elif prop[0] == "Neighbours":
            map_neighbours = prop[1]
        else:
            lprint('\nW Unknown property in "Map Point" data: "%s"!', prop[0])
    return map_name, map_visual_flags, map_nav_flags, map_position, map_neighbours


def _get_trigger_point_properties(section):
    """Receives a Trigger Point section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    trp_name = trp_trigger_id = trp_action = trp_range = trp_reset_delay = \
        trp_reset_dist = trp_flags = trp_position = trp_neighbours = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            trp_name = prop[1]
        elif prop[0] == "TriggerID":
            trp_trigger_id = prop[1]
        elif prop[0] == "TriggerAction":
            trp_action = prop[1]
        elif prop[0] == "TriggerRange":
            trp_range = prop[1]
        elif prop[0] == "TriggerResetDelay":
            trp_reset_delay = prop[1]
        elif prop[0] == "TriggerResetDist":
            trp_reset_dist = prop[1]
        elif prop[0] == "Flags":
            trp_flags = prop[1]
        elif prop[0] == "Position":
            trp_position = prop[1]
        elif prop[0] == "Neighbours":
            trp_neighbours = prop[1]
        else:
            lprint('\nW Unknown property in "Trigger Point" data: "%s"!', prop[0])
    return (trp_name,
            trp_trigger_id,
            trp_action,
            trp_range,
            trp_reset_delay,
            trp_reset_dist,
            trp_flags,
            trp_position,
            trp_neighbours)


def _create_node_locator(
        node_name,
        node_index,
        node_position,
        node_direction,
        node_input_lanes,
        node_output_lanes,
        node_terpoint_count,
        node_stream_count
):
    handle_unused_arg(__file__, _create_node_locator.__name__, "node_input_lanes", node_input_lanes)
    handle_unused_arg(__file__, _create_node_locator.__name__, "node_output_lanes", node_output_lanes)
    handle_unused_arg(__file__, _create_node_locator.__name__, "node_terpoint_count", node_terpoint_count)
    handle_unused_arg(__file__, _create_node_locator.__name__, "node_stream_count", node_stream_count)

    locator = _object_utils.create_locator_empty(node_name,
                                                 node_position,
                                                 (
                                                     math.radians(node_direction[0]),
                                                     math.radians(node_direction[1]),
                                                     math.radians(node_direction[2])
                                                 ),
                                                 (1, 1, 1),
                                                 0.1,
                                                 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Control Node'
        locator.scs_props.locator_prefab_con_node_index = str(node_index)

    return locator


def _create_sign_locator(
        sign_name,
        sign_index,
        sign_position,
        sign_rotation,
        sign_model_id,
        sign_part,
        scs_sign_model_inventory
):
    handle_unused_arg(__file__, _create_sign_locator.__name__, "sign_index", sign_index)

    locator = _object_utils.create_locator_empty(sign_name, sign_position, sign_rotation, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Sign'
        locator.scs_props.locator_prefab_sign_model = _inventory.get_inventory_name(scs_sign_model_inventory, sign_model_id)
        locator.scs_props.scs_part = sign_part

    return locator


def _create_spawn_locator(
        spawn_name,
        spawn_index,
        spawn_position,
        spawn_rotation,
        spawn_type
):
    handle_unused_arg(__file__, _create_spawn_locator.__name__, "spawn_index", spawn_index)

    locator = _object_utils.create_locator_empty(spawn_name, spawn_position, spawn_rotation, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Spawn Point'
        locator.scs_props.locator_prefab_spawn_type = str(spawn_type)
    return locator


def _create_traffic_light_locator(
        tsem_name,
        tsem_position,
        tsem_rotation,
        tsem_type,
        tsem_id,
        tsem_intervals,
        tsem_cycle,
        tsem_model,
        tsem_profile,
        scs_tsem_profile_inventory
):
    handle_unused_arg(__file__, _create_traffic_light_locator.__name__, "tsem_model", tsem_model)

    locator = _object_utils.create_locator_empty(tsem_name, tsem_position, tsem_rotation, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Traffic Semaphore'
        if tsem_id == -1:
            tsem_id = 'none'
        else:
            tsem_id = str(tsem_id)
        locator.scs_props.locator_prefab_tsem_id = tsem_id
        # locator.scs_props.locator_prefab_tsem_model = tsem_model
        locator.scs_props.locator_prefab_tsem_profile = _inventory.get_inventory_name(scs_tsem_profile_inventory, tsem_profile)
        locator.scs_props.locator_prefab_tsem_type = str(tsem_type)
        if tsem_type == 6:
            locator.scs_props.locator_prefab_tsem_gm = tsem_intervals[0]
            locator.scs_props.locator_prefab_tsem_om1 = tsem_intervals[1]
            locator.scs_props.locator_prefab_tsem_rm = tsem_intervals[2]
        else:
            locator.scs_props.locator_prefab_tsem_gs = tsem_intervals[0]
            locator.scs_props.locator_prefab_tsem_os1 = tsem_intervals[1]
            locator.scs_props.locator_prefab_tsem_rs = tsem_intervals[2]
            locator.scs_props.locator_prefab_tsem_os2 = tsem_intervals[3]
        locator.scs_props.locator_prefab_tsem_cyc_delay = tsem_cycle
        # locator.scs_props.locator_prefab_tsem_activation =
        # locator.scs_props.locator_prefab_tsem_ai_only =
    return locator


def _create_nav_locator(nav_locator_data):
    """."""
    name = nav_locator_data['np_name']
    position = nav_locator_data['np_pos']
    if nav_locator_data['np_qua']:
        direction = nav_locator_data['np_qua']
    else:
        direction = nav_locator_data['np_dir']
        direction = (
            math.radians(direction[0]),
            math.radians(direction[1]),
            math.radians(direction[2])
        )
    locator = _object_utils.create_locator_empty(name, position, direction, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Navigation Point'
        # locator.scs_props.locator_prefab_con_node_index = str(node_index)
        locator.scs_props.locator_prefab_np_speed_limit = nav_locator_data['np_speed_limit']

        # print(' %r' % str(nav_locator_data['locator_prefab_np_name']))
        # print(' --> locator_prefab_np_stopper: %s' % str(nav_locator_data['locator_prefab_np_stopper']))
        # print(' --> locator_prefab_np_allowed_veh: %s' % str(nav_locator_data['locator_prefab_np_allowed_veh']))
        # print(' --> locator_prefab_np_blinker: %s' % str(nav_locator_data['locator_prefab_np_blinker']))
        # print(' --> locator_prefab_np_tl_activ: %s' % str(nav_locator_data['locator_prefab_np_tl_activ']))
        # print(' --> locator_prefab_np_low_probab: %s' % str(nav_locator_data['locator_prefab_np_low_probab']))
        # print(' --> locator_prefab_np_ig_blink_prior: %s' % str(nav_locator_data['locator_prefab_np_ig_blink_prior']))
        # print(' --> locator_prefab_np_low_prior: %s' % str(nav_locator_data['locator_prefab_np_low_prior']))
        # print(' --> locator_prefab_np_crossroad: %s' % str(nav_locator_data['locator_prefab_np_crossroad']))
        # print(' --> locator_prefab_np_add_priority: %s' % str(nav_locator_data['locator_prefab_np_add_priority']))
        # print(' --> locator_prefab_np_priority_mask: %s' % str(nav_locator_data['locator_prefab_np_priority_mask']))

        locator.scs_props.locator_prefab_np_stopper = nav_locator_data['np_stopper']
        locator.scs_props.locator_prefab_np_allowed_veh = nav_locator_data['np_allowed_veh']
        locator.scs_props.locator_prefab_np_blinker = nav_locator_data['np_blinker']
        locator.scs_props.locator_prefab_np_tl_activ = nav_locator_data['np_tl_activ']
        locator.scs_props.locator_prefab_np_low_probab = nav_locator_data['np_low_probab']
        locator.scs_props.locator_prefab_np_ig_blink_prior = nav_locator_data['np_ig_blink_prior']
        locator.scs_props.locator_prefab_np_low_prior = nav_locator_data['np_low_prior']
        locator.scs_props.locator_prefab_np_crossroad = nav_locator_data['np_crossroad']
        locator.scs_props.locator_prefab_np_add_priority = nav_locator_data['np_add_priority']
        locator.scs_props.locator_prefab_np_priority_mask = nav_locator_data['np_priority_mask']

        # nav_locator_data['locator_prefab_np_name']
        # nav_locator_data['locator_prefab_np_pos']
        # nav_locator_data['locator_prefab_np_dir']

        # nav_locator_data['locator_prefab_np_tl_activ'],         ## BoolProperty - "Traffic Semaphore Activator"
        # nav_locator_data['locator_prefab_np_low_prior'],        ## BoolProperty - "Low Priority"
        # nav_locator_data['locator_prefab_np_ig_blink_prior'],   ## BoolProperty - "Ignore Blinker Priority"
        # nav_locator_data['locator_prefab_np_crossroad'],        ## BoolProperty - "Crossroad"
        # nav_locator_data['locator_prefab_np_stopper'],          ## BoolProperty - "Stopper"
        # nav_locator_data['locator_prefab_np_low_probab'],       ## BoolProperty - "Low Probability"

        # nav_locator_data['locator_prefab_np_allowed_veh'],      ## EnumProperty - "Allowed Vehicles"

        # nav_locator_data['locator_prefab_np_speed_limit'],      ## FloatProperty - "Speed Limit [km/h]"

        # nav_locator_data['locator_prefab_np_blinker'],          ## EnumProperty - "Blinker"
        # nav_locator_data['locator_prefab_np_boundary'],         ## EnumProperty - "Boundary"
        # nav_locator_data['locator_prefab_np_boundary_node'],    ## EnumProperty - "Boundary Node"
        # nav_locator_data['locator_prefab_np_traffic_light'],    ## EnumProperty - "Traffic Semaphore"
        # nav_locator_data['locator_prefab_np_priority_mask'],    ## EnumProperty - "Priority Modifier"

    return locator


def _create_map_locator(
        map_name,
        map_index,
        map_visual_flags,
        map_nav_flags,
        map_position,
        map_neighbours
):
    handle_unused_arg(__file__, _create_map_locator.__name__, "map_index", map_index)
    handle_unused_arg(__file__, _create_map_locator.__name__, "map_neighbours", map_neighbours)

    locator = _object_utils.create_locator_empty(map_name, map_position, (0, 0, 0), (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Map Point'

        locator.scs_props.locator_prefab_mp_road_over = (map_visual_flags & 0x00010000) != 0
        locator.scs_props.locator_prefab_mp_no_outline = (map_visual_flags & 0x00100000) != 0
        locator.scs_props.locator_prefab_mp_no_arrow = (map_visual_flags & 0x00200000) != 0
        locator.scs_props.locator_prefab_mp_prefab_exit = (map_nav_flags & 0x00000400) != 0

        flag = map_visual_flags & 0x00000F00
        if flag == 0x000:
            locator.scs_props.locator_prefab_mp_road_size = 'ow'
        elif flag == 0x100:
            locator.scs_props.locator_prefab_mp_road_size = '1 lane'
        elif flag == 0x200:
            locator.scs_props.locator_prefab_mp_road_size = '2 lane'
        elif flag == 0x300:
            locator.scs_props.locator_prefab_mp_road_size = '3 lane'
        elif flag == 0x400:
            locator.scs_props.locator_prefab_mp_road_size = '4 lane'
        elif flag == 0xD00:
            locator.scs_props.locator_prefab_mp_road_size = 'poly'
        elif flag == 0xE00:
            locator.scs_props.locator_prefab_mp_road_size = 'auto'

        flag = map_visual_flags & 0x0000F000
        if flag == 0x0000:
            locator.scs_props.locator_prefab_mp_road_offset = '0m'
        elif flag == 0x1000:
            locator.scs_props.locator_prefab_mp_road_offset = '1m'
        elif flag == 0x2000:
            locator.scs_props.locator_prefab_mp_road_offset = '2m'
        elif flag == 0x3000:
            locator.scs_props.locator_prefab_mp_road_offset = '5m'
        elif flag == 0x4000:
            locator.scs_props.locator_prefab_mp_road_offset = '10m'
        elif flag == 0x5000:
            locator.scs_props.locator_prefab_mp_road_offset = '15m'
        elif flag == 0x6000:
            locator.scs_props.locator_prefab_mp_road_offset = '20m'
        elif flag == 0x7000:
            locator.scs_props.locator_prefab_mp_road_offset = '25m'

        flag = map_visual_flags & 0x000F0000
        if flag == 0x20000:
            locator.scs_props.locator_prefab_mp_custom_color = 'light'
        elif flag == 0x40000:
            locator.scs_props.locator_prefab_mp_custom_color = 'dark'
        elif flag == 0x80000:
            locator.scs_props.locator_prefab_mp_custom_color = 'green'

        flag = map_nav_flags & 0x00000F00
        if flag == 0x100:
            locator.scs_props.locator_prefab_mp_assigned_node = '1'
        elif flag == 0x200:
            locator.scs_props.locator_prefab_mp_assigned_node = '2'
        elif flag == 0x300:
            locator.scs_props.locator_prefab_mp_assigned_node = '3'
        # TODO: Not even properly exported from Blender so import is incomplete!

        locator.scs_props.locator_prefab_mp_des_nodes_0 = (map_nav_flags & 0x00000001) != 0
        locator.scs_props.locator_prefab_mp_des_nodes_1 = (map_nav_flags & 0x00000002) != 0
        locator.scs_props.locator_prefab_mp_des_nodes_2 = (map_nav_flags & 0x00000004) != 0
        locator.scs_props.locator_prefab_mp_des_nodes_3 = (map_nav_flags & 0x00000008) != 0
        # locator.scs_props.locator_prefab_mp_des_nodes_4 = (map_nav_flags & 0x00000010) != 0
        # locator.scs_props.locator_prefab_mp_des_nodes_5 = (map_nav_flags & 0x00000020) != 0
        # locator.scs_props.locator_prefab_mp_des_nodes_6 = (map_nav_flags & 0x00000040) != 0
        locator.scs_props.locator_prefab_mp_des_nodes_ct = (map_nav_flags & 0x00000080) != 0

        # print('  Map Locator Name: "%s" - neighbours: %s' % (map_name, str(map_neighbours)))
    return locator


def _create_trigger_locator(
        trp_name,
        trp_index,
        trp_trigger_id,
        trp_action,
        trp_range,
        trp_reset_delay,
        trp_reset_dist,
        trp_flags,
        trp_position,
        trp_neighbours
):
    handle_unused_arg(__file__, _create_trigger_locator.__name__, "trp_index", trp_index)
    handle_unused_arg(__file__, _create_trigger_locator.__name__, "trp_trigger_id", trp_trigger_id)
    handle_unused_arg(__file__, _create_trigger_locator.__name__, "trp_reset_dist", trp_reset_dist)
    handle_unused_arg(__file__, _create_trigger_locator.__name__, "trp_flags", trp_flags)
    handle_unused_arg(__file__, _create_trigger_locator.__name__, "trp_neighbours", trp_neighbours)

    locator = _object_utils.create_locator_empty(trp_name, trp_position, (0, 0, 0), (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Trigger Point'
        locator.scs_props.locator_prefab_tp_action = trp_action
        locator.scs_props.locator_prefab_tp_range = trp_range
        locator.scs_props.locator_prefab_tp_reset_delay = trp_reset_delay
        # trp_index, trp_trigger_id, trp_reset_dist, trp_flags, trp_neighbours
        # locator.scs_props.locator_prefab_tp_sphere_trigger =
        # locator.scs_props.locator_prefab_tp_partial_activ =
        # locator.scs_props.locator_prefab_tp_onetime_activ =
        # locator.scs_props.locator_prefab_tp_manual_activ =
    return locator


def _nav_loc_duplicate_test(nav_locator_data, nav_locs):
    """Takes a single Locator data and list of already processed Locators and returns
    True if Locator of the same location and direction is already in processed data
    together with index of Locator to omit (delete) and index of Locator to use instead or
    False if the Locator is not duplicate of any processed Locator (plus None, None)."""
    tested_np_pos_dir = (nav_locator_data['locator_prefab_np_pos'],
                         nav_locator_data['locator_prefab_np_dir'],
                         nav_locator_data['locator_prefab_np_qua'])
    # print(' tested_np_pos_dir: %s' % str(tested_np_pos_dir))
    for nav_loc in nav_locs:
        # print('  (%s)' % str(nav_loc['locator_prefab_np_index']))
        np_pos_dir = (nav_loc['locator_prefab_np_pos'], nav_loc['locator_prefab_np_dir'], nav_loc['locator_prefab_np_qua'])
        # print('  np_pos_dir: %s' % str(np_pos_dir))
        if tested_np_pos_dir == np_pos_dir:
            deleted_loc_ind = nav_locator_data['locator_prefab_np_index']
            replacement_loc_ind = nav_loc['locator_prefab_np_index']
            # print('  DELETED Locator: %s ==> %s' % (str(deleted_loc_ind), str(replacement_loc_ind)))
            return True, deleted_loc_ind, replacement_loc_ind
    return False, None, None


def load(filepath):
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIP Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # from bpy_extras.image_utils import load_image  # UNUSED

    # scene = context.scene
    ind = '    '
    pip_container = _pix_container.get_data_from_file(filepath, ind)

    '''
    # TEST PRINTOUTS
    ind = '  '
    for section in pip_container:
        print('SEC.: "%s"' % section.type)
    for prop in section.props:
        print('%sProp: %s' % (ind, prop))
    for data in section.data:
        print('%sdata: %s' % (ind, data))
    for sec in section.sections:
        print_section(sec, ind)
    print('\nTEST - Source: "%s"' % pip_container[0].props[1][1])
    print('')

    # TEST EXPORT
    path, file = os.path.splitext(filepath)
    export_filepath = str(path + '_reex' + file)
    result = pix_write.write_data(pip_container, export_filepath, ind)
    if result == {'FINISHED'}:
        Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
    else:
        Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)
    '''
    # LOAD HEADER
    '''
    NOTE: skipped for now as no data needs to be readed
    (format_version, source, f_type, f_name, source_filename, author) = _get_header(pip_container)
    '''

    # LOAD GLOBALS
    '''
    NOTE: skipped for now as no data needs to be readed
    (node_count,
     terrain_point_count,
     nav_curve_count,
     sign_count,
     spawn_point_count,
     traffic_light_count,
     map_point_count,
     trigger_point_count,
     intersection_count) = _get_global(pip_container)
    '''

    # DATA BUILDING
    nodes_data = {}
    # terrain_points_data = {}
    signs_data = {}
    spawn_points_data = {}
    traffic_lights_data = {}
    nav_curves_data = {}
    # map_points_data = {}
    map_points_data = []
    # trigger_points_data = {}
    trigger_points_data = []

    locators = []

    # node_index = 0
    sign_index = 0
    spawn_index = 0
    tsem_index = 0
    map_index = 0
    trp_index = 0

    for section in pip_container:
        if section.type == 'Node':
            (node_name,
             node_index,
             node_position,
             node_direction,
             node_input_lanes,
             node_output_lanes,
             node_terpoint_count,
             node_stream_count) = _get_node_properties(section)

            if not node_name:
                node_name = str('Node_Locator_' + str(node_index))
            # print('\nnode_name: %r' % node_name)
            # print('  node_index: %i' % node_index)
            # print('  node_position 1: %s' % node_position)
            # print('  node_direction 1: %s' % node_direction)
            # node_direction = [0.0, 0.0, 0.0]
            node_direction = _curve_utils.set_direction(node_direction)
            # print('  node_direction 2: %s' % node_direction)
            # print('  node_input_lanes: %s' % str(node_input_lanes))
            # print('  node_output_lanes: %s' % str(node_output_lanes))
            # print('  node_terpoint_count: %s' % str(node_terpoint_count))
            # print('  node_stream_count: %s' % str(node_stream_count))
            nodes_data[node_name] = (
                node_index,
                node_position,
                node_direction,
                node_input_lanes,
                node_output_lanes,
                node_terpoint_count,
                node_stream_count,
            )
        elif section.type == 'Sign':
            (sign_name,
             sign_position,
             sign_rotation,
             sign_model,
             sign_part) = _get_sign_properties(section)

            if not sign_name:
                sign_name = str('Sign_Locator_' + str(sign_index))
            # print('\nsign_name: %r' % sign_name)
            # print('  sign_position: %s' % sign_position)
            # print('  sign_rotation: %s' % sign_rotation)
            # print('  sign_model: %s' % sign_model)
            signs_data[sign_name] = (
                sign_index,
                sign_position,
                sign_rotation,
                sign_model,
                sign_part,
            )
            sign_index += 1
        elif section.type == 'SpawnPoint':
            (spawn_name,
             spawn_position,
             spawn_rotation,
             spawn_type) = _get_spawn_properties(section)

            if not spawn_name:
                spawn_name = str('Sign_Locator_' + str(spawn_index))
            # print('\nspawn_name: %r' % spawn_name)
            # print('  spawn_position: %s' % spawn_position)
            # print('  spawn_rotation: %s' % spawn_rotation)
            # print('  spawn_type: %s' % spawn_type)
            spawn_points_data[spawn_name] = (
                spawn_index,
                spawn_position,
                spawn_rotation,
                spawn_type,
            )
            spawn_index += 1
        elif section.type == 'Semaphore':  # former "TrafficLight"
            (tsem_name,
             tsem_position,
             tsem_rotation,
             tsem_type,
             tsem_id,
             tsem_intervals,
             tsem_cycle,
             tsem_model,
             tsem_profile) = _get_t_light_properties(section)

            if not tsem_name:
                tsem_name = str('Semaphore_Locator_' + str(tsem_index))
            # print('\ntsem_name: %r' % tsem_name)
            # print('  tsem_position: %s' % tsem_position)
            # print('  tsem_rotation: %s' % str(tsem_rotation))
            # print('  tsem_type: %s' % tsem_type)
            print('  tsem_id: %s' % tsem_id)
            # print('  tsem_intervals: %s' % tsem_intervals)
            # print('  tsem_cycle: %s' % tsem_cycle)
            # print('  tsem_model: %s' % tsem_model)
            # print('  tsem_profile: %s' % tsem_profile)
            traffic_lights_data[tsem_name] = (
                tsem_position,
                tsem_rotation,
                tsem_type,
                tsem_id,
                tsem_intervals,
                tsem_cycle,
                tsem_model,
                tsem_profile,
            )
            tsem_index += 1
        elif section.type == 'Curve':
            (cur_name,
             cur_index,
             cur_flags,
             cur_leads_to_nodes,
             cur_speed_limit,
             cur_traffic_light_id,
             cur_next_curves,
             cur_prev_curves,
             cur_length,
             bezier_start_pos,
             bezier_start_dir,
             bezier_start_qua,
             bezier_end_pos,
             bezier_end_dir,
             bezier_end_qua) = _get_curve_properties(section)

            # print('\ncur_name: %r' % cur_name)
            # print('  cur_index: %i' % cur_index)
            # print('  cur_flags: %s' % cur_flags)
            # print('  cur_leads_to_nodes: %s' % cur_leads_to_nodes)
            # print('  cur_speed_limit: %s' % cur_speed_limit)
            # print('  cur_traffic_light_id: %s' % cur_traffic_light_id)
            # print('  cur_next_curves: %s' % cur_next_curves)
            # print('  cur_prev_curves: %s' % cur_prev_curves)
            # print('  cur_length: %s' % cur_length)
            nav_curves_data[cur_index] = (
                cur_name,
                cur_flags,
                cur_leads_to_nodes,
                cur_speed_limit,
                cur_traffic_light_id,
                cur_next_curves,
                cur_prev_curves,
                cur_length,
                bezier_start_pos,
                bezier_start_dir,
                bezier_start_qua,
                bezier_end_pos,
                bezier_end_dir,
                bezier_end_qua,
            )
        elif section.type == 'MapPoint':
            (map_name,
             map_visual_flags,
             map_nav_flags,
             map_position,
             map_neighbours) = _get_map_point_properties(section)

            if not map_name:
                map_name = _name_utils.make_unique_name(object, str('Map_Point_Locator_' + str(map_index)))
            # print('\nmap_name: %r' % map_name)
            # print('  map_visual_flags: %s' % map_visual_flags)
            # print('  map_nav_flags: %s' % map_nav_flags)
            # print('  map_position: %s' % str(map_position))
            # print('  map_neighbours: %s' % map_neighbours)
            map_points_data.append((
                map_name,
                map_index,
                map_visual_flags,
                map_nav_flags,
                map_position,
                map_neighbours,
            ))
            map_index += 1
        elif section.type == 'TriggerPoint':
            (trp_name,
             trp_trigger_id,
             trp_action,
             trp_range,
             trp_reset_delay,
             trp_reset_dist,
             trp_flags,
             trp_position,
             trp_neighbours) = _get_trigger_point_properties(section)

            if not trp_name:
                trp_name = str('Trigger_Locator_' + str(trp_index))
            # print('\ntrp_name: %r' % trp_name)
            # print('  trp_trigger_id: %s' % trp_trigger_id)
            # print('  trp_action: %s' % trp_action)
            trp_range = float(trp_range)
            # print('  trp_range: %s' % trp_range)
            trp_reset_delay = float(trp_reset_delay)
            # print('  trp_reset_delay: %s' % trp_reset_delay)
            # print('  trp_reset_dist: %s' % trp_reset_dist)
            # print('  trp_flags: %s' % trp_flags)
            # print('  trp_position: %s' % str(trp_position))
            # print('  trp_neighbours: %s' % str(trp_neighbours))
            trigger_points_data.append((
                trp_name,
                trp_index,
                trp_trigger_id,
                trp_action,
                trp_range,
                trp_reset_delay,
                trp_reset_dist,
                trp_flags,
                trp_position,
                trp_neighbours,
            ))
            trp_index += 1

            # print('')

    # CREATE NODES
    for name in nodes_data:
        # print('nodes_data[name]: %s' % str(nodes_data[name]))
        loc = _create_node_locator(
            name,
            nodes_data[name][0],  # node_index
            nodes_data[name][1],  # node_position
            nodes_data[name][2],  # node_direction
            nodes_data[name][3],  # node_input_lanes
            nodes_data[name][4],  # node_output_lanes
            nodes_data[name][5],  # node_terpoint_count
            nodes_data[name][6],  # node_stream_count
        )
        if loc:
            _print_locator_result(loc, "Node", name)
            locators.append(loc)

    # CREATE SIGNS
    for name in signs_data:
        # print('signs_data[name]: %s' % str(signs_data[name]))
        loc = _create_sign_locator(
            name,
            signs_data[name][0],
            signs_data[name][1],
            signs_data[name][2],
            signs_data[name][3],
            signs_data[name][4],
            scs_globals.scs_sign_model_inventory
        )
        if loc:
            _print_locator_result(loc, "Sign", name)
            locators.append(loc)

    # CREATE SPAWN POINTS
    for name in spawn_points_data:
        # print('spawn_points_data[name]: %s' % str(spawn_points_data[name]))
        loc = _create_spawn_locator(
            name,
            spawn_points_data[name][0],
            spawn_points_data[name][1],
            spawn_points_data[name][2],
            spawn_points_data[name][3],
        )
        if loc:
            _print_locator_result(loc, "Spawn Point", name)
            locators.append(loc)

    # CREATE TRAFFIC LIGHTS
    for name in traffic_lights_data:
        # print('traffic_lights_data[name]: %s' % str(traffic_lights_data[name]))
        loc = _create_traffic_light_locator(
            name,
            traffic_lights_data[name][0],  # tsem_position
            traffic_lights_data[name][1],  # tsem_rotation
            traffic_lights_data[name][2],  # tsem_type
            traffic_lights_data[name][3],  # tsem_id
            traffic_lights_data[name][4],  # tsem_intervals
            traffic_lights_data[name][5],  # tsem_cycle
            traffic_lights_data[name][6],  # tsem_model
            traffic_lights_data[name][7],  # tsem_profile
            scs_globals.scs_tsem_profile_inventory
        )
        if loc:
            _print_locator_result(loc, "Traffic Semaphore", name)
            locators.append(loc)

    # PREPROCESS CURVE DATA AND CREATE LOCATORS AND DICTIONARY OF CONNECTIONS
    conns_dict = {}
    nav_locs_count = 0
    for index in nav_curves_data:

        # assemble variables
        cur_name = nav_curves_data[index][0]
        cur_flags = nav_curves_data[index][1]
        cur_leads_to_nodes = nav_curves_data[index][2]
        cur_speed_limit = nav_curves_data[index][3]
        cur_traffic_light_id = nav_curves_data[index][4]
        cur_next_curves = nav_curves_data[index][5]
        cur_prev_curves = nav_curves_data[index][6]
        # cur_length = nav_curves_data[index][7]
        bezier_start_pos = nav_curves_data[index][8]
        if nav_curves_data[index][9]:
            bezier_start_dir = _curve_utils.set_direction(nav_curves_data[index][9])
        else:
            bezier_start_qua = nav_curves_data[index][10]
        bezier_end_pos = nav_curves_data[index][11]
        if nav_curves_data[index][12]:
            bezier_end_dir = _curve_utils.set_direction(nav_curves_data[index][12])
        else:
            bezier_end_qua = nav_curves_data[index][13]

        # print('nav_curves_data[%i]: %r' % (index, str(nav_curves_data[index][0])))
        # print('  name: %r' % cur_name)
        # print('  flags: %r' % cur_flags)
        # print('  leads_to_nodes: %r' % cur_leads_to_nodes)
        # print('  curve_speed_limit: %r' % cur_speed_limit)
        # print('  curve_traffic_light_id: %r' % cur_traffic_light_id)
        # print('  next: %s' % str(cur_next_curves))
        # print('  prev: %s' % str(cur_prev_curves))
        # print('  start POS: %s' % str(bezier_start_pos))
        # print('  start DIR: %s' % str(bezier_start_dir))
        # print('  start QUA: %s' % str(bezier_start_qua))
        # print('  end POS: %s' % str(bezier_end_pos))
        # print('  end DIR: %s' % str(bezier_end_dir))
        # print('  end QUA: %s' % str(bezier_end_qua))

        # check if there is need to create new one or alter the existing
        curve_locators_to_create = {"start": True, "end": True}
        for prev_curve_ind in cur_prev_curves:

            if prev_curve_ind != -1 and prev_curve_ind in conns_dict:

                if "end" in conns_dict[prev_curve_ind]:
                    curve_locators_to_create["start"] = False

                    # properly create entry for current curve
                    if index in conns_dict:
                        conns_dict[index]["start"] = conns_dict[prev_curve_ind]["end"]
                    else:
                        conns_dict[index] = {
                            "start": conns_dict[prev_curve_ind]["end"]
                        }

                    break

        for next_curve_ind in cur_next_curves:

            if next_curve_ind != -1 and next_curve_ind in conns_dict:

                if "start" in conns_dict[next_curve_ind]:
                    curve_locators_to_create["end"] = False

                    if index in conns_dict:
                        conns_dict[index]["end"] = conns_dict[next_curve_ind]["start"]
                    else:
                        conns_dict[index] = {
                            "end": conns_dict[next_curve_ind]["start"]
                        }

                    break

        # CREATE 2 LOCATORS FOR EACH CURVE IF NEEDED
        for loc_key in curve_locators_to_create:

            # start_obj.scs_props.locator_prefab_np_stopper: number |= 0x00000001
            # start_obj.scs_props.locator_prefab_np_low_prior and end_obj.scs_props.locator_prefab_np_low_prior: number |= 0x00000002
            # end_obj.scs_props.locator_prefab_np_allowed_veh == 'to': number |= 0x00000004 # Trucks Only
            # start_obj.scs_props.locator_prefab_np_blinker == 'rb': number |= 0x00000008 # Right Blinker
            # start_obj.scs_props.locator_prefab_np_blinker == 'lb': number |= 0x00000010 # Left Blinker
            # start_obj.scs_props.locator_prefab_np_crossroad and end_obj.scs_props.locator_prefab_np_crossroad: number |= 0x00000200
            # end_obj.scs_props.locator_prefab_np_allowed_veh == 'nt': number |= 0x00000400 # No Trucks
            # start_obj.scs_props.locator_prefab_np_tl_activ: number |= 0x00000800
            # end_obj.scs_props.locator_prefab_np_allowed_veh == 'po': number |= 0x00001000 # Player Only
            # end_obj.scs_props.locator_prefab_np_low_probab: number |= 0x00002000
            # start_obj.scs_props.locator_prefab_np_ig_blink_prior: number |= 0x00004000
            # start_obj.scs_props.locator_prefab_np_add_priority: number |= 0x00008000

            # locators already exists just cover the needed properties
            if curve_locators_to_create[loc_key] is False:

                loc_obj = conns_dict[index][loc_key]
                if loc_key == "start":

                    loc_obj.scs_props.locator_prefab_np_stopper = (cur_flags & 0x00000001) != 0
                    loc_obj.scs_props.locator_prefab_np_tl_activ = (cur_flags & 0x00000800) != 0
                    loc_obj.scs_props.locator_prefab_np_ig_blink_prior = (cur_flags & 0x00004000) != 0

                else:

                    loc_obj.scs_props.locator_prefab_np_low_probab = (cur_flags & 0x00002000) != 0

                continue

            nav_locator_data = {}
            nav_locs_count += 1
            if loc_key == "start":

                nav_locator_data['np_name'] = "Nav_Point_" + str(nav_locs_count)
                nav_locator_data['np_pos'] = bezier_start_pos
                if bezier_start_qua is not None:
                    nav_locator_data['np_dir'] = None
                    nav_locator_data['np_qua'] = bezier_start_qua
                else:
                    nav_locator_data['np_dir'] = bezier_start_dir
                    nav_locator_data['np_qua'] = None
                nav_locator_data['np_stopper'] = (cur_flags & 0x00000001) != 0
                # nav_locator_data['np_allowed_veh'] = 'all'
                # nav_locator_data['np_blinker'] = (cur_flags & 0x00000008) != 0
                # nav_locator_data['np_blinker'] = (cur_flags & 0x00000010) != 0
                nav_locator_data['np_tl_activ'] = (cur_flags & 0x00000800) != 0
                nav_locator_data['np_low_probab'] = False
                nav_locator_data['np_ig_blink_prior'] = (cur_flags & 0x00004000) != 0

            elif loc_key == "end":

                nav_locator_data['np_name'] = "Nav_Point_" + str(nav_locs_count)
                nav_locator_data['np_pos'] = bezier_end_pos
                if bezier_end_qua is not None:
                    nav_locator_data['np_dir'] = None
                    nav_locator_data['np_qua'] = bezier_end_qua
                else:
                    nav_locator_data['np_dir'] = bezier_end_dir
                    nav_locator_data['np_qua'] = None
                nav_locator_data['np_stopper'] = False
                nav_locator_data['np_tl_activ'] = False
                # nav_locator_data['np_blinker'] = 'no'
                # nav_locator_data['np_allowed_veh'] = (cur_flags & 0x00000004) != 0
                # nav_locator_data['np_allowed_veh'] = (cur_flags & 0x00000400) != 0
                # nav_locator_data['np_allowed_veh'] = (cur_flags & 0x00001000) != 0
                nav_locator_data['np_low_probab'] = (cur_flags & 0x00002000) != 0
                nav_locator_data['np_ig_blink_prior'] = False

            nav_locator_data['np_low_prior'] = (cur_flags & 0x00000002) != 0
            nav_locator_data['np_crossroad'] = (cur_flags & 0x00000200) != 0
            nav_locator_data['np_add_priority'] = (cur_flags & 0x00008000) != 0
            # nav_locator_data['np_priority_mask'] = (cur_flags & 0x000F0000) != 0  # PRIORITY MASK

            if cur_speed_limit:
                nav_locator_data['np_speed_limit'] = cur_speed_limit  # from 'start' locator - Float - "Speed Limit [km/h]"
            else:
                nav_locator_data['np_speed_limit'] = 0.0

            # TODO: setup enums properly!
            nav_locator_data['np_blinker'] = 'no'  # from "cur_flags" - Enum - "Blinker"
            nav_locator_data['np_boundary'] = 'no'  # ??? - Enum - "Boundary"
            nav_locator_data['np_boundary_node'] = '0'  # ??? - Enum - "Boundary Node"
            nav_locator_data['np_traffic_light'] = '-1'  # (Enum) - Enum - "Traffic Semaphore"
            nav_locator_data['np_priority_mask'] = '-1'  # (Enum) - Enum - "Priority Modifier"
            nav_locator_data['np_allowed_veh'] = 'all'  # (Enum) - Enum - "Allowed Vehicles"

            # print(' %r' % str(nav_locator_data['locator_prefab_np_name']))
            # print(' --> locator_prefab_np_stopper: %s' % str(nav_locator_data['locator_prefab_np_stopper']))
            # print(' --> locator_prefab_np_allowed_veh: %s' % str(nav_locator_data['locator_prefab_np_allowed_veh']))
            # print(' --> locator_prefab_np_blinker: %s' % str(nav_locator_data['locator_prefab_np_blinker']))
            # print(' --> locator_prefab_np_tl_activ: %s' % str(nav_locator_data['locator_prefab_np_tl_activ']))
            # print(' --> locator_prefab_np_low_probab: %s' % str(nav_locator_data['locator_prefab_np_low_probab']))
            # print(' --> locator_prefab_np_ig_blink_prior: %s' % str(nav_locator_data['locator_prefab_np_ig_blink_prior']))
            # print(' --> locator_prefab_np_low_prior: %s' % str(nav_locator_data['locator_prefab_np_low_prior']))
            # print(' --> locator_prefab_np_crossroad: %s' % str(nav_locator_data['locator_prefab_np_crossroad']))
            # print(' --> locator_prefab_np_add_priority: %s' % str(nav_locator_data['locator_prefab_np_add_priority']))
            # print(' --> locator_prefab_np_priority_mask: %s' % str(nav_locator_data['locator_prefab_np_priority_mask']))

            loc = _create_nav_locator(nav_locator_data)
            locators.append(loc)
            if loc:
                # decide which side to update
                if loc_key == "start":
                    related_curves = cur_prev_curves
                    related_end = "end"
                else:
                    related_curves = cur_next_curves
                    related_end = "start"

                # create or update references for current connection
                if not index in conns_dict:
                    conns_dict[index] = {
                        loc_key: loc
                    }
                else:
                    conns_dict[index][loc_key] = loc

                # update references for prev or next connections
                for prev_curve_ind in related_curves:

                    if prev_curve_ind != -1:

                        if prev_curve_ind in conns_dict:

                            if not related_end in conns_dict[prev_curve_ind]:
                                conns_dict[prev_curve_ind][related_end] = loc

                        else:

                            conns_dict[prev_curve_ind] = {
                                related_end: loc
                            }

    # CREATE CONNECTIONS BETWEEN NAVIGATION POINTS
    for connection in conns_dict.values():
        _group_connections_wrapper.create_connection(connection["start"], connection["end"])

    # COLLECT MAP POINT CONNECTIONS
    connections = []
    for loc_index, map_point in enumerate(map_points_data):
        # print('      map_point: %s' % str(map_point))
        # print('      name: %r' % map_point[0])
        for loc_neighbour_index in map_point[5]:
            if loc_neighbour_index != -1:
                add_con = True
                for con in connections:
                    if loc_neighbour_index == con[0] and loc_index == con[1]:
                        add_con = False
                if loc_index == loc_neighbour_index:
                    add_con = False
                if add_con:
                    connections.append((loc_index, loc_neighbour_index))
                    # print('Map Point connections:')
                    # for connection_i, connection in enumerate(connections):
                    # print('    %i\t%s' % (connection_i, str(connection)))
                    # print('    connections:\n%s' % str(connections))

    # CREATE MAP POINTS
    mp_locs = []
    for map_point in map_points_data:
        name = map_point[0]
        # print('map_points_data[%r]: %s' % (name, str(map_point)))
        loc = _create_map_locator(
            map_point[0],
            map_point[1],
            map_point[2],
            map_point[3],
            map_point[4],
            map_point[5],
        )
        if loc:
            _print_locator_result(loc, "Map Point", name)
            locators.append(loc)
            mp_locs.append(loc)

    # APPLY MAP POINT CONNECTIONS
    # print('      mp_locs: %s' % str(mp_locs))
    # for mp_loc in mp_locs:
    # print('      mp_loc: %s' % str(mp_loc))
    if len(mp_locs) > 0:
        for connection_i, connection in enumerate(connections):

            # safety check if connection indexes really exists
            if connection[0] < len(mp_locs) and connection[1] < len(mp_locs):
                start_node = mp_locs[connection[0]]
                end_node = mp_locs[connection[1]]
            else:
                print('   Err - map connection out of range: %s' % str(connection))
                continue

            _group_connections_wrapper.create_connection(start_node, end_node)

    # COLLECT TRIGGER POINT CONNECTIONS
    connections = []
    for loc_index, tr_point in enumerate(trigger_points_data):
        # print('      name: %s' % tr_point[0])
        if len(tr_point[9]) != 2:
            print('WARNING - Unexpected number of connections (%i) for Trigger Point "%s"!' % (len(tr_point[9]), tr_point[0]))

        for loc_neighbour_index in tr_point[9]:
            connections.append((loc_index, loc_neighbour_index))

    # CREATE TRIGGER POINTS
    tp_locs = []
    for tr_point in trigger_points_data:
        name = tr_point[0]
        # print('trigger_points_data[%r]: %s' % (name, str(tr_point)))
        loc = _create_trigger_locator(
            tr_point[0],
            tr_point[1],
            tr_point[2],
            tr_point[3],
            tr_point[4],
            tr_point[5],
            tr_point[6],
            tr_point[7],
            tr_point[8],
            tr_point[9],
        )
        if loc:
            _print_locator_result(loc, "Trigger Point", name)
            locators.append(loc)
            tp_locs.append(loc)

            # APPLY TRIGGER POINT CONNECTIONS
            # print('      tp_locs: %s' % str(tp_locs))
            # for tp_loc in tp_locs:
            # print('      tp_loc: %s' % str(tp_loc))
    if len(tp_locs) > 0:
        for connection_i, connection in enumerate(connections):

            # safety check if connection indexes really exists
            if connection[0] < len(tp_locs) and connection[1] < len(tp_locs):
                start_node = tp_locs[connection[0]]
                end_node = tp_locs[connection[1]]
            else:
                print('   Err - trigger connection: %s' % str(connection))
                continue

            _group_connections_wrapper.create_connection(start_node, end_node)

    '''
    # WARNING PRINTOUTS
    if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
    if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
    if dump_level > 1: print('')
    '''

    print("************************************")
    return {'FINISHED'}, locators