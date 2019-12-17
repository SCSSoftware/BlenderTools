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


class Grass(Dif):
    NORMAL_TRANS_NODE = "UpNormal"

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

        # init parent
        Dif.init(node_tree)

        geom_n = node_tree.nodes[Dif.GEOM_NODE]
        lighting_eval_n = node_tree.nodes[Dif.LIGHTING_EVAL_NODE]

        # nodes creation
        normal_trans_n = node_tree.nodes.new("ShaderNodeVectorTransform")
        normal_trans_n.name = normal_trans_n.label = Grass.NORMAL_TRANS_NODE
        normal_trans_n.location = (geom_n.location.x, geom_n.location.y - 250)
        normal_trans_n.vector_type = "NORMAL"
        normal_trans_n.convert_from = "OBJECT"
        normal_trans_n.convert_to = "WORLD"
        normal_trans_n.inputs['Vector'].default_value = (0, 0, 1)  # up normal in object space

        # links creation
        node_tree.links.new(lighting_eval_n.inputs['Normal Vector'], normal_trans_n.outputs['Vector'])

        # enable hardcoded flavour
        Dif.set_alpha_test_flavor(node_tree, True)
