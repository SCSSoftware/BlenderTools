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
from io_scs_tools.internals.shaders.eut2.std_node_groups import refl_normal
from io_scs_tools.internals.shaders.eut2.std_node_groups import fresnel

ADD_ENV_G = _MAT_consts.node_group_prefix + "AddEnvGroup"

COMBINE_BASE_ALPHA_NODE = "CombineBaseAlpha"
ENV_SPEC_MULT_NODE = "EnvSpecMultiplier"
REFL_TEX_MULT_NODE = "ReflectionTexMultiplier"
REFL_TEX_COL_MULT_NODE = "ReflTexColorMultiplier"
TEX_FRESNEL_MULT_NODE = "TextureFresnelMultiplier"
GLOBAL_ENV_FACTOR_NODE = "GlobalEnvFactor"
GLOBAL_ENV_MULT_NODE = "GlobalEnvMultiplier"
FRESNEL_GNODE = "FresnelGroup"
REFL_NORMAL_GNODE = "ReflNormalGroup"


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

    get_node_group().nodes[GLOBAL_ENV_FACTOR_NODE].outputs[0].default_value = value


def __group_needs_recreation__():
    """Tells if group needs recreation.

    :return: True group isn't up to date and has to be (re)created; False if group doesn't need to be (re)created
    :rtype: bool
    """
    # current checks:
    # 1. group existence in blender data block
    # 2. existence of GLOBAL_ENV_FACTOR_NODE which was added in BT version 1.5
    return ADD_ENV_G not in bpy.data.node_groups or GLOBAL_ENV_FACTOR_NODE not in bpy.data.node_groups[ADD_ENV_G].nodes


def __create_node_group__():
    """Creates add env group.

    Inputs: Fresnel Scale, Fresnel Bias, Normal Vector, View Vector, Apply Fresnel,
    Reflection Texture Color, Base Texture Alpha, Env Factor Color and Specular Color
    Outputs: Environment Addition Color
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    if ADD_ENV_G not in bpy.data.node_groups:  # creation

        add_env_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=ADD_ENV_G)

        # inputs defining
        add_env_g.inputs.new("NodeSocketFloat", "Fresnel Scale")
        add_env_g.inputs.new("NodeSocketFloat", "Fresnel Bias")
        add_env_g.inputs.new("NodeSocketVector", "Normal Vector")
        add_env_g.inputs.new("NodeSocketVector", "View Vector")
        add_env_g.inputs.new("NodeSocketFloat", "Apply Fresnel")
        add_env_g.inputs.new("NodeSocketColor", "Reflection Texture Color")
        add_env_g.inputs.new("NodeSocketFloat", "Base Texture Alpha")
        add_env_g.inputs.new("NodeSocketColor", "Env Factor Color")
        add_env_g.inputs.new("NodeSocketColor", "Specular Color")

        # outputs defining
        add_env_g.outputs.new("NodeSocketColor", "Environment Addition Color")

    else:  # recreation

        add_env_g = bpy.data.node_groups[ADD_ENV_G]

        # delete all old nodes and links as they will be recreated now with actual version
        add_env_g.nodes.clear()

    # node creation
    input_n = add_env_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    output_n = add_env_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    refl_normal_gn = add_env_g.nodes.new("ShaderNodeGroup")
    refl_normal_gn.name = REFL_NORMAL_GNODE
    refl_normal_gn.label = REFL_NORMAL_GNODE
    refl_normal_gn.location = (start_pos_x + pos_x_shift, start_pos_y)
    refl_normal_gn.node_tree = refl_normal.get_node_group()

    combine_base_alpha_n = add_env_g.nodes.new("ShaderNodeCombineRGB")
    combine_base_alpha_n.name = COMBINE_BASE_ALPHA_NODE
    combine_base_alpha_n.label = COMBINE_BASE_ALPHA_NODE
    combine_base_alpha_n.location = (start_pos_x + pos_x_shift, start_pos_y - 150)

    env_spec_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    env_spec_mult_n.name = ENV_SPEC_MULT_NODE
    env_spec_mult_n.label = ENV_SPEC_MULT_NODE
    env_spec_mult_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 350)
    env_spec_mult_n.blend_type = "MULTIPLY"
    env_spec_mult_n.inputs['Fac'].default_value = 1

    refl_tex_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    refl_tex_mult_n.name = REFL_TEX_MULT_NODE
    refl_tex_mult_n.label = REFL_TEX_MULT_NODE
    refl_tex_mult_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y - 150)
    refl_tex_mult_n.blend_type = "MULTIPLY"
    refl_tex_mult_n.inputs['Fac'].default_value = 1

    refl_tex_col_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    refl_tex_col_mult_n.name = REFL_TEX_COL_MULT_NODE
    refl_tex_col_mult_n.label = REFL_TEX_COL_MULT_NODE
    refl_tex_col_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y - 200)
    refl_tex_col_mult_n.blend_type = "MULTIPLY"
    refl_tex_col_mult_n.inputs['Fac'].default_value = 1

    fresnel_gn = add_env_g.nodes.new("ShaderNodeGroup")
    fresnel_gn.name = FRESNEL_GNODE
    fresnel_gn.label = FRESNEL_GNODE
    fresnel_gn.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 150)
    fresnel_gn.node_tree = fresnel.get_node_group()
    fresnel_gn.inputs['Scale'].default_value = 0.9
    fresnel_gn.inputs['Bias'].default_value = 0.2

    tex_fresnel_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    tex_fresnel_mult_n.name = TEX_FRESNEL_MULT_NODE
    tex_fresnel_mult_n.label = TEX_FRESNEL_MULT_NODE
    tex_fresnel_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y)
    tex_fresnel_mult_n.blend_type = "MULTIPLY"
    tex_fresnel_mult_n.inputs['Fac'].default_value = 1

    global_env_factor_n = add_env_g.nodes.new("ShaderNodeValue")
    global_env_factor_n.name = GLOBAL_ENV_FACTOR_NODE
    global_env_factor_n.label = GLOBAL_ENV_FACTOR_NODE
    global_env_factor_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y - 200)

    global_env_mult_n = add_env_g.nodes.new("ShaderNodeMixRGB")
    global_env_mult_n.name = GLOBAL_ENV_MULT_NODE
    global_env_mult_n.label = GLOBAL_ENV_MULT_NODE
    global_env_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y)
    global_env_mult_n.blend_type = "MULTIPLY"
    global_env_mult_n.inputs['Fac'].default_value = 1

    # geometry links
    add_env_g.links.new(refl_normal_gn.inputs['View Vector'], input_n.outputs['View Vector'])
    add_env_g.links.new(refl_normal_gn.inputs['Normal Vector'], input_n.outputs['Normal Vector'])

    add_env_g.links.new(combine_base_alpha_n.inputs['R'], input_n.outputs['Base Texture Alpha'])
    add_env_g.links.new(combine_base_alpha_n.inputs['G'], input_n.outputs['Base Texture Alpha'])
    add_env_g.links.new(combine_base_alpha_n.inputs['B'], input_n.outputs['Base Texture Alpha'])

    # pass 1
    add_env_g.links.new(env_spec_mult_n.inputs['Color1'], input_n.outputs['Env Factor Color'])
    add_env_g.links.new(env_spec_mult_n.inputs['Color2'], input_n.outputs['Specular Color'])

    add_env_g.links.new(refl_tex_mult_n.inputs['Color1'], input_n.outputs['Reflection Texture Color'])
    add_env_g.links.new(refl_tex_mult_n.inputs['Color2'], combine_base_alpha_n.outputs['Image'])

    # pass 2
    add_env_g.links.new(fresnel_gn.inputs['Reflection Normal Vector'], refl_normal_gn.outputs['Reflection Normal'])
    add_env_g.links.new(fresnel_gn.inputs['Normal Vector'], input_n.outputs['Normal Vector'])
    add_env_g.links.new(fresnel_gn.inputs['Scale'], input_n.outputs['Fresnel Scale'])
    add_env_g.links.new(fresnel_gn.inputs['Bias'], input_n.outputs['Fresnel Bias'])

    add_env_g.links.new(refl_tex_col_mult_n.inputs['Color1'], refl_tex_mult_n.outputs['Color'])
    add_env_g.links.new(refl_tex_col_mult_n.inputs['Color2'], env_spec_mult_n.outputs['Color'])

    # pass 3
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Fac'], input_n.outputs['Apply Fresnel'])
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Color1'], refl_tex_col_mult_n.outputs['Color'])
    add_env_g.links.new(tex_fresnel_mult_n.inputs['Color2'], fresnel_gn.outputs['Fresnel Factor'])

    # pass 4
    add_env_g.links.new(global_env_mult_n.inputs['Color1'], tex_fresnel_mult_n.outputs['Color'])
    add_env_g.links.new(global_env_mult_n.inputs['Color2'], global_env_factor_n.outputs['Value'])

    # output pass
    add_env_g.links.new(output_n.inputs['Environment Addition Color'], global_env_mult_n.outputs['Color'])
