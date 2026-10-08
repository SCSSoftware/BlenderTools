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
from io_scs_tools.internals.shaders.base import BaseShader
from io_scs_tools.internals.shaders.flavors import nocull
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.std_node_groups import output_shader_ng
from io_scs_tools.utils import material as _material_utils


class Fakeshadow(BaseShader):
    WIREFRAME_NODE = "Wireframe"
    MIX_NODE = "Mix"
    UVMAP_NODE = "FirstUVs"
    BASE_TEX_NODE = "BaseTex"
    OUT_MAT_NODE = "OutMaterial"
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
        wireframe_n.location = (start_pos_x - pos_x_shift, start_pos_y)
        wireframe_n.use_pixel_size = True
        wireframe_n.inputs['Size'].default_value = 2.0

        uvmap_n = node_tree.nodes.new("ShaderNodeUVMap")
        uvmap_n.name = uvmap_n.label = Fakeshadow.UVMAP_NODE
        uvmap_n.location = (start_pos_x - pos_x_shift, start_pos_y - 250)
        uvmap_n.uv_map = _MESH_consts.none_uv

        mix_n = node_tree.nodes.new("ShaderNodeMix")
        mix_n.name = mix_n.label = Fakeshadow.MIX_NODE
        mix_n.location = (start_pos_x, start_pos_y)
        mix_n.data_type = "RGBA"
        mix_n.blend_type = "MIX"
        mix_n.inputs['A'].default_value = (1, 1, 1, 1)  # fakeshadow color
        mix_n.inputs['B'].default_value = (0, 0, 0, 1)  # wireframe color

        base_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        base_tex_n.name = base_tex_n.label = Fakeshadow.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x, start_pos_y - 250)
        base_tex_n.width = 140

        out_mat_node = node_tree.nodes.new("ShaderNodeGroup")
        out_mat_node.name = out_mat_node.label = Fakeshadow.OUT_MAT_NODE
        out_mat_node.location = (start_pos_x + pos_x_shift, start_pos_y - 100)
        out_mat_node.node_tree = output_shader_ng.get_node_group()

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = Fakeshadow.OUTPUT_NODE
        output_n.location = (start_pos_x + pos_x_shift * 2, start_pos_y)

        # links creation
        node_tree.links.new(mix_n.inputs['Factor'], wireframe_n.outputs['Fac'])
        node_tree.links.new(output_n.inputs['Surface'], mix_n.outputs['Result'])
        node_tree.links.new(out_mat_node.inputs['Color'], mix_n.outputs['Result'])

        node_tree.links.new(base_tex_n.inputs['Vector'], uvmap_n.outputs['UV'])
        node_tree.links.new(out_mat_node.inputs['Alpha'], base_tex_n.outputs['Alpha'])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        material.use_backface_culling = True
        material.surface_render_method = "DITHERED"

        if nocull.is_set(node_tree):
            material.use_backface_culling = False

        # set proper blend method and possible alpha test pass
        if alpha_test.is_set(node_tree):

            # init parent
            out_mat_node = node_tree.nodes[Fakeshadow.OUT_MAT_NODE]
            output_n = node_tree.nodes[Fakeshadow.OUTPUT_NODE]

            out_mat_node.inputs["Alpha Type"].default_value = 0.0

            # links creation
            node_tree.links.new(out_mat_node.outputs['Shader'], output_n.inputs['Surface'])

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            alpha_test.init(node_tree)
        else:
            alpha_test.delete(node_tree)

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
    def set_nocull_flavor(node_tree, switch_on):
        """Set nocull flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if it should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            nocull.init(node_tree)
        else:
            nocull.delete(node_tree)

    @staticmethod
    def set_base_texture(node_tree, image):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to base texture node
        :type image: bpy.types.Image
        """
        if alpha_test.is_set(node_tree):
            node_tree.nodes[Fakeshadow.BASE_TEX_NODE].image = image

    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        if alpha_test.is_set(node_tree):
            _material_utils.set_texture_settings_to_node(node_tree.nodes[Fakeshadow.BASE_TEX_NODE], settings)

    @staticmethod
    def set_base_uv(node_tree, uv_layer):
        """Set UV layer to base texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """
        if alpha_test.is_set(node_tree):
            if uv_layer is None or uv_layer == "":
                uv_layer = _MESH_consts.none_uv

            node_tree.nodes[Fakeshadow.UVMAP_NODE].uv_map = uv_layer
