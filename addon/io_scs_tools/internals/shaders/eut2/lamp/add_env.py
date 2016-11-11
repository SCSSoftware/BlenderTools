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

from io_scs_tools.internals.shaders.eut2.lamp import Lamp
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv


class LampAddEnv(Lamp, DifSpecAddEnv):
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
        DifSpecAddEnv.init(node_tree)
        Lamp.init(node_tree, init_dif_spec=False, start_pos_x=0, start_pos_y=500)

        out_add_lampmask_n = node_tree.nodes[Lamp.OUT_ADD_LAMPMASK_NODE]
        out_add_lampmask_n.location.y -= 300
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]

        # links fixing
        node_tree.links.new(out_add_lampmask_n.inputs["Color2"], compose_lighting_n.outputs["Composed Color"])
