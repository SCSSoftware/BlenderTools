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

ALPHA_TEST_NODE = "AlphaTestCalc"


def __create_node__(node_tree):
    """Create node for alpha test.

    :param node_tree: node tree on which alpha test will be used
    :type node_tree: bpy.types.NodeTree
    """
    alpha_test_n = node_tree.nodes.new("ShaderNodeMath")
    alpha_test_n.name = ALPHA_TEST_NODE
    alpha_test_n.label = ALPHA_TEST_NODE
    alpha_test_n.operation = "GREATER_THAN"
    alpha_test_n.inputs[1].default_value = 0.05


def init(node_tree, location, alpha_from, alpha_to):
    """Initialize alpha test.

    :param node_tree: node tree on which alpha test will be used
    :type node_tree: bpy.types.NodeTree
    :param location: x position in node tree
    :type location (int, int)
    :param alpha_from: node socket from which alpha test should be applierd
    :type alpha_from: bpy.types.NodeSocket
    :param alpha_to: node socket to which result of alpha test should be send
    :type alpha_to: bpy.types.NodeSocket
    """

    if ALPHA_TEST_NODE not in node_tree.nodes:
        __create_node__(node_tree)

        node_tree.nodes[ALPHA_TEST_NODE].location = location

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(nodes[ALPHA_TEST_NODE].inputs[0], alpha_from)
    node_tree.links.new(alpha_to, nodes[ALPHA_TEST_NODE].outputs[0])


def delete(node_tree):
    """Delete alpha test nodes from node tree.

    :param node_tree: node tree from which alpha test should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if ALPHA_TEST_NODE in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[ALPHA_TEST_NODE])
