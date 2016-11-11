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


from io_scs_tools.internals.shaders.eut2.dif_spec_weight import DifSpecWeight
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv


class DifSpecWeightAddEnv(DifSpecWeight, StdAddEnv):
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
        DifSpecWeight.init(node_tree)
        StdAddEnv.add(node_tree,
                      DifSpecWeight.GEOM_NODE,
                      DifSpecWeight.SPEC_COL_NODE,
                      DifSpecWeight.BASE_TEX_NODE,
                      DifSpecWeight.OUT_MAT_NODE,
                      DifSpecWeight.COMPOSE_LIGHTING_NODE)

    @staticmethod
    def set_reflection_texture(node_tree, texture):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture object which should be used for reflection
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecWeightAddEnv.REFL_TEX_NODE].texture = texture
