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

# Copyright (C) 2015-2021: SCS Software

from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.parameters import get_fresnel_window
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.internals.shaders.eut2.window import window_uv_offset_ng
from io_scs_tools.utils import material as _material_utils


class WindowLit(DifSpecAddEnv):
    SEC_UV_MAP = "SecUVMap"
    LIGHTMAP_TEX_NODE = "LightmapTex"
    INTERIOR_RGB_NODE = "InteriorRgb"
    INTERIOR_LIGHT_LUM_NODE = "InteriorLightLuminosity"
    INTERIOR_LIGHT_FINAL_NODE = "InteriorLightFinal"
    FINAL_MIX_NODE = "Final=LitResult+InteriorLight"
    WINDOW_OUT_SHADER_NODE = "WindowOutShader"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        pos_x_shift = 185

        start_pos_x = 0
        start_pos_y = 0

        # init parent
        DifSpecAddEnv.init(node_tree)

        # set fresnel type to schlick
        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Type'].default_value = 1.0

        uv_map_n = node_tree.nodes[DifSpecAddEnv.UVMAP_NODE]
        geom_n = node_tree.nodes[DifSpecAddEnv.GEOM_NODE]
        diff_col_n = node_tree.nodes[DifSpecAddEnv.DIFF_COL_NODE]
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpecAddEnv.OUTPUT_NODE]

        # move existing
        output_n.location.x += pos_x_shift * 2

        # remove existing
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.OPACITY_NODE])

        # create nodes
        uv_recalc_n = node_tree.nodes.new("ShaderNodeGroup")
        uv_recalc_n.name = uv_recalc_n.label = window_uv_offset_ng.WINDOW_UV_OFFSET_G
        uv_recalc_n.location = (start_pos_x, start_pos_y + 1500)
        uv_recalc_n.node_tree = window_uv_offset_ng.get_node_group()

        sec_uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uv_map_n.name = sec_uv_map_n.label = WindowLit.SEC_UV_MAP
        sec_uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1000)
        sec_uv_map_n.uv_map = _MESH_consts.none_uv

        lightmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        lightmap_tex_n.name = lightmap_tex_n.label = WindowLit.LIGHTMAP_TEX_NODE
        lightmap_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        lightmap_tex_n.width = 140

        interior_rgb_n = node_tree.nodes.new("ShaderNodeVectorMath")
        interior_rgb_n.name = interior_rgb_n.label = WindowLit.INTERIOR_RGB_NODE
        interior_rgb_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        interior_rgb_n.operation = "MULTIPLY"

        # TODO: implement decode_window_luminance, for now use direct alpha since Blender yields approximation anyway
        interior_lum_n = node_tree.nodes.new("ShaderNodeVectorMath")
        interior_lum_n.name = interior_lum_n.label = WindowLit.INTERIOR_LIGHT_LUM_NODE
        interior_lum_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1100)
        interior_lum_n.operation = "MULTIPLY"

        interior_light_n = node_tree.nodes.new("ShaderNodeVectorMath")
        interior_light_n.name = interior_light_n.label = WindowLit.INTERIOR_LIGHT_FINAL_NODE
        interior_light_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1200)
        interior_light_n.operation = "MULTIPLY"

        final_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        final_mix_n.name = final_mix_n.label = WindowLit.FINAL_MIX_NODE
        final_mix_n.location = (output_n.location.x - pos_x_shift * 2, output_n.location.y - 200)
        final_mix_n.operation = "ADD"

        out_shader_n = node_tree.nodes.new("ShaderNodeEeveeSpecular")
        out_shader_n.name = out_shader_n.label = WindowLit.WINDOW_OUT_SHADER_NODE
        out_shader_n.location = (output_n.location.x - pos_x_shift * 1, output_n.location.y)
        out_shader_n.inputs["Base Color"].default_value = (0.0,) * 4
        out_shader_n.inputs["Specular"].default_value = (0.0,) * 4

        # create links
        node_tree.links.new(uv_recalc_n.inputs['UV'], uv_map_n.outputs['UV'])
        node_tree.links.new(uv_recalc_n.inputs['Normal'], geom_n.outputs['Normal'])
        node_tree.links.new(uv_recalc_n.inputs['Incoming'], geom_n.outputs['Incoming'])

        node_tree.links.new(base_tex_n.inputs['Vector'], uv_recalc_n.outputs['UV Final'])
        node_tree.links.new(lightmap_tex_n.inputs['Vector'], sec_uv_map_n.outputs['UV'])

        # pass 1
        node_tree.links.new(interior_rgb_n.inputs[0], diff_col_n.outputs['Color'])
        node_tree.links.new(interior_rgb_n.inputs[1], base_tex_n.outputs['Color'])

        node_tree.links.new(interior_lum_n.inputs[0], base_tex_n.outputs['Alpha'])
        node_tree.links.new(interior_lum_n.inputs[1], lightmap_tex_n.outputs['Color'])

        # pass 2
        node_tree.links.new(interior_light_n.inputs[0], interior_rgb_n.outputs[0])
        node_tree.links.new(interior_light_n.inputs[1], interior_lum_n.outputs[0])

        # pass 3
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_col_n.outputs['Color'])

        # pass 4
        node_tree.links.new(final_mix_n.inputs[0], compose_lighting_n.outputs['Color'])
        node_tree.links.new(final_mix_n.inputs[1], interior_light_n.outputs[0])

        # pass 5
        node_tree.links.new(out_shader_n.inputs['Emissive Color'], final_mix_n.outputs[0])

        # output
        node_tree.links.new(output_n.inputs['Surface'], out_shader_n.outputs['BSDF'])

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        bias_scale_window = get_fresnel_window(bias_scale[0], bias_scale[1])

        DifSpecAddEnv.set_fresnel(node_tree, bias_scale_window)

    @staticmethod
    def set_lightmap_texture(node_tree, image):
        """Set lightmap texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to lightmap texture node
        :type image: bpy.types.Image
        """
        node_tree.nodes[WindowLit.LIGHTMAP_TEX_NODE].image = image

    @staticmethod
    def set_lightmap_texture_settings(node_tree, settings):
        """Set lightmap texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[WindowLit.LIGHTMAP_TEX_NODE], settings)

    @staticmethod
    def set_lightmap_uv(node_tree, uv_layer):
        """Set UV layer to lightmap texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for lightmap texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[WindowLit.SEC_UV_MAP].uv_map = uv_layer
