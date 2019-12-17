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

from io_scs_tools.internals.shaders.std_node_groups import blend_add_ng

FLAVOR_ID = "blend_add"

_BLEND_ADD_GN = "BlendAddPass"


def init(node_tree, location, shader_from, shader_to):
    """Initialize blend add.

    :param node_tree: node tree on which blend over will be used
    :type node_tree: bpy.types.NodeTree
    :param location: location where blend pass node should be created
    :type location: tuple(int, int)
    :param shader_from: node socket from which blend pass should take the shader result
    :type shader_from: bpy.types.NodeSocket
    :param shader_to: node socket to which result of blend pass should be sent
    :type shader_to: bpy.types.NodeSocket
    """

    # node creation
    blend_add_n = node_tree.nodes.new("ShaderNodeGroup")
    blend_add_n.name = blend_add_n.label = _BLEND_ADD_GN
    blend_add_n.location = location
    blend_add_n.node_tree = blend_add_ng.get_node_group()

    # link creation
    node_tree.links.new(blend_add_n.inputs['Shader'], shader_from)
    node_tree.links.new(shader_to, blend_add_n.outputs['Shader'])

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID


def delete(node_tree):
    """Delete blend over from node tree.

    :param node_tree: node tree from which blend over should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if _BLEND_ADD_GN in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[_BLEND_ADD_GN])

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
