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

# Copyright (C) 2015-2019: SCS Software

from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.base import BaseShader
from io_scs_tools.internals.shaders.eut2.std_node_groups import compose_lighting_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import lighting_evaluator_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import refl_normal_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import vcolor_input_ng
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import material as _material_utils


class Glass(BaseShader):
    # inputs
    DIFF_COL_NODE = "DiffuseColor"
    SPEC_COL_NODE = "SpecularColor"
    TINT_COL_NODE = "TintColor"
    TINT_OPACITY_NODE = "TintOpacity"
    BASE_TEX_NODE = "BaseTex"
    REFL_NORMAL_NODE = "ReflectionNormal"
    REFL_TEX_NODE = "ReflTex"
    ENV_COLOR_NODE = "EnvFactorColor"

    VCOL_GROUP_NODE = "VColorGroup"
    GEOM_NODE = "Geometry"
    UV_MAP_NODE = "UVMap"

    # pass 1
    VCOL_SCALE_NODE = "DiffVColScale"

    # pass 2
    GLASS_OPACITY_NODE = "GetGlassOpacity"
    GLASS_TINT_NODE = "GetGlassTint"

    # pass 3
    OPAQUE_COLOR_NODE = "OpaqueColor"

    # pass 4
    FINAL_DIFFUSE = "FinalDiffuse"
    FINAL_SPECULAR = "FinalSpecular"

    # pass 5
    ADD_ENV_GROUP_NODE = "AddEnvGroup"

    # pass 6
    LIGHTING_EVAL_NODE = "LightingEvaluator"
    FAKEOPAC_HSV_NODE = "FakeOpacityHSVSeparate"

    # pass 7
    FAKEOPAC_SPEC_MIX_NODE = "FakeOpacitySpecMix"
    FAKEOPAC_ADD_SV_NODE = "FakeOpacityAddSV"

    # pass 8
    FAKEOPAC_SUB_SV_NODE = "FakeOpacitySubSV"
    FAKEOPAC_V_INV_NODE = "FakeOpacityVInvert"

    # pass 9
    FAKEOPAC_ADD_SPEC_MIX_NODE = "FakeOpacityAddSpec"
    FAKEOPAC_MAX_SVV_NODE = "FakeOpacityMaxSVV"

    # pass 10
    FAKEOPAC_MAX_ENV_SV_NODE = "FakeOpacityEnvSV"

    # pass 11
    FAKEOPAC_MAX_FINAL_NODE = "FakeOpacityFinal"

    # pass 12
    COMPOSE_LIGHTING_NODE = "ComposeLighting"

    # pass 13
    OUTPUT_NODE = "Output"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.
        NOTE: this shader can not be fully implemented, because in game this shader works with frame buffer
        which already has color of underlying pixel.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # node creation
        vcol_group_n = node_tree.nodes.new("ShaderNodeGroup")
        vcol_group_n.name = vcol_group_n.label = Glass.VCOL_GROUP_NODE
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1650)
        vcol_group_n.node_tree = vcolor_input_ng.get_node_group()

        geometry_n = node_tree.nodes.new("ShaderNodeNewGeometry")
        geometry_n.name = geometry_n.label = Glass.GEOM_NODE
        geometry_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)

        uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        uv_map_n.name = uv_map_n.label = Glass.UV_MAP_NODE
        uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)
        uv_map_n.uv_map = _MESH_consts.none_uv

        refl_tex_n = node_tree.nodes.new("ShaderNodeTexEnvironment")
        refl_tex_n.name = refl_tex_n.label = Glass.REFL_TEX_NODE
        refl_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2700)
        refl_tex_n.width = 140

        env_col_n = node_tree.nodes.new("ShaderNodeRGB")
        env_col_n.name = env_col_n.label = Glass.ENV_COLOR_NODE
        env_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2400)

        tint_col_n = node_tree.nodes.new("ShaderNodeRGB")
        tint_col_n.name = tint_col_n.label = Glass.TINT_COL_NODE
        tint_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)

        tint_opacity_n = node_tree.nodes.new("ShaderNodeValue")
        tint_opacity_n.name = tint_opacity_n.label = Glass.TINT_OPACITY_NODE
        tint_opacity_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2000)

        spec_col_n = node_tree.nodes.new("ShaderNodeRGB")
        spec_col_n.name = spec_col_n.label = Glass.SPEC_COL_NODE
        spec_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1900)

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = diff_col_n.label = Glass.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        base_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        base_tex_n.name = base_tex_n.label = Glass.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)
        base_tex_n.width = 140

        # pass 0
        refl_norm_n = node_tree.nodes.new("ShaderNodeGroup")
        refl_norm_n.name = refl_norm_n.label = Glass.REFL_NORMAL_NODE
        refl_norm_n.location = (start_pos_x + pos_x_shift * 0, start_pos_y + 2500)
        refl_norm_n.node_tree = refl_normal_ng.get_node_group()

        # pass 1
        vcol_scale_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vcol_scale_n.name = vcol_scale_n.label = Glass.VCOL_SCALE_NODE
        vcol_scale_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1650)
        vcol_scale_n.operation = "MULTIPLY"
        vcol_scale_n.inputs[1].default_value = (2.0,) * 3

        # pass 2
        glass_opacity_n = node_tree.nodes.new("ShaderNodeMath")
        glass_opacity_n.name = glass_opacity_n.label = Glass.GLASS_OPACITY_NODE
        glass_opacity_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1500)
        glass_opacity_n.operation = "MULTIPLY"

        glass_tint_n = node_tree.nodes.new("ShaderNodeVectorMath")
        glass_tint_n.name = glass_tint_n.label = Glass.GLASS_TINT_NODE
        glass_tint_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        glass_tint_n.operation = "MULTIPLY"

        # pass 3
        opaque_col_n = node_tree.nodes.new("ShaderNodeVectorMath")
        opaque_col_n.name = opaque_col_n.label = Glass.OPAQUE_COLOR_NODE
        opaque_col_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1900)
        opaque_col_n.operation = "MULTIPLY"

        # pass 4
        final_diff_n = node_tree.nodes.new("ShaderNodeVectorMath")
        final_diff_n.name = final_diff_n.label = Glass.FINAL_DIFFUSE
        final_diff_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1500)
        final_diff_n.operation = "MULTIPLY"
        final_diff_n.inputs[0].default_value = (1.0,) * 3

        final_spec_n = node_tree.nodes.new("ShaderNodeVectorMath")
        final_spec_n.name = final_spec_n.label = Glass.FINAL_SPECULAR
        final_spec_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1700)
        final_spec_n.operation = "MULTIPLY"

        # pass 5
        lighting_eval_n = node_tree.nodes.new("ShaderNodeGroup")
        lighting_eval_n.name = lighting_eval_n.label = Glass.LIGHTING_EVAL_NODE
        lighting_eval_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1800)
        lighting_eval_n.node_tree = lighting_evaluator_ng.get_node_group()

        fakeopac_hsv_n = node_tree.nodes.new("ShaderNodeSeparateHSV")
        fakeopac_hsv_n.name = fakeopac_hsv_n.label = Glass.FAKEOPAC_HSV_NODE
        fakeopac_hsv_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1500)

        # pass 6
        add_env_n = node_tree.nodes.new("ShaderNodeGroup")
        add_env_n.name = add_env_n.label = Glass.ADD_ENV_GROUP_NODE
        add_env_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 2500)
        add_env_n.node_tree = add_env_ng.get_node_group()
        add_env_n.inputs['Fresnel Scale'].default_value = 2.0
        add_env_n.inputs['Fresnel Bias'].default_value = 1.0
        add_env_n.inputs['Apply Fresnel'].default_value = 1.0
        add_env_n.inputs['Base Texture Alpha'].default_value = 1.0
        add_env_n.inputs['Weighted Color'].default_value = (1.0,) * 4
        add_env_n.inputs['Strength Multiplier'].default_value = 0.5

        fakeopac_spec_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        fakeopac_spec_mix_n.name = fakeopac_spec_mix_n.label = Glass.FAKEOPAC_SPEC_MIX_NODE
        fakeopac_spec_mix_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1900)
        fakeopac_spec_mix_n.operation = "MULTIPLY"

        fakeopac_add_sv_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_add_sv_n.name = fakeopac_add_sv_n.label = Glass.FAKEOPAC_ADD_SV_NODE
        fakeopac_add_sv_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1600)
        fakeopac_add_sv_n.operation = "ADD"

        # pass 7
        fakeopac_sub_sv_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_sub_sv_n.name = fakeopac_sub_sv_n.label = Glass.FAKEOPAC_SUB_SV_NODE
        fakeopac_sub_sv_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1500)
        fakeopac_sub_sv_n.operation = "SUBTRACT"
        fakeopac_sub_sv_n.use_clamp = True

        fakeopac_v_inv_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_v_inv_n.name = fakeopac_v_inv_n.label = Glass.FAKEOPAC_V_INV_NODE
        fakeopac_v_inv_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1300)
        fakeopac_v_inv_n.operation = "SUBTRACT"

        # pass 8
        fakeopac_add_spec_mix_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_add_spec_mix_n.name = fakeopac_add_spec_mix_n.label = Glass.FAKEOPAC_ADD_SPEC_MIX_NODE
        fakeopac_add_spec_mix_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 1800)
        fakeopac_add_spec_mix_n.operation = "ADD"

        fakeopac_max_svv_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_max_svv_n.name = fakeopac_max_svv_n.label = Glass.FAKEOPAC_MAX_SVV_NODE
        fakeopac_max_svv_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 1600)
        fakeopac_max_svv_n.operation = "MAXIMUM"

        # pass 9
        fakeopac_max_env_sv_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_max_env_sv_n.name = fakeopac_max_env_sv_n.label = Glass.FAKEOPAC_MAX_ENV_SV_NODE
        fakeopac_max_env_sv_n.location = (start_pos_x + pos_x_shift * 10, start_pos_y + 1700)
        fakeopac_max_env_sv_n.operation = "MAXIMUM"

        # pass 10
        fakeopac_max_final_n = node_tree.nodes.new("ShaderNodeMath")
        fakeopac_max_final_n.name = fakeopac_max_final_n.label = Glass.FAKEOPAC_MAX_FINAL_NODE
        fakeopac_max_final_n.location = (start_pos_x + pos_x_shift * 11, start_pos_y + 1500)
        fakeopac_max_final_n.operation = "MAXIMUM"

        # pass 11
        compose_lighting_n = node_tree.nodes.new("ShaderNodeGroup")
        compose_lighting_n.name = compose_lighting_n.label = Glass.COMPOSE_LIGHTING_NODE
        compose_lighting_n.location = (start_pos_x + pos_x_shift * 12, start_pos_y + 2000)
        compose_lighting_n.node_tree = compose_lighting_ng.get_node_group()
        compose_lighting_n.inputs['Alpha'].default_value = 1.0

        # output
        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = Glass.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 13, start_pos_y + 1800)

        # links creation
        # inputs
        node_tree.links.new(base_tex_n.inputs['Vector'], uv_map_n.outputs['UV'])
        node_tree.links.new(refl_tex_n.inputs['Vector'], refl_norm_n.outputs['Reflection Normal'])

        # pass 0
        node_tree.links.new(refl_norm_n.inputs['Incoming'], geometry_n.outputs['Incoming'])
        node_tree.links.new(refl_norm_n.inputs['Normal'], lighting_eval_n.outputs['Normal'])

        # pass 1
        node_tree.links.new(vcol_scale_n.inputs[0], vcol_group_n.outputs['Vertex Color'])

        # pass 2
        node_tree.links.new(glass_opacity_n.inputs[0], tint_opacity_n.outputs[0])
        node_tree.links.new(glass_opacity_n.inputs[1], vcol_group_n.outputs['Vertex Color Alpha'])

        node_tree.links.new(glass_tint_n.inputs[0], tint_col_n.outputs['Color'])
        node_tree.links.new(glass_tint_n.inputs[1], vcol_scale_n.outputs[0])

        # pass 3
        node_tree.links.new(opaque_col_n.inputs[0], diff_col_n.outputs['Color'])
        node_tree.links.new(opaque_col_n.inputs[1], glass_tint_n.outputs[0])

        # pass 4
        # node_tree.links.new(final_diff_n.inputs[0], glass_opacity_n.outputs[0])
        node_tree.links.new(final_diff_n.inputs[1], opaque_col_n.outputs[0])

        node_tree.links.new(final_spec_n.inputs[0], spec_col_n.outputs['Color'])
        node_tree.links.new(final_spec_n.inputs[1], base_tex_n.outputs['Alpha'])

        # pass 5
        node_tree.links.new(lighting_eval_n.inputs['Normal Vector'], geometry_n.outputs['Normal'])
        node_tree.links.new(lighting_eval_n.inputs['Incoming Vector'], geometry_n.outputs['Incoming'])

        node_tree.links.new(fakeopac_hsv_n.inputs['Color'], glass_tint_n.outputs[0])

        # pass 6
        node_tree.links.new(add_env_n.inputs['Normal Vector'], lighting_eval_n.outputs['Normal'])
        node_tree.links.new(add_env_n.inputs['Reflection Normal Vector'], refl_norm_n.outputs['Reflection Normal'])
        node_tree.links.new(add_env_n.inputs['Reflection Texture Color'], refl_tex_n.outputs['Color'])
        node_tree.links.new(add_env_n.inputs['Env Factor Color'], env_col_n.outputs['Color'])
        node_tree.links.new(add_env_n.inputs['Specular Color'], spec_col_n.outputs['Color'])

        node_tree.links.new(fakeopac_spec_mix_n.inputs[0], final_spec_n.outputs[0])
        node_tree.links.new(fakeopac_spec_mix_n.inputs[1], lighting_eval_n.outputs['Specular Lighting'])

        node_tree.links.new(fakeopac_add_sv_n.inputs[0], fakeopac_hsv_n.outputs['S'])
        node_tree.links.new(fakeopac_add_sv_n.inputs[1], fakeopac_hsv_n.outputs['V'])

        # pass 7
        node_tree.links.new(fakeopac_sub_sv_n.inputs[0], fakeopac_add_sv_n.outputs['Value'])
        node_tree.links.new(fakeopac_sub_sv_n.inputs[1], fakeopac_hsv_n.outputs['V'])

        node_tree.links.new(fakeopac_v_inv_n.inputs[1], fakeopac_hsv_n.outputs['V'])

        # pass 8
        node_tree.links.new(fakeopac_add_spec_mix_n.inputs[0], add_env_n.outputs['Environment Addition Color'])
        node_tree.links.new(fakeopac_add_spec_mix_n.inputs[1], fakeopac_spec_mix_n.outputs[0])

        node_tree.links.new(fakeopac_max_svv_n.inputs[0], fakeopac_sub_sv_n.outputs['Value'])
        node_tree.links.new(fakeopac_max_svv_n.inputs[1], fakeopac_v_inv_n.outputs['Value'])

        # pass 9
        node_tree.links.new(fakeopac_max_env_sv_n.inputs[0], fakeopac_add_spec_mix_n.outputs['Value'])
        node_tree.links.new(fakeopac_max_env_sv_n.inputs[1], fakeopac_max_svv_n.outputs['Value'])

        # pass 10
        node_tree.links.new(fakeopac_max_final_n.inputs[0], fakeopac_max_env_sv_n.outputs['Value'])
        node_tree.links.new(fakeopac_max_final_n.inputs[1], glass_opacity_n.outputs['Value'])

        # pass 11
        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], final_diff_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], final_spec_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs['Env Color'], add_env_n.outputs['Environment Addition Color'])
        node_tree.links.new(compose_lighting_n.inputs['Diffuse Lighting'], lighting_eval_n.outputs['Diffuse Lighting'])
        node_tree.links.new(compose_lighting_n.inputs['Specular Lighting'], lighting_eval_n.outputs['Specular Lighting'])
        node_tree.links.new(compose_lighting_n.inputs['Alpha'], fakeopac_max_final_n.outputs['Value'])

        # output
        node_tree.links.new(output_n.inputs['Surface'], compose_lighting_n.outputs['Shader'])

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

    @staticmethod
    def set_add_ambient(node_tree, factor):
        """Set ambient factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: add ambient factor
        :type factor: float
        """

        node_tree.nodes[Glass.COMPOSE_LIGHTING_NODE].inputs["AddAmbient"].default_value = factor

    @staticmethod
    def set_diffuse(node_tree, color):
        """Set diffuse color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: diffuse color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Glass.DIFF_COL_NODE].outputs['Color'].default_value = color

    @staticmethod
    def set_specular(node_tree, color):
        """Set specular color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: specular color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Glass.SPEC_COL_NODE].outputs['Color'].default_value = color

    @staticmethod
    def set_shininess(node_tree, factor):
        """Set shininess factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: shininess factor
        :type factor: float
        """

        node_tree.nodes[Glass.LIGHTING_EVAL_NODE].inputs['Shininess'].default_value = factor

    @staticmethod
    def set_reflection(node_tree, value):
        """Set reflection factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: reflection factor
        :type value: float
        """

        pass  # NOTE: reflection attribute doesn't change anything in rendered material, so pass it

    @staticmethod
    def set_base_texture(node_tree, image):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to base texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Glass.BASE_TEX_NODE].image = image

    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Glass.BASE_TEX_NODE], settings)

    @staticmethod
    def set_base_uv(node_tree, uv_layer):
        """Set UV layer to base texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Glass.UV_MAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_reflection_texture(node_tree, image):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image object which should be used for reflection
        :type image: bpy.types.Image
        """

        node_tree.nodes[Glass.REFL_TEX_NODE].image = image

    @staticmethod
    def set_reflection_texture_settings(node_tree, settings):
        """Set reflection texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        pass  # reflection texture shouldn't use any custom settings

    @staticmethod
    def set_env_factor(node_tree, color):
        """Set environment factor color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: environment color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Glass.ENV_COLOR_NODE].outputs[0].default_value = color

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        node_tree.nodes[Glass.ADD_ENV_GROUP_NODE].inputs['Fresnel Bias'].default_value = bias_scale[0]
        node_tree.nodes[Glass.ADD_ENV_GROUP_NODE].inputs['Fresnel Scale'].default_value = bias_scale[1]

    @staticmethod
    def set_tint_opacity(node_tree, opacity):
        """Set tint opacity to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param opacity: tint opacity as float
        :type opacity: float
        """

        node_tree.nodes[Glass.TINT_OPACITY_NODE].outputs[0].default_value = opacity

    @staticmethod
    def set_tint(node_tree, color):
        """Set tint color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: tint color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Glass.TINT_COL_NODE].outputs[0].default_value = color
