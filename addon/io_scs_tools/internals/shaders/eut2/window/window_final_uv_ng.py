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

WINDOW_FINAL_UV_G = _MAT_consts.node_group_prefix + "WindowFinalUV"


def get_node_group():
    """Gets node group for calculation of final uvs.
    For more information take a look at: eut2.window.cg

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if WINDOW_FINAL_UV_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[WINDOW_FINAL_UV_G]


def __create_node_group__():
    """Create final UV calculation group.

    Inputs: UV, Factor
    Outputs: Final UV
    """

    pos_x_shift = 185

    final_uv_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=WINDOW_FINAL_UV_G)

    # inputs defining
    final_uv_g.inputs.new("NodeSocketFloat", "UV")
    final_uv_g.inputs.new("NodeSocketFloat", "Factor")
    input_n = final_uv_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    final_uv_g.outputs.new("NodeSocketFloat", "Final UV")
    output_n = final_uv_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 6, 0)

    # group nodes
    # UV_STEPS = floor(uv * 0.5)
    half_scale_n = final_uv_g.nodes.new("ShaderNodeMath")
    half_scale_n.location = (pos_x_shift * 1, 150)
    half_scale_n.operation = "MULTIPLY"
    half_scale_n.inputs[1].default_value = 0.5

    floor_n = final_uv_g.nodes.new("ShaderNodeMath")
    floor_n.location = (pos_x_shift * 2, 150)
    floor_n.operation = "FLOOR"

    # OFFSET_STEP = 1/512 * UV_STEPS
    offset_step_n = final_uv_g.nodes.new("ShaderNodeMath")
    offset_step_n.location = (pos_x_shift * 3, 150)
    offset_step_n.operation = "MULTIPLY"
    offset_step_n.inputs[1].default_value = 1.0 / 512.0

    # FINAL_OFFSET = OFFSET_STEP * FACTOR
    final_offset_n = final_uv_g.nodes.new("ShaderNodeMath")
    final_offset_n.location = (pos_x_shift * 4, -100)
    final_offset_n.operation = "MULTIPLY"

    # FINAL_UVS = FINAL_OFFSET + UV
    final_uvs_n = final_uv_g.nodes.new("ShaderNodeMath")
    final_uvs_n.location = (pos_x_shift * 5, 50)
    final_uvs_n.operation = "ADD"

    # group links
    # formula: floor(uv * 0.5) * 1/512 * factor + uv
    final_uv_g.links.new(half_scale_n.inputs[0], input_n.outputs['UV'])

    final_uv_g.links.new(floor_n.inputs[0], half_scale_n.outputs[0])

    final_uv_g.links.new(offset_step_n.inputs[0], floor_n.outputs[0])

    final_uv_g.links.new(final_offset_n.inputs[0], offset_step_n.outputs[0])
    final_uv_g.links.new(final_offset_n.inputs[1], input_n.outputs['Factor'])

    final_uv_g.links.new(final_uvs_n.inputs[1], final_offset_n.outputs[0])
    final_uv_g.links.new(final_uvs_n.inputs[0], input_n.outputs['UV'])

    final_uv_g.links.new(output_n.inputs['Final UV'], final_uvs_n.outputs[0])
