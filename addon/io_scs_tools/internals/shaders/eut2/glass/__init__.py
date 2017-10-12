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

# Copyright (C) 2015: SCS Software


from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.std_node_groups import compose_lighting
from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env
from io_scs_tools.internals.shaders.eut2.std_node_groups import vcolor_input
from io_scs_tools.utils import convert as _convert_utils


class Glass:
    DIFF_COL_NODE = "DiffuseColor"
    SPEC_COL_NODE = "SpecularColor"
    TINT_COL_NODE = "TintColor"
    TINT_OPACITY_NODE = "TintOpacity"
    VCOL_GROUP_NODE = "VColorGroup"
    GEOM_NODE = "Geometry"
    BASE_TEX_NODE = "BaseTex"
    REFL_TEX_NODE = "ReflTex"
    ENV_COLOR_NODE = "EnvFactorColor"
    ADD_ENV_GROUP_NODE = "AddEnvGroup"

    TINT_HSV_NODE = "TintColHSV"
    TINT_OPACITY_COMBINE_NODE = "TintColCombine"
    DIFF_VCOL_MULT_NODE = "DiffVColMultiplier"
    OPACITY_VCOL_MULT_NODE = "DiffVColMultiplier"
    SPEC_MULT_NODE = "SpecMultiplier"

    TINT_SAT_SUBTRACT_NODE = "TintSaturationSubstract"
    TINT_VCOL_MULT_NODE = "TintVColMultiplier"
    DIFF_OPACITY_MULT_NODE = "DiffOpacityMultiplier"

    TINT_VAL_SAT_MULT_NODE = "TintValueSaturationMultiplier"

    TINT_DIFF_MULT_NODE = "TintDiffMultiplier"

    OUT_MAT_NODE = "InputMaterial"
    TINT_VAL_SUBTRACT_NODE = "TintValueSubtract"

    COMPOSE_LIGHTING_NODE = "ComposeLighting"
    OUT_ADD_SPEC_A_NODE = "OutputAddSpecAlpha"
    MAX_TINT_VAL_OR_OPACITY_NODE = "MaxTintValueOpacity"

    OUT_ADD_SPEC_NODE = "OutputAddSpec"
    OUT_ADD_TINT_MAX_A_NODE = "OutputAddTintMaximum"

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
        # vertex colors
        vcol_group_n = node_tree.nodes.new("ShaderNodeGroup")
        vcol_group_n.name = Glass.VCOL_GROUP_NODE
        vcol_group_n.label = Glass.VCOL_GROUP_NODE
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1650)
        vcol_group_n.node_tree = vcolor_input.get_node_group()

        # geometry
        geometry_n = node_tree.nodes.new("ShaderNodeGeometry")
        geometry_n.name = Glass.GEOM_NODE
        geometry_n.label = Glass.GEOM_NODE
        geometry_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        geometry_n.uv_layer = _MESH_consts.none_uv

        # inputs
        refl_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        refl_tex_n.name = Glass.REFL_TEX_NODE
        refl_tex_n.label = Glass.REFL_TEX_NODE
        refl_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2700)

        env_col_n = node_tree.nodes.new("ShaderNodeRGB")
        env_col_n.name = Glass.ENV_COLOR_NODE
        env_col_n.label = Glass.ENV_COLOR_NODE
        env_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2400)

        tint_col_n = node_tree.nodes.new("ShaderNodeRGB")
        tint_col_n.name = Glass.TINT_COL_NODE
        tint_col_n.label = Glass.TINT_COL_NODE
        tint_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)

        tint_opacity_n = node_tree.nodes.new("ShaderNodeValue")
        tint_opacity_n.name = Glass.TINT_OPACITY_NODE
        tint_opacity_n.label = Glass.TINT_OPACITY_NODE
        tint_opacity_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2000)

        spec_col_n = node_tree.nodes.new("ShaderNodeRGB")
        spec_col_n.name = Glass.SPEC_COL_NODE
        spec_col_n.label = Glass.SPEC_COL_NODE
        spec_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1900)

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = Glass.DIFF_COL_NODE
        diff_col_n.label = Glass.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        base_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        base_tex_n.name = Glass.BASE_TEX_NODE
        base_tex_n.label = Glass.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)

        # pass 1
        add_env_gn = node_tree.nodes.new("ShaderNodeGroup")
        add_env_gn.name = Glass.ADD_ENV_GROUP_NODE
        add_env_gn.label = Glass.ADD_ENV_GROUP_NODE
        add_env_gn.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2500)
        add_env_gn.node_tree = add_env.get_node_group()
        add_env_gn.inputs['Apply Fresnel'].default_value = 1.0
        add_env_gn.inputs['Base Texture Alpha'].default_value = 1.0
        add_env_gn.inputs['Fresnel Scale'].default_value = 2.0
        add_env_gn.inputs['Fresnel Bias'].default_value = 1.0

        tint_col_hsv_n = node_tree.nodes.new("ShaderNodeSeparateHSV")
        tint_col_hsv_n.name = Glass.TINT_HSV_NODE
        tint_col_hsv_n.label = Glass.TINT_HSV_NODE
        tint_col_hsv_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2100)

        tint_opacity_combine_n = node_tree.nodes.new("ShaderNodeCombineRGB")
        tint_opacity_combine_n.name = Glass.TINT_OPACITY_COMBINE_NODE
        tint_opacity_combine_n.label = Glass.TINT_OPACITY_COMBINE_NODE
        tint_opacity_combine_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1800)

        diff_vcol_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        diff_vcol_mult_n.name = Glass.DIFF_VCOL_MULT_NODE
        diff_vcol_mult_n.label = Glass.DIFF_VCOL_MULT_NODE
        diff_vcol_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1650)
        diff_vcol_mult_n.blend_type = "MULTIPLY"
        diff_vcol_mult_n.inputs['Fac'].default_value = 1

        spec_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        spec_mult_n.name = Glass.SPEC_MULT_NODE
        spec_mult_n.label = Glass.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1450)
        spec_mult_n.blend_type = "MULTIPLY"
        spec_mult_n.inputs['Fac'].default_value = 1

        # pass 2
        tint_sat_subtract_n = node_tree.nodes.new("ShaderNodeMath")
        tint_sat_subtract_n.name = Glass.TINT_SAT_SUBTRACT_NODE
        tint_sat_subtract_n.label = Glass.TINT_SAT_SUBTRACT_NODE
        tint_sat_subtract_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 2200)
        tint_sat_subtract_n.operation = "SUBTRACT"
        tint_sat_subtract_n.inputs[0].default_value = 1.0

        tint_vcol_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        tint_vcol_mult_n.name = Glass.TINT_VCOL_MULT_NODE
        tint_vcol_mult_n.label = Glass.TINT_VCOL_MULT_NODE
        tint_vcol_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1950)
        tint_vcol_mult_n.blend_type = "MULTIPLY"
        tint_vcol_mult_n.inputs['Fac'].default_value = 1

        diff_opacity_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        diff_opacity_mult_n.name = Glass.DIFF_OPACITY_MULT_NODE
        diff_opacity_mult_n.label = Glass.DIFF_OPACITY_MULT_NODE
        diff_opacity_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1750)
        diff_opacity_mult_n.blend_type = "MULTIPLY"
        diff_opacity_mult_n.inputs['Fac'].default_value = 1

        # pass 3
        tint_val_sat_mult_n = node_tree.nodes.new("ShaderNodeMath")
        tint_val_sat_mult_n.name = Glass.TINT_VAL_SAT_MULT_NODE
        tint_val_sat_mult_n.label = Glass.TINT_VAL_SAT_MULT_NODE
        tint_val_sat_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 2150)
        tint_val_sat_mult_n.operation = "MULTIPLY"

        # pass 4
        tint_diff_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        tint_diff_mult_n.name = Glass.TINT_DIFF_MULT_NODE
        tint_diff_mult_n.label = Glass.TINT_DIFF_MULT_NODE
        tint_diff_mult_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1900)
        tint_diff_mult_n.blend_type = "MULTIPLY"
        tint_diff_mult_n.inputs['Fac'].default_value = 1

        # pass 5
        out_mat_n = node_tree.nodes.new("ShaderNodeExtendedMaterial")
        out_mat_n.name = Glass.OUT_MAT_NODE
        out_mat_n.label = Glass.OUT_MAT_NODE
        if "SpecTra" in out_mat_n:
            out_mat_n.inputs['SpecTra'].default_value = 0.0
        if "Refl" in out_mat_n:
            out_mat_n.inputs['Refl'].default_value = 1.0
        elif "Reflectivity" in out_mat_n:
            out_mat_n.inputs['Reflectivity'].default_value = 1.0
        out_mat_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 2100)

        tint_val_subtract_n = node_tree.nodes.new("ShaderNodeMath")
        tint_val_subtract_n.name = Glass.TINT_VAL_SUBTRACT_NODE
        tint_val_subtract_n.label = Glass.TINT_VAL_SUBTRACT_NODE
        tint_val_subtract_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1400)
        tint_val_subtract_n.operation = "SUBTRACT"
        tint_val_subtract_n.inputs[0].default_value = 1.0

        # pass 6
        compose_lighting_n = node_tree.nodes.new("ShaderNodeGroup")
        compose_lighting_n.name = Glass.COMPOSE_LIGHTING_NODE
        compose_lighting_n.label = Glass.COMPOSE_LIGHTING_NODE
        compose_lighting_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 2400)
        compose_lighting_n.node_tree = compose_lighting.get_node_group()

        out_add_spec_a_n = node_tree.nodes.new("ShaderNodeMath")
        out_add_spec_a_n.name = Glass.OUT_ADD_SPEC_A_NODE
        out_add_spec_a_n.label = Glass.OUT_ADD_SPEC_A_NODE
        out_add_spec_a_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1550)
        out_add_spec_a_n.operation = "ADD"

        max_tint_n = node_tree.nodes.new("ShaderNodeMath")
        max_tint_n.name = Glass.MAX_TINT_VAL_OR_OPACITY_NODE
        max_tint_n.label = Glass.MAX_TINT_VAL_OR_OPACITY_NODE
        max_tint_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1350)
        max_tint_n.operation = "MAXIMUM"

        # pass 7
        out_add_spec_n = node_tree.nodes.new("ShaderNodeMixRGB")
        out_add_spec_n.name = Glass.OUT_ADD_SPEC_NODE
        out_add_spec_n.label = Glass.OUT_ADD_SPEC_NODE
        out_add_spec_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 2200)
        out_add_spec_n.blend_type = "ADD"
        out_add_spec_n.inputs['Fac'].default_value = 1

        out_add_tint_max_a_n = node_tree.nodes.new("ShaderNodeMath")
        out_add_tint_max_a_n.name = Glass.OUT_ADD_TINT_MAX_A_NODE
        out_add_tint_max_a_n.label = Glass.OUT_ADD_TINT_MAX_A_NODE
        out_add_tint_max_a_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 1500)

        # output
        output_n = node_tree.nodes.new("ShaderNodeOutput")
        output_n.name = Glass.OUTPUT_NODE
        output_n.label = Glass.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 11, start_pos_y + 1900)

        # links creation
        # input
        node_tree.links.new(base_tex_n.inputs['Vector'], geometry_n.outputs['UV'])
        node_tree.links.new(refl_tex_n.inputs['Vector'], geometry_n.outputs['Normal'])

        # pass 1
        node_tree.links.new(add_env_gn.inputs['Normal Vector'], geometry_n.outputs['Normal'])
        node_tree.links.new(add_env_gn.inputs['View Vector'], geometry_n.outputs['View'])
        node_tree.links.new(add_env_gn.inputs['Reflection Texture Color'], refl_tex_n.outputs['Color'])
        node_tree.links.new(add_env_gn.inputs['Env Factor Color'], env_col_n.outputs['Color'])
        node_tree.links.new(add_env_gn.inputs['Specular Color'], spec_col_n.outputs['Color'])

        node_tree.links.new(tint_col_hsv_n.inputs['Color'], tint_col_n.outputs['Color'])

        node_tree.links.new(tint_opacity_combine_n.inputs['R'], tint_opacity_n.outputs['Value'])
        node_tree.links.new(tint_opacity_combine_n.inputs['G'], tint_opacity_n.outputs['Value'])
        node_tree.links.new(tint_opacity_combine_n.inputs['B'], tint_opacity_n.outputs['Value'])

        node_tree.links.new(diff_vcol_mult_n.inputs['Color1'], diff_col_n.outputs['Color'])
        node_tree.links.new(diff_vcol_mult_n.inputs['Color2'], vcol_group_n.outputs['Vertex Color'])

        node_tree.links.new(spec_mult_n.inputs['Color1'], spec_col_n.outputs['Color'])
        node_tree.links.new(spec_mult_n.inputs['Color2'], base_tex_n.outputs['Value'])

        # pass 2
        node_tree.links.new(tint_sat_subtract_n.inputs[1], tint_col_hsv_n.outputs['S'])

        node_tree.links.new(tint_vcol_mult_n.inputs['Color1'], tint_col_n.outputs['Color'])
        node_tree.links.new(tint_vcol_mult_n.inputs['Color2'], vcol_group_n.outputs['Vertex Color'])

        node_tree.links.new(diff_opacity_mult_n.inputs['Color1'], tint_opacity_combine_n.outputs['Image'])
        node_tree.links.new(diff_opacity_mult_n.inputs['Color2'], diff_vcol_mult_n.outputs['Color'])

        # pass 3
        node_tree.links.new(tint_val_sat_mult_n.inputs[0], tint_sat_subtract_n.outputs[0])
        node_tree.links.new(tint_val_sat_mult_n.inputs[1], tint_col_hsv_n.outputs['V'])

        # pass 4
        node_tree.links.new(tint_diff_mult_n.inputs['Fac'], tint_val_sat_mult_n.outputs['Value'])
        node_tree.links.new(tint_diff_mult_n.inputs['Color1'], tint_vcol_mult_n.outputs['Color'])
        node_tree.links.new(tint_diff_mult_n.inputs['Color2'], diff_opacity_mult_n.outputs['Color'])

        # pass 5
        node_tree.links.new(out_mat_n.inputs['Spec'], spec_mult_n.outputs['Color'])
        node_tree.links.new(tint_val_subtract_n.inputs[1], vcol_group_n.outputs['Vertex Color Alpha'])

        # pass 6
        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], tint_diff_mult_n.outputs['Color'])
        node_tree.links.new(compose_lighting_n.inputs['Material Color'], tint_diff_mult_n.outputs['Color'])
        node_tree.links.new(compose_lighting_n.inputs['Env Color'], add_env_gn.outputs['Environment Addition Color'])

        node_tree.links.new(out_add_spec_a_n.inputs[0], out_mat_n.outputs['Spec'])
        node_tree.links.new(out_add_spec_a_n.inputs[1], add_env_gn.outputs['Environment Addition Color'])

        node_tree.links.new(max_tint_n.inputs[0], tint_val_subtract_n.outputs[0])
        node_tree.links.new(max_tint_n.inputs[1], tint_opacity_n.outputs[0])

        # pass 7
        node_tree.links.new(out_add_spec_n.inputs['Color1'], compose_lighting_n.outputs['Composed Color'])
        node_tree.links.new(out_add_spec_n.inputs['Color2'], out_mat_n.outputs['Spec'])

        node_tree.links.new(out_add_tint_max_a_n.inputs[0], out_add_spec_a_n.outputs[0])
        node_tree.links.new(out_add_tint_max_a_n.inputs[1], max_tint_n.outputs[0])

        # output
        node_tree.links.new(output_n.inputs['Color'], out_add_spec_n.outputs['Color'])
        node_tree.links.new(output_n.inputs['Alpha'], out_add_tint_max_a_n.outputs[0])

    @staticmethod
    def set_material(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        material.use_transparency = True
        material.transparency_method = "Z_TRANSPARENCY"
        node_tree.nodes[Glass.OUT_MAT_NODE].material = material

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
        node_tree.nodes[Glass.OUT_MAT_NODE].material.diffuse_intensity = 0.7

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
        # fix intensity each time if user might changed it by hand directly on material
        node_tree.nodes[Glass.OUT_MAT_NODE].material.specular_intensity = 1.0

    @staticmethod
    def set_shininess(node_tree, factor):
        """Set shininess factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: shininess factor
        :type factor: float
        """

        node_tree.nodes[Glass.OUT_MAT_NODE].material.specular_hardness = factor

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
    def set_base_texture(node_tree, texture):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to base texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Glass.BASE_TEX_NODE].texture = texture

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

        node_tree.nodes[Glass.GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_reflection_texture(node_tree, texture):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture object which should be used for reflection
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Glass.REFL_TEX_NODE].texture = texture

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
