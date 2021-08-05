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
from io_scs_tools.internals.shaders.std_node_groups import animsheet_frame_idx_to_col_row_ng
from io_scs_tools.internals.shaders.std_node_groups import animsheet_loop_frame_ng
from io_scs_tools.consts import Material as _MAT_consts

ANIMSHEET_FRAME_G = _MAT_consts.node_group_prefix + "AnimsheetFrame"

_LOOP_FRAME_NODE = "LoopFrameNG"
_LOOP_FRAME_FLOORED_NODE = "LoopFrameFloored"
_FRAME_COL_ROW_NODE = "Frame0ColRowNG"


def get_node_group():
    """Gets node group.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ANIMSHEET_FRAME_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return ANIMSHEET_FRAME_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates animsheet frame calculation group.

    Outputs frame indices.

    Inputs: Float, Float, Float
    Outputs: Float, Float
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ANIMSHEET_FRAME_G not in bpy.data.node_groups:  # creation

        animsheet_xfade_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ANIMSHEET_FRAME_G)

    else:  # recreation

        animsheet_xfade_g = bpy.data.node_groups[ANIMSHEET_FRAME_G]

        # delete all inputs and outputs
        animsheet_xfade_g.inputs.clear()
        animsheet_xfade_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        animsheet_xfade_g.nodes.clear()

    # inputs defining
    animsheet_xfade_g.inputs.new("NodeSocketFloat", "FPS")
    animsheet_xfade_g.inputs.new("NodeSocketFloat", "FramesTotal")
    animsheet_xfade_g.inputs.new("NodeSocketFloat", "FramesRow")

    # outputs defining
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "FrameX")
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "FrameY")

    # node creation
    input_n = animsheet_xfade_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = animsheet_xfade_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)

    loop_frame_n = animsheet_xfade_g.nodes.new("ShaderNodeGroup")
    loop_frame_n.name = loop_frame_n.label = _LOOP_FRAME_NODE
    loop_frame_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y)
    loop_frame_n.node_tree = animsheet_loop_frame_ng.get_node_group()

    loop_frame_floored_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    loop_frame_floored_n.name = loop_frame_floored_n.label = _LOOP_FRAME_FLOORED_NODE
    loop_frame_floored_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 100)
    loop_frame_floored_n.operation = "FLOOR"

    frame_col_row_n = animsheet_xfade_g.nodes.new("ShaderNodeGroup")
    frame_col_row_n.name = frame_col_row_n.label = _FRAME_COL_ROW_NODE
    frame_col_row_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 100)
    frame_col_row_n.node_tree = animsheet_frame_idx_to_col_row_ng.get_node_group()

    # create links
    animsheet_xfade_g.links.new(loop_frame_n.inputs['FPS'], input_n.outputs['FPS'])
    animsheet_xfade_g.links.new(loop_frame_n.inputs['FramesTotal'], input_n.outputs['FramesTotal'])

    animsheet_xfade_g.links.new(loop_frame_floored_n.inputs[0], loop_frame_n.outputs[0])

    animsheet_xfade_g.links.new(frame_col_row_n.inputs['FrameIndex'], loop_frame_floored_n.outputs[0])
    animsheet_xfade_g.links.new(frame_col_row_n.inputs['FramesRow'], input_n.outputs['FramesRow'])

    # output
    animsheet_xfade_g.links.new(output_n.inputs['FrameX'], frame_col_row_n.outputs['ColIndex'])
    animsheet_xfade_g.links.new(output_n.inputs['FrameY'], frame_col_row_n.outputs['RowIndex'])
