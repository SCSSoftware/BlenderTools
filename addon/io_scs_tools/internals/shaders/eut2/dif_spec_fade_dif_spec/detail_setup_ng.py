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

# Copyright (C) 2015-2019: SCS Software

import bpy
from .....consts import Material as _MAT_consts

DETAIL_SETUP_G = _MAT_consts.node_group_prefix + "DetailStrengthGroup"


def get_node_group():
    """Gets node group for calculating of detail strength.

    Inputs: Fade From, Fade Range, Blend Bias;
    Outputs: Detail Strength, Blend Factor;

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if DETAIL_SETUP_G not in bpy.data.node_groups:
        __create_group__()

    return bpy.data.node_groups[DETAIL_SETUP_G]


def __create_group__():
    """Creates detail strength computation group.

    Inputs: Fade From, Fade Range, Blend Bias
    Outputs: Detail Strength, Blend Factor
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    detail_setup_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=DETAIL_SETUP_G)

    # inputs defining
    detail_setup_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Fade From")
    detail_setup_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Fade Range")
    detail_setup_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Blend Bias")

    # outputs defining
    detail_setup_g.interface.new_socket(in_out = "OUTPUT", socket_type = "NodeSocketFloat", name = "Detail Strength")
    detail_setup_g.interface.new_socket(in_out = "OUTPUT", socket_type = "NodeSocketFloat", name = "Blend Factor")


    # group nodes
    input_n = detail_setup_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = detail_setup_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    camera_data_n = detail_setup_g.nodes.new("ShaderNodeCameraData")
    camera_data_n.location = (start_pos_x, start_pos_y + 100)

    equation_nodes = []

    for i, name in enumerate(("DistInv", "DistInv+FadeFrom", "(DistInv+FadeFrom)/FadeRange",
                              "Clamp(1+(DistInv+FadeFrom)/FadeRange)")):

        # node creation
        equation_nodes.append(detail_setup_g.nodes.new("ShaderNodeMath"))
        equation_nodes[i].name = equation_nodes[i].label = name
        equation_nodes[i].location = (start_pos_x + pos_x_shift * (1 + i), start_pos_y + 150 - i * 40)

        # links creation and settings
        if i == 0:

            equation_nodes[i].operation = "MULTIPLY"
            equation_nodes[i].inputs[1].default_value = -1.0
            detail_setup_g.links.new(equation_nodes[i].inputs[0], camera_data_n.outputs['View Distance'])

        elif i == 1:

            equation_nodes[i].operation = "ADD"
            detail_setup_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])
            detail_setup_g.links.new(equation_nodes[i].inputs[1], input_n.outputs['Fade From'])

        elif i == 2:

            equation_nodes[i].operation = "DIVIDE"
            detail_setup_g.links.new(equation_nodes[i].inputs[0], equation_nodes[i - 1].outputs[0])
            detail_setup_g.links.new(equation_nodes[i].inputs[1], input_n.outputs['Fade Range'])

        elif i == 3:

            equation_nodes[i].operation = "ADD"
            equation_nodes[i].use_clamp = True
            equation_nodes[i].inputs[0].default_value = 1.0
            detail_setup_g.links.new(equation_nodes[i].inputs[1], equation_nodes[i - 1].outputs[0])

            detail_setup_g.links.new(output_n.inputs['Detail Strength'], equation_nodes[i].outputs[0])

    blend_factor_mix_n = detail_setup_g.nodes.new("ShaderNodeMix")
    blend_factor_mix_n.name = blend_factor_mix_n.label = "BlendFactor"
    blend_factor_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y - 50)
    blend_factor_mix_n.data_type = "RGBA"
    blend_factor_mix_n.blend_type = "MIX"
    blend_factor_mix_n.inputs['B'].default_value = (0.0,) * 4

    # group links
    detail_setup_g.links.new(blend_factor_mix_n.inputs['Factor'], input_n.outputs['Blend Bias'])
    detail_setup_g.links.new(blend_factor_mix_n.inputs['A'], equation_nodes[-1].outputs[0])

    detail_setup_g.links.new(output_n.inputs['Blend Factor'], blend_factor_mix_n.outputs['Result'])
