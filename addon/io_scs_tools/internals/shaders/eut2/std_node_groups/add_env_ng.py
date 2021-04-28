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

# Copyright (C) 2015-2021: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.internals.shaders.eut2.std_node_groups import fresnel_legacy_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import fresnel_schlick_ng

ADD_ENV_G = _MAT_consts.node_group_prefix + "AddEnvGroup"

_ENV_STRENGTH_MULT_NODE = "EnvStrengthMultiplier"
_ENV_WEIGHT_MULT_NODE = "EnvWeightMultiplier"
_ENV_SPEC_MULT_NODE = "EnvSpecMultiplier"
_REFL_TEX_MULT_NODE = "ReflectionTexMultiplier"
_REFL_TEX_COL_MULT_NODE = "ReflTexColorMultiplier"
_TEX_FRESNEL_MULT_NODE = "TextureFresnelMultiplier"
_GLOBAL_ENV_FACTOR_NODE = "GlobalEnvFactor"
_GLOBAL_ENV_MULT_NODE = "GlobalEnvMultiplier"
_FRESNEL_LEGACY_GNODE = "FresnelLegacyGroup"
_FRESNEL_SCHLICK_GNODE = "FresnelSchlickGroup"
_FRESNEL_TYPE_MIX_NODE = "Fresnel Mix"


def get_node_group():
    """Gets node group for calcualtion of environment addition color.

    :return: node group which calculates environment addition color
    :rtype: bpy.types.NodeGroup
    """

    if __group_needs_recreation__():
        __create_node_group__()

    return bpy.data.node_groups[ADD_ENV_G]


def set_global_env_factor(value):
    """Sets global environment factor multiplication to the node group.

    NOTE: We are using global factor as we can not determinate if texture is generated one or static one and
    based on that decide how much of envirnoment should be applied to result.
    So for closest result to game this factor should be "env_static_mod" variable from "sun_profile" multiplied
    with "env" variable from "sun_profile".
    This way static cubemaps will be used as in game, however even generated cubemaps well mostl work well,
    becuase expected values of that multiplication is from 0 to 1.0.

    :param value: global enironment factor (should come from sun profile)
    :type value: float
    """

    get_node_group().nodes[_GLOBAL_ENV_FACTOR_NODE].outputs[0].default_value = value


def reset_lighting_params():
    """Resets lighting to default values.
    """
    set_global_env_factor(_LIGHTING_consts.default_env)


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    # 2. existence of GLOBAL_ENV_FACTOR_NODE which was added in BT version 1.5
    return (ADD_ENV_G not in bpy.data.node_groups or
            _GLOBAL_ENV_FACTOR_NODE not in bpy.data.node_groups[ADD_ENV_G].nodes or
            _ENV_STRENGTH_MULT_NODE not in bpy.data.node_groups[ADD_ENV_G].nodes or
            _ENV_WEIGHT_MULT_NODE not in bpy.data.node_groups[ADD_ENV_G].nodes)


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

    if ADD_ENV_G not in bpy.data.node_groups:  # creation

        add_env_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ADD_ENV_G)

    else:  # recreation

        add_env_g = bpy.data.node_groups[ADD_ENV_G]

        # delete all inputs and outputs
        add_env_g.inputs.clear()
        add_env_g.outputs.clear()

        # delete all old nodes and links as they will be recreated now with actual version
        add_env_g.nodes.clear()

    # inputs defining
    add_env_g.inputs.new("NodeSocketFloat", "Fresnel Type")
    add_env_g.inputs.new("NodeSocketFloat", "Fresnel Scale")
    add_env_g.inputs.new("NodeSocketFloat", "Fresnel Bias")
    add_env_g.inputs.new("NodeSocketVector", "Normal Vector")
    add_env_g.inputs.new("NodeSocketVector", "Reflection Normal Vector")
    add_env_g.inputs.new("NodeSocketFloat", "Apply Fresnel")
    add_env_g.inputs.new("NodeSocketColor", "Reflection Texture Color")
    add_env_g.inputs.new("NodeSocketFloat", "Base Texture Alpha")
    add_env_g.inputs.new("NodeSocketColor", "Env Factor Color")
    add_env_g.inputs.new("NodeSocketColor", "Specular Color")
    add_env_g.inputs.new("NodeSocketColor", "Weighted Color")
    add_env_g.inputs.new("NodeSocketFloat", "Strength Multiplier")

    # outputs defining
    add_env_g.outputs.new("NodeSocketColor", "Environment Addition Color")

    # node creation
    input_n = add_env_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    output_n = add_env_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y)

    env_weight_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    env_weight_mult_n.name = env_weight_mult_n.label = _ENV_WEIGHT_MULT_NODE
    env_weight_mult_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y - 500)
    env_weight_mult_n.operation = "MULTIPLY"

    fresnel_legacy_n = add_env_g.nodes.new("ShaderNodeGroup")
    fresnel_legacy_n.name = fresnel_legacy_n.label = _FRESNEL_LEGACY_GNODE
    fresnel_legacy_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 300)
    fresnel_legacy_n.node_tree = fresnel_legacy_ng.get_node_group()
    fresnel_legacy_n.inputs['Scale'].default_value = 0.9
    fresnel_legacy_n.inputs['Bias'].default_value = 0.2

    fresnel_schlick_n = add_env_g.nodes.new("ShaderNodeGroup")
    fresnel_schlick_n.name = fresnel_schlick_n.label = _FRESNEL_SCHLICK_GNODE
    fresnel_schlick_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 100)
    fresnel_schlick_n.node_tree = fresnel_schlick_ng.get_node_group()
    fresnel_schlick_n.inputs['Bias'].default_value = 0.2

    env_spec_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    env_spec_mult_n.name = env_spec_mult_n.label = _ENV_SPEC_MULT_NODE
    env_spec_mult_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 350)
    env_spec_mult_n.operation = "MULTIPLY"

    refl_tex_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    refl_tex_mult_n.name = refl_tex_mult_n.label = _REFL_TEX_MULT_NODE
    refl_tex_mult_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 150)
    refl_tex_mult_n.operation = "MULTIPLY"

    fresnel_type_mix_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    fresnel_type_mix_n.name = fresnel_type_mix_n.label = _FRESNEL_TYPE_MIX_NODE
    fresnel_type_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 200)
    fresnel_type_mix_n.blend_type = "MIX"

    refl_tex_col_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    refl_tex_col_mult_n.name = refl_tex_col_mult_n.label = _REFL_TEX_COL_MULT_NODE
    refl_tex_col_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y - 200)
    refl_tex_col_mult_n.operation = "MULTIPLY"

    tex_fresnel_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    tex_fresnel_mult_n.name = tex_fresnel_mult_n.label = _TEX_FRESNEL_MULT_NODE
    tex_fresnel_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)
    tex_fresnel_mult_n.blend_type = "MULTIPLY"

    global_env_factor_n = add_env_g.nodes.new("ShaderNodeValue")
    global_env_factor_n.name = global_env_factor_n.label = _GLOBAL_ENV_FACTOR_NODE
    global_env_factor_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y - 200)

    global_env_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    global_env_mult_n.name = global_env_mult_n.label = _GLOBAL_ENV_MULT_NODE
    global_env_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y)
    global_env_mult_n.operation = "MULTIPLY"

    env_strength_mult_n = add_env_g.nodes.new("ShaderNodeVectorMath")
    env_strength_mult_n.name = env_strength_mult_n.label = _ENV_STRENGTH_MULT_NODE
    env_strength_mult_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y - 100)
    env_strength_mult_n.operation = "MULTIPLY"

    # links
    # pass 1
    add_env_g.links.new(env_weight_mult_n.inputs[0], input_n.outputs['Specular Color'])
    add_env_g.links.new(env_weight_mult_n.inputs[1], input_n.outputs['Weighted Color'])

    # pass 2
    add_env_g.links.new(env_spec_mult_n.inputs[0], input_n.outputs['Env Factor Color'])
    add_env_g.links.new(env_spec_mult_n.inputs[1], env_weight_mult_n.outputs[0])

    add_env_g.links.new(refl_tex_mult_n.inputs[0], input_n.outputs['Reflection Texture Color'])
    add_env_g.links.new(refl_tex_mult_n.inputs[1], input_n.outputs['Base Texture Alpha'])

    add_env_g.links.new(fresnel_legacy_n.inputs['Reflection Normal Vector'], input_n.outputs['Reflection Normal Vector'])
    add_env_g.links.new(fresnel_legacy_n.inputs['Normal Vector'], input_n.outputs['Normal Vector'])
    add_env_g.links.new(fresnel_legacy_n.inputs['Scale'], input_n.outputs['Fresnel Scale'])
    add_env_g.links.new(fresnel_legacy_n.inputs['Bias'], input_n.outputs['Fresnel Bias'])

    add_env_g.links.new(fresnel_schlick_n.inputs['Reflection Normal Vector'], input_n.outputs['Reflection Normal Vector'])
    add_env_g.links.new(fresnel_schlick_n.inputs['Normal Vector'], input_n.outputs['Normal Vector'])
    add_env_g.links.new(fresnel_schlick_n.inputs['Bias'], input_n.outputs['Fresnel Bias'])

    # pass 3
    add_env_g.links.new(fresnel_type_mix_n.inputs['Fac'], input_n.outputs['Fresnel Type'])
    add_env_g.links.new(fresnel_type_mix_n.inputs['Color1'], fresnel_legacy_n.outputs['Fresnel Factor'])
    add_env_g.links.new(fresnel_type_mix_n.inputs['Color2'], fresnel_schlick_n.outputs['Fresnel Factor'])

    add_env_g.links.new(refl_tex_col_mult_n.inputs[0], refl_tex_mult_n.outputs[0])
    add_env_g.links.new(refl_tex_col_mult_n.inputs[1], env_spec_mult_n.outputs[0])

    # pass 4
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Fac'], input_n.outputs['Apply Fresnel'])
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Color1'], refl_tex_col_mult_n.outputs[0])
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Color2'], fresnel_type_mix_n.outputs['Color'])

    # pass 5
    add_env_g.links.new(global_env_mult_n.inputs[0], tex_fresnel_mult_n.outputs['Color'])
    add_env_g.links.new(global_env_mult_n.inputs[1], global_env_factor_n.outputs['Value'])

    # pass 6
    add_env_g.links.new(env_strength_mult_n.inputs[0], global_env_mult_n.outputs[0])
    add_env_g.links.new(env_strength_mult_n.inputs[1], input_n.outputs['Strength Multiplier'])

    # output pass
    add_env_g.links.new(output_n.inputs['Environment Addition Color'], env_strength_mult_n.outputs[0])

    # set default lighting
    reset_lighting_params()
