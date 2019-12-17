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
from io_scs_tools.internals.shaders.eut2.dif_spec_mult_dif_spec import DifSpecMultDifSpec
from io_scs_tools.utils import material as _material_utils


class DifSpecMultDifSpecIamodDifSpec(DifSpecMultDifSpec):
    THIRD_UVMAP_NODE = "ThirdUVMap"
    IAMOD_TEX_NODE = "IamodTex"
    IAMOD_SCALE_NODE = "IamodScaled"
    IAMOD_SCALE_A_NODE = "IamodAlphaScaled"
    IAMOD_MULTBASE_COL_MIX_NODE = "IamodMultBaseColorMix"
    IAMOD_MULTBASE_A_MIX_NODE = "IamodMultBaseAlphaMix"

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
        DifSpecMultDifSpec.init(node_tree)

        vcol_group_n = node_tree.nodes[DifSpecMultDifSpec.VCOL_GROUP_NODE]
        mult_base_col_mix_n = node_tree.nodes[DifSpecMultDifSpec.MULT_BASE_COL_MIX_NODE]
        mult_base_a_mix_n = node_tree.nodes[DifSpecMultDifSpec.MULT_BASE_A_MIX_NODE]
        vcol_scale_n = node_tree.nodes[DifSpecMultDifSpec.VCOLOR_SCALE_NODE]
        vcol_mult_n = node_tree.nodes[DifSpecMultDifSpec.VCOLOR_MULT_NODE]
        diff_mult_n = node_tree.nodes[DifSpecMultDifSpec.DIFF_MULT_NODE]
        spec_mult_n = node_tree.nodes[DifSpecMultDifSpec.SPEC_MULT_NODE]

        # move existing
        spec_mult_n.location.x += pos_x_shift

        vcol_scale_n.location.y -= 200
        vcol_mult_n.location.y -= 200
        diff_mult_n.location.y -= 200
        mult_base_col_mix_n.location.y -= 200

        # node creation
        third_uvmap_n = node_tree.nodes.new("ShaderNodeUVMap")
        third_uvmap_n.name = DifSpecMultDifSpecIamodDifSpec.THIRD_UVMAP_NODE
        third_uvmap_n.label = DifSpecMultDifSpecIamodDifSpec.THIRD_UVMAP_NODE
        third_uvmap_n.location = (start_pos_x - pos_x_shift, start_pos_y + 900)
        third_uvmap_n.uv_map = _MESH_consts.none_uv

        iamod_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        iamod_tex_n.name = DifSpecMultDifSpecIamodDifSpec.IAMOD_TEX_NODE
        iamod_tex_n.label = DifSpecMultDifSpecIamodDifSpec.IAMOD_TEX_NODE
        iamod_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 900)
        iamod_tex_n.width = 140

        iamod_scale_col_n = node_tree.nodes.new("ShaderNodeMixRGB")
        iamod_scale_col_n.name = DifSpecMultDifSpecIamodDifSpec.IAMOD_SCALE_NODE
        iamod_scale_col_n.label = DifSpecMultDifSpecIamodDifSpec.IAMOD_SCALE_NODE
        iamod_scale_col_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1000)
        iamod_scale_col_n.blend_type = "MIX"
        iamod_scale_col_n.inputs['Color2'].default_value = (1,) * 4

        iamod_scale_a_n = node_tree.nodes.new("ShaderNodeMixRGB")
        iamod_scale_a_n.name = DifSpecMultDifSpecIamodDifSpec.IAMOD_SCALE_A_NODE
        iamod_scale_a_n.label = DifSpecMultDifSpecIamodDifSpec.IAMOD_SCALE_A_NODE
        iamod_scale_a_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1500)
        iamod_scale_a_n.blend_type = "MIX"
        iamod_scale_a_n.inputs['Color2'].default_value = (1,) * 4

        iamod_multbase_col_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        iamod_multbase_col_mix_n.name = DifSpecMultDifSpecIamodDifSpec.IAMOD_MULTBASE_COL_MIX_NODE
        iamod_multbase_col_mix_n.label = DifSpecMultDifSpecIamodDifSpec.IAMOD_MULTBASE_COL_MIX_NODE
        iamod_multbase_col_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1100)
        iamod_multbase_col_mix_n.operation = "MULTIPLY"

        iamod_multbase_a_mix_n = node_tree.nodes.new("ShaderNodeMath")
        iamod_multbase_a_mix_n.name = DifSpecMultDifSpecIamodDifSpec.IAMOD_MULTBASE_A_MIX_NODE
        iamod_multbase_a_mix_n.label = DifSpecMultDifSpecIamodDifSpec.IAMOD_MULTBASE_A_MIX_NODE
        iamod_multbase_a_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1600)
        iamod_multbase_a_mix_n.operation = "MULTIPLY"

        # links creation
        node_tree.links.new(iamod_tex_n.inputs['Vector'], third_uvmap_n.outputs['UV'])

        node_tree.links.new(iamod_scale_col_n.inputs['Fac'], vcol_group_n.outputs['Vertex Color Alpha'])
        node_tree.links.new(iamod_scale_col_n.inputs['Color1'], iamod_tex_n.outputs['Color'])

        node_tree.links.new(iamod_scale_a_n.inputs['Fac'], vcol_group_n.outputs['Vertex Color Alpha'])
        node_tree.links.new(iamod_scale_a_n.inputs['Color1'], iamod_tex_n.outputs['Alpha'])

        node_tree.links.new(iamod_multbase_col_mix_n.inputs[0], mult_base_col_mix_n.outputs[0])
        node_tree.links.new(iamod_multbase_col_mix_n.inputs[1], iamod_scale_col_n.outputs['Color'])

        node_tree.links.new(iamod_multbase_a_mix_n.inputs[0], mult_base_a_mix_n.outputs['Value'])
        node_tree.links.new(iamod_multbase_a_mix_n.inputs[1], iamod_scale_a_n.outputs['Color'])

        node_tree.links.new(vcol_mult_n.inputs[1], iamod_multbase_col_mix_n.outputs[0])
        node_tree.links.new(spec_mult_n.inputs[1], iamod_multbase_a_mix_n.outputs['Value'])

    @staticmethod
    def set_iamod_texture(node_tree, image):
        """Set inverse alpha modulating texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to iamod texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[DifSpecMultDifSpecIamodDifSpec.IAMOD_TEX_NODE].image = image

    @staticmethod
    def set_iamod_texture_settings(node_tree, settings):
        """Set inverse alpha modulating texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifSpecMultDifSpecIamodDifSpec.IAMOD_TEX_NODE], settings)

    @staticmethod
    def set_iamod_uv(node_tree, uv_layer):
        """Set UV layer to inverse alpha modulating texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for iamod texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[DifSpecMultDifSpecIamodDifSpec.THIRD_UVMAP_NODE].uv_map = uv_layer

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
    def set_blend_mult_flavor(node_tree, switch_on):
        """Set blend mult flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend mult should be switched on or off
        :type switch_on: bool
        """

        pass  # NOTE: no support for this flavor; overriding with empty function
