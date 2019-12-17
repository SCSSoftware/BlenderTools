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
from io_scs_tools.utils import convert as _convert_utils


class NNone(BaseShader):
    WIREFRAME_NODE = "Wire"
    INVERT_NODE = "Invert"
    SHADER_NODE = "Shader"
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

        pos_x_shift = 185

        # node creation
        wireframe_n = node_tree.nodes.new("ShaderNodeWireframe")
        wireframe_n.name = wireframe_n.label = NNone.WIREFRAME_NODE
        wireframe_n.use_pixel_size = True
        wireframe_n.inputs['Size'].default_value = 2

        invert_n = node_tree.nodes.new("ShaderNodeInvert")
        invert_n.name = invert_n.label = NNone.INVERT_NODE
        invert_n.location = (wireframe_n.location.x + pos_x_shift, wireframe_n.location.y)
        invert_n.inputs['Fac'].default_value = 1

        shader_n = node_tree.nodes.new("ShaderNodeEeveeSpecular")
        shader_n.name = shader_n.label = NNone.SHADER_NODE
        shader_n.location = (invert_n.location.x + pos_x_shift, invert_n.location.y)
        shader_n.inputs['Base Color'].default_value = (0,) * 4
        shader_n.inputs['Specular'].default_value = (0,) * 4
        shader_n.inputs['Emissive Color'].default_value = _convert_utils.to_node_color((0.3,) * 3 + (1.0,))

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = NNone.OUTPUT_NODE
        output_n.location = (shader_n.location.x + pos_x_shift, shader_n.location.y)

        # links creation
        node_tree.links.new(invert_n.inputs['Color'], wireframe_n.outputs['Fac'])
        node_tree.links.new(shader_n.inputs['Transparency'], invert_n.outputs['Color'])
        node_tree.links.new(output_n.inputs['Surface'], shader_n.outputs['BSDF'])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        # make sure that alpha clip is enabled on that material
        material.blend_method = "CLIP"
