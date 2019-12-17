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

import bpy
from io_scs_tools.internals.shaders.eut2.std_node_groups import linear_to_srgb_ng
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.consts import Mesh as _MESH_consts

VCOLOR_G = _MAT_consts.node_group_prefix + "VColorGroup"

_VCOL_ATTRIBUTE_NODE = "VertexColor"
_VCOL_ATTRIBUTE_A_NODE = "VertexColorAlpha"

_VCOL_SEPARATE_NODE = "VertexColorToRGB"
_ALPHA_TO_BW_NODE = "VertexColAToBW"

_VCOL_R_LIN_TO_SRGB_NODE = "RedLinearToSRGB"
_VCOL_G_LIN_TO_SRGB_NODE = "GreenLinearToSRGB"
_VCOL_B_LIN_TO_SRGB_NODE = "BlueLinearToSRGB"
_ALPHA_LIN_TO_SRGB_NODE = "ALphaLinearToSRGB"

_ALPHA_EXTEND_NODE = "AlphaExtend"

_VCOL_COMBINE_NODE = "VertexColorRGBCombine"


def get_node_group():
    """Gets node group for vertex color inputs.

    :return: node group which exposes vertex color input
    :rtype: bpy.types.NodeGroup
    """

    if VCOLOR_G not in bpy.data.node_groups:
        __create_vcolor_group__()

    return bpy.data.node_groups[VCOLOR_G]


def __create_vcolor_group__():
    """Creates vertex color input group.

    Inputs: None
    Outputs: Vertex Color, Vertex Color Alpha
    """

    pos_x_shift = 185

    vcol_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=VCOLOR_G)

    # outputs defining
    vcol_g.outputs.new("NodeSocketColor", "Vertex Color")
    vcol_g.outputs.new("NodeSocketFloat", "Vertex Color Alpha")
    output_n = vcol_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 5, 0)

    # group nodes
    vcol_n = vcol_g.nodes.new("ShaderNodeVertexColor")
    vcol_n.name = vcol_n.label = _VCOL_ATTRIBUTE_NODE
    vcol_n.location = (pos_x_shift, 200)
    vcol_n.layer_name = _MESH_consts.default_vcol

    vcol_a_n = vcol_g.nodes.new("ShaderNodeVertexColor")
    vcol_a_n.name = vcol_a_n.label = _VCOL_ATTRIBUTE_A_NODE
    vcol_a_n.location = (pos_x_shift, -100)
    vcol_a_n.layer_name = _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix

    vcol_separate_rgb_n = vcol_g.nodes.new("ShaderNodeSeparateRGB")
    vcol_separate_rgb_n.name = vcol_separate_rgb_n.label = _VCOL_SEPARATE_NODE
    vcol_separate_rgb_n.location = (pos_x_shift * 2, 200)

    alpha_to_bw_n = vcol_g.nodes.new("ShaderNodeRGBToBW")
    alpha_to_bw_n.name = alpha_to_bw_n.label = _ALPHA_TO_BW_NODE
    alpha_to_bw_n.location = (pos_x_shift * 2, -100)

    vcol_r_lin_to_srgb_n = vcol_g.nodes.new("ShaderNodeGroup")
    vcol_r_lin_to_srgb_n.name = vcol_r_lin_to_srgb_n.label = _VCOL_R_LIN_TO_SRGB_NODE
    vcol_r_lin_to_srgb_n.location = (pos_x_shift * 3, 350)
    vcol_r_lin_to_srgb_n.node_tree = linear_to_srgb_ng.get_node_group()

    vcol_g_lin_to_srgb_n = vcol_g.nodes.new("ShaderNodeGroup")
    vcol_g_lin_to_srgb_n.name = vcol_g_lin_to_srgb_n.label = _VCOL_G_LIN_TO_SRGB_NODE
    vcol_g_lin_to_srgb_n.location = (pos_x_shift * 3, 200)
    vcol_g_lin_to_srgb_n.node_tree = linear_to_srgb_ng.get_node_group()

    vcol_b_lin_to_srgb_n = vcol_g.nodes.new("ShaderNodeGroup")
    vcol_b_lin_to_srgb_n.name = vcol_b_lin_to_srgb_n.label = _VCOL_B_LIN_TO_SRGB_NODE
    vcol_b_lin_to_srgb_n.location = (pos_x_shift * 3, 50)
    vcol_b_lin_to_srgb_n.node_tree = linear_to_srgb_ng.get_node_group()

    alpha_lin_to_srgb_n = vcol_g.nodes.new("ShaderNodeGroup")
    alpha_lin_to_srgb_n.name = alpha_lin_to_srgb_n.label = _ALPHA_LIN_TO_SRGB_NODE
    alpha_lin_to_srgb_n.location = (pos_x_shift * 3, -100)
    alpha_lin_to_srgb_n.node_tree = linear_to_srgb_ng.get_node_group()

    alpha_extend_n = vcol_g.nodes.new("ShaderNodeMath")
    alpha_extend_n.name = alpha_extend_n.label = _ALPHA_EXTEND_NODE
    alpha_extend_n.location = (pos_x_shift * 4, -100)
    alpha_extend_n.operation = "MULTIPLY"
    alpha_extend_n.inputs[1].default_value = 2.0

    vcol_combine_n = vcol_g.nodes.new("ShaderNodeCombineRGB")
    vcol_combine_n.name = vcol_combine_n.label = _VCOL_COMBINE_NODE
    vcol_combine_n.location = (pos_x_shift * 4, 200)

    # group links
    vcol_g.links.new(vcol_separate_rgb_n.inputs['Image'], vcol_n.outputs['Color'])
    vcol_g.links.new(alpha_to_bw_n.inputs["Color"], vcol_a_n.outputs['Color'])

    vcol_g.links.new(vcol_r_lin_to_srgb_n.inputs['Value'], vcol_separate_rgb_n.outputs['R'])
    vcol_g.links.new(vcol_g_lin_to_srgb_n.inputs['Value'], vcol_separate_rgb_n.outputs['G'])
    vcol_g.links.new(vcol_b_lin_to_srgb_n.inputs['Value'], vcol_separate_rgb_n.outputs['B'])
    vcol_g.links.new(alpha_lin_to_srgb_n.inputs['Value'], alpha_to_bw_n.outputs['Val'])

    vcol_g.links.new(vcol_combine_n.inputs['R'], vcol_r_lin_to_srgb_n.outputs["Value"])
    vcol_g.links.new(vcol_combine_n.inputs['G'], vcol_g_lin_to_srgb_n.outputs["Value"])
    vcol_g.links.new(vcol_combine_n.inputs['B'], vcol_b_lin_to_srgb_n.outputs["Value"])

    vcol_g.links.new(alpha_extend_n.inputs[0], alpha_lin_to_srgb_n.outputs['Value'])

    vcol_g.links.new(output_n.inputs['Vertex Color'], vcol_combine_n.outputs['Image'])
    vcol_g.links.new(output_n.inputs['Vertex Color Alpha'], alpha_extend_n.outputs['Value'])
