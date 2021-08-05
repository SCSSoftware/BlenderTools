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

ANIMSHEET_XFADE_G = _MAT_consts.node_group_prefix + "AnimsheetXFade"

_LOOP_FRAME_NODE = "LoopFrameNG"
_FRAME0_FROM_FRAME1_NODE = "Frame1-1"
_FRAME0_NODE = "Frame0"
_FRAME1_NODE = "Frame1"
_FRAME_BLEND_FRAC_NODE = "FrameBlendFrac"
_FRAME_BLEND_NODE = "FrameBlend"
_FRAME0_COL_ROW_NODE = "Frame0ColRowNG"
_FRAME1_COL_ROW_NODE = "Frame1ColRowNG"


def get_node_group():
    """Gets node group.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ANIMSHEET_XFADE_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return ANIMSHEET_XFADE_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates animsheet cross fade sheet indices calculation group.

    Outputs cross fade sheet indices for both frames and blending factor between them.

    Inputs: Float, Float, Float
    Outputs: Float, Float, Float
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ANIMSHEET_XFADE_G not in bpy.data.node_groups:  # creation

        animsheet_xfade_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ANIMSHEET_XFADE_G)

    else:  # recreation

        animsheet_xfade_g = bpy.data.node_groups[ANIMSHEET_XFADE_G]

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
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "Frame0X")
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "Frame0Y")
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "Frame1X")
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "Frame1Y")
    animsheet_xfade_g.outputs.new("NodeSocketFloat", "FrameBlend")

    # node creation
    input_n = animsheet_xfade_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = animsheet_xfade_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y)

    loop_frame_n = animsheet_xfade_g.nodes.new("ShaderNodeGroup")
    loop_frame_n.name = loop_frame_n.label = _LOOP_FRAME_NODE
    loop_frame_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y)
    loop_frame_n.node_tree = animsheet_loop_frame_ng.get_node_group()

    frame1_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    frame1_n.name = frame1_n.label = _FRAME1_NODE
    frame1_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 100)
    frame1_n.operation = "FLOOR"

    frame0_from_frame1_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    frame0_from_frame1_n.name = frame0_from_frame1_n.label = _FRAME0_FROM_FRAME1_NODE
    frame0_from_frame1_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 100)
    frame0_from_frame1_n.operation = "SUBTRACT"
    frame0_from_frame1_n.inputs[1].default_value = 1.0

    frame0_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    frame0_n.name = frame0_n.label = _FRAME0_NODE
    frame0_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 100)
    frame0_n.operation = "WRAP"
    frame0_n.inputs[1].default_value = 0.0  # minimum

    frame_blend_frac_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    frame_blend_frac_n.name = frame_blend_frac_n.label = _FRAME_BLEND_FRAC_NODE
    frame_blend_frac_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y - 300)
    frame_blend_frac_n.operation = "FRACT"

    frame_blend_n = animsheet_xfade_g.nodes.new("ShaderNodeMath")
    frame_blend_n.name = frame_blend_n.label = _FRAME_BLEND_FRAC_NODE
    frame_blend_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y - 300)
    frame_blend_n.operation = "MULTIPLY"
    frame_blend_n.inputs[1].default_value = 2.0
    frame_blend_n.use_clamp = True

    frame0_col_row_n = animsheet_xfade_g.nodes.new("ShaderNodeGroup")
    frame0_col_row_n.name = frame0_col_row_n.label = _FRAME0_COL_ROW_NODE
    frame0_col_row_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 100)
    frame0_col_row_n.node_tree = animsheet_frame_idx_to_col_row_ng.get_node_group()

    frame1_col_row_n = animsheet_xfade_g.nodes.new("ShaderNodeGroup")
    frame1_col_row_n.name = frame1_col_row_n.label = _FRAME1_COL_ROW_NODE
    frame1_col_row_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y - 100)
    frame1_col_row_n.node_tree = animsheet_frame_idx_to_col_row_ng.get_node_group()

    # create links
    # loop frame
    animsheet_xfade_g.links.new(loop_frame_n.inputs['FPS'], input_n.outputs['FPS'])
    animsheet_xfade_g.links.new(loop_frame_n.inputs['FramesTotal'], input_n.outputs['FramesTotal'])

    # frame1
    animsheet_xfade_g.links.new(frame1_n.inputs[0], loop_frame_n.outputs[0])

    # frame0
    animsheet_xfade_g.links.new(frame0_from_frame1_n.inputs[0], frame1_n.outputs[0])

    animsheet_xfade_g.links.new(frame0_n.inputs[0], frame0_from_frame1_n.outputs[0])  # value
    animsheet_xfade_g.links.new(frame0_n.inputs[2], input_n.outputs['FramesTotal'])  # maximum

    # frame_blend
    animsheet_xfade_g.links.new(frame_blend_frac_n.inputs[0], loop_frame_n.outputs['LoopFrame'])

    animsheet_xfade_g.links.new(frame_blend_n.inputs[0], frame_blend_frac_n.outputs[0])

    # frame0 col row
    animsheet_xfade_g.links.new(frame0_col_row_n.inputs['FrameIndex'], frame0_n.outputs[0])
    animsheet_xfade_g.links.new(frame0_col_row_n.inputs['FramesRow'], input_n.outputs['FramesRow'])

    # frame1 col row
    animsheet_xfade_g.links.new(frame1_col_row_n.inputs['FrameIndex'], frame1_n.outputs[0])
    animsheet_xfade_g.links.new(frame1_col_row_n.inputs['FramesRow'], input_n.outputs['FramesRow'])

    # output
    animsheet_xfade_g.links.new(output_n.inputs['Frame0X'], frame0_col_row_n.outputs['ColIndex'])
    animsheet_xfade_g.links.new(output_n.inputs['Frame0Y'], frame0_col_row_n.outputs['RowIndex'])

    animsheet_xfade_g.links.new(output_n.inputs['Frame1X'], frame1_col_row_n.outputs['ColIndex'])
    animsheet_xfade_g.links.new(output_n.inputs['Frame1Y'], frame1_col_row_n.outputs['RowIndex'])

    animsheet_xfade_g.links.new(output_n.inputs['FrameBlend'], frame_blend_n.outputs[0])
