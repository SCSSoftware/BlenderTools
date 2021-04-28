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
from io_scs_tools.internals.shaders.eut2.sky import texture_types

SKY_UV_RESCALE_G = _MAT_consts.node_group_prefix + "SkyUVRescale"

_RESCALE_INV_NODE = "Rescale Inv"
_SEP_UV_NODE = "Separate UV"
_MULT_V_SCALE_PREFIX = "V Scale Mult "
_COMBINE_V_SCALE_PREFIX = "Combine UV "
_MULT_RESCALED_UV_PREFIX = "Mult Rescaled UV "
_MULT_UNSCALED_UV_PREFIX = "Mult Unscaled UV "
_COMBINE_UV_PREFIX = "Final UV "


def get_node_group():
    """Gets node group for DDS 16-bit normal map texture.

    :return: node group which handles 16-bit DDS
    :rtype: bpy.types.NodeGroup
    """

    if SKY_UV_RESCALE_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[SKY_UV_RESCALE_G]


def __create_node_group__():
    """Creates node group for remapping alpha to weight

    Inputs: Alpha, Factor1, Factor2
    Outputs: Weighted Alpha
    """

    pos_x_shift = 185

    rescale_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=SKY_UV_RESCALE_G)

    # inputs defining
    rescale_g.inputs.new("NodeSocketFloat", "Rescale Enabled")
    rescale_g.inputs.new("NodeSocketFloat", "V Scale Base A")
    rescale_g.inputs.new("NodeSocketFloat", "V Scale Base B")
    rescale_g.inputs.new("NodeSocketFloat", "V Scale Over A")
    rescale_g.inputs.new("NodeSocketFloat", "V Scale Over B")
    rescale_g.inputs.new("NodeSocketVector", "UV")
    input_n = rescale_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    rescale_g.outputs.new("NodeSocketVector", "UV Base A")
    rescale_g.outputs.new("NodeSocketVector", "UV Base B")
    rescale_g.outputs.new("NodeSocketVector", "UV Over A")
    rescale_g.outputs.new("NodeSocketVector", "UV Over B")
    output_n = rescale_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 9, 0)

    # create nodes
    rescale_inv_n = rescale_g.nodes.new("ShaderNodeMath")
    rescale_inv_n.name = rescale_inv_n.label = _RESCALE_INV_NODE
    rescale_inv_n.location = (pos_x_shift * 2, 100)
    rescale_inv_n.operation = "SUBTRACT"
    rescale_inv_n.inputs[0].default_value = 1.0

    separate_uv_n = rescale_g.nodes.new("ShaderNodeSeparateXYZ")
    separate_uv_n.name = separate_uv_n.label = _SEP_UV_NODE
    separate_uv_n.location = (pos_x_shift * 2, -100)

    # group links
    rescale_g.links.new(rescale_inv_n.inputs[1], input_n.outputs['Rescale Enabled'])
    rescale_g.links.new(separate_uv_n.inputs[0], input_n.outputs['UV'])

    # create components for each texture type
    for tex_type_i, tex_type in enumerate(texture_types.get()):
        __init_rescale_component__(rescale_g,
                                   tex_type,
                                   (pos_x_shift * 3, tex_type_i * -400 + 500),
                                   input_n.outputs['UV'],
                                   separate_uv_n.outputs['X'],
                                   separate_uv_n.outputs['Y'],
                                   input_n.outputs['V Scale ' + tex_type],
                                   input_n.outputs['Rescale Enabled'],
                                   rescale_inv_n.outputs[0],
                                   output_n.inputs['UV ' + tex_type])


def __init_rescale_component__(node_tree, uv_type, location, uv_socket, uv_x_socket, uv_y_socket,
                               v_scale_socket, rescale_socket, rescale_inv_socket, uv_output_socket):
    """Creates nodes for one UV rescale component.

    :param node_tree: node tree of the uv rescale group
    :type node_tree: bpy.types.NodeTree
    :param uv_type: string for prefixing nodes
    :type uv_type: str
    :param location: location of the first component element
    :type location: (int, int)
    :param uv_socket: original UV
    :type uv_socket: bpy.types.NodeSocketVector
    :param uv_x_socket: U part of original UV
    :type uv_x_socket: bpy.types.NodeSocketFloat
    :param uv_y_socket: V part of original UV
    :type uv_y_socket: bpy.types.NodeSocketFloat
    :param v_scale_socket: v scale input parameter
    :type v_scale_socket: bpy.types.NodeSocketFloat
    :param rescale_socket:
    :type rescale_socket: bpy.types.NodeSocketFloat
    :param rescale_inv_socket:
    :type rescale_inv_socket: bpy.types.NodeSocketFloat
    :param uv_output_socket:
    :type uv_output_socket: bpy.types.NodeSocketVector
    """

    pos_x_shift = 185

    # create nodes
    mult_vscale_n = node_tree.nodes.new("ShaderNodeMath")
    mult_vscale_n.name = mult_vscale_n.label = _MULT_V_SCALE_PREFIX + uv_type
    mult_vscale_n.location = (location[0] + pos_x_shift * 1, location[1] + 200)
    mult_vscale_n.operation = "MULTIPLY"

    combine_vscale_uv_n = node_tree.nodes.new("ShaderNodeCombineXYZ")
    combine_vscale_uv_n.name = combine_vscale_uv_n.label = _COMBINE_V_SCALE_PREFIX + uv_type
    combine_vscale_uv_n.location = (location[0] + pos_x_shift * 2, location[1] + 200)

    mult_rescaled_uv_n = node_tree.nodes.new("ShaderNodeVectorMath")
    mult_rescaled_uv_n.name = mult_rescaled_uv_n.label = _MULT_RESCALED_UV_PREFIX + uv_type
    mult_rescaled_uv_n.location = (location[0] + pos_x_shift * 3, location[1] + 200)
    mult_rescaled_uv_n.operation = "MULTIPLY"

    mult_unscaled_uv_n = node_tree.nodes.new("ShaderNodeVectorMath")
    mult_unscaled_uv_n.name = mult_unscaled_uv_n.label = _MULT_UNSCALED_UV_PREFIX + uv_type
    mult_unscaled_uv_n.location = (location[0] + pos_x_shift * 3, location[1])
    mult_unscaled_uv_n.operation = "MULTIPLY"

    combine_uv_n = node_tree.nodes.new("ShaderNodeVectorMath")
    combine_uv_n.name = combine_uv_n.label = _COMBINE_UV_PREFIX + uv_type
    combine_uv_n.location = (location[0] + pos_x_shift * 4, location[1] + 100)
    combine_uv_n.operation = "ADD"

    # create links
    node_tree.links.new(mult_vscale_n.inputs[0], uv_y_socket)
    node_tree.links.new(mult_vscale_n.inputs[1], v_scale_socket)

    node_tree.links.new(combine_vscale_uv_n.inputs[0], uv_x_socket)
    node_tree.links.new(combine_vscale_uv_n.inputs[1], mult_vscale_n.outputs[0])

    node_tree.links.new(mult_rescaled_uv_n.inputs[0], combine_vscale_uv_n.outputs[0])
    node_tree.links.new(mult_rescaled_uv_n.inputs[1], rescale_socket)
    node_tree.links.new(mult_unscaled_uv_n.inputs[0], uv_socket)
    node_tree.links.new(mult_unscaled_uv_n.inputs[1], rescale_inv_socket)

    node_tree.links.new(combine_uv_n.inputs[0], mult_rescaled_uv_n.outputs[0])
    node_tree.links.new(combine_uv_n.inputs[1], mult_unscaled_uv_n.outputs[0])

    node_tree.links.new(uv_output_socket, combine_uv_n.outputs[0])
