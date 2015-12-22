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


from io_scs_tools.internals.shaders.eut2.dif import Dif


class DifLum(Dif):
    LUM_MIX_NODE = "LuminosityMix"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # init parent
        Dif.init(node_tree)

        output_n = node_tree.nodes[Dif.OUTPUT_NODE]
        out_mat_n = node_tree.nodes[Dif.OUT_MAT_NODE]
        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]

        # move existing
        output_n.location.x += pos_x_shift

        # nodes creation
        lum_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        lum_mix_n.name = DifLum.LUM_MIX_NODE
        lum_mix_n.label = DifLum.LUM_MIX_NODE
        lum_mix_n.location = (out_mat_n.location.x + pos_x_shift, out_mat_n.location.y + 200)
        lum_mix_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(lum_mix_n.inputs['Fac'], base_tex_n.outputs['Value'])
        node_tree.links.new(lum_mix_n.inputs['Color1'], out_mat_n.outputs['Color'])
        node_tree.links.new(lum_mix_n.inputs['Color2'], base_tex_n.outputs['Color'])

        node_tree.links.new(output_n.inputs['Color'], lum_mix_n.outputs['Color'])

    @staticmethod
    def set_lvcol_flavor(node_tree, switch_on):
        """Set (vertex color*luminance) flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        lum_mix_n = node_tree.nodes[DifLum.LUM_MIX_NODE]

        if switch_on:
            node_tree.links.new(lum_mix_n.inputs['Color2'], vcol_mult_n.outputs['Color'])
        else:
            node_tree.links.new(lum_mix_n.inputs['Color2'], base_tex_n.outputs['Color'])
