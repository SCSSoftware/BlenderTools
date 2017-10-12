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

# Copyright (C) 2017: SCS Software

FLAVOR_ID = "asafew"


def init(node_tree, alpha_remap_gn):
    """Initialize alpha test safe weight.

    :param node_tree: node tree on which this flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param alpha_remap_gn: node of alpha remap
    :type alpha_remap_gn: bpy.types.Node
    """

    if is_set(node_tree):
        return

    alpha_remap_gn.inputs["Factor1"].default_value = 1.0 / 0.875
    alpha_remap_gn.inputs["Factor2"].default_value = -0.125 * 1.0 / 0.875

    node_tree[FLAVOR_ID] = True


def delete(node_tree, alpha_remap_gn):
    """Delete alpha to white flavor from node tree.

    :param node_tree: node tree from which this flavor should be deleted
    :type node_tree: bpy.types.NodeTree
    :param alpha_remap_gn: node of alpha remap
    :type alpha_remap_gn: bpy.types.Node
    """

    if FLAVOR_ID in node_tree:
        alpha_remap_gn.inputs["Factor1"].default_value = 1.0
        alpha_remap_gn.inputs["Factor2"].default_value = 0.0

        del node_tree[FLAVOR_ID]


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree and node_tree[FLAVOR_ID]
