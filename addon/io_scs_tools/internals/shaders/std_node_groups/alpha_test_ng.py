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

ALPHA_TEST_G = _MAT_consts.node_group_prefix + "AlphaTestPass"

_SHADER_TO_RGB_NODE = "ShaderToRGB"
_ALPHA_TEST_NODE = "AlphaTest"
_ALPHA_INV_NODE = "AlphaInv"
_ALPHA_SHADER_NODE = "AlphaShader"


def get_node_group():
    """Gets node group for blending pass.

    :return: node group which adds blending pass
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ALPHA_TEST_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    return ALPHA_TEST_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates add blending group.

    Inputs: Shader, Alpha
    Outputs: Shader
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ALPHA_TEST_G not in bpy.data.node_groups:  # creation

        alpha_test_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ALPHA_TEST_G)

    else:  # recreation

        alpha_test_g = bpy.data.node_groups[ALPHA_TEST_G]

        # delete all inputs and outputs
        alpha_test_g.inputs.clear()
        alpha_test_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        alpha_test_g.nodes.clear()

    # inputs defining
    alpha_test_g.inputs.new("NodeSocketShader", "Shader")
    alpha_test_g.inputs.new("NodeSocketFloat", "Alpha")

    # outputs defining
    alpha_test_g.outputs.new("NodeSocketShader", "Shader")

    # node creation
    input_n = alpha_test_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x, start_pos_y)

    output_n = alpha_test_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)

    shader_to_rgb_n = alpha_test_g.nodes.new("ShaderNodeShaderToRGB")
    shader_to_rgb_n.name = shader_to_rgb_n.label = _SHADER_TO_RGB_NODE
    shader_to_rgb_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y)

    alpha_test_n = alpha_test_g.nodes.new("ShaderNodeMath")
    alpha_test_n.name = alpha_test_n.label = _ALPHA_TEST_NODE
    alpha_test_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y - 200)
    alpha_test_n.operation = "GREATER_THAN"
    alpha_test_n.inputs[1].default_value = 0.05

    alpha_test_inv_n = alpha_test_g.nodes.new("ShaderNodeMath")
    alpha_test_inv_n.name = alpha_test_inv_n.label = _ALPHA_INV_NODE
    alpha_test_inv_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 200)
    alpha_test_inv_n.operation = "SUBTRACT"
    alpha_test_inv_n.use_clamp = True
    alpha_test_inv_n.inputs[0].default_value = 1

    alpha_shader_n = alpha_test_g.nodes.new("ShaderNodeEeveeSpecular")
    alpha_shader_n.name = alpha_shader_n.label = _ALPHA_SHADER_NODE
    alpha_shader_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)
    alpha_shader_n.inputs["Base Color"].default_value = (0.0,) * 4
    alpha_shader_n.inputs["Specular"].default_value = (0.0,) * 4

    # create extra links
    alpha_test_g.links.new(shader_to_rgb_n.inputs['Shader'], input_n.outputs['Shader'])
    alpha_test_g.links.new(alpha_test_n.inputs[0], input_n.outputs['Alpha'])

    alpha_test_g.links.new(alpha_test_inv_n.inputs[1], alpha_test_n.outputs[0])

    alpha_test_g.links.new(alpha_shader_n.inputs['Emissive Color'], shader_to_rgb_n.outputs['Color'])
    alpha_test_g.links.new(alpha_shader_n.inputs['Transparency'], alpha_test_inv_n.outputs[0])

    alpha_test_g.links.new(output_n.inputs['Shader'], alpha_shader_n.outputs['BSDF'])
