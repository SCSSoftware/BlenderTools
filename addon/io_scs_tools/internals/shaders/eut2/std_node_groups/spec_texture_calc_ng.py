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

# Copyright (C) 2024: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts

SPEC_TEXTURE_CALC_G = _MAT_consts.node_group_prefix + "SpecularTextureCalc"

_COLOR_TO_RGB_NODE = "ColorToRGB"
_SHININESS_MULT = "ShininessMult"


def get_node_group():
    """Gets node group for specular and shininess calculation.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if SPEC_TEXTURE_CALC_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[SPEC_TEXTURE_CALC_G]

def __create_node_group__():
    """Creates specular and shininess group.

    Inputs: Color
    Outputs: Shininess, Specular
    """

    spec_txt_calc_n = bpy.data.node_groups.new(type="ShaderNodeTree", name=SPEC_TEXTURE_CALC_G)

    # inputs defining
    spec_txt_calc_n.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketColor", name = "Color")

    # outputs defining
    spec_txt_calc_n.interface.new_socket(in_out = "OUTPUT", socket_type = "NodeSocketVector", name = "Shininess")
    spec_txt_calc_n.interface.new_socket(in_out = "OUTPUT", socket_type = "NodeSocketVector", name = "Specular")


    # node creation
    input_n = spec_txt_calc_n.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    output_n = spec_txt_calc_n.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 3, 0)

    color_to_rgb_n = spec_txt_calc_n.nodes.new("ShaderNodeSeparateColor")
    color_to_rgb_n.name = color_to_rgb_n.label = _COLOR_TO_RGB_NODE
    color_to_rgb_n.location = (185, 0)
    color_to_rgb_n.mode = "RGB"

    shininess_mult_n = spec_txt_calc_n.nodes.new("ShaderNodeVectorMath")
    shininess_mult_n.name = shininess_mult_n.label = _SHININESS_MULT
    shininess_mult_n.location = (185 * 2, 100)
    shininess_mult_n.operation = "MULTIPLY"
    shininess_mult_n.inputs[1].default_value = (255,) * 3

    # links
    spec_txt_calc_n.links.new(input_n.outputs['Color'], color_to_rgb_n.inputs['Color'])

    spec_txt_calc_n.links.new(color_to_rgb_n.outputs['Red'], shininess_mult_n.inputs[0])
    spec_txt_calc_n.links.new(color_to_rgb_n.outputs['Green'], output_n.inputs['Specular'])

    spec_txt_calc_n.links.new(shininess_mult_n.outputs['Vector'], output_n.inputs['Shininess'])