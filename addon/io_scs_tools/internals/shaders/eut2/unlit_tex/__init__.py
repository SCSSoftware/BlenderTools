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

# Copyright (C) 2015-2022: SCS Software

from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.base import BaseShader
from io_scs_tools.internals.shaders.eut2 import parameters
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import blend_mult
from io_scs_tools.internals.shaders.flavors import paint
from io_scs_tools.internals.shaders.std_node_groups import output_shader_ng
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import material as _material_utils


class UnlitTex(BaseShader):
    DIFF_COL_NODE = "DiffuseColor"
    UV_MAP_NODE = "UVMap"
    BASE_TEX_NODE = "BaseTex"
    TEX_MULT_NODE = "TextureMultiplier"
    LUM_MULT_NODE = "LuminanceMultiplier"
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
        uv_map_n.name = uv_map_n.label = UnlitTex.UV_MAP_NODE
        uv_map_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        uv_map_n.uv_map = _MESH_consts.none_uv

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = diff_col_n.label = UnlitTex.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        base_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        base_tex_n.name = base_tex_n.label = UnlitTex.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)
        base_tex_n.width = 140

        tex_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        tex_mult_n.name = tex_mult_n.label = UnlitTex.TEX_MULT_NODE
        tex_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1500)
        tex_mult_n.operation = "MULTIPLY"

        lum_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_mult_n.name = lum_mult_n.label = UnlitTex.LUM_MULT_NODE
        lum_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1500)
        lum_mult_n.operation = "MULTIPLY"
        lum_mult_n.inputs[0].default_value = (1.0,) * 3

        out_shader_node = node_tree.nodes.new("ShaderNodeGroup")
        out_shader_node.name = out_shader_node.label = UnlitTex.OUT_SHADER_NODE
        out_shader_node.location = (start_pos_x + pos_x_shift * 5, 1500)
        out_shader_node.node_tree = output_shader_ng.get_node_group()

        output_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_n.name = output_n.label = UnlitTex.OUTPUT_NODE
        output_n.location = (start_pos_x + + pos_x_shift * 6, start_pos_y + 1500)

        # links creation
        node_tree.links.new(base_tex_n.inputs['Vector'], uv_map_n.outputs['UV'])

        node_tree.links.new(tex_mult_n.inputs[0], diff_col_n.outputs['Color'])
        node_tree.links.new(tex_mult_n.inputs[1], base_tex_n.outputs['Color'])

        node_tree.links.new(lum_mult_n.inputs[1], tex_mult_n.outputs[0])

        node_tree.links.new(out_shader_node.inputs['Color'], lum_mult_n.outputs[0])
        node_tree.links.new(out_shader_node.inputs['Alpha'], base_tex_n.outputs['Alpha'])

        node_tree.links.new(output_n.inputs['Surface'], out_shader_node.outputs['Shader'])

    @staticmethod
    def finalize(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        material.use_backface_culling = True
        material.blend_method = "OPAQUE"

        # set proper blend method
        if alpha_test.is_set(node_tree):
            material.blend_method = "CLIP"
            material.alpha_threshold = 0.05

            # add alpha test pass if multiply blend enabled, where alphed pixels shouldn't be multiplied as they are discarded
            if blend_mult.is_set(node_tree):
                out_shader_n = node_tree.nodes[UnlitTex.OUT_SHADER_NODE]

                # alpha test pass has to get fully opaque input, thus remove transparency linkage
                if out_shader_n.inputs['Alpha'].links:
                    node_tree.links.remove(out_shader_n.inputs['Alpha'].links[0])

                shader_from = out_shader_n.outputs['Shader']
                alpha_from = node_tree.nodes[UnlitTex.BASE_TEX_NODE].outputs['Alpha']
                shader_to = out_shader_n.outputs['Shader'].links[0].to_socket

                alpha_test.add_pass(node_tree, shader_from, alpha_from, shader_to)

        if blend_add.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_mult.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_over.is_set(node_tree):
            material.blend_method = "BLEND"

        if material.blend_method == "OPAQUE" and node_tree.nodes[UnlitTex.OUT_SHADER_NODE].inputs['Alpha'].links:
            node_tree.links.remove(node_tree.nodes[UnlitTex.OUT_SHADER_NODE].inputs['Alpha'].links[0])

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
    def set_queue_bias(node_tree, value):
        """Set queue bias attirbute for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: queue bias index
        :type value: int
        """

        pass  # NOTE: shadow bias won't be visualized as game uses it's own implementation

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminosity boost factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: luminosity output represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        luminance_boost = aux_property[0]['value']
        node_tree.nodes[UnlitTex.LUM_MULT_NODE].inputs[0].default_value = (parameters.get_material_luminosity(luminance_boost),) * 3

    @staticmethod
    def set_base_texture(node_tree, image):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to base texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[UnlitTex.BASE_TEX_NODE].image = image

    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[UnlitTex.BASE_TEX_NODE], settings)

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

        node_tree.nodes[UnlitTex.UV_MAP_NODE].uv_map = uv_layer

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
    def set_blend_over_flavor(node_tree, switch_on):
        """Set blend over flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend over should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            blend_over.init(node_tree)
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

        if switch_on:
            in_node = node_tree.nodes[UnlitTex.OUT_SHADER_NODE]
            out_node = node_tree.nodes[UnlitTex.OUTPUT_NODE]

            # put it on location of output node & move output node for one slot to the right
            location = tuple(out_node.location)
            out_node.location.x += 185

            blend_add.init(node_tree, location, in_node.outputs['Shader'], out_node.inputs['Surface'])
        else:
            blend_add.delete(node_tree)

    @staticmethod
    def set_blend_mult_flavor(node_tree, switch_on):
        """Set blend mult flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blending should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            out_node = node_tree.nodes[UnlitTex.OUTPUT_NODE]
            in_node = node_tree.nodes[UnlitTex.OUT_SHADER_NODE]

            # break link to out shader node as mult uses DST_COLOR as source factor in blend function
            if in_node.inputs['Alpha'].links:
                node_tree.links.remove(in_node.inputs['Alpha'].links[0])

            # put it on location of output node & move output node for one slot to the right
            location = tuple(out_node.location)
            out_node.location.x += 185

            blend_mult.init(node_tree, location, in_node.outputs['Shader'], out_node.inputs['Surface'])
        else:
            blend_mult.delete(node_tree)

    @staticmethod
    def set_paint_flavor(node_tree, switch_on):
        """Set paint flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        diff_col_n = node_tree.nodes[UnlitTex.DIFF_COL_NODE]
        diff_mult_n = node_tree.nodes[UnlitTex.TEX_MULT_NODE]

        if switch_on:

            for node in node_tree.nodes:
                if node.location.x > diff_col_n.location.x:
                    node.location.x += 185

            location = (diff_mult_n.location.x - 185, diff_mult_n.location.y + 50)
            paint.init(node_tree, location, diff_col_n.outputs["Color"], diff_mult_n.inputs[0])

        else:
            paint.delete(node_tree)
