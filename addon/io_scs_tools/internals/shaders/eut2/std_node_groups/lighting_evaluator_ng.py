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
from math import cos, radians
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.utils import convert as _convert_utils

LIGHTING_EVALUATOR_G = _MAT_consts.node_group_prefix + "LightingEvaluator"

_LIGHT_DIR_NODE = "LightDir"
_CAM_TO_WORLD_NODE = "CameraToWorld"
_CAM_NORMALIZE_NODE = "NormalizedCameraWorld"

_LIGHT_AMB_COLOR_NODE = "AmbientLightColor"
_LIGHT_DIFF_COLOR_NODE = "DiffuseLightColor"
_LIGHT_SPEC_COLOR_NODE = "SpecularLightColor"

_N_DOT_L_NODE = "NDotL=dot(NormalVector, NLight)"
_DIFF_FACTOR_NODE = "DiffFac=max(0, NDotL)"
_DIFF_MULT_NODE = "Diff=DiffuseLightColor*DiffFac"
_DIFF_AMB_ADD_NODE = "D=AmbientLight+Diff"  # goes to Diffuse Lighting output

_DIFF_FLAT_MULT_NODE = "DFlat=DiffuseLightColor*0.4"

_DIFF_FLAT_NODE = "FlatFilter"

_N_SUM_NODE = "NSum=IncomingVector+NLight"
_N_HALF_NODE = "NHalf=normalize(NSum)"
_N_DOT_H_NODE = "NDotH=dot(NormalVector, NHalf)"
_N_DOT_H_MAX_NODE = "NDotHMax=max(0.0, NDotH)"
_N_DOT_L_SPEC_CUT_NODE = "NDotLSpecCut=NDotL*10"
_SPEC_FACTOR_NODE = "SpecFac=pow(NDotHMax, Shininess)"
_SPEC_FACTOR_SMOOTH_NODE = "SpecFacSmooth=SpecFac*NDotLSpecCut"  # clamp it!
_SPEC_MULT_NODE = "S=SpecularLightColor*SpecFacSmooth"  # goes to Specular Lighting output

_SPEC_FLAT_NODE = "FlatFilter"


def get_node_group():
    """Gets node group for end result of lighting evaluator functions from our effect library.

    It's actually approximation of eut2_pass_common::forward_lighting_evaluator_t:
    1. It calculates lighting factors from: cg_lib_light::light_directional_normalized
    2. Combines factors with environment lighting: eut2_library::add_forward_light
    3. Outputs diffuse and specular lighting factors, ready to be used by material.

    :return: node group which exposes vertex color input
    :rtype: bpy.types.NodeGroup
    """

    if LIGHTING_EVALUATOR_G not in bpy.data.node_groups:
        __create_group__()

    return bpy.data.node_groups[LIGHTING_EVALUATOR_G]


def set_light_direction(sun_obj):
    """Sets light direction from sun object.

    :param sun_obj: blender object representing scs sun, from which direction will be read
    :type sun_obj: bpy.types.Object
    """
    light_dir_n = get_node_group().nodes[_LIGHT_DIR_NODE]

    rot_matrix = sun_obj.rotation_euler.to_matrix()

    light_dir_n.inputs[0].default_value = rot_matrix[0][2]
    light_dir_n.inputs[1].default_value = rot_matrix[1][2]
    light_dir_n.inputs[2].default_value = rot_matrix[2][2]

    cam_to_world_n = get_node_group().nodes[_CAM_TO_WORLD_NODE]
    cam_to_world_n.convert_from = "WORLD"


def reset_light_direction():
    """Resets light direction and uses default one which is bound to current view matrix.
    """
    light_dir_n = get_node_group().nodes[_LIGHT_DIR_NODE]

    light_dir_n.inputs[0].default_value = 0
    light_dir_n.inputs[1].default_value = cos(radians(60.0))
    light_dir_n.inputs[2].default_value = -cos(radians(60.0))

    cam_to_world_n = get_node_group().nodes[_CAM_TO_WORLD_NODE]
    cam_to_world_n.convert_from = "CAMERA"


def set_ambient_light(color):
    """Sets ambient light color to evaluator.

    :param color: color to use as ambient
    :type color: tuple[float] | list[float | mathutils.Color
    """
    get_node_group().nodes[_LIGHT_AMB_COLOR_NODE].outputs[0].default_value = _convert_utils.to_node_color(color, from_linear=True)


def set_diffuse_light(color):
    """Sets diffuse light color to evaluator.

    :param color: color to use as diffuse
    :type color: tuple[float] | list[float | mathutils.Color
    """
    get_node_group().nodes[_LIGHT_DIFF_COLOR_NODE].outputs[0].default_value = _convert_utils.to_node_color(color, from_linear=True)


def set_specular_light(color):
    """Sets specular light color to evaluator.

    :param color: color to use as specular
    :type color: tuple[float] | list[float | mathutils.Color
    """
    get_node_group().nodes[_LIGHT_SPEC_COLOR_NODE].outputs[0].default_value = _convert_utils.to_node_color(color, from_linear=True)


def reset_lighting_params():
    """Resets lighting to default values.
    """
    reset_light_direction()
    set_ambient_light(_LIGHTING_consts.default_ambient)
    set_diffuse_light(_LIGHTING_consts.default_diffuse)
    set_specular_light(_LIGHTING_consts.default_specular)


def __create_group__():
    """Creates group and their nodes.

    Inputs: Normal Vector, Incoming Vector, Shininess
    Outputs: Diffuse Lighting, Specular Lighting
    """

    start_pos_x = 0
    pos_x_shift = 185

    if LIGHTING_EVALUATOR_G not in bpy.data.node_groups:  # creation

        lighting_eval_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=LIGHTING_EVALUATOR_G)

        # inputs defining
        lighting_eval_g.inputs.new("NodeSocketVector", "Normal Vector")  # n_normal
        lighting_eval_g.inputs.new("NodeSocketVector", "Incoming Vector")  # n_eye
        lighting_eval_g.inputs.new("NodeSocketFloat", "Shininess")  # specular_exponent
        lighting_eval_g.inputs.new("NodeSocketFloat", "Flat Lighting")  # flat lighting switch, should be 0 or 1

        # outputs defining
        lighting_eval_g.outputs.new("NodeSocketColor", "Diffuse Lighting")  # final diffuse lighting
        lighting_eval_g.outputs.new("NodeSocketColor", "Specular Lighting")  # final specular lighting
        lighting_eval_g.outputs.new("NodeSocketVector", "Normal")  # bypassed normal, to have one access point to final normal

    else:  # recreation

        lighting_eval_g = bpy.data.node_groups[LIGHTING_EVALUATOR_G]

        # delete all old nodes and links as they will be recreated now with actual version
        lighting_eval_g.nodes.clear()

    # node creation
    # 1. inputs and light infos
    input_n = lighting_eval_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, -100)

    output_n = lighting_eval_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 11, 0)

    light_dir_n = lighting_eval_g.nodes.new("ShaderNodeCombineXYZ")
    light_dir_n.name = light_dir_n.label = _LIGHT_DIR_NODE
    light_dir_n.location = (start_pos_x - pos_x_shift * 2, 100)

    cam_to_world_n = lighting_eval_g.nodes.new("ShaderNodeVectorTransform")
    cam_to_world_n.name = cam_to_world_n.label = _CAM_TO_WORLD_NODE
    cam_to_world_n.location = (start_pos_x - pos_x_shift, 100)
    cam_to_world_n.vector_type = "VECTOR"
    cam_to_world_n.convert_from = "CAMERA"
    cam_to_world_n.convert_to = "WORLD"

    cam_normalize_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    cam_normalize_n.name = cam_normalize_n.label = _CAM_NORMALIZE_NODE
    cam_normalize_n.location = (start_pos_x, 100)
    cam_normalize_n.operation = "NORMALIZE"

    light_amb_n = lighting_eval_g.nodes.new("ShaderNodeRGB")
    light_amb_n.name = light_amb_n.label = _LIGHT_AMB_COLOR_NODE
    light_amb_n.location = (start_pos_x, 600)

    light_diff_n = lighting_eval_g.nodes.new("ShaderNodeRGB")
    light_diff_n.name = light_diff_n.label = _LIGHT_DIFF_COLOR_NODE
    light_diff_n.location = (start_pos_x, 400)

    light_spec_n = lighting_eval_g.nodes.new("ShaderNodeRGB")
    light_spec_n.name = light_spec_n.label = _LIGHT_SPEC_COLOR_NODE
    light_spec_n.location = (start_pos_x, -400)

    # 2. diffuse lighting
    n_dot_l_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    n_dot_l_n.name = n_dot_l_n.label = _N_DOT_L_NODE
    n_dot_l_n.location = (start_pos_x + pos_x_shift * 2, 200)
    n_dot_l_n.operation = "DOT_PRODUCT"

    diff_factor_n = lighting_eval_g.nodes.new("ShaderNodeMath")
    diff_factor_n.name = diff_factor_n.label = _DIFF_FACTOR_NODE
    diff_factor_n.location = (start_pos_x + pos_x_shift * 3, 300)
    diff_factor_n.operation = "MAXIMUM"
    diff_factor_n.inputs[1].default_value = 0.0

    diff_mult_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    diff_mult_n.name = diff_mult_n.label = _DIFF_MULT_NODE
    diff_mult_n.location = (start_pos_x + pos_x_shift * 4, 450)
    diff_mult_n.operation = "MULTIPLY"

    diff_flat_mult_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    diff_flat_mult_n.name = diff_flat_mult_n.label = _DIFF_FLAT_MULT_NODE
    diff_flat_mult_n.location = (start_pos_x + pos_x_shift * 4, 250)
    diff_flat_mult_n.operation = "MULTIPLY"
    diff_flat_mult_n.inputs[1].default_value = (0.4,) * 3

    diff_flat_n = lighting_eval_g.nodes.new("ShaderNodeMixRGB")
    diff_flat_n.name = diff_flat_n.label = _DIFF_FLAT_NODE
    diff_flat_n.location = (start_pos_x + pos_x_shift * 5, 400)
    diff_flat_n.blend_type = "MIX"

    diff_amb_add_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    diff_amb_add_n.name = diff_amb_add_n.label = _DIFF_AMB_ADD_NODE
    diff_amb_add_n.location = (start_pos_x + pos_x_shift * 6, 600)
    diff_amb_add_n.operation = "ADD"

    # 3. specular lighting
    n_sum_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    n_sum_n.name = n_sum_n.label = _N_SUM_NODE
    n_sum_n.location = (start_pos_x + pos_x_shift * 2, 0)
    n_sum_n.operation = "ADD"

    n_half_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    n_half_n.name = n_half_n.label = _N_HALF_NODE
    n_half_n.location = (start_pos_x + pos_x_shift * 3, 0)
    n_half_n.operation = "NORMALIZE"

    n_dot_h_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    n_dot_h_n.name = n_dot_h_n.label = _N_DOT_H_NODE
    n_dot_h_n.location = (start_pos_x + pos_x_shift * 4, -100)
    n_dot_h_n.operation = "DOT_PRODUCT"

    n_dot_h_max_n = lighting_eval_g.nodes.new("ShaderNodeMath")
    n_dot_h_max_n.name = n_dot_h_max_n.label = _N_DOT_H_MAX_NODE
    n_dot_h_max_n.location = (start_pos_x + pos_x_shift * 5, -100)
    n_dot_h_max_n.operation = "MAXIMUM"
    n_dot_h_max_n.inputs[1].default_value = 0.0

    n_dot_l_spec_cut_n = lighting_eval_g.nodes.new("ShaderNodeMath")
    n_dot_l_spec_cut_n.name = n_dot_l_spec_cut_n.label = _N_DOT_L_SPEC_CUT_NODE
    n_dot_l_spec_cut_n.location = (start_pos_x + pos_x_shift * 6, 0)
    n_dot_l_spec_cut_n.operation = "MULTIPLY"
    n_dot_l_spec_cut_n.inputs[1].default_value = 10.0
    n_dot_l_spec_cut_n.use_clamp = True

    spec_factor_n = lighting_eval_g.nodes.new("ShaderNodeMath")
    spec_factor_n.name = spec_factor_n.label = _SPEC_FACTOR_NODE
    spec_factor_n.location = (start_pos_x + pos_x_shift * 6, -200)
    spec_factor_n.operation = "POWER"

    spec_factor_smooth_n = lighting_eval_g.nodes.new("ShaderNodeMath")
    spec_factor_smooth_n.name = spec_factor_smooth_n.label = _SPEC_FACTOR_SMOOTH_NODE
    spec_factor_smooth_n.location = (start_pos_x + pos_x_shift * 7, 0)
    spec_factor_smooth_n.operation = "MULTIPLY"

    spec_mult_n = lighting_eval_g.nodes.new("ShaderNodeVectorMath")
    spec_mult_n.name = spec_mult_n.label = _SPEC_MULT_NODE
    spec_mult_n.location = (start_pos_x + pos_x_shift * 8, -200)
    spec_mult_n.operation = "MULTIPLY"

    spec_flat_n = lighting_eval_g.nodes.new("ShaderNodeMixRGB")
    spec_flat_n.name = spec_flat_n.label = _SPEC_FLAT_NODE
    spec_flat_n.location = (start_pos_x + pos_x_shift * 9, -200)
    spec_flat_n.blend_type = "MIX"
    spec_flat_n.inputs["Color2"].default_value = (0.0,) * 4

    # group links
    # pass #-2
    lighting_eval_g.links.new(cam_to_world_n.inputs["Vector"], light_dir_n.outputs["Vector"])

    # pass #-1
    lighting_eval_g.links.new(cam_normalize_n.inputs[0], cam_to_world_n.outputs["Vector"])

    # pass #1
    lighting_eval_g.links.new(n_dot_l_n.inputs[0], cam_normalize_n.outputs["Vector"])
    lighting_eval_g.links.new(n_dot_l_n.inputs[1], input_n.outputs["Normal Vector"])

    lighting_eval_g.links.new(n_sum_n.inputs[0], cam_normalize_n.outputs["Vector"])
    lighting_eval_g.links.new(n_sum_n.inputs[1], input_n.outputs["Incoming Vector"])

    # pass #2
    lighting_eval_g.links.new(diff_factor_n.inputs[0], n_dot_l_n.outputs["Value"])

    lighting_eval_g.links.new(n_half_n.inputs[0], n_sum_n.outputs["Vector"])

    # pass #3
    lighting_eval_g.links.new(diff_mult_n.inputs[0], light_diff_n.outputs["Color"])
    lighting_eval_g.links.new(diff_mult_n.inputs[1], diff_factor_n.outputs["Value"])

    lighting_eval_g.links.new(diff_flat_mult_n.inputs[0], light_diff_n.outputs["Color"])

    lighting_eval_g.links.new(n_dot_h_n.inputs[0], n_half_n.outputs["Vector"])
    lighting_eval_g.links.new(n_dot_h_n.inputs[1], input_n.outputs["Normal Vector"])

    # pass #4
    lighting_eval_g.links.new(diff_flat_n.inputs["Fac"], input_n.outputs["Flat Lighting"])
    lighting_eval_g.links.new(diff_flat_n.inputs["Color1"], diff_mult_n.outputs[0])
    lighting_eval_g.links.new(diff_flat_n.inputs["Color2"], diff_flat_mult_n.outputs[0])

    lighting_eval_g.links.new(n_dot_h_max_n.inputs[0], n_dot_h_n.outputs["Value"])

    # pass #5
    lighting_eval_g.links.new(diff_amb_add_n.inputs[0], light_amb_n.outputs["Color"])
    lighting_eval_g.links.new(diff_amb_add_n.inputs[1], diff_flat_n.outputs["Color"])

    lighting_eval_g.links.new(n_dot_l_spec_cut_n.inputs[0], n_dot_l_n.outputs["Value"])

    lighting_eval_g.links.new(spec_factor_n.inputs[0], n_dot_h_max_n.outputs["Value"])
    lighting_eval_g.links.new(spec_factor_n.inputs[1], input_n.outputs["Shininess"])

    # pass #6
    lighting_eval_g.links.new(spec_factor_smooth_n.inputs[0], n_dot_l_spec_cut_n.outputs["Value"])
    lighting_eval_g.links.new(spec_factor_smooth_n.inputs[1], spec_factor_n.outputs["Value"])

    # pass #7
    lighting_eval_g.links.new(spec_mult_n.inputs[0], spec_factor_smooth_n.outputs["Value"])
    lighting_eval_g.links.new(spec_mult_n.inputs[1], light_spec_n.outputs["Color"])

    # pass #8
    lighting_eval_g.links.new(spec_flat_n.inputs["Fac"], input_n.outputs["Flat Lighting"])
    lighting_eval_g.links.new(spec_flat_n.inputs["Color1"], spec_mult_n.outputs[0])

    # pass: out
    lighting_eval_g.links.new(output_n.inputs["Diffuse Lighting"], diff_amb_add_n.outputs[0])
    lighting_eval_g.links.new(output_n.inputs["Specular Lighting"], spec_flat_n.outputs["Color"])
    lighting_eval_g.links.new(output_n.inputs["Normal"], input_n.outputs["Normal Vector"])

    # set default lighting
    reset_lighting_params()
