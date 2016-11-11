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
from io_scs_tools.internals.shaders.flavors import nmap

DET_NMAP_NODE = "DetailNormalMapMat"
DET_NMAP_TEX_NODE = "DetailNMapTex"
DET_NMAP_SCALE_GNODE = "DetailNMapScaleGroup"
DET_NMAP_UV_SCALE_NODE = "DetailNMapUVScale"
DET_NMAP_STRENGTH_NODE = "DetailNMapStrength"
DET_NMAP_MIX_NODE = "DetailNMapMix"
DET_NMAP_SEPARATE_NODE = "SeparateBaseNMap"
NMAP_SEPARATE_NODE = "SeparateBaseNMap"
NMAP_DET_NMAP_COMBINE_NODE = "CombineNMap&DetailNMap"
NMAP_NORMALIZE_NODE = "NormalizeNMapNormal"


def __create_nodes__(node_tree, location, uv_scale_from, det_nmap_strength_from, normal_to):
    """Create node for detail normal maps.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    """

    frame = node_tree.nodes[nmap.NMAP_FLAVOR_FRAME_NODE]
    nmap_geom_n = node_tree.nodes[nmap.NMAP_GEOM_NODE]

    # move existing
    nmap_geom_n.location.y -= 300

    # nodes creation
    det_nmap_uv_scale_n = node_tree.nodes.new("ShaderNodeMixRGB")
    det_nmap_uv_scale_n.parent = frame
    det_nmap_uv_scale_n.name = det_nmap_uv_scale_n.label = DET_NMAP_UV_SCALE_NODE
    det_nmap_uv_scale_n.location = (location[0] - 185 * 2, location[1] - 700)
    det_nmap_uv_scale_n.blend_type = "MULTIPLY"
    det_nmap_uv_scale_n.inputs['Fac'].default_value = 1.0

    det_nmap_tex_n = node_tree.nodes.new("ShaderNodeTexture")
    det_nmap_tex_n.parent = frame
    det_nmap_tex_n.name = det_nmap_tex_n.label = DET_NMAP_TEX_NODE
    det_nmap_tex_n.location = (location[0] - 185, location[1] - 600)

    det_nmap_n = node_tree.nodes.new("ShaderNodeNormalMap")
    det_nmap_n.parent = frame
    det_nmap_n.name = det_nmap_n.label = DET_NMAP_NODE
    det_nmap_n.location = (location[0], location[1] - 800)
    det_nmap_n.space = "TANGENT"
    det_nmap_n.inputs["Strength"].default_value = 1

    det_nmap_scale_gn = node_tree.nodes.new("ShaderNodeGroup")
    det_nmap_scale_gn.parent = frame
    det_nmap_scale_gn.name = det_nmap_scale_gn.label = DET_NMAP_SCALE_GNODE
    det_nmap_scale_gn.location = (location[0] + 185, location[1] - 600)
    det_nmap_scale_gn.node_tree = nmap.scale_ng.get_node_group()

    det_nmap_strength_n = node_tree.nodes.new("ShaderNodeMixRGB")
    det_nmap_strength_n.parent = frame
    det_nmap_strength_n.name = det_nmap_strength_n.label = DET_NMAP_STRENGTH_NODE
    det_nmap_strength_n.location = (location[0] + 185 * 2, location[1] - 450)
    det_nmap_strength_n.blend_type = "MULTIPLY"
    det_nmap_strength_n.inputs['Fac'].default_value = 1.0

    det_nmap_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
    det_nmap_mix_n.parent = frame
    det_nmap_mix_n.name = det_nmap_mix_n.label = DET_NMAP_STRENGTH_NODE
    det_nmap_mix_n.location = (location[0] + 185 * 3, location[1] - 300)
    det_nmap_mix_n.blend_type = "ADD"
    det_nmap_mix_n.inputs['Fac'].default_value = 1.0

    det_nmap_sep_n = node_tree.nodes.new("ShaderNodeSeparateRGB")
    det_nmap_sep_n.parent = frame
    det_nmap_sep_n.name = det_nmap_sep_n.label = DET_NMAP_SEPARATE_NODE
    det_nmap_sep_n.location = (location[0] + 185 * 4, location[1] - 300)

    nmap_sep_n = node_tree.nodes.new("ShaderNodeSeparateRGB")
    nmap_sep_n.parent = frame
    nmap_sep_n.name = nmap_sep_n.label = NMAP_SEPARATE_NODE
    nmap_sep_n.location = (location[0] + 185 * 4, location[1] - 450)

    nmap_det_nmap_combine_n = node_tree.nodes.new("ShaderNodeCombineRGB")
    nmap_det_nmap_combine_n.parent = frame
    nmap_det_nmap_combine_n.name = nmap_det_nmap_combine_n.label = NMAP_SEPARATE_NODE
    nmap_det_nmap_combine_n.location = (location[0] + 185 * 5, location[1] - 350)

    nmap_normalize_n = node_tree.nodes.new("ShaderNodeVectorMath")
    nmap_normalize_n.parent = frame
    nmap_normalize_n.name = nmap_normalize_n.label = NMAP_SEPARATE_NODE
    nmap_normalize_n.location = (location[0] + 185 * 6, location[1] - 350)
    nmap_normalize_n.operation = "NORMALIZE"

    # links creation
    nodes = node_tree.nodes

    # pass 1
    node_tree.links.new(det_nmap_uv_scale_n.inputs['Color1'], nodes[nmap.NMAP_GEOM_NODE].outputs['UV'])
    node_tree.links.new(det_nmap_uv_scale_n.inputs['Color2'], uv_scale_from)

    # pass 2
    node_tree.links.new(det_nmap_tex_n.inputs['Vector'], det_nmap_uv_scale_n.outputs['Color'])

    # pass 3
    node_tree.links.new(det_nmap_n.inputs['Color'], det_nmap_tex_n.outputs['Color'])

    # pass 4
    node_tree.links.new(det_nmap_scale_gn.inputs['NMap Tex Color'], det_nmap_tex_n.outputs['Color'])
    node_tree.links.new(det_nmap_scale_gn.inputs['Original Normal'], nodes[nmap.NMAP_GEOM_NODE].outputs['Normal'])
    node_tree.links.new(det_nmap_scale_gn.inputs['Modified Normal'], det_nmap_n.outputs['Normal'])

    # pass 5
    node_tree.links.new(det_nmap_strength_n.inputs['Color1'], det_nmap_strength_from)
    node_tree.links.new(det_nmap_strength_n.inputs['Color2'], det_nmap_scale_gn.outputs['Normal'])

    # pass 6
    node_tree.links.new(det_nmap_mix_n.inputs['Color1'], nodes[nmap.NMAP_SCALE_GNODE].outputs['Normal'])
    node_tree.links.new(det_nmap_mix_n.inputs['Color2'], det_nmap_strength_n.outputs['Color'])

    # pass 7
    node_tree.links.new(det_nmap_sep_n.inputs['Image'], det_nmap_mix_n.outputs['Color'])

    node_tree.links.new(nmap_sep_n.inputs['Image'], nodes[nmap.NMAP_SCALE_GNODE].outputs['Normal'])

    # pass 8
    node_tree.links.new(nmap_det_nmap_combine_n.inputs['R'], det_nmap_sep_n.outputs['R'])
    node_tree.links.new(nmap_det_nmap_combine_n.inputs['G'], det_nmap_sep_n.outputs['G'])
    node_tree.links.new(nmap_det_nmap_combine_n.inputs['B'], nmap_sep_n.outputs['B'])

    # pass 9
    node_tree.links.new(nmap_normalize_n.inputs[0], nmap_det_nmap_combine_n.outputs['Image'])

    node_tree.links.new(normal_to, nmap_normalize_n.outputs['Vector'])


def init(node_tree, location, uv_scale_from, det_nmap_strength_from, normal_to):
    """Initialize normal map nodes.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location: tuple[int, int]
    :param uv_scale_from: node socket from which UV scale factor should be taken
    :type uv_scale_from: bpy.types.NodeSocket
    :param det_nmap_strength_from: node socket from which detail normal map strength should be taken
    :type det_nmap_strength_from: bpy.types.NodeSocket
    :param normal_to: node socket to which result of normal map material should be send
    :type normal_to: bpy.types.NodeSocket
    """

    if nmap.NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        nmap.init(node_tree, location, normal_to)
        __create_nodes__(node_tree, location, uv_scale_from, det_nmap_strength_from, normal_to)


def set_texture(node_tree, texture):
    """Set texture to normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param texture: texture which should be assignet to nmap texture node
    :type texture: bpy.types.Texture
    """
    nmap.set_texture(node_tree, texture)


def set_detail_texture(node_tree, texture):
    """Set texture to normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param texture: texture which should be assignet to nmap texture node
    :type texture: bpy.types.Texture
    """

    # save currently active node to properly reset it on the end
    # without reset of active node this material is marked as active which we don't want
    old_active = node_tree.nodes.active

    # ignore empty texture
    if texture is None:
        delete(node_tree, True)
        return

    # create material node if not yet created
    if nmap.NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        return

    # assign texture to texture node first
    node_tree.nodes[DET_NMAP_TEX_NODE].texture = texture

    node_tree.nodes.active = old_active


def set_uv(node_tree, uv_layer):
    """Set UV layer to texture in normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param uv_layer: uv layer string used for nmap texture
    :type uv_layer: str
    """
    nmap.set_uv(node_tree, uv_layer)
    node_tree.nodes[DET_NMAP_NODE].uv_map = uv_layer


def set_detail_uv(node_tree, uv_layer):
    """Set UV layer to texture in normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param uv_layer: uv layer string used for nmap texture
    :type uv_layer: str
    """

    nmap.set_uv(node_tree, uv_layer)  # NOTE : no support for extra uv on detail texture in shaders


def delete(node_tree, preserve_node=False):
    """Delete normal map nodes from node tree.

    :param node_tree: node tree from which normal map should be deleted
    :type node_tree: bpy.types.NodeTree
    :param preserve_node: if true node won't be deleted
    :type preserve_node: bool
    """

    if DET_NMAP_NODE in node_tree.nodes and not preserve_node:
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_UV_SCALE_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_SCALE_GNODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_STRENGTH_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_MIX_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_SEPARATE_NODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_SEPARATE_NODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_DET_NMAP_COMBINE_NODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_NORMALIZE_NODE])

    nmap.delete(node_tree, preserve_node=preserve_node)
