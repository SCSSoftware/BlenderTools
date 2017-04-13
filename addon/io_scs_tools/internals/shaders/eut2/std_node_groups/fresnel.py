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
from io_scs_tools.consts import Material as _MAT_consts

FRESNEL_G = _MAT_consts.node_group_prefix + "FresnelGroup"


def get_node_group():
    """Gets node group for calcualtion of fresnel.

    :return: node group which calculates fresnel factor
    :rtype: bpy.types.NodeGroup
    """

    if FRESNEL_G not in bpy.data.node_groups:
        __create_fresnel_group__()

    return bpy.data.node_groups[FRESNEL_G]


def __create_fresnel_group__():
    """Creates fresnel group.

    Inputs: Scale, Bias, Reflection Normal Vector, Normal Vector
    Outputs: Fresnel Factor
    """

    fresnel_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=FRESNEL_G)

    # inputs defining
    fresnel_g.inputs.new("NodeSocketFloat", "Scale")
    fresnel_g.inputs.new("NodeSocketFloat", "Bias")
    fresnel_g.inputs.new("NodeSocketVector", "Normal Vector")
    fresnel_g.inputs.new("NodeSocketVector", "Reflection Normal Vector")
    input_n = fresnel_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    fresnel_g.outputs.new("NodeSocketFloat", "Fresnel Factor")
    output_n = fresnel_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 5, 0)

    # group nodes
    dot_n = fresnel_g.nodes.new("ShaderNodeVectorMath")
    dot_n.location = (185, 100)
    dot_n.operation = "DOT_PRODUCT"

    subtract_dot_n = fresnel_g.nodes.new("ShaderNodeMath")
    subtract_dot_n.location = (185 * 2, 100)
    subtract_dot_n.operation = "SUBTRACT"
    subtract_dot_n.use_clamp = False
    subtract_dot_n.inputs[0].default_value = 1.0

    mult_subtract_n = fresnel_g.nodes.new("ShaderNodeMath")
    mult_subtract_n.location = (185 * 3, 50)
    mult_subtract_n.operation = "MULTIPLY"
    mult_subtract_n.use_clamp = False
    mult_subtract_n.inputs[0].default_value = 1.0

    add_mult_n = fresnel_g.nodes.new("ShaderNodeMath")
    add_mult_n.location = (185 * 4, 0)
    add_mult_n.operation = "ADD"
    add_mult_n.use_clamp = False
    add_mult_n.inputs[0].default_value = 1.0

    # group links
    # formula: (1 - dot(normal, reflection)) * scale + bias
    fresnel_g.links.new(dot_n.inputs[0], input_n.outputs['Normal Vector'])
    fresnel_g.links.new(dot_n.inputs[1], input_n.outputs['Reflection Normal Vector'])

    fresnel_g.links.new(subtract_dot_n.inputs[1], dot_n.outputs['Value'])

    fresnel_g.links.new(mult_subtract_n.inputs[0], subtract_dot_n.outputs['Value'])
    fresnel_g.links.new(mult_subtract_n.inputs[1], input_n.outputs['Scale'])

    fresnel_g.links.new(add_mult_n.inputs[0], mult_subtract_n.outputs['Value'])
    fresnel_g.links.new(add_mult_n.inputs[1], input_n.outputs['Bias'])

    fresnel_g.links.new(output_n.inputs['Fresnel Factor'], add_mult_n.outputs['Value'])
