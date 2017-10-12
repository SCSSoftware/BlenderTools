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


from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv


class DifSpecAddEnv(DifSpec, StdAddEnv):
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

        # init parents
        DifSpec.init(node_tree)
        StdAddEnv.add(node_tree,
                      DifSpec.GEOM_NODE,
                      node_tree.nodes[DifSpec.SPEC_COL_NODE].outputs['Color'],
                      node_tree.nodes[DifSpec.REMAP_ALPHA_GNODE].outputs['Weighted Alpha'],
                      node_tree.nodes[DifSpec.OUT_MAT_NODE].outputs['Normal'],
                      node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE].inputs['Env Color'])

    @staticmethod
    def set_indenv_flavor(node_tree, switch_on):
        """Set independent environment flavor to this shader.

        NOTE: flavor is not implemented indepenently because it is used only by this shader

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if indenv should be switched on or off
        :type switch_on: bool
        """

        add_env_group_n = node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE]
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]

        if switch_on:
            node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs["Specular Color"].default_value = (1.0,) * 4
            for link in node_tree.links:
                if link.from_node == spec_col_n and link.to_node == add_env_group_n:
                    node_tree.links.remove(link)
                    break
        else:
            node_tree.links.new(add_env_group_n.inputs["Specular Color"], spec_col_n.outputs["Color"])
