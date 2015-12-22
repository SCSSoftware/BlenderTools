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
from io_scs_tools.internals.shaders.eut2.std_node_groups import window_uv_offset


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
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        out_mat_n = node_tree.nodes[DifSpecAddEnv.OUT_MAT_NODE]

        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE])

        # create nodes
        uv_recalc_gn = node_tree.nodes.new("ShaderNodeGroup")
        uv_recalc_gn.name = window_uv_offset.WINDOW_UV_OFFSET_G
        uv_recalc_gn.label = window_uv_offset.WINDOW_UV_OFFSET_G
        uv_recalc_gn.location = (start_pos_x, start_pos_y + 1500)
        uv_recalc_gn.node_tree = window_uv_offset.get_node_group()

        # create links
        node_tree.links.new(out_mat_n.inputs["Spec"], spec_col_n.outputs["Color"])

        node_tree.links.new(uv_recalc_gn.inputs["UV"], geom_n.outputs["UV"])
        node_tree.links.new(uv_recalc_gn.inputs["Normal"], geom_n.outputs["Normal"])

        node_tree.links.new(base_tex_n.inputs["Vector"], uv_recalc_gn.outputs["UV Final"])

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
    def set_lightmap_uv(node_tree, uv_layer):
        """Set UV layer to lightmap texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for lightmap texture
        :type uv_layer: str
        """
        pass  # NOTE: light map texture is not used in day version of effect, so pass it
