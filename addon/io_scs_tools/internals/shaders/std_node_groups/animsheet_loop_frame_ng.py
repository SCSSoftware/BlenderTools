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

ANIMSHEET_LOOP_FRAME_G = _MAT_consts.node_group_prefix + "AnimsheetLoopFrame"

_GLOBAL_FRAME_OLD_NODE = "GlobalFrameOld"
_GLOBAL_FRAME_NODE = "GlobalFrame"
_LOOP_COUNT_NODE = "LoopCount"
_LOOP_COUNT_FLOORED_NODE = "LoopCountFloor"
_GLOBAL_FRAME_FLOORED_NODE = "GlobalFrameFloor"
_LOOP_FRAME_NODE = "LoopFrame"


def get_node_group():
    """Gets node group.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ANIMSHEET_LOOP_FRAME_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return ANIMSHEET_LOOP_FRAME_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates animsheet loop frame calculation group.

    Outputs loop frame index in the anim sheet

    Inputs: Float, Float
    Outputs: Float
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ANIMSHEET_LOOP_FRAME_G not in bpy.data.node_groups:  # creation

        animsheet_loop_frame_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ANIMSHEET_LOOP_FRAME_G)

    else:  # recreation

        animsheet_loop_frame_g = bpy.data.node_groups[ANIMSHEET_LOOP_FRAME_G]

        # delete all inputs and outputs
        animsheet_loop_frame_g.inputs.clear()
        animsheet_loop_frame_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        animsheet_loop_frame_g.nodes.clear()

    # inputs defining
    animsheet_loop_frame_g.inputs.new("NodeSocketFloat", "FPS")
    animsheet_loop_frame_g.inputs.new("NodeSocketFloat", "FramesTotal")

    # outputs defining
    animsheet_loop_frame_g.outputs.new("NodeSocketFloat", "LoopFrame")

    # node creation
    input_n = animsheet_loop_frame_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = animsheet_loop_frame_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    global_frame_old_n = animsheet_loop_frame_g.nodes.new("ShaderNodeValue")
    global_frame_old_n.name = global_frame_old_n.label = _GLOBAL_FRAME_OLD_NODE
    global_frame_old_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y + 400)

    global_frame_n = animsheet_loop_frame_g.nodes.new("ShaderNodeMath")
    global_frame_n.name = global_frame_n.label = _GLOBAL_FRAME_NODE
    global_frame_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y + 200)
    global_frame_n.operation = "MULTIPLY"

    loop_count_n = animsheet_loop_frame_g.nodes.new("ShaderNodeMath")
    loop_count_n.name = loop_count_n.label = _LOOP_COUNT_NODE
    loop_count_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y)
    loop_count_n.operation = "DIVIDE"

    loop_count_floored_n = animsheet_loop_frame_g.nodes.new("ShaderNodeMath")
    loop_count_floored_n.name = loop_count_floored_n.label = _LOOP_COUNT_FLOORED_NODE
    loop_count_floored_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)
    loop_count_floored_n.operation = "FLOOR"

    global_frame_floored_n = animsheet_loop_frame_g.nodes.new("ShaderNodeMath")
    global_frame_floored_n.name = global_frame_floored_n.label = _GLOBAL_FRAME_FLOORED_NODE
    global_frame_floored_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)
    global_frame_floored_n.operation = "MULTIPLY"

    loop_frame_n = animsheet_loop_frame_g.nodes.new("ShaderNodeMath")
    loop_frame_n.name = loop_frame_n.label = _LOOP_FRAME_NODE
    loop_frame_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y)
    loop_frame_n.operation = "SUBTRACT"

    # create extra links
    animsheet_loop_frame_g.links.new(global_frame_n.inputs[0], input_n.outputs['FPS'])

    animsheet_loop_frame_g.links.new(loop_count_n.inputs[0], global_frame_n.outputs[0])
    animsheet_loop_frame_g.links.new(loop_count_n.inputs[1], input_n.outputs['FramesTotal'])

    animsheet_loop_frame_g.links.new(loop_count_floored_n.inputs[0], loop_count_n.outputs[0])

    animsheet_loop_frame_g.links.new(global_frame_floored_n.inputs[0], loop_count_floored_n.outputs[0])
    animsheet_loop_frame_g.links.new(global_frame_floored_n.inputs[1], input_n.outputs['FramesTotal'])

    animsheet_loop_frame_g.links.new(loop_frame_n.inputs[0], global_frame_n.outputs[0])
    animsheet_loop_frame_g.links.new(loop_frame_n.inputs[1], global_frame_floored_n.outputs[0])

    animsheet_loop_frame_g.links.new(output_n.inputs['LoopFrame'], loop_frame_n.outputs[0])


def update_time(scene):
    """Updates time value used in calculation of blend factor.

    :param scene: scene in which time for shaders is being updated
    :type scene: bpy.types.Scene
    """

    if ANIMSHEET_LOOP_FRAME_G not in bpy.data.node_groups:
        return

    # properly handle playing to prevent jumping time into unknown location when animation switches to the start/end
    old_global_frame_node = bpy.data.node_groups[ANIMSHEET_LOOP_FRAME_G].nodes[_GLOBAL_FRAME_OLD_NODE]
    # jumped from end to start
    if old_global_frame_node.outputs[0].default_value == scene.frame_end and scene.frame_current == scene.frame_start:
        frame_change = 1
    # jumped from start to end (reverse playing)
    elif old_global_frame_node.outputs[0].default_value == scene.frame_start and scene.frame_current == scene.frame_end:
        frame_change = -1
    # user jump to start do nothing and reset time
    elif old_global_frame_node.outputs[0].default_value > scene.frame_current:
        frame_change = 0
        bpy.data.node_groups[ANIMSHEET_LOOP_FRAME_G].nodes[_GLOBAL_FRAME_NODE].inputs[1].default_value = 0
    # normal playing
    else:
        frame_change = scene.frame_current - old_global_frame_node.outputs[0].default_value

    # store current frame into the node
    old_global_frame_node.outputs[0].default_value = scene.frame_current

    time_fragment = frame_change / (scene.render.fps / scene.render.fps_base)
    bpy.data.node_groups[ANIMSHEET_LOOP_FRAME_G].nodes[_GLOBAL_FRAME_NODE].inputs[1].default_value += time_fragment
