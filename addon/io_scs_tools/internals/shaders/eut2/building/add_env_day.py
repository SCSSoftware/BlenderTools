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


from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv


class BuildingAddEnvDay(DifSpecAddEnv):
    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        # init parent
        DifSpecAddEnv.init(node_tree)

        geometry_n = node_tree.nodes[DifSpecAddEnv.GEOM_NODE]
        refl_tex_n = node_tree.nodes[DifSpecAddEnv.REFL_TEX_NODE]

        # change mapping of reflection texture to View coordinates, it gives better effect for plain surfaces
        node_tree.links.new(refl_tex_n.inputs['Vector'], geometry_n.outputs['View'])