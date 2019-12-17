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

SCS_UVS_SEPARATE_G = _MAT_consts.node_group_prefix + "UVsSeparate"


def get_node_group():
    """Gets node group for separation of UVs into SCS coordinate system U and V.

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if SCS_UVS_SEPARATE_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[SCS_UVS_SEPARATE_G]


def __create_node_group__():
    """Create group for separation of UVs to SCS coordinate system.

    Inputs: UV
    Outputs: U, V
    """

    pos_x_shift = 185

    scs_uvs_separate_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=SCS_UVS_SEPARATE_G)

    # inputs defining
    scs_uvs_separate_g.inputs.new("NodeSocketVector", "UV")
    input_n = scs_uvs_separate_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    scs_uvs_separate_g.outputs.new("NodeSocketFloat", "U")
    scs_uvs_separate_g.outputs.new("NodeSocketFloat", "V")
    output_n = scs_uvs_separate_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 4, 0)

    # group nodes
    separate_xyz_n = scs_uvs_separate_g.nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz_n.location = (pos_x_shift * 1, 0)

    v_to_scs_inv_n = scs_uvs_separate_g.nodes.new("ShaderNodeMath")
    v_to_scs_inv_n.location = (pos_x_shift * 2, -100)
    v_to_scs_inv_n.operation = "MULTIPLY"
    v_to_scs_inv_n.inputs[1].default_value = -1

    v_to_scs_add_n = scs_uvs_separate_g.nodes.new("ShaderNodeMath")
    v_to_scs_add_n.location = (pos_x_shift * 3, -100)
    v_to_scs_add_n.operation = "ADD"
    v_to_scs_add_n.inputs[1].default_value = 1

    # group links
    scs_uvs_separate_g.links.new(separate_xyz_n.inputs[0], input_n.outputs['UV'])

    scs_uvs_separate_g.links.new(v_to_scs_inv_n.inputs[0], separate_xyz_n.outputs['Y'])

    scs_uvs_separate_g.links.new(v_to_scs_add_n.inputs[0], v_to_scs_inv_n.outputs[0])

    scs_uvs_separate_g.links.new(output_n.inputs['U'], separate_xyz_n.outputs['X'])
    scs_uvs_separate_g.links.new(output_n.inputs['V'], v_to_scs_add_n.outputs[0])
