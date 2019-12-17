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

from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.flavors import blend_over


class Retroreflective(Dif):
    SPEC_MULT_NODE = "SpecMultiplier"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        Retroreflective.init(node_tree)

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        pos_x_shift = 185

        # init parent
        Dif.init(node_tree)

        opacity_n = node_tree.nodes[Dif.OPACITY_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        lighting_eval_n = node_tree.nodes[Dif.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]

        # modify exisiting
        lighting_eval_n.inputs['Shininess'].default_value = 60

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.SPEC_COL_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.DIFF_COL_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.DIFF_MULT_NODE])

        # node creation
        spec_mult_n = node_tree.nodes.new("ShaderNodeMath")
        spec_mult_n.name = spec_mult_n.label = Retroreflective.SPEC_MULT_NODE
        spec_mult_n.location = (opacity_n.location[0] + pos_x_shift, opacity_n.location[1])
        spec_mult_n.operation = "MULTIPLY"
        spec_mult_n.inputs[1].default_value = 0.2  # used for spcular color designed for the best visual on traffic signs

        # links creation
        node_tree.links.new(spec_mult_n.inputs[0], opacity_n.outputs['Value'])

        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], vcol_mult_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_mult_n.outputs['Value'])

    @staticmethod
    def set_retroreflective_decal_flavor(node_tree, switch_on):
        """Set depth retroreflective decal flavor to this shader.
        NOTE: this is essentially same flavor as blend_over, thus just use blend over internally

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if retroreflective decal should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            blend_over.init(node_tree)
        else:
            blend_over.delete(node_tree)
