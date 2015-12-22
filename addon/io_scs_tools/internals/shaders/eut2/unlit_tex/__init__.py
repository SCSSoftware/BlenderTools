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


from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.utils import convert as _convert_utils


class UnlitTex:
    DIFF_COL_NODE = "DiffuseColor"
    GEOM_NODE = "Geometry"
    BASE_TEX_NODE = "BaseTex"
    TEX_MULT_NODE = "TextureMultiplier"
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
        geometry_n = node_tree.nodes.new("ShaderNodeGeometry")
        geometry_n.name = UnlitTex.GEOM_NODE
        geometry_n.label = UnlitTex.GEOM_NODE
        geometry_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        geometry_n.uv_layer = _MESH_consts.none_uv

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = UnlitTex.DIFF_COL_NODE
        diff_col_n.label = UnlitTex.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        base_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        base_tex_n.name = UnlitTex.BASE_TEX_NODE
        base_tex_n.label = UnlitTex.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)

        tex_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        tex_mult_n.name = UnlitTex.TEX_MULT_NODE
        tex_mult_n.label = UnlitTex.TEX_MULT_NODE
        tex_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1500)
        tex_mult_n.blend_type = "MULTIPLY"
        tex_mult_n.inputs['Fac'].default_value = 1

        output_n = node_tree.nodes.new("ShaderNodeOutput")
        output_n.name = UnlitTex.OUTPUT_NODE
        output_n.label = UnlitTex.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 5, start_pos_y + 1500)

        # links creation
        node_tree.links.new(base_tex_n.inputs['Vector'], geometry_n.outputs['UV'])

        node_tree.links.new(tex_mult_n.inputs['Color1'], diff_col_n.outputs['Color'])
        node_tree.links.new(tex_mult_n.inputs['Color2'], base_tex_n.outputs['Color'])

        node_tree.links.new(output_n.inputs['Color'], tex_mult_n.outputs['Color'])

    @staticmethod
    def set_material(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        pass  # NOTE: there is no material node for this shader, because no lightning is applied

    @staticmethod
    def set_diffuse(node_tree, color):
        """Set diffuse color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: diffuse color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[UnlitTex.DIFF_COL_NODE].outputs['Color'].default_value = color

    @staticmethod
    def set_base_texture(node_tree, texture):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to base texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[UnlitTex.BASE_TEX_NODE].texture = texture

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

        node_tree.nodes[UnlitTex.GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not blend_over.is_set(node_tree):
            out_node = node_tree.nodes[UnlitTex.OUTPUT_NODE]
            in_node = node_tree.nodes[UnlitTex.BASE_TEX_NODE]
            location = (out_node.location.x - 185 * 2, out_node.location.y - 500)

            alpha_test.init(node_tree, location, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            alpha_test.delete(node_tree)

    @staticmethod
    def set_blend_over_flavor(node_tree, switch_on):
        """Set blend over flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend over should be switched on or off
        :type switch_on: bool
        """

        # remove alpha test flavor if it was set already. Because these two can not coexist
        if alpha_test.is_set(node_tree):
            UnlitTex.set_alpha_test_flavor(node_tree, False)

        if switch_on:
            out_node = node_tree.nodes[UnlitTex.OUTPUT_NODE]
            in_node = node_tree.nodes[UnlitTex.BASE_TEX_NODE]

            blend_over.init(node_tree, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            blend_over.delete(node_tree)

    @staticmethod
    def set_blend_add_flavor(node_tree, switch_on):
        """Set blend add flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend add should be switched on or off
        :type switch_on: bool
        """

        # remove alpha test flavor if it was set already. Because these two can not coexist
        if alpha_test.is_set(node_tree):
            UnlitTex.set_alpha_test_flavor(node_tree, False)

        if switch_on:
            out_node = node_tree.nodes[UnlitTex.OUTPUT_NODE]
            in_node = node_tree.nodes[UnlitTex.BASE_TEX_NODE]

            blend_add.init(node_tree, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            blend_add.delete(node_tree)
