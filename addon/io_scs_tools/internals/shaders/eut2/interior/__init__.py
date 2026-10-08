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

# Copyright (C) 2024-2026: Michaleczeq

from ..parameters import get_fresnel_window
from ..dif_spec_add_env import DifSpecAddEnv
from .....consts import Mesh as _MESH_consts
from .....utils import material as _material_utils

class InteriorLit(DifSpecAddEnv):
    VGCOLOR_MULT_NODE = "VertexGlassColorMultiplier"
    GLASS_COL_NODE = "GlassColor"
    GLASS_COL_MIX_NODE = "GlassColorMix"
    LAYER0_TEX_NODE = "Layer0Tex"
    LAYER1_TEX_NODE = "Layer1Tex"
    MASK_TEX_NODE = "MaskTex"
    NMAP_TEX_NODE = "NmapTex"
    ENV_SEP_XYZ_NODE = "EnvSepXYZ"
    ENV_CHECK_XYZ_NODE = "EnvCheckXYZ"
    PERT_UVMAP_NODE = "PerturbationUVMap"
    

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
        DifSpecAddEnv.init(node_tree)

        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        uvmap_n = node_tree.nodes[DifSpecAddEnv.UVMAP_NODE]
        vcol_mult_n = node_tree.nodes[DifSpecAddEnv.VCOLOR_MULT_NODE]
        diff_mult_n = node_tree.nodes[DifSpecAddEnv.DIFF_MULT_NODE]
        add_env_group_n = node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE]

        # set fresnel type to schlick
        add_env_group_n.inputs['Fresnel Type'].default_value = 1.0

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.OPACITY_NODE])

        # move existing
        diff_mult_n.location.x += pos_x_shift
        vcol_mult_n.location.x += pos_x_shift

        # node creation
        # - column -1 -
        pert_uv_n = node_tree.nodes.new("ShaderNodeUVMap")
        pert_uv_n.name = pert_uv_n.label = InteriorLit.PERT_UVMAP_NODE
        pert_uv_n.location = (start_pos_x - pos_x_shift, start_pos_y + 950)
        pert_uv_n.uv_map = _MESH_consts.none_uv

        # - column 0 -
        env_sep_xyz_n = node_tree.nodes.new("ShaderNodeSeparateXYZ")
        env_sep_xyz_n.name = env_sep_xyz_n.label = InteriorLit.ENV_SEP_XYZ_NODE
        env_sep_xyz_n.location = (start_pos_x, start_pos_y + 1800)

        env_check_xyz_n = node_tree.nodes.new("ShaderNodeMath")
        env_check_xyz_n.name = env_check_xyz_n.label = InteriorLit.ENV_CHECK_XYZ_NODE
        env_check_xyz_n.location = (start_pos_x, start_pos_y + 2000)
        env_check_xyz_n.operation = "LESS_THAN"
        env_check_xyz_n.inputs[1].default_value = 1.0

        # - column 1 -
        glass_col_n = node_tree.nodes.new("ShaderNodeRGB")
        glass_col_n.name = glass_col_n.label = InteriorLit.GLASS_COL_NODE
        glass_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 900)

        """
        layer0_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        layer0_tex_n.name = layer0_tex_n.label = InteriorLit.LAYER0_TEX_NODE
        layer0_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 700)
        layer0_tex_n.width = 140

        layer1_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        layer1_tex_n.name = layer1_tex_n.label = InteriorLit.LAYER1_TEX_NODE
        layer1_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 450)
        layer1_tex_n.width = 140

        mask_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mask_tex_n.name = mask_tex_n.label = InteriorLit.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 200)
        mask_tex_n.width = 140

        nmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        nmap_tex_n.name = nmap_tex_n.label = InteriorLit.NMAP_TEX_NODE
        nmap_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y - 50)
        nmap_tex_n.width = 140
        """

        # - column 3 -
        vgcol_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vgcol_mult_n.name = vgcol_mult_n.label = InteriorLit.VGCOLOR_MULT_NODE
        vgcol_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1200)
        vgcol_mult_n.operation = "MULTIPLY"

        # - column 4 -
        glass_col_mix_n = node_tree.nodes.new("ShaderNodeMix")
        glass_col_mix_n.name = glass_col_mix_n.label = InteriorLit.GLASS_COL_MIX_NODE
        glass_col_mix_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1200)
        glass_col_mix_n.data_type = "RGBA"
        glass_col_mix_n.blend_type = "MIX"


        # links creation
        # - column -1 -
        node_tree.links.new(uvmap_n.outputs['UV'], env_sep_xyz_n.inputs['Vector'])

        # - column 0 -
        node_tree.links.new(env_sep_xyz_n.outputs['Y'], env_check_xyz_n.inputs[0])
        node_tree.links.new(env_check_xyz_n.outputs['Value'], add_env_group_n.inputs['Weighted Color'])

        # - column 1 -
        node_tree.links.new(base_tex_n.outputs['Color'], vgcol_mult_n.inputs[0])

        node_tree.links.new(glass_col_n.outputs['Color'], vgcol_mult_n.inputs[1])
        node_tree.links.new(glass_col_n.outputs['Color'], glass_col_mix_n.inputs['B'])

        # - column 3 -
        node_tree.links.new(vgcol_mult_n.outputs['Vector'], glass_col_mix_n.inputs['A'])

        # - column 4 -
        node_tree.links.new(glass_col_mix_n.outputs['Result'], vcol_mult_n.inputs[1])

    ### TEXTURES ###
    @staticmethod
    def set_nmap_texture(node_tree, image):
        """Set nmap texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to nmap texture node
        :type image: bpy.types.Texture
        """

        node_tree.nodes[InteriorLit.NMAP_TEX_NODE].image = image

    @staticmethod
    def set_nmap_texture_settings(node_tree, settings):
        """Set nmap texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[InteriorLit.NMAP_TEX_NODE], settings)
    
    ### ATTRIBUTES ###
    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        bias_scale_window = get_fresnel_window(bias_scale[0], bias_scale[1])

        DifSpecAddEnv.set_fresnel(node_tree, bias_scale_window)
    
    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set unit room dimension for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: TBA
        :type aux_property: bpy.types.IDPropertyGroup
        """
        # NOTE: TBA?
        pass  # NOTE: aux doesn't change anything in rendered material, so pass it

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set atlas dimension for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: TBA
        :type aux_property: bpy.types.IDPropertyGroup
        """
        # NOTE: TBA?
        pass  # NOTE: aux doesn't change anything in rendered material, so pass it

    @staticmethod
    def set_aux2(node_tree, aux_property):
        """Set glass color for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: glass color
        :type aux_property: bpy.types.IDPropertyGroup
        """

        color = (aux_property[0]["value"], aux_property[1]["value"], aux_property[2]["value"], 1.0)
        node_tree.nodes[InteriorLit.GLASS_COL_NODE].outputs["Color"].default_value = color

        factor = aux_property[3]["value"]


        node_tree.nodes[InteriorLit.GLASS_COL_MIX_NODE].inputs['Factor'].default_value = factor
        
    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set luminance boost factor for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: luminosity factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """
        pass  # NOTE: as this variant doesn't use luminance effect we just ignore this factor


    # def made to override base texture settings, because overwriting "extension" in init doesn't work
    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """

        node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE].extension = 'REPEAT'

    @staticmethod
    def set_perturbation_mapping(node_tree, uv_layer):
        """Set Perturbation UV layer to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[InteriorLit.PERT_UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_lit_flavor(node_tree, switch_on):
        """Set lit for the shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        pass
