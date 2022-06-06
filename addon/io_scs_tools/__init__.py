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
# GNU General Public License for more details.<
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2021: SCS Software

bl_info = {
    "name": "SCS Tools",
    "description": "Setup models, Import-Export SCS data format",
    "author": "Simon Lusenc (50keda), Milos Zajic (4museman)",
    "version": (2, 3, "aa16aece"),
    "blender": (3, 0, 0),
    "location": "File > Import-Export",
    "doc_url": "http://modding.scssoft.com/wiki/Documentation/Tools/SCS_Blender_Tools",
    "tracker_url": "http://forum.scssoft.com/viewforum.php?f=163",
    "support": "COMMUNITY",
    "category": "Import-Export"}

import bpy
import os
import traceback
from time import time
from bpy.props import CollectionProperty, StringProperty, PointerProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.imp import pix as _pix_import
from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback
from io_scs_tools.internals.callbacks import persistent as _persistent_callback
from io_scs_tools.internals import icons as _icons
from io_scs_tools.operators.bases.export import SCSExportHelper as _SCSExportHelper
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.view3d import has_view3d_space as _has_view3d_space
from io_scs_tools.utils.printout import lprint


class SCS_TOOLS_OT_Import(bpy.types.Operator, ImportHelper):
    """
    Load various SCS file formats containing geometries and numerous settings.
    """
    bl_idname = "scs_tools.import_pim"
    bl_label = "SCS Import"
    bl_description = "Load various SCS file formats containing geometries and numerous settings."
    bl_options = {'UNDO'}

    filename_ext = "*.pim;*.pim.ef;"
    files: CollectionProperty(name="File Path",
                              description="File path used for importing the SCS files",
                              type=bpy.types.OperatorFileListElement)

    scs_project_path_mode: BoolProperty(
        default=False,
        description="Set currently selected directory as SCS Project Path"
    )

    directory: StringProperty()
    filter_glob: StringProperty(default=filename_ext, options={'HIDDEN'})

    def check(self, context):

        if self.scs_project_path_mode:
            _get_scs_globals().scs_project_path = os.path.dirname(self.filepath)
            self.scs_project_path_mode = False

        return True

    def execute(self, context):

        from io_scs_tools.internals.containers.config import AsyncPathsInit

        # if paths are still initializing report that to user and don't execute import
        if AsyncPathsInit.is_running():

            self.report({'INFO'}, "Can't import yet, paths initialization is still in progress! Try again in few moments.")

            # revoke to add new fileselect dialog otherwise this operator will finish
            return self.invoke(context, None)

        if not _has_view3d_space(context.screen):
            message = "Cannot import SCS Models, no 3D viewport found! Make sure you have at least one 3D view visible."
            self.report({'ERROR'}, message)
            lprint("E " + message)
            return {'FINISHED'}

        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.path)

        start_time = time()

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

        end_time = time()
        self.report({'INFO'}, "Import finished and took %.3f sec." % (end_time - start_time))
        return {'FINISHED'}

    def draw(self, context):
        """
        :param context:
        :return:
        """

        from io_scs_tools.ui.shared import get_on_off_icon
        from io_scs_tools.ui.shared import draw_common_settings
        from io_scs_tools.internals.containers.config import AsyncPathsInit

        scs_globals = _get_scs_globals()

        # importer_version = round(import_pix.version(), 2)
        layout = self.layout

        # SCS Project Path
        box1 = layout.box()
        layout_box_col = box1.column(align=True)
        layout_box_col.label(text="SCS Project Base Path:", icon='FILE_FOLDER')
        layout_box_col.separator()

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.alert = not os.path.isdir(scs_globals.scs_project_path)
        layout_box_row.prop(scs_globals, 'scs_project_path', text="")

        layout_box_row = layout_box_col.row(align=True)
        layout_box_row.prop(self, "scs_project_path_mode", toggle=True, text="Set Current Dir as Project Base", icon='PASTEDOWN')

        if AsyncPathsInit.is_running():  # report running path initialization operator
            layout_box_row = layout_box_col.row(align=True)
            layout_box_row.scale_y = 2
            layout_box_row.label(text="Paths initialization in progress...")
            layout_box_row.label(text="", icon='SORTTIME')

        # import settings
        box2 = layout.box()
        col = box2.column()

        col.label(text="Import Options:", icon='SETTINGS')
        col.separator()
        col.prop(scs_globals, "import_scale")
        col.prop(scs_globals, "import_preserve_path_for_export")
        col.prop(scs_globals, "import_pim_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pim_file))
        if scs_globals.import_pim_file:
            col.prop(scs_globals, "import_use_normals")
            col.prop(scs_globals, "import_use_welding")
            if scs_globals.import_use_welding:
                col.prop(scs_globals, "import_welding_precision")
        col.prop(scs_globals, "import_pit_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pit_file))
        if scs_globals.import_pit_file:
            col.prop(scs_globals, "import_load_textures")
        col.prop(scs_globals, "import_pic_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pic_file))
        col.prop(scs_globals, "import_pip_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pip_file))
        col.prop(scs_globals, "import_pis_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pis_file))
        if scs_globals.import_pis_file:
            col.prop(scs_globals, "import_bone_scale")
            col.prop(scs_globals, "import_pia_file", toggle=True, icon=get_on_off_icon(scs_globals.import_pia_file))
            if scs_globals.import_pia_file:
                col.prop(scs_globals, "import_include_subdirs_for_pia")

        # Common global settings
        box3 = layout.box()
        box3.label(text="Log Level:", icon='MOD_EXPLODE')
        box3.prop(scs_globals, 'dump_level', text="")


class SCS_TOOLS_OT_Export(bpy.types.Operator, _SCSExportHelper, ExportHelper):
    """
    Export complex geometries to the SCS file formats.
    """
    bl_idname = "scs_tools.export_pim"
    bl_label = "SCS Export"
    bl_description = "Export complex geometries to the SCS file formats."
    bl_options = set()

    filename_ext = ".pim"
    filter_glob: StringProperty(default=str("*" + filename_ext), options={'HIDDEN'})

    def execute(self, context):
        # convert filepath to None if empty, so export will ignore given menu file path and try to export to other none menu set paths
        if self.filepath == "":
            filepath = None
        else:
            filepath = os.path.dirname(self.filepath)

        return self.execute_export(context, True, menu_filepath=filepath)

    def draw(self, context):
        from io_scs_tools.ui.shared import draw_export_panel

        box0 = self.layout.box()
        box0.use_property_split = True
        box0.use_property_decorate = False

        box0.label(text="Export Options:", icon='SETTINGS')
        box0.prop(_get_scs_globals(), 'export_scope', expand=True)

        draw_export_panel(box0, ignore_extra_boxes=True)


class SCS_TOOLS_MT_AddObject(bpy.types.Menu):
    bl_label = "Add"
    bl_description = "Creates menu for adding SCS objects"

    def draw(self, context):
        self.layout.operator_enum("object.scs_tools_add_object", "new_object_type")


class SCS_TOOLS_MT_ObjectsMisc(bpy.types.Menu):
    bl_label = "Objects Misc"
    bl_description = "Creates menu for SCS objects miscellaneous actions"

    def draw(self, context):
        self.layout.operator("object.scs_tools_fix_model_locator_hookups")


class SCS_TOOLS_MT_MaterialsMisc(bpy.types.Menu):
    bl_label = "Materials Misc"
    bl_description = "Creates menu for SCS materials miscellaneous actions"

    def draw(self, context):
        self.layout.operator("material.scs_tools_reload_materials")
        self.layout.operator("material.scs_tools_merge_materials")
        self.layout.operator("material.scs_tools_adapt_color_management")


class SCS_TOOLS_MT_MainMenu(bpy.types.Menu):
    bl_label = "SCS Tools"
    bl_description = "Global menu for accessing all SCS Blender Tools features in one place"

    __static_popovers = {
        "sidebar": [],
        "props": [],
        "output": []
    }

    @staticmethod
    def append_sidebar_entry(menu_item_name, panel_id):
        SCS_TOOLS_MT_MainMenu.__static_popovers["sidebar"].append((menu_item_name, panel_id))

    @staticmethod
    def append_props_entry(menu_item_name, panel_id):
        SCS_TOOLS_MT_MainMenu.__static_popovers["props"].append((menu_item_name, panel_id))

    @staticmethod
    def append_output_entry(menu_item_name, panel_id):
        SCS_TOOLS_MT_MainMenu.__static_popovers["output"].append((menu_item_name, panel_id))

    @classmethod
    def unregister(cls):
        for category in SCS_TOOLS_MT_MainMenu.__static_popovers:
            SCS_TOOLS_MT_MainMenu.__static_popovers[category].clear()

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # sub-menus
        column.menu(SCS_TOOLS_MT_AddObject.__name__)
        column.menu(SCS_TOOLS_MT_ObjectsMisc.__name__)
        column.menu(SCS_TOOLS_MT_MaterialsMisc.__name__)

        # popovers by category
        for category in SCS_TOOLS_MT_MainMenu.__static_popovers:
            column.separator()
            for menu_item_name, panel_id in SCS_TOOLS_MT_MainMenu.__static_popovers[category]:
                column.popover(panel_id, text=menu_item_name)


def add_menu_func(self, context):
    self.layout.menu(SCS_TOOLS_MT_AddObject.__name__, text="SCS Object", icon_value=_icons.get_icon(_ICONS_consts.Types.scs_object_menu))
    self.layout.separator()


def menu_func_import(self, context):
    self.layout.operator(SCS_TOOLS_OT_Import.bl_idname, text="SCS Game Object (.pim)",
                         icon_value=_icons.get_icon(_ICONS_consts.Types.scs_object_menu))


def menu_func_export(self, context):
    self.layout.operator(SCS_TOOLS_OT_Export.bl_idname, text="SCS Game Object(s) (.pim)",
                         icon_value=_icons.get_icon(_ICONS_consts.Types.scs_object_menu))


def menu_scs_tools(self, context):
    self.layout.menu(SCS_TOOLS_MT_MainMenu.__name__)


classes = (
    SCS_TOOLS_OT_Import,
    SCS_TOOLS_OT_Export,
    SCS_TOOLS_MT_AddObject,
    SCS_TOOLS_MT_ObjectsMisc,
    SCS_TOOLS_MT_MaterialsMisc,
    SCS_TOOLS_MT_MainMenu

)


# #################################################

def register():
    # CUSTOM ICONS INITIALIZATION
    _icons.register()

    # REGISTRATION OF OUR PROPERTIES
    from io_scs_tools.properties import register as props_register
    props_register()

    # PROPERTIES REGISTRATION INTO EXISTING CLASSES
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

    bpy.types.WorkSpace.scs_props = PointerProperty(
        name="SCS Tools Workspace Variables",
        type=properties.workspace.WorkspaceSCSProps,
        description="SCS Tools workspace variables"
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

    # REGISTER UI
    from io_scs_tools.ui import register as ui_register
    ui_register()

    # REGISTER OPERATORS
    from io_scs_tools.operators import register as ops_register
    ops_register()

    # MAIN MODULE REGISTRATION
    for cls in classes:
        bpy.utils.register_class(cls)

    # MENU REGISTRATION
    bpy.types.TOPBAR_MT_editor_menus.append(menu_scs_tools)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.VIEW3D_MT_add.prepend(add_menu_func)

    # PERSISTENT HANDLERS
    _persistent_callback.enable()


def unregister():
    # DELETE CUSTOM ICONS
    _icons.unregister()

    # REMOVE OPENGL HANDLERS
    _open_gl_callback.disable()

    # REMOVE PERSISTENT HANDLERS
    _persistent_callback.disable()

    # REMOVE MENU ENTRIES
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_scs_tools)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)
    bpy.types.VIEW3D_MT_add.remove(add_menu_func)

    # REMOVE MAIN MODULE CLASSES
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # UNREGISTER OPERATORS
    from io_scs_tools.operators import unregister as ops_unregister
    ops_unregister()

    # UNREGISTER UI
    from io_scs_tools.ui import unregister as ui_unregister
    ui_unregister()

    # REMOVE PROPERTIES FROM DATA
    del bpy.types.Action.scs_props
    del bpy.types.Material.scs_props
    del bpy.types.Mesh.scs_props
    del bpy.types.Scene.scs_props
    del bpy.types.Object.scs_props
    del bpy.types.WorkSpace.scs_props

    del bpy.types.Object.scs_object_look_inventory
    del bpy.types.Object.scs_object_part_inventory
    del bpy.types.Object.scs_object_variant_inventory
    del bpy.types.Object.scs_object_animation_inventory

    # UNREGISTER PROPS
    from io_scs_tools.properties import unregister as props_unregister
    props_unregister()


if __name__ == "__main__":
    register()
    print("Running from if in main module!")
