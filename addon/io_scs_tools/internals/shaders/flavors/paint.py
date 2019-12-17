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

# Copyright (C) 2016: SCS Software

from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

FLAVOR_ID = "paint"
PAINT_MULT_NODE = "PaintFlavorMult"


def __create_node__(node_tree):
    """Create node for paint node.

    :param node_tree: node tree on which paint flavor will be used
    :type node_tree: bpy.types.NodeTree
    """
    paint_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
    paint_mult_n.name = paint_mult_n.label = PAINT_MULT_NODE
    paint_mult_n.operation = "MULTIPLY"

    color = _convert_utils.to_node_color(_get_scs_globals().base_paint_color)
    paint_mult_n.inputs[1].default_value = color[:3]


def init(node_tree, location, diffuse_from, paint_to):
    """Initialize paint flavor

    :param node_tree: node tree on which paint flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location (int, int)
    :param diffuse_from: node socket from which paint flavor should get multiplication color
    :type diffuse_from: bpy.types.NodeSocket
    :param paint_to: node socket to which result of base paint multiplication should be send
    :type paint_to: bpy.types.NodeSocket
    """

    if PAINT_MULT_NODE not in node_tree.nodes:
        __create_node__(node_tree)

        node_tree.nodes[PAINT_MULT_NODE].location = location

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(nodes[PAINT_MULT_NODE].inputs[0], diffuse_from)
    node_tree.links.new(paint_to, nodes[PAINT_MULT_NODE].outputs[0])

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID


def delete(node_tree):
    """Delete paint flavor nodes from node tree.

    :param node_tree: node tree from which paint flavor should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if PAINT_MULT_NODE in node_tree.nodes:

        out_socket = None
        in_socket = None

        for link in node_tree.links:

            if link.to_node == node_tree.nodes[PAINT_MULT_NODE]:
                out_socket = link.from_socket

            if link.from_node == node_tree.nodes[PAINT_MULT_NODE]:
                in_socket = link.to_socket

        node_tree.nodes.remove(node_tree.nodes[PAINT_MULT_NODE])

        # if out and in socket were properly recovered recreate link state without paint flavor
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


def set_color(node_tree, color):
    """Set paint color to this node tree if paint flavor is enabled

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :param color: new color value
    :type color: mathutils.Color
    """

    if not is_set(node_tree):
        return

    color = _convert_utils.to_node_color(color)
    node_tree.nodes[PAINT_MULT_NODE].inputs[1].default_value = color
