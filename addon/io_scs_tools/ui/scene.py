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
from bpy.types import Panel
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
        layout_box_col = layout_box.column()

        # SCS Project Path (DIR_PATH - absolute)
        layout_box_col.label('SCS Project Base Path:', icon='FILE_FOLDER')
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not os.path.isdir(scs_globals.scs_project_path)
        layout_box_row.prop(scs_globals, 'scs_project_path', text='', icon='PACKAGE')
        layout_box_row.operator('scene.select_scs_project_path', text='', icon='FILESEL')

        # Sign Library Directory (FILE_PATH - relative)
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not _path_utils.is_valid_sign_library_rel_path()
        layout_box_row.prop(scs_globals, 'sign_library_rel_path', icon='FILE_SCRIPT')
        layout_box_row.operator('scene.select_sign_library_rel_path', text='', icon='FILESEL')

        # Traffic Semaphore Profile Library Directory (FILE_PATH - relative)
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not _path_utils.is_valid_tsem_library_rel_path()
        layout_box_row.prop(scs_globals, 'tsem_library_rel_path', text="Semaphore Lib", icon='FILE_SCRIPT')
        layout_box_row.operator('scene.select_tsem_library_rel_path', text='', icon='FILESEL')

        # Traffic Rules Library Directory (FILE_PATH - relative)
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not _path_utils.is_valid_traffic_rules_library_rel_path()
        layout_box_row.prop(scs_globals, 'traffic_rules_library_rel_path', text="Traffic Rules Lib", icon='FILE_SCRIPT')
        layout_box_row.operator('scene.select_traffic_rules_library_rel_path', text='', icon='FILESEL')

        # Hookup Library Directory (DIR_PATH - relative)
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not _path_utils.is_valid_hookup_library_rel_path()
        layout_box_row.prop(scs_globals, 'hookup_library_rel_path', text="Hookup Lib Dir", icon='FILE_FOLDER')
        layout_box_row.operator('scene.select_hookup_library_rel_path', text='', icon='FILESEL')

        # Material Substance Library Directory (FILE_PATH - relative)
        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not _path_utils.is_valid_matsubs_library_rel_path()
        layout_box_row.prop(scs_globals, 'matsubs_library_rel_path', text="Mat Substance Lib", icon='FILE_SCRIPT')
        layout_box_row.operator('scene.select_matsubs_library_rel_path', text='', icon='FILESEL')

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

        # ## CgFX Templates File (FILE_PATH)
        # layout_box_row = layout_box_col.row(align=True)
        # if utils.is_valid_cgfx_template_library_path():
        # layout_box_row.alert = False
        # else:
        # layout_box_row.alert = True
        # layout_box_row.prop(scs_globals, 'cgfx_templates_filepath', icon='FILE_TEXT')
        # layout_box_row.operator('scene.select_cgfx_templates_filepath', text='', icon='FILESEL')
        #
        # ## CgFX Library Directory (DIR_PATH - relative)
        # layout_box_row = layout_box_col.row(align=True)
        # if utils.is_valid_cgfx_library_rel_path():
        # layout_box_row.alert = False
        # else:
        # layout_box_row.alert = True
        # layout_box_row.prop(scs_globals, 'cgfx_library_rel_path', icon='FILE_FOLDER')
        # layout_box_row.operator('scene.select_cgfx_library_rel_path', text='', icon='FILESEL')

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


def _draw_display_settings_panel(scene, layout):
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
        layout_box_row.prop(scene.scs_props, 'drawing_mode', expand=True)

        layout_box_row = layout_box.row()
        if scene.scs_props.display_locators:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scene.scs_props, 'display_locators', icon=icon, toggle=True)

        if scene.scs_props.display_locators:
            layout_box_row = layout_box.row()
            layout_box_row.prop(scene.scs_props, 'locator_size', icon='NONE')
            layout_box_row.prop(scene.scs_props, 'locator_empty_size', icon='NONE')
            layout_box_col = layout_box.column()
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'locator_prefab_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'locator_model_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'locator_coll_wire_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'locator_coll_face_color', icon='NONE')
        layout_box_row = layout_box.row()

        if scene.scs_props.display_connections:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scene.scs_props, 'display_connections', icon=icon, toggle=True)

        if scene.scs_props.display_connections:
            layout_box_row = layout_box.row()
            layout_box_row.prop(scene.scs_props, 'optimized_connections_drawing')
            layout_box_row = layout_box.row()
            layout_box_row.prop(scene.scs_props, 'curve_segments', icon='NONE')
            layout_box_col = layout_box.column()
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'np_connection_base_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'mp_connection_base_color', icon='NONE')
            layout_box_row = layout_box_col.row()
            layout_box_row.prop(scene.scs_props, 'tp_connection_base_color', icon='NONE')

        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props, 'display_info', icon='NONE')
        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props, 'info_text_color', icon='NONE')
        layout_box_row = layout_box.row()
        if scene.scs_props.show_preview_models:
            icon = "FILE_TICK"
        else:
            icon = "X_VEC"
        layout_box_row.prop(scene.scs_props, 'show_preview_models', icon=icon, toggle=True)
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
        _draw_display_settings_panel(scene, layout_box.row())

        _shared.draw_debug_settings(layout_box)

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
        if not scene.scs_props.preview_export_selection_active:
            col = layout_box.column(align=True)
            col_extra = col.column(align=True)
            col_extra.scale_y = 2
            col_extra.operator('scene.export_selected', text='EXPORT SELECTED')
            if scene.scs_props.preview_export_selection:
                icon = "FILE_TICK"
            else:
                icon = "X_VEC"
            col.prop(scene.scs_props, 'preview_export_selection', text="Preview Selection", icon=icon, toggle=True)

            box_row = layout_box.row()
            box_row.scale_y = 2
            box_row.operator('scene.export_scene', text='EXPORT SCENE')
            box_row.operator('scene.export_all', text='EXPORT ALL')
        else:
            row = layout_box.box()
            row.prop(scene.scs_props, "preview_export_selection_active", text="Export preview mode is active!", icon='ERROR', icon_only=True,
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
        col_row.alert = ((default_export_path != "" and not default_export_path.startswith(os.sep * 2)) or
                         not os.path.isdir(os.path.join(scs_globals.scs_project_path, default_export_path.strip(os.sep * 2))))
        if col_row.alert:
            _shared.draw_warning_operator(
                col_row,
                "Default Export Path Warning",
                str("Current Default Export Path is unreachable, which may result into an error on export!\n" +
                    "Make sure you did following:\n"
                    "1. Properly set \"SCS Project Base Path\"\n" +
                    "2. Properly set \"Default Export Path\" which must be relative on \"SCS Project Base Path\"")
            )

        col_row.prop(scene.scs_props, 'default_export_filepath', text='', icon='EXPORT')
        col_row.operator('scene.select_default_export_filepath', text='', icon='FILESEL')

        _shared.draw_export_panel(layout_box)
    else:
        box_row = layout_box.row()
        box_row.prop(scene.scs_props, 'export_panel_expand', text="Export Panel:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        box_row.label('')


class SCSTools(_ScenePanelBlDefs, Panel):
    """Creates a Panel in the Scene properties window"""
    bl_label = "SCS Tools"
    bl_idname = "OBJECT_PT_SCS_tools"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = context.scene
        # print('scene: %r\t- %r' % (scene.name, context.scene.name))
        # obj = context.object  # FIXME: Gives 'None type' in this place - everywhere else it works normally (?!?)
        # print('obj:   %s\t- %s' % (obj, context.object))
        # blend_data = context.blend_data
        scs_globals = _get_scs_globals()

        # def draw_scs_tools_settings_panel_box(layout):
        # """Draw SCS Tools settings panel box."""
        # layout_box = layout.box()
        # layout_box_row = layout_box.row()
        # layout_box_row.prop(scene.scs_props, 'scs_lod_definition_type', icon='NONE', expand=True)
        # layout_box_row.prop(scs_globals, 'scs_lod_definition_type', icon='NONE', expand=True)

        if scene:
            # PART PANEL
            # if obj:  # FIXME: 'None type' obj - see above...
            # ui.shared.draw_part_panel(layout, scene, obj)

            # GLOBAL SETTINGS PANEL
            _draw_global_settings_panel(scene, layout, scs_globals)

            # EXPORT PANEL
            if context.mode == 'OBJECT':
                _draw_export_panel(scene, layout, scs_globals)