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

# Copyright (C) 2021: SCS Software

from io_scs_tools.internals.shaders.flavors.flipsheet import flipsheet_compute_ng

FLAVOR_ID = "flipsheet"
FLIPSHEET_COMPUTE_NODE = "FlipsheetCompute"


def __create_node__(node_tree):
    """Create node for fadesheet computation.

    :param node_tree: node tree to create node in
    :type node_tree: bpy.types.NodeTree
    """
    fadesheet_compute_n = node_tree.nodes.new("ShaderNodeGroup")
    fadesheet_compute_n.name = fadesheet_compute_n.label = FLIPSHEET_COMPUTE_NODE
    fadesheet_compute_n.node_tree = flipsheet_compute_ng.get_node_group()


def init(node_tree, location, uv_output, base_texture_input):
    """Initialize fadesheet flavor.

    :param node_tree: node tree on which fadesheet will be used
    :type node_tree: bpy.types.NodeTree
    :param location: position in node tree
    :type location: (int, int)
    :param uv_output: output socket of the uv node
    :type uv_output: bpy.types.NodeSocket
    :param base_texture_input: input socket of the base texture
    :type base_texture_input: bpy.types.NodeSocket
    """

    if FLIPSHEET_COMPUTE_NODE not in node_tree.nodes:
        __create_node__(node_tree)

        node_tree.nodes[FLIPSHEET_COMPUTE_NODE].location = location

    # links creation
    nodes = node_tree.nodes

    node_tree.links.new(nodes[FLIPSHEET_COMPUTE_NODE].inputs['UV'], uv_output)
    node_tree.links.new(base_texture_input, nodes[FLIPSHEET_COMPUTE_NODE].outputs['UV'])

    # FIXME: move to old system after: https://developer.blender.org/T68406 is resolved
    flavor_frame = node_tree.nodes.new(type="NodeFrame")
    flavor_frame.name = flavor_frame.label = FLAVOR_ID


def delete(node_tree):
    """Delete alpha test nodes from node tree.

    :param node_tree: node tree from which alpha test should be deleted
    :type node_tree: bpy.types.NodeTree
    """

    if FLIPSHEET_COMPUTE_NODE in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[FLIPSHEET_COMPUTE_NODE])

    if FLAVOR_ID in node_tree.nodes:
        node_tree.nodes.remove(node_tree.nodes[FLAVOR_ID])


def get_node(node_tree):
    """Gets flavor node.

    :param node_tree: node tree from which tex gen flavor node should be returned
    :type node_tree: bpy.types.NodeTree
    :return: node if it's set; otherwise None
    :rtype: bpy.types.NodeTree | None
    """
    return node_tree.nodes[FLIPSHEET_COMPUTE_NODE] if FLIPSHEET_COMPUTE_NODE in node_tree.nodes else None


def is_set(node_tree):
    """Check if flavor is set or not.

    :param node_tree: node tree which should be checked for existance of this flavor
    :type node_tree: bpy.types.NodeTree
    :return: True if flavor exists; False otherwise
    :rtype: bool
    """
    return FLAVOR_ID in node_tree.nodes


def set_fps(node_tree, fps):
    """Sets FPS playback speed to the flavor.

    :param node_tree: node tree to set to
    :type node_tree: bpy.types.NodeTree
    :param fps: fps playback in sceonds
    :type: fps: float
    """
    fadesheet_compute_n = get_node(node_tree)

    if fadesheet_compute_n:
        fadesheet_compute_n.inputs['FPS'].default_value = fps


def set_frames_total(node_tree, frames_total):
    """Sets total number of frame to the flavor.

    :param node_tree: node tree to set to
    :type node_tree: bpy.types.NodeTree
    :param frames_total: total number of frames
    :type: frames_total: float
    """
    fadesheet_compute_n = get_node(node_tree)

    if fadesheet_compute_n:
        fadesheet_compute_n.inputs['FramesTotal'].default_value = frames_total


def set_frames_row(node_tree, frames_row):
    """Sets number of frames per row to the flavor.

    :param node_tree: node tree to set to
    :type node_tree: bpy.types.NodeTree
    :param frames_row: number of frames per row
    :type: frames_row: float
    """
    fadesheet_compute_n = get_node(node_tree)

    if fadesheet_compute_n:
        fadesheet_compute_n.inputs['FramesRow'].default_value = frames_row


def set_frame_size(node_tree, frame_width, frame_height):
    """Sets size of the individual frame to the flavor.

    :param node_tree: node tree to set to
    :type node_tree: bpy.types.NodeTree
    :param frame_width: normalized width of the frame
    :type: frame_width: float
    :param frame_height: normalized height of the frame
    :type: frame_height: float
    """
    fadesheet_compute_n = get_node(node_tree)

    if fadesheet_compute_n:
        fadesheet_compute_n.inputs['FrameSize'].default_value[0] = frame_width
        fadesheet_compute_n.inputs['FrameSize'].default_value[1] = frame_height
        fadesheet_compute_n.inputs['FrameSize'].default_value[2] = 0.0
