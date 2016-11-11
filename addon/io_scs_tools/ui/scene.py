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

import os
from bpy.types import Panel, UIList
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _ScenePanelBlDefs(_shared.HeaderIconPanel):
    """
    Defines class for showing in Blender Scene Properties window
    """
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = ""

    layout = None  # predefined Blender variable to avoid warnings in PyCharm


def _draw_path_settings_panel(scene, layout, scs_globals):
    """Draw global path settings panel.

    :param layout:
    :type layout: bpy.types.Layout
    :return:
    :rtype:
    """
    layout_box = layout.box()
    if scene.scs_props.global_paths_settings_expand:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_paths_settings_expand',
            text="Path Settings:",
            icon='TRIA_DOWN',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')
        layout_box_col = layout_box.column(align=True)

        # SCS Project Path (DIR_PATH - absolute)
        icon = 'SNAP_ON' if _get_scs_globals().use_alternative_bases else 'SNAP_OFF'
        layout_box_col.label('SCS Project Base Path:', icon='FILE_FOLDER')
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not os.path.isdir(scs_globals.scs_project_path)
        layout_box_row.prop(scs_globals, 'scs_project_path', text='', icon='PACKAGE')
        layout_box_row.prop(scs_globals, 'use_alternative_bases', icon=icon, icon_only=True)
        layout_box_row.operator('scene.select_scs_project_path', text='', icon='FILESEL')

        # Divide labels and sub paths to columns
        sub_paths_layout = layout_box_col.row().split(percentage=0.3)
        sub_paths_left_col = sub_paths_layout.column(align=True)
        sub_paths_right_col = sub_paths_layout.column(align=True)

        # Trigger Actions File (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().trigger_actions_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label("Trigger Action Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_trigger_actions_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'trigger_actions_rel_path', text='', icon='FILE_SCRIPT')
        sub_path_right_col_row.prop(scs_globals, 'trigger_actions_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.select_trigger_actions_rel_path', text='', icon='FILESEL')

        # Sign Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().sign_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label("Sign Library:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_sign_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'sign_library_rel_path', text='', icon='FILE_SCRIPT')
        sub_path_right_col_row.prop(scs_globals, 'sign_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.select_sign_library_rel_path', text='', icon='FILESEL')

        # Traffic Semaphore Profile Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().tsem_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label("Semaphore Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_tsem_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'tsem_library_rel_path', text='', icon='FILE_SCRIPT')
        sub_path_right_col_row.prop(scs_globals, 'tsem_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.select_tsem_library_rel_path', text='', icon='FILESEL')

        # Traffic Rules Library Directory (FILE_PATH - relative)
        icon = 'SNAP_ON' if _get_scs_globals().traffic_rules_library_use_infixed else 'SNAP_OFF'
        sub_paths_left_col.label("Traffic Rules Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_traffic_rules_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'traffic_rules_library_rel_path', text='', icon='FILE_SCRIPT')
        sub_path_right_col_row.prop(scs_globals, 'traffic_rules_library_use_infixed', icon=icon, icon_only=True)
        sub_path_right_col_row.operator('scene.select_traffic_rules_library_rel_path', text='', icon='FILESEL')

        # Hookup Library Directory (DIR_PATH - relative)
        sub_paths_left_col.label("Hookup Lib Dir:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_hookup_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'hookup_library_rel_path', text='', icon='FILE_FOLDER')
        sub_path_right_col_row.operator('scene.select_hookup_library_rel_path', text='', icon='FILESEL')

        # Material Substance Library Directory (FILE_PATH - relative)
        sub_paths_left_col.label("Mat Substance Lib:")
        sub_path_right_col_row = sub_paths_right_col.row(align=True)
        sub_path_right_col_row.alert = not _path_utils.is_valid_matsubs_library_rel_path()
        sub_path_right_col_row.prop(scs_globals, 'matsubs_library_rel_path', text='', icon='FILE_SCRIPT')
        sub_path_right_col_row.operator('scene.select_matsubs_library_rel_path', text='', icon='FILESEL')

        layout_box_row = layout_box_col.row()
        layout_box_row.separator()

        # Shader Presets File (FILE_PATH)
        layout_box_col.label('Shader Presets Library:', icon='FILE_TEXT')
        layout_box_row = layout_box_col.row(align=True)
        if _path_utils.is_valid_shader_presets_library_path():
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
        layout_box_row.prop(scs_globals, 'shader_presets_filepath', text='', icon='NONE')
        layout_box_row.operator('scene.select_shader_presets_filepath', text='', icon='FILESEL')

        # CONVERSION TOOLS PATH
        layout_box_col.label("Conversion Tools Path:", icon="FILE_FOLDER")

        layout_box_row = layout_box_col.row(align=True)
        valid = (os.path.isdir(scs_globals.conv_hlpr_converters_path) and
                 os.path.isfile(os.path.join(scs_globals.conv_hlpr_converters_path, "extra_mount.txt")) and
                 os.path.isfile(os.path.join(scs_globals.conv_hlpr_converters_path, "convert.cmd")))
        layout_box_row.alert = not valid
        layout_box_row.prop(scs_globals, "conv_hlpr_converters_path", text="")

    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_paths_settings_expand',
            text="Path Settings:",
            icon='TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')


def _draw_display_settings_panel(scene, layout, scs_globals):
    """Draw global display settings panel."""
    layout_box = layout.box()
    if scene.scs_props.global_display_settings_expand:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_display_settings_expand',
            text="Display Settings:",
            icon='TRIA_DOWN',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')

        layout_box_row = layout_box.row()
        layout_box_row.label("Drawing Mode:")
        layout_box_row.prop(scs_globals, 'drawing_mode', expand=True)

        layout_box_row = layout_box.row()
        if scs_globals.display_locators:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scs_globals, 'display_locators', icon=icon, toggle=True)

        if scs_globals.display_locators:
            layout_box_row = layout_box.row()
            layout_box_row.prop(scs_globals, 'locator_size', icon='NONE')
            layout_box_row.prop(scs_globals, 'locator_empty_size', icon='NONE')
            layout_box_col = layout_box.column()
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'locator_prefab_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'locator_model_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'locator_coll_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'locator_coll_face_color', icon='NONE')
        layout_box_row = layout_box.row()

        if scs_globals.display_connections:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scs_globals, 'display_connections', icon=icon, toggle=True)

        if scs_globals.display_connections:
            layout_box_row = layout_box.row()
            layout_box_row.prop(scs_globals, 'optimized_connections_drawing')
            layout_box_row = layout_box.row()
            layout_box_row.prop(scs_globals, 'curve_segments', icon='NONE')
            layout_box_col = layout_box.column()
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'np_connection_base_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'mp_connection_base_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scs_globals, 'tp_connection_base_color', icon='NONE')

        layout_box_row = layout_box.row()
        layout_box_row.prop(scs_globals, 'display_info', icon='NONE')
        layout_box_row = layout_box.row()
        layout_box_row.prop(scs_globals, 'info_text_color', icon='NONE')
        layout_box_row = layout_box.row()
        if scs_globals.show_preview_models:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scs_globals, 'show_preview_models', icon=icon, toggle=True)
        layout_box_row = layout_box.row()
        layout_box_row.prop(scs_globals, 'base_paint_color', icon='NONE')
    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_display_settings_expand',
            text="Display Settings:",
            icon='TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')


def _draw_global_settings_panel(scene, layout, scs_globals):
    """Draw global settings panel."""
    layout_column = layout.column(align=True)
    layout_box = layout_column.box()  # header
    if scene.scs_props.global_settings_expand:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_settings_expand',
            text="Global Settings:",
            icon='TRIA_DOWN',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')

        # GLOBAL SETTINGS PANEL
        # draw_scs_tools_settings_panel_box(layout_box.row())

        layout_box = layout_column.box()  # body
        # PATH SETTINGS PANEL
        _draw_path_settings_panel(scene, layout_box.row(), scs_globals)

        # DISPLAY SETTINGS PANEL
        _draw_display_settings_panel(scene, layout_box.row(), scs_globals)

        _shared.draw_common_settings(layout_box)

    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(
            scene.scs_props,
            'global_settings_expand',
            text="Global Settings:",
            icon='TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )
        layout_box_row.label('')


def _draw_export_panel(scene, layout, scs_globals):
    """Draw Export panel."""
    layout_column = layout.column(align=True)
    layout_box = layout_column.box()  # header
    if scene.scs_props.export_panel_expand:
        box_row = layout_box.row()
        box_row.prop(scene.scs_props, 'export_panel_expand', text="Export Panel:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        box_row.label('')

        layout_box = layout_column.box()  # body
        if not scs_globals.preview_export_selection_active:

            col = layout_box.column(align=True)
            col.row(align=True).prop(scs_globals, 'export_scope', expand=True)

            col_row = col.row(align=True)
            col_row.enabled = scs_globals.export_scope == "selection"
            icon = "FILE_TICK" if scs_globals.preview_export_selection else "X_VEC"
            col_row.prop(scs_globals, 'preview_export_selection', text="Preview Selection", icon=icon, toggle=True)

            col_row = col.row(align=True)
            col_row.scale_y = 2
            col_row.operator('scene.export_scs_content_by_scope', text="EXPORT")

        else:

            row = layout_box.box()
            row.prop(scs_globals, "preview_export_selection_active", text="Export preview mode is active!", icon='ERROR', icon_only=True,
                     emboss=False)
            row = row.column(align=True)
            row.label("Press ENTER to export selection!")
            row.label("Press ESC to cancel export!")

        box_row = layout_box.row()
        box = box_row.box()
        col = box.column()

        # Default Export Path (FILE_PATH - relative)
        col_row = col.row()
        col_row.label("Default Export Path:", icon="FILE_FOLDER")
        col_row = col.row(align=True)
        default_export_path = scene.scs_props.default_export_filepath
        col_row.alert = ((default_export_path != "" and not default_export_path.startswith("//")) or
                         not os.path.isdir(os.path.join(scs_globals.scs_project_path, default_export_path.strip("//"))))
        if col_row.alert:
            _shared.draw_warning_operator(
                col_row,
                "Default Export Path Warning",
                str("Current Default Export Path is unreachable, which may result into an error on export!\n"
                    "Make sure you did following:\n"
                    "1. Properly set \"SCS Project Base Path\"\n"
                    "2. Properly set \"Default Export Path\" which must be relative on \"SCS Project Base Path\"")
            )

        col_row.prop(scene.scs_props, 'default_export_filepath', text='', icon='EXPORT')
        props = col_row.operator('scene.select_directory_inside_base', text='', icon='FILESEL')
        props.type = "DefaultExportPath"

        _shared.draw_export_panel(layout_box)
    else:
        box_row = layout_box.row()
        box_row.prop(scene.scs_props, 'export_panel_expand', text="Export Panel:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        box_row.label('')


def _draw_conversion_panel(layout, scs_globals):
    """Draw Conversion Helper panel."""
    layout_column = layout.column(align=True)
    layout_box = layout_column.box()  # header
    if scs_globals.conversion_helper_expand:
        box_row = layout_box.row()
        box_row.prop(scs_globals, 'conversion_helper_expand', text="Conversion Helper:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        box_row.label('')

        layout_box = layout_column.box()  # body

        # CLEAN & CONVERT CURRENT
        row = layout_box.row(align=True)
        row.scale_y = 1.2
        row.operator("scene.scs_conv_hlpr_clean_rsrc", text='CLEAN RSRC')
        row.operator("scene.scs_conv_hlpr_convert_current", text='CONVERT CURRENT SCS PROJECT')

        # CUSTOM PATHS & CONVERT
        cstm_paths_col = layout_box.column(align=False)
        cstm_paths_col.label("Custom Paths:", icon="LINENUMBERS_ON")

        row = cstm_paths_col.row()
        row.column().template_list(
            'SCSConversionEntrySlots',
            list_id="",
            dataptr=scs_globals,
            propname="conv_hlpr_custom_paths",
            active_dataptr=scs_globals,
            active_propname="conv_hlpr_custom_paths_active",
            rows=3,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )

        side_bar = row.column(align=True)
        side_bar.operator("scene.scs_conv_hlpr_add_path", text="", icon="ZOOMIN")
        side_bar.operator("scene.scs_conv_hlpr_remove_path", text="", icon="ZOOMOUT")
        side_bar.separator()
        props = side_bar.operator("scene.scs_conv_hlpr_order_path", icon="TRIA_UP", text="")
        props.move_up = True
        props = side_bar.operator("scene.scs_conv_hlpr_order_path", icon="TRIA_DOWN", text="")
        props.move_up = False

        row = cstm_paths_col.row(align=True)
        row.scale_y = 1.2
        row.operator("scene.scs_conv_hlpr_convert_custom", text='CONVERT CUSTOM PATHS')

        # PACKING
        col = layout_box.column(align=True)
        col.row().label("Mod Packing:", icon="PACKAGE")

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_destination", text="", icon="FILE_FOLDER")
        row.operator("scene.scs_conv_hlpr_find_mod_folder", text="", icon="RECOVER_AUTO")

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_name", text="", icon="FILE")

        row = col.row(align=True)
        row.scale_y = 1.2
        icon = "FILE_TICK" if scs_globals.conv_hlpr_clean_on_packing else "X_VEC"
        row.prop(scs_globals, "conv_hlpr_clean_on_packing", toggle=True, icon=icon)
        icon = "FILE_TICK" if scs_globals.conv_hlpr_export_on_packing else "X_VEC"
        row.prop(scs_globals, "conv_hlpr_export_on_packing", toggle=True, icon=icon)
        icon = "FILE_TICK" if scs_globals.conv_hlpr_convert_on_packing else "X_VEC"
        row.prop(scs_globals, "conv_hlpr_convert_on_packing", toggle=True, icon=icon)

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_compression", expand=True)

        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("scene.scs_conv_hlpr_pack", text="PACK CONVERTED DATA")

    else:
        box_row = layout_box.row()
        box_row.prop(scs_globals, 'conversion_helper_expand', text="Conversion Helper:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        box_row.label('')


class SCSConversionEntrySlots(UIList):
    """
    Draw conversion path entry within ui list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            icon = "ERROR" if not os.path.isdir(_path_utils.repair_path(item.path)) else "NONE"
            layout.prop(item, "path", text="", emboss=False, icon=icon)
        else:
            layout.label(text="", icon_value=icon)


class SCSTools(_ScenePanelBlDefs, Panel):
    """Creates a Panel in the Scene properties window"""
    bl_label = "SCS Tools"
    bl_idname = "OBJECT_PT_SCS_tools"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = context.scene
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        if scene:

            # GLOBAL SETTINGS PANEL
            _draw_global_settings_panel(scene, layout, scs_globals)

            # EXPORT PANEL
            if context.mode == 'OBJECT':
                _draw_export_panel(scene, layout, scs_globals)

            # CONVERSION PANEL
            _draw_conversion_panel(layout, scs_globals)
