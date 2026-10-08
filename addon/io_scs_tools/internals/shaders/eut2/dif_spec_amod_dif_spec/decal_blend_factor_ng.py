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

# Copyright (C) 2024-2026: Michaleczeq

import bpy
from .....consts import Material as _MAT_consts

DECAL_BLEND_FACTOR_G = _MAT_consts.node_group_prefix + "DecalBlendFactor"

_MAP_VCOLA_SHIFT_NODE = "MapVColAlphaShift"
_INVERT_NEG_NODE = "InvertNegatives"
_ALPHA_1_SCALE_NODE = "AlphaScale_1"
_ALPHA_2_SCALE_NODE = "AlphaScale_2"
_BLEND_1_ABS_NODE = "BlendingAbsolute_1"
_BLEND_2_ABS_NODE = "BlendingAbsolute_2"
_MULT_1_SCALE_NODE = "MultScale_1"
_MULT_2_SCALE_NODE = "MultScale_2"
_MULT_FINAL_NODE = "MultFinal"

def get_node_group():
    """Gets node group for combining of Decal blending factors with mask texture.

    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if DECAL_BLEND_FACTOR_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[DECAL_BLEND_FACTOR_G]

def __create_node_group__():
    """Creates decal blending factor group.

    Inputs: Decal blending factor (1 & 2) and Vertex Color Alpha
    Outputs: Factor
    """

    pos_x_shift = 185

    dec_blend_fac_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=DECAL_BLEND_FACTOR_G)

    # inputs defining
    dec_blend_fac_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Vertex Alpha")
    dec_blend_fac_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Factor1")
    dec_blend_fac_g.interface.new_socket(in_out = "INPUT", socket_type = "NodeSocketFloat", name = "Factor2")

    # outputs defining
    dec_blend_fac_g.interface.new_socket(in_out = "OUTPUT", socket_type = "NodeSocketColor", name = "Factor")


    # nodes creation
    input_n = dec_blend_fac_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    output_n = dec_blend_fac_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 6, 0)

    # - column 1 -
    map_vcol_a_shift_n = dec_blend_fac_g.nodes.new("ShaderNodeMapping")
    map_vcol_a_shift_n.name = map_vcol_a_shift_n.label = _MAP_VCOLA_SHIFT_NODE
    map_vcol_a_shift_n.location = (pos_x_shift, 100)
    map_vcol_a_shift_n.vector_type = "POINT"
    map_vcol_a_shift_n.inputs['Location'].default_value = (-0.5,) * 3

    # - column 2 -
    invert_neg_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    invert_neg_n.name = invert_neg_n.label = _INVERT_NEG_NODE
    invert_neg_n.location = (pos_x_shift * 2, 250)
    invert_neg_n.operation = "MULTIPLY"
    invert_neg_n.inputs[1].default_value = (-1,) * 3

    # - column 3 -
    alpha_1_scale_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    alpha_1_scale_n.name = alpha_1_scale_n.label = _ALPHA_1_SCALE_NODE
    alpha_1_scale_n.location = (pos_x_shift * 3, 250)
    alpha_1_scale_n.operation = "MULTIPLY"
    alpha_1_scale_n.inputs[1].default_value = (2,) * 3

    blending_1_abs_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    blending_1_abs_n.name = blending_1_abs_n.label = _BLEND_1_ABS_NODE
    blending_1_abs_n.location = (pos_x_shift * 3, 50)
    blending_1_abs_n.operation = "ABSOLUTE"

    alpha_2_scale_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    alpha_2_scale_n.name = alpha_2_scale_n.label = _ALPHA_2_SCALE_NODE
    alpha_2_scale_n.location = (pos_x_shift * 3, -100)
    alpha_2_scale_n.operation = "MULTIPLY"
    alpha_2_scale_n.inputs[1].default_value = (2,) * 3

    blending_2_abs_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    blending_2_abs_n.name = blending_2_abs_n.label = _BLEND_2_ABS_NODE
    blending_2_abs_n.location = (pos_x_shift * 3, -300)
    blending_2_abs_n.operation = "ABSOLUTE"

    # - column 4 -
    mult_1_scale_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    mult_1_scale_n.name = mult_1_scale_n.label = _MULT_1_SCALE_NODE
    mult_1_scale_n.location = (pos_x_shift * 4, 100)
    mult_1_scale_n.operation = "MULTIPLY"

    mult_2_scale_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    mult_2_scale_n.name = mult_2_scale_n.label = _MULT_2_SCALE_NODE
    mult_2_scale_n.location = (pos_x_shift * 4, -200)
    mult_2_scale_n.operation = "MULTIPLY"

    # - column 5 -
    mult_final_n = dec_blend_fac_g.nodes.new("ShaderNodeVectorMath")
    mult_final_n.name = mult_final_n.label = _MULT_FINAL_NODE
    mult_final_n.location = (pos_x_shift * 5, 0)
    mult_final_n.operation = "MAXIMUM"


    # links creation
    # - column 0 -
    dec_blend_fac_g.links.new(input_n.outputs["Vertex Alpha"], map_vcol_a_shift_n.inputs["Vector"])
    dec_blend_fac_g.links.new(input_n.outputs["Factor1"], blending_1_abs_n.inputs["Vector"])
    dec_blend_fac_g.links.new(input_n.outputs["Factor2"], blending_2_abs_n.inputs["Vector"])

    # - column 1 -
    dec_blend_fac_g.links.new(map_vcol_a_shift_n.outputs["Vector"], invert_neg_n.inputs[0])
    dec_blend_fac_g.links.new(map_vcol_a_shift_n.outputs["Vector"], alpha_2_scale_n.inputs[0])

    # - column 2 -
    dec_blend_fac_g.links.new(invert_neg_n.outputs["Vector"], alpha_1_scale_n.inputs[0])

    # - column 3 -
    dec_blend_fac_g.links.new(alpha_1_scale_n.outputs["Vector"], mult_1_scale_n.inputs[0])
    dec_blend_fac_g.links.new(blending_1_abs_n.outputs["Vector"], mult_1_scale_n.inputs[1])

    dec_blend_fac_g.links.new(alpha_2_scale_n.outputs["Vector"], mult_2_scale_n.inputs[0])
    dec_blend_fac_g.links.new(blending_2_abs_n.outputs["Vector"], mult_2_scale_n.inputs[1])

    # - column 4 -
    dec_blend_fac_g.links.new(mult_1_scale_n.outputs["Vector"], mult_final_n.inputs[0])
    dec_blend_fac_g.links.new(mult_2_scale_n.outputs["Vector"], mult_final_n.inputs[1])

    # - column 5 -
    dec_blend_fac_g.links.new(mult_final_n.outputs["Vector"], output_n.inputs["Factor"])
