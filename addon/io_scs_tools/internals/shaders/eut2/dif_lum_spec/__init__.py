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

from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.std_passes.lum import StdLum
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import blend_mult


class DifLumSpec(DifSpec, StdLum):

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

        # init parent
        DifSpec.init(node_tree)

        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]

        StdLum.add(node_tree,
                   base_tex_n.outputs['Color'],
                   base_tex_n.outputs['Alpha'],
                   compose_lighting_n.outputs['Color'],
                   compose_lighting_n.outputs['Alpha'],
                   output_n.inputs['Surface'])

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
                lum_out_shader_n = node_tree.nodes[StdLum.LUM_OUT_SHADER_NODE]

                # alpha test pass has to get fully opaque input, thus remove transparency linkage
                compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
                if compose_lighting_n.inputs['Alpha'].links:
                    node_tree.links.remove(compose_lighting_n.inputs['Alpha'].links[0])
                if lum_out_shader_n.inputs['Alpha'].links:
                    node_tree.links.remove(lum_out_shader_n.inputs['Alpha'].links[0])

                shader_from = lum_out_shader_n.outputs['Shader']
                alpha_from = node_tree.nodes[DifSpec.OPACITY_NODE].outputs[0]
                shader_to = lum_out_shader_n.outputs['Shader'].links[0].to_socket

                alpha_test.add_pass(node_tree, shader_from, alpha_from, shader_to)

        if blend_add.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_mult.is_set(node_tree):
            material.blend_method = "BLEND"
        if blend_over.is_set(node_tree):
            material.blend_method = "BLEND"

        if material.blend_method == "OPAQUE" and node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links:
            node_tree.links.remove(node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE].inputs['Alpha'].links[0])

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminosity boost factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: luminosity output represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        StdLum.set_aux5(node_tree, aux_property)

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
            in_node = node_tree.nodes[StdLum.LUM_OUT_SHADER_NODE]

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
            out_node = node_tree.nodes[DifSpec.OUTPUT_NODE]
            in_node = node_tree.nodes[StdLum.LUM_OUT_SHADER_NODE]

            # break link to lum out shader transparency as mult uses DST_COLOR as source factor in blend function
            compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
            if compose_lighting_n.inputs['Alpha'].links:
                node_tree.links.remove(compose_lighting_n.inputs['Alpha'].links[0])
            lum_out_shader_n = in_node
            if lum_out_shader_n.inputs['Alpha'].links:
                node_tree.links.remove(lum_out_shader_n.inputs['Alpha'].links[0])

            # put it on location of output node & move output node for one slot to the right
            location = tuple(out_node.location)
            out_node.location.x += 185

            blend_mult.init(node_tree, location, in_node.outputs['Shader'], out_node.inputs['Surface'])
        else:
            blend_mult.delete(node_tree)

    @staticmethod
    def set_lvcol_flavor(node_tree, switch_on):
        """Set (vertex color*luminance) flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]
        vcol_opacity_n = node_tree.nodes[DifSpec.OPACITY_NODE]
        lum_col_vcol_modul_n = node_tree.nodes[StdLum.LUM_COL_LVCOL_MULT_NODE]
        lum_a_vcol_modul_n = node_tree.nodes[StdLum.LUM_A_LVCOL_MULT_NODE]

        if switch_on:
            node_tree.links.new(lum_col_vcol_modul_n.inputs[1], vcol_mult_n.outputs[0])
            node_tree.links.new(lum_a_vcol_modul_n.inputs[1], vcol_opacity_n.outputs[0])
        else:
            node_tree.links.remove(lum_col_vcol_modul_n.inputs[1].links[0])
            node_tree.links.remove(lum_a_vcol_modul_n.inputs[1].links[0])
