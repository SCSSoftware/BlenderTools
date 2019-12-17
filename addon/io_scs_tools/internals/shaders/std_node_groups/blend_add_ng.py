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

BLEND_ADD_G = _MAT_consts.node_group_prefix + "BlendAddPass"

_SHADER_TO_RGB_NODE = "ShaderToRGB"
_EMISSION_SHADER_NODE = "Emission"
_TRANSPARENT_NODE = "Transparent"
_ADD_SHADER_NODE = "AddShader"


def get_node_group():
    """Gets node group for blending pass.

    :return: node group which adds blending pass
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[BLEND_ADD_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return BLEND_ADD_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates add blending group.

    Inputs: Shader
    Outputs: Shader
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if BLEND_ADD_G not in bpy.data.node_groups:  # creation

        blend_add_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=BLEND_ADD_G)

    else:  # recreation

        blend_add_g = bpy.data.node_groups[BLEND_ADD_G]

        # delete all inputs and outputs
        blend_add_g.inputs.clear()
        blend_add_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        blend_add_g.nodes.clear()

    # inputs defining
    blend_add_g.inputs.new("NodeSocketShader", "Shader")

    # outputs defining
    blend_add_g.outputs.new("NodeSocketShader", "Shader")

    # node creation
    input_n = blend_add_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = blend_add_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)

    shader_to_rgb_n = blend_add_g.nodes.new("ShaderNodeShaderToRGB")
    shader_to_rgb_n.name = shader_to_rgb_n.label = _SHADER_TO_RGB_NODE
    shader_to_rgb_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y)

    emission_shader_n = blend_add_g.nodes.new("ShaderNodeEmission")
    emission_shader_n.name = emission_shader_n.label = _EMISSION_SHADER_NODE
    emission_shader_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 50)
    emission_shader_n.inputs['Strength'].default_value = 1.0

    transparent_shader_n = blend_add_g.nodes.new("ShaderNodeBsdfTransparent")
    transparent_shader_n.name = transparent_shader_n.label = _TRANSPARENT_NODE
    transparent_shader_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 50)

    add_shader_n = blend_add_g.nodes.new("ShaderNodeAddShader")
    add_shader_n.name = add_shader_n.label = _ADD_SHADER_NODE
    add_shader_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)

    # links
    # input pass
    blend_add_g.links.new(shader_to_rgb_n.inputs['Shader'], input_n.outputs['Shader'])

    # pass 1
    blend_add_g.links.new(emission_shader_n.inputs['Color'], shader_to_rgb_n.outputs['Color'])

    # pass 2
    blend_add_g.links.new(add_shader_n.inputs[0], emission_shader_n.outputs['Emission'])
    blend_add_g.links.new(add_shader_n.inputs[1], transparent_shader_n.outputs['BSDF'])

    # output pass
    blend_add_g.links.new(output_n.inputs['Shader'], add_shader_n.outputs['Shader'])
