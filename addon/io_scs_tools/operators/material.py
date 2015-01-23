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


class CustomMapping:
    class AddCustomMapping(bpy.types.Operator):
        bl_label = "Add Custom TexCoord Mapping"
        bl_idname = "material.add_custom_tex_coord_map"
        bl_description = "Add custom TexCoord mapping to list"

        def execute(self, context):
            material = context.active_object.active_material

            if material:
                item = material.scs_props.shader_custom_tex_coord_maps.add()
                item.name = "text_coord_x"

            return {'FINISHED'}

    class RemoveCustomMapping(bpy.types.Operator):
        bl_label = "Remove Custom TexCoord Mapping"
        bl_idname = "material.remove_custom_tex_coord_map"
        bl_description = "Remove selected custom TexCoord mapping from list"

        def execute(self, context):
            material = context.active_object.active_material

            if material:

                material.scs_props.shader_custom_tex_coord_maps.remove(material.scs_props.active_custom_tex_coord)

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