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
    "author": "Simon Lusenc (50keda), Milos Zajic (4museman)",
    "version": (1, 10, "793b390"),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "wiki_url": "http://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools",
    "tracker_url": "http://forum.scssoft.com/viewforum.php?f=163",
    "support": "COMMUNITY",
    "category": "Import-Export"}

import bpy
import os
import traceback
from bpy.props import CollectionProperty, StringProperty, PointerProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.imp import pix as _pix_import
from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback
from io_scs_tools.internals.callbacks import persistent as _persistent_callback
from io_scs_tools.internals import icons as _icons
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.view3d import switch_layers_visibility as _switch_layers_visibility
from io_scs_tools.utils.view3d import has_view3d_space as _has_view3d_space
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
    filename_ext = "*.pim;*.pim.ef;"
    filter_glob = StringProperty(default=filename_ext, options={'HIDDEN'})

    def check(self, context):

        if self.scs_project_path_mode:
            _get_scs_globals().scs_project_path = os.path.dirname(self.filepath)
            self.scs_project_path_mode = False

        return True

    def execute(self, context):

        # if paths are still initializing report that to user and don't execute import
        if operators.world.SCSPathsInitialization.is_running():

            self.report({'INFO'}, "Can't import yet, paths initialization is still in progress! Try again in few moments.")

            # there is no way to keep current operator alive if we want to abort import sequence.
            # That's why we call another import operator, which will end up with
            # printing out above info and taking us back to import screen with file browser.
            bpy.ops.import_mesh.pim('INVOKE_DEFAULT')

            return {'FINISHED'}

        if not _has_view3d_space(context.screen):
            message = "Cannot import SCS Models, no 3D viewport found! Make sure you have at least one 3D view visible."
            self.report({'ERROR'}, message)
            lprint("E " + message)
            return {'FINISHED'}

        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.path)

        failed_files = []
        for filepath in paths:

            result = False
            if filepath.endswith(".pim") or filepath.endswith(".pim.ef"):

                # check extension for DEF format and properly assign it to name suffix
                ef_format_suffix = ""
                if filepath.endswith(".ef"):
                    ef_format_suffix = ".ef"
                    filepath = filepath[:-len(ef_format_suffix)]

                filepath = filepath[:-4]

                try:

                    _get_scs_globals().import_in_progress = True
                    result = _pix_import.load(context, filepath, name_suffix=ef_format_suffix)
                    _get_scs_globals().import_in_progress = False

                except Exception as e:

                    _get_scs_globals().import_in_progress = False
                    context.window.cursor_modal_restore()

                    trace_str = traceback.format_exc().replace("\n", "\n\t   ")
                    lprint("E Unexpected %r accured during import:\n\t   %s", (type(e).__name__, trace_str))

            if result is False:
                failed_files.append(str(filepath).replace("\\", "/"))

        if len(failed_files) > 0:
            err_message = "E Following files failed to load:"

            for _ in failed_files:
                err_message += "\n\t   -> %r\n"

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

        # SCS Project Path
        box1 = layout.box()
        layout_box_col = box1.column(align=True)
        layout_box_col.label('SCS Project Base Path:', icon='FILE_FOLDER')

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not os.path.isdir(scs_globals.scs_project_path)
        layout_box_row.prop(scs_globals, 'scs_project_path', text='')

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.prop(self, "scs_project_path_mode", toggle=True, text="Set Current Dir as Project Base", icon='SCREEN_BACK')

        if operators.world.SCSPathsInitialization.is_running():  # report running path initialization operator
            layout_box_row = layout_box_col.row(align=True)
            layout_box_row.label("Paths initialization in progress...")
            layout_box_row.label("", icon='TIME')

        # import settings
        box2 = layout.box()
        col = box2.column(align=True)

        col.row().prop(scs_globals, "import_scale")
        col.row().separator()
        col.row().prop(scs_globals, "import_preserve_path_for_export")
        col.row().separator()
        col.row().prop(scs_globals, "import_pim_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pim_file else "X")
        if scs_globals.import_pim_file:
            col.row().prop(scs_globals, "import_use_normals")
            col.row().prop(scs_globals, "import_use_welding")
            if scs_globals.import_use_welding:
                col.row().prop(scs_globals, "import_welding_precision")
        col.row().separator()
        col.row().prop(scs_globals, "import_pit_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pit_file else "X")
        if scs_globals.import_pit_file:
            col.row().prop(scs_globals, "import_load_textures")
        col.row().separator()
        col.row().prop(scs_globals, "import_pic_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pic_file else "X")
        col.row().separator()
        col.row().prop(scs_globals, "import_pip_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pip_file else "X")
        col.row().separator()
        col.row(align=True).prop(scs_globals, "import_pis_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pis_file else "X")
        if scs_globals.import_pis_file:
            col.row(align=True).prop(scs_globals, "import_bone_scale")
            col.row().separator()
            col.row().prop(scs_globals, "import_pia_file", toggle=True, icon="FILE_TICK" if scs_globals.import_pia_file else "X")
            if scs_globals.import_pia_file:
                col.row().prop(scs_globals, "import_include_subdirs_for_pia")

        # Common global settings
        ui.shared.draw_common_settings(layout, log_level_only=True)


class ExportSCS(bpy.types.Operator, ExportHelper):
    """
    Export complex geometries to the SCS file formats.
    """
    bl_idname = "export_mesh.pim"
    bl_label = "SCS Export"
    bl_description = "Export complex geometries to the SCS file formats."
    bl_options = set()

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

        # convert it to None, so export will ignore given menu file path and try to export to other none menu set paths
        if self.filepath == "":
            filepath = None

        export_scope = _get_scs_globals().export_scope
        init_obj_list = {}
        if export_scope == "selection":
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
        elif export_scope == "scene":
            init_obj_list = tuple(bpy.context.scene.objects)
        elif export_scope == 'scenes':
            init_obj_list = tuple(bpy.data.objects)

        # check extension for EF format and properly assign it to name suffix
        ef_name_suffix = ""
        if _get_scs_globals().export_output_type == "EF":
            ef_name_suffix = ".ef"

        try:
            result = _export.batch_export(self, init_obj_list, name_suffix=ef_name_suffix, menu_filepath=filepath)
        except Exception as e:

            result = {"CANCELLED"}
            context.window.cursor_modal_restore()

            trace_str = traceback.format_exc().replace("\n", "\n\t   ")
            lprint("E Unexpected %r accured during batch export:\n\t   %s",
                   (type(e).__name__, trace_str),
                   report_errors=1,
                   report_warnings=1)

        return result

    def draw(self, context):
        box0 = self.layout.box()
        row = box0.row()
        row.prop(_get_scs_globals(), 'export_scope', expand=True)
        ui.shared.draw_export_panel(self.layout)


class SCSAddObject(bpy.types.Menu):
    bl_idname = "INFO_MT_SCS_add_object"
    bl_label = "SCS Object"
    bl_description = "Creates menu for adding SCS objects."

    def draw(self, context):
        self.layout.operator_enum("object.scs_add_object", "new_object_type")


def add_menu_func(self, context):
    self.layout.menu("INFO_MT_SCS_add_object", text="SCS Object", icon_value=_icons.get_icon(_ICONS_consts.Types.scs_logo_orange))
    self.layout.separator()


def menu_func_import(self, context):
    self.layout.operator(ImportSCS.bl_idname, text="SCS Formats (.pim)")


def menu_func_export(self, context):
    self.layout.operator(ExportSCS.bl_idname, text="SCS Formats (.pim)")


# #################################################

def register():
    from . import properties

    bpy.utils.register_module(__name__)

    # CUSTOM ICONS INITIALIZATION
    _icons.init()

    # PROPERTIES REGISTRATION
    bpy.types.Object.scs_object_look_inventory = CollectionProperty(
        type=properties.object.ObjectLooksInventoryItem
    )

    bpy.types.Object.scs_object_part_inventory = CollectionProperty(
        type=properties.object.ObjectPartInventoryItem
    )

    bpy.types.Object.scs_object_variant_inventory = CollectionProperty(
        type=properties.object.ObjectVariantInventoryItem
    )

    bpy.types.Object.scs_object_animation_inventory = CollectionProperty(
        type=properties.object.ObjectAnimationInventoryItem
    )

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
    bpy.types.INFO_MT_add.prepend(add_menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # REMOVE MENU ENTRIES
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_add.remove(add_menu_func)

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


if __name__ == "__main__":
    register()
    print("Running from if in main module!")
