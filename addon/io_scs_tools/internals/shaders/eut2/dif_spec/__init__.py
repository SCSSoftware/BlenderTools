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

from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.eut2.std_node_groups import alpha_remap_ng
from io_scs_tools.internals.shaders.flavors import asafew


class DifSpec(Dif):
    SPEC_MULT_NODE = "SpecMultiplier"
    REMAP_ALPHA_GNODE = "RemapAlphaToWeight"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        DifSpec.init(node_tree, disable_remap_alpha=False)

    @staticmethod
    def init(node_tree, disable_remap_alpha=False):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param disable_remap_alpha: shoudl alpha remaping with weight factors (used for alpha test safe weighting) be disabled?
        :type disable_remap_alpha: bool
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # init parent
        Dif.init(node_tree)

        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[Dif.SPEC_COL_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]

        # node creation
        spec_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_mult_n.name = DifSpec.SPEC_MULT_NODE
        spec_mult_n.label = DifSpec.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        spec_mult_n.operation = "MULTIPLY"

        remap_alpha_n = None
        if not disable_remap_alpha:
            remap_alpha_n = node_tree.nodes.new("ShaderNodeGroup")
            remap_alpha_n.name = remap_alpha_n.label = DifSpec.REMAP_ALPHA_GNODE
            remap_alpha_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1900)
            remap_alpha_n.node_tree = alpha_remap_ng.get_node_group()
            remap_alpha_n.inputs['Factor1'].default_value = 1.0
            remap_alpha_n.inputs['Factor2'].default_value = 0.0

        # links creation
        if not disable_remap_alpha:
            node_tree.links.new(remap_alpha_n.inputs['Alpha'], base_tex_n.outputs['Alpha'])
            node_tree.links.new(spec_mult_n.inputs[1], remap_alpha_n.outputs['Weighted Alpha'])
        else:
            node_tree.links.new(spec_mult_n.inputs[1], base_tex_n.outputs['Alpha'])

        node_tree.links.new(spec_mult_n.inputs[0], spec_col_n.outputs['Color'])

        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_mult_n.outputs[0])

    @staticmethod
    def set_asafew_flavor(node_tree, switch_on):
        """Set alpha test safe weight flavor to this shader.

        NOTE: there is no safety check if remap was enabled on initialization
        thus calling this setter can result in error.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        remap_alpha_n = node_tree.nodes[DifSpec.REMAP_ALPHA_GNODE]

        if switch_on:
            asafew.init(node_tree, remap_alpha_n)
        else:
            asafew.delete(node_tree, remap_alpha_n)
