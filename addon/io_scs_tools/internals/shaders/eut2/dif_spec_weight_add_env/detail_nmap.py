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

# Copyright (C) 2025-2026: Michaleczeq

import bpy
from ...flavors import nmap
from .....utils import material as _material_utils
from .....consts import Mesh as _MESH_consts


DET_NMAP_UVMAP_NODE = "DetailNMapUVs"
DET_NMAP_TEX_NODE = "DetailNMapTex"
DET_NMAP_COMBINE_NODE = "DetailNMapCombine"


def __create_nodes__(node_tree, location):
    """Create node for detail normal maps.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    """

    frame = node_tree.nodes[nmap.NMAP_FLAVOR_FRAME_NODE]
    nmap_uvs_n = node_tree.nodes[nmap.NMAP_UVMAP_NODE]
    nmap_tex_n = node_tree.nodes[nmap.NMAP_TEX_NODE]
    nmap_dds16_n = node_tree.nodes[nmap.NMAP_DDS16_GNODE]
    nmap_scale_n = node_tree.nodes[nmap.NMAP_SCALE_GNODE]

    # move existing
    nmap_uvs_n.location.x -= 185
    nmap_tex_n.location.x -= 185

    # nodes creation
    det_nmap_uvs_n = node_tree.nodes.new("ShaderNodeUVMap")
    det_nmap_uvs_n.parent = frame
    det_nmap_uvs_n.name = det_nmap_uvs_n.label = DET_NMAP_UVMAP_NODE
    det_nmap_uvs_n.location = (location[0] - 185 * 5, location[1] - 400)
    det_nmap_uvs_n.uv_map = _MESH_consts.none_uv

    det_nmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
    det_nmap_tex_n.parent = frame
    det_nmap_tex_n.name = det_nmap_tex_n.label = DET_NMAP_TEX_NODE
    det_nmap_tex_n.location = (location[0] - 185 * 4, location[1] - 400)
    det_nmap_tex_n.width = 140

    det_nmap_combine_n = node_tree.nodes.new("ShaderNodeMix")
    det_nmap_combine_n.parent = frame
    det_nmap_combine_n.name = det_nmap_combine_n.label = DET_NMAP_COMBINE_NODE
    det_nmap_combine_n.location = (location[0] - 185 * 3, location[1] - 110)
    det_nmap_combine_n.data_type = "RGBA"
    det_nmap_combine_n.blend_type = "OVERLAY"
    det_nmap_combine_n.inputs["Factor"].default_value = 1.0

    # links creation
    node_tree.links.new(nmap_uvs_n.outputs["UV"], det_nmap_tex_n.inputs["Vector"])
    node_tree.links.new(det_nmap_uvs_n.outputs["UV"], nmap_tex_n.inputs["Vector"])

    node_tree.links.new(nmap_tex_n.outputs["Color"], det_nmap_combine_n.inputs["A"])
    node_tree.links.new(det_nmap_tex_n.outputs["Color"], det_nmap_combine_n.inputs["B"])

    node_tree.links.new(det_nmap_combine_n.outputs["Result"], nmap_dds16_n.inputs["Color"])
    node_tree.links.new(det_nmap_combine_n.outputs["Result"], nmap_scale_n.inputs["NMap Tex Color"])


def init(node_tree, location, normal_to, normal_from):
    """Initialize normal map nodes.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location: tuple[int, int]
    :param normal_to: node socket to which result of normal map material should be send
    :type normal_to: bpy.types.NodeSocket
    :param normal_from: node socket from which original mesh normal should be taken
    :type normal_from: bpy.types.NodeSocket
    """

    if nmap.NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        nmap.init(node_tree, location, normal_to, normal_from)
        __create_nodes__(node_tree, location)


def set_detail_texture(node_tree, image):
    """Set texture to normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param image: texture image which should be assignet to nmap texture node
    :type image: bpy.types.Texture
    """

    # save currently active node to properly reset it on the end
    # without reset of active node this material is marked as active which we don't want
    old_active = node_tree.nodes.active

    # ignore empty texture
    if image is None:
        delete(node_tree, True)
        return

    # create material node if not yet created
    if nmap.NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        return

    # assign texture to texture node first
    node_tree.nodes[DET_NMAP_TEX_NODE].image = image

    node_tree.nodes.active = old_active


def set_detail_texture_settings(node_tree, settings):
    """Set detail normal map texture settings to flavor.

    :param node_tree: node tree of current shader
    :type node_tree: bpy.types.NodeTree
    :param settings: binary string of TOBJ settings gotten from tobj import
    :type settings: str
    """
    _material_utils.set_texture_settings_to_node(node_tree.nodes[DET_NMAP_TEX_NODE], settings)

def set_detail_uv(node_tree, uv_layer):
    """Set UV layer to texture in normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param uv_layer: uv layer string used for nmap texture
    :type uv_layer: str
    """

    if uv_layer is None or uv_layer == "":
        uv_layer = _MESH_consts.none_uv

    # set uv layer to texture node and normal map node
    node_tree.nodes[DET_NMAP_UVMAP_NODE].uv_map = uv_layer
    node_tree.nodes[nmap.NMAP_NODE].uv_map = uv_layer


def delete(node_tree, preserve_node=False):
    """Delete normal map nodes from node tree.

    :param node_tree: node tree from which normal map should be deleted
    :type node_tree: bpy.types.NodeTree
    :param preserve_node: if true node won't be deleted
    :type preserve_node: bool
    """

    if DET_NMAP_TEX_NODE in node_tree.nodes and not preserve_node:
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_UVMAP_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[DET_NMAP_COMBINE_NODE])

    nmap.delete(node_tree, preserve_node=preserve_node)
