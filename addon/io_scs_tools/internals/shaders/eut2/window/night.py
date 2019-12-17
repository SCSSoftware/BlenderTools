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

from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.internals.shaders.eut2.window import window_uv_offset_ng
from io_scs_tools.utils import material as _material_utils


class WindowNight(DifSpecAddEnv):
    SEC_UV_MAP = "SecUVMap"
    LIGHTMAP_TEX_NODE = "LightmapTex"
    BASE_LIGHTMAP_MULT_NODE = "BaseLightmapMultiplier"
    BASE_ALPHA_MULT_NODE = "BaseAlphaMultiplier"

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

        pos_x_shift = 185

        start_pos_x = 0
        start_pos_y = 0

        # init parent
        DifSpecAddEnv.init(node_tree)

        uv_map_n = node_tree.nodes[DifSpecAddEnv.UVMAP_NODE]
        geom_n = node_tree.nodes[DifSpecAddEnv.GEOM_NODE]
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        diff_mult_n = node_tree.nodes[DifSpecAddEnv.DIFF_MULT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]

        # remove existing
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOL_GROUP_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOLOR_SCALE_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOLOR_MULT_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.OPACITY_NODE])

        # create nodes
        uv_recalc_n = node_tree.nodes.new("ShaderNodeGroup")
        uv_recalc_n.name = window_uv_offset_ng.WINDOW_UV_OFFSET_G
        uv_recalc_n.label = window_uv_offset_ng.WINDOW_UV_OFFSET_G
        uv_recalc_n.location = (start_pos_x, start_pos_y + 1500)
        uv_recalc_n.node_tree = window_uv_offset_ng.get_node_group()

        sec_uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uv_map_n.name = sec_uv_map_n.label = WindowNight.SEC_UV_MAP
        sec_uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1000)
        sec_uv_map_n.uv_map = _MESH_consts.none_uv

        lightmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        lightmap_tex_n.name = lightmap_tex_n.label = WindowNight.LIGHTMAP_TEX_NODE
        lightmap_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        lightmap_tex_n.width = 140

        base_lightmap_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        base_lightmap_mult_n.name = base_lightmap_mult_n.label = WindowNight.BASE_LIGHTMAP_MULT_NODE
        base_lightmap_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        base_lightmap_mult_n.operation = "MULTIPLY"

        base_alpha_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        base_alpha_mult_n.name = base_alpha_mult_n.label = WindowNight.BASE_ALPHA_MULT_NODE
        base_alpha_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1500)
        base_alpha_mult_n.operation = "MULTIPLY"

        # create links
        node_tree.links.new(uv_recalc_n.inputs['UV'], uv_map_n.outputs['UV'])
        node_tree.links.new(uv_recalc_n.inputs['Normal'], geom_n.outputs['Normal'])
        node_tree.links.new(uv_recalc_n.inputs['Incoming'], geom_n.outputs['Incoming'])

        node_tree.links.new(base_tex_n.inputs['Vector'], uv_recalc_n.outputs['UV Final'])
        node_tree.links.new(lightmap_tex_n.inputs['Vector'], sec_uv_map_n.outputs['UV'])

        # pass 1
        node_tree.links.new(base_lightmap_mult_n.inputs[0], base_tex_n.outputs['Color'])
        node_tree.links.new(base_lightmap_mult_n.inputs[1], lightmap_tex_n.outputs['Color'])

        # pass 2
        node_tree.links.new(base_alpha_mult_n.inputs[0], base_tex_n.outputs['Alpha'])
        node_tree.links.new(base_alpha_mult_n.inputs[1], base_lightmap_mult_n.outputs[0])

        # pass 3
        node_tree.links.new(diff_mult_n.inputs[1], base_alpha_mult_n.outputs[0])

        # pass 4
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_col_n.outputs['Color'])

    @staticmethod
    def set_lightmap_texture(node_tree, image):
        """Set lightmap texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to lightmap texture node
        :type image: bpy.types.Image
        """
        node_tree.nodes[WindowNight.LIGHTMAP_TEX_NODE].image = image

    @staticmethod
    def set_lightmap_texture_settings(node_tree, settings):
        """Set lightmap texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[WindowNight.LIGHTMAP_TEX_NODE], settings)

    @staticmethod
    def set_lightmap_uv(node_tree, uv_layer):
        """Set UV layer to lightmap texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for lightmap texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[WindowNight.SEC_UV_MAP].uv_map = uv_layer
