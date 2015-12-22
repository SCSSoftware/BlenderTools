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
from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.eut2.dif_anim import anim_blend_factor_ng
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import blend_over


class DifAnim(Dif):
    ANIM_SPEED_NODE = "SpeedNode"
    BLEND_FACTOR_NODE = "BlendFactorGNode"
    SEC_GEOM_NODE = "SecondGeometry"
    OVER_TEX_NODE = "OverTex"
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

        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])

        # nodes creation
        anim_speed_n = node_tree.nodes.new("ShaderNodeValue")
        anim_speed_n.name = anim_speed_n.label = DifAnim.ANIM_SPEED_NODE
        anim_speed_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)

        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = sec_geom_n.label = DifAnim.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1000)
        sec_geom_n.uv_layer = _MESH_consts.none_uv

        blend_fac_gn = node_tree.nodes.new("ShaderNodeGroup")
        blend_fac_gn.name = blend_fac_gn.label = anim_blend_factor_ng.BLEND_FACTOR_G
        blend_fac_gn.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        blend_fac_gn.node_tree = anim_blend_factor_ng.get_node_group()

        over_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        over_tex_n.name = over_tex_n.label = DifAnim.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1000)

        base_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_mix_n.name = base_over_mix_n.label = DifAnim.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        base_over_mix_n.blend_type = "MIX"

        opacity_n = node_tree.nodes.new("ShaderNodeMixRGB")
        opacity_n.name = opacity_n.label = Dif.OPACITY_NODE
        opacity_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1100)
        opacity_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(blend_fac_gn.inputs['Speed'], anim_speed_n.outputs[0])
        node_tree.links.new(over_tex_n.inputs['Vector'], sec_geom_n.outputs['UV'])

        # pass 1
        node_tree.links.new(base_over_mix_n.inputs['Fac'], blend_fac_gn.outputs['Factor'])
        node_tree.links.new(base_over_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(base_over_mix_n.inputs['Color2'], over_tex_n.outputs['Color'])

        node_tree.links.new(opacity_n.inputs['Fac'], blend_fac_gn.outputs['Factor'])
        node_tree.links.new(opacity_n.inputs['Color1'], base_tex_n.outputs['Value'])
        node_tree.links.new(opacity_n.inputs['Color2'], over_tex_n.outputs['Value'])

        # pass 2
        node_tree.links.new(vcol_mult_n.inputs['Color2'], base_over_mix_n.outputs['Color'])

    @staticmethod
    def set_over_texture(node_tree, texture):
        """Set overlying texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to over texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifAnim.OVER_TEX_NODE].texture = texture

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to overlying texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[DifAnim.SEC_GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not blend_over.is_set(node_tree):
            out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
            in_node = node_tree.nodes[Dif.OPACITY_NODE]
            location = (out_node.location.x - 185 * 2, out_node.location.y - 500)

            alpha_test.init(node_tree, location, in_node.outputs['Color'], out_node.inputs['Alpha'])
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
            Dif.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
        in_node = node_tree.nodes[Dif.OPACITY_NODE]

        if switch_on:
            blend_over.init(node_tree, in_node.outputs['Color'], out_node.inputs['Alpha'])
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
            Dif.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
        in_node = node_tree.nodes[Dif.OPACITY_NODE]

        if switch_on:
            blend_add.init(node_tree, in_node.outputs['Color'], out_node.inputs['Alpha'])
        else:
            blend_add.delete(node_tree)

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set animation speed.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: animation speed represented with one float auxiliary entry
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[DifAnim.ANIM_SPEED_NODE].outputs[0].default_value = aux_property[0]['value']
