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
from io_scs_tools.internals.shaders.eut2.parameters import get_fresnel_truckpaint
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


class Truckpaint(DifSpecAddEnv):
    PAINT_UV_MAP_NODE = "PaintUVMap"

    PAINT_TEX_NODE = "PaintTex"
    PAINT_BASE_COL_NODE = "PaintjobBaseCol"
    PAINT_B_COL_NODE = "PaintjobBCol"
    PAINT_G_COL_NODE = "PaintjobGCol"
    PAINT_R_COL_NODE = "PaintjobRCol"

    PAINT_TEX_SEP_NODE = "PaintTexSeparate"

    ENV_VCOL_MULT_NODE = "EnvFactorVColorMultiplier"
    SPEC_VCOL_MULT_NODE = "SpecVColorMultiplier"
    OPACITY_VCOL_MULT_NODE = "OpacityVColorMultplier"
    AIRBRUSH_MIX_NODE = "AirbrushMixer"
    COL_MASK_B_MIX_NODE = "ColormaskBCol"
    COL_MASK_G_MIX_NODE = "ColormaskGCol"
    COL_MASK_R_MIX_NODE = "ColormaskRCol"

    BASE_PAINT_MULT_NODE = "BasePaintMult"

    BLEND_MIX_NODE = "BlendMode"

    PAINT_DIFFUSE_MULT_NODE = "PaintDiffuseMultiplier"
    PAINT_SPECULAR_MULT_NODE = "PaintSpecularMultiplier"

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

        # init parent
        DifSpecAddEnv.init(node_tree)

        # set fresnel type to schlick
        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Type'].default_value = 1.0

        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        env_color_n = node_tree.nodes[DifSpecAddEnv.ENV_COLOR_NODE]
        spec_color_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        diff_mult_n = node_tree.nodes[DifSpecAddEnv.DIFF_MULT_NODE]
        add_refl_gn = node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE]
        spec_mult_n = node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpecAddEnv.VCOLOR_SCALE_NODE]
        opacity_n = node_tree.nodes[DifSpecAddEnv.OPACITY_NODE]
        lighting_eval_n = node_tree.nodes[DifSpecAddEnv.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpecAddEnv.OUTPUT_NODE]

        # move existing
        add_refl_gn.location.x += pos_x_shift * 3
        spec_mult_n.location.x += pos_x_shift * 3
        lighting_eval_n.location.x += pos_x_shift
        compose_lighting_n.location.x += pos_x_shift * 2
        output_n.location.x += pos_x_shift * 2

        # set fresnel factor to 1
        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Apply Fresnel'].default_value = 1.0

        # node creation - level 3
        env_vcol_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        env_vcol_mix_n.name = env_vcol_mix_n.label = Truckpaint.ENV_VCOL_MULT_NODE
        env_vcol_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 2000)
        env_vcol_mix_n.operation = "MULTIPLY"

        spec_vcol_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_vcol_mix_n.name = spec_vcol_mix_n.label = Truckpaint.SPEC_VCOL_MULT_NODE
        spec_vcol_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1750)
        spec_vcol_mix_n.operation = "MULTIPLY"

        opacity_vcol_n = node_tree.nodes.new("ShaderNodeMath")
        opacity_vcol_n.name = opacity_vcol_n.label = Truckpaint.OPACITY_VCOL_MULT_NODE
        opacity_vcol_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1300)
        opacity_vcol_n.operation = "MULTIPLY"

        # node creation - level 4
        paint_spec_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        paint_spec_mult_n.name = paint_spec_mult_n.label = Truckpaint.PAINT_SPECULAR_MULT_NODE
        paint_spec_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1950)
        paint_spec_mult_n.blend_type = "MULTIPLY"
        paint_spec_mult_n.inputs['Fac'].default_value = 0

        # node creation - level 5
        base_paint_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_paint_mult_n.name = base_paint_mult_n.label = Truckpaint.BASE_PAINT_MULT_NODE
        base_paint_mult_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1500)
        base_paint_mult_n.blend_type = "MULTIPLY"
        base_paint_mult_n.inputs['Fac'].default_value = 1
        base_paint_mult_n.inputs['Color2'].default_value = _convert_utils.to_node_color(_get_scs_globals().base_paint_color)

        # node creation - level 6
        paint_diff_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        paint_diff_mult_n.name = paint_diff_mult_n.label = Truckpaint.PAINT_DIFFUSE_MULT_NODE
        paint_diff_mult_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1400)
        paint_diff_mult_n.blend_type = "MULTIPLY"
        paint_diff_mult_n.inputs['Fac'].default_value = 0

        # make links - level 2
        node_tree.links.new(env_vcol_mix_n.inputs[0], env_color_n.outputs['Color'])
        node_tree.links.new(env_vcol_mix_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(spec_vcol_mix_n.inputs[0], base_tex_n.outputs['Alpha'])
        node_tree.links.new(spec_vcol_mix_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(opacity_vcol_n.inputs[0], vcol_scale_n.outputs[0])
        node_tree.links.new(opacity_vcol_n.inputs[1], opacity_n.outputs[0])

        # make links - level 3
        node_tree.links.new(paint_spec_mult_n.inputs['Color1'], spec_color_n.outputs['Color'])

        # make links - level 4
        node_tree.links.new(spec_mult_n.inputs[0], paint_spec_mult_n.outputs['Color'])
        node_tree.links.new(spec_mult_n.inputs[1], spec_vcol_mix_n.outputs[0])

        node_tree.links.new(base_paint_mult_n.inputs['Color1'], diff_mult_n.outputs[0])

        # make links - level 5
        node_tree.links.new(add_refl_gn.inputs['Env Factor Color'], env_vcol_mix_n.outputs[0])
        node_tree.links.new(add_refl_gn.inputs['Specular Color'], paint_spec_mult_n.outputs['Color'])

        node_tree.links.new(paint_diff_mult_n.inputs['Color1'], base_paint_mult_n.outputs['Color'])

        # make links - output
        # node_tree.links.new(compose_lighting_n.inputs['Specular Color'], paint_spec_mult_n.outputs['Color'])
        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], paint_diff_mult_n.outputs['Color'])

    @staticmethod
    def init_colormask_or_airbrush(node_tree):
        """Initialize extended node tree for colormask or airbrush flavors with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # disable base paint color
        if Truckpaint.BASE_PAINT_MULT_NODE in node_tree.nodes:
            node_tree.nodes[Truckpaint.BASE_PAINT_MULT_NODE].inputs["Fac"].default_value = 0

        paint_diff_mult_n = node_tree.nodes[Truckpaint.PAINT_DIFFUSE_MULT_NODE]
        paint_spec_mult_n = node_tree.nodes[Truckpaint.PAINT_SPECULAR_MULT_NODE]

        # node creation - level 0
        paint_uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        paint_uv_map_n.name = paint_uv_map_n.label = Truckpaint.PAINT_UV_MAP_NODE
        paint_uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 950)
        paint_uv_map_n.uv_map = _MESH_consts.none_uv

        # node creation - level 1
        paint_base_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_base_col_n.name = paint_base_col_n.label = Truckpaint.PAINT_BASE_COL_NODE
        paint_base_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 950)

        paint_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        paint_tex_n.name = paint_tex_n.label = Truckpaint.PAINT_TEX_NODE
        paint_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 750)
        paint_tex_n.width = 140

        paint_b_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_b_col_n.name = paint_b_col_n.label = Truckpaint.PAINT_B_COL_NODE
        paint_b_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 450)

        paint_g_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_g_col_n.name = paint_g_col_n.label = Truckpaint.PAINT_G_COL_NODE
        paint_g_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 250)

        paint_r_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_r_col_n.name = paint_r_col_n.label = Truckpaint.PAINT_R_COL_NODE
        paint_r_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 50)

        # node creation - level 2
        paint_tex_sep = node_tree.nodes.new("ShaderNodeSeparateRGB")
        paint_tex_sep.name = paint_tex_sep.label = Truckpaint.PAINT_TEX_SEP_NODE
        paint_tex_sep.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 650)

        # node creation - level 3
        airbrush_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        airbrush_mix_n.name = airbrush_mix_n.label = Truckpaint.AIRBRUSH_MIX_NODE
        airbrush_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1000)
        airbrush_mix_n.blend_type = "MIX"

        col_mask_b_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_b_mix_n.name = col_mask_b_mix_n.label = Truckpaint.COL_MASK_B_MIX_NODE
        col_mask_b_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 600)
        col_mask_b_mix_n.blend_type = "MIX"

        col_mask_g_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_g_mix_n.name = col_mask_g_mix_n.label = Truckpaint.COL_MASK_G_MIX_NODE
        col_mask_g_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 400)
        col_mask_g_mix_n.blend_type = "MIX"

        col_mask_r_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_r_mix_n.name = col_mask_r_mix_n.label = Truckpaint.COL_MASK_R_MIX_NODE
        col_mask_r_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 200)
        col_mask_r_mix_n.blend_type = "MIX"

        # node creation - level 4
        blend_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        blend_mix_n.name = blend_mix_n.label = Truckpaint.BLEND_MIX_NODE
        blend_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 800)
        blend_mix_n.inputs['Fac'].default_value = 1.0
        blend_mix_n.blend_type = "MIX"

        # make links - level 0
        node_tree.links.new(paint_tex_n.inputs['Vector'], paint_uv_map_n.outputs['UV'])

        # make links - level 1
        node_tree.links.new(paint_tex_sep.inputs['Image'], paint_tex_n.outputs['Color'])

        # make links - level 2
        node_tree.links.new(airbrush_mix_n.inputs['Fac'], paint_tex_n.outputs['Alpha'])
        node_tree.links.new(airbrush_mix_n.inputs['Color1'], paint_base_col_n.outputs['Color'])
        node_tree.links.new(airbrush_mix_n.inputs['Color2'], paint_tex_n.outputs['Color'])

        node_tree.links.new(col_mask_b_mix_n.inputs['Fac'], paint_tex_sep.outputs['B'])
        node_tree.links.new(col_mask_b_mix_n.inputs['Color1'], paint_base_col_n.outputs['Color'])
        node_tree.links.new(col_mask_b_mix_n.inputs['Color2'], paint_b_col_n.outputs['Color'])

        node_tree.links.new(col_mask_g_mix_n.inputs['Fac'], paint_tex_sep.outputs['G'])
        node_tree.links.new(col_mask_g_mix_n.inputs['Color1'], col_mask_b_mix_n.outputs['Color'])
        node_tree.links.new(col_mask_g_mix_n.inputs['Color2'], paint_g_col_n.outputs['Color'])

        node_tree.links.new(col_mask_r_mix_n.inputs['Fac'], paint_tex_sep.outputs['R'])
        node_tree.links.new(col_mask_r_mix_n.inputs['Color1'], col_mask_g_mix_n.outputs['Color'])
        node_tree.links.new(col_mask_r_mix_n.inputs['Color2'], paint_r_col_n.outputs['Color'])

        # make links - level 3
        node_tree.links.new(blend_mix_n.inputs['Color1'], airbrush_mix_n.outputs['Color'])
        node_tree.links.new(blend_mix_n.inputs['Color2'], col_mask_r_mix_n.outputs['Color'])

        # make links - level 5
        node_tree.links.new(paint_diff_mult_n.inputs['Color2'], blend_mix_n.outputs['Color'])
        node_tree.links.new(paint_spec_mult_n.inputs['Color2'], paint_tex_n.outputs['Alpha'])

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        bias_scale_truckpaint = get_fresnel_truckpaint(bias_scale[0], bias_scale[1])

        DifSpecAddEnv.set_fresnel(node_tree, bias_scale_truckpaint)

    @staticmethod
    def set_base_paint_color(node_tree, color):
        """Set paint color to this node tree if basic truckpaint shader is used (no colormask or airbrush or altuv)

        :param node_tree: node tree to which paint color should be applied
        :type node_tree: bpy.types.NodeTree
        :param color: new color value
        :type color: mathutils.Color
        """

        if Truckpaint.BASE_PAINT_MULT_NODE not in node_tree.nodes:
            return

        color = _convert_utils.to_node_color(color)
        node_tree.nodes[Truckpaint.BASE_PAINT_MULT_NODE].inputs["Color2"].default_value = color

    @staticmethod
    def set_paintjob_texture(node_tree, image):
        """Set paint texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to paint texture node
        :type image: bpy.types.Image
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_TEX_NODE not in node_tree.nodes:
            return

        node_tree.nodes[Truckpaint.PAINT_TEX_NODE].image = image

    @staticmethod
    def set_paintjob_texture_settings(node_tree, settings):
        """Set paintjob texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Truckpaint.PAINT_TEX_NODE], settings)

    @staticmethod
    def set_paintjob_uv(node_tree, uv_layer):
        """Set UV layer to paint texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for paint texture
        :type uv_layer: str
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_TEX_NODE not in node_tree.nodes:
            return

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Truckpaint.PAINT_UV_MAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_aux8(node_tree, color):
        """Set base paintjob color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: base paintjob color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_BASE_COL_NODE not in node_tree.nodes:
            return

        node_tree.nodes[Truckpaint.PAINT_BASE_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux7(node_tree, color):
        """Set paintjob blue component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob blue component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_B_COL_NODE not in node_tree.nodes:
            return

        node_tree.nodes[Truckpaint.PAINT_B_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux6(node_tree, color):
        """Set paintjob green component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob green component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_G_COL_NODE not in node_tree.nodes:
            return

        node_tree.nodes[Truckpaint.PAINT_G_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux5(node_tree, color):
        """Set paintjob green component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob green component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        # as this functions should be called from airbrush or colormask derivatives
        # make sure to skip execution if for some historical reasons this is called from stock truckpaint
        if Truckpaint.PAINT_R_COL_NODE not in node_tree.nodes:
            return

        node_tree.nodes[Truckpaint.PAINT_R_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)
