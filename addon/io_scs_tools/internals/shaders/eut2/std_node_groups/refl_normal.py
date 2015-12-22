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

REFL_NORMAL_G = _MAT_consts.node_group_prefix + "ReflectionNormalGroup"


def get_node_group():
    """Gets node group for calculation of reflection normal.

    :return: node group which calculates reflection normal
    :rtype: bpy.types.NodeGroup
    """

    if REFL_NORMAL_G not in bpy.data.node_groups:
        __create_refl_normal_group__()

    return bpy.data.node_groups[REFL_NORMAL_G]


def __create_refl_normal_group__():
    """Create reflection normal group.

    Inputs: View Vector, Normal Vector
    Outputs: Reflection Normal Vector
    """

    refl_normal_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=REFL_NORMAL_G)

    # inputs defining
    refl_normal_g.inputs.new("NodeSocketVector", "Normal Vector")
    refl_normal_g.inputs.new("NodeSocketVector", "View Vector")
    input_n = refl_normal_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    refl_normal_g.outputs.new("NodeSocketVector", "Reflection Normal")
    output_n = refl_normal_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 5, 0)

    # group nodes
    dot_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    dot_n.location = (185, 150)
    dot_n.operation = "DOT_PRODUCT"

    dot_mult_2_n = refl_normal_g.nodes.new("ShaderNodeMath")
    dot_mult_2_n.location = (185 * 2, 100)
    dot_mult_2_n.operation = "MULTIPLY"
    dot_mult_2_n.inputs[1].default_value = 2.0

    cross_product_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    cross_product_n.location = (185 * 3, 50)
    cross_product_n.operation = "CROSS_PRODUCT"

    substract_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    substract_n.location = (185 * 4, -50)
    substract_n.operation = "SUBTRACT"

    # group links
    # formula: view_v - 2*dot(view_v, normal_v)*normal_v
    refl_normal_g.links.new(dot_n.inputs[0], input_n.outputs['View Vector'])
    refl_normal_g.links.new(dot_n.inputs[1], input_n.outputs['Normal Vector'])

    refl_normal_g.links.new(dot_mult_2_n.inputs[0], dot_n.outputs['Value'])

    refl_normal_g.links.new(cross_product_n.inputs[0], input_n.outputs['Normal Vector'])
    refl_normal_g.links.new(cross_product_n.inputs[1], dot_mult_2_n.outputs['Value'])

    refl_normal_g.links.new(substract_n.inputs[0], input_n.outputs['View Vector'])
    refl_normal_g.links.new(substract_n.inputs[1], cross_product_n.outputs['Vector'])

    refl_normal_g.links.new(output_n.inputs['Reflection Normal'], substract_n.outputs['Vector'])
