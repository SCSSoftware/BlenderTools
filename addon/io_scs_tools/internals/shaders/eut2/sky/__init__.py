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
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.eut2.std_node_groups import vcolor_input
from io_scs_tools.utils import convert as _convert_utils


class Sky:
    VCOL_GROUP_NODE = "VColorGroup"
    GEOM_NODE = "Geometry"
    SEC_GEOM_NODE = "SecGeometry"
    DIFF_COL_NODE = "DiffuseColor"
    BASE_TEX_NODE = "BaseTex"
    OVER_TEX_NODE = "OverTex"
    MASK_TEX_NODE = "MaskTex"
    BLEND_VAL_NODE = "BlendInput"
    VCOLOR_SCALE_NODE = "VertexColorScale"
    MASK_TEX_SEP_NODE = "SeparateMask"
    MASK_FACTOR_MIX_NODE = "MaskFactorMix"
    MASK_FACTOR_BLEND_MULT_NODE = "MaskFactorBlendMultiplier"
    BASE_OVER_MIX_NODE = "BaseOverMix"
    BASE_OVER_A_MIX_NODE = "BaseOverAlphaMix"
    VCOLOR_MULT_NODE = "VertexColorMultiplier"
    DIFF_MULT_NODE = "DiffuseMultiplier"
    OUTPUT_NODE = "Output"

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
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1650)
        vcol_group_n.node_tree = vcolor_input.get_node_group()

        geometry_n = node_tree.nodes.new("ShaderNodeGeometry")
        geometry_n.name = geometry_n.label = Sky.GEOM_NODE
        geometry_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        geometry_n.uv_layer = _MESH_consts.none_uv

        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = sec_geom_n.label = Sky.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 900)
        sec_geom_n.uv_layer = _MESH_consts.none_uv

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = diff_col_n.label = Sky.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        base_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        base_tex_n.name = base_tex_n.label = Sky.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)

        over_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        over_tex_n.name = over_tex_n.label = Sky.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        mask_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        mask_tex_n.name = mask_tex_n.label = Sky.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 900)

        blend_input_n = node_tree.nodes.new("ShaderNodeValue")
        blend_input_n.name = blend_input_n.label = Sky.BLEND_VAL_NODE
        blend_input_n.location = (start_pos_x + pos_x_shift, start_pos_y + 600)

        vcol_scale_n = node_tree.nodes.new("ShaderNodeMixRGB")
        vcol_scale_n.name = vcol_scale_n.label = Sky.VCOLOR_SCALE_NODE
        vcol_scale_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1600)
        vcol_scale_n.blend_type = "MULTIPLY"
        vcol_scale_n.inputs['Fac'].default_value = 1
        vcol_scale_n.inputs['Color2'].default_value = (2,) * 4

        mask_tex_sep_n = node_tree.nodes.new("ShaderNodeSeparateRGB")
        mask_tex_sep_n.name = mask_tex_sep_n.label = Sky.MASK_TEX_SEP_NODE
        mask_tex_sep_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 900)

        mask_factor_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mask_factor_mix_n.name = mask_factor_mix_n.label = Sky.MASK_FACTOR_MIX_NODE
        mask_factor_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 900)
        mask_factor_mix_n.blend_type = "MIX"
        mask_factor_mix_n.inputs['Color1'].default_value = (1,) * 4
        mask_factor_mix_n.inputs['Color2'].default_value = (16,) * 4

        mask_factor_blend_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mask_factor_blend_mult_n.name = mask_factor_blend_mult_n.label = Sky.MASK_FACTOR_BLEND_MULT_NODE
        mask_factor_blend_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 900)
        mask_factor_blend_mult_n.blend_type = "MULTIPLY"
        mask_factor_blend_mult_n.inputs['Fac'].default_value = 1
        mask_factor_blend_mult_n.use_clamp = True

        base_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_mix_n.name = base_over_mix_n.label = Sky.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1400)
        base_over_mix_n.blend_type = "MIX"

        base_over_a_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_a_mix_n.name = base_over_a_mix_n.label = Sky.BASE_OVER_A_MIX_NODE
        base_over_a_mix_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 1200)
        base_over_a_mix_n.blend_type = "MIX"

        vcol_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        vcol_mult_n.name = Sky.VCOLOR_MULT_NODE
        vcol_mult_n.label = Sky.VCOLOR_MULT_NODE
        vcol_mult_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1500)
        vcol_mult_n.blend_type = "MULTIPLY"
        vcol_mult_n.inputs['Fac'].default_value = 1

        diff_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        diff_mult_n.name = Sky.DIFF_MULT_NODE
        diff_mult_n.label = Sky.DIFF_MULT_NODE
        diff_mult_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1650)
        diff_mult_n.blend_type = "MULTIPLY"
        diff_mult_n.inputs['Fac'].default_value = 1
        diff_mult_n.inputs['Color2'].default_value = (0, 0, 0, 1)

        output_n = node_tree.nodes.new("ShaderNodeOutput")
        output_n.name = Sky.OUTPUT_NODE
        output_n.label = Sky.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 10, start_pos_y + 1500)

        # links creation
        node_tree.links.new(base_tex_n.inputs['Vector'], geometry_n.outputs['UV'])
        node_tree.links.new(over_tex_n.inputs['Vector'], geometry_n.outputs['UV'])
        node_tree.links.new(mask_tex_n.inputs['Vector'], sec_geom_n.outputs['UV'])

        # pass 1
        node_tree.links.new(vcol_scale_n.inputs['Color1'], vcol_group_n.outputs['Vertex Color'])
        node_tree.links.new(mask_tex_sep_n.inputs['Image'], mask_tex_n.outputs['Color'])

        # pass 2
        node_tree.links.new(mask_factor_mix_n.inputs['Fac'], mask_tex_sep_n.outputs['R'])

        # pass 3
        node_tree.links.new(mask_factor_blend_mult_n.inputs['Color1'], mask_factor_mix_n.outputs['Color'])
        node_tree.links.new(mask_factor_blend_mult_n.inputs['Color2'], blend_input_n.outputs['Value'])

        # pass 4
        node_tree.links.new(base_over_mix_n.inputs['Fac'], mask_factor_blend_mult_n.outputs['Color'])
        node_tree.links.new(base_over_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(base_over_mix_n.inputs['Color2'], over_tex_n.outputs['Color'])

        node_tree.links.new(base_over_a_mix_n.inputs['Fac'], mask_factor_blend_mult_n.outputs['Color'])
        node_tree.links.new(base_over_a_mix_n.inputs['Color1'], base_tex_n.outputs['Value'])
        node_tree.links.new(base_over_a_mix_n.inputs['Color2'], over_tex_n.outputs['Value'])

        # pass 5
        node_tree.links.new(vcol_mult_n.inputs['Color1'], vcol_scale_n.outputs['Color'])
        node_tree.links.new(vcol_mult_n.inputs['Color2'], base_over_mix_n.outputs['Color'])

        # pass 6
        node_tree.links.new(diff_mult_n.inputs['Color1'], diff_col_n.outputs['Color'])
        node_tree.links.new(diff_mult_n.inputs['Color2'], vcol_mult_n.outputs['Color'])

        # output pass
        node_tree.links.new(output_n.inputs['Color'], diff_mult_n.outputs['Color'])

    @staticmethod
    def set_material(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        pass  # we don't use any material as no shading is applied

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
    def set_base_texture(node_tree, texture):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to base texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Sky.BASE_TEX_NODE].texture = texture

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

        node_tree.nodes[Sky.GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_over_texture(node_tree, texture):
        """Set over texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to over texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Sky.OVER_TEX_NODE].texture = texture

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to over texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        Sky.set_base_uv(node_tree, uv_layer)

    @staticmethod
    def set_mask_texture(node_tree, texture):
        """Set mask texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to mask texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Sky.MASK_TEX_NODE].texture = texture

    @staticmethod
    def set_mask_uv(node_tree, uv_layer):
        """Set UV layer to mask texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mask texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Sky.SEC_GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set layer blend factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: layer blend factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Sky.BLEND_VAL_NODE].outputs[0].default_value = aux_property[0]['value']

    @staticmethod
    def set_blend_over_flavor(node_tree, switch_on):
        """Set blend over flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend over should be switched on or off
        :type switch_on: bool
        """

        out_node = node_tree.nodes[Sky.OUTPUT_NODE]
        in_node = node_tree.nodes[Sky.BASE_OVER_A_MIX_NODE]

        if switch_on:
            blend_over.init(node_tree, in_node.outputs['Color'], out_node.inputs['Alpha'])
        else:
            blend_over.delete(node_tree)
