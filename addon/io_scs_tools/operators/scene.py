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
import subprocess
import shutil
from hashlib import sha1
from sys import platform
from bpy.props import StringProperty, CollectionProperty, EnumProperty, IntProperty, BoolProperty
from io_scs_tools.consts import ConvHlpr as _CONV_HLPR_consts
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.property import get_filebrowser_display_type
from io_scs_tools import exp as _export
from io_scs_tools import imp as _import


class Import:
    """
    Wrapper class for better navigation in file
    """

    class ImportAnimActions(bpy.types.Operator):
        bl_label = "Import SCS Animation (PIA)"
        bl_idname = "scene.import_scs_anim_actions"
        bl_description = "Import SCS Animation files (PIA) as a new SCS animations"

        directory = StringProperty(
            name="Import PIA Directory",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        files = CollectionProperty(
            type=bpy.types.OperatorFileListElement,
            options={'HIDDEN', 'SKIP_SAVE'},
        )
        filter_glob = StringProperty(default="*.pia", options={'HIDDEN'})

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

    class ExportByScope(bpy.types.Operator):
        """Export selected operator."""
        bl_idname = "scene.export_scs_content_by_scope"
        bl_label = "Export By Used Scope"
        bl_description = "Export SCS models depending on selected export scope."
        bl_options = set()

        @staticmethod
        def execute_rotation(rot_direction):
            """Uses Blender orbit rotation to rotate all 3D views
            :param rot_direction: "ORBITLEFT" | "ORBITRIGHT" | "ORBITUP" | "ORBITDOWN"
            :type rot_direction: str
            """
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    override = {
                        'window': bpy.context.window,
                        'screen': bpy.context.screen,
                        'blend_data': bpy.context.blend_data,
                        'scene': bpy.context.scene,
                        'region': area.regions[4],
                        'area': area
                    }
                    bpy.ops.view3d.view_orbit(override, type=rot_direction)

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

        def __init__(self):
            """Shows all layer to be able to alter selection on the whole scene and
            alter Blender selection the way that:
            1. if only child within root is selected -> selects root too
            2. if only root is selected -> select all children
            3. if root and some children are selected -> don't change selection
            """
            self.layers_visibilities = _view3d_utils.switch_layers_visibility([], True)
            self.last_active_obj = bpy.context.active_object
            self.altered_objs = []
            self.altered_objs_visibilities = []
            self.not_root_objs = []

            for obj in bpy.context.selected_objects:
                root = _object_utils.get_scs_root(obj)
                if root:
                    if root != obj:
                        if not root.select:
                            root.select = True
                            self.altered_objs.append(root.name)
                    else:
                        children = _object_utils.get_children(obj)
                        local_reselected_objs = []
                        for child_obj in children:
                            local_reselected_objs.append(child_obj.name)
                            # if some child is selected this means we won't reselect nothing in this game objecdt
                            if child_obj.select:
                                local_reselected_objs = []
                                break
                        self.altered_objs.extend(local_reselected_objs)
                else:
                    obj.select = False
                    self.not_root_objs.append(obj.name)

            for obj_name in self.altered_objs:
                self.altered_objs_visibilities.append(bpy.data.objects[obj_name].hide)
                bpy.data.objects[obj_name].hide = False
                bpy.data.objects[obj_name].select = True

        def __del__(self):
            """Revert altered initial selection and layers visibilites
            """

            # saftey check if it's not deleting last instance
            if hasattr(self, "altered_objs"):
                i = 0
                for obj_name in self.altered_objs:
                    bpy.data.objects[obj_name].hide = self.altered_objs_visibilities[i]
                    i += 1
                    bpy.data.objects[obj_name].select = False

                for obj_name in self.not_root_objs:
                    bpy.data.objects[obj_name].select = True

                if self.last_active_obj is not None:
                    # call selection twice to actually change active object
                    self.last_active_obj.select = not self.last_active_obj.select
                    self.last_active_obj.select = not self.last_active_obj.select

                _view3d_utils.switch_layers_visibility(self.layers_visibilities, False)

        def execute_export(self, context, disable_local_view):
            """Actually executes export of current selected objects (bpy.context.selected_objects)

            :param context: operator context
            :type context: bpy_struct
            :param disable_local_view: True if you want to disable local view after export
            :type disable_local_view: bool
            :return: succes of batch export
            :rtype: {'FINISHED'} | {'CANCELLED'}
            """

            init_obj_list = ()
            export_scope = _get_scs_globals().export_scope
            if export_scope == "selection":
                init_obj_list = tuple(bpy.context.selected_objects)
            elif export_scope == "scene":
                init_obj_list = tuple(bpy.context.scene.objects)
            elif export_scope == "scenes":
                init_obj_list = tuple(bpy.data.objects)

            try:
                result = _export.batch_export(self, init_obj_list)
            except Exception as e:

                result = {"CANCELLED"}
                context.window.cursor_modal_restore()

                import traceback

                trace_str = traceback.format_exc().replace("\n", "\n\t   ")
                lprint("E Unexpected %r accured during batch export:\n\t   %s",
                       (type(e).__name__, trace_str),
                       report_errors=1,
                       report_warnings=1)

            if disable_local_view:
                _view3d_utils.switch_local_view(False)

            return result

        def modal(self, context, event):

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
            elif event.type in ('RET', 'NUMPAD_ENTER'):
                return self.execute_export(context, True)
            elif event.type == 'ESC':
                _view3d_utils.switch_local_view(False)
                return {'CANCELLED'}

            return {'RUNNING_MODAL'}

        def invoke(self, context, event):
            # show preview or directly execute export
            if _get_scs_globals().export_scope == "selection":

                if _get_scs_globals().preview_export_selection:

                    if len(context.selected_objects) == 0:
                        print(self.not_root_objs)
                        if len(self.not_root_objs) > 0:
                            msg = "Selected objects are not part of any SCS Game Object!"
                        else:
                            msg = "Nothing selected!"
                        self.report({'ERROR'}, msg)
                        return {'FINISHED'}

                    _view3d_utils.switch_local_view(True)
                    context.window_manager.modal_handler_add(self)
                    return {'RUNNING_MODAL'}

            return self.execute_export(context, False)

    class ExportAnimAction(bpy.types.Operator):
        bl_label = "Export SCS Animation (PIA)"
        bl_idname = "scene.export_scs_anim_action"
        bl_description = "Select directory and export SCS animation (PIA) to it."
        bl_options = {'INTERNAL'}

        index = IntProperty(
            name="Anim Index",
            default=False,
            options={'HIDDEN'}
        )

        directory = StringProperty(
            name="Export PIA Directory",
            subtype='DIR_PATH',
        )
        filename_ext = ".pia"
        filter_glob = StringProperty(default=str("*" + filename_ext), options={'HIDDEN'})

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
                _export.pia.export(scs_root_obj, armature, anim, self.directory, skeleton_filepath)

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

    class SCSProjectPath(bpy.types.Operator):
        """Operator for setting an absolute path to SCS Project Directory."""
        bl_label = "Select SCS Project Directory"
        bl_idname = "scene.select_scs_project_path"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        directory = StringProperty(
            name="SCS Project Directory Path",
            description="SCS project directory path",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob = StringProperty(default="*.*", options={'HIDDEN'})

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

    class ShaderPresetsFilePath(bpy.types.Operator):
        """Operator for setting relative or absolute path to Shader Presets Library file."""
        bl_label = "Select Shader Presets Library File"
        bl_idname = "scene.select_shader_presets_filepath"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Shader Presets Library File",
            description="Shader Presets library relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})

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

    class TriggerActionsRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Trigger actions file."""
        bl_label = "Select Trigger Actions File"
        bl_idname = "scene.select_trigger_actions_rel_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Trigger Actions File",
            description="Trigger actions relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class SignLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Sign Library file."""
        bl_label = "Select Sign Library File"
        bl_idname = "scene.select_sign_library_rel_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Sign Library File",
            description="Sign library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class TSemLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Semaphore Profile Library file."""
        bl_label = "Select Traffic Semaphore Profile Library File"
        bl_idname = "scene.select_tsem_library_rel_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Traffic Semaphore Profile Library File",
            description="Traffic Semaphore Profile library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class TrafficRulesLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Rules Library file."""
        bl_label = "Select Traffic Rules Library File"
        bl_idname = "scene.select_traffic_rules_library_rel_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Traffic Rules Library File",
            description="Traffic Rules library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class HookupLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Hookup files."""
        bl_label = "Select Hookup Library Directory"
        bl_idname = "scene.select_hookup_library_rel_path"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        directory = StringProperty(
            name="Hookup Library Directory Path",
            description="Hookup library directory path",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class MatSubsLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Material Substance shader files."""
        bl_label = "Select Material Substance Library File"
        bl_idname = "scene.select_matsubs_library_rel_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Material Substance Library File",
            description="Material Substance library relative file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.db", options={'HIDDEN'})

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

    class SunProfilesLibraryPath(bpy.types.Operator):
        """Operator for setting relative path to Material Substance shader files."""
        bl_label = "Select Sun Profiles Library File"
        bl_idname = "scene.select_sun_profiles_lib_path"
        bl_description = "Open a file browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        filepath = StringProperty(
            name="Sun Profiles Library File",
            description="Sun Profiles library relative/absolute file path",
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.sii", options={'HIDDEN'})

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

    class DirSelectorInsideBase(bpy.types.Operator):
        """Operator for setting relative or absolute path to Global Export file."""
        bl_label = "Select Directory"
        bl_idname = "scene.select_directory_inside_base"
        bl_description = "Open a directory browser"

        # always set default display type so blender won't be using "last used"
        display_type = get_filebrowser_display_type()

        directory = StringProperty(
            name="Directory",
            description="Directory inside SCS Project Base path",
            subtype='DIR_PATH',
        )

        type = EnumProperty(
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

        filter_glob = StringProperty(default="*.pim", options={'HIDDEN'})

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

    class ReloadLibraryPath(bpy.types.Operator):
        """Operator for reloading given library."""
        bl_label = "Reload"
        bl_idname = "scene.scs_reload_library"
        bl_description = "Reloads library and updates it with any possible new entries."

        library_path_attr = StringProperty()

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


class Animation:
    """
    Wraper class for better navigation in file
    """

    class IncreaseAnimationSteps(bpy.types.Operator):
        bl_label = "Increase Animation Steps"
        bl_idname = "scene.increase_animation_steps"
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

    class DecreaseAnimationSteps(bpy.types.Operator):
        bl_label = "Decrease Animation Steps"
        bl_idname = "scene.decrease_animation_steps"
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
                scene.frame_start /= 2
                scene.frame_end /= 2

                # INCREASE PREVIEW RANGE
                scene.frame_preview_start /= 2
                scene.frame_preview_end /= 2

                # INCREASE END FRAME NUMBER IN ALL ANIMATIONS THAT USES THE ACTUAL ACTION
                for anim in inventory:
                    if anim.action == action.name:
                        anim.anim_start /= 2
                        anim.anim_end /= 2

                # INCREASE EXPORT STEP
                # print('anim_export_step: %s' % str(action.scs_props.anim_export_step))
                action.scs_props.anim_export_step /= 2

            return {'FINISHED'}


class ConversionHelper:
    """
    Wraper class for better navigation in file
    """

    class CleanRSRC(bpy.types.Operator):
        bl_label = "Clean RSRC"
        bl_idname = "scene.scs_conv_hlpr_clean_rsrc"
        bl_description = "Cleans 'rsrc' folder from any already converted content"

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
                    shutil.rmtree(root + os.sep + folder)
                for file in files:
                    os.remove(root + os.sep + file)

            self.report({'INFO'}, "Successfully cleaned 'rsrc' folder!")
            return {'FINISHED'}

    class AddConversionPath(bpy.types.Operator):
        bl_label = "Add Path"
        bl_idname = "scene.scs_conv_hlpr_add_path"
        bl_description = "Adds new path to the stack of paths for conversion"

        directory = StringProperty(
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

    class RemoveConversionPath(bpy.types.Operator):
        bl_label = "Remove Path"
        bl_idname = "scene.scs_conv_hlpr_remove_path"
        bl_description = "Removes path from the stack of paths for conversion"

        def execute(self, context):
            scs_globals = _get_scs_globals()

            i = scs_globals.conv_hlpr_custom_paths_active
            scs_globals.conv_hlpr_custom_paths.remove(i)

            if scs_globals.conv_hlpr_custom_paths_active > 0:
                scs_globals.conv_hlpr_custom_paths_active -= 1

            return {'FINISHED'}

    class OrderConversionPath(bpy.types.Operator):
        bl_label = "Order Path"
        bl_idname = "scene.scs_conv_hlpr_order_path"
        bl_description = "Change order for the current path"

        move_up = BoolProperty(default=True)

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

    class RunConversion(bpy.types.Operator):
        bl_label = "Run Conversion"
        bl_idname = "scene.scs_conv_hlpr_run"
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

                # NOTE: we are assuming that user installed wine as we did through easiest way:
                # downloading winebottler and then just drag&drop to applications
                wineconsole_path = "/Applications/Wine.app/Contents/Resources/bin/wineconsole"

                if os.system("command -v wineconsole") == 0:

                    command = ["wineconsole " + os.path.join(main_path, "convert.cmd")]

                elif os.path.isfile(wineconsole_path):

                    command = [wineconsole_path + " " + os.path.join(main_path, "convert.cmd")]

                else:
                    self.report({'ERROR'}, "Conversion aborted! Please install at least Wine application from WineBottler, "
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

    class ConvertCurrentBase(bpy.types.Operator):
        bl_label = "Convert Current Base"
        bl_idname = "scene.scs_conv_hlpr_convert_current"
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

            with open(extra_mount_path, mode="w") as f:
                f.write(link_hash)

            return ConversionHelper.RunConversion.execute(self, context)

    class ConvertCustomPaths(bpy.types.Operator):
        bl_label = "Convert Custom Paths"
        bl_idname = "scene.scs_conv_hlpr_convert_custom"
        bl_description = "Converts all paths given in Custom Paths list (order is the same as they appear in the list)"

        include_current_project = BoolProperty(
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

            with open(extra_mount_path, mode="w") as f:

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

            return ConversionHelper.RunConversion.execute(self, context)

    class FindGameModFolder(bpy.types.Operator):
        bl_label = "Search SCS Game 'mod' Folder"
        bl_idname = "scene.scs_conv_hlpr_find_mod_folder"
        bl_description = "Search for given SCS game 'mod' folder and set it as mod destination"

        game = EnumProperty(
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

    class RunPacking(bpy.types.Operator):
        bl_label = "Run Packing"
        bl_idname = "scene.scs_conv_hlpr_pack"
        bl_description = "Pack converted sources from 'rsrc' to mod package and copy it to mod destination path."

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
                    bpy.ops.scene.scs_conv_hlpr_clean_rsrc()
                except RuntimeError as e:
                    self.report({'ERROR'}, e.args[0])
                    return {'CANCELLED'}

            if scs_globals.conv_hlpr_export_on_packing:

                try:
                    bpy.ops.export_mesh.pim()
                except RuntimeError as e:
                    self.report({'ERROR'}, e.args[0])
                    return {'CANCELLED'}

            if scs_globals.conv_hlpr_convert_on_packing:

                try:
                    if len(scs_globals.conv_hlpr_custom_paths) > 0:
                        bpy.ops.scene.scs_conv_hlpr_convert_custom(include_current_project=True)
                    else:
                        bpy.ops.scene.scs_conv_hlpr_convert_current()
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
                shutil.rmtree(mod_filepath_as_dir)

            # make sure previous ZIP file is not present
            if os.path.isfile(mod_filepath):
                os.remove(mod_filepath)

            # do copy or zipping
            if scs_globals.conv_hlpr_mod_compression == _CONV_HLPR_consts.NoZip:

                for converted_dir in os.listdir(rsrc_path):  # use old conversion tools behaviour and pack everything that is in rsrc

                    curr_dir = os.path.join(os.path.join(rsrc_path, converted_dir), "@cache")
                    if not os.path.isdir(curr_dir):
                        continue

                    shutil.copytree(curr_dir, mod_filepath_as_dir)

                self.report({'INFO'}, "Packing done, mod copied to: '%s'" % mod_filepath_as_dir)

            else:

                from zipfile import ZipFile

                with ZipFile(mod_filepath, 'w') as myzip:

                    for converted_dir in os.listdir(rsrc_path):  # use old conversion tools behaviour and pack everything that is in rsrc

                        curr_dir = os.path.join(os.path.join(rsrc_path, converted_dir), "@cache")
                        if not os.path.isdir(curr_dir):
                            continue

                        for root, dirs, files in os.walk(curr_dir):

                            for file in files:

                                abs_file = os.path.join(root, file)
                                # Extract archive path+name, do conversion to proper slashes
                                # as zipfile namelist is returning only normal slashes even on windows and
                                # as last remove leading slash as zipfile namelist again doesn't have it.
                                archive_file = abs_file.replace(curr_dir, "").replace("\\", "/").lstrip("/")

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

    class CopyLogToClipboard(bpy.types.Operator):
        bl_label = "Copy BT Log To Clipboard"
        bl_idname = "scene.scs_copy_log"
        bl_description = "Copies whole Blender Tools log to clipboard (log was captured since Blender startup)."

        def execute(self, context):
            from io_scs_tools.utils.printout import get_log

            text = bpy.data.texts.new("SCS BT Log")

            override = {
                'window': bpy.context.window,
                'region': None,
                'area': None,
                'edit_text': text,
            }
            bpy.ops.text.insert(override, text=get_log())
            bpy.ops.text.select_all(override)
            bpy.ops.text.copy(override)

            bpy.data.texts.remove(text, do_unlink=True)

            self.report({'INFO'}, "Blender Tools log copied to clipboard!")
            return {'FINISHED'}
