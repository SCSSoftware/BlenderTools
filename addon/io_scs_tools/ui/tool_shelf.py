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
from bpy.types import Panel
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.consts import LampTools as _LT_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.consts import VertexColorTools as _VCT_consts
from io_scs_tools.internals.icons import get_icon
from io_scs_tools.ui import shared as _shared
from io_scs_tools.utils import object as _object_utils

_ICON_TYPES = _ICONS_consts.Types


class _ToolShelfBlDefs(_shared.HeaderIconPanel):
    """
    Creating initial class with needed members to be registered in Blender 3D View Tool Shelf
    """
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SCS Tools"
    bl_label = "not set"

    layout = None  # predefined Blender variable to avoid warnings in PyCharm


class SCSToolShelfBlDefs(_ToolShelfBlDefs, Panel):
    """
    Creates a Tool Shelf panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Tool Shelf"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator('object.create_scs_root_object', text='Add Root', icon_value=get_icon(_ICON_TYPES.scs_root))
            row.operator('object.create_scs_root_object_dialog', text='', icon='OUTLINER_DATA_FONT')
            row = col.row(align=True)
            row.operator('object.scs_geometry_check', text="Check Geometry", icon="ZOOM_SELECTED")
            row = col.row(align=True)
            row.operator('mesh.scs_vcoloring_edit', text="VColoring", icon="GROUP_VCOL")
            row.operator('mesh.scs_vcoloring_rebake', text="", icon="FILE_REFRESH")


class SCSToolsConvexBlDefs(_ToolShelfBlDefs, Panel):
    """
    Creates a Convex panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Convex"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene:
            col = layout.column(align=True)
            col.operator('object.make_convex', text='Make Convex', icon_value=get_icon(_ICON_TYPES.loc_collider_convex))
            col.operator('object.convert_meshes_to_convex_locator', text='Convert to Locator', icon_value=get_icon(_ICON_TYPES.loc))
            col.operator('object.convert_convex_locator_to_mesh', text='Convert to Mesh', icon='OUTLINER_OB_MESH')
            # col.operator('object.update_convex', text='Update Convex')


'''
class SCSToolsPartsBlDefs(_ToolShelfBlDefs, Panel):
    # bl_space_type = 'IMAGE_EDITOR'
    bl_context = "objectmode"
    bl_label = "Parts"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # print('scene: %r\t- %r' % (scene.name, context.scene.name))
        # obj = context.object  # FIXME: Gives None type in this place - everywhere else it works normally (?!?)
        # print('obj:   %s\t- %s' % (obj, context.object))
        # blend_data = context.blend_data

        if scene:
            # PART PANEL
            # if obj: ## FIXME: None type obj - see above...
            #     ui.shared.draw_part_panel(layout, scene, obj)
            col = layout.column(align=True)
            col.operator('object.select_part', text='Select Active', icon='RESTRICT_SELECT_OFF')
            row = col.row(align=True)
            row.operator('object.view_part_only', text='View Active')
            row.operator('object.hide_part', text='Hide Active')
            row = col.row(align=True)
            row.operator('object.view_all_objects', text='View All')
            row.operator('object.invert_visibility', text='Invert')


class SCSToolsVariantsBlDefs(_ToolShelfBlDefs, Panel):
    bl_context = "objectmode"
    bl_label = "Variants"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # print('scene: %r\t- %r' % (scene.name, context.scene.name))
        # obj = context.object  # FIXME: Gives None type in this place - everywhere else it works normally (?!?)
        # print('obj:   %s\t- %s' % (obj, context.object))
        # blend_data = context.blend_data

        if scene:
            # VARIANT PANEL
            # if obj: ## FIXME: None type obj - see above...
            #     ui.shared.draw_part_panel(layout, scene, obj)

            col = layout.column(align=True)
            col.operator('object.select_variant', text='Select Active', icon='RESTRICT_SELECT_OFF')
            row = col.row(align=True)
            row.operator('object.view_variant_only', text='View Active')
            row.operator('object.hide_variant', text='Hide Active')
            row = col.row(align=True)
            row.operator('object.view_all_objects', text='View All')
            row.operator('object.invert_visibility', text='Invert')


class SCSToolsSelection(_ToolShelfBlDefs, Panel):
    bl_context = "objectmode"
    bl_label = "Selection Tools"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = context.scene

        if scene:
            box = layout.box()
            row0 = box.row()
            row0.label(text="Select by SCS Type:", icon='RESTRICT_SELECT_OFF')
            col = box.column(align=True)
            row1 = col.row(align=True)
            row1.alignment = 'CENTER'
            row1.operator('object.select_model_objects', text='', icon='OBJECT_DATA')
            row1.operator('object.select_shadow_casters', text='', icon='MAT_SPHERE_SKY')
            row1.operator('object.select_glass_objects', text='', icon='MOD_LATTICE')
            row1.operator('object.blank_operator', text='', icon='MOD_PHYSICS')  # TODO: Material Physics - has it sense?
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.select_all_locators', text='', icon='OUTLINER_OB_EMPTY')
            row2.operator('object.select_model_locators', text='', icon='MONKEY')
            row2.operator('object.select_prefab_locators', text='', icon='MOD_BUILD')
            row2.operator('object.select_collision_locators', text='', icon='PHYSICS')
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.select_prefab_nodes', text='', icon='FORCE_FORCE')
            row2.operator('object.select_prefab_signs', text='', icon='QUESTION')
            row2.operator('object.select_prefab_spawns', text='', icon='PARTICLE_DATA')
            row2.operator('object.select_prefab_traffics', text='', icon='PMARKER_ACT')
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.select_prefab_navigations', text='', icon='AUTO')
            row2.operator('object.select_prefab_maps', text='', icon='LAMP_SUN')
            row2.operator('object.select_prefab_triggers', text='', icon='FORCE_TURBULENCE')
            row2.operator('object.blank_operator', text='', icon='BLANK1')
'''


class SCSToolsVisibility(_ToolShelfBlDefs, Panel):
    """
    Creates a Visibility Tools panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Visibility Tools"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = context.scene

        if not scene:
            return

        scs_root_is_reachable = _object_utils.get_scs_root(context.active_object) is not None

        box = layout.box()

        row = box.row()
        row.prop(scene.scs_props, "visibility_tools_scope", expand=True)

        col = box.column(align=True)
        col.enabled = scs_root_is_reachable or scene.scs_props.visibility_tools_scope == "Global"
        row1 = col.row(align=True)
        row1.alignment = 'CENTER'
        props = row1.operator('object.switch_model_objects_visibility', text='', icon_value=get_icon(_ICON_TYPES.mesh))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.switch_shadow_casters_visibility', text='', icon_value=get_icon(_ICON_TYPES.mesh_shadow_caster))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.switch_glass_objects_visibility', text='', icon_value=get_icon(_ICON_TYPES.mesh_glass))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.switch_substance_objects_visibility', text='', icon_value=get_icon(_ICON_TYPES.mesh_with_physics))
        props.view_type = _OP_consts.ViewType.viewonly
        row2 = col.row(align=True)
        row2.alignment = 'CENTER'
        props = row2.operator('object.switch_all_locators_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_model_locators_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_model))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_locators_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_collision_locators_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_collider))
        props.view_type = _OP_consts.ViewType.viewonly

        col = box.column(align=True)
        col.enabled = scs_root_is_reachable or scene.scs_props.visibility_tools_scope == "Global"
        row2 = col.row(align=True)
        row2.alignment = 'CENTER'
        props = row2.operator('object.switch_prefab_nodes_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_node))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_signs_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_sign))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_spawns_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_spawn))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_traffics_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_semaphore))
        props.view_type = _OP_consts.ViewType.viewonly
        row2 = col.row(align=True)
        row2.alignment = 'CENTER'
        props = row2.operator('object.switch_prefab_navigations_visibility', text='',
                              icon_value=get_icon(_ICONS_consts.Types.loc_prefab_navigation))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_maps_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_map))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.switch_prefab_triggers_visibility', text='', icon_value=get_icon(_ICON_TYPES.loc_prefab_trigger))
        props.view_type = _OP_consts.ViewType.viewonly
        row2.operator('object.blank_operator', text='', icon='BLANK1')

        col = layout.column(align=True)
        col.enabled = scs_root_is_reachable or scene.scs_props.visibility_tools_scope == "Global"
        col.label("Current SCS Root:", icon_value=get_icon(_ICONS_consts.Types.scs_root))
        col.operator('object.invert_visibility_within_root', text='Invert Visibility')
        col.operator('object.view_all_objects_within_root', text='View All')
        col.operator('object.isolate_objects_within_root', text='Isolate')


class SCSDisplayMethods(_ToolShelfBlDefs, Panel):
    """
    Creates a Display Methods panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Display Methods"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = context.scene

        if not scene:
            return

        # GLASS OBJECTS
        col = layout.column(align=True)
        col.label(text='Glass Objects', icon_value=get_icon(_ICON_TYPES.mesh_glass))
        row = col.row(align=True)
        row.operator('object.glass_objects_in_wireframes', text='Wires')
        row.operator('object.glass_objects_textured', text='Textured')

        # SHADOW CASTERS
        col = layout.column(align=True)
        col.label(text='Shadow Casters', icon_value=get_icon(_ICON_TYPES.mesh_shadow_caster))
        row = col.row(align=True)
        row.operator('object.shadow_caster_objects_in_wireframes', text='Wires')
        row.operator('object.shadow_caster_objects_textured', text='Textured')

        # COLLISION LOCATORS
        col = layout.column(align=True)
        col.label(text='Collision Locators', icon_value=get_icon(_ICON_TYPES.loc_collider))
        row = col.row(align=True)
        row.operator('object.all_collision_locators_wires', text='All Wires')
        row.operator('object.no_collision_locators_wires', text='No Wires')
        row = col.row(align=True)
        row.operator('object.all_collision_locators_faces', text='All Faces')
        row.operator('object.no_collision_locators_faces', text='No Faces')


class SCSLampSwitcher(_ToolShelfBlDefs, Panel):
    """
    Creates Lamp Switcher panel for SCS Tools tab.
    """
    bl_label = "Lamp Switcher"

    @classmethod
    def poll(cls, context):
        return not context.vertex_paint_object

    def draw(self, context):
        layout = self.layout

        # vehicle switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Vehicle", icon="AUTO")

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Positional")
        props.lamp_type = _LT_consts.VehicleLampTypes.Positional.name
        props = body_row.operator("material.scs_switch_lampmask", text="DRL")
        props.lamp_type = _LT_consts.VehicleLampTypes.DRL.name

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Left Blinker")
        props.lamp_type = _LT_consts.VehicleLampTypes.LeftTurn.name
        props = body_row.operator("material.scs_switch_lampmask", text="Right Blinker")
        props.lamp_type = _LT_consts.VehicleLampTypes.RightTurn.name

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Low Beam")
        props.lamp_type = _LT_consts.VehicleLampTypes.LowBeam.name
        props = body_row.operator("material.scs_switch_lampmask", text="High Beam")
        props.lamp_type = _LT_consts.VehicleLampTypes.HighBeam.name

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Brake")
        props.lamp_type = _LT_consts.VehicleLampTypes.Brake.name
        props = body_row.operator("material.scs_switch_lampmask", text="Reverse")
        props.lamp_type = _LT_consts.VehicleLampTypes.Reverse.name

        # auxiliary switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Auxiliary", icon="LAMP_SPOT")

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Dim")
        props.lamp_type = _LT_consts.AuxiliaryLampTypes.Dim.name
        props = body_row.operator("material.scs_switch_lampmask", text="Bright")
        props.lamp_type = _LT_consts.AuxiliaryLampTypes.Bright.name

        # traffic light switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Traffic Lights", icon="COLOR_RED")

        body_row = body_col.row(align=True)
        props = body_row.operator("material.scs_switch_lampmask", text="Red")
        props.lamp_type = _LT_consts.TrafficLightTypes.Red.name
        props = body_row.operator("material.scs_switch_lampmask", text="Yellow")
        props.lamp_type = _LT_consts.TrafficLightTypes.Yellow.name
        props = body_row.operator("material.scs_switch_lampmask", text="Green")
        props.lamp_type = _LT_consts.TrafficLightTypes.Green.name


class SCSLampTool(_ToolShelfBlDefs, Panel):
    """
    Creates Lamp Switcher panel for SCS Tools tab.
    """
    bl_label = "Lamp UV Tool"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Vehicle", icon="AUTO")

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Front Left")
        props.vehicle_side = _LT_consts.VehicleSides.FrontLeft.name
        props.aux_color = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Front Right")
        props.vehicle_side = _LT_consts.VehicleSides.FrontRight.name
        props.aux_color = props.traffic_light_color = ""
        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Rear Left")
        props.vehicle_side = _LT_consts.VehicleSides.RearLeft.name
        props.aux_color = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Rear Right")
        props.vehicle_side = _LT_consts.VehicleSides.RearRight.name
        props.aux_color = props.traffic_light_color = ""
        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Middle")
        props.vehicle_side = _LT_consts.VehicleSides.Middle.name
        props.aux_color = props.traffic_light_color = ""

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Auxiliary", icon="LAMP_SPOT")

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="White")
        props.aux_color = _LT_consts.AuxiliaryLampColors.White.name
        props.vehicle_side = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Orange")
        props.aux_color = _LT_consts.AuxiliaryLampColors.Orange.name
        props.vehicle_side = props.traffic_light_color = ""

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label("Traffic Lights", icon="COLOR_RED")

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Red")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Red.name
        props.vehicle_side = props.aux_color = ""
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Yellow")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Yellow.name
        props.vehicle_side = props.aux_color = ""
        props = body_row.operator("mesh.scs_set_lampmask_uv", text="Green")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Green.name
        props.vehicle_side = props.aux_color = ""


class SCSVColoring(_ToolShelfBlDefs, Panel):
    bl_label = "VColoring"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object and bpy.ops.mesh.scs_vcoloring_edit.poll()

    def draw(self, context):
        layout = self.layout
        body_col = layout.column(align=True)
        active_vcol_name = context.vertex_paint_object.data.vertex_colors.active.name

        for layer_name in _VCT_consts.ColoringLayersTypes.as_list():

            if layer_name == _VCT_consts.ColoringLayersTypes.Color:
                text = "Edit Color"
            elif layer_name == _VCT_consts.ColoringLayersTypes.Decal:
                text = "Edit Decal"
            elif layer_name == _VCT_consts.ColoringLayersTypes.AO:
                text = "Edit AO"
            elif layer_name == _VCT_consts.ColoringLayersTypes.AO2:
                text = "Edit AO2"
            else:
                text = "Edit Undefined"

            body_row = body_col.row(align=True)
            icon = 'RADIOBUT_ON' if active_vcol_name == layer_name else 'RADIOBUT_OFF'
            props = body_row.operator("mesh.scs_vcoloring_edit", text=text, icon=icon)
            props.layer_name = layer_name

        body_row = layout.row()
        body_row.operator("mesh.scs_vcoloring_exit", text="Exit (ESC)", icon="QUIT")


class SCSVertexColorWrapTool(_ToolShelfBlDefs, Panel):
    bl_label = "Wrap Tool"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object

    def draw(self, context):
        layout = self.layout
        body_col = layout.column(align=True)

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_wrap_vcol", text="Wrap All")
        props.wrap_type = "all"

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_wrap_vcol", text="Wrap Selected")
        props.wrap_type = "selected"


class SCSVertexColorStatsTool(_ToolShelfBlDefs, Panel):
    bl_label = "Stats Tool"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object

    def draw(self, context):
        layout = self.layout

        body_row = layout.row(align=True)
        body_row.operator("mesh.scs_get_vcol_stats")
