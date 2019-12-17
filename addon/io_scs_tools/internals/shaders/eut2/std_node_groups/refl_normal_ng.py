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

    Inputs: Position, Normal
    Outputs: Reflection Normal Vector
    """

    refl_normal_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=REFL_NORMAL_G)

    # inputs defining
    refl_normal_g.inputs.new("NodeSocketVector", "Incoming")
    refl_normal_g.inputs.new("NodeSocketVector", "Normal")
    input_n = refl_normal_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    refl_normal_g.outputs.new("NodeSocketVector", "Reflection Normal")
    output_n = refl_normal_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 7, 0)

    # group nodes
    view_vector_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    view_vector_n.location = (185, 250)
    view_vector_n.operation = "MULTIPLY"
    view_vector_n.inputs[1].default_value = (-1,) * 3

    view_vector_norm_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    view_vector_norm_n.location = (185 * 2, 250)
    view_vector_norm_n.operation = "NORMALIZE"

    view_normal_dot_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    view_normal_dot_n.location = (185 * 3, 200)
    view_normal_dot_n.operation = "DOT_PRODUCT"

    view_normal_dot_scaled_n = refl_normal_g.nodes.new("ShaderNodeMath")
    view_normal_dot_scaled_n.location = (185 * 4, 200)
    view_normal_dot_scaled_n.operation = "MULTIPLY"
    view_normal_dot_scaled_n.inputs[1].default_value = 2.0

    normal_mult_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    normal_mult_n.location = (185 * 5, 100)
    normal_mult_n.operation = "MULTIPLY"

    view_normal_subtract_n = refl_normal_g.nodes.new("ShaderNodeVectorMath")
    view_normal_subtract_n.location = (185 * 6, 350)
    view_normal_subtract_n.operation = "SUBTRACT"

    # group links
    # formula: view_v - 2*dot(view_v, normal_v) * normal_v as in GLSL reflect function
    refl_normal_g.links.new(view_vector_n.inputs[0], input_n.outputs['Incoming'])

    refl_normal_g.links.new(view_vector_norm_n.inputs[0], view_vector_n.outputs['Vector'])

    refl_normal_g.links.new(view_normal_dot_n.inputs[0], view_vector_norm_n.outputs['Vector'])
    refl_normal_g.links.new(view_normal_dot_n.inputs[1], input_n.outputs['Normal'])

    refl_normal_g.links.new(view_normal_dot_scaled_n.inputs[0], view_normal_dot_n.outputs['Value'])

    refl_normal_g.links.new(normal_mult_n.inputs[0], view_normal_dot_scaled_n.outputs['Value'])
    refl_normal_g.links.new(normal_mult_n.inputs[1], input_n.outputs['Normal'])

    refl_normal_g.links.new(view_normal_subtract_n.inputs[0], view_vector_norm_n.outputs['Vector'])
    refl_normal_g.links.new(view_normal_subtract_n.inputs[1], normal_mult_n.outputs[0])

    refl_normal_g.links.new(output_n.inputs['Reflection Normal'], view_normal_subtract_n.outputs['Vector'])
