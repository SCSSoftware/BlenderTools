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

# Copyright (C) 2015-2019: SCS Software

from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec


class DifSpecWeight(DifSpec):
    SPEC_DIFF_MULT_NODE = "SpecDiffMultiplier"

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
        DifSpec.init(node_tree)

        lighting_eval_n = node_tree.nodes[DifSpec.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpec.VCOLOR_SCALE_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]

        # move existing
        lighting_eval_n.location.x += pos_x_shift
        compose_lighting_n.location.x += pos_x_shift
        output_n.location.x += pos_x_shift

        # node creation
        spec_diff_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_diff_mult_n.name = DifSpecWeight.SPEC_DIFF_MULT_NODE
        spec_diff_mult_n.label = DifSpecWeight.SPEC_DIFF_MULT_NODE
        spec_diff_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1900)
        spec_diff_mult_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(spec_diff_mult_n.inputs[0], spec_mult_n.outputs[0])
        node_tree.links.new(spec_diff_mult_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_diff_mult_n.outputs[0])
