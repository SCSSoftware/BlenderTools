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
from time import time
from io_scs_tools.consts import Material as _MAT_consts

BLEND_FACTOR_G = _MAT_consts.node_group_prefix + "BlendFactor"

ANIM_TIME_NODE = "AnimTime"


def get_node_group():
    """Gets node group for calcualtion of environment addition color.

    :return: node group which calculates environment addition color
    :rtype: bpy.types.NodeGroup
    """

    if BLEND_FACTOR_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[BLEND_FACTOR_G]


def update_time():
    """Updates time value used in calculation of blend factor.
    """

    if BLEND_FACTOR_G not in bpy.data.node_groups:
        return

    bpy.data.node_groups[BLEND_FACTOR_G].nodes[ANIM_TIME_NODE].outputs[0].default_value = time() % 60.0


def __create_node_group__():
    """Creates add env group.

    Inputs: Fresnel Scale, Fresnel Bias, Normal Vector, View Vector, Apply Fresnel,
    Reflection Texture Color, Base Texture Alpha, Env Factor Color and Specular Color
    Outputs: Environment Addition Color
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    blend_fac_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=BLEND_FACTOR_G)

    # inputs defining
    blend_fac_g.inputs.new("NodeSocketFloat", "Speed")
    input_n = blend_fac_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    # outputs defining
    blend_fac_g.outputs.new("NodeSocketColor", "Factor")
    output_n = blend_fac_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y)

    # node creation
    anim_time_n = blend_fac_g.nodes.new("ShaderNodeValue")
    anim_time_n.name = anim_time_n.label = ANIM_TIME_NODE
    anim_time_n.location = (start_pos_x, start_pos_y + 200)

    equation_nodes = []

    for i, name in enumerate(("(Time*Speed)", "((Time*Speed)/3)", "((Time*Speed)/3)*2", "((Time*Speed)/3)*2*3.14159",
                              "sin(((Time*Speed)/3)*2*3.14159)", "sin(((Time*Speed)/3)*2*3.14159)/2",
                              "sin(((Time*Speed)/3)*2*3.14159)/2+0.5")):

        # node creation
        equation_nodes.append(blend_fac_g.nodes.new("ShaderNodeMath"))
        equation_nodes[i].name = equation_nodes[i].label = name
        equation_nodes[i].location = (start_pos_x + pos_x_shift * (1 + i), start_pos_y)

        # links creation and settings
        if i == 0:

            equation_nodes[i].operation = "MULTIPLY"
            blend_fac_g.links.new(equation_nodes[i].inputs[0], anim_time_n.outputs[0])
            blend_fac_g.links.new(equation_nodes[i].inputs[1], input_n.outputs['Speed'])

        elif i == 1:

            equation_nodes[i].operation = "DIVIDE"
            equation_nodes[i].inputs[1].default_value = 3.0
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

        elif i == 2:

            equation_nodes[i].operation = "MULTIPLY"
            equation_nodes[i].inputs[1].default_value = 2.0
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

        elif i == 3:

            equation_nodes[i].operation = "MULTIPLY"
            equation_nodes[i].inputs[1].default_value = 3.14159
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

        elif i == 4:

            equation_nodes[i].operation = "SINE"
            equation_nodes[i].inputs[1].default_value = 0.0
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

        elif i == 5:

            equation_nodes[i].operation = "DIVIDE"
            equation_nodes[i].inputs[1].default_value = 2.0
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

        elif i == 6:

            equation_nodes[i].operation = "ADD"
            equation_nodes[i].inputs[1].default_value = 0.5
            blend_fac_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])

            # output
            blend_fac_g.links.new(output_n.inputs['Factor'], equation_nodes[i].outputs[0])
