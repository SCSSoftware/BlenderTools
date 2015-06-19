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

bl_info = {
    "name": "SCS Tools",
    "description": "Setup models, Import-Export SCS data format",
    "author": "Milos Zajic (4museman), Simon Lusenc (50keda)",
    "version": (0, 6, "792edf5"),
    "blender": (2, 73, 0),
    "location": "File > Import-Export",
    "warning": "WIP - beta version, doesn't include all features!",
    "wiki_url": "https://github.com/SCSSoftware/BlenderTools/wiki",
    "tracker_url": "http://forum.scssoft.com/viewforum.php?f=165",
    "support": "COMMUNITY",
    "category": "Import-Export"}


def get_tools_version():
    """Returns Blender Tools version as string from bl_info["version"] dictonary value.
    :return: string representation of bl_info["version"] tuple
    :rtype: str
    """
    ver = ""
    for ver_num in bl_info["version"]:
        ver += str(ver_num) + "."
    return ver[:-1]


import bpy
import os
import traceback
from bpy.props import CollectionProperty, StringProperty, PointerProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from io_scs_tools.imp import pix as _pix_import
from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback
from io_scs_tools.internals.callbacks import persistent as _persistent_callback
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.view3d import switch_layers_visibility as _switch_layers_visibility
from io_scs_tools.utils.printout import lprint


# importing all SCS Tools modules which creates panels in UI
from io_scs_tools import ui
from io_scs_tools import operators


class ImportSCS(bpy.types.Operator, ImportHelper):
    """
    Load various SCS file formats containing geometries and numerous settings.
    """
    bl_idname = "import_mesh.pim"
    bl_label = "SCS Import"
    bl_description = "Load various SCS file formats containing geometries and numerous settings."
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                               description="File path used for importing the SCS files",
                               type=bpy.types.OperatorFileListElement)

    scs_project_path_mode = BoolProperty(
        default=False,
        description="Set currently selected directory as SCS Project Path"
    )

    directory = StringProperty()
    filename_ext = "*.pim"
    filter_glob = StringProperty(default=filename_ext, options={'HIDDEN'})

    def check(self, context):

        if self.scs_project_path_mode:
            _get_scs_globals().scs_project_path = os.path.dirname(self.filepath)
            self.scs_project_path_mode = False

        return True

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.path)

        failed_files = []
        for self.filepath in paths:

            result = False
            if self.filepath.endswith("pim"):

                try:

                    _get_scs_globals().import_in_progress = True
                    result = _pix_import.load(context, self.filepath)
                    _get_scs_globals().import_in_progress = False

                except Exception as e:

                    _get_scs_globals().import_in_progress = False
                    context.window.cursor_modal_restore()

                    traceback.print_exc()
                    lprint("E Unexpected %r accured during import, see stack trace above.", (type(e).__name__,))

            if result is False:
                failed_files.append(str(self.filepath).replace("\\", "/"))

        if len(failed_files) > 0:
            err_message = "E Following files failed to load:\n"

            for _ in failed_files:
                err_message += "-> %r\n"

            lprint(err_message, tuple(failed_files), report_warnings=1, report_errors=1)

        return {'FINISHED'}

    def draw(self, context):
        """
        :param context:
        :return:
        """

        scs_globals = _get_scs_globals()

        # importer_version = round(import_pix.version(), 2)
        layout = self.layout
        box1 = layout.box()

        row = box1.row()
        row.prop(scs_globals, "import_scale")

        box2 = layout.box()

        row = box2.row()
        row.prop(scs_globals, "import_pim_file", toggle=True)
        if scs_globals.import_pim_file:
            row = box2.row()
            row.prop(scs_globals, "use_welding")
            if scs_globals.use_welding:
                row = box2.row()
                row.prop(scs_globals, "welding_precision")
        row = box2.row()
        row.prop(scs_globals, "import_pit_file", toggle=True)
        if scs_globals.import_pit_file:
            row = box2.row()
            row.prop(scs_globals, "load_textures")
        row = box2.row()
        row.prop(scs_globals, "import_pic_file", toggle=True)
        row = box2.row()
        row.prop(scs_globals, "import_pip_file", toggle=True)
        row = box2.row()
        row.prop(scs_globals, "import_pis_file", toggle=True)
        if scs_globals.import_pis_file:
            # row = box2.row()
            # row.prop(_get_scs_globals(), "connected_bones")
            row = box2.row()
            row.prop(scs_globals, "bone_import_scale")
            row = box2.row()
            row.prop(scs_globals, "import_pia_file", toggle=True)
            if scs_globals.import_pia_file:
                row = box2.row()
                row.prop(scs_globals, "include_subdirs_for_pia")

        # SCS Project Path
        box3 = layout.box()
        layout_box_col = box3.column(align=True)
        layout_box_col.label('SCS Project Base Path:', icon='FILE_FOLDER')

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not os.path.isdir(scs_globals.scs_project_path)
        layout_box_row.prop(scs_globals, 'scs_project_path', text='')

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.prop(self, "scs_project_path_mode", toggle=True, text="Set Current Dir as Project Base", icon='SAVE_COPY')

        # Debug options
        ui.shared.draw_debug_settings(layout)


class ExportSCS(bpy.types.Operator, ExportHelper):
    """
    Export complex geometries to the SCS file formats.
    """
    bl_idname = "export_mesh.pim"
    bl_label = "SCS Export"
    bl_description = "Export complex geometries to the SCS file formats."

    filename_ext = ".pim"
    filter_glob = StringProperty(default=str("*" + filename_ext), options={'HIDDEN'})

    layers_visibilities = []
    """List for storing layers visibility in the init of operator"""

    def __init__(self):
        """Constructor used for showing all scene visibility layers.
        This provides possibility to updates world matrixes even on hidden objects.
        """
        self.layers_visibilities = _switch_layers_visibility([], True)

    def __del__(self):
        """Destructor with reverting visible layers.
        """
        _switch_layers_visibility(self.layers_visibilities, False)

    def execute(self, context):
        lprint('D Export From Menu...')

        from io_scs_tools import exp as _export
        from io_scs_tools.utils import object as _object_utils

        filepath = os.path.dirname(self.filepath)

        export_type = _get_scs_globals().content_type
        init_obj_list = {}
        if export_type == "selection":
            for obj in bpy.context.selected_objects:
                root = _object_utils.get_scs_root(obj)
                if root:
                    if root != obj:  # add only selected children
                        init_obj_list[obj.name] = obj
                        init_obj_list[root.name] = root
                    else:  # add every children if all are unselected
                        children = _object_utils.get_children(obj)
                        local_reselected_objs = []
                        for child_obj in children:
                            local_reselected_objs.append(child_obj)
                            # if some child is selected this means we won't reselect nothing in this game object
                            if child_obj.select:
                                local_reselected_objs = []
                                break

                        for reselected_obj in local_reselected_objs:
                            init_obj_list[reselected_obj.name] = reselected_obj

            init_obj_list = tuple(init_obj_list.values())
        elif export_type == "scene":
            init_obj_list = tuple(bpy.context.scene.objects)
        elif export_type == 'scenes':
            init_obj_list = tuple(bpy.data.objects)

        try:
            result = _export.batch_export(self, init_obj_list, export_type != "selection", filepath)
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

    def draw(self, context):
        box0 = self.layout.box()
        row = box0.row()
        row.prop(_get_scs_globals(), 'content_type', expand=True)
        ui.shared.draw_export_panel(self.layout)


def menu_func_import(self, context):
    self.layout.operator(ImportSCS.bl_idname, text="SCS Formats (.pim)")


def menu_func_export(self, context):
    self.layout.operator(ExportSCS.bl_idname, text="SCS Formats (.pim)")


# #################################################

def register():
    from . import properties

    bpy.utils.register_module(__name__)

    # PROPERTIES REGISTRATION
    bpy.types.Object.scs_object_look_inventory = CollectionProperty(
        type=properties.object.ObjectLooksInventory
    )

    bpy.types.Object.scs_object_part_inventory = CollectionProperty(
        type=properties.object.ObjectPartInventory
    )

    bpy.types.Object.scs_object_variant_inventory = CollectionProperty(
        type=properties.object.ObjectVariantInventory
    )

    bpy.types.Object.scs_object_animation_inventory = CollectionProperty(
        type=properties.object.ObjectAnimationInventory
    )

    bpy.types.World.scs_shader_presets_inventory = CollectionProperty(
        type=properties.world.SceneShaderPresetsInventory
    )

    # bpy.types.Scene.scs_cgfx_template_inventory = CollectionProperty(
    # type=scene_props.SceneCgFXTemplateInventory
    # )
    #
    # bpy.types.Scene.scs_cgfx_inventory = CollectionProperty(
    # type=scene_props.SceneCgFXShaderInventory
    # )
    #
    # bpy.types.Material.scs_cgfx_looks = CollectionProperty(
    # type=material_props.MaterialCgFXShaderLooks
    # )

    bpy.types.World.scs_globals = PointerProperty(
        name="SCS Tools Global Variables",
        type=properties.world.GlobalSCSProps,
        description="SCS Tools global variables",
    )

    bpy.types.Object.scs_props = PointerProperty(
        name="SCS Tools Object Variables",
        type=properties.object.ObjectSCSTools,
        description="SCS Tools object variables",
    )

    bpy.types.Scene.scs_props = PointerProperty(
        name="SCS Tools Scene Variables",
        type=properties.scene.SceneSCSProps,
        description="SCS Tools scene variables",
    )

    bpy.types.Mesh.scs_props = PointerProperty(
        name="SCS Tools Mesh Variables",
        type=properties.mesh.MeshSCSTools,
        description="SCS Tools Mesh variables",
    )

    bpy.types.Material.scs_props = PointerProperty(
        name="SCS Tools Material Variables",
        type=properties.material.MaterialSCSTools,
        description="SCS Tools Material variables",
    )

    bpy.types.Action.scs_props = PointerProperty(
        name="SCS Tools Action Variables",
        type=properties.action.ActionSCSTools,
        description="SCS Tools Action variables",
    )

    # REGISTER DYNAMIC PROPERTIES
    properties.object_dynamic.register()
    properties.scene_dynamic.register()

    # PERSISTENT HANDLERS
    _persistent_callback.enable()

    # MENU REGISTRATION
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    # REMOVE MENU ENTRIES
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

    # REMOVE OPENGL HANDLERS
    _open_gl_callback.disable()

    # REMOVE PERSISTENT HANDLERS
    _persistent_callback.disable()

    # REMOVE PROPERTIES FROM DATA
    del bpy.types.Action.scs_props
    del bpy.types.Material.scs_props
    del bpy.types.Mesh.scs_props
    del bpy.types.Scene.scs_props
    del bpy.types.Object.scs_props
    del bpy.types.World.scs_globals

    del bpy.types.Object.scs_object_look_inventory
    del bpy.types.Object.scs_object_part_inventory
    del bpy.types.Object.scs_object_variant_inventory
    del bpy.types.Object.scs_object_animation_inventory
    del bpy.types.World.scs_shader_presets_inventory


if __name__ == "__main__":
    register()
    print("Running from if in main module!")
