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

from ..dif import Dif
from .....utils import material as _material_utils

class Leaves(Dif):
    MASK_TEX_NODE = "MaskTex"
    SPEC_MULT_NODE = "SpecMultiplier"
    SEP_MASK_COL_NODE = "SeparateMaskCol"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        DISCLAIMER: This shader is provisional and should be reworked as soon, as more information about leaves shader will be available.
        Please, do not treat that preview as real equivalent of game shader. Please, chceck everything in game after export.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # init parent
        Dif.init(node_tree)

        uvmap_n = node_tree.nodes[Dif.UVMAP_NODE]
        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]
        spec_col_n = node_tree.nodes[Dif.SPEC_COL_NODE]
        diff_mult_n = node_tree.nodes[Dif.DIFF_MULT_NODE]

        opacity_mult_n = node_tree.nodes[Dif.OPACITY_NODE]
        vcol_scale_n = node_tree.nodes[Dif.VCOLOR_SCALE_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]

        # delete existing
        node_tree.nodes.remove(opacity_mult_n)
        node_tree.nodes.remove(vcol_scale_n)
        node_tree.nodes.remove(vcol_mult_n)

        # node creation
        # - column 1 -
        mask_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mask_tex_n.name = mask_tex_n.label = Leaves.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        mask_tex_n.width = 140

        # - column 2 -
        sep_mask_col_n = node_tree.nodes.new("ShaderNodeSeparateColor")
        sep_mask_col_n.name = sep_mask_col_n.label = Leaves.SEP_MASK_COL_NODE
        sep_mask_col_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y + 1200)

        # - column 3 -
        spec_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_mult_n.name = spec_mult_n.label = Leaves.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        spec_mult_n.operation = "MULTIPLY"

        # links creation
        # - column -1 -
        node_tree.links.new(uvmap_n.outputs['UV'], mask_tex_n.inputs['Vector'])

        # - column 1 -
        node_tree.links.new(spec_col_n.outputs['Color'], spec_mult_n.inputs[0])

        node_tree.links.new(base_tex_n.outputs['Color'], diff_mult_n.inputs[1])
        node_tree.links.new(base_tex_n.outputs['Alpha'], compose_lighting_n.inputs['Alpha'])

        node_tree.links.new(mask_tex_n.outputs['Color'], sep_mask_col_n.inputs['Color'])

        # - column 2 -
        # Idk if this is correct. This is made to prevent specular shading on model. It can also be done by "Flat Light" in light evaluator,
        # but I think, that B channel is used for specular mask because that channel is very similar to specular effect on leaves in game.
        # It also can be G or anything else. I don't have time to test that shader in game.
        node_tree.links.new(sep_mask_col_n.outputs['Blue'], spec_mult_n.inputs[1])

        # - column 3 -
        node_tree.links.new(spec_mult_n.outputs['Vector'], compose_lighting_n.inputs['Specular Color'])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        compose_lighting_n = node_tree.nodes[Leaves.COMPOSE_LIGHTING_NODE]

        material.use_backface_culling = False
        material.surface_render_method = "DITHERED"
        compose_lighting_n.inputs["Alpha Type"].default_value = 0.0

        if compose_lighting_n.inputs["Alpha Type"].default_value < 0.0 and node_tree.nodes[Leaves.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links:
            node_tree.links.remove(node_tree.nodes[Leaves.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links[0])

    @staticmethod
    def set_mask_texture(node_tree, image):
        """Set mask texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to mask texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[Leaves.MASK_TEX_NODE].image = image

    @staticmethod
    def set_mask_texture_settings(node_tree, settings):
        """Set mask texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Leaves.MASK_TEX_NODE], settings)

    @staticmethod
    def set_mask_uv(node_tree, uv_layer):
        """Set UV layer to mask texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mask texture
        :type uv_layer: str
        """

        Dif.set_base_uv(node_tree, uv_layer)

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set LOD selector for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: LOD selector represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        # NOTE: As long as we not use it for now, we can pass it.
        pass