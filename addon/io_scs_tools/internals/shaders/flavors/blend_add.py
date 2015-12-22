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


FLAVOR_ID = "blend_add"


def init(node_tree, alpha_from, alpha_to):
    """Initialize blend add.

    NOTE: this flavor is implemented the same as "blend_over" for now
    because we don't have access to pixel color behind the material
    using this flavor. So the closest solution is to use blend_over
    as we at least get the opacity blending with alpha channel.
    :param node_tree: node tree on which blend over will be used
    :type node_tree: bpy.types.NodeTree
    :param alpha_from: node socket from which blend over should be applierd
    :type alpha_from: bpy.types.NodeSocket
    :param alpha_to: node socket to which result of blend over should be send
    :type alpha_to: bpy.types.NodeSocket
    """

    # links creation
    node_tree.links.new(alpha_to, alpha_from)

    node_tree[FLAVOR_ID] = True


def delete(node_tree):
    """Delete blend over from node tree.

    :param node_tree: node tree from which blend over should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if FLAVOR_ID in node_tree:
        del node_tree[FLAVOR_ID]


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree and node_tree[FLAVOR_ID]
