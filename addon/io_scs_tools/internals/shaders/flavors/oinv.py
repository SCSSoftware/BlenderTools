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

# Copyright (C) 2025: SCS Software

FLAVOR_ID = "oinv"
INV_OPAC_NODE = "InvertOpacity"


def __create_node__(node_tree):
    """Create node for oinv node.

    :param node_tree: node tree on which oinv flavor will be used
    :type node_tree: bpy.types.NodeTree
    """
    inv_opac_n = node_tree.nodes.new("ShaderNodeInvert")
    inv_opac_n.name = inv_opac_n.label = INV_OPAC_NODE
    inv_opac_n.inputs[0].default_value = 1.0


def init(node_tree, location, opac_from, oinv_to):
    """Initialize oinv flavor

    :param node_tree: node tree on which oinv flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location (int, int)
    :param opac_from: node socket from which oinv flavor should get opacity
    :type opac_from: bpy.types.NodeSocket
    :param oinv_to: node socket to which result of inverted opacity should be send
    :type oinv_to: bpy.types.NodeSocket
    """

    if INV_OPAC_NODE not in node_tree.nodes:
        __create_node__(node_tree)

        node_tree.nodes[INV_OPAC_NODE].location = location

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(nodes[INV_OPAC_NODE].inputs["Color"], opac_from)
    node_tree.links.new(oinv_to, nodes[INV_OPAC_NODE].outputs[0])

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID


def delete(node_tree):
    """Delete oinv flavor nodes from node tree.

    :param node_tree: node tree from which oinv flavor should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if INV_OPAC_NODE in node_tree.nodes:

        out_socket = None
        in_socket = None

        for link in node_tree.links:

            if link.to_node == node_tree.nodes[INV_OPAC_NODE]:
                out_socket = link.from_socket

            if link.from_node == node_tree.nodes[INV_OPAC_NODE]:
                in_socket = link.to_socket

        node_tree.nodes.remove(node_tree.nodes[INV_OPAC_NODE])

        # if out and in socket were properly recovered recreate link state without oinv flavor
        if out_socket and in_socket:
            node_tree.links.new(out_socket, in_socket)

    if FLAVOR_ID in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[FLAVOR_ID])


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree.nodes

