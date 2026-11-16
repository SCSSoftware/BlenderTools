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

"""Compatibility layer for different Blender versions (3.x up to 5.x).

All the functions here use feature detection rather than version checks,
so they keep working on any Blender version providing either old or new API.
"""

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader

# ---------------------------------------------------------------------------
# Node groups (Blender 4.0 replaced NodeTree.inputs/outputs with NodeTree.interface)
# ---------------------------------------------------------------------------


def ng_new_socket(node_group, in_out, socket_type, name):
    """Creates new input or output socket on given node group.

    :param node_group: node group to create socket on
    :type node_group: bpy.types.NodeTree
    :param in_out: 'INPUT' or 'OUTPUT'
    :type in_out: str
    :param socket_type: socket type, e.g. "NodeSocketFloat"
    :type socket_type: str
    :param name: name of the socket
    :type name: str
    :return: created interface socket
    """
    if hasattr(node_group, "interface"):
        return node_group.interface.new_socket(name, in_out=in_out, socket_type=socket_type)

    sockets = node_group.inputs if in_out == 'INPUT' else node_group.outputs
    return sockets.new(socket_type, name)


def ng_clear_sockets(node_group):
    """Removes all input and output sockets from given node group.

    :param node_group: node group to clear sockets of
    :type node_group: bpy.types.NodeTree
    """
    if hasattr(node_group, "interface"):
        node_group.interface.clear()
    else:
        node_group.inputs.clear()
        node_group.outputs.clear()


def ng_get_socket(node_group, in_out, name):
    """Gets input or output interface socket from given node group by name.

    :param node_group: node group to get socket from
    :type node_group: bpy.types.NodeTree
    :param in_out: 'INPUT' or 'OUTPUT'
    :type in_out: str
    :param name: name of the socket
    :type name: str
    :return: interface socket
    """
    if hasattr(node_group, "interface"):
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == in_out and item.name == name:
                return item
        raise KeyError("Socket %r not found in node group %r" % (name, node_group.name))

    sockets = node_group.inputs if in_out == 'INPUT' else node_group.outputs
    return sockets[name]


# ---------------------------------------------------------------------------
# Shader nodes (Blender 3.3 replaced Separate/Combine RGB/HSV with Separate/Combine Color)
# NOTE: sockets of created nodes should be accessed by index as names differ between old and new nodes:
#   separate: inputs[0] -> color; outputs[0..2] -> R,G,B (or H,S,V)
#   combine: inputs[0..2] -> R,G,B; outputs[0] -> color
# ---------------------------------------------------------------------------


def __new_color_node__(nodes, new_type, mode, legacy_type):
    try:
        node = nodes.new(new_type)
        node.mode = mode
    except RuntimeError:
        node = nodes.new(legacy_type)
    return node


def new_separate_rgb_node(nodes):
    """Creates separate RGB node. Sockets have to be accessed by index!"""
    return __new_color_node__(nodes, "ShaderNodeSeparateColor", 'RGB', "ShaderNodeSeparateRGB")


def new_combine_rgb_node(nodes):
    """Creates combine RGB node. Sockets have to be accessed by index!"""
    return __new_color_node__(nodes, "ShaderNodeCombineColor", 'RGB', "ShaderNodeCombineRGB")


def new_separate_hsv_node(nodes):
    """Creates separate HSV node. Sockets have to be accessed by index!"""
    return __new_color_node__(nodes, "ShaderNodeSeparateColor", 'HSV', "ShaderNodeSeparateHSV")


# ---------------------------------------------------------------------------
# Mesh normals (Blender 4.1 removed auto smooth and split normals API)
# ---------------------------------------------------------------------------


HAS_LEGACY_SPLIT_NORMALS = hasattr(bpy.types.Mesh, "calc_normals_split")
"""True if mesh has auto smooth & split normals API (Blender < 4.1)."""


def mesh_calc_split_normals(mesh):
    """Makes sure that corner (split) normals are calculated and available in mesh.loops[].normal,
    without splitting any normals by angle.

    :param mesh: mesh to calculate normals for
    :type mesh: bpy.types.Mesh
    """
    if HAS_LEGACY_SPLIT_NORMALS:
        if not mesh.use_auto_smooth:
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = 3.14
        mesh.calc_normals_split()
    # Blender 4.1+: corner normals are always calculated on demand


def mesh_free_split_normals(mesh):
    """Frees split normals if needed by this Blender version.

    :param mesh: mesh to free normals of
    :type mesh: bpy.types.Mesh
    """
    if HAS_LEGACY_SPLIT_NORMALS:
        mesh.free_normals_split()


def mesh_enable_custom_normals(mesh):
    """Makes sure custom normals set on mesh will be used (Blender < 4.1 requires auto smooth).

    :param mesh: mesh to enable custom normals for
    :type mesh: bpy.types.Mesh
    """
    if HAS_LEGACY_SPLIT_NORMALS:
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = 3.14


# ---------------------------------------------------------------------------
# Actions (Blender 4.4 introduced slotted actions, Blender 5.0 removed legacy Action.fcurves/groups)
# ---------------------------------------------------------------------------


def action_get_fcurves(action):
    """Gets all F-Curves of given action.

    :param action: action to get curves from
    :type action: bpy.types.Action
    :return: list of fcurves
    :rtype: list[bpy.types.FCurve]
    """
    if hasattr(action, "layers") and not hasattr(action, "fcurves"):
        fcurves = []
        for layer in action.layers:
            for strip in layer.strips:
                for channelbag in getattr(strip, "channelbags", ()):
                    fcurves.extend(channelbag.fcurves)
        return fcurves

    return list(action.fcurves)


def action_new_fcurve(action, datablock, data_path, index, group_name):
    """Creates new F-Curve in given action for given data-block.
    NOTE: action has to be assigned to datablock animation data already.

    :param action: action to create curve in
    :type action: bpy.types.Action
    :param datablock: ID data-block action is animating
    :type datablock: bpy.types.ID
    :param data_path: data path of the curve
    :type data_path: str
    :param index: array index of the curve
    :type index: int
    :param group_name: name of the group curve should belong to
    :type group_name: str
    :return: created fcurve
    :rtype: bpy.types.FCurve
    """
    if hasattr(action, "fcurve_ensure_for_datablock"):
        return action.fcurve_ensure_for_datablock(datablock, data_path, index=index, group_name=group_name)

    return action.fcurves.new(data_path, index=index, action_group=group_name)


# ---------------------------------------------------------------------------
# Drawing (Blender 4.0 removed blf dpi argument and "2D_"/"3D_" builtin shader prefixes)
# ---------------------------------------------------------------------------


def blf_size(font_id, size):
    """Sets font size in version independent way.

    :param font_id: font id
    :type font_id: int
    :param size: font size
    :type size: float
    """
    try:
        blf.size(font_id, size)
    except TypeError:
        blf.size(font_id, size, 72)


def get_builtin_shader(name):
    """Gets builtin shader by its new name (without "2D_"/"3D_" prefix), falling back to legacy name.

    :param name: shader name, e.g. "UNIFORM_COLOR", "IMAGE"
    :type name: str
    :rtype: gpu.types.GPUShader
    """
    try:
        return gpu.shader.from_builtin(name)
    except ValueError:
        return gpu.shader.from_builtin("2D_" + name)


def draw_texture_2d(texture, position, width, height):
    """Draws given GPU texture as 2D rectangle with alpha blending.

    :param texture: texture to draw
    :type texture: gpu.types.GPUTexture
    :param position: bottom left position of the rectangle
    :type position: tuple[float, float]
    :param width: width of the rectangle
    :type width: float
    :param height: height of the rectangle
    :type height: float
    """
    x, y = position
    shader = get_builtin_shader("IMAGE")
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": ((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
        },
    )
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_sampler("image", texture)
    batch.draw(shader)
    gpu.state.blend_set('NONE')


# ---------------------------------------------------------------------------
# Operators (Blender 4.0 removed passing context override dictionary to operators)
# ---------------------------------------------------------------------------


def call_op_with_override(op, override, *args, **kwargs):
    """Calls given operator with context override.

    :param op: operator to call, e.g. bpy.ops.object.join
    :param override: context override members
    :type override: dict
    :return: operator result
    """
    if hasattr(bpy.context, "temp_override"):
        with bpy.context.temp_override(**override):
            return op(*args, **kwargs)

    return op(override, *args, **kwargs)


# ---------------------------------------------------------------------------
# Properties (Blender 5.0 separated storage of bpy.props defined properties from custom properties,
# thus struct["prop_name"] no longer accesses value of property defined with bpy.props)
# ---------------------------------------------------------------------------


def rna_props_storage(struct):
    """Gets ID properties storage holding raw values of properties defined with bpy.props.
    Writing into it changes property value without triggering property update callbacks.

    :param struct: struct (ID, PropertyGroup etc.) holding properties
    :type struct: bpy.types.bpy_struct
    :return: storage that can be accessed as dictionary
    :rtype: idprop.types.IDPropertyGroup | bpy.types.bpy_struct
    """
    getter = getattr(struct, "bl_system_properties_get", None)
    if getter:
        return getter(do_create=True)

    return struct
