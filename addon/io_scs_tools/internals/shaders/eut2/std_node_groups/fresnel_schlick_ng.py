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

FRESNEL_SCHLICK_G = _MAT_consts.node_group_prefix + "FresnelSchlickGroup"


def get_node_group():
    """Gets node group for calcualtion of fresnel.

    :return: node group which calculates fresnel factor
    :rtype: bpy.types.NodeGroup
    """

    if FRESNEL_SCHLICK_G not in bpy.data.node_groups:
        __create_fresnel_group__()

    return bpy.data.node_groups[FRESNEL_SCHLICK_G]


def __create_fresnel_group__():
    """Creates fresnel group.

    Inputs: Scale, Bias, Reflection Normal Vector, Normal Vector
    Outputs: Fresnel Factor
    """

    fresnel_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=FRESNEL_SCHLICK_G)

    pos_x_shift = 185

    # inputs defining
    fresnel_g.inputs.new("NodeSocketFloat", "Bias")
    fresnel_g.inputs.new("NodeSocketVector", "Normal Vector")
    fresnel_g.inputs.new("NodeSocketVector", "Reflection Normal Vector")
    input_n = fresnel_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    fresnel_g.outputs.new("NodeSocketFloat", "Fresnel Factor")
    output_n = fresnel_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 6, 0)

    # group nodes
    dot_n = fresnel_g.nodes.new("ShaderNodeVectorMath")
    dot_n.location = (pos_x_shift, 100)
    dot_n.operation = "DOT_PRODUCT"

    subtract_dot_n = fresnel_g.nodes.new("ShaderNodeMath")
    subtract_dot_n.location = (pos_x_shift * 2, 100)
    subtract_dot_n.operation = "SUBTRACT"
    subtract_dot_n.use_clamp = False
    subtract_dot_n.inputs[0].default_value = 1.0

    subtract_bias_n = fresnel_g.nodes.new("ShaderNodeMath")
    subtract_bias_n.location = (pos_x_shift * 2, -100)
    subtract_bias_n.operation = "SUBTRACT"
    subtract_bias_n.use_clamp = False
    subtract_bias_n.inputs[0].default_value = 1.0

    pow5_bias_n = fresnel_g.nodes.new("ShaderNodeMath")
    pow5_bias_n.location = (pos_x_shift * 3, 100)
    pow5_bias_n.operation = "POWER"
    pow5_bias_n.use_clamp = False
    pow5_bias_n.inputs[1].default_value = 5.0

    mult_pow5_bias_n = fresnel_g.nodes.new("ShaderNodeMath")
    mult_pow5_bias_n.location = (pos_x_shift * 4, 50)
    mult_pow5_bias_n.operation = "MULTIPLY"
    mult_pow5_bias_n.use_clamp = False

    add_mult_bias_n = fresnel_g.nodes.new("ShaderNodeMath")
    add_mult_bias_n.location = (pos_x_shift * 5, 0)
    add_mult_bias_n.operation = "ADD"
    add_mult_bias_n.use_clamp = True

    # group links
    # formula: pow5(1 - dot(normal, reflection)) * (1 - bias) + bias
    fresnel_g.links.new(dot_n.inputs[0], input_n.outputs['Normal Vector'])
    fresnel_g.links.new(dot_n.inputs[1], input_n.outputs['Reflection Normal Vector'])

    fresnel_g.links.new(subtract_dot_n.inputs[1], dot_n.outputs['Value'])

    fresnel_g.links.new(subtract_bias_n.inputs[1], input_n.outputs['Bias'])

    fresnel_g.links.new(pow5_bias_n.inputs[0], subtract_dot_n.outputs['Value'])

    fresnel_g.links.new(mult_pow5_bias_n.inputs[0], pow5_bias_n.outputs['Value'])
    fresnel_g.links.new(mult_pow5_bias_n.inputs[1], subtract_bias_n.outputs['Value'])

    fresnel_g.links.new(add_mult_bias_n.inputs[0], mult_pow5_bias_n.outputs['Value'])
    fresnel_g.links.new(add_mult_bias_n.inputs[1], input_n.outputs['Bias'])

    fresnel_g.links.new(output_n.inputs['Fresnel Factor'], add_mult_bias_n.outputs['Value'])
