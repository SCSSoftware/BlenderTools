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
_RED_CHANNEL_MATH_SUB_NODE = "RedOffset"
_RED_CHANNEL_MATH_MULT_NODE = "RedScale"
_RED_CHANNEL_MATH_ABS_NODE = "RedAbsolute"
_GREEN_CHANNEL_MATH_SUB_NODE = "GreenOffset"
_GREEN_CHANNEL_MATH_MULT_NODE = "GreenScale"
_GREEN_CHANNEL_MATH_ABS_NODE = "GreenAbsolute"
_COMBINE_RED_NODE = "RedCombine"
_COMBINE_GREEN_NODE = "GreenCombine"


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

    Current implementation tries to mix normals instead of
    ignoring modified normal by nmap texture if R or G is 128.
    Mixing is done by subtracting middle point nmap texture value (128 -> 0.502)
    and then scaling it by scale factor so for values 128 only
    unmodified geometry normal is used and for values neear middle point
    both normals are mixed depending on distance from 128 ( the bigger the
    distance from 128 is more of modified normal is used).
    And by enough big distance (currently 20) effect of mixing completely
    fades out and only modified normal is used.

    Inputs: NMap Tex Color, Original Normal, Modified Normal
    Outputs: Normal
    """

    _NMAP_MIDDLE_VALUE = 128.0 / 255.0
    _SCALE_FACTOR = 20.0

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
    output_n.location = (185 * 7, 0)

    # group nodes
    separate_rgb_n = nmap_scale_g.nodes.new("ShaderNodeSeparateRGB")
    separate_rgb_n.name = separate_rgb_n.label = _NMAP_TEX_SEP_NODE
    separate_rgb_n.location = (185 * 1, 400)

    red_math_sub_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_math_sub_n.name = red_math_sub_n.label = _RED_CHANNEL_MATH_SUB_NODE
    red_math_sub_n.location = (185 * 2, 700)
    red_math_sub_n.operation = "SUBTRACT"
    red_math_sub_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE

    red_math_mult_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_math_mult_n.name = red_math_mult_n.label = _RED_CHANNEL_MATH_MULT_NODE
    red_math_mult_n.location = (185 * 3, 700)
    red_math_mult_n.operation = "MULTIPLY"
    red_math_mult_n.inputs[1].default_value = _SCALE_FACTOR

    red_math_abs_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    red_math_abs_n.name = red_math_abs_n.label = _RED_CHANNEL_MATH_ABS_NODE
    red_math_abs_n.location = (185 * 4, 700)
    red_math_abs_n.operation = "ABSOLUTE"
    red_math_abs_n.use_clamp = True

    green_math_sub_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_math_sub_n.name = green_math_sub_n.label = _GREEN_CHANNEL_MATH_SUB_NODE
    green_math_sub_n.location = (185 * 2, 500)
    green_math_sub_n.operation = "SUBTRACT"
    green_math_sub_n.inputs[1].default_value = _NMAP_MIDDLE_VALUE

    green_math_mult_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_math_mult_n.name = green_math_mult_n.label = _GREEN_CHANNEL_MATH_MULT_NODE
    green_math_mult_n.location = (185 * 3, 500)
    green_math_mult_n.operation = "MULTIPLY"
    green_math_mult_n.inputs[1].default_value = _SCALE_FACTOR

    green_math_abs_n = nmap_scale_g.nodes.new("ShaderNodeMath")
    green_math_abs_n.name = green_math_abs_n.label = _GREEN_CHANNEL_MATH_ABS_NODE
    green_math_abs_n.location = (185 * 4, 500)
    green_math_abs_n.operation = "ABSOLUTE"
    green_math_abs_n.use_clamp = True

    red_mix_n = nmap_scale_g.nodes.new("ShaderNodeMixRGB")
    red_mix_n.name = red_mix_n.label = _COMBINE_RED_NODE
    red_mix_n.location = (185 * 5, 100)
    red_mix_n.blend_type = "MIX"

    green_mix_n = nmap_scale_g.nodes.new("ShaderNodeMixRGB")
    green_mix_n.name = green_mix_n.label = _COMBINE_GREEN_NODE
    green_mix_n.location = (185 * 6, -100)
    green_mix_n.blend_type = "MIX"

    # group links
    nmap_scale_g.links.new(separate_rgb_n.inputs['Image'], input_n.outputs['NMap Tex Color'])

    nmap_scale_g.links.new(red_math_sub_n.inputs[0], separate_rgb_n.outputs['R'])
    nmap_scale_g.links.new(green_math_sub_n.inputs[0], separate_rgb_n.outputs['G'])

    nmap_scale_g.links.new(red_math_mult_n.inputs[0], red_math_sub_n.outputs[0])
    nmap_scale_g.links.new(green_math_mult_n.inputs[0], green_math_sub_n.outputs[0])

    nmap_scale_g.links.new(red_math_abs_n.inputs[0], red_math_mult_n.outputs[0])
    nmap_scale_g.links.new(green_math_abs_n.inputs[0], green_math_mult_n.outputs[0])

    nmap_scale_g.links.new(red_mix_n.inputs['Fac'], red_math_abs_n.outputs[0])
    nmap_scale_g.links.new(red_mix_n.inputs['Color1'], input_n.outputs['Original Normal'])
    nmap_scale_g.links.new(red_mix_n.inputs['Color2'], input_n.outputs['Modified Normal'])

    nmap_scale_g.links.new(green_mix_n.inputs['Fac'], green_math_abs_n.outputs[0])
    nmap_scale_g.links.new(green_mix_n.inputs['Color1'], red_mix_n.outputs['Color'])
    nmap_scale_g.links.new(green_mix_n.inputs['Color2'], input_n.outputs['Modified Normal'])

    nmap_scale_g.links.new(output_n.inputs['Normal'], green_mix_n.outputs['Color'])
