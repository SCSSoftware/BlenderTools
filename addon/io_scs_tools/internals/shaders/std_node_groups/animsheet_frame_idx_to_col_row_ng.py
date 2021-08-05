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
from io_scs_tools.consts import Material as _MAT_consts

ANIMSHEET_FRAME_IDX_TO_COL_ROW_G = _MAT_consts.node_group_prefix + "AnimsheetFrameIndexToColRow"

_ROW_IDX_NODE = "RowIndex"
_ROW_IDX_FLOORED_NODE = "RowIndexFloored"
_FRAME_FLOORED_NODE = "FrameFloored"
_ROW_USED_FRAMES_NODE = "RowUsedFrames"
_COL_IDX_NODE = "ColIndex"


def get_node_group():
    """Gets node group.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ANIMSHEET_FRAME_IDX_TO_COL_ROW_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return ANIMSHEET_FRAME_IDX_TO_COL_ROW_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates animsheet frame index to column and row group.

    Outputs column and row index in the anim sheet from frame index and frames per row paramters.

    Inputs: Float, Float
    Outputs: Float, Float
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ANIMSHEET_FRAME_IDX_TO_COL_ROW_G not in bpy.data.node_groups:  # creation

        animsheet_frame_idx_to_col_row_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ANIMSHEET_FRAME_IDX_TO_COL_ROW_G)

    else:  # recreation

        animsheet_frame_idx_to_col_row_g = bpy.data.node_groups[ANIMSHEET_FRAME_IDX_TO_COL_ROW_G]

        # delete all inputs and outputs
        animsheet_frame_idx_to_col_row_g.inputs.clear()
        animsheet_frame_idx_to_col_row_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        animsheet_frame_idx_to_col_row_g.nodes.clear()

    # inputs defining
    animsheet_frame_idx_to_col_row_g.inputs.new("NodeSocketFloat", "FrameIndex")
    animsheet_frame_idx_to_col_row_g.inputs.new("NodeSocketFloat", "FramesRow")

    # outputs defining
    animsheet_frame_idx_to_col_row_g.outputs.new("NodeSocketFloat", "ColIndex")
    animsheet_frame_idx_to_col_row_g.outputs.new("NodeSocketFloat", "RowIndex")

    # node creation
    input_n = animsheet_frame_idx_to_col_row_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = animsheet_frame_idx_to_col_row_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    row_idx_n = animsheet_frame_idx_to_col_row_g.nodes.new("ShaderNodeMath")
    row_idx_n.name = row_idx_n.label = _ROW_IDX_NODE
    row_idx_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y + 200)
    row_idx_n.operation = "DIVIDE"

    row_idx_floored_n = animsheet_frame_idx_to_col_row_g.nodes.new("ShaderNodeMath")
    row_idx_floored_n.name = row_idx_floored_n.label = _ROW_IDX_FLOORED_NODE
    row_idx_floored_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y)
    row_idx_floored_n.operation = "FLOOR"

    frame_floored_n = animsheet_frame_idx_to_col_row_g.nodes.new("ShaderNodeMath")
    frame_floored_n.name = frame_floored_n.label = _FRAME_FLOORED_NODE
    frame_floored_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)
    frame_floored_n.operation = "FLOOR"

    row_used_frames_n = animsheet_frame_idx_to_col_row_g.nodes.new("ShaderNodeMath")
    row_used_frames_n.name = row_used_frames_n.label = _ROW_USED_FRAMES_NODE
    row_used_frames_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)
    row_used_frames_n.operation = "MULTIPLY"

    col_idx_n = animsheet_frame_idx_to_col_row_g.nodes.new("ShaderNodeMath")
    col_idx_n.name = col_idx_n.label = _COL_IDX_NODE
    col_idx_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y)
    col_idx_n.operation = "SUBTRACT"

    # create links
    animsheet_frame_idx_to_col_row_g.links.new(row_idx_n.inputs[0], input_n.outputs['FrameIndex'])
    animsheet_frame_idx_to_col_row_g.links.new(row_idx_n.inputs[1], input_n.outputs['FramesRow'])

    animsheet_frame_idx_to_col_row_g.links.new(row_idx_floored_n.inputs[0], row_idx_n.outputs[0])

    animsheet_frame_idx_to_col_row_g.links.new(frame_floored_n.inputs[0], input_n.outputs['FrameIndex'])

    animsheet_frame_idx_to_col_row_g.links.new(row_used_frames_n.inputs[0], row_idx_floored_n.outputs[0])
    animsheet_frame_idx_to_col_row_g.links.new(row_used_frames_n.inputs[1], input_n.outputs['FramesRow'])

    animsheet_frame_idx_to_col_row_g.links.new(col_idx_n.inputs[0], frame_floored_n.outputs[0])
    animsheet_frame_idx_to_col_row_g.links.new(col_idx_n.inputs[1], row_used_frames_n.outputs[0])

    animsheet_frame_idx_to_col_row_g.links.new(output_n.inputs['ColIndex'], col_idx_n.outputs[0])
    animsheet_frame_idx_to_col_row_g.links.new(output_n.inputs['RowIndex'], row_idx_floored_n.outputs[0])
