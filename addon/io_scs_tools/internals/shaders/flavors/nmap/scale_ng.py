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

import bpy
from io_scs_tools.consts import Material as _MAT_consts

TSNMAP_SCALE_G = _MAT_consts.node_group_prefix + "TSNMapScaleGroup"

_NMAP_TEX_SEP_NODE = "SeparateNMapTexRGB"
_ORIG_NOR_SEP_NODE = "SeparateNorRGB"
_MODIF_NOR_SEP_NODE = "SeparateNorRGB"
_RED_CHANNEL_MATH_UPPER_NODE = "RedUpper"
_RED_CHANNEL_MATH_LOWER_NODE = "RedLower"
_GREEN_CHANNEL_MATH_UPPER_NODE = "GreenUpper"
_GREEN_CHANNEL_MATH_LOWER_NODE = "GreenLower"
_RED_MAX_MATH_NODE = "RedMax"
_GREEN_MAX_MATH_NODE = "GreenMax"
_RED_MIX_NODE = "RedMix"
_GREEN_MIX_NODE = "GreenMix"
_COMBINE_NORMAL_NODE = "NormalCombine"


def get_node_group():
    """Gets node group for normal map scaling workaround.

    This actually disables normal maps for surfaces with RGB value (128,128,255).

    :return: node group which exposes vertex color input
    :rtype: bpy.types.NodeGroup
    """

    if TSNMAP_SCALE_G not in bpy.data.node_groups:
        __create_nmap_scale_group__()

    return bpy.data.node_groups[TSNMAP_SCALE_G]


def __create_nmap_scale_group__():
    """Creates tangent space normal map scale group.

    Inputs: NMap Tex Color, Original Normal, Modified Normal
    Outputs: Normal
    """

    _NMAP_MIDDLE_VALUE = 128.0 / 255.0
    _EPSILON = 0.0000003

    nmap_scale_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=TSNMAP_SCALE_G)

    # inputs defining
    nmap_scale_g.inputs.new("NodeSocketColor", "NMap Tex Color")
    nmap_scale_g.inputs.new("NodeSocketVector", "Original Normal")
    nmap_scale_g.inputs.new("NodeSocketVector", "Modified Normal")
    input_n = nmap_scale_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    nmap_scale_g.outputs.new("NodeSocketVector", "Normal")
    output_n = nmap_scale_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 6, 0)

    # group nodes
    separate_rgb_n = nmap_scale_g.nodes.new("ShaderNodeSeparateRGB")
    separate_rgb_n.name = separate_rgb_n.label = _NMAP_TEX_SEP_NODE
    separate_rgb_n.location = (185 * 1, 400)

    sep_orig_nor_n = nmap_scale_g.nodes.new("ShaderNodeSeparateRGB")
    sep_orig_nor_n.name = sep_orig_nor_n.label = _ORIG_NOR_SEP_NODE
    sep_orig_nor_n.location = (185 * 1, -100)

    sep_modif_nor_n = nmap_scale_g.nodes.new("ShaderNodeSeparateRGB")
    sep_modif_nor_n.name = sep_modif_nor_n.label = _MODIF_NOR_SEP_NODE
    sep_modif_nor_n.location = (185 * 1, -300)

    red_math_upper_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_math_upper_n.name = red_math_upper_n.label = _RED_CHANNEL_MATH_UPPER_NODE
    red_math_upper_n.location = (185 * 2, 700)
    red_math_upper_n.operation = "GREATER_THAN"
    red_math_upper_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE + _EPSILON

    red_math_lower_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_math_lower_n.name = red_math_lower_n.label = _RED_CHANNEL_MATH_LOWER_NODE
    red_math_lower_n.location = (185 * 2, 500)
    red_math_lower_n.operation = "LESS_THAN"
    red_math_lower_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE - _EPSILON

    green_math_upper_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_math_upper_n.name = green_math_upper_n.label = _GREEN_CHANNEL_MATH_UPPER_NODE
    green_math_upper_n.location = (185 * 2, 300)
    green_math_upper_n.operation = "GREATER_THAN"
    green_math_upper_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE + _EPSILON

    green_math_lower_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_math_lower_n.name = green_math_lower_n.label = _GREEN_CHANNEL_MATH_LOWER_NODE
    green_math_lower_n.location = (185 * 2, 100)
    green_math_lower_n.operation = "LESS_THAN"
    green_math_lower_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE - _EPSILON

    red_max_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_max_n.name = red_max_n.label = _RED_MAX_MATH_NODE
    red_max_n.location = (185 * 3, 600)
    red_max_n.operation = "MAXIMUM"

    green_max_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_max_n.name = green_max_n.label = _GREEN_MAX_MATH_NODE
    green_max_n.location = (185 * 3, 200)
    green_max_n.operation = "MAXIMUM"

    red_mix_n = nmap_scale_g.nodes.new("ShaderNodeMixRGB")
    red_mix_n.name = red_mix_n.label = _RED_MIX_NODE
    red_mix_n.location = (185 * 4, 100)
    red_mix_n.blend_type = "MIX"

    green_mix_n = nmap_scale_g.nodes.new("ShaderNodeMixRGB")
    green_mix_n.name = green_mix_n.label = _GREEN_MIX_NODE
    green_mix_n.location = (185 * 4, -100)
    green_mix_n.blend_type = "MIX"

    combine_nor_n = nmap_scale_g.nodes.new("ShaderNodeCombineRGB")
    combine_nor_n.name = combine_nor_n.label = _COMBINE_NORMAL_NODE
    combine_nor_n.location = (185 * 5, -250)

    # group links
    nmap_scale_g.links.new(separate_rgb_n.inputs['Image'], input_n.outputs['NMap Tex Color'])
    nmap_scale_g.links.new(sep_orig_nor_n.inputs['Image'], input_n.outputs['Original Normal'])
    nmap_scale_g.links.new(sep_modif_nor_n.inputs['Image'], input_n.outputs['Modified Normal'])

    nmap_scale_g.links.new(red_math_upper_n.inputs[0], separate_rgb_n.outputs['R'])
    nmap_scale_g.links.new(red_math_lower_n.inputs[0], separate_rgb_n.outputs['R'])
    nmap_scale_g.links.new(green_math_upper_n.inputs[0], separate_rgb_n.outputs['G'])
    nmap_scale_g.links.new(green_math_lower_n.inputs[0], separate_rgb_n.outputs['G'])

    nmap_scale_g.links.new(red_max_n.inputs[0], red_math_upper_n.outputs[0])
    nmap_scale_g.links.new(red_max_n.inputs[1], red_math_lower_n.outputs[0])
    nmap_scale_g.links.new(green_max_n.inputs[0], green_math_upper_n.outputs[0])
    nmap_scale_g.links.new(green_max_n.inputs[1], green_math_lower_n.outputs[0])

    nmap_scale_g.links.new(red_mix_n.inputs['Fac'], red_max_n.outputs[0])
    nmap_scale_g.links.new(red_mix_n.inputs['Color1'], sep_orig_nor_n.outputs['R'])
    nmap_scale_g.links.new(red_mix_n.inputs['Color2'], sep_modif_nor_n.outputs['R'])
    nmap_scale_g.links.new(green_mix_n.inputs['Fac'], green_max_n.outputs[0])
    nmap_scale_g.links.new(green_mix_n.inputs['Color1'], sep_orig_nor_n.outputs['G'])
    nmap_scale_g.links.new(green_mix_n.inputs['Color2'], sep_modif_nor_n.outputs['G'])

    nmap_scale_g.links.new(combine_nor_n.inputs['R'], red_mix_n.outputs['Color'])
    nmap_scale_g.links.new(combine_nor_n.inputs['G'], green_mix_n.outputs['Color'])
    nmap_scale_g.links.new(combine_nor_n.inputs['B'], sep_modif_nor_n.outputs['B'])

    nmap_scale_g.links.new(output_n.inputs['Normal'], combine_nor_n.outputs['Image'])
