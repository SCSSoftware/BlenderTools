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


FLAVOR_ID = "awhite"

_AWHITE_MIX_NODE = "AwhiteMix"


def __create_node__(node_tree):
    """Create node for alpha to white mixing.

    :param node_tree: node tree on which this flavor will be used
    :type node_tree: bpy.types.NodeTree
    :return: alpha to white mixing node
    :rtype: bpy.types.Node
    """
    awhite_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
    awhite_mix_n.name = awhite_mix_n.label = _AWHITE_MIX_NODE
    awhite_mix_n.blend_type = "MIX"
    awhite_mix_n.inputs['Color1'].default_value = (1,) * 4

    return awhite_mix_n


def init(node_tree, location, mix_factor_from, color_from, color_to):
    """Initialize alpha to white flavor.

    :param node_tree: node tree on which this flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param location: position in node tree
    :type location: (int, int)
    :param mix_factor_from: node socket from which mixing factor should be taken
    :type mix_factor_from: bpy.types.NodeSocket
    :param color_from: node socket from which color should be applierd
    :type color_from: bpy.types.NodeSocket
    :param color_to: node socket to which result of awhite should be send
    :type color_to: bpy.types.NodeSocket
    """

    if is_set(node_tree):
        return

    awhite_mix_n = __create_node__(node_tree)
    awhite_mix_n.location = location

    # links creation
    node_tree.links.new(awhite_mix_n.inputs['Fac'], mix_factor_from)
    node_tree.links.new(awhite_mix_n.inputs['Color2'], color_from)

    node_tree.links.new(color_to, awhite_mix_n.outputs['Color'])

    node_tree[FLAVOR_ID] = True


def delete(node_tree):
    """Delete alpha to white flavor from node tree.

    :param node_tree: node tree from which this flavor should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if FLAVOR_ID in node_tree:
        node_tree.nodes.remove(node_tree.nodes[_AWHITE_MIX_NODE])
        del node_tree[FLAVOR_ID]


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree and node_tree[FLAVOR_ID]


def get_out_socket(node_tree):
    """Gets socket from which this flavor is outputing color.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: node socket if flavor is set; None otherwise
    :rtype: bpy.types.NodeSocket | None
    """
    if is_set(node_tree):
        return node_tree.nodes[_AWHITE_MIX_NODE].outputs['Color']

    return None
