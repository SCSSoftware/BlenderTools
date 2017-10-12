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


from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.std_node_groups import mult2_mix
from io_scs_tools.internals.shaders.flavors import tg0


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

        geom_n = node_tree.nodes[DifSpec.GEOM_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpec.VCOLOR_SCALE_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        opacity_mult_n = node_tree.nodes[DifSpec.OPACITY_NODE]
        out_mat_n = node_tree.nodes[DifSpec.OUT_MAT_NODE]

        # move existing
        geom_n.location.x -= pos_x_shift * 2
        opacity_mult_n.location.y -= 100
        for node in node_tree.nodes:
            if node.location.x > start_pos_x + pos_x_shift:
                node.location.x += pos_x_shift

        # nodes creation
        uv_scale_n = node_tree.nodes.new("ShaderNodeMapping")
        uv_scale_n.name = uv_scale_n.label = DifSpecWeightMult2.UV_SCALE_NODE
        uv_scale_n.location = (start_pos_x - pos_x_shift * 2, start_pos_y + 1200)
        uv_scale_n.vector_type = "POINT"
        uv_scale_n.translation = uv_scale_n.rotation = (0.0,) * 3
        uv_scale_n.scale = (1.0,) * 3
        uv_scale_n.use_min = uv_scale_n.use_max = False

        mult_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        mult_tex_n.name = mult_tex_n.label = DifSpecWeightMult2.MULT_TEX_NODE
        mult_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        mult2_mix_gn = node_tree.nodes.new("ShaderNodeGroup")
        mult2_mix_gn.name = mult2_mix_gn.label = DifSpecWeightMult2.MULT2_MIX_GROUP_NODE
        mult2_mix_gn.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1400)
        mult2_mix_gn.node_tree = mult2_mix.get_node_group()

        spec_vcol_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        spec_vcol_mult_n.name = spec_vcol_mult_n.label = DifSpecWeightMult2.SPEC_VCOL_MULT_NODE
        spec_vcol_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1800)
        spec_vcol_mult_n.blend_type = "MULTIPLY"
        spec_vcol_mult_n.inputs["Fac"].default_value = 1.0

        # links creation
        node_tree.links.new(uv_scale_n.inputs["Vector"], geom_n.outputs["UV"])

        node_tree.links.new(mult_tex_n.inputs["Vector"], uv_scale_n.outputs["Vector"])

        # pass 1
        node_tree.links.new(mult2_mix_gn.inputs["Base Alpha"], base_tex_n.outputs["Value"])
        node_tree.links.new(mult2_mix_gn.inputs["Base Color"], base_tex_n.outputs["Color"])
        node_tree.links.new(mult2_mix_gn.inputs["Mult Alpha"], mult_tex_n.outputs["Value"])
        node_tree.links.new(mult2_mix_gn.inputs["Mult Color"], mult_tex_n.outputs["Color"])

        # pass 2
        node_tree.links.new(spec_mult_n.inputs["Color2"], mult2_mix_gn.outputs["Mix Alpha"])

        node_tree.links.new(opacity_mult_n.inputs[0], mult2_mix_gn.outputs["Mix Alpha"])

        # pass 3
        node_tree.links.new(spec_vcol_mult_n.inputs["Color1"], spec_mult_n.outputs["Color"])
        node_tree.links.new(spec_vcol_mult_n.inputs["Color2"], vcol_scale_n.outputs["Color"])

        node_tree.links.new(vcol_mult_n.inputs["Color2"], mult2_mix_gn.outputs["Mix Color"])

        # pass 4
        node_tree.links.new(out_mat_n.inputs["Spec"], spec_vcol_mult_n.outputs["Color"])

    @staticmethod
    def set_mult_texture(node_tree, texture):
        """Set multiplication texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to mult texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecWeightMult2.MULT_TEX_NODE].texture = texture

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

        node_tree.nodes[DifSpecWeightMult2.UV_SCALE_NODE].scale[0] = aux_property[0]["value"]
        node_tree.nodes[DifSpecWeightMult2.UV_SCALE_NODE].scale[1] = aux_property[1]["value"]

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

            tg0.init(node_tree, location, out_node.outputs["Global"], in_node.inputs["Vector"])
            tg0.init(node_tree, location, out_node.outputs["Global"], in_node2.inputs["Vector"])

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
