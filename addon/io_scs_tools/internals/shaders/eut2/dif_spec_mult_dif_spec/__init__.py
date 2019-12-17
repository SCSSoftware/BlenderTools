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
from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.flavors import tg1
from io_scs_tools.utils import material as _material_utils


class DifSpecMultDifSpec(DifSpec):
    SEC_UVMAP_NODE = "SecondUVMap"
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

        vcol_gn = node_tree.nodes[DifSpec.VCOL_GROUP_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[DifSpec.OPACITY_NODE])

        # move existing
        for node in node_tree.nodes:
            if node.location.x > pos_x_shift:
                node.location.x += pos_x_shift

        # node creation
        sec_uvmap_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uvmap_n.name = DifSpecMultDifSpec.SEC_UVMAP_NODE
        sec_uvmap_n.label = DifSpecMultDifSpec.SEC_UVMAP_NODE
        sec_uvmap_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)
        sec_uvmap_n.uv_map = _MESH_consts.none_uv

        mult_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mult_tex_n.name = DifSpecMultDifSpec.MULT_TEX_NODE
        mult_tex_n.label = DifSpecMultDifSpec.MULT_TEX_NODE
        mult_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        mult_tex_n.width = 140

        mult_base_col_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        mult_base_col_mix_n.name = DifSpecMultDifSpec.MULT_BASE_COL_MIX_NODE
        mult_base_col_mix_n.label = DifSpecMultDifSpec.MULT_BASE_COL_MIX_NODE
        mult_base_col_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1400)
        mult_base_col_mix_n.operation = "MULTIPLY"

        mult_base_a_mix_n = node_tree.nodes.new("ShaderNodeMath")
        mult_base_a_mix_n.name = DifSpecMultDifSpec.MULT_BASE_A_MIX_NODE
        mult_base_a_mix_n.label = DifSpecMultDifSpec.MULT_BASE_A_MIX_NODE
        mult_base_a_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1700)
        mult_base_a_mix_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(mult_tex_n.inputs['Vector'], sec_uvmap_n.outputs['UV'])

        node_tree.links.new(mult_base_col_mix_n.inputs[0], base_tex_n.outputs['Color'])
        node_tree.links.new(mult_base_col_mix_n.inputs[1], mult_tex_n.outputs['Color'])
        node_tree.links.new(mult_base_a_mix_n.inputs[0], base_tex_n.outputs['Alpha'])
        node_tree.links.new(mult_base_a_mix_n.inputs[1], mult_tex_n.outputs['Alpha'])

        node_tree.links.new(vcol_mult_n.inputs[1], mult_base_col_mix_n.outputs[0])
        node_tree.links.new(spec_mult_n.inputs[1], mult_base_a_mix_n.outputs['Value'])

        node_tree.links.new(compose_lighting_n.inputs['Alpha'], vcol_gn.outputs['Vertex Color Alpha'])

    @staticmethod
    def set_mult_texture(node_tree, image):
        """Set multiplication texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to mult texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[DifSpecMultDifSpec.MULT_TEX_NODE].image = image

    @staticmethod
    def set_mult_texture_settings(node_tree, settings):
        """Set multiplication texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifSpecMultDifSpec.MULT_TEX_NODE], settings)

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

        node_tree.nodes[DifSpecMultDifSpec.SEC_UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_tg1_flavor(node_tree, switch_on):
        """Set zero texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg1.is_set(node_tree):

            out_node = node_tree.nodes[DifSpecMultDifSpec.GEOM_NODE]
            in_node = node_tree.nodes[DifSpecMultDifSpec.MULT_TEX_NODE]

            out_node.location.x -= 185
            location = (out_node.location.x + 185, out_node.location.y)

            tg1.init(node_tree, location, out_node.outputs["Position"], in_node.inputs["Vector"])

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
