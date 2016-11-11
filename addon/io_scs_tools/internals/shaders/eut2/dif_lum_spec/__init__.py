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


class DifLumSpec(DifSpec):
    LUM_MIX_NODE = "LuminosityMix"
    LUM_BOOST_MIX_NODE = "LuminosityBoostMix"
    LUM_BOOST_VALUE_NODE = "LuminosityBoost"

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
        DifSpec.init(node_tree)

        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[DifSpec.SPEC_COL_NODE]

        # move existing
        output_n.location.x += pos_x_shift

        # nodes creation
        lum_boost_val_n = node_tree.nodes.new("ShaderNodeValue")
        lum_boost_val_n.name = lum_boost_val_n.label = DifLumSpec.LUM_BOOST_VALUE_NODE
        lum_boost_val_n.location = (spec_col_n.location.x, spec_col_n.location.y + 100)

        lum_boost_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        lum_boost_mix_n.name = lum_boost_mix_n.label = DifLumSpec.LUM_BOOST_MIX_NODE
        lum_boost_mix_n.location = (compose_lighting_n.location.x, compose_lighting_n.location.y + 200)
        lum_boost_mix_n.blend_type = "MULTIPLY"
        lum_boost_mix_n.inputs["Fac"].default_value = 1.0

        lum_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        lum_mix_n.name = lum_mix_n.label = DifLumSpec.LUM_MIX_NODE
        lum_mix_n.location = (compose_lighting_n.location.x + pos_x_shift, compose_lighting_n.location.y + 100)
        lum_mix_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(lum_boost_mix_n.inputs['Color1'], lum_boost_val_n.outputs['Value'])
        node_tree.links.new(lum_boost_mix_n.inputs['Color2'], base_tex_n.outputs['Color'])

        node_tree.links.new(lum_mix_n.inputs['Fac'], base_tex_n.outputs['Color'])
        node_tree.links.new(lum_mix_n.inputs['Color1'], compose_lighting_n.outputs['Composed Color'])
        node_tree.links.new(lum_mix_n.inputs['Color2'], lum_boost_mix_n.outputs['Color'])

        node_tree.links.new(output_n.inputs['Color'], lum_mix_n.outputs['Color'])

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminosity boost factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[DifLumSpec.LUM_BOOST_VALUE_NODE].outputs[0].default_value = 1 + aux_property[0]['value']

    @staticmethod
    def set_linv_flavor(node_tree, switch_on):
        """Set luminance inverse flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        lum_mix_n = node_tree.nodes[DifLumSpec.LUM_MIX_NODE]
        lum_boost_mix_n = node_tree.nodes[DifLumSpec.LUM_BOOST_MIX_NODE]
        out_mat_n = node_tree.nodes[DifSpec.OUT_MAT_NODE]

        if switch_on:
            node_tree.links.new(lum_mix_n.inputs['Color1'], lum_boost_mix_n.outputs['Color'])
            node_tree.links.new(lum_mix_n.inputs['Color2'], out_mat_n.outputs['Color'])
        else:
            node_tree.links.new(lum_mix_n.inputs['Color1'], out_mat_n.outputs['Color'])
            node_tree.links.new(lum_mix_n.inputs['Color2'], lum_boost_mix_n.outputs['Color'])

    @staticmethod
    def set_lvcol_flavor(node_tree, switch_on):
        """Set (vertex color*luminance) flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        lum_boost_mix_n = node_tree.nodes[DifLumSpec.LUM_BOOST_MIX_NODE]

        if switch_on:
            node_tree.links.new(lum_boost_mix_n.inputs['Color2'], vcol_mult_n.outputs['Color'])
        else:
            node_tree.links.new(lum_boost_mix_n.inputs['Color2'], base_tex_n.outputs['Color'])
