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

# Copyright (C) 2017: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts

ASAFEW_G = _MAT_consts.node_group_prefix + "AlphaRemapGroup"

_MULT_FAC1_NODE = "MultiplyFact1"
_ADD_FAC2_NODE = "AddFact2"


def get_node_group():
    """Gets node group for DDS 16-bit normal map texture.

    :return: node group which handles 16-bit DDS
    :rtype: bpy.types.NodeGroup
    """

    if ASAFEW_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[ASAFEW_G]


def __create_node_group__():
    """Creates node group for remapping alpha to weight

    Inputs: Alpha, Factor1, Factor2
    Outputs: Weighted Alpha
    """

    asafew_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ASAFEW_G)

    # inputs defining
    asafew_g.inputs.new("NodeSocketFloat", "Alpha")
    asafew_g.inputs.new("NodeSocketFloat", "Factor1")
    asafew_g.inputs.new("NodeSocketFloat", "Factor2")
    input_n = asafew_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    asafew_g.outputs.new("NodeSocketFloat", "Weighted Alpha")
    output_n = asafew_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 3, 0)

    # (alpha * alpha_to_weight_factors.x)
    mult_fac1_n = asafew_g.nodes.new("ShaderNodeMath")
    mult_fac1_n.name = mult_fac1_n.label = _MULT_FAC1_NODE
    mult_fac1_n.location = (185 * 1, 100)
    mult_fac1_n.operation = "MULTIPLY"

    # ((alpha * alpha_to_weight_factors.x) + alpha_to_weight_factors.y)
    add_fac2_n = asafew_g.nodes.new("ShaderNodeMath")
    add_fac2_n.name = add_fac2_n.label = _ADD_FAC2_NODE
    add_fac2_n.location = (185 * 2, 0)
    add_fac2_n.operation = "ADD"
    add_fac2_n.use_clamp = True

    # group links
    asafew_g.links.new(mult_fac1_n.inputs[0], input_n.outputs['Alpha'])
    asafew_g.links.new(mult_fac1_n.inputs[1], input_n.outputs['Factor1'])

    asafew_g.links.new(add_fac2_n.inputs[0], mult_fac1_n.outputs[0])
    asafew_g.links.new(add_fac2_n.inputs[1], input_n.outputs['Factor2'])

    asafew_g.links.new(output_n.inputs['Weighted Alpha'], add_fac2_n.outputs[0])
