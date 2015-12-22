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
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.connections.wrappers import group as _group_connections_wrapper
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


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
        node_output_lanes = node_terpoint_count = node_terpoint_variant_count = node_stream_count = None
    tp_positions = []
    tp_normals = []
    tp_variants = []

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
        elif prop[0] in "TerrainPointVariantCount":
            node_terpoint_variant_count = prop[1]
        elif prop[0] == "StreamCount":
            node_stream_count = prop[1]
        else:
            lprint('\nW Unknown property in "Node" data: "%s"!', prop[0])

    for sec in section.sections:
        if sec.type == "Stream":
            stream_format = stream_tag = None
            for prop in sec.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "Format":
                    stream_format = prop[1]
                elif prop[0] == "Tag":
                    stream_tag = prop[1]
                else:
                    lprint('\nW Unknown property in "Stream" data: "%s"!', prop[0])

            data_block = []
            for data_line in sec.data:
                data_block.append(data_line)

            if stream_tag == '_POSITION' and stream_format == 'FLOAT3':
                tp_positions = data_block
            elif stream_tag == '_NORMAL' and stream_format == 'FLOAT3':
                tp_normals = data_block
            elif stream_tag == '_VARIANT_BLOCK' and stream_format == 'INT2':
                tp_variants = data_block

    # even check stream count validity
    assert node_terpoint_count == len(tp_positions)
    assert node_terpoint_count == len(tp_normals)

    if node_terpoint_variant_count:  # variant block exists
        assert node_terpoint_variant_count == len(tp_variants)
        assert node_stream_count == 3
    else:
        assert node_terpoint_count == 0 or node_stream_count == 2

    return (node_name,
            node_index,
            node_position,
            node_direction,
            node_input_lanes,
            node_output_lanes,
            tp_positions,
            tp_normals,
            tp_variants)


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
        tsem_intervals = tsem_cycle = tsem_profile = None
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
            tsem_profile)


def _get_curve_properties(section):
    """Receives a Curve section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    cur_name = cur_index = cur_flags = cur_leads_to_nodes = cur_traffic_rule = cur_traffic_light_id = \
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
        elif prop[0] == "TrafficRule":
            cur_traffic_rule = prop[1]
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
            cur_traffic_rule,
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
    map_index = map_name = map_visual_flags = map_nav_flags = map_position = map_neighbours = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            map_index = prop[1]
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
    return map_index, map_name, map_visual_flags, map_nav_flags, map_position, map_neighbours


def _get_trigger_point_properties(section):
    """Receives a Trigger Point section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    trp_index = trp_name = trp_trigger_id = trp_action = trp_range = trp_reset_delay = \
        trp_flags = trp_position = trp_neighbours = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            trp_index = prop[1]
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
            pass  # not used anymore
        elif prop[0] == "Flags":
            trp_flags = prop[1]
        elif prop[0] == "Position":
            trp_position = prop[1]
        elif prop[0] == "Neighbours":
            trp_neighbours = prop[1]
        else:
            lprint('\nW Unknown property in "Trigger Point" data: "%s"!', prop[0])
    return (trp_index,
            trp_name,
            trp_trigger_id,
            trp_action,
            trp_range,
            trp_reset_delay,
            trp_flags,
            trp_position,
            trp_neighbours)


def _create_node_locator(
        node_name,
        node_index,
        node_position,
        node_direction
):
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
        sign_position,
        sign_rotation,
        sign_model_id,
        sign_part,
        scs_sign_model_inventory
):
    locator = _object_utils.create_locator_empty(sign_name, sign_position, sign_rotation, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Sign'
        sign_model_value = _inventory.get_item_name(scs_sign_model_inventory, sign_model_id, report_errors=True)
        locator.scs_props.locator_prefab_sign_model = sign_model_value
        locator.scs_props.scs_part = sign_part

    return locator


def _create_spawn_locator(
        spawn_name,
        spawn_position,
        spawn_rotation,
        spawn_type
):
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
        tsem_profile,
        scs_tsem_profile_inventory
):
    locator = _object_utils.create_locator_empty(tsem_name, tsem_position, tsem_rotation, (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Traffic Semaphore'
        if tsem_id == -1:
            tsem_id = 'none'
        else:
            tsem_id = str(tsem_id)
        locator.scs_props.locator_prefab_tsem_id = tsem_id

        tsem_profile_value = _inventory.get_item_name(scs_tsem_profile_inventory, tsem_profile, report_errors=True)
        locator.scs_props.locator_prefab_tsem_profile = tsem_profile_value

        locator.scs_props.locator_prefab_tsem_type = str(tsem_type)
        locator.scs_props.locator_prefab_tsem_gs = tsem_intervals[0]
        locator.scs_props.locator_prefab_tsem_os1 = tsem_intervals[1]
        locator.scs_props.locator_prefab_tsem_rs = tsem_intervals[2]
        locator.scs_props.locator_prefab_tsem_os2 = tsem_intervals[3]
        locator.scs_props.locator_prefab_tsem_cyc_delay = tsem_cycle
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

    return locator


def _set_nav_locator_props(loc, nav_locator_data, is_start):
    scs_props = loc.scs_props
    """:type: io_scs_tools.properties.object.ObjectSCSTools"""

    if is_start:

        scs_props.locator_prefab_np_blinker = str(nav_locator_data['np_blinker'])
        scs_props.locator_prefab_np_priority_modifier = str(nav_locator_data['np_prior_modif'])
        scs_props.locator_prefab_np_add_priority = bool(nav_locator_data['np_add_priority'])
        scs_props.locator_prefab_np_limit_displace = bool(nav_locator_data['np_limit_displace'])

        if nav_locator_data['np_semaphore_id'] is not None:
            scs_props.locator_prefab_np_traffic_semaphore = str(nav_locator_data['np_semaphore_id'])

        if nav_locator_data['np_traffic_rule'] is not None:
            scs_props.locator_prefab_np_traffic_rule = str(nav_locator_data['np_traffic_rule'])

    else:

        scs_props.locator_prefab_np_low_probab = bool(nav_locator_data['np_low_probab'])
        scs_props.locator_prefab_np_allowed_veh = str(nav_locator_data['np_allowed_veh'])

    if 'np_boundary' in nav_locator_data:
        scs_props.locator_prefab_np_boundary = str(nav_locator_data['np_boundary'])
        scs_props.locator_prefab_np_boundary_node = str(nav_locator_data['np_boundary_node'])


def _create_map_locator(
        map_name,
        map_visual_flags,
        map_nav_flags,
        map_position,
):
    locator = _object_utils.create_locator_empty(map_name, map_position, (0, 0, 0), (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Map Point'

        # visual flags
        locator.scs_props.locator_prefab_mp_road_over = (map_visual_flags & _PL_consts.MPVF.ROAD_OVER) != 0
        locator.scs_props.locator_prefab_mp_no_outline = (map_visual_flags & _PL_consts.MPVF.NO_OUTLINE) != 0
        locator.scs_props.locator_prefab_mp_no_arrow = (map_visual_flags & _PL_consts.MPVF.NO_ARROW) != 0
        locator.scs_props.locator_prefab_mp_road_size = str(map_visual_flags & _PL_consts.MPVF.ROAD_SIZE_MASK)
        locator.scs_props.locator_prefab_mp_road_offset = str(map_visual_flags & _PL_consts.MPVF.ROAD_OFFSET_MASK)

        if map_visual_flags & _PL_consts.MPVF.CUSTOM_COLOR1 != 0:
            locator.scs_props.locator_prefab_mp_custom_color = str(_PL_consts.MPVF.CUSTOM_COLOR1)
        elif map_visual_flags & _PL_consts.MPVF.CUSTOM_COLOR2 != 0:
            locator.scs_props.locator_prefab_mp_custom_color = str(_PL_consts.MPVF.CUSTOM_COLOR2)
        elif map_visual_flags & _PL_consts.MPVF.CUSTOM_COLOR3 != 0:
            locator.scs_props.locator_prefab_mp_custom_color = str(_PL_consts.MPVF.CUSTOM_COLOR3)

        # navigation flags
        locator.scs_props.locator_prefab_mp_prefab_exit = (map_nav_flags & _PL_consts.MPNF.PREFAB_EXIT) != 0
        if map_nav_flags & _PL_consts.MPNF.NAV_NODE_START != 0:

            if map_nav_flags & _PL_consts.MPNF.NAV_NODE_0 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_0)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_1 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_1)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_2 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_2)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_3 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_3)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_4 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_4)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_5 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_5)
            elif map_nav_flags & _PL_consts.MPNF.NAV_NODE_6 != 0:
                locator.scs_props.locator_prefab_mp_assigned_node = str(_PL_consts.MPNF.NAV_NODE_6)

        dest_nodes = []
        for index in range(_PL_consts.PREFAB_NODE_COUNT_MAX):
            if map_nav_flags >> index & 1 != 0:
                dest_nodes.append(str(index))

        locator.scs_props.locator_prefab_mp_dest_nodes = set(dest_nodes)

    return locator


def _create_trigger_locator(
        trp_name,
        trp_action,
        trp_range,
        trp_reset_delay,
        trp_flags,
        trp_position,
        scs_trigger_actions_inventory
):
    locator = _object_utils.create_locator_empty(trp_name, trp_position, (0, 0, 0), (1, 1, 1), 0.1, 'Prefab')
    if locator:
        locator.scs_props.locator_prefab_type = 'Trigger Point'

        action_value = _inventory.get_item_name(scs_trigger_actions_inventory, trp_action, report_errors=True)
        locator.scs_props.locator_prefab_tp_action = action_value

        locator.scs_props.locator_prefab_tp_range = trp_range
        locator.scs_props.locator_prefab_tp_reset_delay = trp_reset_delay

        locator.scs_props.locator_prefab_tp_manual_activ = (trp_flags & _PL_consts.TPF.MANUAL) != 0
        locator.scs_props.locator_prefab_tp_sphere_trigger = (trp_flags & _PL_consts.TPF.SPHERE) != 0
        locator.scs_props.locator_prefab_tp_partial_activ = (trp_flags & _PL_consts.TPF.PARTIAL) != 0
        locator.scs_props.locator_prefab_tp_onetime_activ = (trp_flags & _PL_consts.TPF.ONETIME) != 0

    return locator


def load(filepath, terrain_points_trans):
    """Loads given PIP file.

    :param filepath: complete filepath to PIP file
    :type filepath: str
    :param terrain_points_trans: terrain points transitional structure where terrain points shall be saved
    :type terrain_points_trans: io_scs_tools.imp.transition_structs.terrain_points.TerrainPntsTrans
    :return: set of operator result and list of created locators
    :rtype: tuple[set, list[bpy.types.Objects]]
    """
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIP Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # from bpy_extras.image_utils import load_image  # UNUSED

    # scene = context.scene
    ind = '    '
    pip_container = _pix_container.get_data_from_file(filepath, ind)

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
    map_points_data = []
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
             tp_positions,
             tp_normals,
             tp_variants,) = _get_node_properties(section)

            if node_name is None:
                node_name = str('Node_Locator_' + str(node_index))

            node_direction = _curve_utils.set_direction(node_direction)

            nodes_data[node_name] = (
                node_index,
                node_position,
                node_direction,
                node_input_lanes,
                node_output_lanes,
                tp_positions,
                tp_normals,
                tp_variants
            )
        elif section.type == 'Sign':
            (sign_name,
             sign_position,
             sign_rotation,
             sign_model,
             sign_part) = _get_sign_properties(section)

            if sign_name is None:
                sign_name = str('Sign_Locator_' + str(sign_index))

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

            if spawn_name is None:
                spawn_name = str('Sign_Locator_' + str(spawn_index))

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
             tsem_profile) = _get_t_light_properties(section)

            if tsem_name is None:
                tsem_name = str('Semaphore_Locator_' + str(tsem_index))

            traffic_lights_data[tsem_name] = (
                tsem_position,
                tsem_rotation,
                tsem_type,
                tsem_id,
                tsem_intervals,
                tsem_cycle,
                tsem_profile,
            )
            tsem_index += 1
        elif section.type == 'Curve':
            (cur_name,
             cur_index,
             cur_flags,
             cur_leads_to_nodes,
             cur_traffic_rule,
             cur_sempahore_id,
             cur_next_curves,
             cur_prev_curves,
             cur_length,
             bezier_start_pos,
             bezier_start_dir,
             bezier_start_qua,
             bezier_end_pos,
             bezier_end_dir,
             bezier_end_qua) = _get_curve_properties(section)

            nav_curves_data[cur_index] = (
                cur_name,
                cur_flags,
                cur_leads_to_nodes,  # not used
                cur_traffic_rule,
                cur_sempahore_id,
                cur_next_curves,
                cur_prev_curves,
                cur_length,  # not used
                bezier_start_pos,
                bezier_start_dir,
                bezier_start_qua,
                bezier_end_pos,
                bezier_end_dir,
                bezier_end_qua,
            )
        elif section.type == 'MapPoint':
            (map_indexx,
             map_name,
             map_visual_flags,
             map_nav_flags,
             map_position,
             map_neighbours) = _get_map_point_properties(section)

            if map_indexx is None:
                map_indexx = map_index

            if map_name is None:
                map_name = str("Map_Point_Locator_" + str(map_indexx))

            map_points_data.append((
                map_name,
                map_indexx,
                map_visual_flags,
                map_nav_flags,
                map_position,
                map_neighbours,
            ))
            map_index += 1
        elif section.type == 'TriggerPoint':
            (trp_indexx,
             trp_name,
             trp_trigger_id,
             trp_action,
             trp_range,
             trp_reset_delay,
             trp_flags,
             trp_position,
             trp_neighbours) = _get_trigger_point_properties(section)

            if trp_indexx is None:
                trp_indexx = trp_index

            if trp_name is None:
                trp_name = str('Trigger_Locator_' + str(trp_indexx))

            trp_range = float(trp_range)

            trigger_points_data.append((
                trp_name,
                trp_indexx,
                trp_action,
                trp_range,
                trp_reset_delay,
                trp_flags,
                trp_position,
                trp_neighbours,
            ))
            trp_index += 1

            # print('')

    # CREATE NODES
    for name in nodes_data:
        loc = _create_node_locator(
            name,
            nodes_data[name][0],  # node_index
            nodes_data[name][1],  # node_position
            nodes_data[name][2],  # node_direction
        )

        tp_pos_l = nodes_data[name][5]
        tp_nor_l = nodes_data[name][6]
        tp_var_l = nodes_data[name][7]

        # save terrain points into transitional structure
        if len(tp_var_l) > 0:  # save per variant block

            for var_i, var in enumerate(tp_var_l):
                for i in range(var[0], var[0] + var[1]):
                    terrain_points_trans.add(var_i, nodes_data[name][0], tp_pos_l[i], tp_nor_l[i])

        else:

            for i in range(len(tp_pos_l)):
                terrain_points_trans.add(-1, nodes_data[name][0], tp_pos_l[i], tp_nor_l[i])

        if loc:
            _print_locator_result(loc, "Node", name)
            locators.append(loc)

    # CREATE SIGNS
    for name in signs_data:
        # print('signs_data[name]: %s' % str(signs_data[name]))
        loc = _create_sign_locator(
            name,
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
            traffic_lights_data[name][6],  # tsem_profile
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
        # cur_name = nav_curves_data[index][0]
        cur_flags = nav_curves_data[index][1]
        cur_traffic_rule = nav_curves_data[index][3]
        cur_sempahore_id = nav_curves_data[index][4]
        cur_next_curves = nav_curves_data[index][5]
        cur_prev_curves = nav_curves_data[index][6]

        bezier_start_pos = nav_curves_data[index][8]
        bezier_start_dir = bezier_start_qua = bezier_end_dir = bezier_end_qua = None
        if nav_curves_data[index][9]:
            bezier_start_dir = _curve_utils.set_direction(nav_curves_data[index][9])
        else:
            bezier_start_qua = nav_curves_data[index][10]

        bezier_end_pos = nav_curves_data[index][11]
        if nav_curves_data[index][12]:
            bezier_end_dir = _curve_utils.set_direction(nav_curves_data[index][12])
        else:
            bezier_end_qua = nav_curves_data[index][13]

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

            nav_locator_data = {}

            nav_locs_count += 1
            if loc_key == "start":

                nav_locator_data['np_name'] = "Nav_Point_" + str(nav_locs_count)
                nav_locator_data['np_pos'] = bezier_start_pos
                nav_locator_data['np_dir'] = bezier_start_dir
                nav_locator_data['np_qua'] = bezier_start_qua

            elif loc_key == "end":

                nav_locator_data['np_name'] = "Nav_Point_" + str(nav_locs_count)
                nav_locator_data['np_pos'] = bezier_end_pos
                nav_locator_data['np_dir'] = bezier_end_dir
                nav_locator_data['np_qua'] = bezier_end_qua

            nav_locator_data['np_low_probab'] = (cur_flags & _PL_consts.PNCF.LOW_PROBABILITY) != 0
            nav_locator_data['np_add_priority'] = (cur_flags & _PL_consts.PNCF.ADDITIVE_PRIORITY) != 0
            nav_locator_data['np_limit_displace'] = (cur_flags & _PL_consts.PNCF.LIMIT_DISPLACEMENT) != 0

            nav_locator_data['np_allowed_veh'] = cur_flags & _PL_consts.PNCF.ALLOWED_VEHICLES_MASK

            if cur_flags & _PL_consts.PNCF.LEFT_BLINKER != 0:
                nav_locator_data['np_blinker'] = _PL_consts.PNCF.LEFT_BLINKER
            elif cur_flags & _PL_consts.PNCF.FORCE_NO_BLINKER != 0:
                nav_locator_data['np_blinker'] = _PL_consts.PNCF.FORCE_NO_BLINKER
            elif cur_flags & _PL_consts.PNCF.RIGHT_BLINKER != 0:
                nav_locator_data['np_blinker'] = _PL_consts.PNCF.RIGHT_BLINKER
            else:
                nav_locator_data['np_blinker'] = 0

            nav_locator_data['np_prior_modif'] = (cur_flags & _PL_consts.PNCF.PRIORITY_MASK) >> _PL_consts.PNCF.PRIORITY_SHIFT

            nav_locator_data['np_semaphore_id'] = cur_sempahore_id
            nav_locator_data['np_traffic_rule'] = cur_traffic_rule

            for node_data in nodes_data.values():

                if loc_key == "start":

                    for lane_index, curve_index in enumerate(node_data[3]):

                        if curve_index == index:

                            nav_locator_data['np_boundary'] = 1 + lane_index
                            nav_locator_data['np_boundary_node'] = node_data[0]
                            break

                else:

                    for lane_index, curve_index in enumerate(node_data[4]):

                        if curve_index == index:

                            nav_locator_data['np_boundary'] = 1 + lane_index + _PL_consts.PREFAB_LANE_COUNT_MAX
                            nav_locator_data['np_boundary_node'] = node_data[0]
                            break

            # locator already exists just set properties
            if curve_locators_to_create[loc_key] is False:

                loc_obj = conns_dict[index][loc_key]
                _set_nav_locator_props(loc_obj, nav_locator_data, loc_key == "start")

                continue

            loc = _create_nav_locator(nav_locator_data)
            _set_nav_locator_props(loc, nav_locator_data, loc_key == "start")
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
                if index not in conns_dict:
                    conns_dict[index] = {
                        loc_key: loc
                    }
                else:
                    conns_dict[index][loc_key] = loc

                # update references for prev or next connections
                for prev_curve_ind in related_curves:

                    if prev_curve_ind != -1:

                        if prev_curve_ind in conns_dict:

                            if related_end not in conns_dict[prev_curve_ind]:
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
    for map_point in map_points_data:

        # ignore auto generated map points
        if map_point[3] & _PL_consts.MPNF.NAV_BASE != 0:
            continue

        loc_index = map_point[1]

        for loc_neighbour_index in map_point[5]:

            if loc_neighbour_index == -1:
                continue

            if loc_index == loc_neighbour_index:
                continue

            for con in connections:
                if loc_neighbour_index == con[0] and loc_index == con[1]:
                    continue

                if loc_neighbour_index == con[1] and loc_index == con[0]:
                    continue

            connections.append((loc_index, loc_neighbour_index))

    # CREATE MAP POINTS
    mp_locs = {}
    for map_point in map_points_data:
        name = map_point[0]

        # ignore auto generated map points
        if map_point[3] & _PL_consts.MPNF.NAV_BASE != 0:
            continue

        loc = _create_map_locator(
            map_point[0],
            map_point[2],
            map_point[3],
            map_point[4],
        )

        _print_locator_result(loc, "Map Point", name)

        if loc:
            locators.append(loc)
            mp_locs[map_point[1]] = loc

    # APPLY MAP POINT CONNECTIONS
    for connection in connections:

        # safety check if connection indexes really exists
        if connection[0] in mp_locs and connection[1] in mp_locs:
            start_node = mp_locs[connection[0]]
            end_node = mp_locs[connection[1]]
        else:
            lprint('E Map connection out of range: %s', (str(connection),))
            continue

        _group_connections_wrapper.create_connection(start_node, end_node)

    # COLLECT TRIGGER POINT CONNECTIONS
    connections = []
    for tr_point in trigger_points_data:

        loc_index = tr_point[1]

        # print('      name: %s' % tr_point[0])
        if len(tr_point[7]) != 2:
            lprint('W Unexpected number of connections (%i) for Trigger Point "%s"!', (len(tr_point[7]), tr_point[0]))

        for loc_neighbour_index in tr_point[7]:
            connections.append((loc_index, loc_neighbour_index))

    # CREATE TRIGGER POINTS
    tp_locs = {}
    for tr_point in trigger_points_data:
        name = tr_point[0]
        # print('trigger_points_data[%r]: %s' % (name, str(tr_point)))
        loc = _create_trigger_locator(
            tr_point[0],
            tr_point[2],
            tr_point[3],
            tr_point[4],
            tr_point[5],
            tr_point[6],
            scs_globals.scs_trigger_actions_inventory
        )

        _print_locator_result(loc, "Trigger Point", name)

        if loc:
            locators.append(loc)
            tp_locs[tr_point[1]] = loc

    for connection in connections:

        # safety check if connection indexes really exists
        if connection[0] in tp_locs and connection[1] in tp_locs:
            start_node = tp_locs[connection[0]]
            end_node = tp_locs[connection[1]]
        else:
            print('E Trigger connection: %s', (str(connection),))
            continue

        _group_connections_wrapper.create_connection(start_node, end_node)

    print("************************************")
    return {'FINISHED'}, locators
