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

# Copyright (C) 2017: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts

TSNMAP_DDS16_G = _MAT_consts.node_group_prefix + "TSNMapDDS16Group"

_NMAP_TEX_SEP_NODE = "SeparateTexRGB"
_R_POW_NODE = "PowerR"
_G_POW_NODE = "PowerG"
_R_SUBTRACT_NODE = "SubtractR"
_G_SUBTRACT_NODE = "SubtractG"
_SQUARE_POW_NODE = "SquarePow"
_NMAP_TEX_COMBINE_NODE = "CombineTexRGB"


def get_node_group():
    """Gets node group for DDS 16-bit normal map texture.

    :return: node group which handles 16-bit DDS
    :rtype: bpy.types.NodeGroup
    """

    if TSNMAP_DDS16_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[TSNMAP_DDS16_G]


def __create_node_group__():
    """Creates DDS 16-bit handling group.

    Current implementation does 2 things:
    1. sends normal map image to output with statically set blue channel to 1
    2. calculates strength of normal maps aka blue channel as we do it in game

    Inputs: NMap Tex Color
    Outputs: NMap Tex Color
    """

    nmap_dds16_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=TSNMAP_DDS16_G)

    # inputs defining
    nmap_dds16_g.inputs.new("NodeSocketColor", "Color")
    input_n = nmap_dds16_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    nmap_dds16_g.outputs.new("NodeSocketFloat", "Strength")
    nmap_dds16_g.outputs.new("NodeSocketColor", "Color")
    output_n = nmap_dds16_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 7, 0)

    # group nodes
    separate_rgb_n = nmap_dds16_g.nodes.new("ShaderNodeSeparateRGB")
    separate_rgb_n.name = separate_rgb_n.label = _NMAP_TEX_SEP_NODE
    separate_rgb_n.location = (185 * 1, 100)

    # 1. pass
    red_pow_n = nmap_dds16_g.nodes.new("ShaderNodeMath")
    red_pow_n.name = red_pow_n.label = _R_POW_NODE
    red_pow_n.location = (185 * 2, 0)
    red_pow_n.operation = "POWER"
    red_pow_n.inputs[1].default_value = 2.0

    green_pow_n = nmap_dds16_g.nodes.new("ShaderNodeMath")
    green_pow_n.name = green_pow_n.label = _G_POW_NODE
    green_pow_n.location = (185 * 2, -200)
    green_pow_n.operation = "POWER"
    green_pow_n.inputs[1].default_value = 2.0

    # 2. pass
    red_sub_n = nmap_dds16_g.nodes.new("ShaderNodeMath")
    red_sub_n.name = red_sub_n.label = _R_SUBTRACT_NODE
    red_sub_n.location = (185 * 3, 0)
    red_sub_n.operation = "SUBTRACT"
    red_sub_n.inputs[0].default_value = 1.0

    # 3. pass
    green_sub_n = nmap_dds16_g.nodes.new("ShaderNodeMath")
    green_sub_n.name = green_sub_n.label = _G_SUBTRACT_NODE
    green_sub_n.location = (185 * 4, -100)
    green_sub_n.operation = "SUBTRACT"

    # 4. pass
    square_pow_n = nmap_dds16_g.nodes.new("ShaderNodeMath")
    square_pow_n.name = square_pow_n.label = _SQUARE_POW_NODE
    square_pow_n.location = (185 * 5, 0)
    square_pow_n.operation = "POWER"
    square_pow_n.inputs[1].default_value = 0.5

    # 5. pass
    combine_rgb_n = nmap_dds16_g.nodes.new("ShaderNodeCombineRGB")
    combine_rgb_n.name = combine_rgb_n.label = _NMAP_TEX_COMBINE_NODE
    combine_rgb_n.location = (185 * 6, 100)
    combine_rgb_n.inputs['B'].default_value = 1

    # group links
    nmap_dds16_g.links.new(separate_rgb_n.inputs['Image'], input_n.outputs['Color'])

    nmap_dds16_g.links.new(red_pow_n.inputs[0], separate_rgb_n.outputs['R'])
    nmap_dds16_g.links.new(green_pow_n.inputs[0], separate_rgb_n.outputs['G'])

    nmap_dds16_g.links.new(red_sub_n.inputs[1], red_pow_n.outputs[0])

    nmap_dds16_g.links.new(green_sub_n.inputs[0], red_sub_n.outputs[0])
    nmap_dds16_g.links.new(green_sub_n.inputs[1], green_pow_n.outputs[0])

    nmap_dds16_g.links.new(square_pow_n.inputs[0], green_sub_n.outputs[0])

    nmap_dds16_g.links.new(combine_rgb_n.inputs['R'], separate_rgb_n.outputs['R'])
    nmap_dds16_g.links.new(combine_rgb_n.inputs['G'], separate_rgb_n.outputs['G'])

    nmap_dds16_g.links.new(output_n.inputs['Color'], combine_rgb_n.outputs['Image'])
    nmap_dds16_g.links.new(output_n.inputs['Strength'], square_pow_n.outputs[0])
