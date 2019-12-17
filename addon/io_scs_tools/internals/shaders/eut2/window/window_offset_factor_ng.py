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

import bpy
from io_scs_tools.consts import Material as _MAT_consts

WINDOW_OFFSET_FACTOR_G = _MAT_consts.node_group_prefix + "WindowOffsetFactor"


def get_node_group():
    """Gets node group for calculation of uv offset factor.
    For more information take a look at: eut2.window.cg

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if WINDOW_OFFSET_FACTOR_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[WINDOW_OFFSET_FACTOR_G]


def __create_node_group__():
    """Create offset factor calculation group.

    Inputs: WndToEye Direction, WndToEye Up
    Outputs: Offset Factor
    """

    pos_x_shift = 185

    offset_factor_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=WINDOW_OFFSET_FACTOR_G)

    # inputs defining
    offset_factor_g.inputs.new("NodeSocketFloat", "WndToEye Up")
    offset_factor_g.inputs.new("NodeSocketFloat", "WndToEye Direction")
    input_n = offset_factor_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    offset_factor_g.outputs.new("NodeSocketFloat", "Offset Factor")
    output_n = offset_factor_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 6, 0)

    # group nodes
    # ANGLE_TO_ROTATION = saturate(acos(WndToEyeUp))
    arcos_n = offset_factor_g.nodes.new("ShaderNodeMath")
    arcos_n.location = (pos_x_shift * 1, 200)
    arcos_n.operation = "ARCCOSINE"
    arcos_n.use_clamp = True

    # SIGN = -sign(WndToEyeDirection)
    sign_gt_n = offset_factor_g.nodes.new("ShaderNodeMath")
    sign_gt_n.location = (pos_x_shift * 1, 0)
    sign_gt_n.operation = "GREATER_THAN"
    sign_gt_n.inputs[1].default_value = 0.0

    sign_lt_n = offset_factor_g.nodes.new("ShaderNodeMath")
    sign_lt_n.location = (pos_x_shift * 1, -200)
    sign_lt_n.operation = "LESS_THAN"
    sign_lt_n.inputs[1].default_value = 0.0

    sign_gt_mult_n = offset_factor_g.nodes.new("ShaderNodeMath")
    sign_gt_mult_n.location = (pos_x_shift * 2, 0)
    sign_gt_mult_n.operation = "MULTIPLY"
    sign_gt_mult_n.inputs[1].default_value = 1.0

    sign_lt_mult_n = offset_factor_g.nodes.new("ShaderNodeMath")
    sign_lt_mult_n.location = (pos_x_shift * 2, -200)
    sign_lt_mult_n.operation = "MULTIPLY"
    sign_lt_mult_n.inputs[1].default_value = -1.0

    final_sign_n = offset_factor_g.nodes.new("ShaderNodeMath")
    final_sign_n.location = (pos_x_shift * 3, -100)
    final_sign_n.operation = "ADD"

    # FINAL_FACTOR = SIGN * ANGLE_TO_ROTATION
    final_factor_n = offset_factor_g.nodes.new("ShaderNodeMath")
    final_factor_n.location = (pos_x_shift * 5, 100)
    final_factor_n.operation = "MULTIPLY"

    # group links
    # formula: -sign(WndToEyeDirection) * angle_to_rotation(WndToEyeUp)
    offset_factor_g.links.new(arcos_n.inputs[0], input_n.outputs['WndToEye Up'])
    offset_factor_g.links.new(sign_gt_n.inputs[0], input_n.outputs['WndToEye Direction'])
    offset_factor_g.links.new(sign_lt_n.inputs[0], input_n.outputs['WndToEye Direction'])

    offset_factor_g.links.new(sign_gt_mult_n.inputs[0], sign_gt_n.outputs[0])
    offset_factor_g.links.new(sign_lt_mult_n.inputs[0], sign_lt_n.outputs[0])

    offset_factor_g.links.new(final_sign_n.inputs[0], sign_gt_mult_n.outputs[0])
    offset_factor_g.links.new(final_sign_n.inputs[1], sign_lt_mult_n.outputs[0])

    offset_factor_g.links.new(final_factor_n.inputs[0], arcos_n.outputs[0])
    offset_factor_g.links.new(final_factor_n.inputs[1], final_sign_n.outputs[0])

    offset_factor_g.links.new(output_n.inputs['Offset Factor'], final_factor_n.outputs[0])
