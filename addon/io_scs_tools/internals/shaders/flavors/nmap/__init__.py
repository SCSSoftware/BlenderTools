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
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.flavors.nmap import scale_ng
from io_scs_tools.internals.shaders.flavors.nmap import dds16_ng
from io_scs_tools.utils import material as _material_utils

NMAP_FLAVOR_FRAME_NODE = "TSNMap Flavor"
NMAP_UVMAP_NODE = "NormalMapUVs"
NMAP_NODE = "NormalMap"
NMAP_TEX_NODE = "NMapTex"
NMAP_DDS16_GNODE = "NMapDDS16Group"
NMAP_SCALE_GNODE = "NMapScaleGroup"


def __create_nodes__(node_tree, location=None, normal_to=None, normal_from=None):
    """Create node for normal maps.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    """

    # try to recover location
    if not location:
        if NMAP_NODE in node_tree.nodes:
            location = node_tree.nodes[NMAP_NODE].location

    # try to recover normals to link node socket
    if not normal_to and NMAP_NODE in node_tree.nodes:
        for link in node_tree.links:
            if link.from_node == node_tree.nodes[NMAP_NODE] and link.from_socket.name == "Normal":
                normal_to = link.to_socket

    if not normal_from and NMAP_SCALE_GNODE in node_tree.nodes:
        for link in node_tree.links:
            if link.to_node == node_tree.nodes[NMAP_SCALE_GNODE] and link.to_socket.name == "Original Normal":
                normal_from = link.from_socket

    frame = node_tree.nodes.new("NodeFrame")
    frame.name = frame.label = NMAP_FLAVOR_FRAME_NODE

    nmap_uvs_n = node_tree.nodes.new("ShaderNodeUVMap")
    nmap_uvs_n.parent = frame
    nmap_uvs_n.name = nmap_uvs_n.label = NMAP_UVMAP_NODE
    nmap_uvs_n.uv_map = _MESH_consts.none_uv

    nmap_tex_n = node_tree.nodes.new("ShaderNodeTexImage")
    nmap_tex_n.parent = frame
    nmap_tex_n.name = nmap_tex_n.label = NMAP_TEX_NODE
    nmap_tex_n.width = 140

    nmap_n = node_tree.nodes.new("ShaderNodeNormalMap")
    nmap_n.parent = frame
    nmap_n.name = nmap_n.label = NMAP_NODE
    nmap_n.space = "TANGENT"
    nmap_n.inputs["Strength"].default_value = 1

    nmap_scale_n = node_tree.nodes.new("ShaderNodeGroup")
    nmap_scale_n.parent = frame
    nmap_scale_n.name = nmap_scale_n.label = NMAP_SCALE_GNODE
    nmap_scale_n.node_tree = scale_ng.get_node_group()

    # position nodes
    if location:
        nmap_uvs_n.location = (location[0] - 185 * 3, location[1])
        nmap_tex_n.location = (location[0] - 185 * 2, location[1])
        nmap_n.location = (location[0] - 185, location[1] - 200)
        nmap_scale_n.location = (location[0], location[1])

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(nodes[NMAP_UVMAP_NODE].outputs["UV"], nodes[NMAP_TEX_NODE].inputs["Vector"])

    node_tree.links.new(nodes[NMAP_NODE].inputs["Color"], nodes[NMAP_TEX_NODE].outputs["Color"])

    node_tree.links.new(nodes[NMAP_SCALE_GNODE].inputs["NMap Tex Color"], nodes[NMAP_TEX_NODE].outputs["Color"])
    if normal_from:
        node_tree.links.new(nodes[NMAP_SCALE_GNODE].inputs["Original Normal"], normal_from)
    node_tree.links.new(nodes[NMAP_SCALE_GNODE].inputs["Modified Normal"], nodes[NMAP_NODE].outputs["Normal"])

    # set normal only if we know where to
    if normal_to:
        node_tree.links.new(normal_to, nodes[NMAP_SCALE_GNODE].outputs["Normal"])


def __check_and_create_dds16_node__(node_tree, image):
    """Checks if given texture is composed '16-bit DDS' texture and properly create extra node for it's representation.
    On the contrary if texture is not 16-bit DDS and node exists clean that node and restore old connections.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    :param image: texture image which should be assigned to nmap texture node
    :type image: bpy.types.Image
    """

    # in case of DDS simulating 16-bit normal maps create it's group and properly connect it,
    # on the other hand if group exists but shouldn't delete group and restore old connections

    is_dds16 = image and image.filepath.endswith(".dds") and image.pixels[2] == 0.0
    if is_dds16 and NMAP_DDS16_GNODE not in node_tree.nodes:

        nmap_dds16_n = node_tree.nodes.new("ShaderNodeGroup")
        nmap_dds16_n.parent = node_tree.nodes[NMAP_FLAVOR_FRAME_NODE]
        nmap_dds16_n.name = nmap_dds16_n.label = NMAP_DDS16_GNODE
        nmap_dds16_n.node_tree = dds16_ng.get_node_group()

        location = node_tree.nodes[NMAP_NODE].location

        node_tree.nodes[NMAP_TEX_NODE].location[0] -= 185
        node_tree.nodes[NMAP_UVMAP_NODE].location[0] -= 185
        nmap_dds16_n.location = (location[0] - 185, location[1])

        node_tree.links.new(node_tree.nodes[NMAP_DDS16_GNODE].inputs["Color"], node_tree.nodes[NMAP_TEX_NODE].outputs["Color"])

        node_tree.links.new(node_tree.nodes[NMAP_NODE].inputs["Strength"], node_tree.nodes[NMAP_DDS16_GNODE].outputs["Strength"])
        node_tree.links.new(node_tree.nodes[NMAP_NODE].inputs["Color"], node_tree.nodes[NMAP_DDS16_GNODE].outputs["Color"])

    elif not is_dds16 and NMAP_DDS16_GNODE in node_tree.nodes:

        node_tree.nodes.remove(node_tree.nodes[NMAP_DDS16_GNODE])

        node_tree.nodes[NMAP_TEX_NODE].location[0] += 185
        node_tree.nodes[NMAP_UVMAP_NODE].location[0] += 185

        node_tree.links.new(node_tree.nodes[NMAP_NODE].inputs["Color"], node_tree.nodes[NMAP_TEX_NODE].outputs["Color"])


def init(node_tree, location, normal_to, normal_from):
    """Initialize normal map nodes.

    :param node_tree: node tree on which normal map will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location (int, int)
    :param normal_to: node socket to which result of final commbined normal should be send
    :type normal_to: bpy.types.NodeSocket
    :param normal_from: node socket from which original mesh normal should be taken
    :type normal_from: bpy.types.NodeSocket
    """

    if NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        __create_nodes__(node_tree, location, normal_to=normal_to, normal_from=normal_from)


def set_texture(node_tree, image):
    """Set texture to normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param image: texture image which should be assignet to nmap texture node
    :type image: bpy.types.Image
    """

    # save currently active node to properly reset it on the end
    # without reset of active node this material is marked as active which we don't want
    old_active = node_tree.nodes.active

    # ignore empty texture
    if image is None:
        delete(node_tree, True)
        return

    # create material node if not yet created
    if NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        __create_nodes__(node_tree)

    # in case of DDS simulating 16-bit normal maps create it's group and properly connect it
    __check_and_create_dds16_node__(node_tree, image)

    # assign texture to texture node first
    node_tree.nodes[NMAP_TEX_NODE].image = image

    node_tree.nodes.active = old_active


def set_texture_settings(node_tree, settings):
    """Set texture settings to normal map flavor.

    :param node_tree: node tree of current shader
    :type node_tree: bpy.types.NodeTree
    :param settings: binary string of TOBJ settings gotten from tobj import
    :type settings: str
    """
    _material_utils.set_texture_settings_to_node(node_tree.nodes[NMAP_TEX_NODE], settings)


def set_uv(node_tree, uv_layer):
    """Set UV layer to texture in normal map flavor.

    :param node_tree: node tree on which normal map is used
    :type node_tree: bpy.types.NodeTree
    :param uv_layer: uv layer string used for nmap texture
    :type uv_layer: str
    """

    if uv_layer is None or uv_layer == "":
        uv_layer = _MESH_consts.none_uv

    # create material node if not yet created
    if NMAP_FLAVOR_FRAME_NODE not in node_tree.nodes:
        __create_nodes__(node_tree)

    # set uv layer to texture node and normal map node
    node_tree.nodes[NMAP_UVMAP_NODE].uv_map = uv_layer
    node_tree.nodes[NMAP_NODE].uv_map = uv_layer


def delete(node_tree, preserve_node=False):
    """Delete normal map nodes from node tree.

    :param node_tree: node tree from which normal map should be deleted
    :type node_tree: bpy.types.NodeTree
    :param preserve_node: if true node won't be deleted
    :type preserve_node: bool
    """

    if NMAP_NODE in node_tree.nodes and not preserve_node:
        node_tree.nodes.remove(node_tree.nodes[NMAP_TEX_NODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_NODE])
        if NMAP_DDS16_GNODE in node_tree.nodes:
            node_tree.nodes.remove(node_tree.nodes[NMAP_DDS16_GNODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_SCALE_GNODE])
        node_tree.nodes.remove(node_tree.nodes[NMAP_FLAVOR_FRAME_NODE])
