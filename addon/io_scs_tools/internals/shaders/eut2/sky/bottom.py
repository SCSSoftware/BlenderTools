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

# Copyright (C) 2026: SCS Software

from ..std_node_groups import vcolor_input_ng
from ...base import BaseShader
from ...std_node_groups import output_shader_ng
from .....utils import convert as _convert_utils


class SkyBottom(BaseShader):
    VCOL_GROUP_NODE = "VColorGroup"
    DIFF_COL_NODE = "DiffuseColor"
    BCOLOR_NODE = "BottomColor"
    VCOLOR_MULT_NODE = "VertexColorMultiplier"
    BCOLOR_MULT_NODE = "BottomColorMultiplier"
    DIFF_MULT_NODE = "DiffuseMultiplier"

    OUT_SHADER_NODE = "OutShader"
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
        vcol_group_n.name = vcol_group_n.label = SkyBottom.VCOL_GROUP_NODE
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1800)
        vcol_group_n.node_tree = vcolor_input_ng.get_node_group()

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = diff_col_n.label = SkyBottom.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x, start_pos_y + 2000)

        vcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vcol_mult_n.name = vcol_mult_n.label = SkyBottom.VCOLOR_MULT_NODE
        vcol_mult_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1900)
        vcol_mult_n.operation = "MULTIPLY"
        vcol_mult_n.inputs[1].default_value = (2,) * 3

        diff_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        diff_mult_n.name = diff_mult_n.label = SkyBottom.DIFF_MULT_NODE
        diff_mult_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 2000)
        diff_mult_n.operation = "MULTIPLY"

        bcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        bcol_mult_n.name = bcol_mult_n.label = SkyBottom.BCOLOR_MULT_NODE
        bcol_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1950)
        bcol_mult_n.operation = "MULTIPLY"

        bottom_col_n = node_tree.nodes.new("ShaderNodeRGB")
        bottom_col_n.name = bottom_col_n.label = SkyBottom.BCOLOR_NODE
        bottom_col_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1850)

        out_shader_node = node_tree.nodes.new("ShaderNodeGroup")
        out_shader_node.name = out_shader_node.label = SkyBottom.OUT_SHADER_NODE
        out_shader_node.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1700)
        out_shader_node.node_tree = output_shader_ng.get_node_group()

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = SkyBottom.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 5, start_pos_y + 1700)

        # links creation
        # pass 1
        node_tree.links.new(vcol_mult_n.inputs[0], vcol_group_n.outputs['Vertex Color'])
        node_tree.links.new(out_shader_node.inputs['Alpha'], vcol_group_n.outputs['Vertex Color Alpha'])

        # pass 2
        node_tree.links.new(diff_mult_n.inputs[0], diff_col_n.outputs[0])

        # pass 3
        node_tree.links.new(diff_mult_n.inputs[1], vcol_mult_n.outputs[0])

        # pass 4
        node_tree.links.new(bcol_mult_n.inputs[0], diff_mult_n.outputs[0])
        node_tree.links.new(bcol_mult_n.inputs[1], bottom_col_n.outputs[0])

        # pass 5
        node_tree.links.new(out_shader_node.inputs['Color'], bcol_mult_n.outputs[0])

        # output pass
        node_tree.links.new(output_n.inputs['Surface'], out_shader_node.outputs['Shader'])


    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        out_shader_node = node_tree.nodes[SkyBottom.OUT_SHADER_NODE]

        material.use_backface_culling = True
        out_shader_node.inputs["Alpha Type"].default_value = 1.0
        material.surface_render_method = "BLENDED"

    @staticmethod
    def set_diffuse(node_tree, color):
        """Set diffuse color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: diffuse color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[SkyBottom.DIFF_COL_NODE].outputs['Color'].default_value = color

    ##########################
    ####   AUX/FLAVORS    ####
    ##########################

    @staticmethod
    def set_aux0(node_tree, color):
        """Set sky bottom component color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: sky bottom color component color represented with property group
        :type color: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[SkyBottom.BCOLOR_NODE].outputs[0].default_value = _convert_utils.aux_to_node_color(color)
