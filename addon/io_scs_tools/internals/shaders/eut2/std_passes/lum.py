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

# Copyright (C) 2021-2022: SCS Software

from io_scs_tools.internals.shaders.eut2 import parameters
from io_scs_tools.internals.shaders.std_node_groups import output_shader_ng


class StdLum:
    LUM_A_DECODE_NODE = "LumDecodeGammaLumScale"
    LUM_COL_MODULATE_NODE = "LumColModulate"
    LUM_A_MODULATE_NODE = "LumAModulate"
    LUM_COL_LVCOL_MULT_NODE = "LumColVColModulate"
    LUM_A_LVCOL_MULT_NODE = "LumAVColModulate"
    LUM_RESULT_MULT_NODE = "LumResult=RGB*A"
    LUM_MIX_FINAL_NODE = "LumOutFinal=LitResult+LuminanceResult"
    LUM_OUT_SHADER_NODE = "LumShader"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def add(node_tree, base_texel_socket, base_texel_a_socket, lit_result_col_socket, lit_result_a_socket, output_socket):
        """Add add env pass to node tree with links.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param base_texel_socket: base texel node socket from which color will be taken
        :type base_texel_socket: bpy.type.NodeSocket
        :param base_texel_a_socket: socket from which alpha will be taken (if None it won't be used)
        :type base_texel_a_socket: bpy.type.NodeSocket
        :param lit_result_col_socket: lit result node socket from which color will be taken
        :type lit_result_col_socket: bpy.type.NodeSocket
        :param lit_result_a_socket: lit result alpha node socket from which alpha will be taken
        :type lit_result_a_socket: bpy.type.NodeSocket
        :param output_socket: output socket to which result will be given
        :type output_socket: bpy.type.NodeSocket
        """

        pos_x_shift = 185

        output_n = output_socket.node
        output_n.location.x += pos_x_shift * 7

        # node creation
        lum_a_decode_n = node_tree.nodes.new("ShaderNodeMath")
        lum_a_decode_n.name = lum_a_decode_n.label = StdLum.LUM_A_DECODE_NODE
        lum_a_decode_n.location = (output_n.location.x - pos_x_shift * 6, output_n.location.y - 200)
        lum_a_decode_n.operation = "MULTIPLY"

        lum_col_modul_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_col_modul_n.name = lum_col_modul_n.label = StdLum.LUM_COL_MODULATE_NODE
        lum_col_modul_n.location = (output_n.location.x - pos_x_shift * 5, output_n.location.y)
        lum_col_modul_n.operation = "MULTIPLY"
        lum_col_modul_n.inputs[0].default_value = (1,) * 3

        lum_a_modul_n = node_tree.nodes.new("ShaderNodeMath")
        lum_a_modul_n.name = lum_a_modul_n.label = StdLum.LUM_A_MODULATE_NODE
        lum_a_modul_n.location = (output_n.location.x - pos_x_shift * 5, output_n.location.y - 200)
        lum_a_modul_n.operation = "MULTIPLY"
        lum_a_modul_n.inputs[0].default_value = 1

        lum_col_lvcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_col_lvcol_mult_n.name = lum_col_lvcol_mult_n.label = StdLum.LUM_COL_LVCOL_MULT_NODE
        lum_col_lvcol_mult_n.location = (output_n.location.x - pos_x_shift * 4, output_n.location.y)
        lum_col_lvcol_mult_n.operation = "MULTIPLY"
        lum_col_lvcol_mult_n.inputs[1].default_value = (1,) * 3

        lum_a_lvcol_mult_n = node_tree.nodes.new("ShaderNodeMath")
        lum_a_lvcol_mult_n.name = lum_a_lvcol_mult_n.label = StdLum.LUM_A_LVCOL_MULT_NODE
        lum_a_lvcol_mult_n.location = (output_n.location.x - pos_x_shift * 4, output_n.location.y - 200)
        lum_a_lvcol_mult_n.operation = "MULTIPLY"
        lum_a_lvcol_mult_n.inputs[1].default_value = 1

        lum_result_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_result_mult_n.name = lum_result_mult_n.label = StdLum.LUM_RESULT_MULT_NODE
        lum_result_mult_n.location = (output_n.location.x - pos_x_shift * 3, output_n.location.y)
        lum_result_mult_n.operation = "MULTIPLY"

        lum_mix_final_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_mix_final_n.name = lum_mix_final_n.label = StdLum.LUM_MIX_FINAL_NODE
        lum_mix_final_n.location = (output_n.location.x - pos_x_shift * 2, output_n.location.y)
        lum_mix_final_n.operation = "ADD"

        lum_out_shader_n = node_tree.nodes.new("ShaderNodeGroup")
        lum_out_shader_n.name = lum_out_shader_n.label = StdLum.LUM_OUT_SHADER_NODE
        lum_out_shader_n.location = (output_n.location.x - pos_x_shift * 1, output_n.location.y)
        lum_out_shader_n.node_tree = output_shader_ng.get_node_group()

        # geometry links
        node_tree.links.new(lum_a_decode_n.inputs[0], base_texel_a_socket)
        node_tree.links.new(lum_a_decode_n.inputs[1], base_texel_a_socket)

        node_tree.links.new(lum_col_modul_n.inputs[1], base_texel_socket)
        node_tree.links.new(lum_a_modul_n.inputs[1], lum_a_decode_n.outputs[0])

        node_tree.links.new(lum_col_lvcol_mult_n.inputs[0], lum_col_modul_n.outputs[0])
        node_tree.links.new(lum_a_lvcol_mult_n.inputs[0], lum_a_modul_n.outputs[0])

        node_tree.links.new(lum_result_mult_n.inputs[0], lum_col_lvcol_mult_n.outputs[0])
        node_tree.links.new(lum_result_mult_n.inputs[1], lum_a_lvcol_mult_n.outputs[0])

        node_tree.links.new(lum_mix_final_n.inputs[0], lit_result_col_socket)
        node_tree.links.new(lum_mix_final_n.inputs[1], lum_result_mult_n.outputs[0])

        node_tree.links.new(lum_out_shader_n.inputs['Color'], lum_mix_final_n.outputs[0])
        node_tree.links.new(lum_out_shader_n.inputs['Alpha'], lit_result_a_socket)

        node_tree.links.new(output_socket, lum_out_shader_n.outputs['Shader'])

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminosity boost factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: luminosity output represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        luminance_boost = aux_property[0]['value']
        node_tree.nodes[StdLum.LUM_A_MODULATE_NODE].inputs[0].default_value = parameters.get_material_luminosity(luminance_boost)
