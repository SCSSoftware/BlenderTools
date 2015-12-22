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


from io_scs_tools.internals.shaders.eut2.dif import Dif


class LightTex(Dif):
    SPEC_MULT_NODE = "SpecMultiplier"
    RGB_TO_BW_ALPHA_NODE = "RGBToBWColor"

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

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])

        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        v_col_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        out_mat_n = node_tree.nodes[Dif.OUT_MAT_NODE]

        # node creation
        spec_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        spec_mult_n.name = LightTex.SPEC_MULT_NODE
        spec_mult_n.label = LightTex.SPEC_MULT_NODE
        spec_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1850)
        spec_mult_n.blend_type = "MULTIPLY"
        spec_mult_n.inputs['Fac'].default_value = 1

        rgb_to_bw_n = node_tree.nodes.new("ShaderNodeRGBToBW")
        rgb_to_bw_n.name = LightTex.RGB_TO_BW_ALPHA_NODE
        rgb_to_bw_n.label = LightTex.RGB_TO_BW_ALPHA_NODE
        rgb_to_bw_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)

        # links creation
        node_tree.links.new(spec_mult_n.inputs["Color1"], v_col_mult_n.outputs["Color"])
        node_tree.links.new(out_mat_n.inputs["Spec"], spec_mult_n.outputs["Color"])

        node_tree.links.new(rgb_to_bw_n.inputs["Color"], base_tex_n.outputs["Color"])
        node_tree.links.new(out_mat_n.inputs["Alpha"], rgb_to_bw_n.outputs["Val"])

    @staticmethod
    def set_material(node_tree, material):
        """Set output material for this shader.
        NOTE: extended to ensure transparency for this shader, which gives
        partial look of multiplying with underlying surfaces.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """
        Dif.set_material(node_tree, material)

        material.use_transparency = True

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        pass  # NOTE: no support for this flavor; overriding with empty function

    @staticmethod
    def set_blend_over_flavor(node_tree, switch_on):
        """Set blend over flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend over should be switched on or off
        :type switch_on: bool
        """

        pass  # NOTE: no support for this flavor; overriding with empty function

    @staticmethod
    def set_blend_add_flavor(node_tree, switch_on):
        """Set blend add flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend add should be switched on or off
        :type switch_on: bool
        """

        pass  # NOTE: no support for this flavor; overriding with empty function

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set depth bias.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        pass  # NOTE: no support for this parameter as there is no way to simulate eye-space z-bias
