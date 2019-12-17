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

# Copyright (C) 2013-2019: SCS Software

import os
import bpy
from bpy.types import Panel
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals.connections.wrappers import collection as _connections_wrapper
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories
from io_scs_tools.ui import shared as _shared


class _ObjectPanelBlDefs:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return hasattr(context, "active_object") and context.active_object

    def get_layout(self):
        """Returns layout depending where it's drawn into. If popover create extra box to make it distinguisable between different sub-panels."""
        if self.is_popover:
            layout = self.layout.box().column()
        else:
            layout = self.layout

        return layout


class SCS_TOOLS_UL_ObjectPartSlot(bpy.types.UIList):
    """Draw part item slot within SCS Parts list"""

    @staticmethod
    def draw_icon_part_tools(layout, index):
        """Draws Part Tools icons in a line.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param index: index of part in parts inventory
        :type index: int
        """
        props = layout.operator('object.scs_tools_de_select_objects_with_part', text="", emboss=False, icon='RESTRICT_SELECT_OFF')
        props.part_index = index
        props.select_type = _OP_consts.SelectionType.undecided
        props = layout.operator('object.scs_tools_switch_part_visibility', text="", emboss=False, icon='HIDE_OFF')
        props.part_index = index
        props.view_type = _OP_consts.ViewType.undecided

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                line = layout.split(factor=0.6, align=False)
                line.prop(item, "name", text="", emboss=False, icon_value=icon)
                tools = line.row(align=True)
                tools.alignment = 'RIGHT'
                self.draw_icon_part_tools(tools, index)
            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCS_TOOLS_UL_ObjectVariantSlot(bpy.types.UIList):
    """Draw variant item slot within SCS Variants list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                if context.workspace.scs_props.variant_views == 'integrated':
                    layout.prop(item, "name", text="", emboss=False, icon_value=icon)
                    line = layout.row(align=True)
                    for part in item.parts:
                        line.prop(part, 'include', text=part.name, toggle=True)
                else:
                    line = layout.split(factor=0.6, align=False)
                    line.prop(item, "name", text="", emboss=False, icon_value=icon)
                    tools = line.row(align=True)
                    tools.alignment = 'RIGHT'
                    SCS_TOOLS_PT_Variants.draw_icon_variant_tools(tools, index)
            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCS_TOOLS_UL_ObjectAnimationSlot(bpy.types.UIList):
    """Draw animation item slot within SCS Animation list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:

                row = layout.row(align=True)
                row.prop(item, "export", text="")

                row2 = row.row(align=True)
                row2.enabled = item.export
                row2.prop(item, "name", text="", emboss=False)

                extra_ops = row2.row(align=True)
                extra_ops.alignment = 'RIGHT'

                props = extra_ops.operator("scene.scs_tools_export_anim_action", text="", icon='EXPORT', emboss=True)
                props.index = index

            else:
                layout.label(text="", icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCS_TOOLS_PT_Object(_shared.HeaderIconPanel, _ObjectPanelBlDefs, Panel):
    """Creates "SCS Object" panel in the Object properties window."""

    bl_label = "SCS Object"
    bl_context = "object"

    @staticmethod
    def has_any_scs_subpanel(context):
        """Returns sum of poll methods of all panels that has this one as a parent."""

        return (SCS_TOOLS_PT_RootObject.poll(context) or
                SCS_TOOLS_PT_Locator.poll(context) or
                SCS_TOOLS_PT_Parts.poll(context) or
                SCS_TOOLS_PT_Variants.poll(context) or
                SCS_TOOLS_PT_LooksOnObject.poll(context) or
                SCS_TOOLS_PT_Animations.poll(context) or
                SCS_TOOLS_PT_Skeleton.poll(context))

    @staticmethod
    def draw_empty_object_panel(layout, obj, enabled=False):
        """Creates 'Empty Object' settings sub-panel.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param obj: Blender Empty Object
        :type obj: bpy.types.Object
        :param enabled: Should empty object type property be enabled?
        :type enabled: bool
        """
        row = layout.row()
        row.enabled = enabled
        row.use_property_split = True
        row.use_property_decorate = False
        row.prop(obj.scs_props, 'empty_object_type', text="Object Type")

    def draw(self, context):
        """UI draw function."""

        # draw minimalistict info, so user knows what's going on
        if not self.poll(context):
            self.layout.label(text="No active object!", icon="INFO")
            return

        obj = context.active_object

        if obj.type in 'MESH' and _object_utils.can_assign_terrain_points(context):
            other_obj = _object_utils.get_other_object(context.selected_objects, obj)
            self.draw_empty_object_panel(self.get_layout(), other_obj)
        elif obj.type == 'EMPTY':
            self.draw_empty_object_panel(self.get_layout(), obj, enabled=True)
        elif not self.has_any_scs_subpanel(context):
            self.layout.label(text="No SCS props for active object!", icon="INFO")


class SCS_TOOLS_PT_RootObject(_ObjectPanelBlDefs, Panel):
    """Creates 'SCS Root Object' settings sub-panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "Root Object"

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.scs_props.empty_object_type == 'SCS_Root'

    def draw(self, context):
        layout = self.get_layout()
        obj = context.active_object

        layout.use_property_split = True
        layout.use_property_decorate = False

        # export inclusion
        layout.prop(obj.scs_props, 'scs_root_object_export_enabled', text="Export Inclusion")

        # model type
        row = _shared.create_row(layout, use_split=False, enabled=obj.scs_props.scs_root_object_export_enabled)
        row.prop(obj.scs_props, 'scs_root_animated', expand=True, toggle=True)

        # custom export path
        col = layout.column(align=True)
        col.enabled = obj.scs_props.scs_root_object_export_enabled

        # Global Export Filepath (DIR_PATH - absolute)
        row = col.row(align=True)
        row.prop(obj.scs_props, 'scs_root_object_allow_custom_path', text="")
        row2 = row.row(align=True)
        row2.enabled = obj.scs_props.scs_root_object_allow_custom_path
        if row2.enabled:
            root_export_path = obj.scs_props.scs_root_object_export_filepath
            row2.alert = ((root_export_path != "" and not root_export_path.startswith("//")) or
                          not os.path.isdir(os.path.join(_get_scs_globals().scs_project_path,
                                                         obj.scs_props.scs_root_object_export_filepath.strip("//"))))

        row2.prop(obj.scs_props, 'scs_root_object_export_filepath', text="", icon='EXPORT')
        if row2.alert:
            _shared.draw_warning_operator(
                row2,
                "Custom Export Path Warning",
                str("Current custom SCS Game Object filepath is unreachable, which may result into an error on export!\n"
                    "Make sure you did following:\n"
                    "1. Properly set \"SCS Project Base Path\"\n"
                    "2. Properly set this custom export path which must be relative on \"SCS Project Base Path\"")
            )
        props = row2.operator('scene.scs_tools_select_dir_inside_base', text="", icon='FILEBROWSER')
        props.type = "GameObjectExportPath"


class SCS_TOOLS_PT_Locator(_ObjectPanelBlDefs, Panel):
    """Draw Locator Settings Panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "Locator Settings"

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.scs_props.empty_object_type == 'Locator' or _object_utils.can_assign_terrain_points(context)

    @staticmethod
    def draw_model_locator(layout, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        # locator name
        row = layout.row()
        row.prop(obj, 'name', text="Name")

        # locator hookup
        row = layout.row(align=True)
        _shared.compensate_aligning_bug(row, number_of_items=2)
        row.prop_search(obj.scs_props, 'locator_model_hookup', _get_scs_inventories(), 'hookups', text="Hookup")
        props = row.operator('scene.scs_tools_reload_library', icon='FILE_REFRESH', text="")
        props.library_path_attr = "hookup_library_rel_path"
        props = row.operator("object.scs_tools_select_model_locators_with_same_hookup", icon='ZOOM_SELECTED', text="")
        props.source_object = obj.name

    @staticmethod
    def draw_collision_locator(layout, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(obj.scs_props, 'locator_collider_type')

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(obj.scs_props, 'locator_collider_wires', text='Draw Wireframes')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_collider_faces', text='Draw Faces')
        if obj.scs_props.locator_collider_type != 'Convex':
            layout.prop(obj.scs_props, 'locator_collider_centered')

        layout.prop(obj.scs_props, 'locator_collider_mass')

        if obj.scs_props.locator_collider_type == 'Box':
            col = layout.column(align=True)
            col.prop(obj.scs_props, 'locator_collider_box_x')
            col.prop(obj.scs_props, 'locator_collider_box_y')
            col.prop(obj.scs_props, 'locator_collider_box_z')
        elif obj.scs_props.locator_collider_type == 'Sphere':
            layout.prop(obj.scs_props, 'locator_collider_dia', text='Sphere Diameter')
        elif obj.scs_props.locator_collider_type == 'Capsule':
            col = layout.column(align=True)
            col.prop(obj.scs_props, 'locator_collider_dia', text='Capsule Diameter')
            col.prop(obj.scs_props, 'locator_collider_len', text='Capsule Length')
        elif obj.scs_props.locator_collider_type == 'Cylinder':
            col = layout.column(align=True)
            col.prop(obj.scs_props, 'locator_collider_dia', text='Cylinder Diameter')
            col.prop(obj.scs_props, 'locator_collider_len', text='Cylinder Length')
        elif obj.scs_props.locator_collider_type == 'Convex':
            layout.prop(obj.scs_props, 'locator_collider_margin')
            layout.label(text="%i hull vertices." % obj.scs_props.locator_collider_vertices, icon='INFO')

    @staticmethod
    def draw_prefab_control_node(layout, context, obj, enabled=True):
        loc_set = _shared.create_row(layout, use_split=True, enabled=enabled)
        loc_set.prop(obj.scs_props, 'locator_prefab_con_node_index')

        loc_set_col = layout.column(align=True)
        loc_set = loc_set_col.row(align=True)

        if not _object_utils.can_assign_terrain_points(context):
            _shared.draw_warning_operator(
                loc_set,
                "Assigning Terrain Points",
                str("To be able to assign terrain points you have to:\n"
                    "1. Select 'Control Node' locator and mesh object from which vertices you want to use as terrain points\n"
                    "2. Make sure that mesh object was selected last\n"
                    "3. Switch to 'Edit Mode'"),
                icon='INFO'
            )

        loc_set.operator('object.scs_tools_assign_terrain_points')

        loc_set = loc_set_col.row(align=True)
        loc_set.operator('object.scs_tools_clear_terrain_points')

        loc_set = layout.row(align=True)
        loc_set.label(text="Preview Terrain Points:", icon='HIDE_OFF')
        loc_set = layout.row(align=True)
        props = loc_set.operator('object.scs_tools_preview_terrain_points', text="Visible")
        props.preview_all = False
        props = loc_set.operator('object.scs_tools_preview_terrain_points', text="All")
        props.preview_all = True
        loc_set.operator('object.scs_tools_abort_terrain_points_preview', text="Abort")

    @staticmethod
    def draw_prefab_sign(layout, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        _shared.compensate_aligning_bug(row, number_of_items=1)
        row.prop_search(obj.scs_props, 'locator_prefab_sign_model', _get_scs_inventories(), 'sign_models', text="Sign Model")
        props = row.operator('scene.scs_tools_reload_library', icon='FILE_REFRESH', text="")
        props.library_path_attr = "sign_library_rel_path"

    @staticmethod
    def draw_prefab_spawn_point(layout, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(obj.scs_props, 'locator_prefab_spawn_type')

    @staticmethod
    def draw_prefab_semaphore(layout, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        # id
        layout.prop(obj.scs_props, 'locator_prefab_tsem_id')

        # profile
        row = layout.row(align=True)
        _shared.compensate_aligning_bug(row, number_of_items=1)
        row.prop_search(obj.scs_props, 'locator_prefab_tsem_profile', _get_scs_inventories(), 'tsem_profiles')
        props = row.operator('scene.scs_tools_reload_library', icon='FILE_REFRESH', text="")
        props.library_path_attr = "tsem_library_rel_path"

        # type
        layout.prop(obj.scs_props, 'locator_prefab_tsem_type', text="Type")

        # interval distances and cycle delay
        loc_set_col = layout.column()
        loc_set_col.use_property_split = False
        loc_set_col.use_property_decorate = False
        if obj.scs_props.locator_prefab_tsem_type in ('0', '1'):
            loc_set_col.enabled = False
        else:
            loc_set_col.enabled = True
        loc_set = loc_set_col.row(align=True)
        loc_set.label(text="Intervals/Distances:")
        loc_set = loc_set_col.row(align=True)
        loc_set.prop(obj.scs_props, 'locator_prefab_tsem_gs')
        loc_set.prop(obj.scs_props, 'locator_prefab_tsem_os1')
        loc_set.prop(obj.scs_props, 'locator_prefab_tsem_rs')
        loc_set.prop(obj.scs_props, 'locator_prefab_tsem_os2')

        loc_set = loc_set_col.row()
        loc_set.prop(obj.scs_props, 'locator_prefab_tsem_cyc_delay')

    @staticmethod
    def draw_prefab_navigation_point(layout, context, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_np_low_probab')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_np_add_priority')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_np_limit_displace')

        # allowed vehicles
        layout.prop(obj.scs_props, 'locator_prefab_np_allowed_veh')

        # blinker
        col = layout.column(align=True)
        col.prop(obj.scs_props, 'locator_prefab_np_blinker', expand=True)

        # priority modifier
        layout.prop(obj.scs_props, 'locator_prefab_np_priority_modifier')

        # traffic semaphore
        layout.prop(obj.scs_props, 'locator_prefab_np_traffic_semaphore')

        # traffic rule
        row = layout.row(align=True)
        _shared.compensate_aligning_bug(row, number_of_items=1)
        row.prop_search(obj.scs_props, 'locator_prefab_np_traffic_rule', _get_scs_inventories(), 'traffic_rules')
        props = row.operator('scene.scs_tools_reload_library', icon='FILE_REFRESH', text="")
        props.library_path_attr = "traffic_rules_library_rel_path"

        # boundary
        layout.prop(obj.scs_props, 'locator_prefab_np_boundary')

        # boundary node
        layout.prop(obj.scs_props, 'locator_prefab_np_boundary_node')

        loc_set = layout.row()
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
                if _connections_wrapper.has_connection(loc0_obj, loc1_obj):
                    loc_set.operator('object.scs_tools_disconnect_prefab_locators', text="Disconnect Navigation Points", icon='UNLINKED')
                else:
                    loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect Navigation Points", icon='LINKED')
            else:
                loc_set.enabled = False
                loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect / Disconnect Navigation Points", icon='LINKED')
        else:
            loc_set.enabled = False
            loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect / Disconnect Navigation Points", icon='LINKED')

    @staticmethod
    def draw_prefab_map_point(layout, context, obj):
        # box_row_box = layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        is_polygon = int(obj.scs_props.locator_prefab_mp_road_size) == _PL_consts.MPVF.ROAD_SIZE_MANUAL

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_mp_road_over')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_mp_no_outline')
        col = flow.column()
        col.enabled = not is_polygon
        col.prop(obj.scs_props, 'locator_prefab_mp_no_arrow')
        col = flow.column()
        col.enabled = not is_polygon
        col.prop(obj.scs_props, 'locator_prefab_mp_prefab_exit')

        layout.prop(obj.scs_props, 'locator_prefab_mp_road_size')
        row = _shared.create_row(layout, use_split=True, enabled=not is_polygon)
        row.prop(obj.scs_props, 'locator_prefab_mp_road_offset')
        row = _shared.create_row(layout, use_split=True, enabled=is_polygon)
        row.prop(obj.scs_props, 'locator_prefab_mp_custom_color')
        row = _shared.create_row(layout, use_split=True, enabled=not is_polygon)
        row.prop(obj.scs_props, 'locator_prefab_mp_assigned_node')
        row = _shared.create_row(layout, use_split=True, enabled=not is_polygon and obj.scs_props.locator_prefab_mp_assigned_node == "0")
        row.prop_menu_enum(obj.scs_props, 'locator_prefab_mp_dest_nodes')

        loc_set = layout.row()
        if len(context.selected_objects) == 2:

            # check if both selected objects are navigation points and set not active object
            is_mp = 0
            for obj_locator in context.selected_objects:
                if obj_locator.scs_props.locator_type == 'Prefab' and obj_locator.scs_props.locator_prefab_type == 'Map Point':
                    is_mp += 1
            if is_mp == 2:
                if _connections_wrapper.has_connection(context.selected_objects[0], context.selected_objects[1]):
                    loc_set.operator('object.scs_tools_disconnect_prefab_locators', text="Disconnect Map Points", icon='UNLINKED')
                else:
                    loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect Map Points", icon='LINKED')
            else:
                loc_set.enabled = False
                loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect / Disconnect Map Points", icon='LINKED')
        else:
            loc_set.enabled = False
            loc_set.operator('object.scs_tools_connect_prefab_locators', text="Connect / Disconnect Map Points", icon='LINKED')

    @staticmethod
    def draw_prefab_trigger_point(layout, context, obj):
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        _shared.compensate_aligning_bug(row, number_of_items=1)
        row.prop_search(obj.scs_props, 'locator_prefab_tp_action', _get_scs_inventories(), 'trigger_actions')
        props = row.operator('scene.scs_tools_reload_library', icon='FILE_REFRESH', text="")
        props.library_path_attr = "trigger_actions_rel_path"

        layout.prop(obj.scs_props, 'locator_prefab_tp_range')
        layout.prop(obj.scs_props, 'locator_prefab_tp_reset_delay')

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_tp_sphere_trigger')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_tp_partial_activ')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_tp_onetime_activ')
        col = flow.column()
        col.prop(obj.scs_props, 'locator_prefab_tp_manual_activ')

        loc_set = layout.row()
        if len(context.selected_objects) == 2:

            # check if both selected objects are trigger points and set not active object
            is_tp = 0
            for obj_locator in context.selected_objects:
                if obj_locator.scs_props.locator_type == 'Prefab' and obj_locator.scs_props.locator_prefab_type == 'Trigger Point':
                    is_tp += 1
            if is_tp == 2:
                if _connections_wrapper.has_connection(context.selected_objects[0], context.selected_objects[1]):
                    loc_set.operator('object.scs_tools_disconnect_prefab_locators', text='Disconnect Trigger Points', icon='UNLINKED')
                else:
                    loc_set.operator('object.scs_tools_connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')
            else:
                loc_set.enabled = False
                loc_set.operator('object.scs_tools_connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')
        else:
            loc_set.enabled = False
            loc_set.operator('object.scs_tools_connect_prefab_locators', text='Connect Trigger Points', icon='LINKED')

    def draw(self, context):
        layout = self.get_layout()
        obj = context.active_object
        can_select_loc_type = True

        if _object_utils.can_assign_terrain_points(context):
            # if user can assign terrain points, then other object is locator
            obj = _object_utils.get_other_object(context.selected_objects, obj)
            can_select_loc_type = False

        row = _shared.create_row(layout, use_split=True, enabled=can_select_loc_type)
        row.prop(obj.scs_props, 'locator_type')

        # MODEL LOCATORS
        if obj.scs_props.locator_type == 'Model':
            self.draw_model_locator(layout, obj)

        # COLLISION LOCATORS
        elif obj.scs_props.locator_type == 'Collision':
            self.draw_collision_locator(layout, obj)

        # PREFAB LOCATORS
        elif obj.scs_props.locator_type == 'Prefab':
            box_row = _shared.create_row(layout, use_split=True, enabled=can_select_loc_type)
            box_row.prop(obj.scs_props, 'locator_prefab_type')

            if obj.scs_props.locator_prefab_type == 'Control Node':
                self.draw_prefab_control_node(layout, context, obj, enabled=can_select_loc_type)
            elif obj.scs_props.locator_prefab_type == 'Sign':
                self.draw_prefab_sign(layout, obj)
            elif obj.scs_props.locator_prefab_type == 'Spawn Point':
                self.draw_prefab_spawn_point(layout, obj)
            elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
                self.draw_prefab_semaphore(layout, obj)
            elif obj.scs_props.locator_prefab_type == 'Navigation Point':
                self.draw_prefab_navigation_point(layout, context, obj)
            elif obj.scs_props.locator_prefab_type == 'Map Point':
                self.draw_prefab_map_point(layout, context, obj)
            elif obj.scs_props.locator_prefab_type == 'Trigger Point':
                self.draw_prefab_trigger_point(layout, context, obj)


class SCS_TOOLS_PT_PreviewModel(_ObjectPanelBlDefs, Panel):
    """Draw Locator Preview panel."""

    bl_parent_id = SCS_TOOLS_PT_Locator.__name__
    bl_label = "Preview Model"

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.scs_props.empty_object_type == 'Locator' and context.active_object.scs_props.locator_type in ('Prefab', 'Model')

    def draw_header(self, context):
        layout = self.layout
        obj = context.active_object
        layout.prop(obj.scs_props, 'locator_show_preview_model', text="")

    def draw(self, context):
        layout = self.get_layout()
        obj = context.active_object

        layout.enabled = obj.scs_props.locator_show_preview_model
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Locator Preview Model Directory (FILE_PATH - relative)
        row = layout.row(align=True)

        # validity check for preview model path
        row.alert = True
        if obj.scs_props.locator_preview_model_path == "":
            row.alert = False
        elif os.path.isdir(_get_scs_globals().scs_project_path):
            if os.path.isfile(_get_scs_globals().scs_project_path + os.sep + obj.scs_props.locator_preview_model_path):
                if obj.scs_props.locator_preview_model_path.endswith(".pim"):
                    row.alert = False

        row.prop(obj.scs_props, 'locator_preview_model_path', text="Path")
        row.operator('object.scs_tools_select_preview_model_path', text="", icon='FILEBROWSER')

        # Locator Preview Model Controls
        layout.prop(obj.scs_props, 'locator_preview_model_type', )


class SCS_TOOLS_PT_Parts(_ObjectPanelBlDefs, Panel):
    """Creates 'SCS Parts' settings sub-panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "SCS Parts"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        obj = context.active_object

        if obj.type in ('MESH', 'EMPTY'):

            cls.scs_root = _object_utils.get_scs_root(obj)
            active_obj_has_part = not (obj.scs_props.empty_object_type == "Locator" and
                                       obj.scs_props.locator_type == "Prefab" and
                                       obj.scs_props.locator_prefab_type != "Sign")
            return cls.scs_root and active_obj_has_part

        return False

    @staticmethod
    def draw_part_list(layout, root_obj):
        """Creates an editable Part list.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param root_obj: SCS Root Object
        :type root_obj: bpy.types.Object
        """
        row = layout.row()
        row.template_list(
            SCS_TOOLS_UL_ObjectPartSlot.__name__,
            list_id="",
            dataptr=root_obj,
            propname="scs_object_part_inventory",
            active_dataptr=root_obj.scs_props,
            active_propname="active_scs_part",
            rows=4,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )

        # LIST BUTTONS
        col = row.column(align=True)
        col.operator('object.scs_tools_add_part', text="", icon='ADD')
        col.operator('object.scs_tools_remove_active_part', text="", icon='REMOVE')
        col.operator('object.scs_tools_clean_unused_parts', text="", icon='FILE_REFRESH')
        col.operator('object.scs_tools_move_active_part', text="", icon='TRIA_UP').move_direction = _OP_consts.InventoryMoveType.move_up
        col.operator('object.scs_tools_move_active_part', text="", icon='TRIA_DOWN').move_direction = _OP_consts.InventoryMoveType.move_down

    def draw(self, context):
        layout = self.get_layout()
        scs_root_object = self.scs_root
        active_object = context.active_object

        if len(_object_utils.gather_scs_roots(bpy.context.selected_objects)) > 1 and active_object is not scs_root_object:

            warning_box = layout.column(align=True)

            header = warning_box.box()
            header.label(text="WARNING", icon='ERROR')
            body = warning_box.box()
            col = body.column(align=True)
            col.label(text="Can not edit parts!")
            col.label(text="Selection has multiple game objects.")

        else:  # more roots or active object is root object

            # DEBUG
            if int(_get_scs_globals().dump_level) > 2 and not active_object is scs_root_object:

                row = layout.row(align=True)
                row.enabled = False
                row.label(text="DEBUG - active obj part:")
                row.prop(active_object.scs_props, 'scs_part', text="")

            # PART LIST
            self.draw_part_list(layout, scs_root_object)

            # ASSIGNEMENT CONTROLS
            if active_object is not scs_root_object:

                row = layout.row(align=True)
                row.operator("object.scs_tools_assign_part", text="Assign")
                props = row.operator("object.scs_tools_de_select_objects_with_part", text="Select")
                props.part_index = scs_root_object.scs_props.active_scs_part
                props.select_type = _OP_consts.SelectionType.shift_select
                props = row.operator("object.scs_tools_de_select_objects_with_part", text="Deselect")
                props.part_index = scs_root_object.scs_props.active_scs_part
                props.select_type = _OP_consts.SelectionType.ctrl_select


class SCS_TOOLS_PT_Variants(_ObjectPanelBlDefs, Panel):
    """Creates 'SCS Variants' settings sub-panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "SCS Variants"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.scs_props.empty_object_type == 'SCS_Root'

    @staticmethod
    def draw_icon_variant_tools(layout, index):
        """Draws Variant Tools icons in a line.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param index: index of variant in variants inventory
        :type index: int
        """
        props = layout.operator('object.scs_tools_de_select_objects_with_variant', text="", emboss=False, icon='RESTRICT_SELECT_OFF')
        props.variant_index = index
        props.select_type = _OP_consts.SelectionType.undecided
        props = layout.operator('object.scs_tools_switch_objects_with_variant', text="", emboss=False, icon='HIDE_OFF')
        props.variant_index = index
        props.view_type = _OP_consts.ViewType.undecided

    @staticmethod
    def draw_icon_variant_tools_line(layout, index):
        """Creates a line with minimalistic Variant Tools.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param index: index of active variant
        :type index: int
        """
        row = layout.row(align=True)
        col = row.column()
        col.alignment = 'LEFT'
        col.label(text="Additional Variant Tools:")
        col = row.column()
        col_row = col.row(align=True)
        col_row.alignment = 'RIGHT'
        SCS_TOOLS_PT_Variants.draw_icon_variant_tools(col_row, index)

    @staticmethod
    def draw_part_list_for_variant(layout, workspace, variant):
        """Creates 'SCS Part' items for provided 'SCS Variant'.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param workspace: Blender WorkSpace
        :type workspace: bpy.types.WorkSpace
        :param variant: Variant from the SCS Root Object
        :type variant: io_scs_tools.properties.object.ObjectVariantInventoryItem
        """
        if workspace.scs_props.part_list_sorted:
            inventory_names = []
            for part in variant.parts:
                inventory_names.append(part.name)
            for name in sorted(inventory_names):
                part = variant.parts[name]
                layout.prop(part, 'include', text=part.name, toggle=True)
        else:
            for part in variant.parts:
                layout.prop(part, 'include', text=part.name, toggle=True)

    @staticmethod
    def draw_vertical_variant_block(layout, workspace, variant):
        """Creates vertical 'SCS Variant' list.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param workspace: Blender WorkSpace
        :type workspace: bpy.types.WorkSpace
        :param variant: Variant from the SCS Root Object
        :type variant: io_scs_tools.properties.object.ObjectVariantInventoryItem
        """
        layout_column = layout.column(align=True)
        header = layout_column.box()
        row = header.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=variant.name)

        body = layout_column.box()
        col = body.column(align=True)
        SCS_TOOLS_PT_Variants.draw_part_list_for_variant(col, workspace, variant)

    @staticmethod
    def draw_horizontal_scs_variant_block(layout, workspace, variant):
        """Creates horizontal 'SCS Variant' list.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param workspace: Blender WorkSpace
        :type workspace: bpy.types.WorkSpace
        :param variant: Variant from the SCS Root Object
        :type variant: io_scs_tools.properties.object.ObjectVariantInventoryItem
        """
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=variant.name)

        box = layout.box()
        col = box.column(align=True)
        SCS_TOOLS_PT_Variants.draw_part_list_for_variant(col, workspace, variant)

    def draw_header_preset(self, context):
        layout = self.layout
        workspace = context.workspace
        layout.prop(workspace.scs_props, 'variant_views', text="", expand=True, toggle=True, emboss=True)

    def draw(self, context):
        layout = self.get_layout()
        workspace = context.workspace
        scs_root = context.active_object

        variant_inventory = scs_root.scs_object_variant_inventory

        # VARIANT LIST
        row = layout.row()
        col = row.column()
        col.template_list(
            SCS_TOOLS_UL_ObjectVariantSlot.__name__,
            list_id="",
            dataptr=scs_root,
            propname="scs_object_variant_inventory",
            active_dataptr=scs_root.scs_props,
            active_propname="active_scs_variant",
            rows=3,
            maxrows=6,
            type='DEFAULT',
            columns=9
        )

        if workspace.scs_props.variant_views == 'integrated':

            # VARIANT TOOLS FOR INTEGRATED LIST
            self.draw_icon_variant_tools_line(col, scs_root.scs_props.active_scs_variant)

        # LIST BUTTONS
        col = row.column(align=True)
        col.operator('object.scs_tools_add_variant', text="", icon='ADD')
        col.operator('object.scs_tools_remove_active_variant', text="", icon='REMOVE')
        col.operator('object.scs_tools_move_active_variant', text="", icon='TRIA_UP').move_direction = _OP_consts.InventoryMoveType.move_up
        col.operator('object.scs_tools_move_active_variant', text="", icon='TRIA_DOWN').move_direction = _OP_consts.InventoryMoveType.move_down

        # VARIANT-PART LIST
        if len(variant_inventory) > 0:

            # VARIANT-PART LIST HEADER
            if workspace.scs_props.variant_views != 'integrated':

                col = layout.column()
                split = col.split(factor=0.5)
                split1 = split.row()

                split1.label(text="Variant-Part Table:", icon='MESH_GRID')
                split2 = split.row(align=True)
                split2.alignment = 'RIGHT'
                split2.prop(workspace.scs_props, 'part_list_sorted', text='Parts', icon='SORTALPHA', expand=True, toggle=True)

                if workspace.scs_props.variant_views in ('vertical', 'horizontal'):
                    split2.prop(workspace.scs_props, 'variant_list_sorted', text='Variants', icon='SORTALPHA', expand=True, toggle=True)

            if workspace.scs_props.variant_views == 'compact':

                # COMPACT LIST
                row = layout.row()
                col = row.column(align=True)

                active_scs_variant = scs_root.scs_props.active_scs_variant
                self.draw_part_list_for_variant(col, workspace, variant_inventory[active_scs_variant])

            elif workspace.scs_props.variant_views == 'vertical':

                # VERTICAL LIST
                col = layout.column(align=False)
                if workspace.scs_props.variant_list_sorted:
                    inventory_names = []
                    for variant in variant_inventory:
                        inventory_names.append(variant.name)
                    for name in sorted(inventory_names):
                        variant = variant_inventory[name]
                        self.draw_vertical_variant_block(col, workspace, variant)
                else:
                    for variant in variant_inventory:
                        self.draw_vertical_variant_block(col, workspace, variant)

            elif workspace.scs_props.variant_views == 'horizontal':

                # HORIZONTAL LIST
                row = layout.row(align=True)
                if workspace.scs_props.variant_list_sorted:
                    inventory_names = []
                    for variant in variant_inventory:
                        inventory_names.append(variant.name)
                    for name in sorted(inventory_names):
                        variant = variant_inventory[name]
                        self.draw_horizontal_scs_variant_block(row.column(align=True), workspace, variant)
                else:
                    for variant in variant_inventory:
                        self.draw_horizontal_scs_variant_block(row.column(align=True), workspace, variant)


class SCS_TOOLS_PT_LooksOnObject(_ObjectPanelBlDefs, Panel):
    """Draws SCS Looks panel on object tab."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "SCS Looks"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.scs_props.empty_object_type == 'SCS_Root'

    def draw(self, context):
        layout = self.get_layout()
        obj = context.active_object

        _shared.draw_scs_looks_panel(layout, obj, obj, without_box=True)


class SCS_TOOLS_PT_Animations(_ObjectPanelBlDefs, Panel):
    """Draw Animation settings panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "SCS Animations"

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        cls.scs_root = _object_utils.get_scs_root(context.active_object)
        return context.active_object.type == 'ARMATURE'

    def draw_animation_section(self, layout, active_obj):
        """Draw Animation section.

        :param layout: Blender UI Layout to draw to
        :type layout: bpy.types.UILayout
        :param active_obj: operator context
        :type active_obj: bpy.types.Object
        """
        scs_object_animation_inventory = self.scs_root.scs_object_animation_inventory
        active_scs_anim_i = self.scs_root.scs_props.active_scs_animation
        if len(scs_object_animation_inventory) > active_scs_anim_i:

            layout.label(text="Active Animation Settings:", icon='ANIM_DATA')

            active_scs_anim = scs_object_animation_inventory[active_scs_anim_i]

            action_col = layout.column(align=True)

            row = action_col.row(align=True)
            icon = 'NONE' if active_scs_anim.action in bpy.data.actions else 'ERROR'
            row.prop_search(active_scs_anim, 'action', bpy.data, 'actions', text="", icon=icon)

            row = action_col.row(align=True)
            row.enabled = active_scs_anim.action in bpy.data.actions
            row.prop(active_scs_anim, 'anim_start', text="Start")
            row.prop(active_scs_anim, 'anim_end', text="End")
            row.prop(active_scs_anim, 'length', text="Length")

            if active_obj.animation_data and active_obj.animation_data.action:
                row = action_col.row(align=True)
                row.operator('scene.scs_tools_increase_animation_steps', text="", icon='ADD')
                row.operator('scene.scs_tools_decrease_animation_steps', text="", icon='REMOVE')
                row.prop(active_obj.animation_data.action.scs_props, "anim_export_step")

    def draw(self, context):
        layout_column = self.layout
        scs_root = self.scs_root

        # layout_column = layout.column(align=True)

        if scs_root:

            # ANIMATIONS CUSTOM EXPORT PATH
            column = layout_column.column(align=True)
            if self.scs_root.scs_props.scs_root_object_allow_anim_custom_path:
                text = "Custom Export Path Enabled"
            else:
                text = "Custom Export Path Disabled"
            icon = _shared.get_on_off_icon(self.scs_root.scs_props.scs_root_object_allow_anim_custom_path)

            column.prop(scs_root.scs_props, 'scs_root_object_allow_anim_custom_path', text=text, icon=icon, toggle=True)
            row2 = column.row(align=True)
            row2.enabled = scs_root.scs_props.scs_root_object_allow_anim_custom_path
            if row2.enabled:
                root_anim_export_path = scs_root.scs_props.scs_root_object_anim_export_filepath
                row2.alert = ((root_anim_export_path != "" and not root_anim_export_path.startswith("//")) or
                              not os.path.isdir(os.path.join(_get_scs_globals().scs_project_path,
                                                             scs_root.scs_props.scs_root_object_anim_export_filepath.strip("//"))))
            row2.prop(scs_root.scs_props, 'scs_root_object_anim_export_filepath', text="", icon='EXPORT')

            if row2.alert:
                _shared.draw_warning_operator(
                    row2,
                    "Custom Export Path Warning",
                    str("Current custom Animations filepath is unreachable, which may result into an error on export!\n"
                        "Make sure you did following:\n"
                        "1. Properly set \"SCS Project Base Path\"\n"
                        "2. Properly set this custom export path which must be relative on \"SCS Project Base Path\"")
                )

            props = row2.operator('scene.scs_tools_select_dir_inside_base', text="", icon='FILEBROWSER')
            props.type = "GameObjectAnimExportPath"

            # ANIMATION LIST
            layout_setting = layout_column.row()
            layout_setting.template_list(
                SCS_TOOLS_UL_ObjectAnimationSlot.__name__,
                list_id="",
                dataptr=scs_root,
                propname="scs_object_animation_inventory",
                active_dataptr=scs_root.scs_props,
                active_propname="active_scs_animation",
                rows=4,
                maxrows=10,
                type='DEFAULT',
                columns=9,
            )

            # LIST BUTTONS
            list_buttons = layout_setting.column(align=True)
            list_buttons.operator('object.scs_tools_add_animation', text="", icon='ADD')
            list_buttons.operator('object.scs_tools_remove_animation', text="", icon='REMOVE')
            list_buttons.separator()
            list_buttons.operator('scene.scs_tools_import_anim_actions', text="", icon='IMPORT')

            # ANIMATION SETTINGS
            if len(scs_root.scs_object_animation_inventory) > 0:
                self.draw_animation_section(layout_column, context.active_object)
            else:
                layout_column.label(text="No Animation!", icon='INFO')
        else:
            layout_column.label(text="No 'SCS Root Object'!", icon='INFO')


class SCS_TOOLS_PT_AnimPlayer(_ObjectPanelBlDefs, Panel):
    """Draws Animation Player panel."""

    bl_parent_id = SCS_TOOLS_PT_Animations.__name__
    bl_label = "Animation Player"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.get_layout()
        context = bpy.context
        scene = context.scene
        screen = context.screen

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
        # layout_row.prop(scene, "frame_current", text="")

        layout_box_row = layout.row()
        layout_col = layout_box_row.column(align=True)
        layout_col.prop(scene, "frame_preview_start", text="Start")
        layout_col.prop(scene, "frame_preview_end", text="End")
        layout_col = layout_box_row.column(align=True)
        layout_col.prop(scene, "frame_current", text='Current')
        layout_col.prop(scene.render, "fps")

        layout_box_row = layout.row()
        layout_box_row.prop(scene, "use_preview_range", text="", toggle=True)
        layout_row = layout_box_row.row(align=True)
        layout_row.scale_x = 1.3
        layout_row.operator("screen.frame_jump", text="", icon='REW').end = False
        layout_row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
        sub = layout_row.row(align=True)
        sub.scale_x = 10
        if not screen.is_animation_playing:
            if scene.sync_mode == 'AUDIO_SYNC' and context.user_preferences.system.audio_device == 'JACK':
                sub.operator("screen.animation_play", text="", icon='PLAY')
            else:
                sub.operator("screen.animation_play", text="", icon='PLAY_REVERSE').reverse = True
                sub.operator("screen.animation_play", text="", icon='PLAY')
        else:
            sub.operator("screen.animation_play", text="", icon='PAUSE')
        layout_row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
        layout_row.operator("screen.frame_jump", text="", icon='FF').end = True


class SCS_TOOLS_PT_Skeleton(_ObjectPanelBlDefs, Panel):
    """Draws skeleton properties panel."""

    bl_parent_id = SCS_TOOLS_PT_Object.__name__
    bl_label = "SCS Skeleton"

    @classmethod
    def poll(cls, context):
        if not _ObjectPanelBlDefs.poll(context):
            return False

        return context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.get_layout()
        active_object = bpy.context.active_object

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        skeleton_export_path = active_object.scs_props.scs_skeleton_custom_export_dirpath
        row.alert = ((skeleton_export_path != "" and not skeleton_export_path.startswith("//")) or
                     not os.path.isdir(os.path.join(_get_scs_globals().scs_project_path,
                                                    skeleton_export_path.strip("//"))))
        row.prop(active_object.scs_props, "scs_skeleton_custom_export_dirpath", text="Custom Path", icon='EXPORT')
        if row.alert:
            _shared.draw_warning_operator(
                row,
                "Skeleton Relative Export Path Warning",
                str("Current relative export path is unreachable, which may result into an error on export!\n"
                    "Make sure you did following:\n"
                    "1. Properly set \"SCS Project Base Path\"\n"
                    "2. Properly set this relative export path for skeleton which must be relative on \"SCS Project Base Path\"")
            )
        props = row.operator('scene.scs_tools_select_dir_inside_base', text="", icon='FILEBROWSER')
        props.type = "SkeletonExportPath"

        layout.prop(active_object.scs_props, "scs_skeleton_custom_name", text="Custom Name", icon='FILE_TEXT')


classes = (
    SCS_TOOLS_UL_ObjectPartSlot,
    SCS_TOOLS_UL_ObjectVariantSlot,
    SCS_TOOLS_UL_ObjectAnimationSlot,
    SCS_TOOLS_PT_Object,
    SCS_TOOLS_PT_RootObject,
    SCS_TOOLS_PT_Locator,
    SCS_TOOLS_PT_PreviewModel,
    SCS_TOOLS_PT_Parts,
    SCS_TOOLS_PT_Variants,
    SCS_TOOLS_PT_LooksOnObject,
    SCS_TOOLS_PT_Animations,
    SCS_TOOLS_PT_AnimPlayer,
    SCS_TOOLS_PT_Skeleton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_props_entry("Object Properties", SCS_TOOLS_PT_Object.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
