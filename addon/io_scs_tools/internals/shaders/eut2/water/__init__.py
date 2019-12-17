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

import bpy
import math
from io_scs_tools.internals.shaders.eut2.dif import Dif
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv
from io_scs_tools.internals.shaders.eut2.water import mix_factor_ng
from io_scs_tools.internals.shaders.eut2.water import water_stream_ng
from io_scs_tools.internals.shaders.flavors.nmap import scale_ng
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import material as _material_utils


class Water(Dif, StdAddEnv):
    WATER_STREAM_NODE = "WaterStream"
    NEAR_COLOR_NODE = "NearColor"
    HORIZON_COLOR_NODE = "HorizonColor"
    MIX_FACTOR_GNODE = "WaterMixFactor"
    NEAR_MIX_NODE = "NearMix"
    HORIZON_MIX_NODE = "HorizonMix"
    NEAR_HORIZON_ENV_MIX_NODE = "NearHorizonEnvLerpMix"
    NEAR_HORIZON_MIX_NODE = "NearHorizonLerpMix"

    LAYER0_NMAP_UID = "Layer0"
    LAYER1_NMAP_UID = "Layer1"
    LAY0_LAY1_NORMAL_MIX_NODE = "Layer0/Layer1NormalMix"
    LAY0_LAY1_NORMAL_SCRAMBLE_NODE = "Layer0/Layer1NormalScramble"
    NORMAL_NORMALIZE_NODE = "Normalize"

    POSTFIX_STREAM_MIX = "StreamMix"
    POSTFIX_MAPPING_NODE = "Mapping"
    POSTFIX_NMAP_TEX_NODE = "Tex"
    POSTFIX_NMAP_NODE = "NormalMap"
    POSTFIX_NMAP_SCALE_NODE = "NMapScaleGroup"

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

        geom_n = node_tree.nodes[Dif.GEOM_NODE]
        diff_col_n = node_tree.nodes[Dif.DIFF_COL_NODE]
        vcol_mult_n = node_tree.nodes[Dif.VCOLOR_MULT_NODE]
        lighting_eval_n = node_tree.nodes[Dif.LIGHTING_EVAL_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[Dif.OUTPUT_NODE]

        # delete existing
        node_tree.nodes.remove(node_tree.nodes[Dif.BASE_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.OPACITY_NODE])
        node_tree.nodes.remove(node_tree.nodes[Dif.DIFF_MULT_NODE])

        # move existing
        vcol_mult_n.location.y -= 0
        lighting_eval_n.location.x += pos_x_shift * 3
        compose_lighting_n.location.x += pos_x_shift * 3
        output_n.location.x += pos_x_shift * 3

        # nodes creation
        water_stream_n = node_tree.nodes.new("ShaderNodeGroup")
        water_stream_n.name = water_stream_n.label = Water.WATER_STREAM_NODE
        water_stream_n.location = (start_pos_x - pos_x_shift, start_pos_y + 700)
        water_stream_n.node_tree = water_stream_ng.get_node_group()

        mix_factor_n = node_tree.nodes.new("ShaderNodeGroup")
        mix_factor_n.name = mix_factor_n.label = Water.MIX_FACTOR_GNODE
        mix_factor_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)
        mix_factor_n.node_tree = mix_factor_ng.get_node_group()

        near_col_n = node_tree.nodes.new("ShaderNodeRGB")
        near_col_n.label = near_col_n.name = Water.NEAR_COLOR_NODE
        near_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1300)

        horizon_col_n = node_tree.nodes.new("ShaderNodeRGB")
        horizon_col_n.label = horizon_col_n.name = Water.HORIZON_COLOR_NODE
        horizon_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1100)

        near_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        near_mix_n.name = near_mix_n.label = Water.NEAR_MIX_NODE
        near_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1400)
        near_mix_n.operation = "MULTIPLY"

        horizon_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        horizon_mix_n.name = horizon_mix_n.label = Water.HORIZON_MIX_NODE
        horizon_mix_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1200)
        horizon_mix_n.operation = "MULTIPLY"

        lay0_lay1_normal_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        lay0_lay1_normal_mix_n.name = lay0_lay1_normal_mix_n.label = Water.LAY0_LAY1_NORMAL_MIX_NODE
        lay0_lay1_normal_mix_n.location = (start_pos_x + pos_x_shift * 6, start_pos_y + 700)
        lay0_lay1_normal_mix_n.operation = "ADD"

        normal_normalize_n = node_tree.nodes.new("ShaderNodeVectorMath")
        normal_normalize_n.name = normal_normalize_n.label = Water.LAY0_LAY1_NORMAL_MIX_NODE
        normal_normalize_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 700)
        normal_normalize_n.operation = "NORMALIZE"

        near_horizon_env_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        near_horizon_env_mix_n.name = near_horizon_env_mix_n.label = Water.NEAR_HORIZON_ENV_MIX_NODE
        near_horizon_env_mix_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 2100)
        near_horizon_env_mix_n.blend_type = "MIX"
        near_horizon_env_mix_n.inputs['Color2'].default_value = (0.0,) * 4  # far horizon is without env, thus lerp to zero

        near_horizon_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        near_horizon_mix_n.name = near_horizon_mix_n.label = Water.NEAR_HORIZON_MIX_NODE
        near_horizon_mix_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1700)
        near_horizon_mix_n.blend_type = "MIX"

        normal_scramble_n = node_tree.nodes.new("ShaderNodeMixRGB")
        normal_scramble_n.name = normal_scramble_n.label = Water.LAY0_LAY1_NORMAL_SCRAMBLE_NODE
        normal_scramble_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 1200)
        normal_scramble_n.blend_type = "MIX"
        normal_scramble_n.inputs['Color1'].default_value = (0.0, 0.0, 1.0, 0.0)  # WATER_V_NORMAL

        # links creation
        # pass 2
        node_tree.links.new(normal_normalize_n.inputs[0], lay0_lay1_normal_mix_n.outputs[0])
        node_tree.links.new(vcol_mult_n.inputs[1], diff_col_n.outputs['Color'])

        # pass 3
        node_tree.links.new(near_mix_n.inputs[0], vcol_mult_n.outputs[0])
        node_tree.links.new(near_mix_n.inputs[1], near_col_n.outputs['Color'])

        node_tree.links.new(horizon_mix_n.inputs[0], vcol_mult_n.outputs[0])
        node_tree.links.new(horizon_mix_n.inputs[1], horizon_col_n.outputs['Color'])

        node_tree.links.new(normal_scramble_n.inputs['Fac'], mix_factor_n.outputs['Scramble Mix Factor'])
        node_tree.links.new(normal_scramble_n.inputs['Color2'], normal_normalize_n.outputs['Vector'])

        # pass 5
        node_tree.links.new(near_horizon_env_mix_n.inputs['Fac'], mix_factor_n.outputs['Mix Factor'])
        node_tree.links.new(near_horizon_env_mix_n.inputs['Color1'], near_mix_n.outputs[0])

        node_tree.links.new(near_horizon_mix_n.inputs['Fac'], mix_factor_n.outputs['Mix Factor'])
        node_tree.links.new(near_horizon_mix_n.inputs['Color1'], near_mix_n.outputs[0])
        node_tree.links.new(near_horizon_mix_n.inputs['Color2'], horizon_mix_n.outputs[0])

        # pass 6
        node_tree.links.new(lighting_eval_n.inputs['Normal Vector'], normal_scramble_n.outputs['Color'])

        # pass 7
        node_tree.links.new(compose_lighting_n.inputs['Env Color'], near_horizon_env_mix_n.outputs['Color'])
        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], near_horizon_mix_n.outputs['Color'])

        # add environment pass and normal maps
        StdAddEnv.add(node_tree,
                      Dif.GEOM_NODE,
                      node_tree.nodes[Dif.SPEC_COL_NODE].outputs['Color'],
                      None,
                      node_tree.nodes[Water.LIGHTING_EVAL_NODE].outputs['Normal'],
                      node_tree.nodes[Water.NEAR_HORIZON_ENV_MIX_NODE].inputs['Color1'])

        node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE].inputs['Base Texture Alpha'].default_value = 1  # set full reflection strength

        Water.__init_nmap__(node_tree,
                            Water.LAYER0_NMAP_UID,
                            (start_pos_x + pos_x_shift, start_pos_y + 800),
                            geom_n.outputs['Position'],
                            water_stream_n.outputs['Stream0'],
                            geom_n.outputs['Normal'],
                            lay0_lay1_normal_mix_n.inputs[0])

        Water.__init_nmap__(node_tree,
                            Water.LAYER1_NMAP_UID,
                            (start_pos_x + pos_x_shift, start_pos_y + 500),
                            geom_n.outputs['Position'],
                            water_stream_n.outputs['Stream1'],
                            geom_n.outputs['Normal'],
                            lay0_lay1_normal_mix_n.inputs[1])

    @staticmethod
    def __init_nmap__(node_tree, uid, location, position_from, stream_from, normal_from, normal_to):
        """Initialize nodes for normal map for given unique id water layer.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param uid: unique id of water layer to which all nmap nodes will be prefixed
        :type uid: str
        :param location: location where nmap should start creating it's nodes
        :type location: tuple[int, int]
        :param position_from: socket to take position vector from
        :type position_from: bpy.types.NodeSocket
        :param stream_from: socket to take water stream vector from
        :type stream_from: bpy.types.NodeSocket
        :param normal_from: socket from which original normal should be taken
        :type normal_from: bpy.types.NodeSocket
        :param normal_to: socket to which this water layer normal should be put to
        :type normal_to: bpy.types.NodeSocket
        """

        _STREAM_MIX_NODE = uid + Water.POSTFIX_STREAM_MIX
        _MAPPING_NODE = uid + Water.POSTFIX_MAPPING_NODE
        _NMAP_TEX_NODE = uid + Water.POSTFIX_NMAP_TEX_NODE
        _NMAP_NODE = uid + Water.POSTFIX_NMAP_NODE
        _NMAP_SCALE_NODE = uid + Water.POSTFIX_NMAP_SCALE_NODE

        # nodes
        stream_mix_n = node_tree.nodes.new("ShaderNodeVectorMath")
        stream_mix_n.name = stream_mix_n.label = Water.LAY0_LAY1_NORMAL_MIX_NODE
        stream_mix_n.location = location
        stream_mix_n.operation = "ADD"

        vector_mapping_n = node_tree.nodes.new("ShaderNodeMapping")
        vector_mapping_n.name = vector_mapping_n.label = _MAPPING_NODE
        vector_mapping_n.location = (location[0] + 185, location[1])
        vector_mapping_n.vector_type = "POINT"
        vector_mapping_n.inputs['Location'].default_value = vector_mapping_n.inputs['Rotation'].default_value = (0.0,) * 3
        vector_mapping_n.inputs['Scale'].default_value = (1.0,) * 3
        vector_mapping_n.width = 140

        nmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
        nmap_tex_n.name = nmap_tex_n.label = _NMAP_TEX_NODE
        nmap_tex_n.location = (location[0] + 185 * 2, location[1])
        nmap_tex_n.width = 140

        nmap_n = node_tree.nodes.new("ShaderNodeNormalMap")
        nmap_n.name = nmap_n.label = _NMAP_NODE
        nmap_n.location = (location[0] + 185 * 3, location[1] - 150)
        nmap_n.space = "WORLD"
        nmap_n.inputs["Strength"].default_value = 1

        nmap_scale_n = node_tree.nodes.new("ShaderNodeGroup")
        nmap_scale_n.name = nmap_scale_n.label = _NMAP_SCALE_NODE
        nmap_scale_n.location = (location[0] + 185 * 4, location[1])
        nmap_scale_n.node_tree = scale_ng.get_node_group()

        # links
        node_tree.links.new(stream_mix_n.inputs[0], position_from)
        node_tree.links.new(stream_mix_n.inputs[1], stream_from)

        node_tree.links.new(vector_mapping_n.inputs['Vector'], stream_mix_n.outputs['Vector'])

        node_tree.links.new(nmap_tex_n.inputs['Vector'], vector_mapping_n.outputs['Vector'])

        node_tree.links.new(nmap_n.inputs['Color'], nmap_tex_n.outputs['Color'])

        node_tree.links.new(nmap_scale_n.inputs['NMap Tex Color'], nmap_tex_n.outputs['Color'])
        node_tree.links.new(nmap_scale_n.inputs['Original Normal'], normal_from)
        node_tree.links.new(nmap_scale_n.inputs['Modified Normal'], nmap_n.outputs['Normal'])

        node_tree.links.new(normal_to, nmap_scale_n.outputs['Normal'])

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set near distance, far distance and scramble factor.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: near distance, far distance and scramble factor represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        node_tree.nodes[Water.MIX_FACTOR_GNODE].inputs['Near Distance'].default_value = aux_property[0]['value']
        node_tree.nodes[Water.MIX_FACTOR_GNODE].inputs['Far Distance'].default_value = aux_property[1]['value']
        node_tree.nodes[Water.MIX_FACTOR_GNODE].inputs['Scramble Distance'].default_value = aux_property[2]['value']

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

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: yaw, speed, texture scaleX and texture scaleY represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        _LAYER0_NMAP_MAPPING_NODE = Water.LAYER0_NMAP_UID + Water.POSTFIX_MAPPING_NODE

        layer0_mapping_n = node_tree.nodes[_LAYER0_NMAP_MAPPING_NODE]
        layer0_mapping_n.inputs['Scale'].default_value[0] = 1 / aux_property[2]['value']
        layer0_mapping_n.inputs['Scale'].default_value[1] = 1 / aux_property[3]['value']

        yaw = math.radians(aux_property[0]['value'])
        water_stream_n = node_tree.nodes[Water.WATER_STREAM_NODE]
        water_stream_n.inputs['Yaw0'].default_value = (math.sin(yaw), -math.cos(yaw), 0)
        water_stream_n.inputs['Speed0'].default_value = aux_property[1]['value']

    @staticmethod
    def set_aux4(node_tree, aux_property):
        """Set yaw, speed, texture scaleX and texture scaleY for layer1 texture.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: yaw, speed, texture scaleX and texture scaleY represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        _LAYER1_NMAP_MAPPING_NODE = Water.LAYER1_NMAP_UID + Water.POSTFIX_MAPPING_NODE

        layer1_mapping_n = node_tree.nodes[_LAYER1_NMAP_MAPPING_NODE]
        layer1_mapping_n.inputs['Scale'].default_value[0] = 1 / aux_property[2]['value']
        layer1_mapping_n.inputs['Scale'].default_value[1] = 1 / aux_property[3]['value']

        yaw = math.radians(aux_property[0]['value'])
        water_stream_n = node_tree.nodes[Water.WATER_STREAM_NODE]
        water_stream_n.inputs['Yaw1'].default_value = (math.sin(yaw), -math.cos(yaw), 0)
        water_stream_n.inputs['Speed1'].default_value = aux_property[1]['value']

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Enable/disable world space reflections.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: float enabling world space reflections
        :type aux_property: bpy.types.IDPropertyGroup
        """
        pass  # Enabling world space reflections doesn't do anything, thus just pass it.

    @staticmethod
    def set_layer0_texture(node_tree, image):
        """Set texture to layer0 material.

        :param node_tree: node tree
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to layer0 texture node
        :type image: bpy.types.Image
        """

        _LAYER0_MMAP_NODE = Water.LAYER0_NMAP_UID + Water.POSTFIX_NMAP_TEX_NODE

        node_tree.nodes[_LAYER0_MMAP_NODE].image = image

    @staticmethod
    def set_layer0_texture_settings(node_tree, settings):
        """Set layer0 texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """

        _LAYER0_MMAP_NODE = Water.LAYER0_NMAP_UID + Water.POSTFIX_NMAP_TEX_NODE

        _material_utils.set_texture_settings_to_node(node_tree.nodes[_LAYER0_MMAP_NODE], settings)

    @staticmethod
    def set_layer1_texture(node_tree, image):
        """Set texture to layer1 material.

        :param node_tree: node tree
        :type node_tree: bpy.types.NodeTree
        :param image: texture image which should be assigned to layer1 texture node
        :type image: bpy.types.Image
        """

        _LAYER1_MMAP_NODE = Water.LAYER1_NMAP_UID + Water.POSTFIX_NMAP_TEX_NODE

        node_tree.nodes[_LAYER1_MMAP_NODE].image = image

    @staticmethod
    def set_layer1_texture_settings(node_tree, settings):
        """Set layer1 texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """

        _LAYER1_MMAP_NODE = Water.LAYER1_NMAP_UID + Water.POSTFIX_NMAP_TEX_NODE

        _material_utils.set_texture_settings_to_node(node_tree.nodes[_LAYER1_MMAP_NODE], settings)
