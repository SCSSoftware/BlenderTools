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

from io_scs_tools.internals.shaders.base import BaseShader


class Fakeshadow(BaseShader):
    WIREFRAME_NODE = "Wireframe"
    MIX_NODE = "Mix"
    OUTPUT_NODE = "Output"

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

        # node creation
        wireframe_n = node_tree.nodes.new("ShaderNodeWireframe")
        wireframe_n.name = wireframe_n.label = Fakeshadow.WIREFRAME_NODE
        wireframe_n.location = (start_pos_x, start_pos_y)
        wireframe_n.use_pixel_size = True
        wireframe_n.inputs['Size'].default_value = 2.0

        mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mix_n.name = mix_n.label = Fakeshadow.MIX_NODE
        mix_n.location = (start_pos_x + pos_x_shift, start_pos_y)
        mix_n.inputs['Color1'].default_value = (1, 1, 1, 1)  # fakeshadow color
        mix_n.inputs['Color2'].default_value = (0, 0, 0, 1)  # wireframe color

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = Fakeshadow.OUTPUT_NODE
        output_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y)

        # links creation
        node_tree.links.new(mix_n.inputs['Fac'], wireframe_n.outputs['Fac'])

        node_tree.links.new(output_n.inputs['Surface'], mix_n.outputs['Color'])

    @staticmethod
    def set_shadow_bias(node_tree, value):
        """Set shadow bias attirbute for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: blender material for used in this tree node as output
        :type value: float
        """

        pass  # NOTE: shadow bias won't be visualized as game uses it's own implementation

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        material.use_backface_culling = True
        material.blend_method = "OPAQUE"
