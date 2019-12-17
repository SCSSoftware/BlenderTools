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

# Copyright (C) 2019: SCS Software

import os
import bpy
from bpy.types import Panel, UIList
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _OutputPanelBlDefs(_shared.HeaderIconPanel):
    """
    Defines class for showing in Blender Output Properties window
    """
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_ui_units_x = 15

    layout = None  # predefined Blender variable to avoid warnings in PyCharm


class SCS_TOOLS_PT_ExportPanel(_OutputPanelBlDefs, Panel):
    """Draw Export panel."""

    bl_label = "SCS Export"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        if not scs_globals.preview_export_selection_active:

            col = layout.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.2

            if scs_globals.export_scope == "selection":
                icon = _shared.get_on_off_icon(scs_globals.preview_export_selection)
                row.prop(scs_globals, 'preview_export_selection', text="", icon=icon, toggle=False)

            row.prop(scs_globals, 'export_scope', expand=True)

            col_row = col.row(align=True)
            col_row.scale_y = 2
            col_row.operator('scene.scs_tools_export_by_scope', text="EXPORT")

        else:

            row = layout.box()
            row.prop(scs_globals, "preview_export_selection_active", text="Export preview mode is active!", icon='ERROR', icon_only=True,
                     emboss=False)
            row = row.column(align=True)
            row.label(text="Rotate view:")
            row.label(text="* Left Mouse Button + move")
            row.label(text="* Numpad 2, 4, 6, 8")
            row.label(text="Zoom in/out:")
            row.label(text="* Mouse Scroll")
            row.label(text="* Numpad '+', '-'")
            row.separator()
            row.label(text="Press ENTER to export selection!")
            row.label(text="Press ESC to cancel export!")

        col = layout.column()

        # Fallback Export Path (FILE_PATH - relative)
        col_row = _shared.create_row(col, use_split=True, enabled=True)
        default_export_path = scene.scs_props.default_export_filepath
        col_row.alert = ((default_export_path != "" and not default_export_path.startswith("//")) or
                         not os.path.isdir(os.path.join(scs_globals.scs_project_path, default_export_path.strip("//"))))
        col_row.prop(scene.scs_props, 'default_export_filepath', icon='EXPORT')
        if col_row.alert:
            _shared.draw_warning_operator(
                col_row,
                "Default Export Path Warning",
                str("Current Default Export Path is unreachable, which may result into an error on export!\n"
                    "Make sure you did following:\n"
                    "1. Properly set \"SCS Project Base Path\"\n"
                    "2. Properly set \"Default Export Path\" which must be relative on \"SCS Project Base Path\"")
            )

        props = col_row.operator('scene.scs_tools_select_dir_inside_base', text="", icon='FILEBROWSER')
        props.type = "DefaultExportPath"

        _shared.draw_export_panel(layout, ignore_extra_boxes=True)


class SCS_TOOLS_UL_ConversionPathsSlot(UIList):
    """
    Draw conversion path entry within ui list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            icon = 'ERROR' if not os.path.isdir(_path_utils.repair_path(item.path)) else 'NONE'
            layout.prop(item, "path", text="", emboss=False, icon=icon)
        else:
            layout.label(text="", icon_value=icon)


class SCS_TOOLS_PT_ConversionHelper(_OutputPanelBlDefs, Panel):
    """Draw Conversion Helper panel."""

    bl_label = "SCS Conversion Helper"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('scene.scs_tools_clean_conversion_rsrc', text="", icon='SCULPTMODE_HLT')
        layout.separator(factor=0.1)

    def draw(self, context):
        layout = self.layout
        scs_globals = _get_scs_globals()

        # scs tools main panel if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        # CONVERSION TOOLS PATH
        col = layout.column(align=True)
        col.label(text="Conversion Tools Path:", icon='FILE_FOLDER')
        row = col.row(align=True)
        valid = (os.path.isdir(scs_globals.conv_hlpr_converters_path) and
                 os.path.isfile(os.path.join(scs_globals.conv_hlpr_converters_path, "extra_mount.txt")) and
                 os.path.isfile(os.path.join(scs_globals.conv_hlpr_converters_path, "convert.cmd")))
        row.alert = not valid
        row.prop(scs_globals, "conv_hlpr_converters_path", text="")

        # CUSTOM PATHS
        cstm_paths_col = layout.column(align=not scs_globals.conv_hlpr_use_custom_paths)
        row = cstm_paths_col.row(align=True)
        row.scale_y = 1.1
        text = "Custom Paths: ON" if scs_globals.conv_hlpr_use_custom_paths else "Custom Paths: OFF"
        icon = _shared.get_on_off_icon(scs_globals.conv_hlpr_use_custom_paths)
        row.prop(scs_globals, "conv_hlpr_use_custom_paths", text=text, icon=icon, toggle=True)

        if scs_globals.conv_hlpr_use_custom_paths:
            row = cstm_paths_col.row()
            row.template_list(
                SCS_TOOLS_UL_ConversionPathsSlot.__name__,
                list_id="",
                dataptr=scs_globals,
                propname="conv_hlpr_custom_paths",
                active_dataptr=scs_globals,
                active_propname="conv_hlpr_custom_paths_active",
                rows=4,
                maxrows=5,
                type='DEFAULT',
                columns=9
            )

            side_bar = row.column(align=True)
            side_bar.operator("scene.scs_tools_add_conversion_path", text="", icon='ADD')
            side_bar.operator("scene.scs_tools_remove_conversion_path", text="", icon='REMOVE')
            side_bar.separator()

            props = side_bar.operator("scene.scs_tools_order_conversion_path", icon='TRIA_UP', text="")
            props.move_up = True
            props = side_bar.operator("scene.scs_tools_order_conversion_path", icon='TRIA_DOWN', text="")
            props.move_up = False

        # CONVERT
        row = cstm_paths_col.column(align=True)
        row.scale_y = 1.1
        row.operator("scene.scs_tools_convert_current_base", text='CONVERT CURRENT SCS PROJECT')
        if scs_globals.conv_hlpr_use_custom_paths:
            row.operator("scene.scs_tools_convert_custom_paths", text='CONVERT CUSTOM PATHS')
            row.operator("scene.scs_tools_convert_all_paths", text='CONVERT ALL')

        # PACKING
        col = layout.column(align=True)
        col.row().label(text="Mod Package Settings:", icon='PACKAGE')

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_destination", text="")
        row.operator("scene.scs_tools_find_game_mod_folder", text="", icon='ZOOM_SELECTED')

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_name", text="")

        row = col.row(align=True)
        row.prop(scs_globals, "conv_hlpr_mod_compression", text="")

        col.separator()

        row = col.row(align=True)
        row.scale_y = 1.1
        icon = _shared.get_on_off_icon(scs_globals.conv_hlpr_clean_on_packing)
        row.prop(scs_globals, "conv_hlpr_clean_on_packing", toggle=True, icon=icon)
        icon = _shared.get_on_off_icon(scs_globals.conv_hlpr_export_on_packing)
        row.prop(scs_globals, "conv_hlpr_export_on_packing", toggle=True, icon=icon)
        icon = _shared.get_on_off_icon(scs_globals.conv_hlpr_convert_on_packing)
        row.prop(scs_globals, "conv_hlpr_convert_on_packing", toggle=True, icon=icon)

        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("scene.scs_tools_run_packing", text=">>>>    PACK MOD    <<<<")


classes = (
    SCS_TOOLS_PT_ExportPanel,
    SCS_TOOLS_UL_ConversionPathsSlot,
    SCS_TOOLS_PT_ConversionHelper,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_output_entry("Output - Export", SCS_TOOLS_PT_ExportPanel.__name__)
    SCS_TOOLS_MT_MainMenu.append_output_entry("Output - Conversion", SCS_TOOLS_PT_ConversionHelper.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
