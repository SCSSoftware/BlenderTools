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

from io_scs_tools.internals.shaders.std_node_groups import alpha_test_ng

FLAVOR_ID = "alpha_test"
_ALPHA_TEST_PASS = "AlphaTestPass"


def init(node_tree):
    """Initialize alpha test.

    :param node_tree: node tree on which alpha test will be used
    :type node_tree: bpy.types.NodeTree
    """

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID


def delete(node_tree):
    """Delete alpha test nodes from node tree.

    :param node_tree: node tree from which alpha test should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if _ALPHA_TEST_PASS in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[_ALPHA_TEST_PASS])

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


def add_pass(node_tree, shader_from, alpha_from, shader_to):
    """Adds alpha test pass to simulate alpha cliping in combination with blending modes.

    :param node_tree: node tree to which pass should be added
    :type node_tree: bpy.types.NodeTree
    :param shader_from: where shader output should be taken from
    :type shader_from: bpy.types.NodeSocket
    :param alpha_from: where alpha output should be taken from
    :type alpha_from: bpy.types.NodeSocket
    :param shader_to: where should alpha tested pass output should go to
    :type shader_to: bpy.types.NodeSocket
    """
    node_from = shader_from.node

    # we will insert alpha pass, thus move right nodes for one slot to the right
    for node in node_tree.nodes:
        if node.location.x > node_from.location.x:
            node.location.x += 185

    # create alpha pass node
    alpha_test_pass_n = node_tree.nodes.new("ShaderNodeGroup")
    alpha_test_pass_n.name = alpha_test_pass_n.label = _ALPHA_TEST_PASS
    alpha_test_pass_n.location = (node_from.location.x + 185, node_from.location.y)
    alpha_test_pass_n.node_tree = alpha_test_ng.get_node_group()
    alpha_test_pass_n.inputs['Alpha'].default_value = 1.0

    # link it to the the node tree
    node_tree.links.new(alpha_test_pass_n.inputs['Shader'], shader_from)
    node_tree.links.new(alpha_test_pass_n.inputs['Alpha'], alpha_from)

    node_tree.links.new(shader_to, alpha_test_pass_n.outputs['Shader'])
