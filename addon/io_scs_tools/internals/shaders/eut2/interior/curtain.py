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

# Copyright (C) 2024-2026: Michaleczeq

from . import InteriorLit
from .....consts import Mesh as _MESH_consts
from .....utils import material as _material_utils

class InteriorCurtain(InteriorLit):
    SEC_UVMAP_NODE = "SecondUVMap"
    OVER_TEX_NODE = "OverTex"
    BASE_OVER_MIX_NODE = "BaseOverColorMix"
    

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

        pos_x_shift = 185

        # init parent
        InteriorLit.init(node_tree)

        base_tex_n = node_tree.nodes[InteriorLit.BASE_TEX_NODE]
        vgcol_mult_n = node_tree.nodes[InteriorLit.VGCOLOR_MULT_NODE]

        # node creation
        # - column -1 -
        sec_uv_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uv_n.name = sec_uv_n.label = InteriorCurtain.SEC_UVMAP_NODE
        sec_uv_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)
        sec_uv_n.uv_map = _MESH_consts.none_uv

        # - column 1 -
        over_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        over_tex_n.name = over_tex_n.label = InteriorCurtain.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        over_tex_n.width = 140

        # - column 2 -
        base_over_mix_n = node_tree.nodes.new("ShaderNodeMix")
        base_over_mix_n.name = base_over_mix_n.label = InteriorCurtain.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1200)
        base_over_mix_n.data_type = "RGBA"
        base_over_mix_n.blend_type = "MIX"
        

        # links creation
        # - column -1 -
        node_tree.links.new(sec_uv_n.outputs['UV'], over_tex_n.inputs['Vector'])

        # - column 1 -
        node_tree.links.new(base_tex_n.outputs['Color'], base_over_mix_n.inputs['A'])
        node_tree.links.new(over_tex_n.outputs['Color'], base_over_mix_n.inputs['B'])
        node_tree.links.new(over_tex_n.outputs['Alpha'], base_over_mix_n.inputs['Factor'])

        # - column 2 -
        node_tree.links.new(base_over_mix_n.outputs['Result'], vgcol_mult_n.inputs[0])

    @staticmethod
    def set_over_texture(node_tree, image):
        """Set overlying texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to over texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[InteriorCurtain.OVER_TEX_NODE].image = image

    @staticmethod
    def set_over_texture_settings(node_tree, settings):
        """Set overlying texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[InteriorCurtain.OVER_TEX_NODE], settings)

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to overlying texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[InteriorCurtain.SEC_UVMAP_NODE].uv_map = uv_layer
