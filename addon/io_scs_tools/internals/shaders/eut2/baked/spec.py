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

from . import Baked
from ..std_node_groups import spec_texture_calc_ng
from .....utils import material as _material_utils

class BakedSpec(Baked):
    OVER_TEX_NODE = "OverTex"
    SPEC_TEX_CALC = "SpecTexCalc"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        Baked.init(node_tree)

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
        Baked.init(node_tree)

        uvmap_n = node_tree.nodes[Baked.UVMAP_NODE]
        lighting_eval_n = node_tree.nodes[Baked.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[Baked.COMPOSE_LIGHTING_NODE]

        # node creation
        over_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        over_tex_n.name = BakedSpec.OVER_TEX_NODE
        over_tex_n.label = BakedSpec.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1900)
        over_tex_n.width = 140

        over_tex_calc_ng = node_tree.nodes.new("ShaderNodeGroup")
        over_tex_calc_ng.name = BakedSpec.SPEC_TEX_CALC
        over_tex_calc_ng.label = BakedSpec.SPEC_TEX_CALC
        over_tex_calc_ng.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1900)
        over_tex_calc_ng.node_tree = spec_texture_calc_ng.get_node_group()


        # links creation
        node_tree.links.new(uvmap_n.outputs['UV'], over_tex_n.inputs['Vector'])

        node_tree.links.new(over_tex_n.outputs['Color'], over_tex_calc_ng.inputs['Color'])

        node_tree.links.new(over_tex_calc_ng.outputs['Shininess'], lighting_eval_n.inputs['Shininess'])
        node_tree.links.new(over_tex_calc_ng.outputs['Specular'], compose_lighting_n.inputs['Specular Color'])


    @staticmethod
    def set_over_texture(node_tree, image):
        """Set over texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to over texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[BakedSpec.OVER_TEX_NODE].image = image

    @staticmethod
    def set_over_texture_settings(node_tree, settings):
        """Set over texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[BakedSpec.OVER_TEX_NODE], settings)

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to over texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for nmap texture
        :type uv_layer: str
        """

        Baked.set_base_uv(node_tree, uv_layer)