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


FLAVOR_ID = "blend_mult"

_HUE_SAT_NODE = "BlendMultHueSat"
_ALPHA_POW_NODE = "BlendMultAlphaPower"


def __create_nodes__(node_tree):
    """Create node for alpha to white mixing.

    :param node_tree: node tree on which this flavor will be used
    :type node_tree: bpy.types.NodeTree
    :return: alpha to white mixing node
    :rtype: (bpy.types.Node, bpy.types.Node)
    """

    hue_sat_mix_n = node_tree.nodes.new("ShaderNodeHueSaturation")
    hue_sat_mix_n.name = hue_sat_mix_n.label = _HUE_SAT_NODE
    hue_sat_mix_n.inputs['Hue'].default_value = 0.5
    hue_sat_mix_n.inputs['Saturation'].default_value = 1.5
    hue_sat_mix_n.inputs['Value'].default_value = 0.025
    hue_sat_mix_n.inputs['Fac'].default_value = 1.0

    alpha_pow_n = node_tree.nodes.new("ShaderNodeMath")
    alpha_pow_n.name = alpha_pow_n.label = _ALPHA_POW_NODE
    alpha_pow_n.operation = "POWER"
    alpha_pow_n.inputs[1].default_value = 1.5

    return hue_sat_mix_n, alpha_pow_n


def init(node_tree, location, alpha_from, alpha_to, color_from, color_to):
    """Initialize blend multiplication flavor.

    NOTE: this flavor implementation is fake aproximation to be
    used in eut2.unlit.vcol.tex shader

    :param node_tree: node tree on which this flavor will be used
    :type node_tree: bpy.types.NodeTree
    :param location: position in node tree
    :type location: (int, int)
    :param alpha_from: node socket from which alpha should be taken
    :type alpha_from: bpy.types.NodeSocket
    :param alpha_to: node socket to which alpha should be send
    :type alpha_to: bpy.types.NodeSocket
    :param color_from: node socket from which color should be applierd
    :type color_from: bpy.types.NodeSocket
    :param color_to: node socket to which result of this flavor should be send
    :type color_to: bpy.types.NodeSocket
    """

    if not is_set(node_tree):
        (hue_sat_mix_n, alpha_pow_n) = __create_nodes__(node_tree)
        hue_sat_mix_n.location = location
        alpha_pow_n.location = location
        alpha_pow_n.location.y -= 200
    else:
        hue_sat_mix_n = node_tree.nodes[_HUE_SAT_NODE]
        alpha_pow_n = node_tree.nodes[_ALPHA_POW_NODE]

    # links creation
    node_tree.links.new(hue_sat_mix_n.inputs['Color'], color_from)
    node_tree.links.new(alpha_pow_n.inputs[0], alpha_from)

    node_tree.links.new(color_to, hue_sat_mix_n.outputs['Color'])
    node_tree.links.new(alpha_to, alpha_pow_n.outputs[0])

    node_tree[FLAVOR_ID] = True


def delete(node_tree):
    """Delete blend multiplication flavor from node tree.

    :param node_tree: node tree from which blend over should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if FLAVOR_ID in node_tree:
        node_tree.nodes.remove(node_tree.nodes[_HUE_SAT_NODE])
        node_tree.nodes.remove(node_tree.nodes[_ALPHA_POW_NODE])
        del node_tree[FLAVOR_ID]


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree and node_tree[FLAVOR_ID]
