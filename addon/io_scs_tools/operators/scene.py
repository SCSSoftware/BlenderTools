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
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import animation as _anim_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools import exp as _export
from io_scs_tools import imp as _import


class Look:
    """
    Wrapper class for better navigation in file
    """
    '''
    class AddLook(bpy.types.Operator):
        """Triggers adding of a new Look name into Look list."""
        bl_label = "Add Look"
        bl_idname = "scene.add_look"
        bl_description = "Create a new Look name"

        def execute(self, context):
            lprint('D Add Look...')
            bpy.ops.scene.add_look_dialog_operator('INVOKE_DEFAULT')
            return {'FINISHED'}

    class AddLookDialogOperator(bpy.types.Operator):
        """Makes a dialog window allowing specifying a new Look name and adds it into Look list."""
        bl_idname = "scene.add_look_dialog_operator"
        bl_label = "Add Look"

        look_string = StringProperty(name="Name for a new look:")

        def execute(self, context):
            lprint('D Add Look (dialog)...')
            source_look = _utils.get_actual_look()
            print('  source_look: %r (AddLookDialogOperator())' % source_look)
            for material in bpy.data.materials:
                cgfx_utils.cgfx_rec_copy(material, source_look, self.look_string)
            _utils.add_look_to_inventory(self.look_string)
            return {'FINISHED'}

        def invoke(self, context, event):
            self.look_string = ""
            return context.window_manager.invoke_props_dialog(self)

    class RenameLook(bpy.types.Operator):
        """Triggers renaming of active Look name in Look list."""
        bl_label = "Rename Look"
        bl_idname = "scene.rename_look"
        bl_description = "Rename active Look"

        def execute(self, context):
            lprint('D Rename Look...')
            bpy.ops.scene.rename_look_dialog_operator('INVOKE_DEFAULT')
            return {'FINISHED'}

    def rename_look_in_materials(old_look_name, new_look_name):
        """Rename a Look record in all materials."""
        for material in bpy.data.materials:
            material.scs_cgfx_looks[old_look_name].name = new_look_name

    class RenameLookDialogOperator(bpy.types.Operator):
        """Makes a dialog window allowing specifying a new Look name and replace it instead of the active Look name in Look list."""
        bl_idname = "scene.rename_look_dialog_operator"
        bl_label = "Rename Look"

        look_string = StringProperty(name="New name for a look:")

        def execute(self, context):
            lprint('D Rename Look (dialog)...')
            new_look_name = _utils.remove_diacritic(self.look_string)
            if new_look_name != "":
                if not _utils.inventory_has_item(bpy.context.scene.scs_look_inventory, new_look_name):
                    for look in bpy.context.scene.scs_look_inventory:
                        if look.active:
                            old_look_name = look.name
                            rename_look_in_materials(old_look_name, new_look_name)
                            look.name = new_look_name
                else:
                    self.report({'INFO'}, "'%s' is already defined!" % new_look_name)
            # self.report({'INFO'}, "'%s'" % new_look_name)
            return {'FINISHED'}

        def invoke(self, context, event):
            self.look_string = _utils.get_actual_look()
            return context.window_manager.invoke_props_dialog(self)

    def delete_look_from_materials(delete_look_index):
        """Delete a Look record from all materials."""
        for material in bpy.data.materials:
            material.scs_cgfx_looks.remove(delete_look_index)

    class DeleteLook(bpy.types.Operator):
        """Deletes the active Look name from Look list."""
        bl_label = "Delete Look"
        bl_idname = "scene.delete_look"
        bl_description = "Delete active Look"

        def execute(self, context):
            lprint('D Delete Look...')
            delete_look_index = None
            newly_assigned_look = None
            if len(bpy.context.scene.scs_look_inventory) != 1:
                for look_i, look in enumerate(bpy.context.scene.scs_look_inventory):
                    if look.active:
                        delete_look_index = look_i
                    else:
                        if not newly_assigned_look:  # NOTE: Set as active the first Look found.
                            newly_assigned_look = look.name
                            look.active = True
                if delete_look_index is not None:
                    bpy.context.scene.scs_look_inventory.remove(delete_look_index)
                    delete_look_from_materials(delete_look_index)
                    # TODO: Regenerate UI from actual MatLook CgFX Record here!
                else:
                    lprint('W No active Look for deletion!')
            else:
                lprint('I Cannot delete the last Look name!')
            return {'FINISHED'}

    class PrintLookInventory(bpy.types.Operator):
        """Look System debug prints..."""
        bl_label = "Print Look Inventory"
        bl_idname = "scene.print_look_inventory"

        def execute(self, context):
            print('Print Look Inventory...')
            for look in bpy.context.scene.scs_look_inventory:
                if look.active:
                    print('  X Look: "%s"' % look.name)
                else:
                    print('  o Look: "%s"' % look.name)
            return {'FINISHED'}
    '''


class Import:
    """
    Wrapper class for better navigation in file
    """

    class ImportAnimActions(bpy.types.Operator):
        bl_label = "Import SCS Animation (PIA)"
        bl_idname = "scene.import_scs_anim_actions"
        bl_description = "Import SCS Animation files (PIA) as a new Actions"

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

        def execute(self, context):
            lprint('D Import Animation Action...')

            '''
            print('  o directory: %r' % str(self.directory))
            print('  o files:')
            for file in self.files:
                print('  o   file: %r' % str(file.name))
            '''

            pia_files = [os.path.join(self.directory, file.name) for file in self.files]

            if context.active_object.type == 'ARMATURE':
                armature = context.active_object
            else:
                return {'CANCELLED'}

            skeleton = None
            bones = None

            '''
            for file in pia_files:
                print('  o   file: %r' % str(file))
            '''
            root_object = _object_utils.get_scs_root(armature)

            lprint('S armature: %s\nskeleton: %s\nbones: %s\n', (str(armature), str(skeleton), str(bones)))
            _import.pia.load(root_object, pia_files, armature)  # , skeleton, bones)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


class Export:
    """
    Wrapper class for better navigation in file
    """

    class ExportSelected(bpy.types.Operator):
        """Export selected operator."""
        bl_idname = "scene.export_selected"
        bl_label = "Export selected"
        bl_description = "Export selected objects only"

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
                _get_scs_globals().content_type = 'selection'  # NOTE: I'm not sure if this is still necessary.

            try:
                result = _export.batch_export(self, tuple(bpy.context.selected_objects), exclude_switched_off=False)
            except Exception as e:

                result = {"CANCELLED"}
                context.window.cursor_modal_restore()

                import traceback

                traceback.print_exc()
                lprint("E Unexpected %r accured during batch export, see stack trace above.",
                       (type(e).__name__,),
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
            if len(context.selected_objects) != 0:
                # show preview or directly execute export
                if context.scene.scs_props.preview_export_selection:
                    _view3d_utils.switch_local_view(True)
                    context.window_manager.modal_handler_add(self)
                    return {'RUNNING_MODAL'}
                else:
                    return self.execute_export(context, False)
            else:
                self.report({'ERROR'}, "Nothing to export!")
                return {'FINISHED'}

    class ExportScene(bpy.types.Operator):
        """Export active scene operator."""
        bl_label = "Export Scene"
        bl_idname = "scene.export_scene"
        bl_description = "Export active scene only"

        def execute(self, context):
            lprint('D Export Scene...')
            _get_scs_globals().content_type = 'scene'
            init_obj_list = tuple(bpy.context.scene.objects)  # Get all objects from current Scene

            try:
                result = _export.batch_export(self, init_obj_list)
            except Exception as e:

                result = {"CANCELLED"}
                context.window.cursor_modal_restore()

                import traceback

                traceback.print_exc()
                lprint("E Unexpected %r accured during batch export, see stack trace above.",
                       (type(e).__name__,),
                       report_errors=1,
                       report_warnings=1)

            return result

    class ExportAll(bpy.types.Operator):
        """Export all scenes operator."""
        bl_label = "Export All"
        bl_idname = "scene.export_all"
        bl_description = "Export all scenes"

        def execute(self, context):
            lprint('D Export All...')
            _get_scs_globals().content_type = 'scenes'
            init_obj_list = tuple(bpy.data.objects)  # Get all objects from all Scenes

            try:
                result = _export.batch_export(self, init_obj_list)
            except Exception as e:

                result = {"CANCELLED"}
                context.window.cursor_modal_restore()

                import traceback

                traceback.print_exc()
                lprint("E Unexpected %r accured during batch export, see stack trace above.",
                       (type(e).__name__,),
                       report_errors=1,
                       report_warnings=1)

            return result

    class ExportAnimAction(bpy.types.Operator):
        bl_label = "Export SCS Animation (PIA)"
        bl_idname = "scene.export_scs_anim_action"
        bl_description = "Export actual Action as SCS Animation file (PIA)"
        from bpy.props import StringProperty

        filename = StringProperty(
            name="Export PIA Filename",
            # maxlen=1024,
            subtype='FILE_NAME',
        )
        directory = StringProperty(
            name="Export PIA Directory",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filename_ext = ".pia"
        filter_glob = StringProperty(default=str("*" + filename_ext), options={'HIDDEN'})

        @classmethod
        def poll(cls, context):
            return _anim_utils.get_armature_action(context) is not None

        def execute(self, context):
            lprint('D Export Animation Action...')
            import os

            filepath = bpy.path.ensure_ext(os.path.join(self.directory, self.filename), self.filename_ext)
            # print('  o filepath:\n%r' % filepath)
            # print('  o filename:\n%r' % self.filename)
            # print('  o directory:\n%r' % self.directory)

            action = _anim_utils.get_armature_action(context)
            if action:
                # print('Exporting action %r...' % action.name)
                armature = context.active_object
                # bone_list = ['a', 'b']  # TODO...
                bone_list = armature.data.bones
                # print('  bone_list: %s' % str(bone_list))
                file_name = _name_utils.get_lod_name(context)  # FIXME: Probably not reliable!
                # print('  file_name: %s' % str(file_name))

                # EXPORT PIA
                _export.pia.export(armature, bone_list, filepath, file_name)

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.filename = str(_anim_utils.get_armature_action(context).name + ".pia")
            # self.directory = str(os.sep + "home" + os.sep)
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

    class ShaderTextureFilePath(bpy.types.Operator):
        """Universal operator for setting relative or absolute paths to shader texture files."""
        bl_label = "Select Shader Texture File"
        bl_idname = "scene.select_shader_texture_filepath"
        bl_description = "Open a Texture file browser"

        shader_texture = bpy.props.StringProperty(options={'HIDDEN'})
        rel_path = BoolProperty(
            name='Relative Path',
            description='Select the file relative to SCS Project directory',
            default=True,
        )
        filepath = StringProperty(
            name="Shader Texture File",
            description="Shader texture relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(
            default="*.tga;*.png;*.dds",
            options={'HIDDEN'},
        )

        def execute(self, context):
            """Set shader texture file path."""
            scs_globals = _get_scs_globals()
            material = context.active_object.active_material
            if self.rel_path:
                base_path = scs_globals.scs_project_path
                setattr(material.scs_props, self.shader_texture, _path_utils.relative_path(base_path, self.filepath))
            else:
                setattr(material.scs_props, self.shader_texture, str(self.filepath))
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            filepath = getattr(bpy.context.active_object.active_material.scs_props, self.shader_texture)
            if filepath.startswith(str(os.sep + os.sep)):
                self.filepath = _path_utils.get_abs_path(filepath)
            else:
                self.filepath = filepath
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class ShaderPresetsFilePath(bpy.types.Operator):
        """Operator for setting relative or absolute path to Shader Presets Library file."""
        bl_label = "Select Shader Presets Library File"
        bl_idname = "scene.select_shader_presets_filepath"
        bl_description = "Open a file browser"

        rel_path = BoolProperty(
            name='Relative Path',
            description='Select the file relative to SCS Project directory',
            default=True,
        )
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
            if self.rel_path:
                scs_globals.shader_presets_filepath = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)
            else:
                scs_globals.shader_presets_filepath = str(self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            filepath = _get_scs_globals().shader_presets_filepath
            if filepath.startswith(str(os.sep + os.sep)):
                self.filepath = _path_utils.get_abs_path(filepath)
            else:
                self.filepath = filepath
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    '''
    class CgFXTemplatesFilePath(bpy.types.Operator):
        """Operator for setting relative or absolute path to CgFX Template Library file."""
        bl_label = "Select CgFX Template Library File"
        bl_idname = "scene.select_cgfx_templates_filepath"
        bl_description = "Open a file browser"

        rel_path = BoolProperty(
            name='Relative Path',
            description='Select the file relative to SCS Project directory',
            default=True,
        )
        filepath = StringProperty(
            name="CgFX Template Library File",
            description="CgFX Template library relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )
        filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})

        def execute(self, context):
            """Set CgFX Template library file path."""
            scs_globals = _get_scs_globals()
            if self.rel_path:
                scs_globals.cgfx_templates_filepath = _utils.relative_path(scs_globals.scs_project_path, self.filepath)
            else:
                scs_globals.cgfx_templates_filepath = str(self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            filepath = _get_scs_globals().cgfx_templates_filepath
            if filepath.startswith(str(os.sep + os.sep)):
                self.filepath = _utils.get_abs_path(filepath)
            else:
                self.filepath = filepath
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


    class CgFXLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to CgFX Shader files."""
        bl_label = "Select CgFX Library Directory"
        bl_idname = "scene.select_cgfx_library_rel_path"
        bl_description = "Open a directory browser"

        directory = StringProperty(
            name="CgFX Library Directory Path",
            description="CgFX library directory path",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob = StringProperty(default="*.cgfx", options={'HIDDEN'})

        def execute(self, context):
            """Set CgFX directory path."""
            scs_globals = _get_scs_globals()
            scs_globals.cgfx_library_rel_path = _utils.relative_path(scs_globals.scs_project_path, self.directory)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            self.directory = _utils.get_abs_path(_get_scs_globals().cgfx_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
    '''

    class SignLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Sign Library file."""
        bl_label = "Select Sign Library File"
        bl_idname = "scene.select_sign_library_rel_path"
        bl_description = "Open a file browser"

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
            scs_globals.sign_library_rel_path = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.filepath = _path_utils.get_abs_path(_get_scs_globals().sign_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class TSemLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Semaphore Profile Library file."""
        bl_label = "Select Traffic Semaphore Profile Library File"
        bl_idname = "scene.select_tsem_library_rel_path"
        bl_description = "Open a file browser"

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
            scs_globals.tsem_library_rel_path = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.filepath = _path_utils.get_abs_path(_get_scs_globals().tsem_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class TrafficRulesLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Traffic Rules Library file."""
        bl_label = "Select Traffic Rules Library File"
        bl_idname = "scene.select_traffic_rules_library_rel_path"
        bl_description = "Open a file browser"

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
            scs_globals.traffic_rules_library_rel_path = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.filepath = _path_utils.get_abs_path(_get_scs_globals().traffic_rules_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class HookupLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Hookup files."""
        bl_label = "Select Hookup Library Directory"
        bl_idname = "scene.select_hookup_library_rel_path"
        bl_description = "Open a directory browser"

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
            scs_globals.hookup_library_rel_path = _path_utils.relative_path(scs_globals.scs_project_path, self.directory)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            self.directory = _path_utils.get_abs_path(_get_scs_globals().hookup_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class MatSubsLibraryRelativePath(bpy.types.Operator):
        """Operator for setting relative path to Material Substance shader files."""
        bl_label = "Select Material Substance Library File"
        bl_idname = "scene.select_matsubs_library_rel_path"
        bl_description = "Open a file browser"

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
            scs_globals.matsubs_library_rel_path = _path_utils.relative_path(scs_globals.scs_project_path, self.filepath)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""
            self.filepath = _path_utils.get_abs_path(_get_scs_globals().matsubs_library_rel_path)
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class GlobalExportFilePathSelector(bpy.types.Operator):
        """Operator for setting relative or absolute path to Global Export file."""
        bl_label = "Select Global Export Directory"
        bl_idname = "scene.select_global_export_filepath"
        bl_description = "Open a directory browser"

        rel_path = BoolProperty(
            name="Relative Path",
            description="Select the file relative to current Blender file",
            default=True,
        )
        directory = StringProperty(
            name="Global Export Path",
            description="Global export path (relative or absolute)",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob = StringProperty(default="*.pim", options={'HIDDEN'})

        def execute(self, context):
            """Set global export path."""
            scs_globals = _get_scs_globals()
            if self.rel_path:
                rel_filepath = bpy.path.relpath(self.directory, start=None).strip('.')
                # print(' SET REL path:\n\t"%s"' % rel_filepath)
                # print(' SET BLD path:\n\t"%s"' % bpy.data.filepath)
                if not bpy.data.filepath:
                    # scs_globals.global_export_filepath = str(self.directory)
                    scs_globals.global_export_filepath = _path_utils.repair_path(self.directory)
                else:
                    scs_globals.global_export_filepath = rel_filepath
            else:
                # print(' SET ABS path:\n\t"%s"' % self.directory)
                # scs_globals.global_export_filepath = str(self.directory)
                scs_globals.global_export_filepath = _path_utils.repair_path(self.directory)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            global_export_filepath = _get_scs_globals().global_export_filepath
            # print('  * global_export_filepath: %s' % str(global_export_filepath))
            directory = _path_utils.get_blenderfilewise_abs_filepath(global_export_filepath)
            # print('  * directory: %s' % str(directory))
            if directory:
                self.directory = directory
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class SCSGameObjectCustomExportFilePathSelector(bpy.types.Operator):
        """Operator for setting relative or absolute export path for 'SCS Game Object'."""
        bl_label = "Select 'SCS Game Object' Export Directory"
        bl_idname = "scene.select_game_object_custom_export_filepath"
        bl_description = "Open a directory browser"

        rel_path = BoolProperty(
            name="Relative Path",
            description="Select the file relative to current Blender file",
            default=True,
        )
        directory = StringProperty(
            name="'SCS Game Object' Custom Export Path",
            description="'SCS Game Object' custom export path (relative or absolute)",
            # maxlen=1024,
            subtype='DIR_PATH',
        )
        filter_glob = StringProperty(default="*.pim", options={'HIDDEN'})

        def execute(self, context):
            """Set 'SCS Game Object' custom export path."""
            if self.rel_path:

                if not bpy.data.filepath:
                    context.active_object.scs_props.scs_root_object_export_filepath = _path_utils.repair_path(self.directory)
                else:
                    # if the blender file and selected dir has the same starting point, create relative path
                    if bpy.data.filepath[0] == self.directory[0]:
                        rel_filepath = bpy.path.relpath(self.directory, start=None).strip('.')
                    else:
                        rel_filepath = _path_utils.repair_path(self.directory)

                    context.active_object.scs_props.scs_root_object_export_filepath = rel_filepath
            else:
                # print(' SET ABS path:\n\t"%s"' % self.directory)
                # context.active_object.scs_props.scs_root_object_export_filepath = str(self.directory)
                context.active_object.scs_props.scs_root_object_export_filepath = _path_utils.repair_path(self.directory)
            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a path selector."""
            scs_root_object_export_filepath = context.active_object.scs_props.scs_root_object_export_filepath
            # print('  * scs_root_object_export_filepath: %s' % str(scs_root_object_export_filepath))
            directory = _path_utils.get_blenderfilewise_abs_filepath(scs_root_object_export_filepath, data_type="'SCS Game Object' custom export")
            # print('  * directory: %s' % str(directory))
            if directory:
                self.directory = directory
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


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

                # INCREASE FPS
                scene.render.fps *= 2

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

                # INCREASE FPS
                scene.render.fps /= 2

            return {'FINISHED'}


class CgFX:
    """
    Wrapper class for better navigation in file
    """
    '''
    class PrintCgFXInventory(bpy.types.Operator):
        bl_label = "Print CgFX Inventory"
        bl_idname = "scene.print_cgfx_inventory"

        def execute(self, context):
            for cgfx_i, cgfx in enumerate(bpy.context.scene.scs_cgfx_inventory):
                print('%s %s - "%s"' % (str(cgfx_i).rjust(2, '0'), str(cgfx.active), cgfx.name))
            return {'FINISHED'}
    '''