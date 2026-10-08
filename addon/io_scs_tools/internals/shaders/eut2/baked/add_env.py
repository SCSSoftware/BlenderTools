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

from .spec import BakedSpec
from ..parameters import get_fresnel_truckpaint
# from ..std_node_groups import linear_to_srgb_ng
from ..std_passes.add_env import StdAddEnv
from .....utils import convert as _convert_utils
from .....utils import material as _material_utils
from .....utils import get_scs_globals as _get_scs_globals

class BakedSpecAddEnv(BakedSpec, StdAddEnv):
    MASK_TEX_NODE = "MaskTex"
    MASK1_TEX_NODE = "Mask1Tex"

    BASE_PAINT_MULT_NODE = "BasePaintMult"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        BakedSpec.init(node_tree)

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
        BakedSpec.init(node_tree)

        
        StdAddEnv.add(node_tree,
                      BakedSpec.GEOM_NODE,
                      None,
                      None,
                      node_tree.nodes[BakedSpec.LIGHTING_EVAL_NODE].outputs['Normal'],
                      node_tree.nodes[BakedSpec.COMPOSE_LIGHTING_NODE].inputs['Env Color'])

        uvmap_n = node_tree.nodes[BakedSpec.UVMAP_NODE]

        add_env_gn = node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE]

        # overrides
        # set strength multiplier to 2 for better visualization in Blender
        node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE].inputs['Strength Multiplier'].default_value = 2.0

        # node creation
        mask_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        mask_tex_n.name = mask_tex_n.label = BakedSpecAddEnv.MASK_TEX_NODE
        mask_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)
        mask_tex_n.width = 140

        # links creation
        node_tree.links.new(uvmap_n.outputs['UV'], mask_tex_n.inputs['Vector'])

        node_tree.links.new(mask_tex_n.outputs['Color'], add_env_gn.inputs['Env Factor Color'])

    @staticmethod
    def init_paint(node_tree):
        """Initialize extended node tree for colormask or airbrush flavors with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # make sure to skip execution if node exists
        if BakedSpecAddEnv.MASK1_TEX_NODE not in node_tree.nodes:

            uvmap_n = node_tree.nodes[BakedSpec.UVMAP_NODE]
            vcol_mult_n = node_tree.nodes[BakedSpec.VCOLOR_MULT_NODE]
            compose_lighting_n = node_tree.nodes[BakedSpec.COMPOSE_LIGHTING_NODE]

            # node creation
            mask1_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
            mask1_tex_n.name = mask1_tex_n.label = BakedSpecAddEnv.MASK1_TEX_NODE
            mask1_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1150)
            mask1_tex_n.width = 140

            base_paint_mult_n = node_tree.nodes.new("ShaderNodeMix")
            base_paint_mult_n.name = base_paint_mult_n.label = BakedSpecAddEnv.BASE_PAINT_MULT_NODE
            base_paint_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1500)
            base_paint_mult_n.data_type = "RGBA"
            base_paint_mult_n.blend_type = "MULTIPLY"
            base_paint_mult_n.inputs['Factor'].default_value = 1
            base_paint_mult_n.inputs['B'].default_value = _convert_utils.to_node_color(_get_scs_globals().base_paint_color)

            # links creation
            node_tree.links.new(uvmap_n.outputs['UV'], mask1_tex_n.inputs['Vector'])
            node_tree.links.new(mask1_tex_n.outputs['Color'], base_paint_mult_n.inputs['Factor'])
            node_tree.links.new(vcol_mult_n.outputs['Vector'], base_paint_mult_n.inputs['A'])
            node_tree.links.new(base_paint_mult_n.outputs['Result'], compose_lighting_n.inputs['Diffuse Color'])


    @staticmethod
    def set_mask_texture(node_tree, image):
        """Set mask texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to mask texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[BakedSpecAddEnv.MASK_TEX_NODE].image = image

    @staticmethod
    def set_mask_texture_settings(node_tree, settings):
        """Set mask texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[BakedSpecAddEnv.MASK_TEX_NODE], settings)

    @staticmethod
    def set_mask_uv(node_tree, uv_layer):
        """Set UV layer to mask texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mask texture
        :type uv_layer: str
        """

        BakedSpec.set_base_uv(node_tree, uv_layer)

    @staticmethod
    def set_mask_1_texture(node_tree, image):
        """Set mask 1 texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to mask 1 texture node
        :type image: bpy.types.Image
        """

        node_tree.nodes[BakedSpecAddEnv.MASK1_TEX_NODE].image = image

    @staticmethod
    def set_mask_1_texture_settings(node_tree, settings):
        """Set mask 1 texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        _material_utils.set_texture_settings_to_node(node_tree.nodes[BakedSpecAddEnv.MASK1_TEX_NODE], settings)

    @staticmethod
    def set_mask_1_uv(node_tree, uv_layer):
        """Set UV layer to mask 1 texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for mask 1 texture
        :type uv_layer: str
        """

        BakedSpec.set_base_uv(node_tree, uv_layer)

    @staticmethod
    def set_paint_flavor(node_tree, switch_on):
        """Set paint flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """
        
        if switch_on:
            BakedSpecAddEnv.init_paint(node_tree)

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.
        More tests are needed to determine if this is correct for paint flavor in baked shader, because without that, model is too glossy.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """
        # skip ecxecution if node for "paint" flavor does not exist
        if BakedSpecAddEnv.MASK1_TEX_NODE not in node_tree.nodes:
            return

        bias_scale_truckpaint = get_fresnel_truckpaint(bias_scale[0], bias_scale[1])
        StdAddEnv.set_fresnel(node_tree, bias_scale_truckpaint)

        node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Type'].default_value = 1

        