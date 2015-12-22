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


from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.utils import convert as _convert_utils


class Truckpaint(DifSpecAddEnv):
    PAINT_GEOM_NODE = "PaintGeometry"

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

    BLEND_MIX_NODE = "BlendMode"

    PAINT_MULT_NODE = "PaintMultiplier"

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

        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        env_color_n = node_tree.nodes[DifSpecAddEnv.ENV_COLOR_NODE]
        spec_color_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        diff_mult_n = node_tree.nodes[DifSpecAddEnv.DIFF_MULT_NODE]
        add_refl_gn = node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE]
        spec_mult_n = node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpecAddEnv.VCOLOR_SCALE_NODE]
        opacity_n = node_tree.nodes[DifSpecAddEnv.OPACITY_NODE]
        out_mat_n = node_tree.nodes[DifSpecAddEnv.OUT_MAT_NODE]
        out_add_refl_n = node_tree.nodes[DifSpecAddEnv.OUT_ADD_REFL_NODE]
        output_n = node_tree.nodes[DifSpecAddEnv.OUTPUT_NODE]

        # move existing
        add_refl_gn.location.x += pos_x_shift * 2
        spec_mult_n.location.x += pos_x_shift * 2
        out_mat_n.location.x += pos_x_shift
        out_add_refl_n.location.x += pos_x_shift
        output_n.location.x += pos_x_shift

        # set fresnel factor to 0
        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Apply Fresnel'].default_value = 0.0

        # node creation - level 0
        paint_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        paint_geom_n.name = Truckpaint.PAINT_GEOM_NODE
        paint_geom_n.label = Truckpaint.PAINT_GEOM_NODE
        paint_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 950)
        paint_geom_n.uv_layer = _MESH_consts.none_uv

        # node creation - level 1
        paint_base_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_base_col_n.name = Truckpaint.PAINT_BASE_COL_NODE
        paint_base_col_n.label = Truckpaint.PAINT_BASE_COL_NODE
        paint_base_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 950)

        paint_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        paint_tex_n.name = Truckpaint.PAINT_TEX_NODE
        paint_tex_n.label = Truckpaint.PAINT_TEX_NODE
        paint_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 750)

        paint_b_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_b_col_n.name = Truckpaint.PAINT_B_COL_NODE
        paint_b_col_n.label = Truckpaint.PAINT_B_COL_NODE
        paint_b_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 450)

        paint_g_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_g_col_n.name = Truckpaint.PAINT_G_COL_NODE
        paint_g_col_n.label = Truckpaint.PAINT_G_COL_NODE
        paint_g_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 250)

        paint_r_col_n = node_tree.nodes.new("ShaderNodeRGB")
        paint_r_col_n.name = Truckpaint.PAINT_R_COL_NODE
        paint_r_col_n.label = Truckpaint.PAINT_R_COL_NODE
        paint_r_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 50)

        # node creation - level 2
        paint_tex_sep = node_tree.nodes.new("ShaderNodeSeparateRGB")
        paint_tex_sep.name = Truckpaint.PAINT_TEX_SEP_NODE
        paint_tex_sep.label = Truckpaint.PAINT_TEX_SEP_NODE
        paint_tex_sep.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 650)

        # node creation - level 3
        env_vcol_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        env_vcol_mix_n.name = Truckpaint.ENV_VCOL_MULT_NODE
        env_vcol_mix_n.label = Truckpaint.ENV_VCOL_MULT_NODE
        env_vcol_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 2000)
        env_vcol_mix_n.blend_type = "MULTIPLY"
        env_vcol_mix_n.inputs['Fac'].default_value = 1

        spec_vcol_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        spec_vcol_mix_n.name = Truckpaint.SPEC_VCOL_MULT_NODE
        spec_vcol_mix_n.label = Truckpaint.SPEC_VCOL_MULT_NODE
        spec_vcol_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1750)
        spec_vcol_mix_n.blend_type = "MULTIPLY"
        spec_vcol_mix_n.inputs['Fac'].default_value = 1

        opacity_vcol_n = node_tree.nodes.new("ShaderNodeMath")
        opacity_vcol_n.name = Truckpaint.OPACITY_VCOL_MULT_NODE
        opacity_vcol_n.label = Truckpaint.OPACITY_VCOL_MULT_NODE
        opacity_vcol_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1300)
        opacity_vcol_n.operation = "MULTIPLY"

        airbrush_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        airbrush_mix_n.name = Truckpaint.AIRBRUSH_MIX_NODE
        airbrush_mix_n.label = Truckpaint.AIRBRUSH_MIX_NODE
        airbrush_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1000)
        airbrush_mix_n.blend_type = "MIX"

        col_mask_b_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_b_mix_n.name = Truckpaint.COL_MASK_B_MIX_NODE
        col_mask_b_mix_n.label = Truckpaint.COL_MASK_B_MIX_NODE
        col_mask_b_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 600)
        col_mask_b_mix_n.blend_type = "MIX"

        col_mask_g_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_g_mix_n.name = Truckpaint.COL_MASK_G_MIX_NODE
        col_mask_g_mix_n.label = Truckpaint.COL_MASK_G_MIX_NODE
        col_mask_g_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 400)
        col_mask_g_mix_n.blend_type = "MIX"

        col_mask_r_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        col_mask_r_mix_n.name = Truckpaint.COL_MASK_R_MIX_NODE
        col_mask_r_mix_n.label = Truckpaint.COL_MASK_R_MIX_NODE
        col_mask_r_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 200)
        col_mask_r_mix_n.blend_type = "MIX"

        # node creation - level 4
        blend_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        blend_mix_n.name = Truckpaint.BLEND_MIX_NODE
        blend_mix_n.label = Truckpaint.BLEND_MIX_NODE
        blend_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 800)
        blend_mix_n.inputs['Fac'].default_value = 1.0
        blend_mix_n.blend_type = "MIX"

        # node creation - level 5
        paint_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        paint_mult_n.name = Truckpaint.PAINT_MULT_NODE
        paint_mult_n.label = Truckpaint.PAINT_MULT_NODE
        paint_mult_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1400)
        paint_mult_n.blend_type = "MULTIPLY"
        paint_mult_n.inputs['Fac'].default_value = 0

        # make links - level 0
        node_tree.links.new(paint_tex_n.inputs['Vector'], paint_geom_n.outputs['UV'])

        # make links - level 1
        node_tree.links.new(paint_tex_sep.inputs['Image'], paint_tex_n.outputs['Color'])

        # make links - level 2
        node_tree.links.new(env_vcol_mix_n.inputs['Color1'], env_color_n.outputs['Color'])
        node_tree.links.new(env_vcol_mix_n.inputs['Color2'], vcol_scale_n.outputs['Color'])

        node_tree.links.new(spec_vcol_mix_n.inputs['Color1'], base_tex_n.outputs['Value'])
        node_tree.links.new(spec_vcol_mix_n.inputs['Color2'], vcol_scale_n.outputs['Color'])

        node_tree.links.new(airbrush_mix_n.inputs['Fac'], paint_tex_n.outputs['Value'])
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
        node_tree.links.new(add_refl_gn.inputs['Env Factor Color'], env_vcol_mix_n.outputs['Color'])

        node_tree.links.new(spec_mult_n.inputs['Color1'], spec_color_n.outputs['Color'])
        node_tree.links.new(spec_mult_n.inputs['Color2'], spec_vcol_mix_n.outputs['Color'])

        node_tree.links.new(opacity_vcol_n.inputs[0], vcol_scale_n.outputs['Color'])
        node_tree.links.new(opacity_vcol_n.inputs[1], opacity_n.outputs[0])

        node_tree.links.new(blend_mix_n.inputs['Color1'], airbrush_mix_n.outputs['Color'])
        node_tree.links.new(blend_mix_n.inputs['Color2'], col_mask_r_mix_n.outputs['Color'])

        # make links - level 4
        node_tree.links.new(paint_mult_n.inputs['Color1'], diff_mult_n.outputs['Color'])
        node_tree.links.new(paint_mult_n.inputs['Color2'], blend_mix_n.outputs['Color'])

        # make links - output
        node_tree.links.new(out_mat_n.inputs['Color'], paint_mult_n.outputs['Color'])

    @staticmethod
    def set_paintjob_texture(node_tree, texture):
        """Set paint texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to paint texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Truckpaint.PAINT_TEX_NODE].texture = texture

    @staticmethod
    def set_paintjob_uv(node_tree, uv_layer):
        """Set UV layer to paint texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for paint texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Truckpaint.PAINT_GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_aux8(node_tree, color):
        """Set base paintjob color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: base paintjob color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Truckpaint.PAINT_BASE_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux7(node_tree, color):
        """Set paintjob blue component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob blue component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Truckpaint.PAINT_B_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux6(node_tree, color):
        """Set paintjob green component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob green component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Truckpaint.PAINT_G_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)

    @staticmethod
    def set_aux5(node_tree, color):
        """Set paintjob green component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: paintjob green component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Truckpaint.PAINT_R_COL_NODE].outputs['Color'].default_value = _convert_utils.aux_to_node_color(color)
