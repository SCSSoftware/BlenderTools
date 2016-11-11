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
from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.std_node_groups import lampmask_mixer


class Lamp(DifSpec):
    SEC_GEOM_NODE = "SecondGeometry"
    MASK_TEX_NODE = "MaskTex"
    LAMPMASK_MIX_GROUP_NODE = "LampmaskMix"
    OUT_ADD_LAMPMASK_NODE = "LampmaskAdd"

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
        Lamp.init(node_tree, init_dif_spec=True, start_pos_x=0, start_pos_y=0)

    @staticmethod
    def init(node_tree, init_dif_spec=True, start_pos_x=0, start_pos_y=0):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param init_dif_spec should dif spec be initilized, True by default
        :type init_dif_spec bool
        :param start_pos_x: x start position
        :type start_pos_x: int
        :param start_pos_y: y start position
        :type start_pos_y: int
        """

        pos_x_shift = 185

        # init parent
        if init_dif_spec:
            DifSpec.init(node_tree)

        compose_lighting_n = node_tree.nodes[DifSpec.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]

        # move existing
        output_n.location.x += pos_x_shift

        # nodes creation
        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = Lamp.SEC_GEOM_NODE
        sec_geom_n.label = Lamp.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 2300)
        sec_geom_n.uv_layer = _MESH_consts.none_uv

        mask_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        mask_tex_n.name = Lamp.MASK_TEX_NODE
        mask_tex_n.label = Lamp.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2400)

        lampmask_mixr_gn = node_tree.nodes.new("ShaderNodeGroup")
        lampmask_mixr_gn.name = Lamp.LAMPMASK_MIX_GROUP_NODE
        lampmask_mixr_gn.label = Lamp.LAMPMASK_MIX_GROUP_NODE
        lampmask_mixr_gn.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        lampmask_mixr_gn.node_tree = lampmask_mixer.get_node_group()

        out_add_lampmask_n = node_tree.nodes.new("ShaderNodeMixRGB")
        out_add_lampmask_n.name = Lamp.OUT_ADD_LAMPMASK_NODE
        out_add_lampmask_n.label = Lamp.OUT_ADD_LAMPMASK_NODE
        out_add_lampmask_n.location = (output_n.location.x - pos_x_shift, start_pos_y + 1950)
        out_add_lampmask_n.blend_type = "ADD"
        out_add_lampmask_n.inputs['Fac'].default_value = 1

        # links creation
        node_tree.links.new(mask_tex_n.inputs['Vector'], sec_geom_n.outputs["UV"])

        node_tree.links.new(lampmask_mixr_gn.inputs["Lampmask Tex Alpha"], mask_tex_n.outputs["Value"])
        node_tree.links.new(lampmask_mixr_gn.inputs["Lampmask Tex Color"], mask_tex_n.outputs["Color"])
        node_tree.links.new(lampmask_mixr_gn.inputs["UV Vector"], sec_geom_n.outputs["UV"])

        node_tree.links.new(out_add_lampmask_n.inputs["Color1"], lampmask_mixr_gn.outputs["Lampmask Addition Color"])
        node_tree.links.new(out_add_lampmask_n.inputs["Color2"], compose_lighting_n.outputs["Composed Color"])

        node_tree.links.new(output_n.inputs["Color"], out_add_lampmask_n.outputs["Color"])

    @staticmethod
    def set_mask_texture(node_tree, texture):
        """Set mask texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to mask texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Lamp.MASK_TEX_NODE].texture = texture

    @staticmethod
    def set_mask_uv(node_tree, uv_layer):
        """Set UV layer to mask texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mask texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Lamp.SEC_GEOM_NODE].uv_layer = uv_layer
