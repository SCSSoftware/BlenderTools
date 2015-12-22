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

WINDOW_UV_FACTOR_G = _MAT_consts.node_group_prefix + "WindowUVFactorGroup"


def get_node_group():
    """Gets node group for calculation of uv change factor.
    For more information take a look at: eut2.window.cg

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if WINDOW_UV_FACTOR_G not in bpy.data.node_groups:
        __create_uv_factor_group__()

    return bpy.data.node_groups[WINDOW_UV_FACTOR_G]


def __create_uv_factor_group__():
    """Create UV factor group.

    Inputs: UV, Factor
    Outputs: UV Offset
    """

    pos_x_shift = 185

    uv_factor_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=WINDOW_UV_FACTOR_G)

    # inputs defining
    uv_factor_g.inputs.new("NodeSocketFloat", "UV")
    uv_factor_g.inputs.new("NodeSocketFloat", "Factor")
    input_n = uv_factor_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    uv_factor_g.outputs.new("NodeSocketFloat", "UV Offset")
    output_n = uv_factor_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 6, 0)

    # group nodes
    # FLOOR = floor(uv * 0.5)
    half_scale_n = uv_factor_g.nodes.new("ShaderNodeMath")
    half_scale_n.location = (pos_x_shift * 1, 100)
    half_scale_n.operation = "MULTIPLY"
    half_scale_n.inputs[1].default_value = 0.5

    floor_add_n = uv_factor_g.nodes.new("ShaderNodeMath")
    floor_add_n.location = (pos_x_shift * 2, 100)
    floor_add_n.operation = "ADD"
    floor_add_n.inputs[1].default_value = -0.5

    floor_round_n = uv_factor_g.nodes.new("ShaderNodeMath")
    floor_round_n.location = (pos_x_shift * 3, 100)
    floor_round_n.operation = "ROUND"

    # MIN_MAX_FACTOR = min_max(factor * (-1.333))
    factor_expand_n = uv_factor_g.nodes.new("ShaderNodeMath")
    factor_expand_n.location = (pos_x_shift * 1, -100)
    factor_expand_n.operation = "MULTIPLY"
    factor_expand_n.inputs[1].default_value = -1.333

    max_factor_n = uv_factor_g.nodes.new("ShaderNodeMath")
    max_factor_n.location = (pos_x_shift * 2, -100)
    max_factor_n.operation = "MAXIMUM"
    max_factor_n.inputs[1].default_value = -1.0

    min_factor_n = uv_factor_g.nodes.new("ShaderNodeMath")
    min_factor_n.location = (pos_x_shift * 3, -100)
    min_factor_n.operation = "MINIMUM"
    min_factor_n.inputs[1].default_value = 1.0

    # 1/512 * FLOOR * MIN_MAX_FACTOR
    offset_step_n = uv_factor_g.nodes.new("ShaderNodeMath")
    offset_step_n.location = (pos_x_shift * 3, 300)
    offset_step_n.operation = "DIVIDE"
    offset_step_n.inputs[0].default_value = 1
    offset_step_n.inputs[1].default_value = 512

    mult1_n = uv_factor_g.nodes.new("ShaderNodeMath")
    mult1_n.location = (pos_x_shift * 4, 200)
    mult1_n.operation = "MULTIPLY"

    mult2_n = uv_factor_g.nodes.new("ShaderNodeMath")
    mult2_n.location = (pos_x_shift * 5, 0)
    mult2_n.operation = "MULTIPLY"

    # group links
    # formula: 1/512 * floor(uv * 0.5) * min_max(factor * -1.333)
    uv_factor_g.links.new(half_scale_n.inputs[0], input_n.outputs['UV'])
    uv_factor_g.links.new(factor_expand_n.inputs[0], input_n.outputs['Factor'])

    uv_factor_g.links.new(floor_add_n.inputs[0], half_scale_n.outputs[0])
    uv_factor_g.links.new(max_factor_n.inputs[0], factor_expand_n.outputs[0])

    uv_factor_g.links.new(floor_round_n.inputs[0], floor_add_n.outputs[0])
    uv_factor_g.links.new(min_factor_n.inputs[0], max_factor_n.outputs[0])

    uv_factor_g.links.new(mult1_n.inputs[0], offset_step_n.outputs[0])
    uv_factor_g.links.new(mult1_n.inputs[1], floor_round_n.outputs[0])

    uv_factor_g.links.new(mult2_n.inputs[0], mult1_n.outputs[0])
    uv_factor_g.links.new(mult2_n.inputs[1], min_factor_n.outputs[0])

    uv_factor_g.links.new(output_n.inputs[0], mult2_n.outputs[0])
