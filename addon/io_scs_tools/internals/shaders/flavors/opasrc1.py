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

FLAVOR_ID = "opasrc01"
MULT_OPAC_SRC_NODE = "MultOpaqueSource"


def __create_node__(node_tree):
    """Create node for oinv node.

    :param node_tree: node tree on which oinv flavor will be used
    :type node_tree: bpy.types.NodeTree
    """
    mult_opac_src_n = node_tree.nodes.new("ShaderNodeMath")
    mult_opac_src_n.name = mult_opac_src_n.label = MULT_OPAC_SRC_NODE
    mult_opac_src_n.operation = "MULTIPLY"
    mult_opac_src_n.inputs[1].default_value = 1.0


def init(node_tree, location, alpha_from, opac_from, alpha_to):
    """Initialize oinv flavor

    :param node_tree: node tree on which oinv flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location (int, int)
    :param alpha_from: node socket from which opasrc flavor should get alpha
    :type alpha_from: bpy.types.NodeSocket
    :param opac_from: node socket from which opasrc flavor should get opacity
    :type opac_from: bpy.types.NodeSocket
    :param alpha_to: node socket to which result of alpha and opaque mult should be send
    :type alpha_to: bpy.types.NodeSocket
    """

    if MULT_OPAC_SRC_NODE not in node_tree.nodes:
        __create_node__(node_tree)

        node_tree.nodes[MULT_OPAC_SRC_NODE].location = location

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(alpha_from, nodes[MULT_OPAC_SRC_NODE].inputs[0])
    node_tree.links.new(opac_from, nodes[MULT_OPAC_SRC_NODE].inputs[1])

    node_tree.links.new(nodes[MULT_OPAC_SRC_NODE].outputs[0], alpha_to)

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID

def delete(node_tree):
    """Delete oinv flavor nodes from node tree.

    :param node_tree: node tree from which opasrc flavor should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if MULT_OPAC_SRC_NODE in node_tree.nodes:

        out_socket = None
        in_socket = None

        for link in node_tree.links:

            if link.to_node == node_tree.nodes[MULT_OPAC_SRC_NODE]:
                out_socket = link.from_socket

            if link.from_node == node_tree.nodes[MULT_OPAC_SRC_NODE]:
                in_socket = link.to_socket

        node_tree.nodes.remove(node_tree.nodes[MULT_OPAC_SRC_NODE])

        # if out and in socket were properly recovered recreate link state without opasrc flavor
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