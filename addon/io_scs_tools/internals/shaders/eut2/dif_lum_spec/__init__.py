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
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import blend_mult


class DifLumSpec(DifSpec):
    LUM_MIX_NODE = "LuminosityMix"
    LUM_A_INVERSE_NODE = "LumTransp=1-Alpha"
    LUM_OUT_SHADER_NODE = "LumShader"
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

        pos_x_shift = 185

        # init parent
        DifSpec.init(node_tree)

        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        spec_col_n = node_tree.nodes[DifSpec.SPEC_COL_NODE]

        # move existing
        output_n.location.x += pos_x_shift * 4

        # nodes creation
        lum_boost_val_n = node_tree.nodes.new("ShaderNodeValue")
        lum_boost_val_n.name = lum_boost_val_n.label = DifLumSpec.LUM_BOOST_VALUE_NODE
        lum_boost_val_n.location = (spec_col_n.location.x, spec_col_n.location.y + 100)

        lum_boost_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lum_boost_mix_n.name = lum_boost_mix_n.label = DifLumSpec.LUM_BOOST_MIX_NODE
        lum_boost_mix_n.location = (compose_lighting_n.location.x, compose_lighting_n.location.y + 200)
        lum_boost_mix_n.operation = "MULTIPLY"

        lum_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        lum_mix_n.name = lum_mix_n.label = DifLumSpec.LUM_MIX_NODE
        lum_mix_n.location = (compose_lighting_n.location.x + pos_x_shift * 2, compose_lighting_n.location.y + 100)
        lum_mix_n.blend_type = "MIX"

        lum_a_inv_n = node_tree.nodes.new("ShaderNodeMath")
        lum_a_inv_n.name = lum_a_inv_n.label = DifLumSpec.LUM_A_INVERSE_NODE
        lum_a_inv_n.location = (compose_lighting_n.location.x + pos_x_shift * 2, compose_lighting_n.location.y - 300)
        lum_a_inv_n.operation = "SUBTRACT"
        lum_a_inv_n.use_clamp = True
        lum_a_inv_n.inputs[0].default_value = 0.999999  # TODO: change back to 1.0 after bug is fixed: https://developer.blender.org/T71426

        lum_out_shader_n = node_tree.nodes.new("ShaderNodeEeveeSpecular")
        lum_out_shader_n.name = lum_out_shader_n.label = DifLumSpec.LUM_OUT_SHADER_NODE
        lum_out_shader_n.location = (compose_lighting_n.location.x + pos_x_shift * 3, compose_lighting_n.location.y - 200)
        lum_out_shader_n.inputs["Base Color"].default_value = (0.0,) * 4
        lum_out_shader_n.inputs["Specular"].default_value = (0.0,) * 4

        # links creation
        node_tree.links.new(lum_boost_mix_n.inputs[0], lum_boost_val_n.outputs['Value'])
        node_tree.links.new(lum_boost_mix_n.inputs[1], base_tex_n.outputs['Color'])

        node_tree.links.new(lum_mix_n.inputs['Fac'], base_tex_n.outputs['Alpha'])
        node_tree.links.new(lum_mix_n.inputs['Color1'], compose_lighting_n.outputs['Color'])
        node_tree.links.new(lum_mix_n.inputs['Color2'], lum_boost_mix_n.outputs[0])

        node_tree.links.new(lum_a_inv_n.inputs[1], compose_lighting_n.outputs['Alpha'])

        node_tree.links.new(lum_out_shader_n.inputs['Emissive Color'], lum_mix_n.outputs['Color'])
        node_tree.links.new(lum_out_shader_n.inputs['Transparency'], lum_a_inv_n.outputs['Value'])

        node_tree.links.new(output_n.inputs['Surface'], lum_out_shader_n.outputs['BSDF'])

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
                lum_out_shader_n = node_tree.nodes[DifLumSpec.LUM_OUT_SHADER_NODE]

                # alpha test pass has to get fully opaque input, thus remove transparency linkage
                compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
                if compose_lighting_n.inputs['Alpha'].links:
                    node_tree.links.remove(compose_lighting_n.inputs['Alpha'].links[0])
                if lum_out_shader_n.inputs['Transparency'].links:
                    node_tree.links.remove(lum_out_shader_n.inputs['Transparency'].links[0])

                shader_from = lum_out_shader_n.outputs['BSDF']
                alpha_from = node_tree.nodes[DifSpec.OPACITY_NODE].outputs[0]
                shader_to = lum_out_shader_n.outputs['BSDF'].links[0].to_socket

                alpha_test.add_pass(node_tree, shader_from, alpha_from, shader_to)

        if blend_add.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_mult.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_over.is_set(node_tree):
            material.blend_method = "BLEND"

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
        :param switch_on: flag indication if blending should be switched on or off
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
        :param switch_on: flag indication if blending should be switched on or off
        :type switch_on: bool
        """

        if switch_on:
            out_node = node_tree.nodes[DifSpec.OUTPUT_NODE]
            in_node = node_tree.nodes[DifLumSpec.LUM_OUT_SHADER_NODE]

            # put it on location of output node & move output node for one slot to the right
            location = tuple(out_node.location)
            out_node.location.x += 185

            blend_add.init(node_tree, location, in_node.outputs['BSDF'], out_node.inputs['Surface'])
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
            out_node = node_tree.nodes[DifSpec.OUTPUT_NODE]
            in_node = node_tree.nodes[DifLumSpec.LUM_OUT_SHADER_NODE]

            # break link to lum out shader transparency as mult uses DST_COLOR as source factor in blend function
            compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
            if compose_lighting_n.inputs['Alpha'].links:
                node_tree.links.remove(compose_lighting_n.inputs['Alpha'].links[0])
            lum_out_shader_n = node_tree.nodes[DifLumSpec.LUM_OUT_SHADER_NODE]
            if lum_out_shader_n.inputs['Transparency'].links:
                node_tree.links.remove(lum_out_shader_n.inputs['Transparency'].links[0])

            # put it on location of output node & move output node for one slot to the right
            location = tuple(out_node.location)
            out_node.location.x += 185

            blend_mult.init(node_tree, location, in_node.outputs['BSDF'], out_node.inputs['Surface'])
        else:
            blend_mult.delete(node_tree)

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
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]

        if switch_on:
            node_tree.links.new(lum_mix_n.inputs['Color1'], lum_boost_mix_n.outputs[0])
            node_tree.links.new(lum_mix_n.inputs['Color2'], compose_lighting_n.outputs['Color'])
        else:
            node_tree.links.new(lum_mix_n.inputs['Color1'], compose_lighting_n.outputs['Color'])
            node_tree.links.new(lum_mix_n.inputs['Color2'], lum_boost_mix_n.outputs[0])

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
            node_tree.links.new(lum_boost_mix_n.inputs[1], vcol_mult_n.outputs[0])
        else:
            node_tree.links.new(lum_boost_mix_n.inputs[1], base_tex_n.outputs['Color'])
