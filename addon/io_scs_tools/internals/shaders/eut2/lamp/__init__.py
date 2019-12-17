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
from io_scs_tools.internals.shaders.eut2.std_node_groups import lampmask_mixer_ng
from io_scs_tools.utils import material as _material_utils


class Lamp(DifSpec):
    SEC_UVMAP_NODE = "SecondUVMap"
    MASK_TEX_NODE = "MaskTex"
    LAMPMASK_MIX_GROUP_NODE = "LampmaskMix"
    OUT_ADD_LAMPMASK_NODE = "LampmaskAdd"
    OUT_ALPHA_INVERSE_NODE = "OutAlphaInverse"
    OUT_MAT_NODE = "OutMat"

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
        output_n.location.x += pos_x_shift * 3

        # nodes creation
        sec_uvmap_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uvmap_n.name = sec_uvmap_n.label = Lamp.SEC_UVMAP_NODE
        sec_uvmap_n.location = (start_pos_x - pos_x_shift, start_pos_y + 2300)
        sec_uvmap_n.uv_map = _MESH_consts.none_uv

        mask_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mask_tex_n.name = mask_tex_n.label = Lamp.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2400)
        mask_tex_n.width = 140

        lampmask_mixer_n = node_tree.nodes.new("ShaderNodeGroup")
        lampmask_mixer_n.name = lampmask_mixer_n.label = Lamp.LAMPMASK_MIX_GROUP_NODE
        lampmask_mixer_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        lampmask_mixer_n.node_tree = lampmask_mixer_ng.get_node_group()

        out_add_lampmask_n = node_tree.nodes.new("ShaderNodeVectorMath")
        out_add_lampmask_n.name = out_add_lampmask_n.label = Lamp.OUT_ADD_LAMPMASK_NODE
        out_add_lampmask_n.location = (output_n.location.x - pos_x_shift * 2, compose_lighting_n.location.y + 200)
        out_add_lampmask_n.operation = "ADD"

        out_a_inv_n = node_tree.nodes.new("ShaderNodeMath")
        out_a_inv_n.name = out_a_inv_n.label = Lamp.OUT_ALPHA_INVERSE_NODE
        out_a_inv_n.location = (output_n.location.x - pos_x_shift * 2, output_n.location.y - 100)
        out_a_inv_n.operation = "SUBTRACT"
        out_a_inv_n.use_clamp = True
        out_a_inv_n.inputs[0].default_value = 0.999999  # TODO: change back to 1.0 after bug is fixed: https://developer.blender.org/T71426

        out_mat_n = node_tree.nodes.new("ShaderNodeEeveeSpecular")
        out_mat_n.name = out_mat_n.label = Lamp.OUT_MAT_NODE
        out_mat_n.location = (output_n.location.x - pos_x_shift, output_n.location.y)
        out_mat_n.inputs["Base Color"].default_value = (0.0,) * 4
        out_mat_n.inputs["Specular"].default_value = (0.0,) * 4

        # links creation
        node_tree.links.new(mask_tex_n.inputs['Vector'], sec_uvmap_n.outputs["UV"])

        node_tree.links.new(lampmask_mixer_n.inputs['Lampmask Tex Alpha'], mask_tex_n.outputs['Alpha'])
        node_tree.links.new(lampmask_mixer_n.inputs['Lampmask Tex Color'], mask_tex_n.outputs['Color'])
        node_tree.links.new(lampmask_mixer_n.inputs['UV Vector'], sec_uvmap_n.outputs['UV'])

        node_tree.links.new(out_add_lampmask_n.inputs[0], lampmask_mixer_n.outputs['Lampmask Addition Color'])
        node_tree.links.new(out_add_lampmask_n.inputs[1], compose_lighting_n.outputs['Color'])

        node_tree.links.new(out_a_inv_n.inputs[1], compose_lighting_n.outputs['Alpha'])

        node_tree.links.new(out_mat_n.inputs['Emissive Color'], out_add_lampmask_n.outputs[0])
        node_tree.links.new(out_mat_n.inputs['Transparency'], out_a_inv_n.outputs['Value'])

        node_tree.links.new(output_n.inputs["Surface"], out_mat_n.outputs['BSDF'])

    @staticmethod
    def set_mask_texture(node_tree, image):
        """Set mask texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to mask texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[Lamp.MASK_TEX_NODE].image = image

    @staticmethod
    def set_mask_texture_settings(node_tree, settings):
        """Set mask texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[Lamp.MASK_TEX_NODE], settings)

        # due the fact uvs get clamped in vertex shader, we have to manually switch repeat on, for effect to work correctly
        node_tree.nodes[Lamp.MASK_TEX_NODE].extension = "REPEAT"

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

        node_tree.nodes[Lamp.SEC_UVMAP_NODE].uv_map = uv_layer
