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


from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import tg1


class DifSpecMultDifSpec(DifSpec):
    SEC_GEOM_NODE = "SecondGeometry"
    MULT_TEX_NODE = "MultTex"
    MULT_BASE_COL_MIX_NODE = "MultBaseColorMix"
    MULT_BASE_A_MIX_NODE = "MultBaseAlphaMix"

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
        DifSpec.init(node_tree, disable_remap_alpha=True)

        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[DifSpec.OPACITY_NODE])

        # move existing
        for node in node_tree.nodes:
            if node.location.x > pos_x_shift:
                node.location.x += pos_x_shift

        # node creation
        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = DifSpecMultDifSpec.SEC_GEOM_NODE
        sec_geom_n.label = DifSpecMultDifSpec.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)
        sec_geom_n.uv_layer = _MESH_consts.none_uv

        mult_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        mult_tex_n.name = DifSpecMultDifSpec.MULT_TEX_NODE
        mult_tex_n.label = DifSpecMultDifSpec.MULT_TEX_NODE
        mult_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        mult_base_col_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        mult_base_col_mix_n.name = DifSpecMultDifSpec.MULT_BASE_COL_MIX_NODE
        mult_base_col_mix_n.label = DifSpecMultDifSpec.MULT_BASE_COL_MIX_NODE
        mult_base_col_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1400)
        mult_base_col_mix_n.blend_type = "MULTIPLY"
        mult_base_col_mix_n.inputs['Fac'].default_value = 1

        mult_base_a_mix_n = node_tree.nodes.new("ShaderNodeMath")
        mult_base_a_mix_n.name = DifSpecMultDifSpec.MULT_BASE_A_MIX_NODE
        mult_base_a_mix_n.label = DifSpecMultDifSpec.MULT_BASE_A_MIX_NODE
        mult_base_a_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1700)
        mult_base_a_mix_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(mult_tex_n.inputs['Vector'], sec_geom_n.outputs['UV'])

        node_tree.links.new(mult_base_col_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(mult_base_col_mix_n.inputs['Color2'], mult_tex_n.outputs['Color'])
        node_tree.links.new(mult_base_a_mix_n.inputs[0], base_tex_n.outputs['Value'])
        node_tree.links.new(mult_base_a_mix_n.inputs[1], mult_tex_n.outputs['Value'])

        node_tree.links.new(vcol_mult_n.inputs['Color2'], mult_base_col_mix_n.outputs['Color'])
        node_tree.links.new(spec_mult_n.inputs['Color2'], mult_base_a_mix_n.outputs['Value'])

    @staticmethod
    def set_mult_texture(node_tree, texture):
        """Set multiplication texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to mult texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecMultDifSpec.MULT_TEX_NODE].texture = texture

    @staticmethod
    def set_mult_uv(node_tree, uv_layer):
        """Set UV layer to multiplication texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mult texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[DifSpecMultDifSpec.SEC_GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not blend_over.is_set(node_tree):
            out_node = node_tree.nodes[DifSpecMultDifSpec.OUT_MAT_NODE]
            in_node = node_tree.nodes[DifSpecMultDifSpec.VCOL_GROUP_NODE]
            location = (out_node.location.x - 185 * 2, out_node.location.y - 500)

            alpha_test.init(node_tree, location, in_node.outputs['Vertex Color Alpha'], out_node.inputs['Alpha'])
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
            DifSpecMultDifSpec.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[DifSpecMultDifSpec.OUT_MAT_NODE]
        in_node = node_tree.nodes[DifSpecMultDifSpec.VCOL_GROUP_NODE]

        if switch_on:
            blend_over.init(node_tree, in_node.outputs['Vertex Color Alpha'], out_node.inputs['Alpha'])
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
            DifSpecMultDifSpec.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[DifSpecMultDifSpec.OUT_MAT_NODE]
        in_node = node_tree.nodes[DifSpecMultDifSpec.VCOL_GROUP_NODE]

        if switch_on:
            blend_add.init(node_tree, in_node.outputs['Vertex Color Alpha'], out_node.inputs['Alpha'])
        else:
            blend_add.delete(node_tree)

    @staticmethod
    def set_tg1_flavor(node_tree, switch_on):
        """Set zero texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg1.is_set(node_tree):

            out_node = node_tree.nodes[DifSpecMultDifSpec.SEC_GEOM_NODE]
            in_node = node_tree.nodes[DifSpecMultDifSpec.MULT_TEX_NODE]

            out_node.location.x -= 185
            location = (out_node.location.x + 185, out_node.location.y)

            tg1.init(node_tree, location, out_node.outputs["Global"], in_node.inputs["Vector"])

        elif not switch_on:

            tg1.delete(node_tree)

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set second texture generation scale.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        if tg1.is_set(node_tree):

            tg1.set_scale(node_tree, aux_property[0]['value'], aux_property[1]['value'])
