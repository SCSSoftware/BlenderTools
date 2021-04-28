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
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.utils import material as _material_utils


class Shadowmap(BaseShader):
    UV_MAP_NODE = "UVMap"
    BASE_TEX_NODE = "BaseTex"
    ALPHA_INV_NODE = "AlphaInv"
    OUT_SHADER_NODE = "OutShader"
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
        uv_map_n = node_tree.nodes.new("ShaderNodeUVMap")
        uv_map_n.name = uv_map_n.label = Shadowmap.UV_MAP_NODE
        uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        uv_map_n.uv_map = _MESH_consts.none_uv

        base_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        base_tex_n.name = base_tex_n.label = Shadowmap.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)
        base_tex_n.width = 140

        alpha_inv_n = node_tree.nodes.new("ShaderNodeMath")
        alpha_inv_n.name = alpha_inv_n.label = Shadowmap.ALPHA_INV_NODE
        alpha_inv_n.location = (start_pos_x + pos_x_shift * 2, 1300)
        alpha_inv_n.operation = "SUBTRACT"
        alpha_inv_n.inputs[0].default_value = 0.999999  # TODO: change back to 1.0 after bug is fixed: https://developer.blender.org/T71426
        alpha_inv_n.inputs[1].default_value = 1.0
        alpha_inv_n.use_clamp = True

        out_shader_node = node_tree.nodes.new("ShaderNodeEeveeSpecular")
        out_shader_node.name = out_shader_node.label = Shadowmap.OUT_SHADER_NODE
        out_shader_node.location = (start_pos_x + pos_x_shift * 3, 1500)
        out_shader_node.inputs["Emissive Color"].default_value = (0.0,) * 4
        out_shader_node.inputs["Base Color"].default_value = (0.0,) * 4
        out_shader_node.inputs["Specular"].default_value = (0.0,) * 4

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = Shadowmap.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 4, start_pos_y + 1500)

        # links creation
        node_tree.links.new(base_tex_n.inputs['Vector'], uv_map_n.outputs['UV'])

        node_tree.links.new(alpha_inv_n.inputs[1], base_tex_n.outputs['Color'])

        node_tree.links.new(out_shader_node.inputs['Transparency'], alpha_inv_n.outputs['Value'])

        node_tree.links.new(output_n.inputs['Surface'], out_shader_node.outputs['BSDF'])

    @staticmethod
    def finalize(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        material.use_backface_culling = True
        material.blend_method = "BLEND"

    @staticmethod
    def set_base_texture(node_tree, image):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to base texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Shadowmap.BASE_TEX_NODE].image = image

    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Shadowmap.BASE_TEX_NODE], settings)

    @staticmethod
    def set_base_uv(node_tree, uv_layer):
        """Set UV layer to base texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Shadowmap.UV_MAP_NODE].uv_map = uv_layer