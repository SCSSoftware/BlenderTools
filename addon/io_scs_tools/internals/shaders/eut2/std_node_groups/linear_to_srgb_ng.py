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

# Copyright (C) 2019: SCS Software

# Conversion done by formula:
#      / L ≤ 0.0031308: L*12.92
# S = -
#      \ L > 0.0031308: 1.055*L^(1/2.4) − 0.055

import bpy
from io_scs_tools.consts import Material as _MAT_consts

LINEAR_TO_SRGB_G = _MAT_consts.node_group_prefix + "LinearToSRGB"

_SMALL_MULT_NODE = "SMALL_FINAL=L*12.92"

_BIG_POWER_NODE = "BIG_LPOW=L^(1/2.4)"
_BIG_MULT_NODE = "BIG_LMULT=1.055*BIG_LPOW"
_BIG_SUBTRACT_NODE = "BIG_FINAL=BIG_LMULT-0.055"

_IS_SMALL_NODE = "IS_SMALL=L < 0.0031308"
_IS_BIG_NODE = "IS_BIG=L > 0.0031308"

_SMALL_FACTOR_NODE = "SMALL_FINAL*IS_SMALL"
_BIG_FACTOR_NODE = "BIG_FINAL*IS_BIG"

_FINAL_MIX_NODE = "SMALL+BIG"


def get_node_group():
    """Gets node group for linear to srgb conversion.

    :return: node group which exposes linear to srgb conversion
    :rtype: bpy.types.NodeGroup
    """

    if LINEAR_TO_SRGB_G not in bpy.data.node_groups:
        __create_linear_to_srgb_group__()

    return bpy.data.node_groups[LINEAR_TO_SRGB_G]


def __create_linear_to_srgb_group__():
    """Creates linear to srgb coonversion group.

    Inputs: Value
    Outputs: Value
    """

    lin_to_srgb_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=LINEAR_TO_SRGB_G)

    start_pos_x = 0
    pos_x_shift = 185

    # outputs defining
    # inputs defining
    lin_to_srgb_g.inputs.new("NodeSocketFloat", "Value")
    input_n = lin_to_srgb_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, 0)

    # outputs defining
    lin_to_srgb_g.outputs.new("NodeSocketFloat", "Value")
    output_n = lin_to_srgb_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 7, 0)

    # group nodes
    small_mult_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    small_mult_n.name = small_mult_n.label = _SMALL_MULT_NODE
    small_mult_n.location = (start_pos_x + pos_x_shift * 3, 200)
    small_mult_n.operation = 'MULTIPLY'
    small_mult_n.inputs[1].default_value = 12.92

    big_pow_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    big_pow_n.name = big_pow_n.label = _BIG_POWER_NODE
    big_pow_n.location = (start_pos_x + pos_x_shift, -200)
    big_pow_n.operation = 'POWER'
    big_pow_n.inputs[1].default_value = 1 / 2.4

    big_mult_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    big_mult_n.name = big_mult_n.label = _BIG_MULT_NODE
    big_mult_n.location = (start_pos_x + pos_x_shift * 2, -200)
    big_mult_n.operation = 'MULTIPLY'
    big_mult_n.inputs[1].default_value = 1.055

    big_sub_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    big_sub_n.name = big_sub_n.label = _BIG_SUBTRACT_NODE
    big_sub_n.location = (start_pos_x + pos_x_shift * 3, -200)
    big_sub_n.operation = 'SUBTRACT'
    big_sub_n.inputs[1].default_value = 0.055

    is_small_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    is_small_n.name = is_small_n.label = _IS_SMALL_NODE
    is_small_n.location = (start_pos_x + pos_x_shift * 4, 400)
    is_small_n.operation = 'LESS_THAN'
    is_small_n.inputs[1].default_value = 0.0031308

    is_big_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    is_big_n.name = is_big_n.label = _IS_BIG_NODE
    is_big_n.location = (start_pos_x + pos_x_shift * 4, 0)
    is_big_n.operation = 'GREATER_THAN'
    is_big_n.inputs[1].default_value = 0.0031308

    small_factor_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    small_factor_n.name = small_factor_n.label = _SMALL_FACTOR_NODE
    small_factor_n.location = (start_pos_x + pos_x_shift * 5, 300)
    small_factor_n.operation = 'MULTIPLY'

    big_factor_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    big_factor_n.name = big_factor_n.label = _BIG_FACTOR_NODE
    big_factor_n.location = (start_pos_x + pos_x_shift * 5, -100)
    big_factor_n.operation = 'MULTIPLY'

    final_mix_n = lin_to_srgb_g.nodes.new("ShaderNodeMath")
    final_mix_n.name = final_mix_n.label = _FINAL_MIX_NODE
    final_mix_n.location = (start_pos_x + pos_x_shift * 6, 0)
    final_mix_n.operation = 'ADD'

    # group links
    # pass: 1
    lin_to_srgb_g.links.new(big_pow_n.inputs[0], input_n.outputs['Value'])

    # pass: 2
    lin_to_srgb_g.links.new(big_mult_n.inputs[0], big_pow_n.outputs['Value'])

    # pass: 3
    lin_to_srgb_g.links.new(small_mult_n.inputs[0], input_n.outputs['Value'])
    lin_to_srgb_g.links.new(big_sub_n.inputs[0], big_mult_n.outputs['Value'])

    # pass: 4
    lin_to_srgb_g.links.new(is_small_n.inputs[0], input_n.outputs['Value'])
    lin_to_srgb_g.links.new(is_big_n.inputs[0], input_n.outputs['Value'])

    # pass: 5
    lin_to_srgb_g.links.new(small_factor_n.inputs[0], is_small_n.outputs['Value'])
    lin_to_srgb_g.links.new(small_factor_n.inputs[1], small_mult_n.outputs['Value'])

    lin_to_srgb_g.links.new(big_factor_n.inputs[0], is_big_n.outputs['Value'])
    lin_to_srgb_g.links.new(big_factor_n.inputs[1], big_sub_n.outputs['Value'])

    # pass: 6
    lin_to_srgb_g.links.new(final_mix_n.inputs[0], small_factor_n.outputs['Value'])
    lin_to_srgb_g.links.new(final_mix_n.inputs[1], big_factor_n.outputs['Value'])

    # pass: out
    lin_to_srgb_g.links.new(output_n.inputs['Value'], final_mix_n.outputs['Value'])
