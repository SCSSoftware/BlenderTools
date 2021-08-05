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

# Copyright (C) 2021: SCS Software

import bpy
from io_scs_tools.internals.shaders.std_node_groups import animsheet_xfade_ng
from io_scs_tools.consts import Material as _MAT_consts

FADESHEET_COMPUTE_G = _MAT_consts.node_group_prefix + "FadesheetCompute"

_XFADE_NODE = "SheetXFade"

_FRAMEX_COMBINE_NODE_PREFIX = "FrameCombine"
_FRAMEX_MULT_Y_NODE_PREFIX = "Frame*-Y"
_FRAMEX_MULT_SIZE_NODE_PREFIX = "Frame*-Y*FrameSize"
_FRAMEX_UV_ADD_NODE_PREFIX = "UV+(Frame-Y*FrameSize)"


def get_node_group():
    """Gets node group.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[FADESHEET_COMPUTE_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return FADESHEET_COMPUTE_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates group for computing of fadesheet frames and transforming UVs.

    Inputs: Float, Float, Float, Vector, Vector
    Outputs: Vector, Vector, Float
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if FADESHEET_COMPUTE_G not in bpy.data.node_groups:  # creation

        fadesheet_compute_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=FADESHEET_COMPUTE_G)

    else:  # recreation

        fadesheet_compute_g = bpy.data.node_groups[FADESHEET_COMPUTE_G]

        # delete all inputs and outputs
        fadesheet_compute_g.inputs.clear()
        fadesheet_compute_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        fadesheet_compute_g.nodes.clear()

    # inputs defining
    fadesheet_compute_g.inputs.new("NodeSocketFloat", "FPS")
    fadesheet_compute_g.inputs.new("NodeSocketFloat", "FramesRow")
    fadesheet_compute_g.inputs.new("NodeSocketFloat", "FramesTotal")
    fadesheet_compute_g.inputs.new("NodeSocketVector", "FrameSize")
    fadesheet_compute_g.inputs.new("NodeSocketVector", "UV")

    # outputs defining
    fadesheet_compute_g.outputs.new("NodeSocketVector", "UV0")
    fadesheet_compute_g.outputs.new("NodeSocketVector", "UV1")
    fadesheet_compute_g.outputs.new("NodeSocketFloat", "FrameBlend")

    # node creation
    input_n = fadesheet_compute_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = fadesheet_compute_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    xfade_node = fadesheet_compute_g.nodes.new("ShaderNodeGroup")
    xfade_node.name = xfade_node.label = _XFADE_NODE
    xfade_node.location = (start_pos_x + pos_x_shift * 1, start_pos_y)
    xfade_node.node_tree = animsheet_xfade_ng.get_node_group()

    for frame_idx in (0, 1):
        frame_combine_n = fadesheet_compute_g.nodes.new("ShaderNodeCombineXYZ")
        frame_combine_n.name = frame_combine_n.label = _FRAMEX_COMBINE_NODE_PREFIX + str(frame_idx)
        frame_combine_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 200 * frame_idx)
        frame_combine_n.inputs['Z'].default_value = 0.0

        frame_mult_y_n = fadesheet_compute_g.nodes.new("ShaderNodeVectorMath")
        frame_mult_y_n.name = frame_mult_y_n.label = _FRAMEX_MULT_Y_NODE_PREFIX + str(frame_idx)
        frame_mult_y_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y - 200 * frame_idx)
        frame_mult_y_n.operation = "MULTIPLY"
        frame_mult_y_n.inputs[1].default_value = (1.0, -1.0, 0.0)

        frame_mult_size_n = fadesheet_compute_g.nodes.new("ShaderNodeVectorMath")
        frame_mult_size_n.name = frame_mult_size_n.label = _FRAMEX_MULT_SIZE_NODE_PREFIX + str(frame_idx)
        frame_mult_size_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y - 200 * frame_idx)
        frame_mult_size_n.operation = "MULTIPLY"

        frame_uv_add_n = fadesheet_compute_g.nodes.new("ShaderNodeVectorMath")
        frame_uv_add_n.name = frame_uv_add_n.label = _FRAMEX_UV_ADD_NODE_PREFIX + str(frame_idx)
        frame_uv_add_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y - 200 * frame_idx)
        frame_uv_add_n.operation = "ADD"

    # create links
    fadesheet_compute_g.links.new(xfade_node.inputs['FPS'], input_n.outputs['FPS'])
    fadesheet_compute_g.links.new(xfade_node.inputs['FramesTotal'], input_n.outputs['FramesTotal'])
    fadesheet_compute_g.links.new(xfade_node.inputs['FramesRow'], input_n.outputs['FramesRow'])

    for frame_idx in (0, 1):
        frame_combine_n = fadesheet_compute_g.nodes[_FRAMEX_COMBINE_NODE_PREFIX + str(frame_idx)]
        frame_mult_y_n = fadesheet_compute_g.nodes[_FRAMEX_MULT_Y_NODE_PREFIX + str(frame_idx)]
        frame_mult_size_n = fadesheet_compute_g.nodes[_FRAMEX_MULT_SIZE_NODE_PREFIX + str(frame_idx)]
        frame_uv_add_n = fadesheet_compute_g.nodes[_FRAMEX_UV_ADD_NODE_PREFIX + str(frame_idx)]

        fadesheet_compute_g.links.new(frame_combine_n.inputs['X'], xfade_node.outputs['Frame' + str(frame_idx) + 'X'])
        fadesheet_compute_g.links.new(frame_combine_n.inputs['Y'], xfade_node.outputs['Frame' + str(frame_idx) + 'Y'])

        fadesheet_compute_g.links.new(frame_mult_y_n.inputs[0], frame_combine_n.outputs[0])

        fadesheet_compute_g.links.new(frame_mult_size_n.inputs[0], frame_mult_y_n.outputs[0])
        fadesheet_compute_g.links.new(frame_mult_size_n.inputs[1], input_n.outputs['FrameSize'])

        fadesheet_compute_g.links.new(frame_uv_add_n.inputs[0], frame_mult_size_n.outputs[0])
        fadesheet_compute_g.links.new(frame_uv_add_n.inputs[1], input_n.outputs['UV'])

        fadesheet_compute_g.links.new(output_n.inputs['UV' + str(frame_idx)], frame_uv_add_n.outputs[0])

    fadesheet_compute_g.links.new(output_n.inputs['FrameBlend'], xfade_node.outputs['FrameBlend'])
