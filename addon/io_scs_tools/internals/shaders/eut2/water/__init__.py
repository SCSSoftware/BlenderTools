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

import bpy
from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv
from io_scs_tools.internals.shaders.eut2.water import mix_factor_ng
from io_scs_tools.utils import convert as _convert_utils


class Water(Dif, StdAddEnv):
    NEAR_COLOR_NODE = "NearColor"
    HORIZON_COLOR_NODE = "HorizonColor"
    MIX_FACTOR_GNODE = "WaterMixFactor"
    NEAR_MIX_NODE = "NearMix"
    HORIZON_MIX_NODE = "HorizonMix"
    ADD_REFL_MIX_NODE = "AddRefl"
    NEAR_HORIZON_MIX_NODE = "NearHorizonLerpMix"

    LAYER0_MAT_NODE = "Layer0Tex"
    LAYER1_MAT_NODE = "Layer1Tex"
    LAY0_LAY1_NORMAL_MIX_NODE = "Layer0/Layer1NormalMix"
    NORMAL_NORMALIZE_NODE = "Normalize"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        NODE: this is fake representation only to utilize textures

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # init parent
        Dif.init(node_tree)

        diff_col_n = node_tree.nodes[Dif.DIFF_COL_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        out_mat_n = node_tree.nodes[Dif.OUT_MAT_NODE]
        output_n = node_tree.nodes[Dif.OUTPUT_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.BASE_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.DIFF_MULT_NODE])

        # move existing

        vcol_mult_n.location.y -= 0
        out_mat_n.location.x += pos_x_shift * 2
        output_n.location.x += pos_x_shift * 2

        # nodes creation
        mix_factor_gn = node_tree.nodes.new("ShaderNodeGroup")
        mix_factor_gn.name = mix_factor_gn.label = Water.MIX_FACTOR_GNODE
        mix_factor_gn.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)
        mix_factor_gn.node_tree = mix_factor_ng.get_node_group()

        near_col_n = node_tree.nodes.new("ShaderNodeRGB")
        near_col_n.label = near_col_n.name = Water.NEAR_COLOR_NODE
        near_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1300)

        horizon_col_n = node_tree.nodes.new("ShaderNodeRGB")
        horizon_col_n.label = horizon_col_n.name = Water.HORIZON_COLOR_NODE
        horizon_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1100)

        layer0_mat_n = node_tree.nodes.new("ShaderNodeMaterial")
        layer0_mat_n.name = layer0_mat_n.label = Water.LAYER0_MAT_NODE
        layer0_mat_n.location = (start_pos_x + pos_x_shift, start_pos_y + 900)
        layer0_mat_n.use_diffuse = False
        layer0_mat_n.use_specular = False

        layer1_mat_n = node_tree.nodes.new("ShaderNodeMaterial")
        layer1_mat_n.name = layer1_mat_n.label = Water.LAYER1_MAT_NODE
        layer1_mat_n.location = (start_pos_x + pos_x_shift, start_pos_y + 500)
        layer1_mat_n.use_diffuse = False
        layer1_mat_n.use_specular = False

        lay0_lay1_normal_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        lay0_lay1_normal_mix_n.name = lay0_lay1_normal_mix_n.label = Water.LAY0_LAY1_NORMAL_MIX_NODE
        lay0_lay1_normal_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 700)
        lay0_lay1_normal_mix_n.blend_type = "ADD"
        lay0_lay1_normal_mix_n.inputs['Fac'].default_value = 1.0

        normal_normalize_n = node_tree.nodes.new("ShaderNodeVectorMath")
        normal_normalize_n.name = normal_normalize_n.label = Water.LAY0_LAY1_NORMAL_MIX_NODE
        normal_normalize_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 700)
        normal_normalize_n.operation = "NORMALIZE"

        near_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        near_mix_n.name = near_mix_n.label = Water.NEAR_MIX_NODE
        near_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1400)
        near_mix_n.blend_type = "MULTIPLY"
        near_mix_n.inputs['Fac'].default_value = 1.0

        horizon_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        horizon_mix_n.name = horizon_mix_n.label = Water.HORIZON_MIX_NODE
        horizon_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1200)
        horizon_mix_n.blend_type = "MULTIPLY"
        horizon_mix_n.inputs['Fac'].default_value = 1.0

        add_refl_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        add_refl_mix_n.name = add_refl_mix_n.label = Water.ADD_REFL_MIX_NODE
        add_refl_mix_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 2000)
        add_refl_mix_n.blend_type = "ADD"
        add_refl_mix_n.inputs['Fac'].default_value = 1.0

        near_horizon_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        near_horizon_mix_n.name = near_horizon_mix_n.label = Water.NEAR_HORIZON_MIX_NODE
        near_horizon_mix_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1700)
        near_horizon_mix_n.blend_type = "MIX"

        # add environment pass and normal maps
        StdAddEnv.add(node_tree,
                      Dif.GEOM_NODE,
                      Dif.SPEC_COL_NODE,
                      "",
                      Water.NEAR_MIX_NODE,
                      Water.ADD_REFL_MIX_NODE,
                      "Color1")

        # links creation
        # pass 1
        node_tree.links.new(lay0_lay1_normal_mix_n.inputs['Color1'], layer0_mat_n.outputs['Normal'])
        node_tree.links.new(lay0_lay1_normal_mix_n.inputs['Color2'], layer1_mat_n.outputs['Normal'])

        # pass 2
        node_tree.links.new(normal_normalize_n.inputs[0], lay0_lay1_normal_mix_n.outputs['Color'])
        node_tree.links.new(vcol_mult_n.inputs['Color2'], diff_col_n.outputs['Color'])

        # pass 3
        node_tree.links.new(near_mix_n.inputs['Color1'], vcol_mult_n.outputs['Color'])
        node_tree.links.new(near_mix_n.inputs['Color2'], near_col_n.outputs['Color'])

        node_tree.links.new(horizon_mix_n.inputs['Color1'], vcol_mult_n.outputs['Color'])
        node_tree.links.new(horizon_mix_n.inputs['Color2'], horizon_col_n.outputs['Color'])

        # pass 4
        node_tree.links.new(add_refl_mix_n.inputs['Color2'], near_mix_n.outputs['Color'])

        # pass 5
        node_tree.links.new(near_horizon_mix_n.inputs['Fac'], mix_factor_gn.outputs['Mix Factor'])
        node_tree.links.new(near_horizon_mix_n.inputs['Color1'], add_refl_mix_n.outputs['Color'])
        node_tree.links.new(near_horizon_mix_n.inputs['Color2'], horizon_mix_n.outputs['Color'])

        # material pass
        node_tree.links.new(out_mat_n.inputs['Color'], near_horizon_mix_n.outputs['Color'])
        node_tree.links.new(out_mat_n.inputs['Normal'], normal_normalize_n.outputs['Vector'])

        # output pass
        node_tree.links.new(output_n.inputs['Color'], out_mat_n.outputs['Color'])

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set near distance, far distance and scramble factor.

        NOTE: scramble factor is not implemented

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: near distance, far distance and scramble factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Water.MIX_FACTOR_GNODE].inputs['Near Distance'].default_value = aux_property[0]['value']
        node_tree.nodes[Water.MIX_FACTOR_GNODE].inputs['Far Distance'].default_value = aux_property[1]['value']

    @staticmethod
    def set_aux1(node_tree, aux_property):
        """Set near color.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: near color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Water.NEAR_COLOR_NODE].outputs[0].default_value = _convert_utils.aux_to_node_color(aux_property)

    @staticmethod
    def set_aux2(node_tree, aux_property):
        """Set horizon color.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: horizon color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Water.HORIZON_COLOR_NODE].outputs[0].default_value = _convert_utils.aux_to_node_color(aux_property)

    @staticmethod
    def set_aux3(node_tree, aux_property):
        """Set yaw, speed, texture scaleX and texture scaleY for layer0 texture.

        NOTE: yaw and speed are not implemented

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: yaw, speed, texture scaleX and texture scaleY represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        layer0_mat_n = node_tree.nodes[Water.LAYER0_MAT_NODE]

        # if there is no normal map material for layer0 yet
        # force set of None texture so material will be created
        if not layer0_mat_n.material:
            Water.__set_texture__(node_tree, Water.LAYER0_MAT_NODE, None)

        layer0_mat_n.material.texture_slots[0].scale.x = 1 / aux_property[2]['value']
        layer0_mat_n.material.texture_slots[0].scale.y = 1 / aux_property[3]['value']

    @staticmethod
    def set_aux4(node_tree, aux_property):
        """Set yaw, speed, texture scaleX and texture scaleY for layer1 texture.

        NOTE: yaw and speed are not implemented

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: yaw, speed, texture scaleX and texture scaleY represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        layer1_mat_n = node_tree.nodes[Water.LAYER1_MAT_NODE]

        # if there is no normal map material for layer0 yet
        # force set of None texture so material will be created
        if not layer1_mat_n.material:
            Water.__set_texture__(node_tree, Water.LAYER1_MAT_NODE, None)

        layer1_mat_n.material.texture_slots[0].scale.x = 1 / aux_property[2]['value']
        layer1_mat_n.material.texture_slots[0].scale.y = 1 / aux_property[3]['value']

    @staticmethod
    def __set_texture__(node_tree, layer_mat_node_name, texture):
        """Set texture to layer material.

        :param node_tree: node tree
        :type node_tree: bpy.types.NodeTree
        :param layer_mat_node_name: name of the layer to set texture to
        :type layer_mat_node_name: str
        :param texture: texture which should be assigned to layer0 texture node
        :type texture: bpy.types.Texture | None
        """

        # save currently active node to properly reset it on the end
        # without reset of active node this material is marked as active which we don't want
        old_active = node_tree.nodes.active

        # search possible existing materials and use it
        material = None
        i = 1
        while ".scs_nmap_" + str(i) in bpy.data.materials:

            curr_mat = bpy.data.materials[".scs_nmap_" + str(i)]

            # grab only material without any users and clear all texture slots
            if curr_mat.users == 0:
                material = curr_mat

                for i in range(0, len(material.texture_slots)):
                    material.texture_slots.clear(i)

            i += 1

        # if none is found create new one
        if not material:
            material = bpy.data.materials.new(".scs_nmap_" + str(i))

        # finally set texture and it's properties to material
        tex_slot = material.texture_slots.add()
        tex_slot.texture_coords = "GLOBAL"
        tex_slot.use_map_color_diffuse = False
        tex_slot.use_map_normal = True
        tex_slot.texture = texture
        tex_slot.normal_map_space = "TANGENT"

        node_tree.nodes[layer_mat_node_name].material = material

        # trigger set methods for auxiliary items, just to make sure any previously set aux values don't get lost
        # during material creation in this method
        if layer_mat_node_name == Water.LAYER0_MAT_NODE:
            Water.set_aux3(node_tree, node_tree.nodes[Dif.OUT_MAT_NODE].material.scs_props.shader_attribute_aux3)
        elif layer_mat_node_name == Water.LAYER1_MAT_NODE:
            Water.set_aux4(node_tree, node_tree.nodes[Dif.OUT_MAT_NODE].material.scs_props.shader_attribute_aux4)

        node_tree.nodes.active = old_active

    @staticmethod
    def set_layer0_texture(node_tree, texture):
        """Set texture to layer0 material.

        :param node_tree: node tree
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to layer0 texture node
        :type texture: bpy.types.Texture
        """
        Water.__set_texture__(node_tree, Water.LAYER0_MAT_NODE, texture)

    @staticmethod
    def set_layer1_texture(node_tree, texture):
        """Set texture to layer1 material.

        :param node_tree: node tree
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to layer1 texture node
        :type texture: bpy.types.Texture
        """
        Water.__set_texture__(node_tree, Water.LAYER1_MAT_NODE, texture)
