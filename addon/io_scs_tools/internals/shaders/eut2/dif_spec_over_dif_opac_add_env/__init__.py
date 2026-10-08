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

# Copyright (C) 2025-2026: Michaleczeq

from ..dif_spec_over_dif_opac import DifSpecOverDifOpac
from ..std_passes.add_env import StdAddEnv


class DifSpecOverDifOpacAddEnv(DifSpecOverDifOpac, StdAddEnv):
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
        DifSpecOverDifOpac.init(node_tree)
        StdAddEnv.add(node_tree,
                      DifSpecOverDifOpac.GEOM_NODE,
                      node_tree.nodes[DifSpecOverDifOpac.SPEC_COL_NODE].outputs['Color'],
                      node_tree.nodes[DifSpecOverDifOpac.BASE_TEX_NODE].outputs['Alpha'],
                      node_tree.nodes[DifSpecOverDifOpac.LIGHTING_EVAL_NODE].outputs['Normal'],
                      node_tree.nodes[DifSpecOverDifOpac.COMPOSE_LIGHTING_NODE].inputs['Env Color'])
