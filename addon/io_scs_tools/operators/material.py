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

# Copyright (C) 2013-2015: SCS Software

import bpy
import os
from bpy.props import StringProperty
from io_scs_tools.exp import tobj as _tobj_exp
from io_scs_tools.internals import looks as _looks
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils


class CustomMapping:
    """
    Wrapper class for better navigation in file
    """

    class AddCustomMapping(bpy.types.Operator):
        bl_label = "Add Custom TexCoord Mapping"
        bl_idname = "material.add_custom_tex_coord_map"
        bl_description = "Add custom TexCoord mapping to list"

        def execute(self, context):
            material = context.active_object.active_material

            if material:
                item = material.scs_props.custom_tex_coord_maps.add()
                item.name = "text_coord_x"

            return {'FINISHED'}

    class RemoveCustomMapping(bpy.types.Operator):
        bl_label = "Remove Custom TexCoord Mapping"
        bl_idname = "material.remove_custom_tex_coord_map"
        bl_description = "Remove selected custom TexCoord mapping from list"

        def execute(self, context):
            material = context.active_object.active_material

            if material:

                material.scs_props.custom_tex_coord_maps.remove(material.scs_props.active_custom_tex_coord)

            return {'FINISHED'}

    class NormalMapMappingInfo(bpy.types.Operator):
        bl_label = "Mapping info for normal maps"
        bl_idname = "material.show_normal_maps_mapping_info"
        bl_description = "Maping value for normal maps is in the case of imported shader used for defining uv map layer for tangent calculations!"

        @staticmethod
        def popup_draw(self, context):
            self.layout.row().label("Maping value for normal maps is in the case of imported shader")
            self.layout.row().label("also used for defining uv map layer for tangent calculations!")
            self.layout.row().label("If the uv map is not provided first entry from Mappings list above will be used!")

        def execute(self, context):
            bpy.context.window_manager.popup_menu(self.popup_draw, title="Mapping Info", icon="INFO")
            return {'FINISHED'}


class Looks:
    """
    Wrapper class for better navigation in file
    """

    class WriteThrough(bpy.types.Operator):
        bl_label = "Write Through"
        bl_idname = "material.scs_looks_wt"
        bl_description = "Write current material value through all currently defined looks within SCS Game Object"

        property_str = StringProperty(
            description="String representing which property should be written through.",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):
            material = context.active_object.active_material

            if material and hasattr(material.scs_props, self.property_str):

                scs_root = _object_utils.get_scs_root(context.active_object)

                if scs_root:
                    altered_looks = _looks.write_through(scs_root, material, self.property_str)
                    if altered_looks > 0:
                        message = "Write through successfully altered %s looks!" % altered_looks
                    else:
                        message = "Nothing to write through."

                    self.report({'INFO'}, message)

            return {'FINISHED'}


class Tobj:
    """
    Wrapper class for better navigation in file
    """

    class ReloadTOBJ(bpy.types.Operator):
        bl_label = "Reload TOBJ settings"
        bl_idname = "material.scs_reload_tobj"
        bl_description = "Reload TOBJ file for this texture (if marked red TOBJ file is out of sync)"

        texture_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            material = context.active_object.active_material

            if material:

                _material_utils.reload_tobj_settings(material, self.texture_type)

            return {'FINISHED'}

    class CreateTOBJ(bpy.types.Operator):
        bl_label = "Create TOBJ"
        bl_idname = "material.scs_create_tobj"
        bl_description = "Create TOBJ file for this texture with default settings"

        texture_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            material = context.active_object.active_material

            if material:
                shader_texture_filepath = getattr(material.scs_props, "shader_texture_" + self.texture_type)

                if _material_utils.is_valid_shader_texture_path(shader_texture_filepath):

                    tex_filepath = _path_utils.get_abs_path(shader_texture_filepath)

                    if tex_filepath and (tex_filepath.endswith(".tga") or tex_filepath.endswith(".png")):

                        if _tobj_exp.export(tex_filepath[:-4] + ".tobj", os.path.basename(tex_filepath), set()):

                            _material_utils.reload_tobj_settings(material, self.texture_type)

                else:
                    self.report({'ERROR'}, "Please load texture properly first!")

            return {'FINISHED'}


class LampSwitcher:
    """
    Wrapper class for better navigation in file
    """

    class SwitchLampMask(bpy.types.Operator):
        bl_label = "Switch Lamp Mask"
        bl_idname = "material.scs_switch_lampmask"
        bl_description = "Show/Hide specific areas of lamp mask texture in lamp materials."

        lamp_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            from io_scs_tools.internals.shaders.eut2.std_node_groups.lampmask_mixer import LAMPMASK_MIX_G

            if LAMPMASK_MIX_G in bpy.data.node_groups:

                lampmask_nodes = bpy.data.node_groups[LAMPMASK_MIX_G].nodes
                if self.lamp_type in lampmask_nodes:

                    input_switch = lampmask_nodes[self.lamp_type].inputs[0]
                    if input_switch.default_value == 0:
                        input_switch.default_value = 1
                        self.report({"INFO"}, "'" + self.lamp_type + "' is turned ON.")
                    else:
                        input_switch.default_value = 0
                        self.report({"INFO"}, "'" + self.lamp_type + "' is turned OFF.")

            else:

                self.report({"ERROR"}, "No lamp materials yet on scene to change!")

            return {'FINISHED'}


class CgFX:
    """
    Wrapper class for better navigation in file
    """

    '''
    class RecompileCgFX(bpy.types.Operator):
        bl_label = "Recompile CgFX"
        bl_idname = "material.recompile_cgfx"

        def execute(self, context):
            material = context.active_object.active_material
            print("\n=== RECOMPILE REQUEST ======== 0")
            output, vertex_data = cgfx_utils.recompile_cgfx_shader(material)
            cgfx_utils.register_cgfx_ui(material, utils.get_actual_look())
            return {'FINISHED'}


    class RecompileCgFXFileWrite(bpy.types.Operator):
        bl_label = "Recompile CgFX with File Write"
        bl_idname = "material.recompile_cgfx_filewrite"

        def execute(self, context):
            material = context.active_object.active_material
            output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", False, 1)
            cgfx_utils.register_cgfx_ui(material, utils.get_actual_look())
            return {'FINISHED'}
    '''