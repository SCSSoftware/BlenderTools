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


class DifSpecOverDifOpac(DifSpec):
    SEC_GEOM_NODE = "SecGeomety"
    OVER_TEX_NODE = "OverTex"
    OVER_MIX_NODE = "OverMix"

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

        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]

        # nodes creation
        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = DifSpecOverDifOpac.SEC_GEOM_NODE
        sec_geom_n.label = DifSpecOverDifOpac.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)

        over_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        over_tex_n.name = DifSpecOverDifOpac.OVER_TEX_NODE
        over_tex_n.label = DifSpecOverDifOpac.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        over_mix_node = node_tree.nodes.new("ShaderNodeMixRGB")
        over_mix_node.name = DifSpecOverDifOpac.OVER_MIX_NODE
        over_mix_node.label = DifSpecOverDifOpac.OVER_MIX_NODE
        over_mix_node.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        over_mix_node.blend_type = "MIX"

        # links creation
        node_tree.links.new(over_tex_n.inputs['Vector'], sec_geom_n.outputs['UV'])

        node_tree.links.new(over_mix_node.inputs['Fac'], over_tex_n.outputs['Value'])
        node_tree.links.new(over_mix_node.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(over_mix_node.inputs['Color2'], over_tex_n.outputs['Color'])

        node_tree.links.new(vcol_mult_n.inputs['Color2'], over_mix_node.outputs['Color'])

    @staticmethod
    def set_over_texture(node_tree, texture):
        """Set overlying texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to over texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecOverDifOpac.OVER_TEX_NODE].texture = texture

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to overlying texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        node_tree.nodes[DifSpecOverDifOpac.SEC_GEOM_NODE].uv_layer = uv_layer