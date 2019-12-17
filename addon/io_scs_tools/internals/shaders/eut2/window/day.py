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

from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.internals.shaders.eut2.window import window_uv_offset_ng


class WindowDay(DifSpecAddEnv):
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

        # init parent
        DifSpecAddEnv.init(node_tree)

        geom_n = node_tree.nodes[DifSpecAddEnv.GEOM_NODE]
        uv_map_n = node_tree.nodes[DifSpecAddEnv.UVMAP_NODE]
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]

        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE])

        # create nodes
        uv_recalc_n = node_tree.nodes.new("ShaderNodeGroup")
        uv_recalc_n.name = window_uv_offset_ng.WINDOW_UV_OFFSET_G
        uv_recalc_n.label = window_uv_offset_ng.WINDOW_UV_OFFSET_G
        uv_recalc_n.location = (start_pos_x, start_pos_y + 1500)
        uv_recalc_n.node_tree = window_uv_offset_ng.get_node_group()

        # create links
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_col_n.outputs['Color'])

        node_tree.links.new(uv_recalc_n.inputs['UV'], uv_map_n.outputs['UV'])
        node_tree.links.new(uv_recalc_n.inputs['Normal'], geom_n.outputs['Normal'])
        node_tree.links.new(uv_recalc_n.inputs['Incoming'], geom_n.outputs['Incoming'])

        node_tree.links.new(base_tex_n.inputs['Vector'], uv_recalc_n.outputs['UV Final'])

    @staticmethod
    def set_lightmap_texture(node_tree, texture):
        """Set lightmap texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to lightmap texture node
        :type texture: bpy.types.Texture
        """
        pass  # NOTE: light map texture is not used in day version of effect, so pass it

    @staticmethod
    def set_lightmap_texture_settings(node_tree, settings):
        """Set lightmap texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        pass  # NOTE: light map texture is not used in day version of effect, so pass it

    @staticmethod
    def set_lightmap_uv(node_tree, uv_layer):
        """Set UV layer to lightmap texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for lightmap texture
        :type uv_layer: str
        """
        pass  # NOTE: light map texture is not used in day version of effect, so pass it
