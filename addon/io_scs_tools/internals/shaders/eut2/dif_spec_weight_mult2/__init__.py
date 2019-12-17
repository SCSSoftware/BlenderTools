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

from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.std_node_groups import mult2_mix_ng
from io_scs_tools.internals.shaders.flavors import tg0
from io_scs_tools.utils import material as _material_utils


class DifSpecWeightMult2(DifSpec):
    UV_SCALE_NODE = "UVScale"
    MULT_TEX_NODE = "MultTex"
    MULT2_MIX_GROUP_NODE = "Mult2MixGroup"
    SPEC_VCOL_MULT_NODE = "SpecVColMultiplier"

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

        first_uv_map = node_tree.nodes[DifSpec.UVMAP_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpec.VCOLOR_SCALE_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        opacity_mult_n = node_tree.nodes[DifSpec.OPACITY_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]

        # move existing
        first_uv_map.location.x -= pos_x_shift * 2
        opacity_mult_n.location.y -= 100
        for node in node_tree.nodes:
            if node.location.x > start_pos_x + pos_x_shift:
                node.location.x += pos_x_shift

        # nodes creation
        uv_scale_n = node_tree.nodes.new("ShaderNodeMapping")
        uv_scale_n.name = uv_scale_n.label = DifSpecWeightMult2.UV_SCALE_NODE
        uv_scale_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)
        uv_scale_n.vector_type = "POINT"
        uv_scale_n.inputs['Location'].default_value = uv_scale_n.inputs['Rotation'].default_value = (0.0,) * 3
        uv_scale_n.inputs['Scale'].default_value = (1.0,) * 3
        uv_scale_n.width = 140

        mult_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mult_tex_n.name = mult_tex_n.label = DifSpecWeightMult2.MULT_TEX_NODE
        mult_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        mult_tex_n.width = 140

        mult2_mix_n = node_tree.nodes.new("ShaderNodeGroup")
        mult2_mix_n.name = mult2_mix_n.label = DifSpecWeightMult2.MULT2_MIX_GROUP_NODE
        mult2_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1400)
        mult2_mix_n.node_tree = mult2_mix_ng.get_node_group()

        spec_vcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        spec_vcol_mult_n.name = spec_vcol_mult_n.label = DifSpecWeightMult2.SPEC_VCOL_MULT_NODE
        spec_vcol_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1800)
        spec_vcol_mult_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(uv_scale_n.inputs["Vector"], first_uv_map.outputs["UV"])

        node_tree.links.new(mult_tex_n.inputs["Vector"], uv_scale_n.outputs["Vector"])

        # pass 1
        node_tree.links.new(mult2_mix_n.inputs["Base Alpha"], base_tex_n.outputs["Alpha"])
        node_tree.links.new(mult2_mix_n.inputs["Base Color"], base_tex_n.outputs["Color"])
        node_tree.links.new(mult2_mix_n.inputs["Mult Alpha"], mult_tex_n.outputs["Alpha"])
        node_tree.links.new(mult2_mix_n.inputs["Mult Color"], mult_tex_n.outputs["Color"])

        # pass 2
        node_tree.links.new(spec_mult_n.inputs[1], mult2_mix_n.outputs["Mix Alpha"])

        node_tree.links.new(opacity_mult_n.inputs[0], mult2_mix_n.outputs["Mix Alpha"])

        # pass 3
        node_tree.links.new(spec_vcol_mult_n.inputs[0], spec_mult_n.outputs[0])
        node_tree.links.new(spec_vcol_mult_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(vcol_mult_n.inputs[1], mult2_mix_n.outputs["Mix Color"])

        # pass 4
        node_tree.links.new(compose_lighting_n.inputs["Specular Color"], spec_vcol_mult_n.outputs[0])

    @staticmethod
    def set_mult_texture(node_tree, image):
        """Set multiplication texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to mult texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[DifSpecWeightMult2.MULT_TEX_NODE].image = image

    @staticmethod
    def set_mult_texture_settings(node_tree, settings):
        """Set multiplication texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifSpecWeightMult2.MULT_TEX_NODE], settings)

    @staticmethod
    def set_mult_uv(node_tree, uv_layer):
        """Set UV layer to multiplication texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mult texture
        :type uv_layer: str
        """

        DifSpec.set_base_uv(node_tree, uv_layer)

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set UV scaling factors for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: UV scale factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[DifSpecWeightMult2.UV_SCALE_NODE].inputs['Scale'].default_value[0] = aux_property[0]["value"]
        node_tree.nodes[DifSpecWeightMult2.UV_SCALE_NODE].inputs['Scale'].default_value[1] = aux_property[1]["value"]

    @staticmethod
    def set_tg0_flavor(node_tree, switch_on):
        """Set zero texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg0.is_set(node_tree):

            out_node = node_tree.nodes[DifSpecWeightMult2.GEOM_NODE]
            in_node = node_tree.nodes[DifSpecWeightMult2.UV_SCALE_NODE]
            in_node2 = node_tree.nodes[DifSpecWeightMult2.BASE_TEX_NODE]

            out_node.location.x -= 185 * 2
            location = (out_node.location.x + 185, out_node.location.y)

            tg0.init(node_tree, location, out_node.outputs["Position"], in_node.inputs["Vector"])
            tg0.init(node_tree, location, out_node.outputs["Position"], in_node2.inputs["Vector"])

        elif not switch_on:

            tg0.delete(node_tree)

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set zero texture generation scale.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        if tg0.is_set(node_tree):

            tg0.set_scale(node_tree, aux_property[0]['value'], aux_property[1]['value'])
