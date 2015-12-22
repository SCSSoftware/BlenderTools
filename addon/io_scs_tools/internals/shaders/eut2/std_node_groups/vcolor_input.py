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
from io_scs_tools.consts import Colors as _COL_consts
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.consts import Mesh as _MESH_consts

VCOLOR_G = _MAT_consts.node_group_prefix + "VColorGroup"

_VCOL_GEOM_N = "VertexColorGeom"
_VCOL_GEOM_A_N = "VertexColorAlphaGeom"
_VCOL_GAMMA_CORR_N = "VertexColorGamma"
_VCOL_GAMMA_CORR_A_N = "VertexColorAGamma"
_VCOL_SATURATE_N = "VertexColorSaturation"
_ALPHA_TO_BW_N = "VertexColAToBW"
_VCOL_NORM_N = "VertexColorNormalize"
_VCOL_NORM_A_N = "VertexColorAlphaNormalize"


def get_node_group():
    """Gets node group for vertex color inputs.

    :return: node group which exposes vertex color input
    :rtype: bpy.types.NodeGroup
    """

    if VCOLOR_G not in bpy.data.node_groups:
        __create_vcolor_group__()

    return bpy.data.node_groups[VCOLOR_G]


def __create_vcolor_group__():
    """Creates vertex color input group.

    Inputs: None
    Outputs: Vertex Color, Vertex Color Alpha
    """

    vcol_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=VCOLOR_G)

    # outputs defining
    vcol_g.outputs.new("NodeSocketColor", "Vertex Color")
    vcol_g.outputs.new("NodeSocketFloat", "Vertex Color Alpha")
    output_n = vcol_g.nodes.new("NodeGroupOutput")
    output_n.location = (185 * 5, 0)

    # group nodes
    vcol_geom_n = vcol_g.nodes.new("ShaderNodeGeometry")
    vcol_geom_n.name = _VCOL_GEOM_N
    vcol_geom_n.label = _VCOL_GEOM_N
    vcol_geom_n.location = (185, 200)
    vcol_geom_n.color_layer = _MESH_consts.default_vcol

    vcol_a_geom_n = vcol_g.nodes.new("ShaderNodeGeometry")
    vcol_a_geom_n.name = _VCOL_GEOM_A_N
    vcol_a_geom_n.label = _VCOL_GEOM_A_N
    vcol_a_geom_n.location = (185, -100)
    vcol_a_geom_n.color_layer = _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix

    vcol_gamma_corr_n = vcol_g.nodes.new("ShaderNodeGamma")
    vcol_gamma_corr_n.name = _VCOL_GAMMA_CORR_N
    vcol_gamma_corr_n.label = _VCOL_GAMMA_CORR_N
    vcol_gamma_corr_n.location = (185 * 2, 100)
    vcol_gamma_corr_n.inputs["Gamma"].default_value = 1 / _COL_consts.gamma

    vcol_gamma_corr_a_n = vcol_g.nodes.new("ShaderNodeGamma")
    vcol_gamma_corr_a_n.name = _VCOL_GAMMA_CORR_A_N
    vcol_gamma_corr_a_n.label = _VCOL_GAMMA_CORR_A_N
    vcol_gamma_corr_a_n.location = (185 * 2, -100)
    vcol_gamma_corr_a_n.inputs["Gamma"].default_value = 1 / _COL_consts.gamma

    vcol_saturate_n = vcol_g.nodes.new("ShaderNodeHueSaturation")
    vcol_saturate_n.name = _VCOL_SATURATE_N
    vcol_saturate_n.label = _VCOL_SATURATE_N
    vcol_saturate_n.inputs['Hue'].default_value = 0.5
    vcol_saturate_n.inputs['Saturation'].default_value = _COL_consts.saturation
    vcol_saturate_n.inputs['Value'].default_value = 1
    vcol_saturate_n.inputs['Fac'].default_value = 1
    vcol_saturate_n.location = (185 * 3, 100)

    alpha_to_bw_n = vcol_g.nodes.new("ShaderNodeRGBToBW")
    alpha_to_bw_n.name = _ALPHA_TO_BW_N
    alpha_to_bw_n.label = _ALPHA_TO_BW_N
    alpha_to_bw_n.location = (185 * 3, -100)

    normalize_vcol_n = vcol_g.nodes.new("ShaderNodeMixRGB")
    normalize_vcol_n.name = _VCOL_NORM_N
    normalize_vcol_n.label = _VCOL_NORM_N
    normalize_vcol_n.location = (185 * 4, 100)
    normalize_vcol_n.blend_type = "MULTIPLY"
    normalize_vcol_n.inputs["Fac"].default_value = 1
    normalize_vcol_n.inputs["Color2"].default_value = (2.0,) * 4

    normalize_vcol_a_n = vcol_g.nodes.new("ShaderNodeMath")
    normalize_vcol_a_n.name = _VCOL_NORM_A_N
    normalize_vcol_a_n.label = _VCOL_NORM_A_N
    normalize_vcol_a_n.location = (185 * 4, -100)
    normalize_vcol_a_n.operation = "MULTIPLY"
    normalize_vcol_a_n.inputs[1].default_value = 2.0

    # group links
    vcol_g.links.new(vcol_gamma_corr_n.inputs["Color"], vcol_geom_n.outputs["Vertex Color"])
    vcol_g.links.new(vcol_gamma_corr_a_n.inputs["Color"], vcol_a_geom_n.outputs["Vertex Color"])

    vcol_g.links.new(vcol_saturate_n.inputs["Color"], vcol_gamma_corr_n.outputs["Color"])
    vcol_g.links.new(alpha_to_bw_n.inputs["Color"], vcol_gamma_corr_a_n.outputs["Color"])

    vcol_g.links.new(normalize_vcol_n.inputs["Color1"], vcol_saturate_n.outputs["Color"])
    vcol_g.links.new(normalize_vcol_a_n.inputs[0], alpha_to_bw_n.outputs["Val"])

    vcol_g.links.new(output_n.inputs["Vertex Color"], normalize_vcol_n.outputs["Color"])
    vcol_g.links.new(output_n.inputs["Vertex Color Alpha"], normalize_vcol_a_n.outputs["Value"])
