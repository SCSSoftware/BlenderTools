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

# Copyright (C) 2022: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts

OUTPUT_SHADER_G = _MAT_consts.node_group_prefix + "OutputShaderGroup"

_ALPHA_CLAMP = "AlphaClamp"
_EMISSION_OUT_SHADER = "EmissionMaterial"
_TRANSPARENT_OUT_SHADER = "TransparentMaterial"
_MIX_SHADER = "MixShader"


def get_node_group():
    """Gets node group for calcualtion of shader output.

    :return: node group
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[OUTPUT_SHADER_G]


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    return OUTPUT_SHADER_G not in bpy.data.node_groups


def __create_node_group__():
    """Creates add env group.

    Specular Color - needed because our env factor is always multiplied with material specular color
    (eut2_effect_uniforms.cpp::uniform_setup_material_environment)
    Weighted Color - needed for weighted variants of environment (eut2_forward_envmap.cg::ENVMAP_WEIGHT)
    Strength Multiplier - multiplier modulating environment strength (eut2_forward_envmap.ch::ENVMAP_STRENGTH_MULTIPLIER)

    Inputs: Fresnel Scale, Fresnel Bias, Normal Vector, View Vector, Apply Fresnel,
    Reflection Texture Color, Base Texture Alpha, Env Factor Color, Specular Color, Weighted Color, Strength Multiplier
    Outputs: Environment Addition Color
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if OUTPUT_SHADER_G not in bpy.data.node_groups:  # creation

        output_shader_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=OUTPUT_SHADER_G)

    else:  # recreation

        output_shader_g = bpy.data.node_groups[OUTPUT_SHADER_G]

        # delete all inputs and outputs
        output_shader_g.inputs.clear()
        output_shader_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        output_shader_g.nodes.clear()

    # inputs defining
    output_shader_g.inputs.new("NodeSocketColor", "Color")
    output_shader_g.inputs.new("NodeSocketFloat", "Alpha")

    # always set to full opaque by default since this behaviour is expected by shaders
    # since this behaviour is epxected by effects from before.
    output_shader_g.inputs['Alpha'].default_value = 1

    # outputs defining
    output_shader_g.outputs.new("NodeSocketShader", "Shader")

    # node creation
    input_n = output_shader_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    output_n = output_shader_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y)

    emission_shader_n = output_shader_g.nodes.new("ShaderNodeEmission")
    emission_shader_n.name = emission_shader_n.label = _EMISSION_OUT_SHADER
    emission_shader_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y + 200)

    alpha_clamp_n = output_shader_g.nodes.new("ShaderNodeClamp")
    alpha_clamp_n.name = alpha_clamp_n.label = _ALPHA_CLAMP
    alpha_clamp_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y)
    alpha_clamp_n.inputs['Min'].default_value = 0.000001  # blender clips if alpha is way above, so it's safe to use it
    alpha_clamp_n.inputs['Max'].default_value = 1

    transparent_shader_n = output_shader_g.nodes.new("ShaderNodeBsdfTransparent")
    transparent_shader_n.name = transparent_shader_n.label = _TRANSPARENT_OUT_SHADER
    transparent_shader_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y - 200)

    mix_shader_n = output_shader_g.nodes.new("ShaderNodeMixShader")
    mix_shader_n.name = mix_shader_n.label = _MIX_SHADER
    mix_shader_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y)

    # links
    # pass 1
    output_shader_g.links.new(emission_shader_n.inputs['Color'], input_n.outputs['Color'])
    output_shader_g.links.new(alpha_clamp_n.inputs['Value'], input_n.outputs['Alpha'])

    # pass 2
    output_shader_g.links.new(mix_shader_n.inputs[0], alpha_clamp_n.outputs[0])
    output_shader_g.links.new(mix_shader_n.inputs[1], transparent_shader_n.outputs[0])
    output_shader_g.links.new(mix_shader_n.inputs[2], emission_shader_n.outputs[0])

    # output pass
    output_shader_g.links.new(output_n.inputs['Shader'], mix_shader_n.outputs[0])
