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


class DifSpecWeightWeightDifSpecWeight(DifSpec):
    SEC_UVMAP_NODE = "SecondUVMap"
    OVER_TEX_NODE = "OverTex"
    BASE_OVER_MIX_NODE = "BaseOverColorMix"
    BASE_OVER_A_MIX_NODE = "BaseOverAlphaMix"
    SEC_SPEC_COL_NODE = "SecSpecularColor"
    SEC_SPEC_MIX_NODE = "SecSpecMix"
    SEC_SHININESS_MIX_NODE = "SecShininnesMix"
    VCOL_SPEC_MULT_NODE = "VColSpecMult"

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
        DifSpec.init(node_tree, disable_remap_alpha=False)

        vcol_group_n = node_tree.nodes[DifSpec.VCOL_GROUP_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[DifSpec.SPEC_COL_NODE]
        spec_multi_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpec.VCOLOR_SCALE_NODE]
        vcol_multi_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        lighting_eval_n = node_tree.nodes[DifSpec.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[DifSpec.OPACITY_NODE])

        # move existing
        spec_multi_n.location.x += pos_x_shift
        spec_multi_n.location.y += 100
        lighting_eval_n.location.x += pos_x_shift
        compose_lighting_n.location.x += pos_x_shift
        output_n.location.x += pos_x_shift

        # node creation
        sec_geom_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_geom_n.name = sec_geom_n.label = DifSpecWeightWeightDifSpecWeight.SEC_UVMAP_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)
        sec_geom_n.uv_map = _MESH_consts.none_uv

        sec_spec_col_n = node_tree.nodes.new("ShaderNodeRGB")
        sec_spec_col_n.name = sec_spec_col_n.label = DifSpecWeightWeightDifSpecWeight.SEC_SPEC_COL_NODE
        sec_spec_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2100)

        over_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        over_tex_n.name = over_tex_n.label = DifSpecWeightWeightDifSpecWeight.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        over_tex_n.width = 140

        sec_spec_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        sec_spec_mix_n.name = sec_spec_mix_n.label = DifSpecWeightWeightDifSpecWeight.SEC_SPEC_MIX_NODE
        sec_spec_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2100)
        sec_spec_mix_n.blend_type = "MIX"

        sec_shininess_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        sec_shininess_mix_n.name = sec_shininess_mix_n.label = DifSpecWeightWeightDifSpecWeight.SEC_SHININESS_MIX_NODE
        sec_shininess_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        sec_shininess_mix_n.blend_type = "MIX"

        base_over_a_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_a_mix_n.name = base_over_a_mix_n.label = DifSpecWeightWeightDifSpecWeight.BASE_OVER_A_MIX_NODE
        base_over_a_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1900)
        base_over_a_mix_n.blend_type = "MIX"

        base_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_mix_n.name = base_over_mix_n.label = DifSpecWeightWeightDifSpecWeight.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1350)

        vcol_spec_mul_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vcol_spec_mul_n.name = vcol_spec_mul_n.label = DifSpecWeightWeightDifSpecWeight.VCOL_SPEC_MULT_NODE
        vcol_spec_mul_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1900)
        vcol_spec_mul_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(over_tex_n.inputs["Vector"], sec_geom_n.outputs["UV"])

        # pass 1
        node_tree.links.new(sec_shininess_mix_n.inputs["Fac"], vcol_group_n.outputs["Vertex Color Alpha"])

        node_tree.links.new(sec_spec_mix_n.inputs["Fac"], vcol_group_n.outputs["Vertex Color Alpha"])
        node_tree.links.new(sec_spec_mix_n.inputs["Color1"], spec_col_n.outputs["Color"])
        node_tree.links.new(sec_spec_mix_n.inputs["Color2"], sec_spec_col_n.outputs["Color"])

        node_tree.links.new(base_over_a_mix_n.inputs["Fac"], vcol_group_n.outputs["Vertex Color Alpha"])
        node_tree.links.new(base_over_a_mix_n.inputs["Color1"], base_tex_n.outputs["Alpha"])
        node_tree.links.new(base_over_a_mix_n.inputs["Color2"], over_tex_n.outputs["Alpha"])

        node_tree.links.new(base_over_mix_n.inputs["Fac"], vcol_group_n.outputs["Vertex Color Alpha"])
        node_tree.links.new(base_over_mix_n.inputs["Color1"], base_tex_n.outputs["Color"])
        node_tree.links.new(base_over_mix_n.inputs["Color2"], over_tex_n.outputs["Color"])

        # pass 2
        node_tree.links.new(spec_multi_n.inputs[0], sec_spec_mix_n.outputs["Color"])
        node_tree.links.new(spec_multi_n.inputs[1], base_over_a_mix_n.outputs["Color"])

        node_tree.links.new(vcol_multi_n.inputs[1], base_over_mix_n.outputs["Color"])

        # pass 3
        node_tree.links.new(vcol_spec_mul_n.inputs[0], spec_multi_n.outputs[0])
        node_tree.links.new(vcol_spec_mul_n.inputs[1], vcol_scale_n.outputs[0])

        # pass 4
        node_tree.links.new(lighting_eval_n.inputs["Shininess"], sec_shininess_mix_n.outputs["Color"])

        # pass 5
        node_tree.links.new(compose_lighting_n.inputs["Specular Color"], vcol_spec_mul_n.outputs[0])
        node_tree.links.new(compose_lighting_n.inputs['Alpha'], base_tex_n.outputs['Alpha'])

    @staticmethod
    def set_shininess(node_tree, factor):
        """Set shininess factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: shininess factor
        :type factor: float
        """

        node_tree.nodes[DifSpecWeightWeightDifSpecWeight.SEC_SHININESS_MIX_NODE].inputs["Color1"].default_value = (factor,) * 4

    @staticmethod
    def set_over_texture(node_tree, image):
        """Set overlying texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to over texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[DifSpecWeightWeightDifSpecWeight.OVER_TEX_NODE].image = image

    @staticmethod
    def set_over_texture_settings(node_tree, settings):
        """Set overlying texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifSpecWeightWeightDifSpecWeight.OVER_TEX_NODE], settings)

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to overlying texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        node_tree.nodes[DifSpecWeightWeightDifSpecWeight.SEC_UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_aux3(node_tree, aux_property):
        """Set secondary specular color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        color = (aux_property[0]["value"], aux_property[1]["value"], aux_property[2]["value"], 1.0)
        node_tree.nodes[DifSpecWeightWeightDifSpecWeight.SEC_SPEC_COL_NODE].outputs["Color"].default_value = color

        factor = aux_property[3]["value"]
        node_tree.nodes[DifSpecWeightWeightDifSpecWeight.SEC_SHININESS_MIX_NODE].inputs["Color2"].default_value = (factor,) * 4

    @staticmethod
    def set_reflection2(node_tree, value):
        """Set second reflection factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: reflection factor
        :type value: float
        """

        pass  # NOTE: reflection attribute doesn't change anything in rendered material, so pass it@staticmethod

    @staticmethod
    def set_tg1_flavor(node_tree, switch_on):
        """Set second texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg1.is_set(node_tree):

            out_node = node_tree.nodes[DifSpec.GEOM_NODE]
            in_node = node_tree.nodes[DifSpecWeightWeightDifSpecWeight.OVER_TEX_NODE]

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
