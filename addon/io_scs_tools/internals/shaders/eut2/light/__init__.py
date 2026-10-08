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


class Light(Dif):
    SPEC_MULT_NODE = "SpecMultiplier"
    RGB_TO_BW_ALPHA_NODE = "RGBToBWColor"

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
        Dif.init(node_tree)

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.LIGHTING_EVAL_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.BASE_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.UVMAP_NODE])

        vcol_group_n = node_tree.nodes[Dif.VCOL_GROUP_NODE]
        v_col_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        v_col_mult_n.inputs[1].default_value = (1.0,) *3
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]
        compose_lighting_n.inputs['Diffuse Lighting'].default_value = (1.0,) * 4
        compose_lighting_n.inputs['Specular Lighting'].default_value = (1.0,) * 4

        # node creation
        spec_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_mult_n.name = Light.SPEC_MULT_NODE
        spec_mult_n.label = Light.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1850)
        spec_mult_n.operation = "MULTIPLY"

        rgb_to_bw_n = node_tree.nodes.new("ShaderNodeRGBToBW")
        rgb_to_bw_n.name = Light.RGB_TO_BW_ALPHA_NODE
        rgb_to_bw_n.label = Light.RGB_TO_BW_ALPHA_NODE
        rgb_to_bw_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)

        # links creation
        node_tree.links.new(spec_mult_n.inputs[0], v_col_mult_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs["Specular Color"], spec_mult_n.outputs[0])

        node_tree.links.new(rgb_to_bw_n.inputs["Color"], vcol_group_n.outputs["Vertex Color"])
        node_tree.links.new(compose_lighting_n.inputs["Alpha"], rgb_to_bw_n.outputs["Val"])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        # in game it gets added to framebuffer, however we don't have access to frame buffer thus make approximation with alpha blending
        material.surface_render_method = "BLENDED"
        node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE].inputs["Alpha Type"].default_value = 1.0

    @staticmethod
    def set_env_factor(node_tree, color):
        """Set environment factor color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: environment color
        :type color: Color or tuple
        """
        
        pass # NOTE: as this variant doesn't use env_factor we just ignore it

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminance boost factor for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: luminosity factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """
        pass  # NOTE: as this variant doesn't use luminance effect we just ignore this factor
