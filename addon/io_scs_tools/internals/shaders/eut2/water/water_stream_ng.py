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

WATER_STREAM_G = _MAT_consts.node_group_prefix + "WaterStream"

_ANIM_TIME_NODE = "AnimTimeNode"

_STREAM0_SPEED_MULT_NODE = "Stream0SpeedMultiply"
_STREAM0_TIME_ADD_NODE = "Stream0TimeAdd"
_STREAM1_SPEED_MULT_NODE = "Stream1SpeedMultiply"
_STREAM1_TIME_ADD_NODE = "Stream1TimeAdd"


def get_node_group():
    """Gets node group for water stream calculation.

    :return: node group which calculates water stream vectors
    :rtype: bpy.types.NodeGroup
    """

    if WATER_STREAM_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[WATER_STREAM_G]


def update_time(scene):
    """Updates stream velocity value.

    :param scene: scene in which time for shaders is being updated
    :type scene: bpy.types.Scene
    """

    if WATER_STREAM_G not in bpy.data.node_groups:
        return

    time = scene.frame_current / (scene.render.fps / scene.render.fps_base)
    bpy.data.node_groups[WATER_STREAM_G].nodes[_ANIM_TIME_NODE].outputs[0].default_value = time


def __create_node_group__():
    """Creates add env group.

    Inputs: Fresnel Scale, Fresnel Bias, Normal Vector, View Vector, Apply Fresnel,
    Reflection Texture Color, Base Texture Alpha, Env Factor Color and Specular Color
    Outputs: Environment Addition Color
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    water_stream_ng = bpy.data.node_groups.new(type="ShaderNodeTree", name=WATER_STREAM_G)

    # inputs defining
    water_stream_ng.inputs.new("NodeSocketVector", "Yaw0")
    water_stream_ng.inputs.new("NodeSocketFloat", "Speed0")
    water_stream_ng.inputs.new("NodeSocketVector", "Yaw1")
    water_stream_ng.inputs.new("NodeSocketFloat", "Speed1")
    input_n = water_stream_ng.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    # outputs defining
    water_stream_ng.outputs.new("NodeSocketVector", "Stream0")
    water_stream_ng.outputs.new("NodeSocketVector", "Stream1")
    output_n = water_stream_ng.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)

    # node creation
    stream0_speed_mult_n = water_stream_ng.nodes.new("ShaderNodeVectorMath")
    stream0_speed_mult_n.name = stream0_speed_mult_n.label = _STREAM0_SPEED_MULT_NODE
    stream0_speed_mult_n.location = (start_pos_x, start_pos_y + 100)
    stream0_speed_mult_n.operation = "MULTIPLY"

    stream1_speed_mult_n = water_stream_ng.nodes.new("ShaderNodeVectorMath")
    stream1_speed_mult_n.name = stream1_speed_mult_n.label = _STREAM1_SPEED_MULT_NODE
    stream1_speed_mult_n.location = (start_pos_x, start_pos_y - 100)
    stream1_speed_mult_n.operation = "MULTIPLY"

    anim_time_n = water_stream_ng.nodes.new("ShaderNodeValue")
    anim_time_n.name = anim_time_n.label = _ANIM_TIME_NODE
    anim_time_n.location = (start_pos_x, start_pos_y + 300)

    stream0_time_mult_n = water_stream_ng.nodes.new("ShaderNodeVectorMath")
    stream0_time_mult_n.name = stream0_time_mult_n.label = _STREAM0_TIME_ADD_NODE
    stream0_time_mult_n.location = (start_pos_x + pos_x_shift, start_pos_y + 100)
    stream0_time_mult_n.operation = "MULTIPLY"

    stream1_time_mult_n = water_stream_ng.nodes.new("ShaderNodeVectorMath")
    stream1_time_mult_n.name = stream1_time_mult_n.label = _STREAM1_TIME_ADD_NODE
    stream1_time_mult_n.location = (start_pos_x + pos_x_shift, start_pos_y - 100)
    stream1_time_mult_n.operation = "MULTIPLY"

    # links
    water_stream_ng.links.new(stream0_speed_mult_n.inputs[0], input_n.outputs['Yaw0'])
    water_stream_ng.links.new(stream0_speed_mult_n.inputs[1], input_n.outputs['Speed0'])
    water_stream_ng.links.new(stream1_speed_mult_n.inputs[0], input_n.outputs['Yaw1'])
    water_stream_ng.links.new(stream1_speed_mult_n.inputs[1], input_n.outputs['Speed1'])

    water_stream_ng.links.new(stream0_time_mult_n.inputs[0], anim_time_n.outputs[0])
    water_stream_ng.links.new(stream0_time_mult_n.inputs[1], stream0_speed_mult_n.outputs[0])
    water_stream_ng.links.new(stream1_time_mult_n.inputs[0], anim_time_n.outputs[0])
    water_stream_ng.links.new(stream1_time_mult_n.inputs[1], stream1_speed_mult_n.outputs[0])

    water_stream_ng.links.new(output_n.inputs['Stream0'], stream0_time_mult_n.outputs[0])
    water_stream_ng.links.new(output_n.inputs['Stream1'], stream1_time_mult_n.outputs[0])
