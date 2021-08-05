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

# Copyright (C) 2015-2021: SCS Software

from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.eut2.dif_anim import anim_blend_factor_ng
from io_scs_tools.internals.shaders.flavors import fadesheet
from io_scs_tools.internals.shaders.flavors import flipsheet
from io_scs_tools.utils import material as _material_utils


class DifAnim(Dif):
    ANIM_SPEED_NODE = "SpeedNode"
    BLEND_FACTOR_NODE = "BlendFactorGNode"
    SEC_UVMAP_NODE = "SecondUVMap"
    OVER_TEX_NODE = "OverTex"
    BASE_OVER_MIX_NODE = "BaseOverMix"
    BASE_OVER_AMIX_NODE = "BaseOverAMix"

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
        opacity_n = node_tree.nodes[Dif.OPACITY_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]

        # move existing
        opacity_n.location.x += pos_x_shift
        opacity_n.location.y -= 200

        # nodes creation
        anim_speed_n = node_tree.nodes.new("ShaderNodeValue")
        anim_speed_n.name = anim_speed_n.label = DifAnim.ANIM_SPEED_NODE
        anim_speed_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1100)

        sec_uvmap_n = node_tree.nodes.new("ShaderNodeUVMap")
        sec_uvmap_n.name = sec_uvmap_n.label = DifAnim.SEC_UVMAP_NODE
        sec_uvmap_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1000)
        sec_uvmap_n.uv_map = _MESH_consts.none_uv

        blend_fac_gn = node_tree.nodes.new("ShaderNodeGroup")
        blend_fac_gn.name = blend_fac_gn.label = DifAnim.BLEND_FACTOR_NODE
        blend_fac_gn.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)
        blend_fac_gn.node_tree = anim_blend_factor_ng.get_node_group()

        over_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        over_tex_n.name = over_tex_n.label = DifAnim.OVER_TEX_NODE
        over_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1000)
        over_tex_n.width = 140

        base_over_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_mix_n.name = base_over_mix_n.label = DifAnim.BASE_OVER_MIX_NODE
        base_over_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        base_over_mix_n.blend_type = "MIX"

        base_over_a_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_over_a_mix_n.name = base_over_a_mix_n.label = DifAnim.BASE_OVER_AMIX_NODE
        base_over_a_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1100)
        base_over_a_mix_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(blend_fac_gn.inputs['Speed'], anim_speed_n.outputs[0])
        node_tree.links.new(over_tex_n.inputs['Vector'], sec_uvmap_n.outputs['UV'])

        # pass 1
        node_tree.links.new(base_over_mix_n.inputs['Fac'], blend_fac_gn.outputs['Factor'])
        node_tree.links.new(base_over_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(base_over_mix_n.inputs['Color2'], over_tex_n.outputs['Color'])

        node_tree.links.new(base_over_a_mix_n.inputs['Fac'], blend_fac_gn.outputs['Factor'])
        node_tree.links.new(base_over_a_mix_n.inputs['Color1'], base_tex_n.outputs['Alpha'])
        node_tree.links.new(base_over_a_mix_n.inputs['Color2'], over_tex_n.outputs['Alpha'])

        # pass 2
        node_tree.links.new(vcol_mult_n.inputs[1], base_over_mix_n.outputs['Color'])

        node_tree.links.new(opacity_n.inputs[0], base_over_a_mix_n.outputs['Color'])

    @staticmethod
    def finalize(node_tree, material):
        """Finalize node tree and material settings. Should be called as last.

        :param node_tree: node tree on which this shader should be finalized
        :type node_tree: bpy.types.NodeTree
        :param material: material used for this shader
        :type material: bpy.types.Material
        """

        Dif.finalize(node_tree, material)

        if fadesheet.is_set(node_tree):
            node_tree.nodes.remove(node_tree.nodes[DifAnim.ANIM_SPEED_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.SEC_UVMAP_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.BLEND_FACTOR_NODE])
        elif flipsheet.is_set(node_tree):
            node_tree.nodes.remove(node_tree.nodes[DifAnim.ANIM_SPEED_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.SEC_UVMAP_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.BLEND_FACTOR_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.OVER_TEX_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.BASE_OVER_MIX_NODE])
            node_tree.nodes.remove(node_tree.nodes[DifAnim.BASE_OVER_AMIX_NODE])

            node_tree.links.new(node_tree.nodes[DifAnim.VCOLOR_MULT_NODE].inputs[1], node_tree.nodes[DifAnim.BASE_TEX_NODE].outputs['Color'])
            node_tree.links.new(node_tree.nodes[DifAnim.OPACITY_NODE].inputs[0], node_tree.nodes[DifAnim.BASE_TEX_NODE].outputs['Alpha'])

    @staticmethod
    def set_base_texture(node_tree, image):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assignet to base texture node
        :type image: bpy.types.Image
        """

        Dif.set_base_texture(node_tree, image)

        if fadesheet.is_set(node_tree):
            node_tree.nodes[DifAnim.OVER_TEX_NODE].image = image

    @staticmethod
    def set_base_texture_settings(node_tree, settings):
        """Set base texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """

        Dif.set_base_texture_settings(node_tree, settings)

        if fadesheet.is_set(node_tree):
            _material_utils.set_texture_settings_to_node(node_tree.nodes[DifAnim.OVER_TEX_NODE], settings)

    @staticmethod
    def set_base_uv(node_tree, uv_layer):
        """Set UV layer to base texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """

        Dif.set_base_uv(node_tree, uv_layer)

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        if fadesheet.is_set(node_tree):
            node_tree.nodes[DifAnim.UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_over_texture(node_tree, image):
        """Set overlying texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to over texture node
        :type image: bpy.types.Image
        """

        # skip it in case fadesheet is set as we use this as over texture is used as second base
        if fadesheet.is_set(node_tree) or flipsheet.is_set(node_tree):
            return

        node_tree.nodes[DifAnim.OVER_TEX_NODE].image = image

    @staticmethod
    def set_over_texture_settings(node_tree, settings):
        """Set over texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """

        # skip it in case fadesheet is set as we use this as over texture is used as second base
        if fadesheet.is_set(node_tree) or flipsheet.is_set(node_tree):
            return

        _material_utils.set_texture_settings_to_node(node_tree.nodes[DifAnim.OVER_TEX_NODE], settings)

    @staticmethod
    def set_over_uv(node_tree, uv_layer):
        """Set UV layer to overlying texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for over texture
        :type uv_layer: str
        """

        # skip it in case fadesheet is set as we use this as over texture is used as second base
        if fadesheet.is_set(node_tree) or flipsheet.is_set(node_tree):
            return

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[DifAnim.SEC_UVMAP_NODE].uv_map = uv_layer

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set playback FPS, frames per row and total frames in case fade/flipsheet flavor is set.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: animation speed represented with one float auxiliary entry
        :type aux_property: bpy.types.IDPropertyGroup
        """

        if fadesheet.is_set(node_tree):
            fadesheet.set_fps(node_tree, aux_property[0]['value'])
            fadesheet.set_frames_row(node_tree, aux_property[1]['value'])
            fadesheet.set_frames_total(node_tree, aux_property[2]['value'])
        elif flipsheet.is_set(node_tree):
            flipsheet.set_fps(node_tree, aux_property[0]['value'])
            flipsheet.set_frames_row(node_tree, aux_property[1]['value'])
            flipsheet.set_frames_total(node_tree, aux_property[2]['value'])
        else:
            node_tree.nodes[DifAnim.ANIM_SPEED_NODE].outputs[0].default_value = aux_property[0]['value']

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set animation speed or frame size in case fade/flipsheet flavor is set.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: animation speed represented with one float auxiliary entry
        :type aux_property: bpy.types.IDPropertyGroup
        """

        if fadesheet.is_set(node_tree):
            fadesheet.set_frame_size(node_tree, aux_property[0]['value'], aux_property[1]['value'])
        elif flipsheet.is_set(node_tree):
            flipsheet.set_frame_size(node_tree, aux_property[0]['value'], aux_property[1]['value'])

    @staticmethod
    def set_fadesheet_flavor(node_tree, switch_on):
        """Set fadesheet flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        uvmap_n = node_tree.nodes[Dif.UVMAP_NODE]
        geom_n = node_tree.nodes[Dif.GEOM_NODE]
        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]
        over_tex_n = node_tree.nodes[DifAnim.OVER_TEX_NODE]
        base_over_mix_n = node_tree.nodes[DifAnim.BASE_OVER_MIX_NODE]
        base_over_amix_n = node_tree.nodes[DifAnim.BASE_OVER_AMIX_NODE]

        if switch_on:

            uvmap_n.location.x -= 185

            location = (geom_n.location.x, geom_n.location.y - 250)
            fadesheet.init(node_tree, location,
                           uvmap_n.outputs['UV'],
                           base_tex_n.inputs[0],
                           over_tex_n.inputs[0],
                           base_over_mix_n.inputs['Fac'],
                           base_over_amix_n.inputs['Fac'])

        else:
            fadesheet.delete(node_tree)

    @staticmethod
    def set_flipsheet_flavor(node_tree, switch_on):
        """Set flipsheet flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        uvmap_n = node_tree.nodes[Dif.UVMAP_NODE]
        geom_n = node_tree.nodes[Dif.GEOM_NODE]
        base_tex_n = node_tree.nodes[Dif.BASE_TEX_NODE]

        if switch_on:

            uvmap_n.location.x -= 185

            location = (geom_n.location.x, geom_n.location.y - 250)
            flipsheet.init(node_tree, location, uvmap_n.outputs['UV'], base_tex_n.inputs[0])

        else:
            flipsheet.delete(node_tree)
