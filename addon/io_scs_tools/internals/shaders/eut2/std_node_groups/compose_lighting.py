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

# Copyright (C) 2016: SCS Software

import bpy
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.utils import convert as _convert_utils

COMPOSE_LIGHTING_G = _MAT_consts.node_group_prefix + "ComposeLighting"

# D = lighting diffuse
# A = AddAmbient * SunProfileAmbient
# DL = D + A
# SL = lighting specular
# DC = attributes diffuse
# DS = attributes specular
# R = (DC * DL) + (SC * SL) --> R = DC * D + SC * SL + DC * A
#
# instead of implementing original formula we can just add (DC * A) to combined (DC * D + SC * SL)
# which is output of blender material. Additionally lest step is adding environment if specified.

_ADD_AMBIENT_COL_NODE = "AdditionalAmbientColor"  # sun profile ambient color
_MULT_A_NODE = "A=AddAmbient*SunProfileAmbient"
_MULT_DCA_NODE = "DC*A"
_MIX_MATERIAL_DCA_NODE = "Result=MaterialOut+DC*A"
_MIX_FINAL_NODE = "Result=Result+Env"


def get_node_group():
    """Gets node group for calcualtion of final lighting color.

    :return: node group which calculates finall shader output color
    :rtype: bpy.types.NodeGroup
    """

    if COMPOSE_LIGHTING_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[COMPOSE_LIGHTING_G]


def set_additional_ambient_col(color):
    """Sets ambient color which should be used when material is using additional ambient.

    :param color: ambient color from sun profile (not converted to srgb)
    :type color: list
    """

    color = _convert_utils.linear_to_srgb(color)
    color = _convert_utils.to_node_color(color)

    get_node_group().nodes[_ADD_AMBIENT_COL_NODE].outputs[0].default_value = color


def __create_node_group__():
    """Creates compose lighting group.

    Inputs: AddAmbient, Diffuse Color, Material Color, Env Color
    Outputs: Composed Color
    """

    start_pos_x = 0
    start_pos_y = 0

    pos_x_shift = 185

    compose_light_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=COMPOSE_LIGHTING_G)

    # inputs defining
    compose_light_g.inputs.new("NodeSocketFloat", "AddAmbient")
    compose_light_g.inputs.new("NodeSocketColor", "Diffuse Color")
    compose_light_g.inputs.new("NodeSocketColor", "Material Color")
    compose_light_g.inputs.new("NodeSocketColor", "Env Color")
    input_n = compose_light_g.nodes.new("NodeGroupInput")
    input_n.location = (start_pos_x - pos_x_shift, start_pos_y)

    # outputs defining
    compose_light_g.outputs.new("NodeSocketColor", "Composed Color")
    output_n = compose_light_g.nodes.new("NodeGroupOutput")
    output_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y)

    # nodes creation
    add_ambient_col_n = compose_light_g.nodes.new("ShaderNodeRGB")
    add_ambient_col_n.name = add_ambient_col_n.label = _ADD_AMBIENT_COL_NODE
    add_ambient_col_n.location = (start_pos_x + pos_x_shift * 1, start_pos_y + 400)
    add_ambient_col_n.outputs[0].default_value = (0.0,) * 4

    mult_a_n = compose_light_g.nodes.new("ShaderNodeMixRGB")
    mult_a_n.name = mult_a_n.label = _MULT_A_NODE
    mult_a_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 300)
    mult_a_n.blend_type = "MULTIPLY"
    mult_a_n.inputs["Fac"].default_value = 1

    mult_dca_n = compose_light_g.nodes.new("ShaderNodeMixRGB")
    mult_dca_n.name = mult_dca_n.label = _MULT_DCA_NODE
    mult_dca_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 200)
    mult_dca_n.blend_type = "MULTIPLY"
    mult_dca_n.inputs["Fac"].default_value = 1

    mix_material_dca_n = compose_light_g.nodes.new("ShaderNodeVectorMath")
    mix_material_dca_n.name = mix_material_dca_n.label = _MIX_MATERIAL_DCA_NODE
    mix_material_dca_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 100)
    mix_material_dca_n.operation = "ADD"

    mix_final_n = compose_light_g.nodes.new("ShaderNodeVectorMath")
    mix_final_n.name = mix_final_n.label = _MIX_FINAL_NODE
    mix_final_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y)
    mix_final_n.operation = "ADD"

    # links creation
    compose_light_g.links.new(mult_a_n.inputs["Color1"], add_ambient_col_n.outputs["Color"])
    compose_light_g.links.new(mult_a_n.inputs["Color2"], input_n.outputs["AddAmbient"])

    compose_light_g.links.new(mult_dca_n.inputs["Color1"], mult_a_n.outputs["Color"])
    compose_light_g.links.new(mult_dca_n.inputs["Color2"], input_n.outputs["Diffuse Color"])

    compose_light_g.links.new(mix_material_dca_n.inputs[0], mult_dca_n.outputs["Color"])
    compose_light_g.links.new(mix_material_dca_n.inputs[1], input_n.outputs["Material Color"])

    compose_light_g.links.new(mix_final_n.inputs[0], mix_material_dca_n.outputs["Vector"])
    compose_light_g.links.new(mix_final_n.inputs[1], input_n.outputs["Env Color"])

    compose_light_g.links.new(output_n.inputs["Composed Color"], mix_final_n.outputs["Vector"])
