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

from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import blend_mult
from io_scs_tools.internals.shaders.flavors import tg1
from io_scs_tools.utils import material as _material_utils


class DifWeightDif(Dif):
    SEC_UVMAP_NODE = "SecUVMap"
    OVER_TEX_NODE = "OverTex"
    SPEC_MULT_NODE = "SpecMultiplier"
    BASE_OVER_MIX_NODE = "BaseOverMix"

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

        vcol_group_n = node_tree.nodes[Dif.VCOL_GROUP_NODE]
        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[Dif.SPEC_COL_NODE]
        vcol_scale_n = node_tree.nodes[Dif.VCOLOR_SCALE_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])

        # node creation
        sec_uv_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uv_n.name = sec_uv_n.label = DifWeightDif.SEC_UVMAP_NODE
        sec_uv_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)
        sec_uv_n.uv_map = _MESH_consts.none_uv

        over_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        over_tex_n.name = over_tex_n.label = DifWeightDif.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        over_tex_n.width = 140

        spec_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_mult_n.name = spec_mult_n.label = DifWeightDif.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1900)
        spec_mult_n.operation = "MULTIPLY"

        base_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_mix_n.name = base_over_mix_n.label = DifWeightDif.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        base_over_mix_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(over_tex_n.inputs['Vector'], sec_uv_n.outputs['UV'])

        # pass 1
        node_tree.links.new(base_over_mix_n.inputs['Fac'], vcol_group_n.outputs['Vertex Color Alpha'])
        node_tree.links.new(base_over_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(base_over_mix_n.inputs['Color2'], over_tex_n.outputs['Color'])

        # pass 2
        node_tree.links.new(spec_mult_n.inputs[0], spec_col_n.outputs[0])
        node_tree.links.new(spec_mult_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(vcol_mult_n.inputs[1], base_over_mix_n.outputs['Color'])

        # pass to material
        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], spec_mult_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs['Alpha'], base_tex_n.outputs['Alpha'])

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

        # set proper blend method
        if alpha_test.is_set(node_tree):
            material.blend_method = "CLIP"
            material.alpha_threshold = 0.05

            # add alpha test pass if multiply blend enabled, where alphed pixels shouldn't be multiplied as they are discarded
            if blend_mult.is_set(node_tree):
                compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]

                # alpha test pass has to get fully opaque input, thus remove transparency linkage
                if compose_lighting_n.inputs['Alpha'].links:
                    node_tree.links.remove(compose_lighting_n.inputs['Alpha'].links[0])

                shader_from = compose_lighting_n.outputs['Shader']
                alpha_from = node_tree.nodes[Dif.BASE_TEX_NODE].outputs[0]
                shader_to = compose_lighting_n.outputs['Shader'].links[0].to_socket

                alpha_test.add_pass(node_tree, shader_from, alpha_from, shader_to)

        if blend_add.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_mult.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_over.is_set(node_tree):
            material.blend_method = "BLEND"

        if material.blend_method == "OPAQUE" and node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links:
            node_tree.links.remove(node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links[0])

    @staticmethod
    def set_reflection2(node_tree, value):
        """Set reflection2 factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: reflection factor
        :type value: float
        """

        pass  # NOTE: reflection attribute doesn't change anything in rendered material, so pass it

    @staticmethod
    def set_over_texture(node_tree, image):
        """Set over texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to over texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[DifWeightDif.OVER_TEX_NODE].image = image

    @staticmethod
    def set_over_texture_settings(node_tree, settings):
        """Set over texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifWeightDif.OVER_TEX_NODE], settings)

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to over texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[DifWeightDif.SEC_UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_tg1_flavor(node_tree, switch_on):
        """Set second texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg1.is_set(node_tree):

            out_node = node_tree.nodes[Dif.GEOM_NODE]
            in_node = node_tree.nodes[DifWeightDif.OVER_TEX_NODE]

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
