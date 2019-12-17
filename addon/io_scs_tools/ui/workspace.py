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
from bl_ui.utils import PresetPanel
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _WorkspacePanelBlDefs:
    """
    Defines class for showing in Blender Scene Properties window
    """
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_ui_units_x = 15

    layout = None  # predefined Blender variable to avoid warnings in PyCharm
    is_popover = None  # predefined Blender variable to avoid warnings in PyCharm

    @classmethod
    def poll(cls, context):
        return context.region.type in ('WINDOW', 'HEADER')

    def get_layout(self):
        """Returns layout depending where it's drawn into. If popover create extra box to make it distinguisable between different sub-panels."""
        if self.is_popover:
            layout = self.layout.box().column()
        else:
            layout = self.layout

        return layout


class SCS_TOOLS_PT_GlobalSettings(_shared.HeaderIconPanel, _WorkspacePanelBlDefs, Panel):
    """Draw global settings panel."""

    bl_label = "SCS Global Settings"

    def draw(self, context):
        pass


class SCS_TOOLS_PT_PathSettingsPresets(PresetPanel, Panel):
    bl_label = "SCS Tools Paths Presets"
    preset_subdir = "io_scs_tools/paths"
    preset_operator = "script.execute_preset"
    preset_add_operator = "scene.scs_tools_add_path_preset"


class SCS_TOOLS_PT_PathSettings(_WorkspacePanelBlDefs, Panel):
    """Draw global path settings panel."""

    bl_parent_id = SCS_TOOLS_PT_GlobalSettings.__name__
    bl_label = "Path Settings"

    def draw_header_preset(self, context):
        SCS_TOOLS_PT_PathSettingsPresets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.get_layout()
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        # SCS Project Path (DIR_PATH - absolute)
        icon = 'SNAP_ON' if _get_scs_globals().use_alternative_bases else 'SNAP_OFF'
        layout.label(text="SCS Project Base Path:", icon='FILE_FOLDER')
        row = layout.row(align=True)
        row.alert = not os.path.isdir(scs_globals.scs_project_path)
        row.prop(scs_globals, 'scs_project_path', text="")
        row.prop(scs_globals, 'use_alternative_bases', icon=icon, icon_only=True)
        row.operator('scene.scs_tools_select_project_path', text="", icon='FILEBROWSER')

        # Divide labels and sub paths to columns
        sub_paths_layout = layout.row().split(factor=0.35)
        sub_paths_left_col = sub_paths_layout.column(align=True)
        sub_paths_right_col = sub_paths_layout.column(align=True)

        # Trigger Actions File (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().trigger_actions_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label(text="Trigger Action Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_trigger_actions_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'trigger_actions_rel_path', text="", icon='FILE_CACHE')
        sub_path_right_col_row.prop(scs_globals, 'trigger_actions_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.scs_tools_select_trigger_actions_lib_path', text="", icon='FILEBROWSER')

        # Sign Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().sign_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label(text="Sign Library:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_sign_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'sign_library_rel_path', text="", icon='FILE_CACHE')
        sub_path_right_col_row.prop(scs_globals, 'sign_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.scs_tools_select_sign_lib_path', text="", icon='FILEBROWSER')

        # Traffic Semaphore Profile Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().tsem_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label(text="Semaphore Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_tsem_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'tsem_library_rel_path', text="", icon='FILE_CACHE')
        sub_path_right_col_row.prop(scs_globals, 'tsem_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.scs_tools_select_semaphore_lib_path', text="", icon='FILEBROWSER')

        # Traffic Rules Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().traffic_rules_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label(text="Traffic Rules Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_traffic_rules_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'traffic_rules_library_rel_path', text="", icon='FILE_CACHE')
        sub_path_right_col_row.prop(scs_globals, 'traffic_rules_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.scs_tools_select_traffic_rules_lib_path', text="", icon='FILEBROWSER')

        # Hookup Library Directory (DIR_PATH - relative)
        sub_paths_left_col.label(text="Hookup Lib Dir:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_hookup_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'hookup_library_rel_path', text="", icon='FILE_FOLDER')
        sub_path_right_col_row.operator('scene.scs_tools_select_hookup_lib_path', text="", icon='FILEBROWSER')

        # Material Substance Library Directory (FILE_PATH - relative)
        sub_paths_left_col.label(text="Mat Substance Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_matsubs_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'matsubs_library_rel_path', text="", icon='FILE_CACHE')
        sub_path_right_col_row.operator('scene.scs_tools_select_matsubs_lib_path', text="", icon='FILEBROWSER')

        row = layout.row()
        row.separator()

        # Shader Presets File (FILE_PATH)
        layout.label(text="Shader Presets Library:", icon='FILE_TEXT')
        row = layout.row(align=True)
        row.prop(scs_globals, 'shader_presets_use_custom', text="")
        custom_path_row = row.row(align=True)
        custom_path_row.enabled = scs_globals.shader_presets_use_custom
        custom_path_row.alert = not _path_utils.is_valid_shader_presets_library_path()
        custom_path_row.prop(scs_globals, 'shader_presets_filepath', text="")
        custom_path_row.operator('scene.scs_tools_select_shader_presets_path', text="", icon='FILEBROWSER')


class SCS_TOOLS_PT_DisplaySettings(_WorkspacePanelBlDefs, Panel):
    """Draw global display settings panel."""

    bl_parent_id = SCS_TOOLS_PT_GlobalSettings.__name__
    bl_label = "Display Settings"

    def draw(self, context):
        layout = self.get_layout()
        scs_globals = _get_scs_globals()

        layout.use_property_split = True
        layout.use_property_decorate = False

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        layout.prop(scs_globals, 'drawing_mode', expand=True)

        layout.prop(scs_globals, 'icon_theme')
        layout.prop(scs_globals, 'display_info')
        row = _shared.create_row(layout, use_split=True, align=True, enabled=scs_globals.display_info != "none")
        row.prop(scs_globals, 'info_text_color')
        layout.prop(scs_globals, 'base_paint_color')
        layout.prop(scs_globals, 'show_preview_models')


class SCS_TOOLS_PT_LocatorsDisplay(_WorkspacePanelBlDefs, Panel):
    """Draw locators display panel."""

    bl_parent_id = SCS_TOOLS_PT_DisplaySettings.__name__
    bl_label = "Locators Display"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scs_globals = _get_scs_globals()

        layout.enabled = not scs_globals.config_update_lock
        layout.prop(scs_globals, 'display_locators', text="")

    def draw(self, context):
        layout = self.get_layout()
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.enabled = scs_globals.display_locators and not scs_globals.config_update_lock

        layout.prop(scs_globals, 'locator_size')
        layout.prop(scs_globals, 'locator_empty_size')
        layout.prop(scs_globals, 'locator_prefab_wire_color')
        layout.prop(scs_globals, 'locator_model_wire_color')
        layout.prop(scs_globals, 'locator_coll_wire_color')
        layout.prop(scs_globals, 'locator_coll_face_color')


class SCS_TOOLS_PT_ConnectionsDisplay(_WorkspacePanelBlDefs, Panel):
    """Draw connections display panel."""

    bl_parent_id = SCS_TOOLS_PT_DisplaySettings.__name__
    bl_label = "Connections Display"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scs_globals = _get_scs_globals()

        layout.enabled = not scs_globals.config_update_lock
        layout.prop(scs_globals, 'display_connections', text="")

    def draw(self, context):
        layout = self.get_layout()
        scs_globals = _get_scs_globals()

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.enabled = scs_globals.display_connections and not scs_globals.config_update_lock

        layout.prop(scs_globals, 'optimized_connections_drawing')
        layout.prop(scs_globals, 'curve_segments')
        layout.prop(scs_globals, 'np_connection_base_color')
        layout.prop(scs_globals, 'mp_connection_base_color')
        layout.prop(scs_globals, 'tp_connection_base_color')


class SCS_TOOLS_PT_OtherSetttings(_WorkspacePanelBlDefs, Panel):
    """Draw global settings panel."""

    bl_parent_id = SCS_TOOLS_PT_GlobalSettings.__name__
    bl_label = "Other Settings"

    def draw_header(self, context):
        pass  # disable custom icon

    def draw(self, context):
        """Draw global settings panel."""
        layout = self.get_layout()
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        _shared.draw_common_settings(layout, without_box=True)


classes = (
    SCS_TOOLS_PT_GlobalSettings,
    SCS_TOOLS_PT_PathSettingsPresets,
    SCS_TOOLS_PT_PathSettings,
    SCS_TOOLS_PT_DisplaySettings,
    SCS_TOOLS_PT_LocatorsDisplay,
    SCS_TOOLS_PT_ConnectionsDisplay,
    SCS_TOOLS_PT_OtherSetttings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_props_entry("Workspace Properties", SCS_TOOLS_PT_GlobalSettings.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
