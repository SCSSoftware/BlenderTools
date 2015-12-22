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


class DifSpec(Dif):
    SPEC_MULT_NODE = "SpecMultiplier"

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

        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[Dif.SPEC_COL_NODE]
        out_mat_n = node_tree.nodes[Dif.OUT_MAT_NODE]

        # node creation
        spec_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        spec_mult_n.name = DifSpec.SPEC_MULT_NODE
        spec_mult_n.label = DifSpec.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        spec_mult_n.blend_type = "MULTIPLY"
        spec_mult_n.inputs['Fac'].default_value = 1

        # links creation
        node_tree.links.new(spec_mult_n.inputs['Color2'], base_tex_n.outputs['Value'])
        node_tree.links.new(spec_mult_n.inputs['Color1'], spec_col_n.outputs['Color'])

        node_tree.links.new(out_mat_n.inputs['Spec'], spec_mult_n.outputs['Color'])
