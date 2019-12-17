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

SCS_UVS_COMBINE_G = _MAT_consts.node_group_prefix + "UVsCombine"


def get_node_group():
    """Gets node group for combining of SCS coordinate U and V into XYZ vector.

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if SCS_UVS_COMBINE_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[SCS_UVS_COMBINE_G]


def __create_node_group__():
    """Create group for combining of SCS U and V coordinates into XYZ vector.

    Inputs: U, V
    Outputs: Vector
    """

    pos_x_shift = 185

    scs_uvs_combine_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=SCS_UVS_COMBINE_G)

    # inputs defining
    scs_uvs_combine_g.inputs.new("NodeSocketFloat", "U")
    scs_uvs_combine_g.inputs.new("NodeSocketFloat", "V")
    input_n = scs_uvs_combine_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    scs_uvs_combine_g.outputs.new("NodeSocketVector", "Vector")
    output_n = scs_uvs_combine_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 4, 0)

    # group nodes
    v_to_scs_inv_n = scs_uvs_combine_g.nodes.new("ShaderNodeMath")
    v_to_scs_inv_n.location = (pos_x_shift * 1, -100)
    v_to_scs_inv_n.operation = "MULTIPLY"
    v_to_scs_inv_n.inputs[1].default_value = -1

    v_to_scs_add_n = scs_uvs_combine_g.nodes.new("ShaderNodeMath")
    v_to_scs_add_n.location = (pos_x_shift * 2, -100)
    v_to_scs_add_n.operation = "ADD"
    v_to_scs_add_n.inputs[1].default_value = 1

    combine_n = scs_uvs_combine_g.nodes.new("ShaderNodeCombineXYZ")
    combine_n.location = (pos_x_shift * 3, 0)
    combine_n.inputs['Z'].default_value = 0.0

    # group links
    scs_uvs_combine_g.links.new(v_to_scs_inv_n.inputs[0], input_n.outputs['V'])

    scs_uvs_combine_g.links.new(v_to_scs_add_n.inputs[0], v_to_scs_inv_n.outputs[0])

    scs_uvs_combine_g.links.new(combine_n.inputs['X'], input_n.outputs['U'])
    scs_uvs_combine_g.links.new(combine_n.inputs['Y'], v_to_scs_add_n.outputs[0])

    scs_uvs_combine_g.links.new(output_n.inputs['Vector'], combine_n.outputs[0])
