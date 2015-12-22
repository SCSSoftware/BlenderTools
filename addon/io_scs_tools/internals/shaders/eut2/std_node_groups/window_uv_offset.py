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
from io_scs_tools.internals.shaders.eut2.std_node_groups import window_uv_factor

WINDOW_UV_OFFSET_G = _MAT_consts.node_group_prefix + "WindowUVOffsetGroup"


def get_node_group():
    """Gets node group for uv offseting based on view angle.
    For more information take a look at: eut2.window.cg

    NOTE: Due to lack of data view angle is calclulated
    based on normal of the mesh face.
    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if WINDOW_UV_OFFSET_G not in bpy.data.node_groups:
        __create_uv_offset_group__()

    return bpy.data.node_groups[WINDOW_UV_OFFSET_G]


def __create_uv_offset_group__():
    """Create UV factor group.

    Inputs: UV, Normal
    Outputs: UV Final
    """

    pos_x_shift = 185

    uv_offset_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=WINDOW_UV_OFFSET_G)

    # inputs defining
    uv_offset_g.inputs.new("NodeSocketVector", "UV")
    uv_offset_g.inputs.new("NodeSocketVector", "Normal")
    input_n = uv_offset_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    uv_offset_g.outputs.new("NodeSocketVector", "UV Final")
    output_n = uv_offset_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 14, 0)

    # group nodes
    separate_normal_n = uv_offset_g.nodes.new("ShaderNodeSeparateRGB")
    separate_normal_n.location = (pos_x_shift * 1, 100)

    combine_normal_n = uv_offset_g.nodes.new("ShaderNodeCombineRGB")
    combine_normal_n.location = (pos_x_shift * 2, -100)
    combine_normal_n.inputs[1].default_value = 0.0
    combine_normal_n.inputs[2].default_value = 0.0

    normal_cross_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    normal_cross_n.location = (pos_x_shift * 3, -100)
    normal_cross_n.operation = "CROSS_PRODUCT"

    separate_cross_n = uv_offset_g.nodes.new("ShaderNodeSeparateRGB")
    separate_cross_n.location = (pos_x_shift * 4, -100)

    inv_cross_z_n = uv_offset_g.nodes.new("ShaderNodeMath")
    inv_cross_z_n.location = (pos_x_shift * 5, -200)
    inv_cross_z_n.operation = "MULTIPLY"
    inv_cross_z_n.inputs[1].default_value = -1.0

    gt_normal_y_n = uv_offset_g.nodes.new("ShaderNodeMath")
    gt_normal_y_n.location = (pos_x_shift * 5, -400)
    gt_normal_y_n.operation = "GREATER_THAN"
    gt_normal_y_n.inputs[1].default_value = 0.0

    lt_normal_y_n = uv_offset_g.nodes.new("ShaderNodeMath")
    lt_normal_y_n.location = (pos_x_shift * 5, -600)
    lt_normal_y_n.operation = "LESS_THAN"
    lt_normal_y_n.inputs[1].default_value = 0.0

    max_cross_z_n = uv_offset_g.nodes.new("ShaderNodeMath")
    max_cross_z_n.location = (pos_x_shift * 6, -100)
    max_cross_z_n.operation = "MAXIMUM"

    mult_gt_n = uv_offset_g.nodes.new("ShaderNodeMath")
    mult_gt_n.location = (pos_x_shift * 7, -200)
    mult_gt_n.operation = "MULTIPLY"

    mult_lt_n = uv_offset_g.nodes.new("ShaderNodeMath")
    mult_lt_n.location = (pos_x_shift * 7, -400)
    mult_lt_n.operation = "MULTIPLY"

    inv_mult_gt_n = uv_offset_g.nodes.new("ShaderNodeMath")
    inv_mult_gt_n.location = (pos_x_shift * 8, -200)
    inv_mult_gt_n.operation = "MULTIPLY"
    inv_mult_gt_n.inputs[1].default_value = -1.0

    sum_lt_gt_n = uv_offset_g.nodes.new("ShaderNodeMath")
    sum_lt_gt_n.location = (pos_x_shift * 9, -300)
    sum_lt_gt_n.operation = "ADD"

    inv_y_factor_n = uv_offset_g.nodes.new("ShaderNodeMath")
    inv_y_factor_n.location = (pos_x_shift * 10, -300)
    inv_y_factor_n.operation = "MULTIPLY"
    inv_y_factor_n.inputs[1].default_value = -1.0

    separate_uv_n = uv_offset_g.nodes.new("ShaderNodeSeparateRGB")
    separate_uv_n.location = (pos_x_shift * 10, 100)

    u_factor_gn = uv_offset_g.nodes.new("ShaderNodeGroup")
    u_factor_gn.name = window_uv_factor.WINDOW_UV_FACTOR_G
    u_factor_gn.label = window_uv_factor.WINDOW_UV_FACTOR_G
    u_factor_gn.location = (pos_x_shift * 11, 300)
    u_factor_gn.node_tree = window_uv_factor.get_node_group()

    v_factor_gn = uv_offset_g.nodes.new("ShaderNodeGroup")
    v_factor_gn.name = window_uv_factor.WINDOW_UV_FACTOR_G
    v_factor_gn.label = window_uv_factor.WINDOW_UV_FACTOR_G
    v_factor_gn.location = (pos_x_shift * 11, -100)
    v_factor_gn.node_tree = window_uv_factor.get_node_group()

    combine_uv_n = uv_offset_g.nodes.new("ShaderNodeCombineRGB")
    combine_uv_n.location = (pos_x_shift * 12, 100)
    combine_uv_n.inputs[2].default_value = 0.0

    add_offset_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    add_offset_n.location = (pos_x_shift * 13, 100)
    add_offset_n.operation = "ADD"

    # group links
    uv_offset_g.links.new(separate_normal_n.inputs[0], input_n.outputs["Normal"])

    uv_offset_g.links.new(combine_normal_n.inputs[0], separate_normal_n.outputs[0])

    uv_offset_g.links.new(normal_cross_n.inputs[0], combine_normal_n.outputs[0])
    uv_offset_g.links.new(normal_cross_n.inputs[1], input_n.outputs["Normal"])

    uv_offset_g.links.new(separate_cross_n.inputs[0], normal_cross_n.outputs[0])

    uv_offset_g.links.new(inv_cross_z_n.inputs[0], separate_cross_n.outputs[2])
    uv_offset_g.links.new(gt_normal_y_n.inputs[0], separate_normal_n.outputs[1])
    uv_offset_g.links.new(lt_normal_y_n.inputs[0], separate_normal_n.outputs[1])

    uv_offset_g.links.new(max_cross_z_n.inputs[0], separate_cross_n.outputs[2])
    uv_offset_g.links.new(max_cross_z_n.inputs[1], inv_cross_z_n.outputs[0])

    uv_offset_g.links.new(mult_gt_n.inputs[0], max_cross_z_n.outputs[0])
    uv_offset_g.links.new(mult_gt_n.inputs[1], gt_normal_y_n.outputs[0])
    uv_offset_g.links.new(mult_lt_n.inputs[0], max_cross_z_n.outputs[0])
    uv_offset_g.links.new(mult_lt_n.inputs[1], lt_normal_y_n.outputs[0])

    uv_offset_g.links.new(inv_mult_gt_n.inputs[0], mult_gt_n.outputs[0])

    uv_offset_g.links.new(sum_lt_gt_n.inputs[0], inv_mult_gt_n.outputs[0])
    uv_offset_g.links.new(sum_lt_gt_n.inputs[1], mult_lt_n.outputs[0])

    uv_offset_g.links.new(separate_uv_n.inputs[0], input_n.outputs["UV"])
    uv_offset_g.links.new(inv_y_factor_n.inputs[0], sum_lt_gt_n.outputs[0])

    uv_offset_g.links.new(u_factor_gn.inputs["UV"], separate_uv_n.outputs[0])
    uv_offset_g.links.new(u_factor_gn.inputs["Factor"], separate_normal_n.outputs[0])
    uv_offset_g.links.new(v_factor_gn.inputs["UV"], separate_uv_n.outputs[1])
    uv_offset_g.links.new(v_factor_gn.inputs["Factor"], inv_y_factor_n.outputs[0])

    uv_offset_g.links.new(combine_uv_n.inputs[0], u_factor_gn.outputs["UV Offset"])
    uv_offset_g.links.new(combine_uv_n.inputs[1], v_factor_gn.outputs["UV Offset"])

    uv_offset_g.links.new(add_offset_n.inputs[0], combine_uv_n.outputs[0])
    uv_offset_g.links.new(add_offset_n.inputs[1], input_n.outputs["UV"])

    uv_offset_g.links.new(output_n.inputs["UV Final"], add_offset_n.outputs[0])
