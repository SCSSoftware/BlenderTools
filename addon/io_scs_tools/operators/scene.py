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

# Copyright (C) 2013-2022: SCS Software

import bpy
import bmesh
import numpy
import os
import subprocess
from collections import OrderedDict
from hashlib import sha1
from sys import platform
from time import time
from bpy.props import StringProperty, CollectionProperty, EnumProperty, IntProperty, BoolProperty, FloatProperty, FloatVectorProperty
from bl_operators.presets import AddPresetBase
from io_scs_tools.consts import ConvHlpr as _CONV_HLPR_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.consts import PaintjobTools as _PT_consts
from io_scs_tools.imp import pix as _pix_import
from io_scs_tools.internals.structure import UnitData as _UnitData
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.containers import sii as _sii_container
from io_scs_tools.internals.containers.tobj import TobjContainer as _TobjContainer
from io_scs_tools.operators.bases.export import SCSExportHelper as _SCSExportHelper
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.property import get_default as _get_default
from io_scs_tools.utils.property import get_filebrowser_display_type
from io_scs_tools import exp as _export
from io_scs_tools import imp as _import


class Import:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_ImportAnimActions(bpy.types.Operator):
        bl_label = "Import SCS Animation (PIA)"
        bl_idname = "scene.scs_tools_import_anim_actions"
        bl_description = "Import SCS Animation files (PIA) as a new SCS animations"

        directory: StringProperty(
            name="Import PIA Directory",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        files: CollectionProperty(
            type=bpy.types.OperatorFileListElement,
            options={'HIDDEN', 'SKIP_SAVE'},
        )
        filter_glob: StringProperty(default="*.pia", options={'HIDDEN'})

        @classmethod
        def poll(cls, context):
            active_obj = context.active_object
            return active_obj and active_obj.type == "ARMATURE" and _object_utils.get_scs_root(active_obj)

        def execute(self, context):
            lprint('D Import Animation Action...')

            pia_files = [os.path.join(self.directory, file.name) for file in self.files]

            armature = context.active_object
            root_object = _object_utils.get_scs_root(armature)

            imported_count = _import.pia.load(root_object, pia_files, armature)

            # report warnings and errors if actually imported count differs from number of pia files
            if imported_count != len(pia_files):
                lprint("", report_warnings=1, report_errors=1)

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


class Export:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_ExportByScope(bpy.types.Operator, _SCSExportHelper):
        """Export selected operator."""
        bl_idname = "scene.scs_tools_export_by_scope"
        bl_label = "Export By Used Scope"
        bl_description = "Export SCS models depending on selected export scope."
        bl_options = set()

        def __init__(self):
            super().__init__()

            self.can_mouse_rotate = False
            """:type bool: Flag indiciating whether mouse move even will rotate view or no. Initiated by left mouse button press."""

        @staticmethod
        def execute_rotation(rot_direction, angle=0.05):
            """Uses Blender orbit rotation to rotate all 3D views
            :param rot_direction: "ORBITLEFT" | "ORBITRIGHT" | "ORBITUP" | "ORBITDOWN"
            :type rot_direction: str
            :param angle: angle to use by rotation, in radians
            :type angle: float
            """
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    override = {
                        'window': bpy.context.window,
                        'screen': bpy.context.screen,
                        'blend_data': bpy.context.blend_data,
                        'scene': bpy.context.scene,
                        'region': area.regions[5],
                        'area': area
                    }
                    bpy.ops.view3d.view_orbit(override, angle=angle, type=rot_direction)

        @staticmethod
        def execute_zoom(zoom_change):
            """Uses Blender view distance zoom all 3D views
            :param zoom_change: zoom step in integer
            :type zoom_change: int
            """
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    region = area.spaces[0].region_3d
                    region.view_distance += zoom_change

        def modal(self, context, event):

            ret_status = {'RUNNING_MODAL'}

            if event.type in ('WHEELUPMOUSE', 'NUMPAD_PLUS'):
                self.execute_zoom(-1)
            elif event.type in ('WHEELDOWNMOUSE', 'NUMPAD_MINUS'):
                self.execute_zoom(1)
            elif event.type == 'NUMPAD_4':
                self.execute_rotation("ORBITLEFT")
            elif event.type == 'NUMPAD_6':
                self.execute_rotation("ORBITRIGHT")
            elif event.type == 'NUMPAD_8':
                self.execute_rotation("ORBITUP")
            elif event.type == 'NUMPAD_2':
                self.execute_rotation("ORBITDOWN")
            elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.can_mouse_rotate = True
            elif (event.type == 'LEFTMOUSE' and event.value == 'RELEASE') or event.type == 'WINDOW_DEACTIVATE':
                self.can_mouse_rotate = False
            elif event.type == 'MOUSEMOVE' and self.can_mouse_rotate:
                diff_x = event.mouse_x - event.mouse_prev_x
                diff_y = event.mouse_y - event.mouse_prev_y
                if abs(diff_x) > abs(diff_y):
                    self.execute_rotation("ORBITLEFT", angle=diff_x * 0.002)
                else:
                    self.execute_rotation("ORBITDOWN", angle=diff_y * 0.002)
            elif event.type in ('RET', 'NUMPAD_ENTER'):
                ret_status = self.execute_export(context, False)
            elif event.type == 'ESC':
                ret_status = {'CANCELLED'}

            # make sure to finish preview, before ending the operator
            if ret_status.issubset({'CANCELLED', 'FINISHED'}):
                self.finish()

            return ret_status

        def invoke(self, context, event):
            # show preview or directly execute export
            if _get_scs_globals().export_scope == "selection" and _get_scs_globals().preview_export_selection:
                if len(self.get_objects_for_export()) == 0:
                    if len(bpy.context.selected_objects) > 0:
                        msg = "Selected objects are not part of any SCS Game Object!"
                    else:
                        msg = "Nothing selected!"
                    self.report({'ERROR'}, msg)
                    return {'FINISHED'}

                self.init()
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}

            return self.execute_export(context, True)

    class SCS_TOOLS_OT_ExportAnimAction(bpy.types.Operator):
        bl_label = "Export SCS Animation (PIA)"
        bl_idname = "scene.scs_tools_export_anim_action"
        bl_description = "Select directory and export SCS animation (PIA) to it."
        bl_options = {'INTERNAL'}

        index: IntProperty(
            name="Anim Index",
            default=False,
            options={'HIDDEN'}
        )

        directory: StringProperty(
            name="Export PIA Directory",
            subtype='DIR_PATH',
        )
        filename_ext = ".pia"
        filter_glob: StringProperty(default=str("*" + filename_ext), options={'HIDDEN'})

        @classmethod
        def poll(cls, context):
            active_obj = context.active_object
            return active_obj and active_obj.type == "ARMATURE" and _object_utils.get_scs_root(active_obj) is not None

        def execute(self, context):
            lprint("D " + self.bl_idname, report_errors=-1, report_warnings=-1)

            if not _path_utils.startswith(self.directory, _get_scs_globals().scs_project_path):
                message = "E Selected path is not inside SCS Project Base Path! Animation can't be exported to this directory."
                lprint(message)
                self.report({'ERROR'}, message[2:])
                return {'CANCELLED'}

            armature = context.active_object
            scs_root_obj = _object_utils.get_scs_root(armature)
            anim_inventory = scs_root_obj.scs_object_animation_inventory

            skeleton_filepath = _path_utils.get_skeleton_relative_filepath(armature, self.directory, scs_root_obj.name)

            if 0 <= self.index < len(anim_inventory):

                anim = anim_inventory[self.index]

                # check extension for EF format and properly assign it to name suffix
                ef_name_suffix = ""
                if _get_scs_globals().export_output_type == "EF":
                    ef_name_suffix = ".ef"

                _export.pia.export(scs_root_obj, armature, anim, self.directory, ef_name_suffix, skeleton_filepath)

            lprint("", report_errors=1, report_warnings=1)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            scs_project_path = _get_scs_globals().scs_project_path
            if scs_project_path not in self.directory:
                self.directory = _get_scs_globals().scs_project_path
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


class Paths:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_SelectProjectPath(bpy.types.Operator):
        """Operator for setting an absolute path to SCS Project Directory."""
        bl_label = "Select SCS Project Directory"
        bl_idname = "scene.scs_tools_select_project_path"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        directory: StringProperty(
            name="SCS Project Directory Path",
            description="SCS project directory path",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob: StringProperty(default="*.*", options={'HIDDEN'})

        def execute(self, context):
            """Set SCS project directory path."""
            scs_globals = _get_scs_globals()
            scs_globals.scs_project_path = self.directory
            # scs_globals.scs_project_path = _utils.relative_path(scs_globals.scs_project_path, self.directory)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            self.directory = _get_scs_globals().scs_project_path
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectShaderPresetsPath(bpy.types.Operator):
        """Operator for setting relative or absolute path to Shader Presets Library file."""
        bl_label = "Select Shader Presets Library File"
        bl_idname = "scene.scs_tools_select_shader_presets_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Shader Presets Library File",
            description="Shader Presets library relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.txt", options={'HIDDEN'})

        def execute(self, context):
            """Set Shader Presets library file path."""
            scs_globals = _get_scs_globals()
            scs_globals.shader_presets_filepath = self.filepath

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            filepath = _get_scs_globals().shader_presets_filepath
            if _path_utils.is_valid_shader_presets_library_path():
                self.filepath = _path_utils.get_abs_path(filepath, skip_mod_check=True)
            else:
                self.filepath = filepath
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectTriggerActionsLibPath(bpy.types.Operator):
        """Operator for setting relative path to Trigger actions file."""
        bl_label = "Select Trigger Actions File"
        bl_idname = "scene.scs_tools_select_trigger_actions_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Trigger Actions File",
            description="Trigger actions relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Sign directory path."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.trigger_actions_rel_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_trigger_actions_rel_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().trigger_actions_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectSignLibPath(bpy.types.Operator):
        """Operator for setting relative path to Sign Library file."""
        bl_label = "Select Sign Library File"
        bl_idname = "scene.scs_tools_select_sign_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Sign Library File",
            description="Sign library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Sign directory path."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.sign_library_rel_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_sign_library_rel_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().sign_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectSemaphoreLibPath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Semaphore Profile Library file."""
        bl_label = "Select Traffic Semaphore Profile Library File"
        bl_idname = "scene.scs_tools_select_semaphore_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Traffic Semaphore Profile Library File",
            description="Traffic Semaphore Profile library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Traffic Semaphore Profile library filepath."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.tsem_library_rel_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_tsem_library_rel_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().tsem_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectTrafficRulesLibPath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Rules Library file."""
        bl_label = "Select Traffic Rules Library File"
        bl_idname = "scene.scs_tools_select_traffic_rules_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Traffic Rules Library File",
            description="Traffic Rules library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Traffic Rules library filepath."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.traffic_rules_library_rel_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_traffic_rules_library_rel_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().traffic_rules_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectHookupLibPath(bpy.types.Operator):
        """Operator for setting path to Hookup files."""
        bl_label = "Select Hookup Library Directory"
        bl_idname = "scene.scs_tools_select_hookup_lib_path"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        directory: StringProperty(
            name="Hookup Library Directory Path",
            description="Hookup library directory path",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Hookup directory path."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.directory, scs_globals.scs_project_path):
                self.directory = _path_utils.relative_path(scs_globals.scs_project_path, self.directory)

            scs_globals.hookup_library_rel_path = self.directory
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            if _path_utils.is_valid_hookup_library_rel_path():
                self.directory = _path_utils.get_abs_path(_get_scs_globals().hookup_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectMatSubsLibPath(bpy.types.Operator):
        """Operator for setting path to Material Substance file."""
        bl_label = "Select Material Substance Library File"
        bl_idname = "scene.scs_tools_select_matsubs_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Material Substance Library File",
            description="Material Substance library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.db", options={'HIDDEN'})

        def execute(self, context):
            """Set Material Substance library filepath."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.matsubs_library_rel_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_matsubs_library_rel_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().matsubs_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectSunProfilesLibPath(bpy.types.Operator):
        """Operator for setting relative path to Material Substance shader files."""
        bl_label = "Select Sun Profiles Library File"
        bl_idname = "scene.scs_tools_select_sun_profiles_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        filepath: StringProperty(
            name="Sun Profiles Library File",
            description="Sun Profiles library relative/absolute file path",
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        def execute(self, context):
            """Set Material Substance library filepath."""
            scs_globals = _get_scs_globals()

            if _path_utils.startswith(self.filepath, scs_globals.scs_project_path):
                self.filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)

            scs_globals.sun_profiles_lib_path = self.filepath
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            if _path_utils.is_valid_sun_profiles_library_path():
                self.filepath = _path_utils.get_abs_path(_get_scs_globals().sun_profiles_lib_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_SelectDirInsideBase(bpy.types.Operator):
        """Operator for setting relative or absolute path to Global Export file."""
        bl_label = "Select Directory"
        bl_idname = "scene.scs_tools_select_dir_inside_base"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type: get_filebrowser_display_type()

        directory: StringProperty(
            name="Directory",
            description="Directory inside SCS Project Base path",
            subtype='DIR_PATH',
        )

        type: EnumProperty(
            name="Type",
            description="Type of selection",
            items=(
                ('DefaultExportPath', "DefaultExport", "", "NONE", 0),
                ('GameObjectExportPath', "GameObjectExport", "", "NONE", 1),
                ('GameObjectAnimExportPath', "GameObjectExport", "", "NONE", 2),
                ('SkeletonExportPath', "SkeletonExport", "", "NONE", 3),
            ),
            options={'HIDDEN'}
        )

        filter_glob: StringProperty(default="*.pim", options={'HIDDEN'})

        def execute(self, context):

            scs_globals = _get_scs_globals()

            if self.type == "DefaultExportPath":
                obj = context.scene.scs_props
                prop = "default_export_filepath"
            elif self.type == "GameObjectExportPath":
                obj = context.active_object.scs_props
                prop = "scs_root_object_export_filepath"
            elif self.type == "GameObjectAnimExportPath":
                obj = _object_utils.get_scs_root(context.active_object).scs_props
                prop = "scs_root_object_anim_export_filepath"
            else:
                obj = context.active_object.scs_props
                prop = "scs_skeleton_custom_export_dirpath"

            if _path_utils.startswith(self.directory, scs_globals.scs_project_path):
                setattr(obj, prop, _path_utils.relative_path(scs_globals.scs_project_path, self.directory))
            else:
                setattr(obj, prop, "//")
                self.report({'ERROR'}, "Selected path is not within SCS Project Base Path,\npath will be reset to SCS Project Base Path instead.")
                return {'CANCELLED'}

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            self.directory = _get_scs_globals().scs_project_path
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_ReloadLibrary(bpy.types.Operator):
        """Operator for reloading given library."""
        bl_label = "Reload"
        bl_idname = "scene.scs_tools_reload_library"
        bl_description = "Reloads library and updates it with any possible new entries."

        library_path_attr: StringProperty()

        def execute(self, context):
            scs_globals = _get_scs_globals()

            # if given library path attribute exists in globals then just rewrite it,
            # as this will trigger property update function which will take care of reloading library
            if hasattr(scs_globals, self.library_path_attr):
                setattr(scs_globals, self.library_path_attr, getattr(scs_globals, self.library_path_attr))
                self.report({'INFO'}, "Library updated!")
            else:
                self.report({'ERROR'}, "Unknown library, update aborted!")

            return {'FINISHED'}

    class SCS_TOOLS_OT_AddPathPreset(bpy.types.Operator, AddPresetBase):
        bl_label = "Add New Paths Preset"
        bl_idname = "scene.scs_tools_add_path_preset"
        bl_description = "Add or remove preset for SCS Project Base Path and rest of the libraries, to quickly switch between projects"
        preset_menu = "SCS_TOOLS_PT_PathSettingsPresets"

        # variable used for all preset values
        preset_defines = [
            "scs_globals = bpy.context.preferences.addons['io_scs_tools'].preferences.scs_globals"
        ]

        # properties to store in the preset
        preset_values = [
            "scs_globals.scs_project_path",
            "scs_globals.use_alternative_bases",
            "scs_globals.trigger_actions_rel_path",
            "scs_globals.trigger_actions_use_infixed",
            "scs_globals.sign_library_rel_path",
            "scs_globals.sign_library_use_infixed",
            "scs_globals.tsem_library_rel_path",
            "scs_globals.tsem_library_use_infixed",
            "scs_globals.traffic_rules_library_rel_path",
            "scs_globals.traffic_rules_library_use_infixed",
            "scs_globals.hookup_library_rel_path",
            "scs_globals.matsubs_library_rel_path",
            "scs_globals.shader_presets_filepath"
        ]

        # where to store the preset
        preset_subdir = "io_scs_tools/paths"


class Animation:
    """
    Wraper class for better navigation in file
    """

    class SCS_TOOLS_OT_IncreaseAnimationSteps(bpy.types.Operator):
        bl_label = "Increase Animation Steps"
        bl_idname = "scene.scs_tools_increase_animation_steps"
        # TODO: better description...
        bl_description = "Scales the entire animation 2x in length, but compensate for playback and export so the result stays the same..."

        def execute(self, context):
            lprint('D Increase Animation Steps...')
            scene = context.scene
            scene.use_preview_range = True

            if (scene.render.fps * 2) > 120:
                lprint('E %r value cannot be set over %s value!', ('FPS', 120))
            else:
                active_object = context.active_object
                action = active_object.animation_data.action
                scs_root_object = _object_utils.get_scs_root(active_object)
                # active_scs_animation = scs_root_object.scs_props.active_scs_animation
                inventory = scs_root_object.scs_object_animation_inventory
                # animation = inventory[active_scs_animation]

                # MOVE FRAMES
                # print_fcurve = 13
                for fcurve_i, fcurve in enumerate(action.fcurves):
                    # if fcurve_i == print_fcurve: print('fcurve: %r - %s' % (str(fcurve.data_path), str(fcurve.range())))
                    for keyframe_i, keyframe in enumerate(fcurve.keyframe_points):
                        # if fcurve_i == print_fcurve: print('  %i keyframe: %s' % (keyframe_i, str(keyframe.co)))

                        # OLD WAY OF INCREASING ACTION LENGTH FROM THE FIRST KEYFRAME
                        # start_frame = fcurve.range()[0]
                        # actual_frame = keyframe.co.x
                        # keyframe.co.x = ((actual_frame - start_frame) * 2) + start_frame

                        # NEW WAY - SIMPLE DOUBLING THE VALUES
                        keyframe.co.x *= 2
                    fcurve.update()

                    # PRINTOUTS
                    # print('  group: %r' % str(fcurve.group.name))
                    # for channel_i, channel in enumerate(fcurve.group.channels):
                    # print('    %i channel: %s - %s' % (channel_i, str(channel.data_path), str(channel.range())))
                    # for keyframe_i, keyframe in enumerate(channel.keyframe_points):
                    # print('      %i keyframe: %s' % (keyframe_i, str(keyframe.co)))

                # INCREASE GLOBAL RANGE
                scene.frame_start *= 2
                scene.frame_end *= 2

                # INCREASE PREVIEW RANGE
                scene.frame_preview_start *= 2
                scene.frame_preview_end *= 2

                # INCREASE END FRAME NUMBER IN ALL ANIMATIONS THAT USES THE ACTUAL ACTION
                for anim in inventory:
                    if anim.action == action.name:
                        anim.anim_start *= 2
                        anim.anim_end *= 2

                # INCREASE EXPORT STEP
                # print('anim_export_step: %s' % str(action.scs_props.anim_export_step))
                action.scs_props.anim_export_step *= 2

            return {'FINISHED'}

    class SCS_TOOLS_OT_DecreaseAnimationSteps(bpy.types.Operator):
        bl_label = "Decrease Animation Steps"
        bl_idname = "scene.scs_tools_decrease_animation_steps"
        # TODO: better description...
        bl_description = "Scales down the entire animation to its half in length, but compensate for playback and export so the result stays the " \
                         "same..."

        def execute(self, context):
            lprint('D Decrease Animation Steps...')
            scene = context.scene
            scene.use_preview_range = True
            action = context.active_object.animation_data.action

            if action.scs_props.anim_export_step == 1:
                lprint('E Cannot set lower value for %r than %i!', ('Export Step', 1))
            else:
                active_object = context.active_object
                scs_root_object = _object_utils.get_scs_root(active_object)
                # active_scs_animation = scs_root_object.scs_props.active_scs_animation
                inventory = scs_root_object.scs_object_animation_inventory
                # animation = inventory[active_scs_animation]

                # MOVE FRAMES
                # print_fcurve = 13
                for fcurve_i, fcurve in enumerate(action.fcurves):
                    # if fcurve_i == print_fcurve: print('fcurve: %r - %s' % (str(fcurve.data_path), str(fcurve.range())))
                    for keyframe_i, keyframe in enumerate(fcurve.keyframe_points):
                        # if fcurve_i == print_fcurve: print('  %i keyframe: %s' % (keyframe_i, str(keyframe.co)))

                        # OLD WAY OF INCREASING ACTION LENGTH FROM THE FIRST KEYFRAME
                        # start_frame = fcurve.range()[0]
                        # actual_frame = keyframe.co.x
                        # keyframe.co.x = ((actual_frame - start_frame) / 2) + start_frame

                        # NEW WAY - SIMPLE DOUBLING THE VALUES
                        keyframe.co.x /= 2
                    fcurve.update()

                    # ## PRINTOUTS
                    # print('  group: %r' % str(fcurve.group.name))
                    # for channel_i, channel in enumerate(fcurve.group.channels):
                    # print('    %i channel: %s - %s' % (channel_i, str(channel.data_path), str(channel.range())))
                    # for keyframe_i, keyframe in enumerate(channel.keyframe_points):
                    # print('      %i keyframe: %s' % (keyframe_i, str(keyframe.co)))

                # INCREASE GLOBAL RANGE
                scene.frame_start //= 2
                scene.frame_end //= 2

                # INCREASE PREVIEW RANGE
                scene.frame_preview_start //= 2
                scene.frame_preview_end //= 2

                # INCREASE END FRAME NUMBER IN ALL ANIMATIONS THAT USES THE ACTUAL ACTION
                for anim in inventory:
                    if anim.action == action.name:
                        anim.anim_start //= 2
                        anim.anim_end //= 2

                # INCREASE EXPORT STEP
                # print('anim_export_step: %s' % str(action.scs_props.anim_export_step))
                action.scs_props.anim_export_step //= 2

            return {'FINISHED'}


class ConversionHelper:
    """
    Wraper class for better navigation in file
    """

    class SCS_TOOLS_OT_CleanConversionRSRC(bpy.types.Operator):
        bl_label = "Clean RSRC"
        bl_idname = "scene.scs_tools_clean_conversion_rsrc"
        bl_description = "Cleans-up converted data inside of conversion tools (empties 'rsrc' folder & removes symbolic links)."

        def execute(self, context):

            main_path = _get_scs_globals().conv_hlpr_converters_path
            extra_mount_path = os.path.join(main_path, "extra_mount.txt")
            convert_cmd_path = os.path.join(main_path, "convert.cmd")
            rsrc_path = os.path.join(main_path, "rsrc")

            if not os.path.isfile(extra_mount_path) or not os.path.isfile(convert_cmd_path):
                self.report({'ERROR'}, "Conversion tools path is incorrect! Please fix it first.")
                return {'CANCELLED'}

            for root, dirs, files in os.walk(rsrc_path):
                for folder in dirs:
                    _path_utils.rmtree(root + os.sep + folder)
                for file in files:
                    os.remove(root + os.sep + file)

            # also remove symlinks created with blender tools
            for dir_entry in os.listdir(main_path):

                dir_entry_abs_path = os.path.join(main_path, dir_entry)
                if dir_entry.startswith("linked_bt_") and os.path.isdir(dir_entry_abs_path):
                    os.remove(dir_entry_abs_path)

            self.report({'INFO'}, "Successfully cleaned converted data in conversion tools folder!")
            return {'FINISHED'}

    class SCS_TOOLS_OT_AddConversionPath(bpy.types.Operator):
        bl_label = "Add Path"
        bl_idname = "scene.scs_tools_add_conversion_path"
        bl_description = "Adds new path to the stack of paths for conversion"

        directory: StringProperty(
            name="Directory",
            description="Any directory on file system",
            subtype='DIR_PATH',
        )

        def execute(self, context):
            scs_globals = _get_scs_globals()

            new_entry = scs_globals.conv_hlpr_custom_paths.add()
            new_entry.path = self.directory

            # always mark last/new one as active
            scs_globals.conv_hlpr_custom_paths_active = len(scs_globals.conv_hlpr_custom_paths) - 1

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            self.directory = _get_scs_globals().scs_project_path
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_RemoveConversionPath(bpy.types.Operator):
        bl_label = "Remove Path"
        bl_idname = "scene.scs_tools_remove_conversion_path"
        bl_description = "Removes path from the stack of paths for conversion"

        def execute(self, context):
            scs_globals = _get_scs_globals()

            i = scs_globals.conv_hlpr_custom_paths_active
            scs_globals.conv_hlpr_custom_paths.remove(i)

            if scs_globals.conv_hlpr_custom_paths_active > 0:
                scs_globals.conv_hlpr_custom_paths_active -= 1

            return {'FINISHED'}

    class SCS_TOOLS_OT_OrderConversionPath(bpy.types.Operator):
        bl_label = "Order Path"
        bl_idname = "scene.scs_tools_order_conversion_path"
        bl_description = "Change order for the current path"

        move_up: BoolProperty(default=True)

        def execute(self, context):
            scs_globals = _get_scs_globals()

            i = scs_globals.conv_hlpr_custom_paths_active
            other_i = i - 1 if self.move_up else i + 1

            if other_i < 0 or other_i >= len(scs_globals.conv_hlpr_custom_paths):
                self.report({'INFO'}, "Can't order, already on %s!" % ("top" if self.move_up else "bottom"))
                return {'FINISHED'}

            # get paths
            path = scs_globals.conv_hlpr_custom_paths[i].path
            other_path = scs_globals.conv_hlpr_custom_paths[other_i].path

            # switch paths
            scs_globals.conv_hlpr_custom_paths[i].path = other_path
            scs_globals.conv_hlpr_custom_paths[other_i].path = path

            # fix active index
            scs_globals.conv_hlpr_custom_paths_active = other_i

            return {'FINISHED'}

    class SCS_TOOLS_OT_RunConversion(bpy.types.Operator):
        bl_label = "Run Conversion"
        bl_idname = "scene.scs_tools_run_conversion"
        bl_description = "Dry run of conversion tools without managing extra_mount.txt file (Should not be used from UI)"

        def execute(self, context):

            main_path = _get_scs_globals().conv_hlpr_converters_path

            if platform == "linux":  # Linux

                if os.system("command -v wineconsole") == 0:
                    command = ["wineconsole " + os.path.join(main_path, "convert.cmd")]
                else:
                    self.report({'ERROR'}, "Conversion aborted! Please install WINE, it's required to run conversion tools on Linux!")
                    return {'CANCELLED'}

            elif platform == "darwin":  # Mac OS X

                # NOTE: we are assuming that user installed wine as it's written on: https://wiki.winehq.org/MacOS
                wineconsole_path = "/Applications/Wine Stable.app/Contents/Resources/wine/bin/wineconsole"

                if os.system("command -v wineconsole") == 0:

                    command = ["wineconsole " + os.path.join(main_path, "convert.cmd")]

                elif os.path.isfile(wineconsole_path):

                    wineconsole_path = wineconsole_path.replace(" ", "\\ ")  # NOTE: Mac OS bash needs space escaping otherwise it doesn't work
                    command = [wineconsole_path + " " + os.path.join(main_path, "convert.cmd")]

                else:
                    self.report({'ERROR'}, "Conversion aborted!\n"
                                           "Please install stable version of Wine application from 'winehq.org',\n"
                                           "it's required to run conversion tools on Mac OS X!")
                    return {'CANCELLED'}

            elif platform == "win32":  # Windows

                command = 'cmd /C ""' + os.path.join(main_path, "convert.cmd") + '""'
                command = command.replace("\\", "/")

            else:

                self.report({'ERROR'}, "Unsupported OS type! Make sure you are running either Mac OS X, Linux or Windows!")
                return {'CANCELLED'}

            # try to run conversion tools
            if subprocess.call(command, shell=True) == 0:
                self.report({'INFO'}, "Conversion done!")
            else:
                self.report({'ERROR'}, "Can't run conversion tools or there were errors by converting!")

            return {'FINISHED'}

    class SCS_TOOLS_OT_ConvertCurrentBase(bpy.types.Operator):
        bl_label = "Convert Current Base"
        bl_idname = "scene.scs_tools_convert_current_base"
        bl_description = "Converts current SCS Base project (the one which is currently used by SCS Blender Tools) to binary files ready for packing."

        def execute(self, context):

            main_path = _get_scs_globals().conv_hlpr_converters_path
            extra_mount_path = os.path.join(main_path, "extra_mount.txt")
            convert_cmd_path = os.path.join(main_path, "convert.cmd")

            if not os.path.isfile(extra_mount_path) or not os.path.isfile(convert_cmd_path):
                self.report({'ERROR'}, "Conversion tools path is incorrect! Please fix it first.")
                return {'CANCELLED'}

            if not os.path.isdir(_get_scs_globals().scs_project_path):
                self.report({'ERROR'}, "SCS Project Base Path doesn't exists! Aborting Conversion!")
                return {'CANCELLED'}

            link_hash = "linked_bt_" + sha1(str.encode(_get_scs_globals().scs_project_path)).hexdigest()
            linked_path = os.path.join(main_path, link_hash)
            _path_utils.ensure_symlink(_get_scs_globals().scs_project_path, linked_path)

            with open(extra_mount_path, mode="w", encoding="utf8") as f:
                f.write(link_hash)

            return ConversionHelper.SCS_TOOLS_OT_RunConversion.execute(self, context)

    class SCS_TOOLS_OT_ConvertCustomPaths(bpy.types.Operator):
        bl_label = "Convert Custom Paths"
        bl_idname = "scene.scs_tools_convert_custom_paths"
        bl_description = "Converts all paths given in Custom Paths list (order is the same as they appear in the list)"

        include_current_project: BoolProperty(
            default=False
        )

        @classmethod
        def poll(cls, context):
            return len(_get_scs_globals().conv_hlpr_custom_paths) > 0

        def execute(self, context):

            main_path = _get_scs_globals().conv_hlpr_converters_path
            extra_mount_path = os.path.join(main_path, "extra_mount.txt")
            convert_cmd_path = os.path.join(main_path, "convert.cmd")

            if not os.path.isfile(extra_mount_path) or not os.path.isfile(convert_cmd_path):
                self.report({'ERROR'}, "Conversion tools path is incorrect! Please fix it first.")
                return {'CANCELLED'}

            with open(extra_mount_path, mode="w", encoding="utf8") as f:

                for path_entry in _get_scs_globals().conv_hlpr_custom_paths:

                    path = path_entry.path.rstrip(os.sep)

                    if not os.path.isdir(path):
                        self.report({'WARNING'}, "None existing custom paths detected, they were ignored!")
                        continue

                    link_hash = "linked_bt_" + sha1(str.encode(path)).hexdigest()
                    linked_path = os.path.join(main_path, link_hash)
                    _path_utils.ensure_symlink(path, linked_path)

                    f.write(link_hash)
                    f.write("\r\n")

                if self.include_current_project:

                    if os.path.isdir(_get_scs_globals().scs_project_path):

                        link_hash = "linked_bt_" + sha1(str.encode(_get_scs_globals().scs_project_path)).hexdigest()
                        linked_path = os.path.join(main_path, link_hash)
                        _path_utils.ensure_symlink(_get_scs_globals().scs_project_path, linked_path)
                        f.write(link_hash)

                    else:
                        self.report({'WARNING'}, "None existing SCS Project Base Path detected, ignoring it!")

            return ConversionHelper.SCS_TOOLS_OT_RunConversion.execute(self, context)

    class SCS_TOOLS_OT_ConvertAllPaths(bpy.types.Operator):
        bl_label = "Convert All"
        bl_idname = "scene.scs_tools_convert_all_paths"
        bl_description = "Converts all paths given in Custom Paths list + current SCS Project Base"

        def __init__(self):
            self.include_current_project = True

        @classmethod
        def poll(cls, context):
            return len(_get_scs_globals().conv_hlpr_custom_paths) > 0

        def execute(self, context):
            return ConversionHelper.SCS_TOOLS_OT_ConvertCustomPaths.execute(self, context)

    class SCS_TOOLS_OT_FindGameModFolder(bpy.types.Operator):
        bl_label = "Search SCS Game 'mod' Folder"
        bl_idname = "scene.scs_tools_find_game_mod_folder"
        bl_description = "Search for given SCS game 'mod' folder and set it as mod destination"

        game: EnumProperty(
            items=(
                ("Euro Truck Simulator 2", "Euro Truck Simulator 2", ""),
                ("American Truck Simulator", "American Truck Simulator", "")
            )
        )

        @staticmethod
        def ensure_mod_folder(game_home_path):
            """Gets game home folder, creates "mod" directory inside if not yet present and returns full path to mod folder.

            :param game_home_path: path to game home folder
            :type game_home_path: str
            :return: full path to game mod folder
            :rtype: str
            """

            game_mod_path = game_home_path + "/mod"
            if not os.path.isdir(game_mod_path):
                os.mkdir(game_mod_path)

            return os.path.normpath(game_mod_path)

        @staticmethod
        def get_platform_depended_game_path():
            """Gets platform dependent game path as root directory for storing SCS games user data.

            :return: game path or empty string if OS is neither Windows, Linux or Mac OS X
            :rtype: str
            """

            game_path = ""

            if platform == "linux":  # Linux

                game_path = os.path.expanduser("~/.local/share")

            elif platform == "darwin":  # Mac OS X

                game_path = os.path.expanduser("~/Library/Application Support")

            elif platform == "win32":  # Windows

                try:
                    import winreg

                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:

                        personal = winreg.QueryValueEx(key, "Personal")
                        game_path = str(personal[0])

                except OSError:
                    import traceback

                    trace_str = traceback.format_exc().replace("\n", "\n\t   ")
                    lprint("E Error while looking for My Documents in registry:\n\t   %s",
                           (trace_str,),
                           report_errors=1,
                           report_warnings=1)

            return game_path

        def execute(self, context):

            scs_globals = _get_scs_globals()

            possible_game_homes = (
                os.path.expanduser("~"),  # Windows like installation on Linux or Mac OS X
                self.get_platform_depended_game_path(),
            )

            for possible_game_home in possible_game_homes:
                game_home_path = os.path.join(possible_game_home, self.game)
                if os.path.isdir(game_home_path):
                    scs_globals.conv_hlpr_mod_destination = self.ensure_mod_folder(game_home_path)
                    return {'FINISHED'}

            self.report({'WARNING'}, "Could not find '" + self.game + "' mod folder")
            return {'CANCELLED'}

        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)

        def draw(self, context):

            layout = self.layout

            layout.prop(self, "game", expand=True)

    class SCS_TOOLS_OT_RunPacking(bpy.types.Operator):
        bl_label = "Run Packing"
        bl_idname = "scene.scs_tools_run_packing"
        bl_description = "Pack converted sources to mod package and copy it to mod destination path.\n" \
                         "Depending on auto settings this operator will also execute clean, export and convert before packing."

        @staticmethod
        def get_zipfile_path(zipfile_originpath, abs_path):
            """Extract zipfile path, do conversion to proper slashes as zipfile namelist
            is returning only normal slashes even on windows and as last remove leading slash
            as zipfile namelist again doesn't have it.

            :param zipfile_originpath: path to directory where root of zipfile is (generally this should be some parent folder of second argument)
            :type zipfile_originpath: str
            :param abs_path: absolute path of file for which zipfile path shall be returned
            :type abs_path: str
            :return: correct zipfile path for given absolute path relative to irigin path
            :rtype: str
            """
            return abs_path.replace(zipfile_originpath, "").replace("\\", "/").lstrip("/")

        @classmethod
        def poll(cls, context):
            return context.scene is not None

        def execute(self, context):

            scs_globals = _get_scs_globals()

            main_path = scs_globals.conv_hlpr_converters_path
            extra_mount_path = os.path.join(main_path, "extra_mount.txt")
            convert_cmd_path = os.path.join(main_path, "convert.cmd")
            rsrc_path = os.path.join(main_path, "rsrc")

            if not os.path.isfile(extra_mount_path) or not os.path.isfile(convert_cmd_path) or not os.path.isdir(rsrc_path):
                self.report({'ERROR'}, "Conversion tools path is incorrect! Please fix it first.")
                return {'CANCELLED'}

            if scs_globals.conv_hlpr_clean_on_packing:

                try:
                    bpy.ops.scene.scs_tools_clean_conversion_rsrc()
                except RuntimeError as e:
                    self.report({'ERROR'}, e.args[0])
                    return {'CANCELLED'}

            if scs_globals.conv_hlpr_export_on_packing:

                try:
                    bpy.ops.scs_tools.export_pim()
                except RuntimeError as e:
                    self.report({'ERROR'}, e.args[0])
                    return {'CANCELLED'}

            if scs_globals.conv_hlpr_convert_on_packing:

                try:
                    if scs_globals.conv_hlpr_use_custom_paths and len(scs_globals.conv_hlpr_custom_paths) > 0:
                        bpy.ops.scene.scs_tools_convert_custom_paths(include_current_project=True)
                    else:
                        bpy.ops.scene.scs_tools_convert_current_base()
                except RuntimeError as e:
                    self.report({'ERROR'}, e.args[0])
                    return {'CANCELLED'}

            mod_path = scs_globals.conv_hlpr_mod_destination
            mod_name = scs_globals.conv_hlpr_mod_name

            if not os.path.isdir(mod_path):
                self.report({'ERROR'}, "None existing mod destination path, packing aborted!")
                return {'CANCELLED'}

            mod_filepath = os.path.join(mod_path, mod_name)

            # make sure mod file name ends with proper extension: ZIP
            if not mod_name.endswith(".zip"):
                mod_filepath += ".zip"

            # delete mod folder if previously no archive option was used
            mod_filepath_as_dir = mod_filepath[:-4]
            if os.path.isdir(mod_filepath_as_dir):
                _path_utils.rmtree(mod_filepath_as_dir)

            # make sure previous ZIP file is not present
            if os.path.isfile(mod_filepath):
                os.remove(mod_filepath)

            # do copy or zipping
            if scs_globals.conv_hlpr_mod_compression == _CONV_HLPR_consts.NoZip:

                for converted_dir in os.listdir(rsrc_path):  # use old conversion tools behaviour and pack everything that is in rsrc

                    curr_dir = os.path.join(os.path.join(rsrc_path, converted_dir), "@cache")
                    if not os.path.isdir(curr_dir):
                        continue

                    _path_utils.copytree(curr_dir, mod_filepath_as_dir)

                self.report({'INFO'}, "Packing done, mod copied to: '%s'" % mod_filepath_as_dir)

            else:

                from zipfile import ZipFile

                with ZipFile(mod_filepath, 'w') as myzip:

                    for converted_dir in os.listdir(rsrc_path):  # use old conversion tools behaviour and pack everything that is in rsrc

                        curr_dir = os.path.join(os.path.join(rsrc_path, converted_dir), "@cache")
                        if not os.path.isdir(curr_dir):
                            continue

                        for root, dirs, files in os.walk(curr_dir):

                            # ignore packing if no files in current dir
                            if len(files) <= 0:
                                continue

                            # write directories to zip
                            for directory in dirs:

                                abs_dir = os.path.join(root, directory)
                                archive_dir = self.get_zipfile_path(curr_dir, abs_dir)

                                if archive_dir + "/" in myzip.namelist():
                                    lprint("D Archive name %r already exists, ignoring it!" % archive_dir)
                                    continue

                                myzip.write(abs_dir, archive_dir, compress_type=int(scs_globals.conv_hlpr_mod_compression))

                            # write files to zip
                            for file in files:

                                abs_file = os.path.join(root, file)
                                archive_file = self.get_zipfile_path(curr_dir, abs_file)

                                if archive_file in myzip.namelist():
                                    lprint("D Archive name %r already exists, ignoring it!" % archive_file)
                                    continue

                                myzip.write(abs_file, archive_file, compress_type=int(scs_globals.conv_hlpr_mod_compression))

                self.report({'INFO'}, "Packing done, mod packed to: '%s'" % mod_filepath)

            return {'FINISHED'}


class Log:
    """
    Wraper class for better navigation in file
    """

    class SCS_TOOLS_OT_CopyLogToClipboard(bpy.types.Operator):
        bl_label = "Copy BT Log To Clipboard"
        bl_idname = "scene.scs_tools_copy_log_to_clipboard"
        bl_description = "Copies whole Blender Tools log to clipboard (log was captured since Blender startup)."

        def execute(self, context):
            from io_scs_tools.utils.printout import get_log

            context.window_manager.clipboard = get_log()

            self.report({'INFO'}, "Blender Tools log copied to clipboard!")
            return {'FINISHED'}


class PaintjobTools:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_ImportFromDataSII(bpy.types.Operator):
        bl_label = "Import SCS Vehicle From data.sii"
        bl_idname = "scene.scs_tools_import_from_data_sii"
        bl_description = ("Import all models having paintable parts of a vehicle (including upgrades)"
                          "from choosen '/def/vehicle/<vehicle_type>/<brand.model>/data.sii' file.")
        bl_options = set()

        directory: StringProperty(
            name="Import Vehicle",
            subtype='DIR_PATH',
        )
        filepath: StringProperty(
            name="Vehicle 'data.sii' filepath",
            description="File path to vehicle 'data.sii",
            subtype='FILE_PATH',
        )
        filter_glob: StringProperty(default="*.sii", options={'HIDDEN'})

        hide_collections: BoolProperty(
            name="Hide collections after import",
            description="Should collections be hidden or shown after import?",
            default=False
        )

        vehicle_type = _PT_consts.VehicleTypes.NONE
        start_time = None  # saving start time when initialize is called

        # saving old settings from scs globals
        old_import_pis = None
        old_import_pia = None
        old_import_pic = None
        old_import_use_welding = None
        old_scs_project_path = None

        @staticmethod
        def gather_model_paths(dir_path, unit_type, one_of_props):
            """Checks all SII files from combine given base_path & sub_dir and gathers model paths from first unit instance.
            Model path is taken from first found one of property inside unit instance.
            If instance is not of given type, then empty set is returned.

            :param dir_path: absolute directory path from which SII files should be search for model paths
            :type dir_path: str
            :param unit_type: type of the unit we are searching for in SII
            :type unit_type: str
            :param one_of_props: properties which are carrying model paths; algorithm always uses first found
            :type one_of_props: iterable
            :return: dictonary of found model paths where key is unique path and value for it is list of SII files where model was referenced from
            :rtype: dict[str,list[str]]
            """

            model_paths = {}

            if not os.path.isdir(dir_path):
                return model_paths

            for dir_file in os.listdir(dir_path):

                curr_path = _path_utils.readable_norm(os.path.join(dir_path, dir_file))

                if not os.path.isfile(curr_path):
                    continue

                if not curr_path.endswith(".sii"):
                    continue

                file_sii_container = _sii_container.get_data_from_file(curr_path)

                if not _sii_container.has_valid_unit_instance(file_sii_container, unit_type=unit_type, one_of_props=one_of_props):
                    lprint("D Validation failed on SII: %r", (_path_utils.readable_norm(curr_path),))
                    continue

                model_prop = None
                for prop in one_of_props:
                    model_prop = _sii_container.get_unit_property(file_sii_container, prop)

                    if model_prop is not None:
                        break

                if model_prop is None:
                    lprint("E Model can not be extracted from SII: %r", (_path_utils.readable_norm(curr_path),))
                    continue

                if model_prop[:-4] not in model_paths:
                    model_paths[model_prop[:-4]] = set()

                model_paths[model_prop[:-4]].add(curr_path)

            return model_paths

        @staticmethod
        def import_and_clean_model(context, project_path, model_path):
            """Imports model from given model absolute path and removes all useless none paintable stuff.
            If PIT file from given model doesn't have any truckpaint material, nothing is imported and None is returned.
            If no mesh remains in the model after cleaning, whole SCS Object is removed and None is returned.

            :param context: blender context used in PIX importing
            :type context: bpy.types.Context
            :param project_path: project path that will be use as temporary SCS Project Path
            :type project_path: str
            :param model_path: absolute path to the model which should be imported
            :type model_path: str
            :return: SCS Root object of imported model
            :rtype: bpy.types.Object
            """

            # ignore models without pit
            if not os.path.isfile(model_path + ".pit"):
                return None

            # load pit to search for truckpaint
            pit_container = _pix_container.get_data_from_file(model_path + ".pit", ' ' * 4)
            look = None
            for section in pit_container:
                if section.type == "Look":
                    look = section
                    break

            # ignore models with invalid pit (no look = invalid pit)
            if not look:
                return None

            # ignore models without truckpaint material
            for mat_sec in look.get_sections("Material"):
                if "eut2.truckpaint" in mat_sec.get_prop_value("Effect"):
                    break
            else:  # no truckpaint found, ignore this model
                return None

            # internally change project path for the sake of texture loading, path will be reset in finalize method call
            _get_scs_globals()["scs_project_path"] = project_path

            # import model
            _get_scs_globals().import_in_progress = True
            _pix_import.load(context, model_path, suppress_reports=True)
            _get_scs_globals().import_in_progress = False

            curr_scs_root = context.active_object

            # remove useless stuff (none truckpaint meshes & all locators except model locators without hookup)
            mesh_obj_count = 0
            removed_mesh_obj_count = 0
            for obj in curr_scs_root.children:

                remove_object = False

                if obj.type == "MESH":

                    mesh_obj_count += 1

                    if len(obj.material_slots) > 0 and obj.material_slots[0].material:
                        if not obj.material_slots[0].material.scs_props.mat_effect_name.startswith("eut2.truckpaint"):
                            remove_object = True
                            removed_mesh_obj_count += 1
                    else:
                        remove_object = True
                        removed_mesh_obj_count += 1

                elif obj.type == "EMPTY" and obj.scs_props.empty_object_type == "Locator":

                    if obj.scs_props.locator_type == "Model":
                        if obj.scs_props.locator_model_hookup != "":
                            remove_object = True
                    else:
                        remove_object = True

                if remove_object:
                    bpy.data.objects.remove(obj, do_unlink=True)

            # if no mesh has left inside the model, then remove everything
            if removed_mesh_obj_count >= mesh_obj_count:
                for obj in curr_scs_root.children:
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.objects.remove(curr_scs_root, do_unlink=True)
                curr_scs_root = None

            return curr_scs_root

        @staticmethod
        def add_model_to_collection(scs_root, model_type, model_name, linked_to_defs=set()):
            """Adds model to collection so it can be distinguished amongs all other models.

            :param scs_root: blender object representing SCS Root
            :type scs_root: bpy.types.Object
            :param model_type: type of the model (chassis, cabin, upgrade)
            :type model_type: str
            :param model_name: name of the model
            :type model_name: str
            :param linked_to_defs: set of the sii file paths where this model was defined
            :type linked_to_defs: set[str]
            """

            used_variants_by_linked_defs = set()  # stores all variants that are used by linked sii definitions

            # collect used variants for all definitions
            for path in linked_to_defs:

                sii_container = _sii_container.get_data_from_file(path)
                variant = _sii_container.get_unit_property(sii_container, "variant")

                if variant is not None:
                    used_variants_by_linked_defs.add(variant.lower())
                else:  # if no variant specified "default" is used by game, so add it to our set
                    used_variants_by_linked_defs.add("default")

            # create collections per variant
            for i, variant in enumerate(scs_root.scs_object_variant_inventory):

                variant_name = variant.name.lower()

                # do not create collections for unused variants
                if variant_name not in used_variants_by_linked_defs:
                    continue

                bpy.ops.object.select_all(action="DESELECT")

                # operator searches for scs root from active object, so make sure context will be correct
                with bpy.context.temp_override(active_object=scs_root):
                    bpy.ops.object.scs_tools_de_select_objects_with_variant(select_type=_OP_consts.SelectionType.select, variant_index=i)

                collection_name = model_type + " | " + model_name + " | " + variant_name
                collection = bpy.data.collections.new(collection_name)
                mesh_objects_count = 0
                for obj in scs_root.children:

                    if not obj.select_get():
                        continue

                    if obj.type == "MESH":
                        mesh_objects_count += 1

                    collection.objects.link(obj)

                # do not create collections for variant if no mesh objects inside
                if mesh_objects_count <= 0:
                    bpy.data.collections.remove(collection, do_unlink=True)
                    continue

                collection[_PT_consts.model_variant_prop] = variant_name
                collection[_PT_consts.model_refs_to_sii] = list(linked_to_defs)

                # create new layer collection to make our collection visible in outliner
                bpy.context.view_layer.layer_collection.collection.children.link(collection)

        @staticmethod
        def update_model_paths_dict(models_paths_dict, curr_models):
            """Extends given dictonary with models given by second argument.

            :param models_paths_dict: already collected model SII references where key is model path and value is existing list of SII references
            :type models_paths_dict: dict[str|list[str]]
            :param curr_models: current model SII references where key is model path and value is list of SII references
            :type curr_models: dict[str|list[str]]
            """
            for curr_model in curr_models:
                if curr_model in models_paths_dict:
                    models_paths_dict[curr_model].update(curr_models[curr_model])
                else:
                    models_paths_dict[curr_model] = curr_models[curr_model]

        def initalize(self):
            """Initilize scs globals with custom import settings, as we don't nened animations, welding, collisions.
            """

            scs_globals = _get_scs_globals()

            self.old_import_pis = scs_globals.import_pis_file
            self.old_import_pia = scs_globals.import_pia_file
            self.old_import_pic = scs_globals.import_pic_file
            self.old_import_use_welding = scs_globals.import_use_welding
            self.old_scs_project_path = scs_globals.scs_project_path

            self.start_time = time()

            scs_globals.import_pis_file = False
            scs_globals.import_pia_file = False
            scs_globals.import_pic_file = False
            scs_globals.import_use_welding = False

            self.vehicle_type = _PT_consts.VehicleTypes.NONE

        def finalize(self):
            """Restore scs globals settings to the state they were before.
            """

            scs_globals = _get_scs_globals()

            scs_globals.import_pis_file = self.old_import_pis
            scs_globals.import_pia_file = self.old_import_pia
            scs_globals.import_pic_file = self.old_import_pic
            scs_globals.import_use_welding = self.old_import_use_welding
            scs_globals["scs_project_path"] = self.old_scs_project_path  # set internally so initialization is not triggered

            lprint("\nI Import from 'data.sii' took: %0.3f sec" % (time() - self.start_time), report_errors=True, report_warnings=True)

        def execute(self, context):

            self.initalize()

            dir_path = self.directory
            data_sii_path = self.filepath
            data_sii_container = _sii_container.get_data_from_file(data_sii_path)

            # initial checkups
            if _sii_container.has_valid_unit_instance(data_sii_container, unit_type="accessory_truck_data", req_props=("fallback",)):
                self.vehicle_type = _PT_consts.VehicleTypes.TRUCK
            elif _sii_container.has_valid_unit_instance(data_sii_container, unit_type="accessory_trailer_data", req_props=("info",)):
                self.vehicle_type = _PT_consts.VehicleTypes.TRAILER
            else:
                message = "Chosen file is not a valid vehicle 'data.sii' file!"
                lprint("E " + message)
                self.report({'ERROR'}, message)
                self.finalize()
                return {'CANCELLED'}

            ##################################
            #
            # 1. collect all possible project paths
            #
            ##################################

            # first find path of whole game project
            game_project_path = dir_path
            for _ in range(0, 4):  # we can simply go 4 dirs up, as def has to be properly placed /def/vehicle/<vehicle_type>/<brand.name>
                game_project_path = _path_utils.readable_norm(os.path.join(game_project_path, os.pardir))

            vehicle_sub_dir = os.path.relpath(dir_path, game_project_path)
            game_project_path = os.path.join(game_project_path, os.pardir)

            # if data.sii was inside dlc or mod we have to go up once more in filesystem level
            if os.path.basename(game_project_path).startswith("dlc_") or os.path.basename(game_project_path).startswith("mod_"):
                game_project_path = os.path.join(game_project_path, os.pardir)

            # now as we have game project path, let's do real collecting
            project_paths = _path_utils.get_projects_paths(game_project_path)

            # sort project paths in reverse to make sure base will be searched as last
            project_paths = sorted(project_paths, reverse=True)

            lprint("S Project paths (%s):" % len(project_paths))
            for path in project_paths:
                lprint("S %s" % _path_utils.readable_norm(path))

            ##################################
            #
            # 2. import vehicle models
            #
            ##################################

            # collect all models paths for vehicle chassis, cabins and possible trailer body
            vehicle_model_paths = {}  # holds list of SII files that each model was referenced from {KEY: model path, VALUE: list of SII paths}
            for project_path in project_paths:

                vehicle_def_dirpath = os.path.join(project_path, vehicle_sub_dir)

                target_dirpath = os.path.join(vehicle_def_dirpath, "chassis")
                curr_models = self.gather_model_paths(target_dirpath, "accessory_chassis_data", ("detail_model", "model"))
                self.update_model_paths_dict(vehicle_model_paths, curr_models)

                if self.vehicle_type == _PT_consts.VehicleTypes.TRUCK:

                    target_dirpath = os.path.join(vehicle_def_dirpath, "cabin")
                    curr_models = self.gather_model_paths(target_dirpath, "accessory_cabin_data", ("detail_model", "model"))
                    self.update_model_paths_dict(vehicle_model_paths, curr_models)

                elif self.vehicle_type == _PT_consts.VehicleTypes.TRAILER:

                    target_dirpath = os.path.join(vehicle_def_dirpath, "body")
                    curr_models = self.gather_model_paths(target_dirpath, "accessory_trailer_body_data", ("detail_model", "model"))
                    self.update_model_paths_dict(vehicle_model_paths, curr_models)

            lprint("S Vehicle Paths:\n%r" % vehicle_model_paths)

            # import and properly collection imported models
            possible_upgrade_locators = {}  # dictionary holding all locators that can be used as candidates for upgrades positioning
            already_imported = set()  # set holding imported path of already imported model, to avoid double importing
            multiple_project_vehicle_models = set()  # set of model paths found in multiple projects (for reporting purposes)
            vehicle_import_count = 0  # counter for number of properly imported vehicle models
            for project_path in project_paths:

                for vehicle_model_path in vehicle_model_paths:

                    model_path = os.path.join(project_path, vehicle_model_path.lstrip("/"))

                    # initial checks
                    if not os.path.isfile(model_path + ".pim"):
                        continue

                    if vehicle_model_path in already_imported:
                        multiple_project_vehicle_models.add(vehicle_model_path)
                        continue

                    already_imported.add(vehicle_model_path)

                    # import model
                    curr_vehicle_scs_root = self.import_and_clean_model(context, project_path, model_path)

                    # truck did not have any paintable parts, go to next
                    if curr_vehicle_scs_root is None:
                        continue

                    # collect all locators as candidates for being used for upgrades positioning
                    for obj in curr_vehicle_scs_root.children:

                        if obj.type != "EMPTY" or obj.scs_props.empty_object_type != "Locator":
                            continue

                        possible_upgrade_locators[obj.name] = obj

                    # put imported model into it's own collections per variant
                    self.add_model_to_collection(curr_vehicle_scs_root,
                                                 self.vehicle_type,
                                                 os.path.basename(vehicle_model_path),
                                                 vehicle_model_paths[vehicle_model_path])

                    # update the import count
                    vehicle_import_count = vehicle_import_count + 1

            # if none vehicle models were properly imported it makes no sense to go forward on upgrades
            if vehicle_import_count <= 0:
                message = "No vehicle models imported, either none exist or they are corrupted or they are missing 'truckpaint' material!"
                lprint("E " + message)
                self.report({"ERROR"}, message)
                self.finalize()
                return {"CANCELLED"}

            ##################################
            #
            # 3. import upgrades
            #
            ##################################

            # collect all upgrade models, by listing all upgrades directories in all projects for this vehicle
            upgrade_model_paths = {}  # model paths dictionary {key: upgrade type (eg "f_intake_cab"); value: set of model paths for this upgrade}
            for project_path in project_paths:  # collect any possible upgrade over all projects

                vehicle_accessory_def_dirpath = os.path.join(project_path, vehicle_sub_dir)
                vehicle_accessory_def_dirpath = os.path.join(vehicle_accessory_def_dirpath, "accessory")

                # if current project path doesn't have accessories defined just skip it
                if not os.path.isdir(vehicle_accessory_def_dirpath):
                    continue

                for upgrade_type in os.listdir(vehicle_accessory_def_dirpath):

                    # ignore files
                    if not os.path.isdir(os.path.join(vehicle_accessory_def_dirpath, upgrade_type)):
                        continue

                    if upgrade_type not in upgrade_model_paths:
                        upgrade_model_paths[upgrade_type] = {}

                    target_dirpath = os.path.join(vehicle_accessory_def_dirpath, upgrade_type)

                    for unit_type in ("accessory_addon_data", "accessory_addon_tank_data"):
                        curr_models = self.gather_model_paths(target_dirpath, unit_type, ("exterior_model",))
                        self.update_model_paths_dict(upgrade_model_paths[upgrade_type], curr_models)

                    if len(upgrade_model_paths[upgrade_type]) <= 0:  # if no models for upgrade, remove set also
                        del upgrade_model_paths[upgrade_type]

            # import models, position them properly and put them to collections
            already_imported = set()  # set holding imported path of already imported model, to avoid double importing
            multiple_project_upgrade_models = set()  # set of model paths found in multiple projects (for reporting purposes)
            for project_path in project_paths:
                for upgrade_type in upgrade_model_paths:

                    for upgrade_model_path in upgrade_model_paths[upgrade_type]:

                        model_path = os.path.join(project_path, upgrade_model_path.lstrip("/"))

                        # initial checks
                        if not os.path.isfile(model_path + ".pim"):
                            continue

                        # construct key for checking already imported models by same type of upgrade
                        model_path_key = upgrade_type + " | " + upgrade_model_path

                        if model_path_key in already_imported:
                            multiple_project_upgrade_models.add(model_path_key)
                            continue

                        already_imported.add(model_path_key)

                        # import model
                        curr_upgrade_scs_root = self.import_and_clean_model(context, project_path, model_path)

                        if curr_upgrade_scs_root is None:  # everything was removed, so prevent collection creation etc...
                            continue

                        # put imported model into it's own collections
                        self.add_model_to_collection(curr_upgrade_scs_root,
                                                     upgrade_type,
                                                     os.path.basename(upgrade_model_path),
                                                     upgrade_model_paths[upgrade_type][upgrade_model_path])

                        # find upgrade locator by prefix & position upgrade by locator aka make parent on it
                        upgrade_locator = None
                        for locator_name in possible_upgrade_locators:

                            if not locator_name.startswith(upgrade_type):
                                continue

                            # Now we are trying to find "perfect" match, which is found,
                            # when matched prefixed upgrade locator is also assigned to at least one collection.
                            # This way we eliminate locators that are in variants
                            # not used by any chassis, cabin or trailer body of our vehicle.
                            # However cases involving "suitable_for" fields are not covered here!

                            if upgrade_locator is None:
                                upgrade_locator = possible_upgrade_locators[locator_name]
                            elif len(possible_upgrade_locators[locator_name].users_collection) > 0:
                                upgrade_locator = possible_upgrade_locators[locator_name]
                                break

                        if upgrade_locator is None:
                            message = "Locator for upgrade positioning not found, upgrade models for %r won't be properly positioned." % upgrade_type
                            self.report({"WARNING"}, message)
                            lprint("W " + message)
                            continue

                        curr_upgrade_scs_root.location = (0,) * 3
                        curr_upgrade_scs_root.rotation_euler = (0,) * 3
                        curr_upgrade_scs_root.parent = upgrade_locator

            ##################################
            #
            # 4. cleanup the scene and report problems
            #
            ##################################

            # remove any layer collection not created by us
            cols_to_unlink = set()
            for col in bpy.context.scene.collection.children:
                if _PT_consts.model_refs_to_sii not in col:
                    cols_to_unlink.add(col)
            for col in cols_to_unlink:
                bpy.context.scene.collection.children.unlink(col)

            # make our layer collections hidden, as user should later select what to export
            for layer_col in bpy.context.view_layer.layer_collection.children:
                layer_col.exclude = self.hide_collections

            # move all objects still in master collection to our main collection
            if _PT_consts.main_coll_name not in bpy.data.collections:
                main_collection = bpy.data.collections.new(_PT_consts.main_coll_name)
            else:
                main_collection = bpy.data.collections[_PT_consts.main_coll_name]

            bpy.context.view_layer.layer_collection.collection.children.link(main_collection)

            for obj in bpy.context.view_layer.layer_collection.collection.objects:
                main_collection.objects.link(obj)
                bpy.context.view_layer.layer_collection.collection.objects.unlink(obj)

            # hide main collection everywhere
            main_collection.hide_viewport = main_collection.hide_render = main_collection.hide_select = True

            # on the end report multiple project model problems
            if len(multiple_project_vehicle_models) > 0:
                lprint("W Same vehicle models referenced by multiple SIIsprojects, one from 'mod_' or 'dlc_' project was used! Multiple project "
                       "models:")
                for vehicle_model_path in multiple_project_vehicle_models:
                    lprint("W %r", (vehicle_model_path,))

            if len(multiple_project_upgrade_models) > 0:
                lprint("W Same upgrade models referenced by multiple upgrades SIIs or multiple projects ('mod_' or 'dlc_'):")
                for upgrade_model_path in multiple_project_upgrade_models:
                    lprint("W %r", (upgrade_model_path,))

            self.finalize()
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.directory = _get_scs_globals().scs_project_path
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_ExportPaintjobUVLayoutAndMesh(bpy.types.Operator):
        bl_label = "Export SCS Paintjob UV Layout & Mesh"
        bl_idname = "scene.scs_tools_export_paintjob_uv_layout_and_mesh"
        bl_description = "Exports painjtob uv layout & mesh (OBJ) for currently visible objects in scene."
        bl_options = {'PRESET'}

        directory: StringProperty(
            name="Export UV",
            subtype='DIR_PATH',
        )

        filepath: StringProperty(
            name="Export UVs & mesh",
            description="File path to export paintjob uv layout & mesh too.",
            subtype='FILE_PATH',
        )

        config_meta_filepath: StringProperty(
            description="File path to paintjob configuration SII file."
        )

        layout_sii_selection_mode: BoolProperty(
            default=False,
            description="Use currently selected file as paintjob layout configuration file."
        )

        export_2nd_uvs: BoolProperty(
            name="Export 2nd UVs",
            description="Should 2nd UV set layout be exported?",
            default=True
        )
        export_3rd_uvs: BoolProperty(
            name="Export 3rd UVs",
            description="Should 3rd UV set layout be exported?",
            default=True
        )

        export_id_mask: BoolProperty(
            name="Export ID Mask",
            description="Should be id mask marking texture portions be exported?",
            default=True
        )

        id_mask_alpha: FloatProperty(
            name="ID Mask Color Alpha",
            description="Alpha value of ID color when exporting ID Mask\n"
                        "(For debugging purposes of texture portion overlaying, value 0.5 is advised otherwise 1.0 should be used.)",
            default=0.5,
            min=0.1,
            max=1.0
        )

        export_mesh: BoolProperty(
            name="Export Mesh as OBJ",
            description="Should OBJ mesh also be exported?",
            default=True
        )

        @staticmethod
        def is_out_of_uv_bounds(uv):
            return uv[0] > 1 or uv[0] < 0 or uv[1] > 1 or uv[1] < 0

        @staticmethod
        def transform_uvs(obj, texture_portion):
            """Transform paintjob uvs on given object by data from texture portion.

            :param obj: Blender mesh object to be transformed
            :type obj: bpy.types.Object
            :param texture_portion: texture portion defining portion position and size from which transformation is calculated
            :type texture_portion: io_scs_tools.internals.structure.UnitData
            """

            position = [float(i) for i in texture_portion.get_prop("position")]
            size = [float(i) for i in texture_portion.get_prop("size")]

            bm = bmesh.new()
            bm.from_mesh(obj.data)

            for face in bm.faces:

                uv_lay_2nd = bm.loops.layers.uv[_PT_consts.uvs_name_2nd]
                uv_lay_3rd = bm.loops.layers.uv[_PT_consts.uvs_name_3rd]
                for loop in face.loops:

                    uv = loop[uv_lay_2nd].uv
                    uv = (uv[0] * size[0], uv[1] * size[1])
                    uv = (uv[0] + position[0], uv[1] + position[1])
                    loop[uv_lay_2nd].uv = uv

                    uv = loop[uv_lay_3rd].uv
                    uv = (uv[0] * size[0], uv[1] * size[1])
                    uv = (uv[0] + position[0], uv[1] + position[1])
                    loop[uv_lay_3rd].uv = uv

            bm.to_mesh(obj.data)
            bm.free()

        @staticmethod
        def cleanup(*args):
            """Interprets given argumens as iterables holding blender object that shall be cleaned aka removed from datablocks.
            """

            meshes = set()

            for object_iterable in args:
                for obj in object_iterable:
                    meshes.add(obj.data)  # save mesh to remove it afterwards
                    bpy.data.objects.remove(obj, do_unlink=True)

            for mesh in meshes:
                bpy.data.meshes.remove(mesh, do_unlink=True)

        @staticmethod
        def cleanup_meshes():
            """Cleanups any meshes with zero users that might be left-overs from join operator.
            """

            meshes_to_remove = []
            for m in bpy.data.meshes:
                if m.users == 0:
                    meshes_to_remove.append(m.name)

            for mesh_name in meshes_to_remove:
                if mesh_name in bpy.data.meshes:
                    bpy.data.meshes.remove(bpy.data.meshes[mesh_name])

        def check(self, context):

            if self.layout_sii_selection_mode:
                self.config_meta_filepath = _path_utils.readable_norm(self.filepath)
                self.layout_sii_selection_mode = False

            return True

        def draw(self, context):

            col = self.layout.column(align=True)

            col.label(text="Paintjobs Layout META File:", icon='FILE_SCRIPT')
            col.prop(self, "config_meta_filepath", text="")
            col.prop(self, "layout_sii_selection_mode", toggle=True, text="Select Current File from File Browser", icon='PASTEDOWN')

            col.separator()

            col.label(text="What to export?", icon='QUESTION')
            col.prop(self, "export_2nd_uvs")
            col.prop(self, "export_3rd_uvs")
            col.prop(self, "export_id_mask")
            if self.export_id_mask:
                col.prop(self, "id_mask_alpha", slider=True)
            col.prop(self, "export_mesh")

        def do_report(self, type, message, do_report=False):

            if 'INFO' in type:
                prefix = "I "
            elif 'WARNING' in type:
                prefix = "W "
            elif 'ERROR' in type:
                prefix = "E "
            else:
                prefix = "D "

            lprint(prefix + message, report_errors=do_report, report_warnings=do_report)

            for line in message.split("\n"):
                self.report(type, line.replace("\t", "").replace("  ", " "))

        def check_and_prepare_uvs(self, obj, orig_uvs_name_2nd, orig_uvs_name_3rd):
            """Check and prepare uvs for export by creating a copy of the ones used in SCS truckpaint material.

            :param obj: Blender mesh object to be transformed
            :type obj: bpy.types.Object
            :param orig_uvs_name_2nd: name of the uv used in first paintjob slot from truckpaint material
            :type orig_uvs_name_2nd: str
            :param orig_uvs_name_3rd: name of the uv used in second paintjob slot from truckpaint material
            :type orig_uvs_name_3rd: str
            :return: True if check is successful and none of the UVs is out of bounds; False otherwise
            :rtype: bool
            """

            invalid_uv = False

            bm = bmesh.new()
            bm.from_mesh(obj.data)

            uv_lay_2nd = bm.loops.layers.uv[orig_uvs_name_2nd]
            uv_lay_3rd = bm.loops.layers.uv[orig_uvs_name_3rd]

            # check for validity
            for face in bm.faces:
                for loop in face.loops:
                    if self.export_2nd_uvs and self.is_out_of_uv_bounds(loop[uv_lay_2nd].uv):
                        invalid_uv = True
                        break
                    if self.export_3rd_uvs and self.is_out_of_uv_bounds(loop[uv_lay_3rd].uv):
                        invalid_uv = True
                        break

                if invalid_uv:
                    break

            # copy over if valid
            if not invalid_uv:
                bm.loops.layers.uv.new(_PT_consts.uvs_name_2nd)
                bm.loops.layers.uv[_PT_consts.uvs_name_2nd].copy_from(uv_lay_2nd)

                bm.loops.layers.uv.new(_PT_consts.uvs_name_3rd)
                bm.loops.layers.uv[_PT_consts.uvs_name_3rd].copy_from(uv_lay_3rd)

            bm.to_mesh(obj.data)
            bm.free()

            return not invalid_uv

        def execute(self, context):

            ##################################
            #
            # 1. collect visible mesh & determinate which collections to export
            #
            ##################################
            visible_collections = []
            for layer_col in context.view_layer.layer_collection.children:

                if layer_col.hide_viewport:
                    continue

                if layer_col.exclude:
                    continue

                collection = layer_col.collection

                if _PT_consts.model_refs_to_sii not in collection:
                    continue

                # unhide all objects that are part of collections to export (in case user hid them for some reason),
                # becasue hidden objects can not be selected/duplicated otherwise
                for obj in collection.objects:
                    obj.hide_viewport = False
                    obj.hide_set(False)

                visible_collections.append(collection)

            lprint("S Visible collections to export: %s", (visible_collections,))

            merged_objects_to_export = {}
            for collection in visible_collections:

                # start with selection clearing, use our implementation to deselect any possible selected object in hidden layers
                for obj in context.view_layer.objects:
                    obj.select_set(False)

                selected_objects_count = 0
                for obj in collection.objects:
                    if obj.type == "MESH":
                        obj.select_set(True)
                        selected_objects_count += 1

                # in case no mesh objects in this collection, there is no data to be exported, so advance to next collection
                if selected_objects_count <= 0:
                    continue

                bpy.ops.object.duplicate()

                if selected_objects_count > 1:
                    context.view_layer.objects.active = context.selected_objects[0]
                    bpy.ops.object.join()
                    self.cleanup_meshes()

                curr_merged_object = context.selected_objects[0]
                curr_truckpaint_mat = None
                for mat_slot in curr_merged_object.material_slots:
                    if mat_slot.material and mat_slot.material.scs_props.mat_effect_name.startswith("eut2.truckpaint"):
                        curr_truckpaint_mat = mat_slot.material
                        break

                if curr_truckpaint_mat is None:
                    self.do_report({'WARNING'}, "Collection %r won't be exported as 'truckpaint' material wasn't found!" % collection.name)
                    self.cleanup((curr_merged_object,))
                    continue

                # rename paintjob uvs to our constant ones,
                # so exporting at the end is easy as all objects will result in same uv layers names
                if curr_truckpaint_mat.scs_props.active_shader_preset_name == "<imported>":
                    tex_coords = curr_truckpaint_mat.scs_props.custom_tex_coord_maps
                    if 'tex_coord_1' in tex_coords and 'tex_coord_2' in tex_coords:
                        uvs_2nd_name = curr_truckpaint_mat.scs_props.custom_tex_coord_maps['tex_coord_1'].value
                        uvs_3rd_name = curr_truckpaint_mat.scs_props.custom_tex_coord_maps['tex_coord_2'].value
                    else:
                        self.do_report({'WARNING'},
                                       "Collection %r won't be exported as some objects with <imported> truckpaint material are missing tex_coords!" %
                                       collection.name)
                        continue
                else:
                    uvs_2nd_name = curr_truckpaint_mat.scs_props.shader_texture_base_uv[1].value
                    uvs_3rd_name = curr_truckpaint_mat.scs_props.shader_texture_base_uv[2].value

                if not self.check_and_prepare_uvs(curr_merged_object, uvs_2nd_name, uvs_3rd_name):
                    self.do_report({'WARNING'},
                                   "Collection %r won't be exported as one or more objects have UVs out of <0;1> bounds!" %
                                   collection.name)
                    self.cleanup((curr_merged_object,))
                    continue

                # remove all none needed & colliding data-blocks from object: materials, collections
                while len(curr_merged_object.material_slots) > 0:
                    with context.temp_override(object=curr_merged_object):
                        bpy.ops.object.material_slot_remove()

                while len(curr_merged_object.users_collection) > 0:
                    curr_merged_object.users_collection[0].objects.unlink(curr_merged_object)

                # linke merged objects to scene master collection so they can be handled properly by selection operators
                context.view_layer.layer_collection.collection.objects.link(curr_merged_object)

                merged_objects_to_export[curr_merged_object] = collection

            if len(merged_objects_to_export) <= 0:
                self.do_report({'ERROR'}, "No objects to export!", do_report=True)
                return {'CANCELLED'}

            lprint("S Merged objects to export: %s", (merged_objects_to_export.values(),))

            ##################################
            #
            # 2. depending on paintjob layout file, scale/offset uv's
            #
            ##################################

            # 1. parse & fill data from paintjobs layout configuration file

            pj_config_sii_container = _sii_container.get_data_from_file(self.config_meta_filepath)
            if not _sii_container.has_valid_unit_instance(pj_config_sii_container,
                                                          unit_type="paintjobs_metadata",
                                                          req_props=("common_texture_size",)):

                self.do_report({'ERROR'}, "Validation failed on SII: %r" % _path_utils.readable_norm(self.config_meta_filepath), do_report=True)
                self.cleanup(merged_objects_to_export.keys())
                return {'CANCELLED'}

            # interpret common texture size vector as two ints
            common_texture_size = [int(i) for i in _sii_container.get_unit_property(pj_config_sii_container, "common_texture_size")]

            # get and validate texture portion unit existence
            texture_portions = {}
            texture_portion_names = _sii_container.get_unit_property(pj_config_sii_container, "texture_portions")
            if texture_portion_names:

                for unit_id in texture_portion_names:

                    texture_portion = _sii_container.get_unit_by_id(pj_config_sii_container, unit_id, "texture_portion_metadata")
                    if not texture_portion:
                        self.do_report({'WARNING'},
                                       "Ignoring used texture portion with name %r as it's not defined in paintjob layout meta data!" % unit_id)
                        continue

                    parent = texture_portion.get_prop("parent")
                    if parent and parent not in texture_portion_names:
                        self.do_report({'WARNING'},
                                       "Ignoring used texture portion with name %r as it's parent: %r "
                                       "is not defined in paintjob layout meta data!" % (unit_id, parent))
                        continue

                    position = texture_portion.get_prop("position")
                    size = texture_portion.get_prop("size")
                    if position is not None and size is not None:
                        position = [float(x) for x in position]
                        size = [float(x) for x in size]
                        if self.is_out_of_uv_bounds(position):
                            self.do_report({'WARNING'},
                                           "Ignoring used texture portion with name %r as it's position is not within (0,1) bounds: %r" %
                                           (unit_id, position))
                            continue
                        else:
                            position_size = (position[0] + size[0], position[1] + size[1])
                            if self.is_out_of_uv_bounds(position_size):
                                self.do_report({'WARNING'},
                                               "Ignoring used texture portion with name %r as it's calculated "
                                               "position+size is not within (0,1) bounds: %r" %
                                               (unit_id, position_size))
                                continue

                    texture_portions[unit_id] = texture_portion

            # do model sii validation
            for unit_id in texture_portions:
                texture_portion = texture_portions[unit_id]

                if not texture_portion.get_prop("model_sii") and not texture_portion.get_prop("is_master", False):
                    self.do_report({'ERROR'}, "Invalid texture portion with name %r as 'model_sii' is not defined!" % unit_id, do_report=True)
                    return {'CANCELLED'}

            lprint("S Found texture portions: %r", (list(texture_portions.keys()),))

            # 2. bind each merged object to it's texture portion and filter to four categories:

            # objects which are independently exported by transformation defined in their texture potion (be it original or parent portion)
            independent_export_objects = {}
            # objects with set "is_master" property inside texture portion; will use master paintjob definition & texture
            master_export_objects = {}
            # objects which are (direct or indirect) children of master export objects;
            # they have to be duplicated & included in master objects before export (to see uvs on all master layouts)
            master_child_export_objects = {}
            # objects without referenced SII, which won't be exported and should be removed manually via cleanup method
            unconfigured_objects = []
            for obj in merged_objects_to_export:

                collection = merged_objects_to_export[obj]

                # find texture portion belonging to export object
                texture_portion = None
                for unit_id in texture_portions:

                    model_sii = texture_portions[unit_id].get_prop("model_sii")

                    # ignore texture portions without reference to model sii
                    if not model_sii:
                        continue

                    for reference_to_sii in collection[_PT_consts.model_refs_to_sii]:

                        # yep we found possible sii of the model, but not quite yet
                        if reference_to_sii.endswith(model_sii):

                            sii_cont = _sii_container.get_data_from_file(reference_to_sii)
                            variant = _sii_container.get_unit_property(sii_cont, "variant")

                            if variant:
                                variant = variant.lower()
                            else:
                                variant = "default"  # if variant is not specified in sii, our games uses default

                            # now check variant: if it's the same then we have it!
                            if variant == collection[_PT_consts.model_variant_prop]:
                                texture_portion = texture_portions[unit_id]
                                break

                    if texture_portion:
                        break

                if not texture_portion:  # texture portion not found help the user!
                    referenced_siis = ""
                    for referenced_sii in sorted(collection[_PT_consts.model_refs_to_sii]):
                        referenced_siis += "-> %r\n\t   " % referenced_sii

                    self.do_report({'WARNING'},
                                   "Model %r wasn't referenced by any SII defined in paintjob configuration metadata, please reconfigure!\n\t   "
                                   "SII files from which model was referenced:\n\t   %s" % (collection.name, referenced_siis))
                    unconfigured_objects.append(obj)
                    continue

                # filter out objects using master texture portions
                if bool(texture_portion.get_prop("is_master")):
                    master_export_objects[obj] = texture_portion
                    continue

                # filter out objects using independent texture portion
                parent = texture_portion.get_prop("parent")
                if parent is None:
                    independent_export_objects[obj] = texture_portion

                # as last get trough objects with parent & put them in proper dictionary assigning PARENT texture portion already
                parent_texture_portion = texture_portion
                while parent:
                    parent_texture_portion = _sii_container.get_unit_by_id(pj_config_sii_container, parent, parent_texture_portion.type)
                    parent = parent_texture_portion.get_prop("parent")

                if bool(parent_texture_portion.get_prop("is_master")):
                    master_child_export_objects[obj] = texture_portion
                else:
                    independent_export_objects[obj] = parent_texture_portion  # even if it has parent it's exported independent; no duplicates needed

            # cleanup unconfigured objects
            if len(unconfigured_objects) > 0:

                # make sure to remove uncofigured objects from merged,
                # so that cleanup won't be done twice and possibly result in ReferenceError
                for obj in unconfigured_objects:
                    del merged_objects_to_export[obj]

                self.cleanup(unconfigured_objects)

            # nonsense to go further if nothing to export
            if len(independent_export_objects) + len(master_export_objects) <= 0:
                self.do_report({"ERROR"},
                               "Nothing to export, independent objects: %s, master objects: %s, objects with master parent: %s!" %
                               (len(independent_export_objects), len(master_export_objects), len(master_child_export_objects)),
                               do_report=True)
                self.cleanup(merged_objects_to_export.keys())
                return {'CANCELLED'}

            # 3. do uv transformations and distribute master children objects:

            # transform independent objects
            for obj in independent_export_objects:
                self.transform_uvs(obj, independent_export_objects[obj])

            # duplicate all objects with master parent & merge them
            for obj in master_child_export_objects:
                export_uvs_to = master_child_export_objects[obj].get_prop("export_uvs_to")

                for master_obj in master_export_objects:

                    # if there is extra field defining where we should export child of a master
                    # then ignore export for other master portions
                    if export_uvs_to and master_export_objects[master_obj].id not in export_uvs_to:
                        continue

                    bpy.ops.object.select_all(action="DESELECT")

                    # duplicate
                    obj.select_set(True)
                    bpy.ops.object.duplicate()

                    # merge with master object
                    master_obj.select_set(True)
                    context.view_layer.objects.active = master_obj
                    bpy.ops.object.join()
                    self.cleanup_meshes()

                bpy.data.objects.remove(obj, do_unlink=True)

            # as last we transform master objects, as now they should be merged even with child objects
            for obj in master_export_objects:
                self.transform_uvs(obj, master_export_objects[obj])

            ##################################
            #
            # 3. merge final mesh for export
            #
            ##################################

            # select all export objects first
            bpy.ops.object.select_all(action="DESELECT")
            for obj in independent_export_objects:
                obj.select_set(True)
            for obj in master_export_objects:
                obj.select_set(True)

            # merge them
            final_merged_object = context.selected_objects[0]
            if len(merged_objects_to_export) > 1:
                context.view_layer.objects.active = context.selected_objects[0]
                bpy.ops.object.join()
                self.cleanup_meshes()

            ##################################
            #
            # 4. export selected uv layers & mesh
            #
            ##################################
            if self.filepath.endswith(".png"):  # strip last extension if it's png
                self.filepath = self.filepath[:-4]

            if self.export_2nd_uvs:

                # set active uv layer so export will take proper
                final_merged_object.data.uv_layers.active = final_merged_object.data.uv_layers[_PT_consts.uvs_name_2nd]

                with context.temp_override(active_object=final_merged_object):
                    bpy.ops.uv.export_layout(filepath=self.filepath + ".2nd.png",
                                             export_all=True,
                                             mode="PNG",
                                             size=common_texture_size,
                                             opacity=1)

                if self.export_mesh:
                    with context.temp_override(active_object=final_merged_object, selected_objects=(final_merged_object,)):
                        bpy.ops.export_scene.obj(filepath=self.filepath + ".2nd.obj",
                                                 use_selection=True,
                                                 use_materials=False)

            if self.export_3rd_uvs:

                # set active uv layer so export will take proper
                final_merged_object.data.uv_layers.active = final_merged_object.data.uv_layers[_PT_consts.uvs_name_3rd]

                with context.temp_override(active_object=final_merged_object):
                    bpy.ops.uv.export_layout(filepath=self.filepath + ".3rd.png",
                                             export_all=True,
                                             mode="PNG",
                                             size=common_texture_size,
                                             opacity=1)

                if self.export_mesh:
                    with context.temp_override(active_object=final_merged_object, selected_objects=(final_merged_object,)):
                        bpy.ops.export_scene.obj(filepath=self.filepath + ".3rd.obj",
                                                 use_selection=True,
                                                 use_materials=False)

            # remove final merged object now as we done our work here
            bpy.data.objects.remove(final_merged_object, do_unlink=True)

            ##################################
            #
            # 5. export texture portions id mask
            #
            ##################################

            if self.export_id_mask:

                start_time = time()

                # intialize pixel values for id mask texture
                img_pixels = numpy.zeros((common_texture_size[1], common_texture_size[0], 4), numpy.float16)

                id_mask_color_idx = 0
                for unit_id in texture_portions:

                    # ignore portions with parent attribute, they don't use it's own texture space
                    if texture_portions[unit_id].get_prop("parent") is not None:
                        continue

                    position = [float(i) for i in texture_portions[unit_id].get_prop("position")]
                    size = [float(i) for i in texture_portions[unit_id].get_prop("size")]

                    portion_width = round(size[0] * common_texture_size[0])
                    portion_height = round(size[1] * common_texture_size[1])
                    portion_pos_x = round(position[0] * common_texture_size[0])
                    portion_pos_y = round(position[1] * common_texture_size[1])

                    # calculate this portion color from RGB values
                    portion_col = list(_PT_consts.id_mask_colors[id_mask_color_idx % len(_PT_consts.id_mask_colors)])
                    id_mask_color_idx += 1
                    portion_col[0] /= 255.0
                    portion_col[1] /= 255.0
                    portion_col[2] /= 255.0
                    portion_col.append(self.id_mask_alpha)

                    img_pixels[portion_pos_y:portion_pos_y + portion_height, portion_pos_x:portion_pos_x + portion_width, 0] = portion_col[0]
                    img_pixels[portion_pos_y:portion_pos_y + portion_height, portion_pos_x:portion_pos_x + portion_width, 1] = portion_col[1]
                    img_pixels[portion_pos_y:portion_pos_y + portion_height, portion_pos_x:portion_pos_x + portion_width, 2] = portion_col[2]
                    img_pixels[portion_pos_y:portion_pos_y + portion_height, portion_pos_x:portion_pos_x + portion_width, 3] = portion_col[3]

                # create image data block
                img = bpy.data.images.new("tmp_img", common_texture_size[0], common_texture_size[1], alpha=True)
                img.colorspace_settings.name = "sRGB"  # make sure we use sRGB color-profile
                img.alpha_mode = 'CHANNEL_PACKED'
                img.pixels[:] = img_pixels.reshape((common_texture_size[1] * common_texture_size[0] * 4,))

                # save
                scene = bpy.context.scene
                scene.render.image_settings.file_format = "PNG"
                scene.render.image_settings.color_mode = "RGBA"
                img.save_render(self.filepath + ".id_mask.png", scene=bpy.context.scene)

                # remove image data-block, as we don't need it anymore
                img.buffers_free()
                bpy.data.images.remove(img, do_unlink=True)

                lprint("I Exported ID mask texture in %.2f sec!" % (time() - start_time))

            self.do_report({'INFO'}, "Somehow we made it to the end, if no warning & errros appeared, then you are perfect!", do_report=True)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCS_TOOLS_OT_GeneratePaintjob(bpy.types.Operator):
        bl_label = "Generate SCS Paintjob From Common Texture"
        bl_idname = "scene.scs_tools_generate_paintjob"
        bl_description = "Generates complete setup for given paintjob: definitions, TGAs & TOBJs."
        bl_options = {'INTERNAL'}

        class Overrides:
            """Class encapsulating paintjob overrides creation and export."""
            PROPS_KEY = "props"
            ACC_LIST_KEY = "accessories"

            __overrides = OrderedDict()

            @staticmethod
            def __generate_props_hash(props):
                hash_str = ""

                for key in props:
                    hash_str += str(props[key])

                return hash_str

            def __init__(self):
                self.__overrides = OrderedDict()

            def __append_to_acc_list(self, props_hash, acc_type_id):
                """Add accessory to proper override list depending on given properties hash

                NOTE: There is no check if override with given properties hash exists! So check it before.

                :param props_hash: hash of properties values under which this override will be saved
                :type props_hash: str
                :param acc_type_id: accessory type and id as concatenated string divided by dot (<type>.<id>)
                :type acc_type_id: str
                """
                if acc_type_id in self.__overrides[props_hash][self.ACC_LIST_KEY]:
                    return

                self.__overrides[props_hash][self.ACC_LIST_KEY].add(acc_type_id)

            def __create_override(self, props_hash, acc_type_id, props):
                """Creates and saves override structure.

                One override structure is represented with dictonary of two members:
                1. props -> all paintjob properties saved in this override
                2. accessory list -> list of accessoreis compatible with this override

                NOTE: There is no check if override with given propreties hash already exists! So check it before.

                :param props_hash: hash of properties values under which this override will be saved
                :type props_hash: str
                :param acc_type_id: accessory type and id as concatenated string divided by dot (<type>.<id>)
                :type acc_type_id: str
                :param props: properties used in this override
                :type props: OrderedDict[str, any]
                """
                self.__overrides[props_hash] = {
                    self.PROPS_KEY: props,
                    self.ACC_LIST_KEY: {acc_type_id, }
                }

            def add_accessory(self, acc_type_id, props=OrderedDict()):
                """Add acceesory to overides.

                :param acc_type_id: accessory type and id as concatenated string divided by dot (<type>.<id> -> exhaust_m.mg01)
                :type acc_type_id: str
                :param props: simple paint job properites of this accessory
                :type props: OrderedDict[str, any]
                """
                props_hash = self.__generate_props_hash(props)

                if props_hash in self.__overrides:
                    self.__append_to_acc_list(props_hash, acc_type_id)
                else:
                    self.__create_override(props_hash, acc_type_id, props)

            def export_to_sii(self, op_inst, config_path):
                """Exports overrides in given config path.

                :param op_inst: generate paintjob operator instance, to bi able to get default values of paintjob properties
                :type op_inst: bpy.types.Operator
                :param config_path: absolute filepath where overrides should be exported:
                                    /def/vehicle/<vehicle_type>/<brand.model>/paint_job/accessory/<pj_suffixed_name>.sii
                :type config_path: str
                :return: True if export was successful, False otherwise
                :rtype: bool
                """
                export_units = []

                # 1. collect overrides as units
                for props_hash in self.__overrides:
                    override = self.__overrides[props_hash]

                    # if no accessories for current override ignore it
                    if len(override[self.ACC_LIST_KEY]) == 0:
                        continue

                    unit = _UnitData("simple_paint_job_data", ".ovr%i" % len(export_units))

                    # export extra properties only if different than default value
                    pj_props = override[self.PROPS_KEY]
                    for key in pj_props:
                        assert op_inst.append_prop_if_not_default(unit, "pjs_" + key, pj_props[key])

                    # as it can happen now that we don't have any properties in our unit, then it's useless to export it
                    if len(unit.props) == 0:
                        continue

                    # now fill accessory list
                    unit.props["acc_list"] = []
                    for acc_type_id in sorted(override[self.ACC_LIST_KEY]):
                        unit.props["acc_list"].append(acc_type_id)

                    # finally add it to export units
                    export_units.append(unit)

                # 2. export overrides
                return _sii_container.write_data_to_file(config_path, tuple(export_units), create_dirs=True)

        class ColorVariantItem(bpy.types.PropertyGroup):
            """Color variant item."""
            value: FloatVectorProperty(default=(0, 0, 0))

        vehicle_type = _PT_consts.VehicleTypes.NONE

        img_node = None
        premul_node = None
        translate_node = None
        viewer_node = None

        config_meta_filepath: StringProperty(
            description="File path to paintjob configuration SII file."
        )

        project_path: StringProperty(
            description="Project to which this paintjob belongs. Could be usefull if PSD file is not within same project."
        )

        common_texture_path: StringProperty(
            description="File path to original common paintjob TGA texture."
        )

        export_alpha: BoolProperty(
            description="Flag defining if textures shall be exported with alpha or not."
        )

        preserve_common_texture: BoolProperty(
            description="Should given common texture TGA be preserved and not deleted after generation is finished?"
        )

        optimize_single_color_textures: BoolProperty(
            description="Export texture with size 4x4 if whole exported texture has all pixels with same color?"
        )

        export_configs_only: BoolProperty(
            description="Should only configurations be exported (used for export of metallic like paintjobs without paintjob texture)?"
        )

        # paint job settings exported to common SUI settings file
        pjs_name: StringProperty(default="pj_name")
        pjs_price: IntProperty(default=10000)
        pjs_unlock: IntProperty(default=0)
        pjs_icon: StringProperty(default="")
        pjs_part_type: StringProperty(default="unknown")
        pjs_steam_inventory_id: IntProperty(default=-1)

        pjs_paint_job_mask: StringProperty(default="")

        pjs_mask_r_color: FloatVectorProperty(default=(1, 0, 0))
        pjs_mask_r_locked: BoolProperty(default=True)

        pjs_mask_g_color: FloatVectorProperty(default=(0, 1, 0))
        pjs_mask_g_locked: BoolProperty(default=True)

        pjs_mask_b_color: FloatVectorProperty(default=(0, 0, 1))
        pjs_mask_b_locked: BoolProperty(default=True)

        pjs_base_color: FloatVectorProperty(default=(1, 1, 1))
        pjs_base_color_locked: BoolProperty(default=True)

        pjs_flip_color: FloatVectorProperty(default=(1, 0, 0))
        pjs_flip_color_locked: BoolProperty(default=True)

        pjs_flip_strength: FloatProperty(default=0.27)

        pjs_flake_color: FloatVectorProperty(default=(0, 1, 0))
        pjs_flake_color_locked: BoolProperty(default=True)

        pjs_flake_uvscale: FloatProperty(default=32.0)
        pjs_flake_vratio: FloatProperty(default=1.0)
        pjs_flake_density: FloatProperty(default=1.0)
        pjs_flake_shininess: FloatProperty(default=50.0)
        pjs_flake_clearcoat_rolloff: FloatProperty(default=2.2)
        pjs_flake_noise: StringProperty(default="/material/custom/flake_noise.tobj")

        pjs_alternate_uvset: BoolProperty(default=False)
        pjs_alternate_flipflake_uvset: BoolProperty(default=False)
        pjs_flipflake: BoolProperty(default=False)
        pjs_airbrush: BoolProperty(default=False)
        pjs_stock: BoolProperty(default=False)
        pjs_color_variant: CollectionProperty(type=ColorVariantItem)

        @staticmethod
        def do_report(the_type, message, do_report=False):

            if 'INFO' in the_type:
                prefix = "I "
            elif 'WARNING' in the_type:
                prefix = "W "
            elif 'ERROR' in the_type:
                prefix = "E "
            else:
                prefix = "D "

            # change dump level internally as we want this operator to report everything
            if int(_get_scs_globals().dump_level) < 4:
                _get_scs_globals()["dump_level"] = 4

            lprint(prefix + message, report_errors=do_report, report_warnings=do_report)

        def initialize_nodes(self, context, img):
            """Initializes nodes and scene proeprties to be able to use compositor for rendering of texture portions TGAs.

            :param context: blender context
            :type context: bpy.types.Context
            :param img: original big common texture image
            :type img: bpy.types.Image
            """

            # ensure compositing and scene node tree

            context.scene.render.use_compositing = True
            context.scene.use_nodes = True

            _X_SHIFT = 250

            tree = context.scene.node_tree
            nodes = tree.nodes
            links = tree.links

            # remove any existing nodes (they are created by defoult when switching to compositiong)

            while len(nodes) > 0:
                nodes.remove(nodes[0])

            # create nodes

            self.img_node = nodes.new(type="CompositorNodeImage")
            self.img_node.location = (-_X_SHIFT, 0)
            self.img_node.image = img

            self.premul_node = nodes.new(type="CompositorNodePremulKey")
            self.premul_node.location = (0, 0)
            self.premul_node.mapping = 'STRAIGHT_TO_PREMUL'

            self.translate_node = nodes.new(type="CompositorNodeTranslate")
            self.translate_node.location = (_X_SHIFT, 0)

            self.viewer_node = nodes.new(type="CompositorNodeComposite")
            self.viewer_node.location = (_X_SHIFT * 2, 0)
            self.viewer_node.use_alpha = True

            # create links

            links.new(self.premul_node.inputs["Image"], self.img_node.outputs["Image"])
            links.new(self.translate_node.inputs["Image"], self.premul_node.outputs["Image"])
            links.new(self.viewer_node.inputs["Image"], self.translate_node.outputs["Image"])

        def export_texture(self, orig_img, tgas_dir_path, texture_portion):
            """Export given texture portion into given paintjob path.

            :param orig_img: Blender image datablock representing common texture
            :type orig_img: bpy.types.Image
            :param tgas_dir_path: absolute directory path to export TGA and TOBJ to
            :type tgas_dir_path: str
            :param texture_portion: texture portion defining portion position and size
            :type texture_portion: io_scs_tools.internals.structure.UnitData
            :return: TOBJ path of exported texture, in case sth went wrong return None
            :rtype: str | None
            """

            position = [float(i) for i in texture_portion.get_prop("position")]
            size = [float(i) for i in texture_portion.get_prop("size")]
            is_master = bool(texture_portion.get_prop("is_master"))

            orig_img_width = orig_img.size[0]
            orig_img_height = orig_img.size[1]

            orig_img_start_x = round(orig_img_width * position[0])
            orig_img_start_y = round(orig_img_height * position[1])

            img_width = round(orig_img_width * size[0])
            img_height = round(orig_img_height * size[1])

            # setup compositing nodes for current texture
            # NOTE: render clips original image by it's resolution and is centered on the output image,
            # thus we have to translate our original image so that portion texture is in the middle of the render

            orig_img_mid_x = orig_img_start_x + (img_width / 2)
            orig_img_mid_y = orig_img_start_y + (img_height / 2)

            self.translate_node.inputs["X"].default_value = (orig_img_width / 2) - orig_img_mid_x
            self.translate_node.inputs["Y"].default_value = (orig_img_height / 2) - orig_img_mid_y

            # we encode texture name with portion position and size, thus any possible duplicates will end up in same texture
            tga_name = "pjm_at_%ix%i_size_%ix%i.tga" % (orig_img_start_x,
                                                        orig_img_start_y,
                                                        img_width,
                                                        img_height)
            tga_path = os.path.join(tgas_dir_path, tga_name)

            # export texture portion image by properly reset scene settings and then render with compositor

            scene = bpy.context.scene

            scene.display_settings.display_device = "sRGB"

            scene.view_settings.view_transform = "Standard"
            scene.view_settings.look = "None"
            scene.view_settings.exposure = 0
            scene.view_settings.gamma = 1

            scene.render.image_settings.file_format = "TARGA"
            scene.render.image_settings.color_mode = "RGBA" if self.export_alpha else "RGB"
            scene.render.resolution_percentage = 100
            scene.render.resolution_x = img_width
            scene.render.resolution_y = img_height
            scene.render.filepath = tga_path
            scene.render.dither_intensity = 0

            bpy.ops.render.render(write_still=True)

            # if no optimization or is master then we can skip optimization processing,
            # otherwise texture is re-opened and analyzed and
            # in case only one color is inside, we export 4x4 texture and update tga path

            if self.optimize_single_color_textures and not is_master:

                lprint("I Analyzing texture for single color...")

                is_img_single_color = True
                img = bpy.data.images.load(tga_path, check_existing=True)

                _CHUNK_SIZE = 2048 * 1024  # testing showed that this chunk size works best
                rows_in_chunk = round(_CHUNK_SIZE / img_width)
                buffer = []
                comparing_pixel = [0.0] * 4
                for row in range(0, img_height):

                    # on the beginning of the chunk refill pixels from image
                    if row % rows_in_chunk == 0:

                        start_pixel = row * img_width * 4
                        end_pixel = start_pixel + img_width * rows_in_chunk * 4
                        end_pixel = min(end_pixel, img_width * img_height * 4)

                        buffer = img.pixels[start_pixel:end_pixel]

                    # use first pixel for comparison
                    if row == 0:
                        comparing_pixel = buffer[0:4]

                    start_px = (row % rows_in_chunk) * img_width * 4
                    for i in range(0, img_width * 4, 4):
                        if buffer[(start_px + i):(start_px + i + 4)] != comparing_pixel:
                            is_img_single_color = False
                            break

                    if not is_img_single_color:
                        break

                # already exported image not longer needed in Blender, so remove it!

                img.buffers_free()
                bpy.data.images.remove(img, do_unlink=True)

                # finally export single texture

                if is_img_single_color:

                    # don't forget to remove previously exported big TGA
                    os.remove(tga_path)

                    _SINGLE_COLOR_IMAGE_NAME = "single_color_image"

                    if _SINGLE_COLOR_IMAGE_NAME not in bpy.data.images:
                        bpy.data.images.new(_SINGLE_COLOR_IMAGE_NAME, 4, 4, alpha=True)

                    img = bpy.data.images[_SINGLE_COLOR_IMAGE_NAME]
                    img.colorspace_settings.name = "sRGB"  # make sure we use sRGB color-profile
                    img.alpha_mode = 'STRAIGHT'
                    img.pixels[:] = comparing_pixel * 16

                    # we use shared prefix for 4x4 textures in case any other portion will be using same one
                    tga_name = "shared_%.2x%.2x%.2x%.2x.tga" % (int(comparing_pixel[0] * 255.0),
                                                                int(comparing_pixel[1] * 255.0),
                                                                int(comparing_pixel[2] * 255.0),
                                                                int(comparing_pixel[3] * 255.0))
                    tga_path = os.path.join(tgas_dir_path, tga_name)

                    img.save_render(tga_path, scene=bpy.context.scene)

                    lprint("I Texture portion %r has only one color in common texture, optimizing it by exporting 4x4px TGA!", (texture_portion.id,))

            # write TOBJ beside tga file

            tobj_path = tga_path[:-4] + ".tobj"
            tobj_cont = _TobjContainer()

            tobj_cont.map_type = "2d"
            tobj_cont.map_names.append(tga_name)
            tobj_cont.addr.append("clamp_to_edge")
            tobj_cont.addr.append("clamp_to_edge")
            tobj_cont.filepath = tobj_path

            # if there is any error by writting just return none
            if not tobj_cont.write_data_to_file():
                return None

            return tobj_path

        def export_master_sii(self, config_path, pj_token, pj_full_unit_name, pj_props, suitable_for=None):
            """Export master SII configuration file into given absolute path.

            :param config_path: absolute file path for SII where it should be epxorted
            :type config_path: str
            :param pj_token: string of original paintjob token got from original TGA file name
            :type pj_token: str
            :param pj_full_unit_name: <pj_unit_name>.<brand.model>.paint_job
            :type pj_full_unit_name: str
            :param pj_props: dictionary of sii unit attributes to be writen in sii (key: name of attribute, value: any sii unit compatible object)
            :type pj_props: dict[str | object]
            :param suitable_for: possible suitables of this paintjob; if None suitable_for property won't be written
            :type suitable_for: list(str) | None
            :return: True if export was successful, False otherwise
            :rtype: bool
            """

            unit = _UnitData("accessory_paint_job_data", pj_full_unit_name)

            pj_settings_sui_name = pj_token + "_settings.sui"

            # export paint job settings SUI file
            assert self.export_settings_sui(os.path.join(os.path.dirname(config_path), pj_settings_sui_name))

            # write include into paint job sii
            unit.props["@include"] = pj_settings_sui_name

            # export extra properties only if different than default value
            for key in pj_props:
                assert self.append_prop_if_not_default(unit, "pjs_" + key, pj_props[key])

            # export suitable for property
            if suitable_for and len(suitable_for) > 0:
                unit.props["suitable_for"] = suitable_for

            # as it can happen now that we don't have any properties in our unit, then it's useless to export it
            if len(unit.props) == 0:
                lprint("I Unit has not properties thus useless to export empty SII, ignoring it: %r", (config_path,))
                return True

            return _sii_container.write_data_to_file(config_path, (unit,), create_dirs=True)

        def export_settings_sui(self, settings_sui_path):
            """Export common SUI settings for paint job. This file includes all settings of the paintjob
            and shall be included in paint job master definitions.

            :param settings_sui_path: absolute file path for SUI where it should be exported
            :type settings_sui_path: str
            :return: True if settings were successfully written or if file is alredy up to date; False if sth goes wrong
            :rtype: bool
            """

            # do not reexport rapidly
            if os.path.isfile(settings_sui_path) and time() - os.path.getmtime(settings_sui_path) < 5:
                return True

            unit = _UnitData("", "", is_headless=True)

            # NOTE: steam inventory id attribute is part of paintjob settings now, thus don't recover it
            #
            # # if old settings file has steam_inventory_id attribute, recover it!
            # old_settings_container = _sii_container.get_data_from_file(settings_sui_path, is_sui=True)
            # if old_settings_container and "steam_inventory_id" in old_settings_container[0].props:
            #    unit.props[] = int(old_settings_container[0].props["steam_inventory_id"])

            # force export of mandatory properties
            unit.props["name"] = self.pjs_name
            unit.props["price"] = self.pjs_price
            unit.props["unlock"] = self.pjs_unlock

            # now go trough all props and export the ones that are different from default value
            for props_dir_entry in dir(self.properties):
                if props_dir_entry.startswith("pjs_"):
                    assert self.append_prop_if_not_default(unit, props_dir_entry)

            return _sii_container.write_data_to_file(settings_sui_path, (unit,), is_sui=True, create_dirs=True)

        def append_prop_if_not_default(self, unit, prop_name, prop_value=None):
            """Appends property value into given unit instance, if property is different from default value.
            This way we will always write only needed values.

            :param unit: unit from container to be written
            :type unit: io_scs_tools.internals.structure.UnitData
            :param prop_name: name of the property that should be append
            :type prop_name: str
            :param prop_value: value of the property that should be append; if None instance is search for value instead
            :type prop_value: tuple | float | bool
            :return: True if property was found and properly processed; False if property is invalid
            :rtype: bool
            """

            _EPSILON = 0.0001  # float values max difference to be still equal
            _PJS_PREFIX = "pjs_"  # prefix that marks setting as paint job setting

            if not hasattr(self, prop_name):
                lprint("E Invalid property for paintjob settings: %r, contact the developer!", (prop_name,))
                return False

            # gather values
            default_value = _get_default(self.properties, prop_name)

            if prop_value is None:
                current_value = getattr(self, prop_name)
            else:
                current_value = prop_value

            if current_value is None or not prop_name.startswith(_PJS_PREFIX):
                lprint("E Invalid property for paintjob settings: %r, contact the developer!", (prop_name,))
                return False

            # do comparison of property differently for each type and convert current value if needed
            is_different = False
            if isinstance(default_value, list):

                values_as_list = []
                for item in current_value:

                    # we need prescribed interface, which is that array unit properties needs class which defines 'value'
                    # property where value of the property is saved
                    if not hasattr(item, "value"):
                        lprint("E Collection property %r is missing 'value' attribute, contact the developer!", (prop_name,))
                        return False

                    default_item_value = _get_default(item, "value")

                    if isinstance(default_item_value, tuple):
                        current_item_value = tuple(item.value)
                    else:
                        current_item_value = item.value

                    values_as_list.append(current_item_value)

                # collection properties are empty by default, thus any item added means it's different than default
                is_different = len(values_as_list) > 0

                # copy created values list back to current value to write it into unit as array item
                current_value = values_as_list

            elif isinstance(default_value, tuple):

                current_value = tuple(current_value)  # convert to tuple for proper export

                for i in range(0, len(default_value)):
                    if isinstance(default_value[i], float):
                        is_different |= abs(current_value[i] - default_value[i]) > _EPSILON
                    else:
                        is_different |= current_value[i] != default_value[i]

            elif isinstance(default_value, float):

                is_different = abs(current_value - default_value) > _EPSILON

            else:  # for bool, int and string we can compare them directly

                is_different = current_value != default_value

            # finally append property if different
            if is_different:
                unit.props[prop_name[len(_PJS_PREFIX):]] = current_value

            return True

        def execute(self, context):

            from time import time

            start_time = time()

            # clear message queue so that we will report only warnings and errors from this export!
            lprint("", report_warnings=1, report_errors=1)

            ##################################
            #
            # 1. parse & validate input settings
            #
            ##################################

            if not os.path.isfile(self.config_meta_filepath):
                self.do_report({'WARNING'}, "Given paintjob layout META file does not exist: %r!" % self.config_meta_filepath, do_report=True)
                return {'CANCELLED'}

            # get vehicle brand model token
            curr_dir = os.path.abspath(os.path.join(self.config_meta_filepath, os.pardir))
            brand_model_token = os.path.basename(curr_dir)

            # get vehicle type
            curr_dir = os.path.abspath(os.path.join(curr_dir, os.pardir))
            if os.path.basename(curr_dir) == _PT_consts.VehicleTypes.TRUCK:
                self.vehicle_type = _PT_consts.VehicleTypes.TRUCK
            elif os.path.basename(curr_dir) == _PT_consts.VehicleTypes.TRAILER:
                self.vehicle_type = _PT_consts.VehicleTypes.TRAILER
            else:
                self.do_report({'ERROR'}, "Given paintjob layout META file is in wrong directory!", do_report=True)
                return {'CANCELLED'}

            if not self.common_texture_path.endswith(".tif"):
                self.do_report({'ERROR'}, "Given common texture is not TIF file: %r!" % self.common_texture_path, do_report=True)
                return {'CANCELLED'}

            if not os.path.isfile(self.common_texture_path):
                self.do_report({'ERROR'}, "Given common texture file does not exist: %r!" % self.common_texture_path, do_report=True)
                return {'CANCELLED'}

            # solve project path, if not given try to get it from given common texture path
            if self.project_path != "":

                orig_project_path = _path_utils.readable_norm(self.project_path)

                if not os.path.isdir(orig_project_path):
                    self.do_report({'ERROR'}, "Given paintjob project path does not exist: %r!" % orig_project_path, do_report=True)
                    return {'CANCELLED'}

                # there has to be sibling base directory, otherwise we for sure aren't in right place
                if not os.path.isdir(os.path.join(os.path.join(orig_project_path, os.pardir), "base")):
                    self.do_report({'ERROR'}, "Given pointjob project path is invalid, can't find sibling 'base' project: %r" % orig_project_path,
                                   do_report=True)
                    return {'CANCELLED'}

            else:

                orig_project_path = _path_utils.readable_norm(os.path.dirname(self.common_texture_path))

                # we can simply go 5 dirs up, as paintjob has to be properly placed /vehicle/<vehicle_type>/upgrade/paintjob/<brand.model>
                for _ in range(0, 5):
                    orig_project_path = _path_utils.readable_norm(os.path.join(orig_project_path, os.pardir))

                if not os.path.isdir(orig_project_path):
                    self.do_report({'ERROR'},
                                   "Paintjob TGA seems to be saved outside proper structure, should be inside\n"
                                   "'<project_path>/vehicle/<vehicle_type>/upgrade/paintjob/<brand_model>/', instead is in:\n"
                                   "%r" % self.common_texture_path,
                                   do_report=True)
                    return {'CANCELLED'}

            # get paint job token from texture name
            pj_token = os.path.basename(self.common_texture_path)[:-4]

            if _name_utils.tokenize_name(pj_token) != pj_token:
                self.do_report({'ERROR'},
                               "Given common texture name is invalid, can't be tokenized (max. length: 11, accepted chars: a-z, 0-9, _): %r"
                               % pj_token,
                               do_report=True)
                return {'CANCELLED'}

            # get brand & model unit name from texture path
            common_tex_dirpath = _path_utils.readable_norm(os.path.join(self.common_texture_path, os.pardir))
            brand_model_dir = os.path.basename(common_tex_dirpath)

            underscore_idx = brand_model_dir.find("_")
            if underscore_idx == -1:
                self.do_report({'ERROR'},
                               "Paintjob TGA file parent directory name seems to be invalid should be '<brand_model>' instead is: %r." %
                               brand_model_dir,
                               do_report=True)
                return {'CANCELLED'}

            brand_token = brand_model_dir[0:underscore_idx]
            model_token = brand_model_dir[underscore_idx + 1:]

            is_common_tex_path_invalid = (
                    brand_model_token != brand_token + "." + model_token or
                    not common_tex_dirpath.endswith("/vehicle/" + self.vehicle_type + "/upgrade/paintjob/" + brand_model_dir)
            )

            if is_common_tex_path_invalid:
                self.do_report({'ERROR'},
                               "Paintjob TGA file isn't saved on correct place, should be inside\n"
                               "'<project_path>/vehicle/<vehicle_type>/upgrade/paintjob/%s' instead is saved in:\n"
                               "%r." % (brand_model_token.replace(".", "_"), common_tex_dirpath),
                               do_report=True)
                return {'CANCELLED'}

            lprint("D <brand>: %r, <model>: %r, <paintjob_unit_name>: %r" % (brand_token, model_token, pj_token))

            ##################################
            #
            # 2. parse and validate paintjob layout config file
            #
            ##################################

            pj_config_sii_container = _sii_container.get_data_from_file(self.config_meta_filepath)
            if not _sii_container.has_valid_unit_instance(pj_config_sii_container,
                                                          unit_type="paintjobs_metadata",
                                                          req_props=("common_texture_size",)):

                self.do_report({'ERROR'}, "Validation failed on SII: %r" % _path_utils.readable_norm(self.config_meta_filepath), do_report=True)
                return {'CANCELLED'}

            # interpret common texture size vector as two ints
            common_texture_size = [int(i) for i in _sii_container.get_unit_property(pj_config_sii_container, "common_texture_size")]

            # get and validate texture portion unit existence
            texture_portions = OrderedDict()
            texture_portion_names = _sii_container.get_unit_property(pj_config_sii_container, "texture_portions")
            if texture_portion_names:

                for unit_id in texture_portion_names:

                    texture_portion = _sii_container.get_unit_by_id(pj_config_sii_container, unit_id, "texture_portion_metadata")
                    if not texture_portion:
                        self.do_report({'WARNING'},
                                       "Ignoring used texture portion with name %r as it's not defined in paintjob layout meta data!" % unit_id)
                        continue

                    parent = texture_portion.get_prop("parent")
                    if parent and parent not in texture_portion_names:
                        self.do_report({'WARNING'},
                                       "Ignoring used texture portion with name %r as it's parent: %r "
                                       "is not defined in paintjob layout meta data!" % (unit_id, parent))
                        continue

                    texture_portions[unit_id] = texture_portion

            # collect master portions to be able to properly export all override paintjob masks and other paint job attributes
            master_portions = []
            no_model_sii_master_count = 0
            model_sii_master_count = 0
            master_unit_suffixes = set()
            for unit_id in texture_portions:

                texture_portion = texture_portions[unit_id]
                is_master = bool(texture_portion.get_prop("is_master"))
                master_unit_suffix = texture_portion.get_prop("master_unit_suffix", "")
                model_sii = texture_portion.get_prop("model_sii")

                if not is_master:
                    continue

                # check unique suffixes
                if master_unit_suffix in master_unit_suffixes:
                    self.do_report({'ERROR'},
                                   "Multiple master textures using same unit suffix: %r. "
                                   "Make sure all unit suffixes are unique." % master_unit_suffix,
                                   do_report=True)
                    return {'CANCELLED'}

                # check for no model sii definition
                if model_sii:
                    model_sii_master_count += 1
                else:
                    no_model_sii_master_count += 1

                master_unit_suffixes.add(master_unit_suffix)
                master_portions.append(texture_portion)

            if no_model_sii_master_count > 0 and (no_model_sii_master_count + model_sii_master_count) > 1:
                self.do_report({'ERROR'},
                               "One or more master texture portions detected without model SII path. "
                               "Either define model SII path for all of them or use only one master portion without it!",
                               do_report=True)
                return {'CANCELLED'}

            lprint("D Found texture portions: %r", (list(texture_portions.keys()),))

            ##################################
            #
            # 3. load common texture & export texture portions TGAs + TOBJs
            #
            ##################################

            common_tex_img = bpy.data.images.load(self.common_texture_path, check_existing=False)
            common_tex_img.colorspace_settings.name = "sRGB"
            common_tex_img.alpha_mode = 'STRAIGHT' if self.export_alpha else 'NONE'

            self.initialize_nodes(context, common_tex_img)

            if tuple(common_tex_img.size) != tuple(common_texture_size) and not self.export_configs_only:
                self.do_report({'ERROR'},
                               "Wrong size of common texture TGA: [%s, %s], paintjob layout META is prescribing different size: %r!" %
                               (common_tex_img.size[0], common_tex_img.size[1], common_texture_size),
                               do_report=True)
                return {'CANCELLED'}

            # get textures export dir
            tgas_dir_path = os.path.join(common_tex_dirpath, pj_token)

            # first remove old TGAs, TOBJs if directory already exists
            if os.path.isdir(tgas_dir_path):
                for file in os.listdir(tgas_dir_path):
                    current_file_path = os.path.join(tgas_dir_path, file)
                    if os.path.isfile(current_file_path) and (current_file_path.endswith(".tga") or current_file_path.endswith(".tobj")):
                        os.remove(current_file_path)

            # do export by portion id
            texture_portions_tobj_paths = {}  # storing TGA paths for each texture portion, used later for referencing textures in SIIs
            exported_portion_textures = set()  # storing already exported texture portion to avoid double exporting same TGA
            for unit_id in texture_portions:

                # skip texture export if we are doing only configs
                if self.export_configs_only:
                    break

                texture_portion = texture_portions[unit_id]

                # as parented texture portions do not own texture just ignore them
                if texture_portions[unit_id].get_prop("parent"):
                    continue

                # mark this portion as exported
                exported_portion_textures.add(texture_portion.id)

                # export TGA & save TOBJ path to dictionary for later usage in config generation
                exported_tobj_path = self.export_texture(common_tex_img, tgas_dir_path, texture_portion)
                assert exported_tobj_path is not None  # nothing should go wrong thus we have to assert here
                texture_portions_tobj_paths[unit_id] = exported_tobj_path

                lprint("I Exported: %r", (exported_tobj_path,))

            ##################################
            #
            # 4. create configs
            #
            ##################################

            # collect all possible projects for later search of model sii files
            game_project_path = _path_utils.readable_norm(os.path.join(orig_project_path, os.pardir))  # search for game project path
            if os.path.basename(game_project_path).startswith("dlc_") or os.path.basename(game_project_path).startswith("mod_"):
                game_project_path = _path_utils.readable_norm(os.path.join(game_project_path, os.pardir))

            project_paths = sorted(_path_utils.get_projects_paths(game_project_path), reverse=True)  # sort them so dlcs & mods have priority
            vehicle_def_subdir = os.path.join("def/vehicle/" + self.vehicle_type, brand_model_token)

            # prepare overrides and their directory path: "/def/vehicle/<vehicle_type>/<brand.model>/paint_job/accessory/"
            overrides = {}

            overrides_config_dir = os.path.join(orig_project_path, vehicle_def_subdir)
            overrides_config_dir = os.path.join(overrides_config_dir, "paint_job")
            overrides_config_dir = os.path.join(overrides_config_dir, "accessory")

            # delete old overrides files for this paintjob if they exists
            if os.path.isdir(overrides_config_dir):
                for file in os.listdir(overrides_config_dir):
                    pj_config_path = os.path.join(overrides_config_dir, file)
                    # match beginning and end of the file name
                    if os.path.isfile(pj_config_path) and file.startswith(pj_token) and file.endswith(".sii"):
                        os.remove(pj_config_path)

            # iterate texture portions, write master configs and collect overrides
            for unit_id in texture_portions:

                texture_portion = texture_portions[unit_id]

                model_sii = texture_portion.get_prop("model_sii", "")
                is_master = bool(texture_portion.get_prop("is_master"))

                # master can exist without model sii reference!
                requires_valid_model_sii = (not is_master) or (model_sii != "")

                parent = curr_parent = texture_portion.get_prop("parent")
                while curr_parent:
                    parent = curr_parent
                    curr_parent = texture_portions[parent].get_prop("parent")

                # don't collect override for texture portions when top most parent is master
                if parent and bool(texture_portions[parent].get_prop("is_master")):
                    continue

                # check for SIIs from "model_sii" in all projects
                model_sii_subpath = os.path.join(vehicle_def_subdir, model_sii)

                model_sii_path = os.path.join(orig_project_path, model_sii_subpath)

                sii_exists = False
                for project_path in project_paths:

                    model_sii_path = os.path.join(project_path, model_sii_subpath)

                    if os.path.isfile(model_sii_path):  # just take first found path
                        sii_exists = True
                        break

                if not sii_exists and requires_valid_model_sii:
                    self.do_report({'ERROR'},
                                   "Can't find referenced 'model_sii' file for texture portion %r, aborting overrides SII write!" %
                                   texture_portion.id,
                                   do_report=True)
                    return {'CANCELLED'}

                # assamble paintjob properties that will be written in overrides SII (currently: paint_job_mask, flake_uvscale, flake_vratio)
                pj_props = OrderedDict()

                # collect paintjob mask texture
                if not self.export_configs_only:
                    tobj_paths_unit_id = texture_portions[parent].id if parent else unit_id
                    rel_tobj_path = os.path.relpath(texture_portions_tobj_paths[tobj_paths_unit_id], orig_project_path)
                    pj_props["paint_job_mask"] = _path_utils.readable_norm("/" + rel_tobj_path)

                # export either master paint job config or collect override
                if is_master:

                    master_unit_suffix = texture_portion.get_prop("master_unit_suffix", "")
                    suffixed_pj_unit_name = pj_token + master_unit_suffix
                    if _name_utils.tokenize_name(suffixed_pj_unit_name) != suffixed_pj_unit_name:
                        self.do_report({'ERROR'},
                                       "Can't tokenize generated paintjob unit name: %r for texture portion %r, aborting SII write!" %
                                       (suffixed_pj_unit_name, texture_portion.id),
                                       do_report=True)
                        return {'CANCELLED'}

                    # get model sii unit name to use it in suitable for field
                    model_sii_cont = _sii_container.get_data_from_file(model_sii_path)
                    if not model_sii_cont and requires_valid_model_sii:
                        self.do_report({'ERROR'},
                                       "SII is there but getting unit name from 'model_sii' failed for texture portion %r, aborting SII write!" %
                                       texture_portion.id,
                                       do_report=True)
                        return {'CANCELLED'}

                    # unit name of referenced model sii used for suitable_for field in master paint jobs
                    pj_suitable_for = []
                    if model_sii_cont:
                        pj_suitable_for.append(model_sii_cont[0].id)

                    # if there are any other suitables in master texture portion also add it
                    suitable_for = texture_portion.get_prop("suitable_for", [])
                    pj_suitable_for.extend(suitable_for)

                    # config path: "/def/vehicle/<vehicle_type>/<brand.model>/paint_job/<pj_unit_name>.sii"
                    config_path = os.path.join(orig_project_path, vehicle_def_subdir)
                    config_path = os.path.join(config_path, "paint_job")
                    config_path = os.path.join(config_path, suffixed_pj_unit_name + ".sii")

                    # full paint job unit name: <pj_unit_name>.<brand.model>.paint_job
                    pj_full_unit_name = suffixed_pj_unit_name + "." + brand_model_token + ".paint_job"

                    assert self.export_master_sii(config_path, pj_token, pj_full_unit_name, pj_props, pj_suitable_for)
                    lprint("I Created master SII config for %r: %r", (texture_portion.id, config_path))

                else:

                    model_type = str(model_sii).split("/")[0]

                    if model_type in ("accessory", "cabin", "chassis", "body"):

                        model_sii_cont = _sii_container.get_data_from_file(model_sii_path)
                        acc_id_token = model_sii_cont[0].id.split(".")[0]  # first token
                        acc_type_token = model_sii_cont[0].id.split(".")[-1]  # last token

                        if parent:
                            portion_size = [float(i) for i in texture_portions[parent].get_prop("size")]
                        else:
                            portion_size = [float(i) for i in texture_portion.get_prop("size")]

                        # as override paintjob masks are dependent on original paintjob unit name
                        # we have to create override configs for each master portion
                        for master_portion in master_portions:

                            master_size = [float(i) for i in master_portion.get_prop("size")]
                            master_unit_suffix = master_portion.get_prop("master_unit_suffix", "")

                            if self.pjs_flipflake:

                                # calculate flake uv scale by width of textures
                                pj_props["flake_uvscale"] = (portion_size[0] / master_size[0]) * self.pjs_flake_uvscale

                                # calculate vratio by calculating height of portion if it would be in ratio of master texture and
                                # then just divide original texture height with calculated one
                                pj_props["flake_vratio"] = portion_size[1] / (master_size[1] * portion_size[0] / master_size[0])

                            # don't create override if there is no properties to override!
                            if len(pj_props) == 0:
                                continue

                            # ensure current master portion has it's own overrides
                            config_path = os.path.join(overrides_config_dir, pj_token + master_unit_suffix + ".sii")
                            if config_path not in overrides:
                                overrides[config_path] = PaintjobTools.SCS_TOOLS_OT_GeneratePaintjob.Overrides()

                            # now add current accessory to overrides
                            overrides[config_path].add_accessory(acc_type_token + "." + acc_id_token, pj_props)

                    else:

                        self.do_report({'ERROR'},
                                       "Can not collect override for texture portion: %r, as 'model_sii' property is not one of: "
                                       "accessory, cabin or chassis neither is texture portion marked with 'is_master'!" %
                                       texture_portion.id,
                                       do_report=True)
                        return {'CANCELLED'}

            # export overrides SII files
            for config_path in overrides:
                assert overrides[config_path].export_to_sii(self, config_path)
                lprint("I Create override SII: %r", (config_path,))

            # finally we can remove original TGA
            if not self.preserve_common_texture and os.path.isfile(self.common_texture_path):
                os.remove(self.common_texture_path)

            self.do_report({'INFO'}, "Export of paintjobs took: %0.3f sec" % (time() - start_time), do_report=True)
            return {'FINISHED'}


classes = (
    Animation.SCS_TOOLS_OT_IncreaseAnimationSteps,
    Animation.SCS_TOOLS_OT_DecreaseAnimationSteps,

    ConversionHelper.SCS_TOOLS_OT_AddConversionPath,
    ConversionHelper.SCS_TOOLS_OT_CleanConversionRSRC,
    ConversionHelper.SCS_TOOLS_OT_ConvertAllPaths,
    ConversionHelper.SCS_TOOLS_OT_ConvertCurrentBase,
    ConversionHelper.SCS_TOOLS_OT_ConvertCustomPaths,
    ConversionHelper.SCS_TOOLS_OT_FindGameModFolder,
    ConversionHelper.SCS_TOOLS_OT_OrderConversionPath,
    ConversionHelper.SCS_TOOLS_OT_RemoveConversionPath,
    ConversionHelper.SCS_TOOLS_OT_RunConversion,
    ConversionHelper.SCS_TOOLS_OT_RunPacking,

    Export.SCS_TOOLS_OT_ExportAnimAction,
    Export.SCS_TOOLS_OT_ExportByScope,

    Import.SCS_TOOLS_OT_ImportAnimActions,

    Log.SCS_TOOLS_OT_CopyLogToClipboard,

    PaintjobTools.SCS_TOOLS_OT_ExportPaintjobUVLayoutAndMesh,
    PaintjobTools.SCS_TOOLS_OT_GeneratePaintjob.ColorVariantItem,
    PaintjobTools.SCS_TOOLS_OT_GeneratePaintjob,
    PaintjobTools.SCS_TOOLS_OT_ImportFromDataSII,

    Paths.SCS_TOOLS_OT_SelectProjectPath,
    Paths.SCS_TOOLS_OT_SelectShaderPresetsPath,
    Paths.SCS_TOOLS_OT_SelectTriggerActionsLibPath,
    Paths.SCS_TOOLS_OT_SelectSignLibPath,
    Paths.SCS_TOOLS_OT_SelectSemaphoreLibPath,
    Paths.SCS_TOOLS_OT_SelectTrafficRulesLibPath,
    Paths.SCS_TOOLS_OT_SelectHookupLibPath,
    Paths.SCS_TOOLS_OT_SelectMatSubsLibPath,
    Paths.SCS_TOOLS_OT_SelectSunProfilesLibPath,
    Paths.SCS_TOOLS_OT_SelectDirInsideBase,
    Paths.SCS_TOOLS_OT_ReloadLibrary,
    Paths.SCS_TOOLS_OT_AddPathPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
