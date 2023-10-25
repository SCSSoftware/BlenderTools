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
    bl_region_type = "UI"
    bl_category = "SCS Tools"
    bl_label = "not set"

    layout = None  # predefined Blender variable to avoid warnings in PyCharm


class SCS_TOOLS_PT_ToolShelf(_ToolShelfBlDefs, Panel):
    """
    Creates a Tool Shelf panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Tool Shelf"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Not in 'Object Mode'!", icon="INFO")
            return

        layout = self.layout
        scene = context.scene

        if scene:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator('object.scs_tools_create_scs_root', text='Add Root', icon_value=get_icon(_ICON_TYPES.scs_root))
            row.operator('object.scs_tools_create_scs_root', text="", icon='SYNTAX_OFF').use_dialog = True
            row = col.row(align=True)
            row.operator('object.scs_tools_relocate_scs_roots', icon="CON_LOCLIKE")

            col.separator(factor=0.5)

            row = col.row(align=True)
            row.operator('object.scs_tools_search_degenerated_polys', text="Check Geometry", icon='ZOOM_SELECTED')
            row = col.row(align=True)
            row.operator('mesh.scs_tools_start_vcoloring', text="VColoring", icon='GROUP_VCOL')
            row.operator('mesh.scs_tools_rebake_vcoloring', text="", icon='FILE_REFRESH')


class SCS_TOOLS_PT_ConvexBlDefs(_ToolShelfBlDefs, Panel):
    """
    Creates a Convex panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Convex"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):

        if not self.poll(context):
            self.layout.label(text="Not in 'Object Mode'!", icon="INFO")
            return

        layout = self.layout
        scene = context.scene

        if scene:
            col = layout.column(align=True)
            col.operator('object.scs_tools_make_convex_mesh', text='Make Convex', icon_value=get_icon(_ICON_TYPES.loc_collider_convex))
            row = col.row(align=True)
            row.operator('object.scs_tools_convert_meshes_to_convex_locator', text='Convert to Locator', icon_value=get_icon(_ICON_TYPES.loc))
            row.operator('object.scs_tools_convert_meshes_to_convex_locator', text='', icon='MODIFIER').show_face_count_only = True
            col.operator('object.scs_tools_convert_convex_locator_to_mesh', text='Convert to Mesh', icon='MESH_DATA')


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
            row1.operator('object.scs_tools_select_model_objects', text="", icon='OBJECT_DATA')
            row1.operator('object.scs_tools_select_shadow_casters', text="", icon='MAT_SPHERE_SKY')
            row1.operator('object.scs_tools_select_glass_objects', text="", icon='MOD_LATTICE')
            row1.operator('object.scs_tools_blank_operator', text="", icon='MOD_PHYSICS')  # TODO: Material Physics - has it sense?
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.scs_tools_select_all_locators', text="", icon='OUTLINER_OB_EMPTY')
            row2.operator('object.scs_tools_select_model_locators', text="", icon='MONKEY')
            row2.operator('object.scs_tools_select_prefab_locators', text="", icon='MOD_BUILD')
            row2.operator('object.scs_tools_select_collision_locators', text="", icon='PHYSICS')
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.scs_tools_select_prefab_node_locators', text="", icon='FORCE_FORCE')
            row2.operator('object.scs_tools_select_prefab_sign_locators', text="", icon='QUESTION')
            row2.operator('object.scs_tools_select_prefab_spawn_locators', text="", icon='PARTICLE_DATA')
            row2.operator('object.scs_tools_select_prefab_traffic_locators', text="", icon='PMARKER_ACT')
            row2 = col.row(align=True)
            row2.alignment = 'CENTER'
            row2.operator('object.scs_tools_select_prefab_nav_locators', text="", icon='AUTO')
            row2.operator('object.scs_tools_select_prefab_map_locators', text="", icon='LIGHT_SUN')
            row2.operator('object.scs_tools_select_prefab_trigger_locators', text="", icon='FORCE_TURBULENCE')
            row2.operator('object.scs_tools_blank_operator', text="", icon='BLANK1')
'''


class SCS_TOOLS_PT_Visibility(_ToolShelfBlDefs, Panel):
    """
    Creates a Visibility Tools panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Visibility Tools"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        """UI draw function."""
        workspace = context.workspace

        if not workspace:
            return

        if not self.poll(context):
            self.layout.label(text="Not in 'Object Mode'!", icon="INFO")
            return

        layout = self.layout

        scs_root_is_reachable = _object_utils.get_scs_root(context.active_object) is not None

        box = layout.box()

        row = box.row()
        row.prop(workspace.scs_props, "visibility_tools_scope", expand=True)

        col = box.column(align=True)
        col.enabled = scs_root_is_reachable or workspace.scs_props.visibility_tools_scope == "Global"
        row1 = col.row(align=True)
        row1.scale_x = 100  # fake extending to full width
        props = row1.operator('object.scs_tools_switch_model_objects', text="", icon_value=get_icon(_ICON_TYPES.mesh))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.scs_tools_switch_shadow_casters', text="", icon_value=get_icon(_ICON_TYPES.mesh_shadow_caster))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.scs_tools_switch_glass_objects', text="", icon_value=get_icon(_ICON_TYPES.mesh_glass))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row1.operator('object.scs_tools_switch_static_collision_objects', text="", icon_value=get_icon(_ICON_TYPES.mesh_with_physics))
        props.view_type = _OP_consts.ViewType.viewonly
        row2 = col.row(align=True)
        row2.scale_x = 100  # fake extending to full width
        props = row2.operator('object.scs_tools_switch_all_locators', text="", icon_value=get_icon(_ICON_TYPES.loc))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_model_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_model))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_collision_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_collider))
        props.view_type = _OP_consts.ViewType.viewonly

        col = box.column(align=True)
        col.enabled = scs_root_is_reachable or workspace.scs_props.visibility_tools_scope == "Global"
        row2 = col.row(align=True)
        row2.scale_x = 100  # fake extending to full width
        props = row2.operator('object.scs_tools_switch_prefab_node_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_node))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_sign_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_sign))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_spawn_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_spawn))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_traffic_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_semaphore))
        props.view_type = _OP_consts.ViewType.viewonly
        row2 = col.row(align=True)
        row2.scale_x = 100  # fake extending to full width
        props = row2.operator('object.scs_tools_switch_prefab_nav_locators', text="", icon_value=get_icon(_ICONS_consts.Types.loc_prefab_navigation))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_map_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_map))
        props.view_type = _OP_consts.ViewType.viewonly
        props = row2.operator('object.scs_tools_switch_prefab_trigger_locators', text="", icon_value=get_icon(_ICON_TYPES.loc_prefab_trigger))
        props.view_type = _OP_consts.ViewType.viewonly
        row2.operator('object.scs_tools_blank_operator', text="", icon='BLANK1')

        col = layout.column(align=True)
        col.enabled = scs_root_is_reachable or workspace.scs_props.visibility_tools_scope == "Global"
        col.label(text="Current SCS Root:", icon_value=get_icon(_ICONS_consts.Types.scs_root))
        col.operator('object.scs_tools_invert_visibility_within_scs_root', text='Invert Visibility')
        col.operator('object.scs_tools_view_all_objects_within_scs_root', text='View All')
        col.operator('object.scs_tools_isolate_objects_within_scs_root', text='Isolate')


class SCS_TOOLS_PT_DisplayMethods(_ToolShelfBlDefs, Panel):
    """
    Creates a Display Methods panel in the SCS Tools tab.
    """
    bl_context = "objectmode"
    bl_label = "Display Methods"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        """UI draw function."""
        scene = context.scene

        if not scene:
            return

        if not self.poll(context):
            self.layout.label(text="Not in 'Object Mode'!", icon="INFO")
            return

        layout = self.layout

        # GLASS OBJECTS
        col = layout.column(align=True)
        col.label(text="Glass Objects", icon_value=get_icon(_ICON_TYPES.mesh_glass))
        row = col.row(align=True)
        row.operator('object.scs_tools_show_glass_objects_as_wire', text='Wires')
        row.operator('object.scs_tools_show_glass_objects_as_textured', text='Textured')

        # SHADOW CASTERS
        col = layout.column(align=True)
        col.label(text="Shadow Casters", icon_value=get_icon(_ICON_TYPES.mesh_shadow_caster))
        row = col.row(align=True)
        row.operator('object.scs_tools_show_shadow_casters_as_wire', text='Wires')
        row.operator('object.scs_tools_show_shadow_casters_as_textured', text='Textured')

        # COLLISION LOCATORS
        col = layout.column(align=True)
        col.label(text="Collision Locators", icon_value=get_icon(_ICON_TYPES.loc_collider))
        row = col.row(align=True)
        row.operator('object.scs_tools_enable_collision_locators_wire', text='All Wires')
        row.operator('object.scs_tools_disable_collision_locators_wire', text='No Wires')
        row = col.row(align=True)
        row.operator('object.scs_tools_enable_collision_locators_faces', text='All Faces')
        row.operator('object.scs_tools_disable_collision_locators_faces', text='No Faces')


class SCS_TOOLS_PT_LampSwitcher(_ToolShelfBlDefs, Panel):
    """
    Creates Lamp Switcher panel for SCS Tools tab.
    """
    bl_label = "Lamp Switcher"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return not context.vertex_paint_object

    @staticmethod
    def get_lampmask_state_icon(lamp_type):
        """Gets lampmast state icon for given lamp type, to designate whether lamp type is switched on or off.

        :param lamp_type: lamp type gotten from lamp types enumerator names
        :type lamp_type: str
        :return: radio button on or off icon
        :rtype: str
        """

        from io_scs_tools.internals.shaders.eut2.std_node_groups.lampmask_mixer_ng import LAMPMASK_MIX_G

        lamp_type_enabled = False

        if LAMPMASK_MIX_G in bpy.data.node_groups:
            lampmask_nodes = bpy.data.node_groups[LAMPMASK_MIX_G].nodes
            if lamp_type in lampmask_nodes and lampmask_nodes[lamp_type].inputs[0].default_value == 1:
                lamp_type_enabled = True

        return _shared.get_on_off_icon(lamp_type_enabled)

    def draw_lamp_type_switch(self, layout, lamp_type, text_override=None):
        """Draws lamp type switcher operator.

        :param layout: UI to draw operator to
        :type layout: bpy.types.UILayout
        :param lamp_type: lamp type gotten from lamp types enumerator names
        :type lamp_type: str
        :param text_override: text for operator, if None lamp type string is used
        :type text_override: str
        """
        icon = self.get_lampmask_state_icon(lamp_type)
        text = text_override if text_override else lamp_type
        props = layout.operator("material.scs_tools_switch_lampmask", text=text, icon=icon)
        props.lamp_type = lamp_type

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Not in 'Vertex Paint' mode!", icon="INFO")
            return

        layout = self.layout

        # vehicle switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Vehicle", icon='AUTO')

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.Positional.name, text_override="Positional")
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.DRL.name, text_override="DRL")

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.LeftTurn.name, text_override="Left Blinker")
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.RightTurn.name, text_override="Right Blinker")

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.LowBeam.name, text_override="Low Beam")
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.HighBeam.name, text_override="High Beam")

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.Brake.name, text_override="Brake")
        self.draw_lamp_type_switch(body_row, _LT_consts.VehicleLampTypes.Reverse.name, text_override="Reverse")

        # auxiliary switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Auxiliary", icon='LIGHT_SPOT')

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.AuxiliaryLampTypes.Dim.name, text_override="Dim")
        self.draw_lamp_type_switch(body_row, _LT_consts.AuxiliaryLampTypes.Bright.name, text_override="Bright")

        # traffic light switcher
        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Traffic Lights", icon_value=get_icon(_ICONS_consts.Types.loc_prefab_semaphore))

        body_row = body_col.row(align=True)
        self.draw_lamp_type_switch(body_row, _LT_consts.TrafficLightTypes.Red.name, text_override="Red")
        self.draw_lamp_type_switch(body_row, _LT_consts.TrafficLightTypes.Yellow.name, text_override="Yellow")
        self.draw_lamp_type_switch(body_row, _LT_consts.TrafficLightTypes.Green.name, text_override="Green")


class SCS_TOOLS_PT_LampTool(_ToolShelfBlDefs, Panel):
    """
    Creates Lamp Switcher panel for SCS Tools tab.
    """
    bl_label = "Lamp UV Tool"
    bl_context = "mesh_edit"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Not in 'Edit Mode'!", icon="INFO")
            return

        layout = self.layout

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Vehicle", icon='AUTO')

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Front Left")
        props.vehicle_side = _LT_consts.VehicleSides.FrontLeft.name
        props.aux_color = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Front Right")
        props.vehicle_side = _LT_consts.VehicleSides.FrontRight.name
        props.aux_color = props.traffic_light_color = ""
        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Rear Left")
        props.vehicle_side = _LT_consts.VehicleSides.RearLeft.name
        props.aux_color = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Rear Right")
        props.vehicle_side = _LT_consts.VehicleSides.RearRight.name
        props.aux_color = props.traffic_light_color = ""
        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Middle")
        props.vehicle_side = _LT_consts.VehicleSides.Middle.name
        props.aux_color = props.traffic_light_color = ""

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Auxiliary", icon='LIGHT_SPOT')

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="White")
        props.aux_color = _LT_consts.AuxiliaryLampColors.White.name
        props.vehicle_side = props.traffic_light_color = ""
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Orange")
        props.aux_color = _LT_consts.AuxiliaryLampColors.Orange.name
        props.vehicle_side = props.traffic_light_color = ""

        body_col = layout.column(align=True)
        body_row = body_col.row(align=True)
        body_row.label(text="Traffic Lights", icon_value=get_icon(_ICONS_consts.Types.loc_prefab_semaphore))

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Red")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Red.name
        props.vehicle_side = props.aux_color = ""
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Yellow")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Yellow.name
        props.vehicle_side = props.aux_color = ""
        props = body_row.operator("mesh.scs_tools_set_lampmask_uv", text="Green")
        props.traffic_light_color = _LT_consts.TrafficLightTypes.Green.name
        props.vehicle_side = props.aux_color = ""


class SCS_TOOLS_PT_VColoring(_ToolShelfBlDefs, Panel):
    bl_label = "VColoring"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object and bpy.ops.mesh.scs_tools_start_vcoloring.poll()

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Vcoloring not in progress!", icon="INFO")
            return

        layout = self.layout
        body_col = layout.column(align=True)
        active_vcol_name = context.vertex_paint_object.data.color_attributes.active_color.name

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
            props = body_row.operator("mesh.scs_tools_start_vcoloring", text=text, icon=icon)
            props.layer_name = layer_name

        body_row = layout.row()
        body_row.operator("mesh.scs_tools_exit_vcoloring", text="Exit (ESC)", icon='QUIT')


class SCS_TOOLS_PT_VertexColorWrapTool(_ToolShelfBlDefs, Panel):
    bl_label = "Wrap Tool"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Not in 'Vertex Paint' mode!", icon="INFO")
            return

        layout = self.layout
        body_col = layout.column(align=True)

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_wrap_vertex_colors", text="Wrap All")
        props.wrap_type = "all"

        body_row = body_col.row(align=True)
        props = body_row.operator("mesh.scs_tools_wrap_vertex_colors", text="Wrap Selected")
        props.wrap_type = "selected"


class SCS_TOOLS_PT_VertexColorStatsTool(_ToolShelfBlDefs, Panel):
    bl_label = "Stats Tool"

    @classmethod
    def poll(cls, context):
        return context.vertex_paint_object

    def draw(self, context):
        if not self.poll(context):
            self.layout.label(text="Not in 'Vertex Paint' mode!", icon="INFO")
            return

        layout = self.layout

        body_row = layout.row(align=True)
        body_row.operator("mesh.scs_tools_print_vertex_colors_stats")


classes = (
    SCS_TOOLS_PT_ToolShelf,
    SCS_TOOLS_PT_ConvexBlDefs,
    SCS_TOOLS_PT_Visibility,
    SCS_TOOLS_PT_DisplayMethods,
    SCS_TOOLS_PT_LampSwitcher,
    SCS_TOOLS_PT_LampTool,
    SCS_TOOLS_PT_VColoring,
    SCS_TOOLS_PT_VertexColorStatsTool,
    SCS_TOOLS_PT_VertexColorWrapTool,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Tool Shelf", SCS_TOOLS_PT_ToolShelf.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Convex", SCS_TOOLS_PT_ConvexBlDefs.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Visibility Tools", SCS_TOOLS_PT_Visibility.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Display Methods", SCS_TOOLS_PT_DisplayMethods.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Lamp Switcher", SCS_TOOLS_PT_LampSwitcher.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - Lamp Tool", SCS_TOOLS_PT_LampTool.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - VColoring", SCS_TOOLS_PT_VColoring.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - VColor Stats", SCS_TOOLS_PT_VertexColorStatsTool.__name__)
    SCS_TOOLS_MT_MainMenu.append_sidebar_entry("Sidebar - VColor Wrap", SCS_TOOLS_PT_VertexColorWrapTool.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
