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


def init(node_tree, alpha_from, alpha_to):
    """Initialize blend over.

    :param node_tree: node tree on which blend over will be used
    :type node_tree: bpy.types.NodeTree
    :param alpha_from: node socket from which blend over should be applierd
    :type alpha_from: bpy.types.NodeSocket
    :param alpha_to: node socket to which result of blend over should be send
    :type alpha_to: bpy.types.NodeSocket
    """

    # links creation
    node_tree.links.new(alpha_to, alpha_from)