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

# Copyright (C) 2015-2022: SCS Software

from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.base import BaseShader
from io_scs_tools.internals.shaders.flavors import sky_back, sky_stars
from io_scs_tools.internals.shaders.eut2.std_node_groups import vcolor_input_ng
from io_scs_tools.internals.shaders.eut2.sky import texture_types
from io_scs_tools.internals.shaders.eut2.sky import uv_rescale_ng
from io_scs_tools.internals.shaders.std_node_groups import output_shader_ng
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import math as _math_utils


class Sky(BaseShader):
    VCOL_GROUP_NODE = "VColorGroup"
    UV_MAP_NODE = "UVMap"
    RESCALE_UV_GROUP_NODE = "RescaleUV"
    DIFF_COL_NODE = "DiffuseColor"
    VCOLOR_MULT_NODE = "VertexColorMultiplier"
    DIFF_MULT_NODE = "DiffuseMultiplier"
    WEATHER_BASE_MIX_NODE = "WeatherBaseMix"
    WEATHER_BASE_A_MIX_NODE = "WeatherBaseAMix"
    WEATHER_OVER_MIX_NODE = "WeatherOverMix"
    WEATHER_OVER_A_MIX_NODE = "WeatherOverAMix"
    WEATHER_MIX_NODE = "WeatherMix"
    WEATHER_A_MIX_NODE = "WeatherAMix"
    WEATHER_DIFF_MULT_NODE = "WeatherDiffMult"
    OPACITY_STARS_MIX_NODE = "OpacityStarsMix"

    OUT_SHADER_NODE = "OutShader"
    OUTPUT_NODE = "Output"

    SEPARATE_UV_NODE_PREFIX = "Separate UV "
    TEX_NODE_PREFIX = "Tex "
    TEX_OOB_BOOL_NODE_PREFIX = "OOBBool "
    TEX_FINAL_MIX_NODE_PREFIX = "FinalTexel "
    TEX_FINAL_A_MIX_NODE_PREFIX = "FinalTexelA "

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

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # node creation
        vcol_group_n = node_tree.nodes.new("ShaderNodeGroup")
        vcol_group_n.name = vcol_group_n.label = Sky.VCOL_GROUP_NODE
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1800)
        vcol_group_n.node_tree = vcolor_input_ng.get_node_group()

        uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        uv_map_n.name = uv_map_n.label = Sky.UV_MAP_NODE
        uv_map_n.location = (start_pos_x - pos_x_shift * 2, start_pos_y + 1500)
        uv_map_n.uv_map = _MESH_consts.none_uv

        uv_rescale_n = node_tree.nodes.new("ShaderNodeGroup")
        uv_rescale_n.name = uv_rescale_n.label = Sky.RESCALE_UV_GROUP_NODE
        uv_rescale_n.location = (start_pos_x - pos_x_shift * 1, start_pos_y + 1500)
        uv_rescale_n.node_tree = uv_rescale_ng.get_node_group()
        uv_rescale_n.inputs['Rescale Enabled'].default_value = 0

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = diff_col_n.label = Sky.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2000)

        for tex_type_i, tex_type in enumerate(texture_types.get()):
            Sky.__create_texel_component_nodes__(node_tree, tex_type, (start_pos_x + pos_x_shift, start_pos_y + 1500 - tex_type_i * 450))

        base_a_tex_final_n = node_tree.nodes[Sky.TEX_FINAL_MIX_NODE_PREFIX + texture_types.get()[0]]
        base_b_tex_final_n = node_tree.nodes[Sky.TEX_FINAL_MIX_NODE_PREFIX + texture_types.get()[1]]
        over_a_tex_final_n = node_tree.nodes[Sky.TEX_FINAL_MIX_NODE_PREFIX + texture_types.get()[2]]
        over_b_tex_final_n = node_tree.nodes[Sky.TEX_FINAL_MIX_NODE_PREFIX + texture_types.get()[3]]

        base_a_tex_final_alpha_n = node_tree.nodes[Sky.TEX_FINAL_A_MIX_NODE_PREFIX + texture_types.get()[0]]
        base_b_tex_final_alpha_n = node_tree.nodes[Sky.TEX_FINAL_A_MIX_NODE_PREFIX + texture_types.get()[1]]
        over_a_tex_final_alpha_n = node_tree.nodes[Sky.TEX_FINAL_A_MIX_NODE_PREFIX + texture_types.get()[2]]
        over_b_tex_final_alpha_n = node_tree.nodes[Sky.TEX_FINAL_A_MIX_NODE_PREFIX + texture_types.get()[3]]

        vcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vcol_mult_n.name = vcol_mult_n.label = Sky.VCOLOR_MULT_NODE
        vcol_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        vcol_mult_n.operation = "MULTIPLY"
        vcol_mult_n.inputs[1].default_value = (2,) * 3

        diff_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        diff_mult_n.name = diff_mult_n.label = Sky.DIFF_MULT_NODE
        diff_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 2000)
        diff_mult_n.operation = "MULTIPLY"

        weather_base_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_base_mix_n.name = weather_base_mix_n.label = Sky.WEATHER_BASE_MIX_NODE
        weather_base_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1500)
        weather_base_mix_n.blend_type = "MIX"

        weather_base_alpha_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_base_alpha_mix_n.name = weather_base_alpha_mix_n.label = Sky.WEATHER_BASE_A_MIX_NODE
        weather_base_alpha_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1300)
        weather_base_alpha_mix_n.blend_type = "MIX"

        weather_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_over_mix_n.name = weather_over_mix_n.label = Sky.WEATHER_OVER_MIX_NODE
        weather_over_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 700)
        weather_over_mix_n.blend_type = "MIX"

        weather_over_alpha_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_over_alpha_mix_n.name = weather_over_alpha_mix_n.label = Sky.WEATHER_OVER_A_MIX_NODE
        weather_over_alpha_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 500)
        weather_over_alpha_mix_n.blend_type = "MIX"

        weather_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_mix_n.name = weather_mix_n.label = Sky.WEATHER_MIX_NODE
        weather_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1100)
        weather_mix_n.blend_type = "MIX"

        weather_alpha_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        weather_alpha_mix_n.name = weather_alpha_mix_n.label = Sky.WEATHER_A_MIX_NODE
        weather_alpha_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 900)
        weather_alpha_mix_n.blend_type = "MIX"

        weather_diff_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        weather_diff_mult_n.name = weather_diff_mult_n.label = Sky.WEATHER_DIFF_MULT_NODE
        weather_diff_mult_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1500)
        weather_diff_mult_n.operation = "MULTIPLY"

        opacity_stars_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        opacity_stars_mix_n.name = opacity_stars_mix_n.label = Sky.OPACITY_STARS_MIX_NODE
        opacity_stars_mix_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 900)
        opacity_stars_mix_n.operation = "MULTIPLY"
        opacity_stars_mix_n.inputs[1].default_value = (1.0,) * 3

        out_shader_node = node_tree.nodes.new("ShaderNodeGroup")
        out_shader_node.name = out_shader_node.label = Sky.OUT_SHADER_NODE
        out_shader_node.location = (start_pos_x + pos_x_shift * 8, 1500)
        out_shader_node.node_tree = output_shader_ng.get_node_group()

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = Sky.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 9, start_pos_y + 1500)

        # links creation
        # pass 1
        node_tree.links.new(uv_rescale_n.inputs['UV'], uv_map_n.outputs['UV'])

        # pass 1, 2, 3
        for tex_type in texture_types.get():
            Sky.__create_texel_component_links__(node_tree, tex_type, node_tree.nodes[Sky.RESCALE_UV_GROUP_NODE].outputs['UV ' + tex_type])

        # pass 3
        node_tree.links.new(vcol_mult_n.inputs[0], vcol_group_n.outputs['Vertex Color'])

        # pass 4
        node_tree.links.new(diff_mult_n.inputs[0], diff_col_n.outputs[0])
        node_tree.links.new(diff_mult_n.inputs[1], vcol_mult_n.outputs[0])

        node_tree.links.new(weather_base_mix_n.inputs['Color1'], base_a_tex_final_n.outputs[0])
        node_tree.links.new(weather_base_mix_n.inputs['Color2'], base_b_tex_final_n.outputs[0])

        node_tree.links.new(weather_base_alpha_mix_n.inputs['Color1'], base_a_tex_final_alpha_n.outputs[0])
        node_tree.links.new(weather_base_alpha_mix_n.inputs['Color2'], base_b_tex_final_alpha_n.outputs[0])

        node_tree.links.new(weather_over_mix_n.inputs['Color1'], over_a_tex_final_n.outputs[0])
        node_tree.links.new(weather_over_mix_n.inputs['Color2'], over_b_tex_final_n.outputs[0])

        node_tree.links.new(weather_over_alpha_mix_n.inputs['Color1'], over_a_tex_final_alpha_n.outputs[0])
        node_tree.links.new(weather_over_alpha_mix_n.inputs['Color2'], over_b_tex_final_alpha_n.outputs[0])

        # pass 5
        node_tree.links.new(weather_mix_n.inputs['Color1'], weather_base_mix_n.outputs[0])
        node_tree.links.new(weather_mix_n.inputs['Color2'], weather_over_mix_n.outputs[0])

        node_tree.links.new(weather_alpha_mix_n.inputs['Color1'], weather_base_alpha_mix_n.outputs[0])
        node_tree.links.new(weather_alpha_mix_n.inputs['Color2'], weather_over_alpha_mix_n.outputs[0])

        # pass 6
        node_tree.links.new(weather_diff_mult_n.inputs[0], diff_mult_n.outputs[0])
        node_tree.links.new(weather_diff_mult_n.inputs[1], weather_mix_n.outputs[0])

        node_tree.links.new(opacity_stars_mix_n.inputs[0], weather_alpha_mix_n.outputs[0])

        # pass 7
        node_tree.links.new(out_shader_node.inputs['Color'], weather_diff_mult_n.outputs[0])
        node_tree.links.new(out_shader_node.inputs['Alpha'], opacity_stars_mix_n.outputs[0])

        # output pass
        node_tree.links.new(output_n.inputs['Surface'], out_shader_node.outputs['Shader'])

    @staticmethod
    def __create_texel_component_nodes__(node_tree, tex_type, location):
        """Create one texel component nodes.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param tex_type: texture type of the component
        :type tex_type: str
        :param location: location of top left node
        :type location: (int, int)
        """

        pos_x_shift = 185

        separate_uv_n = node_tree.nodes.new("ShaderNodeSeparateXYZ")
        separate_uv_n.name = separate_uv_n.label = Sky.SEPARATE_UV_NODE_PREFIX + tex_type
        separate_uv_n.location = (location[0], location[1] + 150)

        texel_obb_n = node_tree.nodes.new("ShaderNodeMath")
        texel_obb_n.name = texel_obb_n.label = Sky.TEX_OOB_BOOL_NODE_PREFIX + tex_type
        texel_obb_n.location = (location[0] + pos_x_shift, location[1] + 150)
        texel_obb_n.operation = "LESS_THAN"

        tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        tex_n.name = tex_n.label = Sky.TEX_NODE_PREFIX + tex_type
        tex_n.location = (location[0], location[1])
        tex_n.width = 140

        mix_col_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mix_col_n.name = mix_col_n.label = Sky.TEX_FINAL_MIX_NODE_PREFIX + tex_type
        mix_col_n.location = (location[0] + pos_x_shift * 2, location[1] + 100)
        mix_col_n.blend_type = "MIX"
        mix_col_n.inputs['Color2'].default_value = (0.0,) * 4

        mix_a_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mix_a_n.name = mix_a_n.label = Sky.TEX_FINAL_A_MIX_NODE_PREFIX + tex_type
        mix_a_n.location = (location[0] + pos_x_shift * 2, location[1] - 100)
        mix_a_n.blend_type = "MIX"
        mix_a_n.inputs['Color2'].default_value = (0.0,) * 4

    @staticmethod
    def __create_texel_component_links__(node_tree, tex_type, uv_socket):
        """Creates links for texel components.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param tex_type: texture type of the component
        :type tex_type: str
        :param uv_socket: UVs of the texture type
        :type uv_socket: bpy.types.NodeSocketVector
        """

        separate_uv_n = node_tree.nodes[Sky.SEPARATE_UV_NODE_PREFIX + tex_type]
        texel_obb_n = node_tree.nodes[Sky.TEX_OOB_BOOL_NODE_PREFIX + tex_type]
        tex_n = node_tree.nodes[Sky.TEX_NODE_PREFIX + tex_type]
        mix_col_n = node_tree.nodes[Sky.TEX_FINAL_MIX_NODE_PREFIX + tex_type]
        mix_a_n = node_tree.nodes[Sky.TEX_FINAL_A_MIX_NODE_PREFIX + tex_type]

        node_tree.links.new(separate_uv_n.inputs[0], uv_socket)

        node_tree.links.new(texel_obb_n.inputs[0], separate_uv_n.outputs['Y'])
        node_tree.links.new(tex_n.inputs[0], uv_socket)

        node_tree.links.new(mix_col_n.inputs['Fac'], texel_obb_n.outputs[0])
        node_tree.links.new(mix_col_n.inputs['Color1'], tex_n.outputs['Color'])
        node_tree.links.new(mix_a_n.inputs['Fac'], texel_obb_n.outputs[0])
        node_tree.links.new(mix_a_n.inputs['Color1'], tex_n.outputs['Alpha'])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        material.use_backface_culling = True
        material.blend_method = "BLEND"

        if sky_stars.is_set(node_tree):
            material.blend_method = "BLEND"
        if sky_back.is_set(node_tree):
            material.blend_method = "OPAQUE"

        if material.blend_method == "OPAQUE" and node_tree.nodes[Sky.OUT_SHADER_NODE].inputs['Alpha'].links:
            node_tree.links.remove(node_tree.nodes[Sky.OUT_SHADER_NODE].inputs['Alpha'].links[0])

    @staticmethod
    def set_diffuse(node_tree, color):
        """Set diffuse color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: diffuse color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Sky.DIFF_COL_NODE].outputs['Color'].default_value = color

    @staticmethod
    def set_sky_weather_base_a_texture(node_tree, image):
        """Set base_a texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_base_a()].image = image

    @staticmethod
    def set_sky_weather_base_a_texture_settings(node_tree, settings):
        """Set base_a texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_base_a()], settings)

    @staticmethod
    def set_sky_weather_base_a_uv(node_tree, uv_layer):
        """Set UV layer to base_a texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base_a texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Sky.UV_MAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_sky_weather_base_b_texture(node_tree, image):
        """Set base_b texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_base_b()].image = image

    @staticmethod
    def set_sky_weather_base_b_texture_settings(node_tree, settings):
        """Set base_b texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_base_b()], settings)

    @staticmethod
    def set_sky_weather_base_b_uv(node_tree, uv_layer):
        """Set UV layer to base_b texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base_b texture
        :type uv_layer: str
        """

        Sky.set_sky_weather_base_a_uv(node_tree, uv_layer)

    @staticmethod
    def set_sky_weather_over_a_texture(node_tree, image):
        """Set over_a texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_over_a()].image = image

    @staticmethod
    def set_sky_weather_over_a_texture_settings(node_tree, settings):
        """Set over_a texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_over_a()], settings)

    @staticmethod
    def set_sky_weather_over_a_uv(node_tree, uv_layer):
        """Set UV layer to over_a texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over_a texture
        :type uv_layer: str
        """

        Sky.set_sky_weather_base_a_uv(node_tree, uv_layer)

    @staticmethod
    def set_sky_weather_over_b_texture(node_tree, image):
        """Set over_b texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_over_b()].image = image

    @staticmethod
    def set_sky_weather_over_b_texture_settings(node_tree, settings):
        """Set over_b texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Sky.TEX_NODE_PREFIX + texture_types.get_over_b()], settings)

    @staticmethod
    def set_sky_weather_over_b_uv(node_tree, uv_layer):
        """Set UV layer to over_b texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over_b texture
        :type uv_layer: str
        """

        Sky.set_sky_weather_base_a_uv(node_tree, uv_layer)

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set blend factors.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: layer blend factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        profile_blend = _math_utils.clamp(aux_property[0]['value'])

        node_tree.nodes[Sky.WEATHER_BASE_MIX_NODE].inputs['Fac'].default_value = profile_blend
        node_tree.nodes[Sky.WEATHER_BASE_A_MIX_NODE].inputs['Fac'].default_value = profile_blend
        node_tree.nodes[Sky.WEATHER_OVER_MIX_NODE].inputs['Fac'].default_value = profile_blend
        node_tree.nodes[Sky.WEATHER_OVER_A_MIX_NODE].inputs['Fac'].default_value = profile_blend

        weather_blend = _math_utils.clamp(aux_property[1]['value'])

        node_tree.nodes[Sky.WEATHER_MIX_NODE].inputs['Fac'].default_value = weather_blend
        node_tree.nodes[Sky.WEATHER_A_MIX_NODE].inputs['Fac'].default_value = weather_blend

        if sky_stars.is_set(node_tree):
            stars_opacity = (_math_utils.clamp(aux_property[2]['value']),) * 3
        else:
            stars_opacity = (1.0,) * 3

        node_tree.nodes[Sky.OPACITY_STARS_MIX_NODE].inputs[1].default_value = stars_opacity

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set v cutoff factors.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: layer blend factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        for tex_type_i, tex_type in enumerate(texture_types.get()):

            if (not sky_stars.is_set(node_tree)) and (not sky_back.is_set(node_tree)):  # enabled
                v_cutoff = aux_property[tex_type_i]['value']
            else:  # disabled
                v_cutoff = float("-inf")

            node_tree.nodes[Sky.TEX_OOB_BOOL_NODE_PREFIX + tex_type].inputs[1].default_value = v_cutoff

    @staticmethod
    def set_aux2(node_tree, aux_property):
        """Set v scale factors.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: layer blend factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        for tex_type_i, tex_type in enumerate(texture_types.get()):
            node_tree.nodes[Sky.RESCALE_UV_GROUP_NODE].inputs['V Scale ' + tex_type].default_value = aux_property[tex_type_i]['value']

        if sky_stars.is_set(node_tree):
            rescale_enabled = 1.0
        else:
            rescale_enabled = 0.0
        node_tree.nodes[Sky.RESCALE_UV_GROUP_NODE].inputs['Rescale Enabled'].default_value = rescale_enabled

    @staticmethod
    def set_sky_stars_flavor(node_tree, switch_on):
        """Set sky stars flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if it should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            sky_stars.init(node_tree)
        else:
            sky_stars.delete(node_tree)

    @staticmethod
    def set_sky_back_flavor(node_tree, switch_on):
        """Set sky back flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if it should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            sky_back.init(node_tree)
        else:
            sky_back.delete(node_tree)
