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
# Copyright (C) 2025-2026: Michaleczeq

from . import detail_nmap
from ..dif_spec_weight import DifSpecWeight
from ..std_passes.add_env import StdAddEnv


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
                      node_tree.nodes[DifSpecWeight.SPEC_COL_NODE].outputs['Color'],
                      node_tree.nodes[DifSpecWeight.REMAP_ALPHA_GNODE].outputs['Weighted Alpha'],
                      node_tree.nodes[DifSpecWeight.LIGHTING_EVAL_NODE].outputs['Normal'],
                      node_tree.nodes[DifSpecWeight.COMPOSE_LIGHTING_NODE].inputs['Env Color'])

        vcol_scale_n = node_tree.nodes[DifSpecWeight.VCOLOR_SCALE_NODE]
        add_env_gn = node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE]

        # links creation
        node_tree.links.new(add_env_gn.inputs['Weighted Color'], vcol_scale_n.outputs[0])

    @staticmethod
    def set_nmap2_flavor(node_tree, switch_on):
        """Set secondary normal map flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if normal map should be switched on or off
        :type switch_on: bool
        """

        if switch_on:

            # find minimal y position for input nodes and position flavor beneath it
            min_y = None
            for node in node_tree.nodes:
                if node.location.x <= 185 and (min_y is None or min_y > node.location.y):
                    min_y = node.location.y

            lighting_eval_n = node_tree.nodes[DifSpecWeightAddEnv.LIGHTING_EVAL_NODE]
            geom_n = node_tree.nodes[DifSpecWeightAddEnv.GEOM_NODE]
            location = (lighting_eval_n.location.x - 185, min_y - 400)

            detail_nmap.init(node_tree, location, lighting_eval_n.inputs['Normal Vector'], geom_n.outputs['Normal'])
        else:
            detail_nmap.delete(node_tree)

    @staticmethod
    def set_nmap_detail_uv(node_tree, uv_layer):
        """Set UV layer to detail normal map texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for detail nmap texture
        :type uv_layer: str
        """

        detail_nmap.set_detail_uv(node_tree, uv_layer)
            
    @staticmethod
    def set_nmap_detail_texture(node_tree, texture):
        """Set detail normal map texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to detail nmap texture node
        :type texture: bpy.types.Texture
        """

        detail_nmap.set_detail_texture(node_tree, texture)

    @staticmethod
    def set_nmap_detail_texture_settings(node_tree, settings):
        """Set detail normal map texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        detail_nmap.set_detail_texture_settings(node_tree, settings)
