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
import os
from bpy.types import Panel
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _ObjectPanelBlDefs(_shared.HeaderIconPanel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"


def _draw_data_group_panel(layout):
    """Draw data group panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    row = layout.row()
    row.separator()
    row = layout.row()
    row.separator()
    box = row.box()
    col = box.column(align=True)
    col_row = col.row(align=True)
    col_row.operator('scene.add_data_group')
    col_row.operator('scene.remove_data_group')
    col.operator('scene.print_data_group')
    col.operator('scene.restore_data_group')
    # col_row = col.row(align=True)
    # col_row.operator('scene.add_to_the_group')
    # col_row.operator('scene.remove_from_the_group')
    row.separator()


def _draw_collect_data_panel(layout):
    """Draw collect data panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    row = layout.row()
    row.separator()
    row = layout.row()
    row.separator()
    box = row.box()
    col = box.column(align=True)
    col.operator('object.collect_nav_curve_connections')
    col.operator('object.collect_map_line_connections')
    col.operator('object.collect_trigger_line_connections')
    # col.template_component_menu(obj, 'scs_props', name='Props:')
    row.separator()


def _draw_locator_display_settings_panel(layout, scene, obj):
    """Draw Locator Display Settings panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param obj: SCS Locator Object
    :type obj: bpy.types.Object
    """
    if obj.scs_props.locator_type != 'None':
        box = layout.box()
        if scene.scs_props.locator_display_settings_expand:
            row = box.row()
            row.prop(scene.scs_props, 'locator_display_settings_expand', text="Display Settings:", icon='TRIA_DOWN', icon_only=True, emboss=False)
            row.label('')
            row = box.row()
            row.prop(scene.scs_props, 'display_locators', icon='NONE', toggle=True)
            if scene.scs_props.display_locators:
                row = box.row(align=True)
                row.prop(scene.scs_props, 'locator_size', icon='NONE')
                row.prop(scene.scs_props, 'locator_empty_size', icon='NONE')
                if obj.scs_props.locator_type == 'Prefab':
                    row = box.row()
                    row.prop(scene.scs_props, 'locator_prefab_wire_color', icon='NONE')
                elif obj.scs_props.locator_type == 'Model':
                    row = box.row()
                    row.prop(scene.scs_props, 'locator_model_wire_color', icon='NONE')
                elif obj.scs_props.locator_type == 'Collision':
                    col = box.column()
                    col_row = col.row()
                    col_row.prop(scene.scs_props, 'locator_coll_wire_color', icon='NONE')
                    col_row = col.row()
                    col_row.prop(scene.scs_props, 'locator_coll_face_color', icon='NONE')
            else:
                row = box.row()
                row.prop(scene.scs_props, 'locator_empty_size', icon='NONE')
            if obj.scs_props.locator_type == 'Prefab':
                row = box.row()
                row.prop(scene.scs_props, 'display_connections', icon='NONE', toggle=True)
                if scene.scs_props.display_connections:
                    row = box.row()
                    row.prop(scene.scs_props, 'curve_base_color', icon='NONE')
                    row = box.row()
                    row.prop(scene.scs_props, 'curve_segments', icon='NONE')
            row = box.row()
            row.prop(scene.scs_props, 'display_info', icon='NONE')
            if scene.scs_props.display_info != 'none':
                row = box.row()
                row.prop(scene.scs_props, 'info_text_color', icon='NONE')
        else:
            row = box.row()
            row.prop(scene.scs_props, 'locator_display_settings_expand', text="Display Settings:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
            row.label('')


def _draw_locator_preview_panel(layout, obj, draw_box=True):
    """Draw Locator Preview panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param obj: SCS Locator Object
    :type obj: bpy.types.Object
    :param draw_box: Whether to draw a box around the Panel
    :type draw_box: bool
    """
    if draw_box:
        box = layout.box()
    else:
        box = layout

    # Locator Preview Model Directory (FILE_PATH - relative)
    row = box.row(align=True)

    # validity check for preview model path
    row.alert = True
    if obj.scs_props.locator_preview_model_path == "":
        row.alert = False
    elif os.path.isdir(_get_scs_globals().scs_project_path):
        if os.path.isfile(_get_scs_globals().scs_project_path + os.sep + obj.scs_props.locator_preview_model_path):
            if obj.scs_props.locator_preview_model_path.endswith(".pim"):
                row.alert = False

    row.prop(obj.scs_props, 'locator_preview_model_path', expand=True)
    row.operator('object.select_preview_model_path', text='', icon='FILESEL')

    # Locator Preview Model Controls
    row = box.row()
    row.prop(obj.scs_props, 'locator_show_preview_model', icon='NONE')
    row.prop(obj.scs_props, 'locator_preview_model_type', icon='NONE')


def _draw_locator_panel(layout, context, scene, obj):
    """Draw Locator Settings Panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param context: Blender Context
    :type context: bpy.context
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param obj: SCS Locator Object
    :type obj: bpy.types.Object
    """

    group_name = "SCS_connection_numbers"
    nav_curve_data_name = "nav_curves_used_numbers"
    map_line_data_name = "map_lines_used_numbers"
    tp_line_data_name = "tp_lines_used_numbers"

    layout_box = layout.box()
    if scene.scs_props.locator_settings_expand:
        loc_header = layout_box.row()
        loc_header.prop(scene.scs_props, 'locator_settings_expand', text="Locator Settings:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        loc_header.label('')
        row = layout_box.row()
        row.prop(obj.scs_props, 'locator_type', icon='NONE')

        # MODEL LOCATORS
        if obj.scs_props.locator_type == 'Model':
            col = layout_box.column()
            col.prop(obj, 'name')
            # col.prop(obj.scs_props, 'locator_model_hookup', icon='NONE')
            col.prop_search(obj.scs_props, 'locator_model_hookup', _get_scs_globals(), 'scs_hookup_inventory', icon='NONE')
            # (MODEL) LOCATOR PREVIEW PANEL
            _draw_locator_preview_panel(layout_box, obj)

        # COLLISION LOCATORS
        elif obj.scs_props.locator_type == 'Collision':
            row = layout_box.row()
            row.prop(obj.scs_props, 'locator_collider_type', icon='NONE')
            row = layout_box.row()
            row_box = row.box()
            display_row = row_box.row()
            if obj.scs_props.locator_collider_wires:
                icon = "FILE_TICK"
            else:
                icon = "X_VEC"
            display_row.prop(obj.scs_props, 'locator_collider_wires', text='Wireframes', icon=icon, toggle=True)
            if obj.scs_props.locator_collider_faces:
                icon = "FILE_TICK"
            else:
                icon = "X_VEC"
            display_row.prop(obj.scs_props, 'locator_collider_faces', text='Faces', icon=icon, toggle=True)
            if obj.scs_props.locator_collider_type != 'Convex':
                if obj.scs_props.locator_collider_centered:
                    icon = "FILE_TICK"
                else:
                    icon = "X_VEC"
                row_box.prop(obj.scs_props, 'locator_collider_centered', icon=icon, toggle=True)
            box_col = layout_box.column()
            loc_set = box_col.column(align=True)
            loc_set.prop(obj.scs_props, 'locator_collider_mass', icon='NONE')
            if obj.scs_props.locator_collider_type == 'Convex':
                loc_set.prop(obj.scs_props, 'locator_collider_margin', icon='NONE')
            # loc_set = row_box.row()
            # loc_set.prop(obj.scs_props, 'locator_collider_material', icon='NONE')
            row_box_row = box_col.row()
            if obj.scs_props.locator_collider_type == 'Box':
                col = row_box_row.column(align=True)
                col.prop(obj.scs_props, 'locator_collider_box_x', icon='NONE')
                col.prop(obj.scs_props, 'locator_collider_box_y', icon='NONE')
                col.prop(obj.scs_props, 'locator_collider_box_z', icon='NONE')
            elif obj.scs_props.locator_collider_type == 'Sphere':
                row = row_box_row.row()
                row.prop(obj.scs_props, 'locator_collider_dia', text='Sphere Diameter', icon='NONE')
            elif obj.scs_props.locator_collider_type == 'Capsule':
                col = row_box_row.column(align=True)
                col.prop(obj.scs_props, 'locator_collider_dia', text='Capsule Diameter', icon='NONE')
                col.prop(obj.scs_props, 'locator_collider_len', text='Capsule Length', icon='NONE')
            elif obj.scs_props.locator_collider_type == 'Cylinder':
                col = row_box_row.column(align=True)
                col.prop(obj.scs_props, 'locator_collider_dia', text='Cylinder Diameter', icon='NONE')
                col.prop(obj.scs_props, 'locator_collider_len', text='Cylinder Length', icon='NONE')
            elif obj.scs_props.locator_collider_type == 'Convex':
                col_row = row_box_row.row()
                col_row.label('%i hull vertices.' % obj.scs_props.locator_collider_vertices, icon='INFO')

        # PREFAB LOCATORS
        elif obj.scs_props.locator_type == 'Prefab':
            box_row = layout_box.row()
            box_row.prop(obj.scs_props, 'locator_prefab_type', icon='NONE')
            box_row = layout_box.row()
            box_row_box = box_row.box()
            if obj.scs_props.locator_prefab_type == 'Control Node':
                loc_set = box_row_box.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_con_node_index', icon='NONE')
                loc_set = box_row_box.row()
                loc_set.operator('object.assign_terrain_points', text="Assign Terrain Points")
            if obj.scs_props.locator_prefab_type == 'Sign':
                loc_set = box_row_box.column()
                loc_set.prop_search(obj.scs_props, 'locator_prefab_sign_model', _get_scs_globals(), 'scs_sign_model_inventory',
                                    icon='NONE')
            if obj.scs_props.locator_prefab_type == 'Spawn Point':
                loc_set = box_row_box.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_spawn_type', icon='NONE')
            if obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
                loc_set = box_row_box.column()
                loc_set.prop(obj.scs_props, 'locator_prefab_tsem_id', icon='NONE')
                # loc_set.prop(obj.scs_props, 'locator_prefab_tsem_model', icon='NONE')
                # loc_set.prop(obj.scs_props, 'locator_prefab_tsem_profile', icon='NONE')
                loc_set.prop_search(obj.scs_props, 'locator_prefab_tsem_profile', _get_scs_globals(), 'scs_tsem_profile_inventory',
                                    icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_tsem_type', icon='NONE')
                loc_set_col = loc_set.column()
                if obj.scs_props.locator_prefab_tsem_type in ('0', '1'):
                    loc_set_col.enabled = False
                else:
                    loc_set_col.enabled = True
                loc_set = loc_set_col.row()
                loc_set.separator()
                loc_set = loc_set_col.row(align=True)
                if obj.scs_props.locator_prefab_tsem_type == '6':
                    loc_set.label('Distances:', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_gm', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_om1', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_rm', icon='NONE')
                    # loc_set.prop(obj.scs_props, 'locator_prefab_tsem_om2', icon='NONE')
                else:
                    loc_set.label('Intervals:', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_gs', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_os1', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_rs', icon='NONE')
                    loc_set.prop(obj.scs_props, 'locator_prefab_tsem_os2', icon='NONE')
                loc_set = loc_set_col.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_tsem_cyc_delay', icon='NONE')
                # loc_set = box_row_box.row()
                # loc_set.prop(obj.scs_props, 'locator_prefab_tsem_activation', icon='NONE')
                # loc_set = box_row_box.row()
                # loc_set.prop(obj.scs_props, 'locator_prefab_tsem_ai_only', icon='NONE')
            # if obj.scs_props.locator_prefab_type == 'cob':
            # loc_set = box_row_box.row()
            # loc_set.prop(obj.scs_props, 'locator_prefab_colbox_size', icon='NONE')
            # loc_set = box_row_box.row()
            # loc_set.label('Colbox Size:', icon='NONE')
            # loc_set.prop(obj.scs_props, 'locator_prefab_colbox_size_w', icon='NONE')
            # loc_set.prop(obj.scs_props, 'locator_prefab_colbox_size_h', icon='NONE')
            # loc_set.prop(obj.scs_props, 'locator_prefab_colbox_size_d', icon='NONE')
            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                loc_set = box_row_box.column(align=True)

                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_np_stopper', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_np_low_probab', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_np_add_priority', icon='NONE')

                # loc_set_row = loc_set.row()
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_tl_activ', icon='NONE')
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_low_prior', icon='NONE')
                # loc_set_row = loc_set.row()
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_ig_blink_prior', icon='NONE')
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_crossroad', icon='NONE')
                # loc_set_row = loc_set.row()
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_stopper', icon='NONE')
                # loc_set_row.prop(obj.scs_props, 'locator_prefab_np_low_probab', icon='NONE')

                loc_set = box_row_box.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_np_allowed_veh', icon='NONE')
                # loc_set = box_row_box.row()
                # loc_set.prop(obj.scs_props, 'locator_prefab_np_speed_limit', icon='NONE')
                loc_set = box_row_box.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_np_blinker', icon='NONE', expand=True)
                loc_set = box_row_box.column()
                loc_set.prop(obj.scs_props, 'locator_prefab_np_priority_mask', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_np_traffic_light', icon='NONE')
                loc_set.prop_search(obj.scs_props, 'locator_prefab_np_traffic_rule', _get_scs_globals(),
                                    'scs_traffic_rules_inventory', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_np_boundary', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_np_boundary_node', icon='NONE')

                loc_set = box_row_box.row()
                if len(context.selected_objects) == 2:
                    loc0_obj = None
                    loc1_obj = context.active_object

                    # check if both selected objects are navigation points and set not active object
                    is_mp = 0
                    for obj_locator in context.selected_objects:
                        if obj_locator.scs_props.locator_type == 'Prefab' and obj_locator.scs_props.locator_prefab_type == 'Navigation Point':
                            is_mp += 1
                            if obj_locator != context.active_object:
                                loc0_obj = obj_locator
                    if is_mp == 2:
                        if _connections_group_wrapper.has_connection(loc0_obj, loc1_obj):
                            loc_set.operator('object.disconnect_prefab_locators', text="Disconnect Navigation Points", icon='UNLINKED')
                        else:
                            loc_set.operator('object.connect_prefab_locators', text="Connect Navigation Points", icon='LINKED')
                    else:
                        loc_set.enabled = False
                        loc_set.operator('object.connect_prefab_locators', text="Connect / Disconnect Navigation Points", icon='LINKED')
                else:
                    loc_set.enabled = False
                    loc_set.operator('object.connect_prefab_locators', text="Connect / Disconnect Navigation Points", icon='LINKED')

            # if obj.scs_props.locator_prefab_type == 'nac':
            # loc_set = box_row_box.row()
            # loc_set.label('?', icon='QUESTION')
            if obj.scs_props.locator_prefab_type == 'Map Point':
                loc_set = box_row_box.column(align=True)
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_road_over', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_no_outline', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_no_arrow', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_prefab_exit', icon='NONE')
                loc_set = box_row_box.column()
                loc_set.prop(obj.scs_props, 'locator_prefab_mp_road_size', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_mp_road_offset', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_mp_custom_color', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_mp_assigned_node', icon='NONE')
                loc_set = box_row_box.column(align=True)
                loc_set.label('Destination Nodes:', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_des_nodes_0', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_des_nodes_2', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_des_nodes_1', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_des_nodes_3', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_mp_des_nodes_ct', icon='NONE')

                loc_set = box_row_box.row()
                if len(context.selected_objects) == 2:

                    # check if both selected objects are navigation points and set not active object
                    is_mp = 0
                    for obj_locator in context.selected_objects:
                        if obj_locator.scs_props.locator_type == 'Prefab' and obj_locator.scs_props.locator_prefab_type == 'Map Point':
                            is_mp += 1
                    if is_mp == 2:
                        if _connections_group_wrapper.has_connection(context.selected_objects[0], context.selected_objects[1]):
                            loc_set.operator('object.disconnect_prefab_locators', text="Disconnect Map Points", icon='UNLINKED')
                        else:
                            loc_set.operator('object.connect_prefab_locators', text="Connect Map Points", icon='LINKED')
                    else:
                        loc_set.enabled = False
                        loc_set.operator('object.connect_prefab_locators', text="Connect / Disconnect Map Points", icon='LINKED')
                else:
                    loc_set.enabled = False
                    loc_set.operator('object.connect_prefab_locators', text="Connect / Disconnect Map Points", icon='LINKED')

            if obj.scs_props.locator_prefab_type == 'Trigger Point':
                loc_set = box_row_box.row()
                loc_set.prop(obj.scs_props, 'locator_prefab_tp_action', icon='NONE')
                loc_set = box_row_box.column(align=True)
                loc_set.prop(obj.scs_props, 'locator_prefab_tp_range', icon='NONE')
                loc_set.prop(obj.scs_props, 'locator_prefab_tp_reset_delay', icon='NONE')
                loc_set = box_row_box.column(align=True)
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_tp_sphere_trigger', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_tp_partial_activ', icon='NONE')
                loc_set_row = loc_set.row()
                loc_set_row.prop(obj.scs_props, 'locator_prefab_tp_onetime_activ', icon='NONE')
                loc_set_row.prop(obj.scs_props, 'locator_prefab_tp_manual_activ', icon='NONE')

                loc_set = box_row_box.row()
                if len(context.selected_objects) == 2:

                    # check if both selected objects are navigation points and set not active object
                    is_tp = 0
                    for obj_locator in context.selected_objects:
                        if obj_locator.scs_props.locator_type == 'Prefab' and obj_locator.scs_props.locator_prefab_type == 'Trigger Point':
                            is_tp += 1
                    if is_tp == 2:
                        if _connections_group_wrapper.has_connection(context.selected_objects[0], context.selected_objects[1]):
                            loc_set.operator('object.disconnect_prefab_locators', text='Disconnect Trigger Points', icon='UNLINKED')
                        else:
                            loc_set.operator('object.connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')
                    else:
                        loc_set.enabled = False
                        loc_set.operator('object.connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')
                else:
                    loc_set.enabled = False
                    loc_set.operator('object.connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')

            # (PREFAB) LOCATOR PREVIEW PANEL
            _draw_locator_preview_panel(layout_box, obj)

            # DISPLAY SETTINGS
            # _draw_locator_display_settings_panel(layout_box, scene, obj)
    else:
        loc_set = layout_box.row()
        loc_set.prop(scene.scs_props, 'locator_settings_expand', text="Locator Settings:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        loc_set.label('')


def _draw_animation_section(layout):
    """Draw Animation section.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    context = bpy.context
    active_object = context.active_object
    scs_root_object = _object_utils.get_scs_root(active_object)
    scs_object_animation_inventory = scs_root_object.scs_object_animation_inventory
    active_scs_animation = scs_root_object.scs_props.active_scs_animation
    if len(scs_object_animation_inventory) > active_scs_animation:
        active_animation = scs_object_animation_inventory[active_scs_animation]

        row = layout.row()
        row_row = row.row(align=True)
        row_row.prop_search(active_animation, 'action', bpy.data, 'actions', text="", icon='NONE')
        # row_row.separator()
        box_row_row = row_row.row(align=True)
        box_row_row.operator('scene.import_scs_anim_actions', text='', icon='IMPORT')
        if active_object.animation_data:
            if active_object.animation_data.action:
                box_row_row.operator('scene.export_scs_anim_action', text='', icon='EXPORT')
                box_row_row = row_row.row()
                box_row_row.scale_x = 0.35
                if active_animation.export:
                    icon = "FILE_TICK"
                else:
                    icon = "X_VEC"
                box_row_row.prop(active_animation, 'export', text="Export", icon=icon, toggle=True)

        row = layout.row()
        row_row = row.row(align=True)
        row_row.prop(active_animation, 'anim_start', text="Start", icon='NONE')
        row_row.prop(active_animation, 'anim_end', text="End", icon='NONE')
        row_row.prop(active_animation, 'length', text="Length", icon='NONE')

        row = layout.row()
        row.prop(active_animation, 'anim_export_filepath', text="", icon='EXPORT')


def _draw_action_panel(layout):
    """Draw Action settings panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    context = bpy.context
    active_object = context.active_object

    box = layout.box()
    if active_object.animation_data:
        box_row = box.row(align=True)
        box_row.template_ID(active_object.animation_data, 'action', new="action.new")

        # layout_row = box_row.row(align=True)
        # layout_row.operator('scene.import_scs_anim_actions', text='', icon='IMPORT')
        if active_object.animation_data.action:
            # layout_row.operator('scene.export_scs_anim_action', text='', icon='EXPORT')
            # layout_row = box_row.row()
            # layout_row.scale_x = 0.35
            # layout_row.prop(active_object.animation_data.action.scs_props, "export_action", text="Batch Export", toggle=True)

            # box_row = box.row()
            # box_row.enabled = active_object.animation_data.action.scs_props.export_action
            # box_row.prop(active_object.animation_data.action.scs_props, "anim_export_filepath", icon='EXPORT')

            box_row = box.row()
            box_row_row = box_row.row(align=True)
            box_row_row.operator('scene.increase_animation_steps', text='', icon='ZOOMIN')
            box_row_row.operator('scene.decrease_animation_steps', text='', icon='ZOOMOUT')
            # box_row_row.operator('scene.euler_filter', text='', icon='IPO')  # TODO: Turned off for now, Blender's Build-in Euler Filter needs
            # Graph context and "apply_euler_filter()" function still doesn't work.
            box_row.prop(active_object.animation_data.action.scs_props, "anim_export_step")
            # box_row.prop(active_object.animation_data.action.scs_props, "action_length")
    else:
        box_row = box.row()
        # box_row.operator('scene.import_scs_anim_actions', text="Import Animation Action", icon='FILESEL')
        box_row.operator('scene.import_scs_anim_actions', text="Import Animation Actions", icon='IMPORT')


def _draw_animplayer_panel(layout):
    """Draw Animation Player panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    context = bpy.context
    scene = context.scene
    # active_object = context.active_object
    # scs_root_object = utils.get_scs_root_object(active_object)
    screen = context.screen

    layout_box = layout.box()
    if scene.scs_props.animplayer_panel_expand:
        row = layout_box.row()
        row.prop(scene.scs_props, 'animplayer_panel_expand', text="Animation Player:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        row.label('')

        # layout_box_row = layout_box.row()
        # layout_row = layout_box_row.row(align=True)
        # if not scene.use_preview_range:
        # layout_row.prop(scene, "frame_start", text="Start")
        # layout_row.prop(scene, "frame_end", text="End")
        # else:
        # layout_row.prop(scene, "frame_preview_start", text="Start")
        # layout_row.prop(scene, "frame_preview_end", text="End")
        # layout_row = layout_box_row.row()
        # layout_row.scale_x = 0.7
        # layout_row.prop(scene, "frame_current", text='')

        layout_box_row = layout_box.row()
        layout_col = layout_box_row.column(align=True)
        layout_row = layout_col.row(align=True)
        layout_row.prop(scene, "frame_start", text="Start")
        layout_row.prop(scene, "frame_end", text="End")
        layout_row = layout_col.row(align=True)
        layout_row.prop(scene, "frame_preview_start", text="Start")
        layout_row.prop(scene, "frame_preview_end", text="End")
        layout_col = layout_box_row.column(align=True)
        layout_col.scale_x = 0.7
        layout_col.scale_y = 2.0
        layout_col.prop(scene, "frame_current", text='')

        layout_box_row = layout_box.row()
        layout_box_row.prop(scene, "use_preview_range", text='', toggle=True)
        layout_row = layout_box_row.row(align=True)
        layout_row.operator("screen.frame_jump", text='', icon='REW').end = False
        layout_row.operator("screen.keyframe_jump", text='', icon='PREV_KEYFRAME').next = False
        if not screen.is_animation_playing:
            if scene.sync_mode == 'AUDIO_SYNC' and context.user_preferences.system.audio_device == 'JACK':
                sub = layout_row.row(align=True)
                sub.scale_x = 2.0
                sub.operator("screen.animation_play", text='', icon='PLAY')
            else:
                layout_row.operator("screen.animation_play", text='', icon='PLAY_REVERSE').reverse = True
                layout_row.operator("screen.animation_play", text='', icon='PLAY')
        else:
            sub = layout_row.row(align=True)
            sub.scale_x = 2.0
            sub.operator("screen.animation_play", text='', icon='PAUSE')
        layout_row.operator("screen.keyframe_jump", text='', icon='NEXT_KEYFRAME').next = True
        layout_row.operator("screen.frame_jump", text='', icon='FF').end = True
        layout_row = layout_box_row.row(align=True)
        layout_row.scale_x = 0.4
        layout_row.prop(scene.render, "fps")
        layout_row.prop(scene.render, "fps_base", text="/")
    else:
        row = layout_box.row()
        row.prop(scene.scs_props, 'animplayer_panel_expand', text="Animation Player:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.label('')


def _draw_animation_settings_panel(layout):
    """Draw Animation settings panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    """
    context = bpy.context
    scene = context.scene
    active_object = context.active_object
    scs_root_object = _object_utils.get_scs_root(active_object)
    layout_box = layout.box()
    if scene.scs_props.animation_settings_expand:
        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props, 'animation_settings_expand', text="Animation Settings:",
                            icon='TRIA_DOWN', icon_only=True, emboss=False)
        layout_box_row.label('')

        # ACTION SETTINGS PANEL
        _draw_action_panel(layout_box)

        # layout_box_row = layout_box.row()
        # layout_box_row.prop(bpy.data, 'actions', text="Animation Actions:", icon='ACTION')

        action_box = layout_box.box()
        if scs_root_object:

            # ANIMATION LIST
            layout_setting = action_box.row()
            layout_setting.template_list(
                'SCSObjectAnimationSlots',
                list_id="",
                dataptr=scs_root_object,
                propname="scs_object_animation_inventory",
                active_dataptr=scs_root_object.scs_props,
                active_propname="active_scs_animation",
                rows=1,
                maxrows=5,
                type='DEFAULT',
                columns=9,
            )

            # LIST BUTTONS
            list_buttons = layout_setting.column(align=True)
            list_buttons.operator('object.add_scs_animation', text="", icon='ZOOMIN')
            list_buttons.operator('object.remove_scs_animation', text="", icon='ZOOMOUT')

            # ANIMATION SETTINGS
            if len(scs_root_object.scs_object_animation_inventory) > 0:
                _draw_animation_section(action_box)
            else:
                action_box.label('No Animation!', icon='INFO')
        else:
            action_box.label("No 'SCS Root Object'!", icon='INFO')

        # ANIMATION PLAYER PANEL
        _draw_animplayer_panel(layout_box)

    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props, 'animation_settings_expand', text="Animation Settings:",
                            icon='TRIA_RIGHT', icon_only=True, emboss=False)
        layout_box_row.label('')


def _draw_icon_part_tools(layout, index):
    """Draws Part Tools icons in a line.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param index: index of part in parts inventory
    :type index: int
    """
    props = layout.operator('object.switch_part_selection', text="", emboss=False, icon='RESTRICT_SELECT_OFF')
    props.part_index = index
    props.select_type = _OP_consts.SelectionType.undecided
    props = layout.operator('object.switch_part_visibility', text="", emboss=False, icon='RESTRICT_VIEW_OFF')
    props.part_index = index
    props.view_type = _OP_consts.ViewType.undecided


def _draw_icon_variant_tools(layout, index):
    """Draws Variant Tools icons in a line.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param index: index of variant in variants inventory
    :type index: int
    """
    props = layout.operator('object.switch_variant_selection', text="", emboss=False, icon='RESTRICT_SELECT_OFF')
    props.variant_index = index
    props.select_type = _OP_consts.SelectionType.undecided
    props = layout.operator('object.switch_variant_visibility', text="", emboss=False, icon='RESTRICT_VIEW_OFF')
    props.variant_index = index
    props.view_type = _OP_consts.ViewType.undecided


def _draw_icon_variant_tools_line(layout, index):
    """Creates a line with minimalistic Variant Tools.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param index: index of active variant
    :type index: int
    """
    row = layout.row(align=True)
    col = row.column()
    col.alignment = 'LEFT'
    col.label("Additional Variant Tools:")
    col = row.column()
    col_row = col.row(align=True)
    col_row.alignment = 'RIGHT'
    _draw_icon_variant_tools(col_row, index)


def _draw_part_list(layout, root_obj):
    """Creates an editable Part list.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param root_obj: SCS Root Object
    :type root_obj: bpy.types.Object
    """
    row = layout.row()
    row.template_list(
        'SCSObjectPartSlots',
        list_id="",
        dataptr=root_obj,
        propname="scs_object_part_inventory",
        active_dataptr=root_obj.scs_props,
        active_propname="active_scs_part",
        rows=3,
        maxrows=5,
        type='DEFAULT',
        columns=9
    )

    # LIST BUTTONS
    col = row.column(align=True)
    col.operator('object.add_scs_part', text="", icon='ZOOMIN')
    col.operator('object.remove_scs_part', text="", icon='ZOOMOUT')
    col.operator('object.clean_scs_parts', text="", icon='FILE_REFRESH')


def _draw_scs_part_panel(layout, scene, active_object, scs_root_object):
    """Creates 'SCS Parts' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param active_object: active object
    :type active_object: bpy.types.Object
    :param scs_root_object: SCS Root Object
    :type scs_root_object: bpy.types.Object
    """

    layout_column = layout.column(align=True)
    layout_box = layout_column.box()

    if scene.scs_props.scs_part_panel_expand:

        # HEADER (COLLAPSIBLE - OPENED)
        row = layout_box.row()
        row.prop(scene.scs_props, 'scs_part_panel_expand', text="SCS Parts:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        row.prop(scene.scs_props, 'scs_part_panel_expand', text=" ", icon='NONE', icon_only=True, emboss=False)

        layout_box = layout_column.box()  # body box

        if len(_object_utils.gather_scs_roots(bpy.context.selected_objects)) > 1 and active_object is not scs_root_object:

            col = layout_box.box().column(align=True)
            row = col.row()
            row.label("WARNING", icon="ERROR")
            row = col.row()
            row.label("Can not edit parts! Selection has multiple game objects.")

        else:  # more roots or active object is root object

            # DEBUG
            if not active_object is scs_root_object:

                row = layout_box.row(align=True)
                row.label("DEBUG - active obj part:")
                row.prop(active_object.scs_props, 'scs_part', text="")

            # PART LIST
            _draw_part_list(layout_box, scs_root_object)

            # ASSIGNEMENT CONTROLS
            if not active_object is scs_root_object:

                row = layout_box.row(align=True)
                row.operator("object.assign_scs_part", text="Assign")
                props = row.operator("object.switch_part_selection", text="Select")
                props.part_index = scs_root_object.scs_props.active_scs_part
                props.select_type = _OP_consts.SelectionType.shift_select
                props = row.operator("object.switch_part_selection", text="Deselect")
                props.part_index = scs_root_object.scs_props.active_scs_part
                props.select_type = _OP_consts.SelectionType.ctrl_select

    else:
        row = layout_box.row()
        row.prop(scene.scs_props, 'scs_part_panel_expand', text="SCS Parts:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.prop(scene.scs_props, 'scs_part_panel_expand', text=" ", icon='NONE', icon_only=True, emboss=False)


def _draw_part_list_for_variant(layout, scene, variant):
    """Creates 'SCS Part' items for provided 'SCS Variant'.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param variant: Variant from the SCS Root Object
    :type variant: io_scs_tools.ObjectVariantInventory
    """
    if scene.scs_props.part_list_sorted:
        inventory_names = []
        for part in variant.parts:
            inventory_names.append(part.name)
        for name in sorted(inventory_names):
            part = variant.parts[name]
            layout.prop(part, 'include', text=part.name, toggle=True)
    else:
        for part in variant.parts:
            layout.prop(part, 'include', text=part.name, toggle=True)


def _draw_vertical_variant_block(layout, scene, variant):
    """Creates vertical 'SCS Variant' list.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param variant: Variant from the SCS Root Object
    :type variant: io_scs_tools.ObjectVariantInventory
    """
    layout_box = layout.box()
    row = layout_box.row()
    row.alignment = 'CENTER'
    # row.prop_enum(scene.scs_props, 'part_variants', variant.name)
    # row.label('[ ' + variant.name + ' ]', icon='NONE')
    row.label(variant.name, icon='NONE')
    row = layout_box.row()
    row.separator()
    row.separator()
    box = row.box()
    col = box.column(align=True)
    _draw_part_list_for_variant(col, scene, variant)
    row.separator()
    row.separator()


'''
def draw_horizontal_variant_block(layout, scene, variant):
"""Creates horizontal 'SCS Variant' list."""
    variantEntryBox = layout.box()
    variantItem = variantEntryBox.row()
    variantItem.alignment = 'CENTER'
    variantItem.label(variant.name, icon='NONE')
    variantEntryPart = variantEntryBox.column(align=True)
    draw_part_list_for_variant(variantEntryPart, scene, variant)
'''


def _draw_horizontal_scs_variant_block(layout, variant):
    """Creates horizontal 'SCS Variant' list.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param variant: Variant from the SCS Root Object
    :type variant: io_scs_tools.ObjectVariantInventory
    """
    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    row.label(variant.name, icon='NONE')
    col = box.column(align=True)
    _draw_part_list_for_variant(col, bpy.context.scene, variant)


def _draw_scs_root_panel(layout, scene, obj):
    """Creates 'SCS Root Object' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param obj: SCS Root Object
    :type obj: bpy.types.Object
    """
    box = layout.box()
    if scene.scs_props.scs_root_panel_settings_expand:
        row = box.row()
        row.prop(scene.scs_props, 'scs_root_panel_settings_expand', text="Root Object:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        row.label('')
        col = box.column(align=True)
        if obj.scs_props.scs_root_object_export_enabled:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        col.prop(obj.scs_props, 'scs_root_object_export_enabled', text="Export Inclusion", icon=icon, toggle=True)
        row = col.row(align=True)
        if not obj.scs_props.scs_root_object_export_enabled:
            row.enabled = False
        row.prop(obj.scs_props, 'scs_root_animated', expand=True)
        col = box.column()
        if not obj.scs_props.scs_root_object_export_enabled:
            col.enabled = False

        # Global Export Filepath (DIR_PATH - absolute)
        row = col.row(align=True)
        row.prop(obj.scs_props, 'scs_root_object_allow_custom_path', text='', icon='NONE')
        row2 = row.row(align=True)
        if obj.scs_props.scs_root_object_allow_custom_path:
            row2.enabled = True
        else:
            row2.enabled = False
        row2.prop(obj.scs_props, 'scs_root_object_export_filepath', text='', icon='EXPORT')
        row2.operator('scene.select_game_object_custom_export_filepath', text='', icon='FILESEL')
        # row2.prop(obj.scs_props, 'scs_root_object_animations', icon='NONE')
    else:
        row = box.row()
        row.prop(scene.scs_props, 'scs_root_panel_settings_expand', text="Root Object:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.label('')


def _draw_empty_object_panel(layout, context, scene, obj):
    """Creates 'Empty Object' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param context: Blender Context
    :type context: bpy.context
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param obj: Blender Empty Object
    :type obj: bpy.types.Object
    """
    layout_column = layout.column(align=True)
    box = layout_column.box()
    if scene.scs_props.empty_object_settings_expand:
        row = box.row()
        row.prop(scene.scs_props, 'empty_object_settings_expand', text="SCS Objects:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        row.label('')
        box = layout_column.box()
        row = box.row()
        row.prop(obj.scs_props, 'empty_object_type', text="Object Type", icon='NONE')

        # SCS ROOT PANEL
        if obj.scs_props.empty_object_type == 'SCS_Root':
            _draw_scs_root_panel(box, scene, obj)

        # LOCATOR PANEL
        elif obj.scs_props.empty_object_type == 'Locator':
            _draw_locator_panel(box, context, scene, obj)
    else:
        row = box.row()
        row.prop(scene.scs_props, 'empty_object_settings_expand', text="SCS Objects:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.label('')


def _draw_scs_variant_panel(layout, scene, scs_root_object):
    """Creates 'SCS Variants' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param scs_root_object: Blender SCS Root object
    :type scs_root_object: bpy.types.Object
    """

    layout_column = layout.column(align=True)
    box = layout_column.box()

    variant_inventory = scs_root_object.scs_object_variant_inventory

    if scene.scs_props.scs_variant_panel_expand:

        # HEADER (COLLAPSIBLE - OPENED)
        split = box.split(percentage=0.5)
        row = split.row()
        row.prop(scene.scs_props, 'scs_variant_panel_expand', text="SCS Variants:", icon='TRIA_DOWN', icon_only=True, emboss=False)

        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(scene.scs_props, 'variant_views', text='', icon='NONE', expand=True, toggle=True)

        box = layout_column.box()  # body box

        # VARIANT LIST
        row = box.row()
        col = row.column()
        col.template_list(
            'SCSObjectVariantSlots',
            list_id="",
            dataptr=scs_root_object,
            propname="scs_object_variant_inventory",
            active_dataptr=scs_root_object.scs_props,
            active_propname="active_scs_variant",
            rows=1,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )

        if scene.scs_props.variant_views == 'integrated':

            # VARIANT TOOLS FOR INTEGRATED LIST
            _draw_icon_variant_tools_line(col, scs_root_object.scs_props.active_scs_variant)

        # LIST BUTTONS
        col = row.column(align=True)
        col.operator('object.add_scs_variant', text="", icon='ZOOMIN')
        col.operator('object.remove_scs_variant', text="", icon='ZOOMOUT')

        # VARIANT-PART LIST
        if len(variant_inventory) > 0:

            if scene.scs_props.variant_views != 'integrated':

                box = box.box()
                split = box.split(percentage=0.5)
                split1 = split.row()

                split1.label("Variant-Part Table:", icon="MESH_GRID")
                split2 = split.row(align=True)
                split2.alignment = 'RIGHT'
                split2.prop(scene.scs_props, 'part_list_sorted', text='Parts', icon='SORTALPHA', expand=True, toggle=True)

                if scene.scs_props.variant_views in ('vertical', 'horizontal'):
                    split2.prop(scene.scs_props, 'variant_list_sorted', text='Variants', icon='SORTALPHA', expand=True, toggle=True)

            if scene.scs_props.variant_views == 'compact':

                # COMPACT LIST
                if variant_inventory:

                    row = box.row()
                    col = row.column(align=True)

                    active_scs_variant = scs_root_object.scs_props.active_scs_variant
                    _draw_part_list_for_variant(col, scene, variant_inventory[active_scs_variant])
            else:

                # VERTICAL LIST
                if scene.scs_props.variant_views == 'vertical':
                    if scene.scs_props.variant_list_sorted:
                        inventory_names = []
                        for variant in variant_inventory:
                            inventory_names.append(variant.name)
                        for name in sorted(inventory_names):
                            variant = variant_inventory[name]
                            _draw_vertical_variant_block(box, scene, variant)
                    else:
                        for variant in variant_inventory:
                            _draw_vertical_variant_block(box, scene, variant)

                # HORIZONTAL LIST
                elif scene.scs_props.variant_views == 'horizontal':
                    row = box.row()
                    if scene.scs_props.variant_list_sorted:
                        inventory_names = []
                        for variant in variant_inventory:
                            inventory_names.append(variant.name)
                        for name in sorted(inventory_names):
                            variant = variant_inventory[name]
                            _draw_horizontal_scs_variant_block(row, variant)
                    else:
                        for variant in variant_inventory:
                            _draw_horizontal_scs_variant_block(row, variant)

    else:

        # HEADER (COLLAPSIBLE - CLOSED)
        row = box.row()
        row.prop(scene.scs_props, 'scs_variant_panel_expand', text="SCS Variants:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.label('')


class SCSObjectPartSlots(bpy.types.UIList):
    """
    Draw part item slot within SCS Parts list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        # assert(isinstance(item, bpy.types.MaterialSlot)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                line = layout.split(percentage=0.6, align=False)
                line.prop(item, "name", text="", emboss=False, icon_value=icon)
                tools = line.row(align=True)
                tools.alignment = 'RIGHT'
                _draw_icon_part_tools(tools, index)
            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCSObjectVariantSlots(bpy.types.UIList):
    """
    Draw variant item slot within SCS Variants list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.MaterialSlot)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                if context.scene.scs_props.variant_views == 'integrated':
                    layout.prop(item, "name", text="", emboss=False, icon_value=icon)
                    line = layout.row(align=True)
                    for part in item.parts:
                        line.prop(part, 'include', text=part.name, toggle=True)
                else:
                    line = layout.split(percentage=0.6, align=False)
                    line.prop(item, "name", text="", emboss=False, icon_value=icon)
                    tools = line.row(align=True)
                    tools.alignment = 'RIGHT'
                    _draw_icon_variant_tools(tools, index)
            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCSObjectAnimationSlots(bpy.types.UIList):
    """
    Draw animation item slot within SCS Animation list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.MaterialSlot)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                if index == data.scs_props.active_scs_animation:
                    line = layout.split(percentage=0.4, align=False)
                else:
                    line = layout.row()
                line.prop(item, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCSTools(_ObjectPanelBlDefs, Panel):
    """
    Creates "SCS Object Specials" panel in the Object properties window.
    """
    bl_label = "SCS Object Specials"
    bl_idname = "OBJECT_PT_SCS_specials"
    bl_context = "object"

    def draw(self, context):
        """UI draw function.

        :param context: Blender Context
        :type context: bpy.context
        """
        layout = self.layout
        scene = context.scene
        obj = context.object
        # print('obj:   %s\t- %s' % (obj, context.object))

        # ##   SCS OBJECT SPECIALS PANEL   ################

        # TEST & DEBUG PANEL
        # draw_test_panel(layout)

        if obj.type in ('MESH', 'EMPTY'):

            scs_root_obj = _object_utils.get_scs_root(obj)

            active_obj_has_part = not (obj.scs_props.empty_object_type == "Locator" and
                                       obj.scs_props.locator_type == "Prefab" and
                                       obj.scs_props.locator_prefab_type != "Sign")
            if scs_root_obj and active_obj_has_part:

                # SCS PART
                _draw_scs_part_panel(layout, scene, obj, scs_root_obj)

            if obj == scs_root_obj:

                # SCS VARIANT PANEL
                _draw_scs_variant_panel(layout, scene, scs_root_obj)

        # EMPTY OBJECT PANEL
        if obj.type == 'EMPTY':
            _draw_empty_object_panel(layout, context, scene, obj)

        if obj.type == 'ARMATURE':

            # ANIMATION SETTINGS PANEL
            _draw_animation_settings_panel(layout)
