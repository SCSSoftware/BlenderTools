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
from bpy.props import (StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       EnumProperty,
                       FloatProperty,
                       FloatVectorProperty)
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

'''
# CgFX TEMPLATES (on Scenes)
# class SceneCgFXTemplateInventory(bpy.types.PropertyGroup):
# """
# CgFX Shader Templates inventory on Scene.
#     """
#     name = StringProperty(name="CgFX Template Name", default="")
#     active = BoolProperty(name="CgFX Template Activation Status", default=False)
#
#
# CgFX SHADERS (on Scenes)
# class SceneCgFXShaderInventory(bpy.types.PropertyGroup):
#     """
#     CgFX Shader file inventory on Scene.
#     """
#     name = StringProperty(name="CgFX Shader Name", default="")
#     filepath = StringProperty(name="CgFX Shader Absolute File Path", default="")
#     active = BoolProperty(name="CgFX Shader Activation Status", default=False)
'''


class SceneShaderPresetsInventory(bpy.types.PropertyGroup):
    """
    Shader Presets inventory on Scene.
    """
    name = StringProperty(name="Shader Presets Name", default="")


class GlobalSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Global Variables - ...World.scs_globals...
    :return:
    """

    edit_part_name_mode = BoolProperty(
        name="Edit SCS Part Name",
        description="Edit SCS Part name mode",
        default=False,
        # update=edit_part_name_mode_update,
    )

    # SIGN LOCATOR MODEL INVENTORY
    class SignModelInventory(bpy.types.PropertyGroup):
        """
        Sign Model Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model_desc = StringProperty(default="")
        look_name = StringProperty(default="")
        category = StringProperty(default="")
        dynamic = BoolProperty(default=False)

    bpy.utils.register_class(SignModelInventory)
    scs_sign_model_inventory = CollectionProperty(
        type=SignModelInventory,
        options={'SKIP_SAVE'},
    )

    # TRAFFIC SEMAPHORE LOCATOR PROFILE INVENTORY
    class TSemProfileInventory(bpy.types.PropertyGroup):
        """
        Traffic Semaphore Profile Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model = StringProperty(default="")

    bpy.utils.register_class(TSemProfileInventory)
    scs_tsem_profile_inventory = CollectionProperty(
        type=TSemProfileInventory,
        options={'SKIP_SAVE'},
    )

    # TRAFFIC RULES PROFILE INVENTORY
    class TrafficRulesInventory(bpy.types.PropertyGroup):
        """
        Traffic Rules Inventory.
        :return:
        """
        # item_id = StringProperty(default="")
        rule = StringProperty(default="")
        num_params = StringProperty(default="")

    bpy.utils.register_class(TrafficRulesInventory)
    scs_traffic_rules_inventory = CollectionProperty(
        type=TrafficRulesInventory,
        options={'SKIP_SAVE'},
    )

    # HOOKUP INVENTORY
    class HookupInventory(bpy.types.PropertyGroup):
        """
        Hookup Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model = StringProperty(default="")
        brand_idx = IntProperty(default=0)
        dir_type = StringProperty(default="")
        low_poly_only = BoolProperty(default=False)

    bpy.utils.register_class(HookupInventory)
    scs_hookup_inventory = CollectionProperty(
        type=HookupInventory,
        options={'SKIP_SAVE'},
    )

    # MATERIAL SUBSTANCE INVENTORY
    class MatSubsInventory(bpy.types.PropertyGroup):
        """
        Material Substance Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        item_description = StringProperty(default="")

    bpy.utils.register_class(MatSubsInventory)
    scs_matsubs_inventory = CollectionProperty(
        type=MatSubsInventory,
        options={'SKIP_SAVE'},
    )

    # SCS TOOLS GLOBAL PATHS
    def scs_project_path_update(self, context):
        # Update all related paths so their libraries gets reloaded from new "SCS Project Path" location.
        if not _get_scs_globals().config_update_lock:
            # utils.update_cgfx_library_rel_path(_get_scs_globals().cgfx_library_rel_path)
            _config_container.update_sign_library_rel_path(_get_scs_globals().scs_sign_model_inventory,
                                                           _get_scs_globals().sign_library_rel_path)

            _config_container.update_tsem_library_rel_path(_get_scs_globals().scs_tsem_profile_inventory,
                                                           _get_scs_globals().tsem_library_rel_path)

            _config_container.update_traffic_rules_library_rel_path(_get_scs_globals().scs_traffic_rules_inventory,
                                                                    _get_scs_globals().traffic_rules_library_rel_path)

            _config_container.update_hookup_library_rel_path(_get_scs_globals().scs_hookup_inventory,
                                                             _get_scs_globals().hookup_library_rel_path)

            _config_container.update_matsubs_inventory(_get_scs_globals().scs_matsubs_inventory,
                                                       _get_scs_globals().matsubs_library_rel_path)

        _config_container.update_item_in_file('Paths.ProjectPath', self.scs_project_path)

        # Update Blender image textures according to SCS texture records, so the images are loaded always from the correct locations.
        _material_utils.correct_blender_texture_paths()

        return None

    def shader_presets_filepath_update(self, context):
        # print('Shader Presets Library Path UPDATE: "%s"' % self.shader_presets_filepath)
        _config_container.update_shader_presets_path(context.scene.scs_shader_presets_inventory, self.shader_presets_filepath)
        return None

    '''
    # def cgfx_templates_filepath_update(self, context):
    #     # print('CgFX Template Library Path UPDATE: "%s"' % self.cgfx_templates_filepath)
    #     utils.update_cgfx_template_path(self.cgfx_templates_filepath)
    #     return None

    # def cgfx_library_rel_path_update(self, context):
    #     #print('CgFX Library Path UPDATE: "%s"' % self.cgfx_library_rel_path)
    #     utils.update_cgfx_library_rel_path(self.cgfx_library_rel_path)
    #     return None
    '''

    def sign_library_rel_path_update(self, context):
        # print('Sign Library Path UPDATE: "%s"' % self.sign_library_rel_path)
        _config_container.update_sign_library_rel_path(_get_scs_globals().scs_sign_model_inventory,
                                                       self.sign_library_rel_path)
        return None

    def tsem_library_rel_path_update(self, context):
        # print('Traffic Semaphore Profile Path UPDATE: "%s"' % self.tsem_library_rel_path)
        _config_container.update_tsem_library_rel_path(_get_scs_globals().scs_tsem_profile_inventory,
                                                       self.tsem_library_rel_path)
        return None

    def traffic_rules_library_rel_path_update(self, context):
        # print('Traffic Rules Path UPDATE: "%s"' % self.traffic_rules_library_rel_path)
        _config_container.update_traffic_rules_library_rel_path(_get_scs_globals().scs_traffic_rules_inventory,
                                                                self.traffic_rules_library_rel_path)
        return None

    def hookup_library_rel_path_update(self, context):
        # print('Hookup Library Path UPDATE: "%s"' % self.hookup_library_rel_path)
        _config_container.update_hookup_library_rel_path(_get_scs_globals().scs_hookup_inventory,
                                                         self.hookup_library_rel_path)
        return None

    def matsubs_library_rel_path_update(self, context):
        # print('Material Substance Library Path UPDATE: "%s"' % self.matsubs_library_rel_path)
        _config_container.update_matsubs_inventory(_get_scs_globals().scs_matsubs_inventory,
                                                   self.matsubs_library_rel_path)
        return None

    os_rs = str(os.sep + os.sep)  # OS WISE RELATIVE PATH SIGN
    scs_project_path = StringProperty(
        name="SCS Project Main Directory",
        description="SCS project main directory (absolute path)",
        default="",
        # subtype="DIR_PATH",
        subtype='NONE',
        update=scs_project_path_update
    )
    shader_presets_filepath = StringProperty(
        name="Shader Presets Library",
        description="Shader Presets library file path (absolute file path; *.txt)",
        default=_path_utils.get_shader_presets_filepath(),
        subtype='NONE',
        # subtype="FILE_PATH",
        update=shader_presets_filepath_update,
    )
    # cgfx_templates_filepath = StringProperty(
    # name="CgFX Template Library",
    # description="CgFX template library file path (absolute file path; *.txt)",
    # default=utils.get_cgfx_templates_filepath(),
    # subtype='NONE',
    # subtype="FILE_PATH",
    # # update=cgfx_templates_filepath_update,
    # )
    # cgfx_library_rel_path = StringProperty(
    # name="CgFX Library Dir",
    # description="CgFX shaders directory (relative path to 'SCS Project Main Directory')",
    # default=str(os_rs + 'effect' + os.sep + 'eut2' + os.sep + 'cgfx'),
    # subtype='NONE',
    # # update=cgfx_library_rel_path_update,
    # )
    sign_library_rel_path = StringProperty(
        name="Sign Library",
        description="Sign library (relative file path to 'SCS Project Main Directory'; *.sii)",
        default=str(os_rs + 'def' + os.sep + 'world' + os.sep + 'sign.sii'),
        subtype='NONE',
        update=sign_library_rel_path_update,
    )
    tsem_library_rel_path = StringProperty(
        name="Traffic Semaphore Profile Library",
        description="Traffic Semaphore Profile library (relative file path to 'SCS Project Main Directory'; *.sii)",
        default=str(os_rs + 'def' + os.sep + 'world' + os.sep + 'semaphore_profile.sii'),
        subtype='NONE',
        update=tsem_library_rel_path_update,
    )
    traffic_rules_library_rel_path = StringProperty(
        name="Traffic Rules Library",
        description="Traffic rules library (relative file path to 'SCS Project Main Directory'; *.sii)",
        default=str(os_rs + 'def' + os.sep + 'world' + os.sep + 'traffic_rules.sii'),
        subtype='NONE',
        update=traffic_rules_library_rel_path_update,
    )
    hookup_library_rel_path = StringProperty(
        name="Hookup Library Dir",
        description="Hookup library directory (relative path to 'SCS Project Main Directory')",
        default=str(os_rs + 'unit' + os.sep + 'hookup'),
        subtype='NONE',
        update=hookup_library_rel_path_update,
    )
    matsubs_library_rel_path = StringProperty(
        name="Material Substance Library",
        description="Material substance library (relative file path to 'SCS Project Main Directory'; *.db)",
        default=str(os_rs + 'material' + os.sep + 'material.db'),
        subtype='NONE',
        update=matsubs_library_rel_path_update,
    )

    # UPDATE LOCKS (FOR AVOIDANCE OF RECURSION)
    # cgfx_update_lock = BoolProperty(
    # name="Update Lock for CgFX UI",
    # description="Allows temporarily lock CgFX UI updates",
    # default=False,
    # )
    config_update_lock = BoolProperty(
        name="Update Lock For Config Items",
        description="Allows temporarily lock automatic updates for all items which are stored in config file",
        default=False,
    )
    import_in_progress = BoolProperty(
        name="Indicator of import process",
        description="Holds the state of SCS import process",
        default=False,
    )

    # SETTINGS WHICH GET SAVED IN CONFIG FILE
    def dump_level_update(self, context):
        # utils.update_item_in_config_file(utils.get_config_filepath(), 'Various.DumpLevel', self.dump_level)
        _config_container.update_item_in_file('Header.DumpLevel', self.dump_level)
        return None

    def import_scale_update(self, context):
        _config_container.update_item_in_file('Import.ImportScale', float(self.import_scale))
        return None

    def import_pim_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPimFile', int(self.import_pim_file))
        return None

    def auto_welding_update(self, context):
        _config_container.update_item_in_file('Import.AutoWelding', int(self.auto_welding))
        return None

    def import_pit_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPitFile', int(self.import_pit_file))
        return None

    def load_textures_update(self, context):
        _config_container.update_item_in_file('Import.LoadTextures', int(self.load_textures))
        return None

    def import_pic_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPicFile', int(self.import_pic_file))
        return None

    def import_pip_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPipFile', int(self.import_pip_file))
        return None

    def import_pis_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPisFile', int(self.import_pis_file))
        return None

    def connected_bones_update(self, context):
        _config_container.update_item_in_file('Import.ConnectedBones', int(self.connected_bones))
        return None

    def bone_import_scale_update(self, context):
        _config_container.update_item_in_file('Import.BoneImportScale', float(self.bone_import_scale))
        return None

    def import_pia_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPiaFile', int(self.import_pia_file))
        return None

    def search_subdirs_for_pia_update(self, context):
        _config_container.update_item_in_file('Import.IncludeSubdirsForPia', int(self.include_subdirs_for_pia))
        return None

    def mesh_creation_type_update(self, context):
        _config_container.update_item_in_file('Import.MeshCreationType', self.mesh_creation_type)
        return None

    def content_type_update(self, context):
        _config_container.update_item_in_file('Export.ContentType', self.content_type)
        return None

    def export_scale_update(self, context):
        _config_container.update_item_in_file('Export.ExportScale', float(self.export_scale))
        return None

    def apply_modifiers_update(self, context):
        _config_container.update_item_in_file('Export.ApplyModifiers', int(self.apply_modifiers))
        return None

    def exclude_edgesplit_update(self, context):
        _config_container.update_item_in_file('Export.ExcludeEdgesplit', int(self.exclude_edgesplit))
        return None

    def include_edgesplit_update(self, context):
        _config_container.update_item_in_file('Export.IncludeEdgesplit', int(self.include_edgesplit))
        return None

    def active_uv_only_update(self, context):
        _config_container.update_item_in_file('Export.ActiveUVOnly', int(self.active_uv_only))
        return None

    def export_vertex_groups_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexGroups', int(self.export_vertex_groups))
        return None

    def export_vertex_color_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColor', int(self.export_vertex_color))
        return None

    def export_vertex_color_type_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColorType', self.export_vertex_color_type)
        return None

    def export_vertex_color_type_7_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColorType7', self.export_vertex_color_type_7)
        return None

    '''
    # def export_anim_file_update(self, context):
    #     utils.update_item_in_config_file(utils.get_config_filepath(), 'Export.ExportAnimFile', self.export_anim_file)
    #     # if self.export_anim_file == 'anim':
    #         # _get_scs_globals().export_pis_file = True
    #         # _get_scs_globals().export_pia_file = True
    #     # else:
    #         # _get_scs_globals().export_pis_file = False
    #         # _get_scs_globals().export_pia_file = False
    #     return None
    '''

    def export_pim_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPimFile', int(self.export_pim_file))
        return None

    def output_type_update(self, context):
        _config_container.update_item_in_file('Export.OutputType', self.output_type)
        return None

    def export_pit_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPitFile', int(self.export_pit_file))
        return None

    def export_pic_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPicFile', int(self.export_pic_file))
        return None

    def export_pip_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPipFile', int(self.export_pip_file))
        return None

    def export_pis_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPisFile', int(self.export_pis_file))
        return None

    def export_pia_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPiaFile', int(self.export_pia_file))
        return None

    def sign_export_update(self, context):
        _config_container.update_item_in_file('Export.SignExport', int(self.sign_export))
        return None

    # IMPORT & EXPORT OPTIONS
    dump_level = EnumProperty(
        name="Printouts",
        items=(
            ('0', "0 - Errors Only", "Print only Errors to the console"),
            ('1', "1 - Errors and Warnings", "Print Errors and Warnings to the console"),
            ('2', "2 - Errors, Warnings, Info", "Print Errors, Warnings and Info to the console"),
            ('3', "3 - Errors, Warnings, Info, Debugs", "Print Errors, Warnings, Info and Debugs to the console"),
            ('4', "4 - Errors, Warnings, Info, Debugs, Specials", "Print Errors, Warnings, Info, Debugs and Specials to the console"),
        ),
        default='2',
        update=dump_level_update,
    )

    # IMPORT OPTIONS
    import_scale = FloatProperty(
        name="Scale",
        description="Import scale of model",
        min=0.001, max=1000.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        update=import_scale_update,
    )
    import_pim_file = BoolProperty(
        name="Import Model (PIM)",
        description="Import Model data from PIM file",
        default=True,
        update=import_pim_file_update,
    )
    auto_welding = BoolProperty(
        name="Auto Welding",
        description="Use automatic routine for welding of divided mesh surfaces",
        default=True,
        update=auto_welding_update,
    )
    import_pit_file = BoolProperty(
        name="Import Trait (PIT)",
        description="Import Trait information from PIT file",
        default=True,
        update=import_pit_file_update,
    )
    load_textures = BoolProperty(
        name="Load Textures",
        description="Load textures",
        default=True,
        update=load_textures_update,
    )
    import_pic_file = BoolProperty(
        name="Import Collision (PIC)",
        description="Import Collision envelops from PIC file",
        default=True,
        update=import_pic_file_update,
    )
    import_pip_file = BoolProperty(
        name="Import Prefab (PIP)",
        description="Import Prefab from PIP file",
        default=True,
        update=import_pip_file_update,
    )
    import_pis_file = BoolProperty(
        name="Import Skeleton (PIS)",
        description="Import Skeleton from PIS file",
        default=True,
        update=import_pis_file_update,
    )
    connected_bones = BoolProperty(
        name="Create Connected Bones",
        description="Create connected Bones whenever possible",
        default=False,
        update=connected_bones_update,
    )
    bone_import_scale = FloatProperty(
        name="Bone Scale",
        description="Import scale for Bones",
        min=0.0001, max=10.0,
        soft_min=0.001, soft_max=1.0,
        default=0.01,
        update=bone_import_scale_update,
    )
    import_pia_file = BoolProperty(
        name="Import Animations (PIA)",
        description="Import Animations from all corresponding PIA files found in the same directory",
        default=True,
        update=import_pia_file_update,
    )
    include_subdirs_for_pia = BoolProperty(
        name="Search Subdirectories",
        description="Search also all subdirectories for animation files (PIA)",
        default=True,
        update=search_subdirs_for_pia_update,
    )
    mesh_creation_type = EnumProperty(
        name="Mesh CT",
        description="This is a DEBUG option, that refers to Mesh Creation Type",
        items=(
            ('mct_bm', "BMesh", "Use 'BMesh' method to create a geometry"),
            ('mct_tf', "TessFaces", "Use 'TessFaces' method to create a geometry"),
            ('mct_mp', "MeshPolygons", "Use 'MeshPolygons' method to create a geometry")
        ),
        default='mct_bm',
        update=mesh_creation_type_update,
    )

    # EXPORT OPTIONS
    content_type = EnumProperty(
        name="Content",
        items=(
            ('selection', "Selection", "Export selected objects only"),
            ('scene', "Active Scene", "Export only objects within active scene"),
            ('scenes', "All Scenes", "Export objects from all scenes"),
        ),
        default='scene',
        update=content_type_update,
    )
    export_scale = FloatProperty(
        name="Scale",
        description="Export scale of model",
        min=0.01, max=1000.0,
        soft_min=0.01, soft_max=1000.0,
        default=1.0,
        update=export_scale_update,
    )
    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Export meshes as modifiers were applied",
        default=True,
        update=apply_modifiers_update,
    )
    exclude_edgesplit = BoolProperty(
        name="Exclude 'Edge Split'",
        description="When you use Sharp Edge flags, then prevent 'Edge Split' modifier from "
                    "dismemberment of the exported mesh - the correct smoothing will be still "
                    "preserved with use of Sharp Edge Flags",
        default=True,
        update=exclude_edgesplit_update,
    )
    include_edgesplit = BoolProperty(
        name="Apply Only 'Edge Split'",
        description="When you use Sharp Edge flags and don't want to apply modifiers, "
                    "then use only 'Edge Split' modifier for dismemberment of the exported mesh "
                    "- the only way to preserve correct smoothing",
        default=True,
        update=include_edgesplit_update,
    )
    active_uv_only = BoolProperty(
        name="Only Active UVs",
        description="Export only active UV layer coordinates",
        default=False,
        update=active_uv_only_update,
    )
    export_vertex_groups = BoolProperty(
        name="Vertex Groups",
        description="Export all existing 'Vertex Groups'",
        default=True,
        update=export_vertex_groups_update,
    )
    export_vertex_color = BoolProperty(
        name="Vertex Color",
        description="Export active vertex color layer",
        default=True,
        update=export_vertex_color_update,
    )
    export_vertex_color_type = EnumProperty(
        name="Vertex Color Type",
        description="Vertex color type",
        items=(
            ('rgbda', "RGBA (Dummy Alpha)", "RGB color information with dummy alpha set to 1 (usually necessary)"),
            ('rgba', "RGBA (Alpha From Another Layer)", "RGB color information + alpha from other layer"),
        ),
        default='rgbda',
        update=export_vertex_color_type_update,
    )
    export_vertex_color_type_7 = EnumProperty(
        name="Vertex Color Type",
        description="Vertex color type",
        items=(
            ('rgb', "RGB", "Only RGB color information is exported"),
            ('rgbda', "RGBA (Dummy Alpha)", "RGB color information with dummy alpha set to 1 (usually necessary)"),
            ('rgba', "RGBA (Alpha From Another Layer)", "RGB color information + alpha from other layer"),
        ),
        default='rgbda',
        update=export_vertex_color_type_7_update,
    )
    export_pim_file = BoolProperty(
        name="Export Model",
        description="Export model automatically with file save",
        default=True,
        update=export_pim_file_update,
    )
    output_type = EnumProperty(
        name="Output Format",
        items=(
            ('5', "Game Data Format, ver. 5", "Export PIM (version 5) file formats for SCS Game Engine"),
            ('def1', "Data Exchange Format, ver. 1",
             "Export 'PIM Data Exchange Formats' (version 1) file formats designed for data exchange between different modeling tools"),
            # ('7', "PIM Data Exchange Formats, ver. 1", "Export 'PIM Data Exchange Formats' (version 1) file formats designed for data
            # exchange between different modeling tools"),
        ),
        default='5',
        update=output_type_update,
    )
    export_pit_file = BoolProperty(
        name="Export PIT",
        description="PIT...",
        default=True,
        update=export_pit_file_update,
    )
    export_pic_file = BoolProperty(
        name="Export Collision",
        description="Export collision automatically with file save",
        default=True,
        update=export_pic_file_update,
    )
    export_pip_file = BoolProperty(
        name="Export Prefab",
        description="Export prefab automatically with file save",
        default=True,
        update=export_pip_file_update,
    )
    export_pis_file = BoolProperty(
        name="Export Skeleton",
        description="Export skeleton automatically with file save",
        default=True,
        update=export_pis_file_update,
    )
    export_pia_file = BoolProperty(
        name="Export Animations",
        description="Export animations automatically with file save",
        default=True,
        update=export_pia_file_update,
    )
    sign_export = BoolProperty(
        name="Write A Signature To Exported Files",
        description="Add a signature to the header of the output files with some additional information",
        default=False,
        update=sign_export_update,
    )
    # not used at the moment...
    skeleton_name = StringProperty(
        name="Skeleton Name",
        default="_INHERITED",
    )


class SceneSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Scene Variables - ...Scene.scs_props...
    :return:
    """

    part_settings_expand = BoolProperty(
        name="Expand Part Settings",
        description="Expand Part settings panel",
        default=True,
    )
    part_tools_expand = BoolProperty(
        name="Expand Part Tools",
        description="Expand Part tools panel",
        default=False,
    )
    part_list_sorted = BoolProperty(
        name="Part List Sorted Alphabetically",
        description="Sort Part list alphabetically",
        default=False,
    )

    # VARIANTS
    def update_variant_items(self, context):
        """
        Returns the actual Variant name list from "scs_variant_inventory".
        It also updates "variants_container", so the UI could contain all
        the items with no error. (necessary hack :-/)
        :param context:
        :return:
        """
        global variants_container
        items = []
        if context.scene.scs_props.variant_list_sorted:
            inventory = {}
            for variant_i, variant in enumerate(context.scene.scs_variant_inventory):
                inventory[variant.name] = variant_i
            for variant in sorted(inventory):
                variant_i = inventory[variant]
                act_variant = variants_container.add(variant)
                items.append((act_variant, act_variant, "", 'GROUP', variant_i), )
        else:
            for variant_i, variant in enumerate(context.scene.scs_variant_inventory):
                act_variant = variants_container.add(variant.name)
                items.append((act_variant, act_variant, "", 'GROUP', variant_i), )
        return tuple(items)

    def get_variant_items(self):
        """
        Returns menu index of a Variant name of actual object to set
        the right name in UI drop-down menu.
        :return:
        """
        result = 0
        for variant_i, variant in enumerate(bpy.context.scene.scs_variant_inventory):
            if variant.active:
                result = variant_i
                break
        return result

    def set_variant_items(self, value):
        """
        Receives an actual index of currently selected Variant name in the drop-down menu
        and sets that Variant name as active in Variant Inventory...
        :param value:
        :return:
        """
        for variant_i, variant in enumerate(bpy.context.scene.scs_variant_inventory):
            if value == variant_i:
                variant.active = True
            else:
                variant.active = False

    part_variants = EnumProperty(
        name="Current Variant",
        description="Current Variant",
        items=update_variant_items,
        get=get_variant_items,
        set=set_variant_items,
    )

    variant_settings_expand = BoolProperty(
        name="Expand Variant Settings",
        description="Expand Variant settings panel",
        default=True,
    )
    variant_tools_expand = BoolProperty(
        name="Expand Variant Tools",
        description="Expand Variant tools panel",
        default=False,
    )
    variant_list_sorted = BoolProperty(
        name="Variant List Sorted Alphabetically",
        description="Sort Variant list alphabetically",
        default=False,
    )
    variant_views = EnumProperty(
        name="Variant View Setting",
        description="Variant view style options",
        items=(
            ('compact', "Compact", "Compact view (settings just for one Variant at a time)", 'FULLSCREEN', 0),
            ('vertical', "Vertical", "Vertical long view (useful for larger number of Variants)", 'LONGDISPLAY', 1),
            ('horizontal', "Horizontal", "Horizontal table view (best for smaller number of Variants)", 'SHORTDISPLAY', 2),
            ('integrated', "Integrated", "Integrated in Variant list (best for smaller number of Parts)", 'LINENUMBERS_OFF', 3),
        ),
        default='horizontal',
    )

    '''
    CGFX SHADERS
    def update_cgfx(self, context):
        """Returns the actual CgFX name list from "scs_cgfx_inventory".
        It also updates "cgfx_container", so the UI could contain all
        the items with no error. (necessary hack :-/)"""
        # print('  > update_cgfx...')
        global cgfx_container

        def append_cgfx(items, act_cgfx, cgfx_i):
            """Appends CgFX shader item and choose the icon for it."""
            if ".dif" in act_cgfx:
                items.append((act_cgfx, act_cgfx, "", 'SOLID', cgfx_i), )
            else:
                items.append((act_cgfx, act_cgfx, "", 'SMOOTH', cgfx_i), )
            return items

        items = []
        if context.scene.scs_props.cgfx_list_sorted:
            inventory = {}
            for cgfx_i, cgfx in enumerate(context.scene.scs_cgfx_inventory):
                inventory[cgfx.name] = cgfx_i
            for cgfx in sorted(inventory):
                cgfx_i = inventory[cgfx]
                act_cgfx = cgfx_container.add(cgfx)
                items = append_cgfx(items, act_cgfx, cgfx_i)
        else:
            for cgfx_i, cgfx in enumerate(context.scene.scs_cgfx_inventory):
                act_cgfx = cgfx_container.add(cgfx.name)
                items = append_cgfx(items, act_cgfx, cgfx_i)
        return tuple(items)

    def get_cgfx_items(self):
        """Returns menu index of a CgFX shader name of actual Material to set
        the right name in UI menu."""
        # print('  > get_cgfx_items...')
        result = 0
        for cgfx_i, cgfx in enumerate(bpy.context.scene.scs_cgfx_inventory):
            if cgfx.active:
                result = cgfx_i
                break
        return result

    def set_cgfx_items(self, value):
        """Receives an actual index of currently selected CgFX shader name in the menu,
        sets that CgFX shader name as active in CgFX shader Inventory and sets
        the same shader name in active Material."""
        # print('  > set_cgfx_items...')
        for cgfx_i, cgfx in enumerate(bpy.context.scene.scs_cgfx_inventory):
            if value == cgfx_i:
                cgfx.active = True
                ## Set CgFX in the material
                material = bpy.context.active_object.active_material
                cgfx_templates_list = bpy.context.scene.scs_props.cgfx_templates_list
                if cgfx_templates_list == "custom": cgfx_templates_list = "<custom>"
                material.scs_props.cgfx_template = cgfx_templates_list
                print('material: "%s"\t- CgFX: "%s" (%i)' % (material.name, cgfx.name, cgfx_i))
                material.scs_props.cgfx_filename = cgfx.name
                ## Get a valid path to CgFX Shader file
                cgfx_filepath = cgfx_utils.get_cgfx_filepath(cgfx.name)
                if cgfx_filepath:
                    ## Compile CgFX Shader file
                    output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                    cgfx_utils.register_cgfx_ui(material, utils.get_actual_look())
            else:
                cgfx.active = False

    cgfx_file_list = EnumProperty(
            name="Active CgFX Shader",
            description="Active CgFX shader",
            items=update_cgfx,
            get=get_cgfx_items,
            set=set_cgfx_items,
            )
    cgfx_list_sorted = BoolProperty(
            name="CgFX Shader List Sorted Alphabetically",
            description="Sort CgFX shader list alphabetically",
            default=True,
            )
    '''

    # TODO: rename this ShaderNamesDictionary to some generic name used for enumeration and move it to proper class
    class ShaderNamesDictionary:
        """
        Dictionary for saving unique names of shader names loaded from presets file.

        NOTE:
        Necessary to store dictionary of presets names because of blender
        restriction that enum ID properties which are generated with
        callback function needs to have references of it's items strings
        """

        def __init__(self):
            self.preset = {}

        def add(self, new_preset):
            if new_preset not in self.preset:
                self.preset[new_preset] = new_preset
            return self.preset[new_preset]

        def has(self, preset_name):
            if preset_name in self.preset:
                return True
            else:
                return False

    @staticmethod
    def get_shader_icon_str(preset_name):
        """
        Returns icon string for given preset name.

        :type preset_name: str
        :param preset_name: Name of shader preset
        :rtype: str
        """
        if preset_name != "<none>":  # The item already exists...
            if "spec" in preset_name:
                icon_str = 'MATERIAL'
            elif "glass" in preset_name:
                icon_str = 'MOD_LATTICE'
            elif "lamp" in preset_name:
                icon_str = 'LAMP_SPOT'
            elif "shadowonly" in preset_name:
                icon_str = 'MAT_SPHERE_SKY'
            elif "truckpaint" in preset_name:
                icon_str = 'AUTO'
            elif "mlaa" in preset_name:
                icon_str = 'GROUP_UVS'
            else:
                icon_str = 'SOLID'
        else:
            icon_str = None
        return icon_str

    def update_shader_presets(self, context):
        """
        Returns the actual Shader name list from "scs_shader_presets_inventory".
        It also updates "shader_presets_container", so the UI could contain all
        the items with no error. (necessary hack :-/)
        :param context:
        :return:
        """

        items = [("<none>", "<none>", "No SCS shader preset in use (may result in incorrect model output)", 'X_VEC', 0)]

        # print('  > update_shader_presets...')

        # save dictionary of preset names references in globals so that UI doesn't mess up strings
        if not "shader_presets_container" in globals():
            global shader_presets_container
            shader_presets_container = SceneSCSProps.ShaderNamesDictionary()
            # print("Presets container created!")

        if context.scene.scs_props.shader_preset_list_sorted:
            inventory = {}
            for preset_i, preset in enumerate(context.scene.scs_shader_presets_inventory):
                inventory[preset.name] = preset_i
            for preset in sorted(inventory):
                preset_i = inventory[preset]
                act_preset = shader_presets_container.add(preset)
                # print(' + %i act_preset: %s (%s)' % (preset_i, str(act_preset), str(preset)))
                icon_str = SceneSCSProps.get_shader_icon_str(act_preset)
                if icon_str is not None:  # if None then it's <none> preset which is already added
                    items.append((act_preset, act_preset, "", icon_str, preset_i))
        else:
            for preset_i, preset in enumerate(context.scene.scs_shader_presets_inventory):
                act_preset = shader_presets_container.add(preset.name)
                # print(' + %i act_preset: %s (%s)' % (preset_i, str(act_preset), str(preset)))
                icon_str = SceneSCSProps.get_shader_icon_str(act_preset)
                if icon_str is not None:  # if None then it's <none> preset which is already added
                    items.append((act_preset, act_preset, "", icon_str, preset_i))
        return items

    def get_shader_presets_item(self):
        """
        Returns menu index of a Shader preset name of actual Material to set
        the right name in UI menu.
        :return:
        """
        # print('  > get_shader_presets_items...')
        material = bpy.context.active_object.active_material
        result = 0

        for preset_i, preset in enumerate(bpy.context.scene.scs_shader_presets_inventory):
            if preset.name == material.scs_props.active_shader_preset_name:
                result = preset_i

        return result

    def set_shader_presets_item(self, value):
        """
        Receives an actual index of currently selected Shader preset name in the menu,
        sets that Shader name as active in active Material.
        :param value:
        :return:
        """

        scene = bpy.context.scene
        material = bpy.context.active_object.active_material
        if value == 0:  # No Shader...
            material.scs_props.active_shader_preset_name = "<none>"
            material.scs_props.mat_effect_name = "None"
            material["scs_shader_attributes"] = {}
        else:
            for preset_i, preset in enumerate(scene.scs_shader_presets_inventory):
                if value == preset_i:

                    material.scs_props.active_shader_preset_name = preset.name

                    # Set Shader Preset in the Material
                    preset_section = _material_utils.get_shader_preset(_get_scs_globals().shader_presets_filepath, preset.name)

                    if preset_section:
                        preset_name = preset_section.get_prop_value("PresetName")
                        preset_effect = preset_section.get_prop_value("Effect")
                        material.scs_props.mat_effect_name = preset_effect

                        if preset_name:
                            _material_utils.set_shader_data_to_material(material, preset_section, preset_effect)
                        else:
                            material.scs_props.active_shader_preset_name = "<none>"
                            material["scs_shader_attributes"] = {}
                            print('    NO "preset_name"!')
                            # if preset_effect:
                            # print('      preset_effect: "%s"' % preset_effect)
                            # if preset_flags:
                            # print('      preset_flags: "%s"' % preset_flags)
                            # if preset_attribute_cnt:
                            # print('      preset_attribute_cnt: "%s"' % preset_attribute_cnt)
                            # if preset_texture_cnt:
                            # print('      preset_texture_cnt: "%s"' % preset_texture_cnt)
                    else:
                        print('''NO "preset_section"! (Shouldn't happen!)''')
                else:
                    preset.active = False

    shader_preset_list = EnumProperty(
        name="Shader Presets",
        description="Shader presets",
        items=update_shader_presets,
        get=get_shader_presets_item,
        set=set_shader_presets_item,
    )
    shader_preset_list_sorted = BoolProperty(
        name="Shader Preset List Sorted Alphabetically",
        description="Sort Shader preset list alphabetically",
        default=False,
    )

    '''
    CGFX TEMPLATES
    def update_cgfx_template(self, context):
        """Returns the actual CgFX name list from "scs_cgfx_template_inventory".
        It also updates "cgfx_template_container", so the UI could contain all
        the items with no error. (necessary hack :-/)"""
        #print('  > update_cgfx_template...')
        global cgfx_template_container

        def append_cgfx_template(items, act_template, template_i):
            """Appends given Template item and choose the icon for it."""
            if act_template != "<custom>":  # The item already exists...
                if "dif" in act_template:
                    items.append((act_template, act_template, "", 'SOLID', template_i), )
                else:
                    items.append((act_template, act_template, "", 'TEXTURE_SHADED', template_i), )
            return items

        # items = []
        items = [("custom", "<custom>", "Use CgFX shader definition files for manual material setup", 'SOLID', 0)]
        if context.scene.scs_props.cgfx_templates_list_sorted:
            inventory = {}
            for template_i, template in enumerate(context.scene.scs_cgfx_template_inventory):
                inventory[template.name] = template_i
            for template in sorted(inventory):
                template_i = inventory[template]
                act_template = cgfx_template_container.add(template)
                # print(' + %i act_template: %s (%s)' % (template_i, str(act_template), str(template)))
                items = append_cgfx_template(items, act_template, template_i)
        else:
            for template_i, template in enumerate(context.scene.scs_cgfx_template_inventory):
                act_template = cgfx_template_container.add(template.name)
                # print(' + %i act_template: %s (%s)' % (template_i, str(act_template), str(template)))
                items = append_cgfx_template(items, act_template, template_i)
        return tuple(items)

    def get_cgfx_templates_items(self):
        """Returns menu index of a CgFX shader name of actual material to set
        the right name in UI menu."""
        #print('  > get_cgfx_templates_items...')
        result = 0
        for template_i, template in enumerate(bpy.context.scene.scs_cgfx_template_inventory):
            if template.active:
                result = template_i
        return result

    def set_cgfx_templates_items(self, value):
        """Receives an actual index of currently selected CgFX shader name in the menu,
        sets that CgFX shader name as active in CgFX shader Inventory and sets
        the same shader name in active material."""
        print('  > set_cgfx_templates_items...')

        def apply_template_setting(material, actual_look, prop_name, prop_type, prop_value, prop_enabled):
            """."""
            # print('  > apply_template_setting()')
            all_values = {}
            if prop_name in material.scs_cgfx_looks[actual_look].cgfx_data:
                if material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].type == prop_type:
                    # print('prop_name: "%s"' % str(prop_name))
                    # print('prop_value: %s' % str(prop_value))
                    if prop_type == "bool":
                        prop_value = prop_value.lower()
                    elif prop_type == "enum":
                        pass
                    elif prop_type == "float":
                        prop_value = str(prop_value)
                        all_values["cgfx_" + prop_name] = prop_value
                    elif prop_type in ("float2", "float3"):
                        prop_value = "(" + str(prop_value)[1:-1] + ")"
                        all_values["cgfx_" + prop_name] = prop_value
                    elif prop_type == "color":
                        rgb, mult = utils.make_color_mtplr(prop_value)
                        prop_value = "(" + str(rgb)[1:-1] + ", " + str(mult) + ")"
                        all_values["cgfx_" + prop_name] = prop_value
                    else:
                        all_values["cgfx_" + prop_name] = str('"' + prop_value + '"')
                    material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].value = prop_value
                    if prop_enabled == "True":
                        material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].enabled = True
                    elif prop_enabled == "False":
                        material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].enabled = False
                    else:
                        print('WARNING - unknown property "enabled" state found: "%s"' % prop_enabled)

            cgfx_utils.update_ui_props_from_matlook_record(all_values)

        def read_template_settings(material, actual_look, section):
            """."""
            print('  > read_template_settings()')
            #actual_look = utils.get_actual_look()
            for item in section.sections:
                # print('  item:\n%s' % repr(item))
                # print('      type: %s - props: "%s"' % (item.type, str(item.props)))
                if item.type == "Item":
                    prop_name = prop_type = prop_value = prop_enabled = None
                    for prop in item.props:
                        # print('      prop: "%s"' % str(prop))
                        if prop[0] == "#":
                            continue
                        elif prop[0] == "Name":
                            prop_name = prop[1]
                        elif prop[0] == "Type":
                            prop_type = prop[1]
                        elif prop[0] == "Value":
                            prop_value = prop[1]
                        elif prop[0] == "Enabled":
                            prop_enabled = prop[1]
                        else:
                            print('WARNING - unknown property found: "%s"' % str(prop))
                    # if prop_name and prop_type and prop_value and prop_enabled:
                    # print('      prop_name: %s - prop_type: %s - prop_value: %s - prop_enabled: %s' % (prop_name, prop_type, prop_value,
    prop_enabled))
                    apply_template_setting(material, actual_look, prop_name, prop_type, prop_value, prop_enabled)

        scene = bpy.context.scene
        for template_i, template in enumerate(scene.scs_cgfx_template_inventory):
            if value == template_i:
                template.active = True
                material = bpy.context.active_object.active_material
                actual_look = utils.get_actual_look()
                material.scs_props.cgfx_template = template.name
                if value == 0:  # Custom CgFX shader...
                    print('    custom CgFX shader...')
                    print('      cgfx_file_list: "%s"' % scene.scs_props.cgfx_file_list)
                    print('      cgfx_filename:  "%s"' % material.scs_props.cgfx_filename)
                    material.scs_props.cgfx_filename = scene.scs_props.cgfx_file_list
                    # Compile CgFX Shader file
                    output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                    cgfx_utils.register_cgfx_ui(material, actual_look)
                    for item in material.scs_cgfx_looks[actual_look].cgfx_data: item.enabled = True
                else:
                    # Set CgFX in the Material
                    # print('    material: "%s"\t- CgFX: "%s" (%i)' % (material.name, template.name, template_i))
                    template_section = utils.get_cgfx_template(_get_scs_globals().cgfx_templates_filepath, template.name)
                    # template_settings = {}
                    if template_section:
                        cgfx_name = utils.get_prop_value_from_section(template_section, "CgFXFile")
                        if cgfx_name:
                            if cgfx_name.endswith(".cgfx"): cgfx_name = cgfx_name[:-5]
                            material.scs_props.cgfx_filename = cgfx_name
                            # Get a valid path to CgFX Shader file
                            cgfx_filepath = cgfx_utils.get_cgfx_filepath(cgfx_name)
                            # print('    cgfx_filepath: "%s"' % cgfx_filepath)
                            if cgfx_filepath:
                                # Compile CgFX Shader file
                                output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                                cgfx_utils.register_cgfx_ui(material, actual_look)
                            read_template_settings(material, actual_look, template_section)
                        else:
                            print('NO "cgfx_name"!')
                    else:
                        print('NO "template_section"!')
            else:
                template.active = False

    cgfx_templates_list = EnumProperty(
            name="CgFX Shader Templates",
            description="CgFX shader templates",
            items=update_cgfx_template,
            get=get_cgfx_templates_items,
            set=set_cgfx_templates_items,
            )
    cgfx_templates_list_sorted = BoolProperty(
            name="CgFX Shader Template List Sorted Alphabetically",
            description="Sort CgFX shader template list alphabetically",
            default=True,
            )
    '''

    # VISIBILITY VARIABLES
    scs_part_panel_expand = BoolProperty(
        name="Expand SCS Part Panel",
        description="Expand SCS Part panel",
        default=True,
    )
    scs_variant_panel_expand = BoolProperty(
        name="Expand SCS Variant Panel",
        description="Expand SCS Variant panel",
        default=True,
    )
    test_panel_expand = BoolProperty(
        name="Expand Test Panel",
        description="Expand testing panel",
        default=True,
    )
    empty_object_settings_expand = BoolProperty(
        name="Expand SCS Object Settings",
        description="Expand SCS Object settings panel",
        default=True,
    )
    locator_settings_expand = BoolProperty(
        name="Expand Locator Settings",
        description="Expand locator settings panel",
        default=True,
    )
    locator_display_settings_expand = BoolProperty(
        name="Expand Locator Display Settings",
        description="Expand locator display settings panel",
        default=False,
    )
    shader_attributes_expand = BoolProperty(
        name="Expand SCS Material Attributes",
        description="Expand SCS material attributes panel",
        default=True,
    )
    shader_textures_expand = BoolProperty(
        name="Expand SCS Material Textures",
        description="Expand SCS material textures panel",
        default=True,
    )
    '''
    cgfx_shader_expand = BoolProperty(
    name="Expand CgFX Shader Settings",
    description="Expand CgFX shader settings panel",
    default=True,
    )
    cgfx_parameter_expand = BoolProperty(
        name="Expand CgFX Parameters",
        description="Expand CgFX parameters panel",
        default=True,
    )
    cgfx_data_expand = BoolProperty(
        name="Expand CgFX Parameters",
        description="Expand CgFX parameters panel",
        default=True,
    )
    cgfx_vertex_data_expand = BoolProperty(
        name="Expand CgFX Vertex Data",
        description="Expand CgFX vertex data panel",
        default=True,
    )
    cgfx_lib_expand = BoolProperty(
        name="Expand Shader Library",
        description="Expand CgFX shader library panel",
        default=False,
    )
    cgfx_templates_expand = BoolProperty(
        name="Expand Shader Templates",
        description="Expand CgFX shader template panel",
        default=False,
    )
    '''
    shader_presets_expand = BoolProperty(
        name="Expand Shader Presets",
        description="Expand shader presets panel",
        default=False,
    )
    global_display_settings_expand = BoolProperty(
        name="Expand Global Display Settings",
        description="Expand global display settings panel",
        default=True,
    )
    global_paths_settings_expand = BoolProperty(
        name="Expand Global Paths Settings",
        description="Expand global paths settings panel",
        default=True,
    )
    scs_root_panel_settings_expand = BoolProperty(
        name="Expand 'SCS Root Object' Settings",
        description="Expand 'SCS Root Object' settings panel",
        default=True,
    )
    global_settings_expand = BoolProperty(
        name="Expand Global Settings",
        description="Expand global settings panel",
        default=True,
    )
    scene_settings_expand = BoolProperty(
        name="Expand Scene Settings",
        description="Expand scene settings panel",
        default=True,
    )
    animation_settings_expand = BoolProperty(
        name="Expand Animation Settings",
        description="Expand animation settings panel",
        default=True,
    )
    animplayer_panel_expand = BoolProperty(
        name="Expand Animation Player Settings",
        description="Expand animation player panel",
        default=True,
    )
    default_export_filepath = StringProperty(
        name="Default Export Path",
        description="Relative export path (relative to SCS Project Base Path) for all SCS Game Objects without custom export path "
                    "(this path does not apply when exporting via menu)",
        default="",
        # subtype="FILE_PATH",
        subtype='NONE',
    )
    export_panel_expand = BoolProperty(
        name="Expand Export Panel",
        description="Expand Export panel",
        default=True,
    )
    preview_export_selection = BoolProperty(
        name="Preview selection",
        description="Preview selection which will be exported",
        default=True,
    )
    preview_export_selection_active = BoolProperty(
        name="Flag indication if selection preview is active",
        description="",
        default=False,
    )

    # VISIBILITY TOOLS SCOPE
    visibility_tools_scope = EnumProperty(
        name="Visibility Tools Scope",
        description="Selects the scope upon visibility tools are working",
        items=(
            ('Global', "Global", "Use scope of the whole scene"),
            ('SCS Root', "SCS Root", "Use the scope of current SCS Root"),
        ),
    )

    # DRAWING MODE SETTINGS
    def drawing_mode_update(self, context):
        from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback

        _open_gl_callback.enable(self.drawing_mode)

    drawing_mode = EnumProperty(
        name="Custom Drawing Mode",
        description="Drawing mode for custom elements (Locators and Connections)",
        items=(
            ('Normal', "Normal", "Use normal depth testing drawing"),
            ('X-ray', "X-ray", "Use X-ray drawing"),
        ),
        update=drawing_mode_update
    )

    # PREVIEW SETTINGS
    def show_preview_models_update(self, context):
        """
        :param context:
        :return:
        """
        scene = context.scene

        for obj in bpy.data.objects:
            if obj.type == 'EMPTY':
                if scene.scs_props.show_preview_models:
                    if not _preview_models.load(obj):
                        _preview_models.unload(obj)
                else:
                    _preview_models.unload(obj)
        return None

    show_preview_models = BoolProperty(
        name="Show Preview Models",
        description="Show preview models for locators",
        default=True,
        update=show_preview_models_update
    )

    # SETTINGS WHICH GET SAVED IN CONFIG FILE
    def display_locators_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayLocators', int(self.display_locators))
        return None

    def locator_size_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.LocatorSize', self.locator_size)
        return None

    def locator_empty_size_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.LocatorEmptySize', self.locator_empty_size)
        return None

    def locator_prefab_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.PrefabLocatorsWire',
                                              tuple(self.locator_prefab_wire_color))
        return None

    def locator_model_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ModelLocatorsWire',
                                              tuple(self.locator_model_wire_color))
        return None

    def locator_coll_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ColliderLocatorsWire',
                                              tuple(self.locator_coll_wire_color))
        return None

    def locator_coll_face_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ColliderLocatorsFace',
                                              tuple(self.locator_coll_face_color))
        return None

    def display_connections_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayConnections', int(self.display_connections))
        return None

    def optimized_connections_drawing_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.OptimizedConnsDrawing', int(self.optimized_connections_drawing))
        return None

    def curve_segments_update(self, context):
        # utils.update_item_in_config_file(utils.get_config_filepath(), 'GlobalDisplay.CurveSegments', int(self.curve_segments))
        _config_container.update_item_in_file('GlobalDisplay.CurveSegments', self.curve_segments)
        return None

    def np_curve_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.NavigationCurveBase', tuple(self.np_connection_base_color))
        return None

    def mp_line_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.MapLineBase', tuple(self.mp_connection_base_color))
        return None

    def tp_line_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.TriggerLineBase', tuple(self.tp_connection_base_color))
        return None

    def display_info_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayTextInfo', self.display_info)
        return None

    def info_text_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.InfoText', tuple(self.info_text_color))
        return None

    # SCS TOOLS GLOBAL SETTINGS - DISPLAY SETTINGS
    display_locators = BoolProperty(
        name="Display Locators",
        description="Display locators in 3D views",
        default=True,
        update=display_locators_update,
    )
    locator_size = FloatProperty(
        name="Locator Size",
        description="Locator display size in 3D views",
        default=1.0,
        min=0.1, max=50,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
        update=locator_size_update,
    )
    locator_empty_size = FloatProperty(
        name="Locator Empty Object Size",
        description="Locator Empty object display size in 3D views",
        default=0.05,
        min=0.05, max=0.2,
        step=0.1,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
        update=locator_empty_size_update,
    )
    locator_prefab_wire_color = FloatVectorProperty(
        name="Prefab Loc Color",
        description="Color for prefab locators in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.5, 0.5, 0.5),
        update=locator_prefab_wire_color_update,
    )
    locator_model_wire_color = FloatVectorProperty(
        name="Model Loc Color",
        description="Color for model locators in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        # default=(0.25, 0.25, 0.25),
        default=(0.08, 0.12, 0.25),
        update=locator_model_wire_color_update,
    )
    locator_coll_wire_color = FloatVectorProperty(
        name="Collider Loc Wire Color",
        description="Color for collider locators' wireframe in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.5, 0.3, 0.1),
        update=locator_coll_wire_color_update,
    )
    locator_coll_face_color = FloatVectorProperty(
        name="Collider Loc Face Color",
        description="Color for collider locators' faces in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.15, 0.05, 0.05),
        # default=(0.065, 0.18, 0.3),
        update=locator_coll_face_color_update,
    )
    display_connections = BoolProperty(
        name="Display Connections",
        description="Display connections in 3D views",
        default=True,
        update=display_connections_update,
    )
    curve_segments = IntProperty(
        name="Curve Segments",
        description="Curve segment number for displaying in 3D views",
        default=16,
        min=4, max=64,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
        update=curve_segments_update,
    )
    optimized_connections_drawing = BoolProperty(
        name="Optimized Connections Draw",
        description="Draw connections only when data are updated ( switching this off might give you FPS  )",
        default=False,
        update=optimized_connections_drawing_update,
    )
    np_connection_base_color = FloatVectorProperty(
        name="Nav Curves Color",
        description="Base color for navigation curves in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.0, 0.1167, 0.1329),
        update=np_curve_color_update,
    )
    mp_connection_base_color = FloatVectorProperty(
        name="Map Line Color",
        description="Base color for map line connections in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.0, 0.2234, 0.0982),
        update=mp_line_color_update,
    )
    tp_connection_base_color = FloatVectorProperty(
        name="Trigger Line Color",
        description="Base color for trigger line connections in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.1706, 0.0, 0.0593),
        update=tp_line_color_update,
    )
    display_info = EnumProperty(
        name="Display Text Info",
        description="Display additional text information in 3D views",
        items=(
            ('none', "None", "No additional information displayed in 3D view"),
            ('locnames', "Locator Names", "Display locator names only in 3D view"),
            # ('locspeed', "Locator Nav. Points - Speed Limits", "Display navigation point locator speed limits in 3D view"),
            ('locnodes', "Locator Nav. Points - Boundary Nodes", "Display navigation point locator boundary node numbers in 3D view"),
            ('loclanes', "Locator Nav. Points - Boundary Lanes", "Display navigation point locator boundary lanes in 3D view"),
            ('locinfo', "Locator Comprehensive Info", "Display comprehensive information for locators in 3D view"),
        ),
        default='none',
        update=display_info_update,
    )
    info_text_color = FloatVectorProperty(
        name="Info Text Color",
        description="Base color for information text in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(1.0, 1.0, 1.0),
        update=info_text_color_update,
    )
    # DATA GROUP NAMING
    group_name = StringProperty(name="Data Group Name", default="SCS_connection_numbers")
    nav_curve_data_name = StringProperty(name="Navigation Curve Data Name", default="nav_curves_used_numbers")
    map_line_data_name = StringProperty(name="Map Line Data Name", default="map_lines_used_numbers")
    tp_line_data_name = StringProperty(name="Trigger Line Data Name", default="tp_lines_used_numbers")

    view_hide_tools = BoolProperty(
        name="",
        description="Switch View / Hide Tools",
        default=True,
    )