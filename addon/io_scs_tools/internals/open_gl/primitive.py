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

# Copyright (C) 2013-2019: SCS Software

import bgl
import blf
import gpu
from array import array
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from io_scs_tools.internals.open_gl.shaders import get_shader, ShaderTypes


class _Buffer:
    """Buffer class being able to store and dispatch drawing of primitives."""

    class Types:
        POINTS = 1
        LINES = 2
        TRIS = 3

    def __init__(self, buffer_type, draw_size, shader_type, attr_names):
        """Create buffer instance with given type drawing size and shader type.

        :param buffer_type: type of the buffer from _Buffer.Types
        :type buffer_type: int
        :param draw_size: size of the drawing elements
        :type draw_size: float
        :param shader_type: type of the shader for given buffer from ShaderTypes
        :type shader_type: int
        :param attr_names: tuple of string defining attributes that this buffer is holding
        :type attr_names: tuple[str]
        """
        if buffer_type not in {_Buffer.Types.LINES, _Buffer.Types.POINTS, _Buffer.Types.TRIS}:
            raise TypeError("Unsupported buffer type requested: %s!" % buffer_type)

        self.__type = buffer_type
        self.__draw_size = draw_size
        self.__shader = get_shader(shader_type)
        self.__data = {}

        for att_name in attr_names:
            self.__data[att_name] = []

        # depending on type  setup callbacks executed before and after dispatching
        if buffer_type == _Buffer.Types.LINES:

            self.__bgl_callback = bgl.glLineWidth
            self.__bgl_callback_param_before = self.__draw_size
            self.__bgl_callback_param_after = 1.0
            self.__draw_type = 'LINES'

        elif buffer_type == _Buffer.Types.POINTS:

            self.__bgl_callback = bgl.glPointSize
            self.__bgl_callback_param_before = self.__draw_size
            self.__bgl_callback_param_after = 1.0
            self.__draw_type = 'POINTS'

        elif buffer_type == _Buffer.Types.TRIS:

            self.__bgl_callback = lambda *args: None
            self.__bgl_callback_param_before = None
            self.__bgl_callback_param_after = None
            self.__draw_type = 'TRIS'

    def append_attr(self, attr_name, value):
        """Appends given value into the data fields for given attribute name

        NOTE: for performance no safety checks on existing attribute name are made
        :param attr_name: name of the attribute for which value should be append
        :type attr_name: str
        :param value: value that should be append (tuple of floats for position, color etc.)
        :type value: tuple[float] | tuple[int] | float | int
        """
        self.__data[attr_name].append(value)

    def clear(self):
        """Clears all entries in the buffer.
        """
        for attr_name in self.__data:
            self.__data[attr_name].clear()

    def draw(self, uniforms, space_3d):
        """Dispatches drawing for the buffer by creating and drawing batch.

        :param uniforms: list of uniforms tuples to be sent to shader
        :type uniforms: collections.Iterable[(str, type, bytearray, int, int)]
        :param space_3d: space 3D data of viewport to which buffers should be drawn
        :type space_3d: bpy.types.SpaceView3D
        """

        # nothing to draw really
        if not self.has_entries():
            return

        # triangles are not drawn into wireframe views
        if self.__type == _Buffer.Types.TRIS and space_3d.shading.type == 'WIREFRAME':
            return

        self.__bgl_callback(self.__bgl_callback_param_before)

        # bind shader
        self.__shader.bind()

        # fill the uniforms to binded shader
        for uniform_name, uniform_type, uniform_data, uniform_length, uniform_count in uniforms:
            uniform_loc = self.__shader.uniform_from_name(uniform_name)
            if uniform_type == float:
                self.__shader.uniform_vector_float(uniform_loc, uniform_data, uniform_length, uniform_count)
            elif uniform_type == int:
                self.__shader.uniform_vector_int(uniform_loc, uniform_data, uniform_length, uniform_count)
            else:
                raise TypeError("Invalid uniform type: %s" % uniform_type)

        # create batch and dispatch draw
        batch = batch_for_shader(self.__shader, self.__draw_type, self.__data)
        batch.draw(self.__shader)

        self.__bgl_callback(self.__bgl_callback_param_after)

    def has_entries(self):
        """Checks if there is any antries in this buffer.

        :return: True if either position or color have any entries; False otherwise
        :rtype: bool
        """
        return len(self.__data["pos"]) + len(self.__data["color"]) > 0


class _ViewsBufferHandler:
    """Buffers handler class used to implement main view and all local view buffers."""

    @staticmethod
    def __get_new_buffers__():
        """Gets new instance for all buffers we currently use in one view.

        :return: currently we have 5 buffers: 1 for trises, 1 for stipple lines, 1 for normal lines and 2 for points of different size
        :rtype: tuple[_Buffer]
        """
        return (
            _Buffer(_Buffer.Types.TRIS, 0, ShaderTypes.SMOOTH_COLOR_CLIPPED_3D, ("pos", "color")),  # 0
            _Buffer(_Buffer.Types.LINES, 2, ShaderTypes.SMOOTH_COLOR_STIPPLE_CLIPPED_3D, ("pos", "color")),  # 1
            _Buffer(_Buffer.Types.LINES, 2, ShaderTypes.SMOOTH_COLOR_CLIPPED_3D, ("pos", "color")),  # 2
            _Buffer(_Buffer.Types.POINTS, 5, ShaderTypes.SMOOTH_COLOR_CLIPPED_3D, ("pos", "color")),  # 3
            _Buffer(_Buffer.Types.POINTS, 12, ShaderTypes.SMOOTH_COLOR_CLIPPED_3D, ("pos", "color")),  # 4
        )

    def __init__(self):
        """Creates instance of buffers handler. Should be used only once.
        """
        self.__current = None
        self.__buffers = {}

    def __get_buffers__(self, space_3d):
        """Return list of bufffers for given space 3d view. If none is given empty list is returned.

        :param space_3d: space for which buffers should be returned
        :type space_3d: bpy.types.SpaceView3D | None
        :return: list of buffers for given space
        :rtype: list[_Buffer]
        """
        if space_3d in self.__buffers:
            return self.__buffers[space_3d]
        else:
            return []

    def set_current(self, space_3d):
        """Sets currently used view and creates empty buffers to which and point or line will be added.

        :param space_3d: view which should be set as current one, None if main buffers should be set as current
        :type space_3d: bpy.types.SpaceView3D | None
        """
        self.__current = space_3d

        if self.__current not in self.__buffers:
            self.__buffers[self.__current] = self.__get_new_buffers__()

    def append_tris_vertex(self, pos, color):
        """Appends new tris vertex into the current buffers.

        :param pos: world space position of the vertex
        :type pos: mathutils.Vector | tuple
        :param color: color of the vertex, has to be of size 4 and fromat: (r, g, b, a)
        :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
        """
        buffer = self.__buffers[self.__current][0]

        buffer.append_attr("pos", tuple(pos))
        buffer.append_attr("color", tuple(color))

    def append_line_vertex(self, pos, color, is_stipple=False):
        """Appends new line start/end segment into the current buffers.

        :param pos: world space position of the start/end line point
        :type pos: mathutils.Vector | tuple
        :param color: color of the start/end line point, has to be of size 4 and fromat: (r, g, b, a)
        :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
        :param is_stipple: should line be stippled?
        :type is_stipple: bool
        """
        if is_stipple:
            buffer = self.__buffers[self.__current][1]
        else:
            buffer = self.__buffers[self.__current][2]

        buffer.append_attr("pos", tuple(pos))
        buffer.append_attr("color", tuple(color))

    def append_point_vertex(self, pos, color, size):
        """Appends new point into the current buffers.

        :param pos: world space position of the point
        :type pos: mathutils.Vector | tuple
        :param color: color of the point, has to be of size 4 and fromat: (r, g, b, a)
        :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
        :param size: size in which point should be drawn (5.0 and 12.0 currently supported!)
        :type size: float
        """
        if size == 5.0:
            buffer = self.__buffers[self.__current][3]
        elif size == 12.0:
            buffer = self.__buffers[self.__current][4]
        else:
            raise ValueError("Unsupported point size: %.2f. Only 5.0 or 12.0 are supported!" % size)

        buffer.append_attr("pos", tuple(pos))
        buffer.append_attr("color", tuple(color))

    def clear_buffers(self):
        """Clears all the buffers in handler. Then deletes all of them except the main one.
        """
        for buffers in self.__buffers.values():
            for buffer in buffers:
                buffer.clear()

        for space_3d in list(self.__buffers.keys()):
            # ignore main view
            if space_3d is None:
                continue

            # delete other local space buffers
            del self.__buffers[space_3d]

    def draw_buffers(self, space_3d):
        """Draws buffers of given space. If no space is provided main buffers are drawn.

        :param space_3d: space 3D data of viewport to which buffers should be drawn
        :type space_3d: bpy.types.SpaceView3D
        """

        # get clip planes as bytes array ready to be sent into shader
        clip_planes_linear = array('f')
        num_clip_planes = 0
        if space_3d.region_3d.use_clip_planes:
            for clip_plane in space_3d.region_3d.clip_planes:
                if clip_plane[0] == clip_plane[1] == clip_plane[2] == clip_plane[3] == 0.0:
                    continue

                clip_planes_linear.extend(list(clip_plane))
                num_clip_planes += 1

        # put uniforms together
        uniforms = (
            ("clip_planes", float, clip_planes_linear.tobytes(), 4, num_clip_planes),
            ("num_clip_planes", int, array('i', (num_clip_planes,)), 1, 1)
        )

        # if current view has local view use it's buffers otherwise select main ones
        if space_3d.local_view:
            buffers_key = space_3d.local_view
        else:
            buffers_key = None

        # draw selected buffers
        for buffer in self.__get_buffers__(buffers_key):
            buffer.draw(uniforms, space_3d)


_views_buffer_handler = _ViewsBufferHandler()
"""Instace of views buffers handler to be able to have custom handlers for local views."""


def clear_buffers():
    """Clears all drawing buffers we have.
    """
    _views_buffer_handler.clear_buffers()


def draw_buffers(space_3d):
    """Draws current state of buffers onto 3D viewport. If no lines or points, nothing is drawn.

    :param space_3d: space 3D data of viewport to which buffers should be drawn
    :type space_3d: bpy.types.SpaceView3D
    """
    _views_buffer_handler.draw_buffers(space_3d)


def set_active_buffers(space_3d):
    """If given space has local view, then sets it as active, otherwise main buffers are set as active.

    :param space_3d: space 3D data of viewport to which should be set as active; None if main buffers should be set as active
    :type space_3d: bpy.types.SpaceView3D | None
    """
    if space_3d:
        _views_buffer_handler.set_current(space_3d.local_view)
    else:
        _views_buffer_handler.set_current(None)


def append_tris_vertex(pos, color):
    """Appends vertex into the tris buffers (to draw one triangle at least three vertices has to be added).

    :param pos: world space position of the vertex
    :type pos: mathutils.Vector | tuple
    :param color: color of the vertex, has to be of size 4 and fromat: (r, g, b, a)
    :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
    """
    _views_buffer_handler.append_tris_vertex(pos, color)


def append_line_vertex(pos, color, is_strip=False, is_stipple=False):
    """Appends start and/or end segnement of line to buffers (so to draw one line, at least two calls of this function should be made).

    :param pos: world space position of the start/end line point
    :type pos: mathutils.Vector | tuple
    :param color: color of the start/end line point, has to be of size 4 and fromat: (r, g, b, a)
    :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
    :param is_strip: should next line continue from this point on? Similar to GL_LINE_STRIP.
    :type is_strip: bool
    :param is_stipple: should line be stippled?
    :type is_stipple: bool
    """
    _views_buffer_handler.append_line_vertex(pos, color, is_stipple=is_stipple)

    if is_strip:
        append_line_vertex(pos, color, is_stipple=is_stipple)


def append_point_vertex(pos, color, size):
    """Appends point with given position color and size, to buffer

    :param pos: world space position of the point
    :type pos: mathutils.Vector | tuple
    :param color: color of the point, has to be of size 4 and fromat: (r, g, b, a)
    :type color: mathutils.Vector | bpy.types.bpy_prop_collection | tuple
    :param size: size in which point should be drawn (5.0 and 12.0 currently supported!)
    :type size: float
    """
    _views_buffer_handler.append_point_vertex(pos, color, size)


def get_box_data():
    """Returns data for box including vertices, faces and definitions for wired model

    :return: lists of data for box in this order: vertices, faces, wire_lines
    :rtype: list(tuple), list(tuple), list(tuple)
    """
    cube_vertices = [(0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
                     (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5)]

    cube_faces = [(0, 1, 2, 3), (4, 0, 3, 7), (5, 1, 0, 4), (6, 2, 1, 5), (7, 3, 2, 6), (5, 4, 7, 6)]

    cube_wire_lines = [((0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
                        (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
                       ((0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)),
                       ((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5)), ((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))]

    return cube_vertices, cube_faces, cube_wire_lines


def get_sphere_data():
    """Returns data for sphere including vertices, faces and definitions for wired model

    :return: lists of data for sphere in this order: vertices, faces, wire_lines
    :rtype: list(tuple), list(tuple), list(tuple)
    """
    sphere_vertices = [(0.0, -0.5, 0.0), (0.216942, -0.450484, 0.0), (0.153401, -0.450484, 0.153401), (0.0, -0.450484, 0.216942),
                       (-0.153401, -0.450484, 0.153401), (-0.216942, -0.450484, 0.0), (-0.153401, -0.450484, -0.153401),
                       (0.0, -0.450484, -0.216942), (0.153401, -0.450484, -0.153401), (0.390916, -0.311745, 0.0),
                       (0.338543, -0.311745, 0.195458), (0.195458, -0.311745, 0.338543), (0.0, -0.311745, 0.390916),
                       (-0.195458, -0.311745, 0.338543), (-0.338543, -0.311745, 0.195458), (-0.390916, -0.311745, 0.0),
                       (-0.338543, -0.311745, -0.195458), (-0.195458, -0.311745, -0.338543), (0.0, -0.311745, -0.390916),
                       (0.195458, -0.311745, -0.338543), (0.338543, -0.311745, -0.195458), (0.487464, -0.11126, 0.0),
                       (0.422156, -0.111261, 0.243732), (0.243732, -0.111261, 0.422156), (0.0, -0.111261, 0.487464),
                       (-0.243732, -0.111261, 0.422156), (-0.422156, -0.111261, 0.243732), (-0.487464, -0.111261, 0.0),
                       (-0.422156, -0.11126, -0.243732), (-0.243732, -0.11126, -0.422156), (0.0, -0.11126, -0.487464),
                       (0.243732, -0.11126, -0.422156), (0.422156, -0.11126, -0.243732), (0.0, 0.5, 0.0),
                       (-0.216942, 0.450484, 0.0), (-0.153401, 0.450484, 0.153401), (0.0, 0.450484, 0.216942),
                       (0.153401, 0.450484, 0.153401), (0.216942, 0.450484, 0.0), (0.153401, 0.450485, -0.153401),
                       (0.0, 0.450484, -0.216942), (-0.153401, 0.450485, -0.153401), (-0.390916, 0.311745, 0.0),
                       (-0.338543, 0.311745, 0.195458), (-0.195458, 0.311745, 0.338543), (0.0, 0.311745, 0.390916),
                       (0.195458, 0.311745, 0.338543), (0.338543, 0.311745, 0.195458), (0.390916, 0.311745, 0.0),
                       (0.338543, 0.311745, -0.195458), (0.195458, 0.311745, -0.338543), (0.0, 0.311745, -0.390915),
                       (-0.195458, 0.311745, -0.338543), (-0.338543, 0.311745, -0.195458), (-0.487464, 0.11126, 0.0),
                       (-0.422156, 0.11126, 0.243732), (-0.243732, 0.11126, 0.422156), (0.0, 0.11126, 0.487464),
                       (0.243732, 0.11126, 0.422156), (0.422156, 0.11126, 0.243732), (0.487464, 0.11126, 0.0),
                       (0.422156, 0.11126, -0.243732), (0.243732, 0.111261, -0.422156), (0.0, 0.111261, -0.487464),
                       (-0.243732, 0.11126, -0.422156), (-0.422156, 0.11126, -0.243732)]

    sphere_faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 5, 6), (0, 6, 7), (0, 7, 8), (0, 8, 1), (1, 10, 9),
                    (10, 1, 2), (2, 11, 10), (11, 3, 2), (3, 11, 12), (3, 12, 13), (3, 13, 4), (4, 13, 14), (14, 5, 4),
                    (5, 14, 15), (5, 15, 16), (16, 6, 5), (6, 16, 17), (17, 7, 6), (7, 17, 18), (7, 18, 19), (19, 8, 7),
                    (8, 19, 20), (20, 1, 8), (20, 9, 1), (21, 9, 10, 22), (11, 23, 22, 10), (23, 11, 12, 24), (25, 13, 12, 24),
                    (13, 25, 26, 14), (14, 26, 27, 15), (28, 16, 15, 27), (16, 28, 29, 17), (17, 29, 30, 18), (31, 19, 18, 30),
                    (32, 20, 19, 31), (21, 9, 20, 32), (33, 34, 35), (33, 35, 36), (33, 36, 37), (33, 37, 38), (33, 38, 39),
                    (33, 39, 40), (33, 40, 41), (33, 41, 34), (34, 43, 42), (43, 34, 35), (35, 44, 43), (44, 36, 35),
                    (36, 44, 45), (36, 45, 46), (46, 37, 36), (37, 46, 47), (47, 38, 37), (38, 47, 48), (38, 48, 49),
                    (49, 39, 38), (39, 49, 50), (50, 40, 39), (40, 50, 51), (40, 51, 52), (52, 41, 40), (41, 52, 53),
                    (53, 34, 41), (53, 42, 34), (43, 55, 54, 42), (44, 56, 55, 43), (56, 44, 45, 57), (58, 46, 45, 57),
                    (59, 47, 46, 58), (47, 59, 60, 48), (61, 49, 48, 60), (62, 50, 49, 61), (50, 62, 63, 51), (64, 52, 51, 63),
                    (52, 64, 65, 53), (54, 42, 53, 65), (60, 21, 22, 59), (23, 58, 59, 22), (24, 57, 58, 23), (25, 56, 57, 24),
                    (26, 55, 56, 25), (27, 54, 55, 26), (65, 28, 27, 54), (64, 29, 28, 65), (63, 30, 29, 64), (62, 31, 30, 63),
                    (61, 32, 31, 62), (60, 21, 32, 61)]

    sphere_wire_lines = [((0.0, -0.5, 0.0), (0.0, -0.450484, -0.216942), (0.0, -0.311745, -0.390916), (0.0, -0.11126, -0.487464),
                          (0.0, 0.111261, -0.487464), (0.0, 0.311745, -0.390915), (0.0, 0.450484, -0.216942), (0.0, 0.5, 0.0),
                          (0.0, 0.450484, 0.216942), (0.0, 0.311745, 0.390916), (0.0, 0.11126, 0.487464),
                          (0.0, -0.111261, 0.487464), (0.0, -0.311745, 0.390916), (0.0, -0.450484, 0.216942), (0.0, -0.5, 0.0)),
                         ((0.0, -0.5, 0.0), (0.216942, -0.450484, 0.0), (0.390916, -0.311745, 0.0), (0.487464, -0.11126, 0.0),
                          (0.487464, 0.11126, 0.0), (0.390916, 0.311745, 0.0), (0.216942, 0.450484, 0.0), (0.0, 0.5, 0.0),
                          (-0.216942, 0.450484, 0.0), (-0.390916, 0.311745, 0.0), (-0.487464, 0.11126, 0.0),
                          (-0.487464, -0.111261, 0.0), (-0.390916, -0.311745, 0.0), (-0.216942, -0.450484, 0.0), (0.0, -0.5, 0.0)),
                         ((0.0, 0.0, 0.487464), (0.243732, 0.0, 0.422156), (0.422156, 0.0, 0.243732), (0.487464, 0.0, 0.0),
                          (0.422156, 0.0, -0.243732), (0.243732, 0.0, -0.422156), (0.0, 0.0, -0.487464),
                          (-0.243732, 0.0, -0.422156), (-0.422156, 0.0, -0.243732), (-0.487464, 0.0, 0.0),
                          (-0.422156, 0.0, 0.243732), (-0.243732, 0.0, 0.422156), (0.0, 0.0, 0.487464))]

    return sphere_vertices, sphere_faces, sphere_wire_lines


def get_capsule_data():
    """Returns data for capsule including vertices, faces and definitions for wired model

    :return: lists of data for capsule in this order: vertices, faces, wire_lines
    :rtype: list(tuple), list(tuple), list(tuple)
    """
    capsule_vertices = [(0.0, 0.5, 0.0), (-0.433013, 0.0, -0.25), (-0.25, 0.0, -0.433013), (0.0, 0.0, -0.5),
                        (0.25, 0.0, -0.433013), (0.433013, 0.0, -0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, 0.25),
                        (0.25, 0.0, 0.433013), (0.0, 0.0, 0.5), (-0.25, 0.0, 0.433013), (-0.433013, 0.0, 0.25),
                        (-0.5, 0.0, 0.0), (-0.400052, 0.191342, -0.23097), (-0.23097, 0.191342, -0.400051),
                        (0.0, 0.191342, -0.46194), (0.23097, 0.191342, -0.400051), (0.400051, 0.191342, -0.23097),
                        (0.46194, 0.191342, 0.0), (0.400051, 0.191342, 0.23097), (0.23097, 0.191342, 0.400052),
                        (0.0, 0.191342, 0.46194), (-0.23097, 0.191342, 0.400052), (-0.400052, 0.191342, 0.23097),
                        (-0.46194, 0.191342, 0.0), (-0.306186, 0.353553, -0.176777), (-0.176777, 0.353553, -0.306186),
                        (0.0, 0.353553, -0.353553), (0.176777, 0.353554, -0.306186), (0.306186, 0.353554, -0.176777),
                        (0.353553, 0.353553, 0.0), (0.306186, 0.353553, 0.176777), (0.176777, 0.353553, 0.306186),
                        (0.0, 0.353553, 0.353553), (-0.176777, 0.353553, 0.306186), (-0.306186, 0.353553, 0.176777),
                        (-0.353553, 0.353553, 0.0), (-0.135299, 0.46194, -0.135299), (0.0, 0.46194, -0.191341),
                        (0.135299, 0.46194, -0.135299), (0.191342, 0.46194, 0.0), (0.135299, 0.46194, 0.135299),
                        (0.0, 0.46194, 0.191342), (-0.135299, 0.46194, 0.135299), (-0.191342, 0.46194, 0.0),
                        (0.0, -0.5, 0.0), (0.191342, -0.46194, 0.0), (0.135299, -0.46194, 0.135299),
                        (0.0, -0.46194, 0.191342), (-0.135299, -0.46194, 0.135299), (-0.191342, -0.46194, 0.0),
                        (-0.135299, -0.46194, -0.135299), (0.0, -0.46194, -0.191342), (0.135299, -0.46194, -0.135299),
                        (0.353553, -0.353553, 0.0), (0.306186, -0.353553, 0.176777), (0.176777, -0.353553, 0.306186),
                        (0.0, -0.353553, 0.353553), (-0.176777, -0.353554, 0.306186), (-0.306186, -0.353554, 0.176777),
                        (-0.353553, -0.353553, 0.0), (-0.306186, -0.353553, -0.176777), (-0.176777, -0.353553, -0.306186),
                        (0.0, -0.353553, -0.353553), (0.176777, -0.353553, -0.306186), (0.306186, -0.353553, -0.176777),
                        (0.46194, -0.191342, 0.0), (0.400051, -0.191342, 0.23097), (0.23097, -0.191342, 0.400052),
                        (0.0, -0.191342, 0.46194), (-0.23097, -0.191342, 0.400052), (-0.400052, -0.191342, 0.23097),
                        (-0.46194, -0.191342, 0.0), (-0.400051, -0.191342, -0.23097), (-0.23097, -0.191342, -0.400051),
                        (0.0, -0.191342, -0.46194), (0.23097, -0.191342, -0.400051), (0.400051, -0.191342, -0.23097),
                        (0.5, 0.0, 0.0), (0.433012, 0.0, 0.25), (0.25, 0.0, 0.433013), (0.0, 0.0, 0.5),
                        (-0.25, 0.0, 0.433013), (-0.433013, 0.0, 0.25), (-0.5, 0.0, 0.0), (-0.433013, 0.0, -0.25),
                        (-0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (0.25, 0.0, -0.433013), (0.433013, 0.0, -0.25)]

    capsule_faces = [(0, 44, 43), (0, 43, 42), (0, 42, 41), (0, 41, 40), (0, 40, 39), (0, 39, 38), (0, 38, 37), (0, 37, 44),
                     (44, 35, 36), (35, 44, 43), (43, 34, 35), (34, 43, 42), (42, 33, 34), (42, 32, 33), (32, 42, 41),
                     (41, 31, 32), (31, 41, 40), (40, 30, 31), (40, 29, 30), (29, 40, 39), (39, 28, 29), (28, 39, 38),
                     (38, 27, 28), (38, 26, 27), (26, 38, 37), (37, 25, 26), (25, 44, 37), (25, 36, 44), (35, 23, 24, 36),
                     (23, 35, 34, 22), (22, 34, 33, 21), (32, 20, 21, 33), (20, 32, 31, 19), (19, 31, 30, 18), (29, 17, 18, 30),
                     (17, 29, 28, 16), (16, 28, 27, 15), (26, 14, 15, 27), (14, 26, 25, 13), (36, 24, 13, 25), (12, 24, 23, 11),
                     (22, 10, 11, 23), (21, 9, 10, 22), (20, 8, 9, 21), (19, 7, 8, 20), (18, 6, 7, 19), (17, 5, 6, 18),
                     (16, 4, 5, 17), (15, 3, 4, 16), (14, 2, 3, 15), (13, 1, 2, 14), (24, 12, 1, 13), (45, 47, 46), (45, 48, 47),
                     (45, 49, 48), (45, 50, 49), (45, 51, 50), (45, 52, 51), (45, 53, 52), (46, 53, 45), (46, 55, 54),
                     (47, 55, 46), (47, 56, 55), (48, 56, 47), (48, 57, 56), (48, 58, 57), (49, 58, 48), (49, 59, 58),
                     (50, 59, 49), (50, 60, 59), (50, 61, 60), (51, 61, 50), (51, 62, 61), (52, 62, 51), (52, 63, 62),
                     (52, 64, 63), (53, 64, 52), (53, 65, 64), (46, 65, 53), (54, 65, 46), (55, 67, 66, 54), (56, 68, 67, 55),
                     (68, 56, 57, 69), (58, 70, 69, 57), (59, 71, 70, 58), (71, 59, 60, 72), (61, 73, 72, 60), (62, 74, 73, 61),
                     (74, 62, 63, 75), (64, 76, 75, 63), (65, 77, 76, 64), (54, 66, 77, 65), (78, 66, 67, 79), (68, 80, 79, 67),
                     (69, 81, 80, 68), (70, 82, 81, 69), (71, 83, 82, 70), (72, 84, 83, 71), (73, 85, 84, 72), (74, 86, 85, 73),
                     (75, 87, 86, 74), (76, 88, 87, 75), (77, 89, 88, 76), (66, 78, 89, 77), (6, 78, 79, 7), (7, 79, 80, 8),
                     (8, 80, 81, 9), (9, 81, 82, 10), (10, 82, 83, 11), (84, 12, 11, 83), (12, 84, 85, 1), (1, 85, 86, 2),
                     (2, 86, 87, 3), (3, 87, 88, 4), (4, 88, 89, 5), (5, 89, 78, 6)]

    capsule_wire_lines = [((-0.5, 0.0, 0.0), (-0.433013, 0.0, 0.25), (-0.25, 0.0, 0.433013), (0.0, 0.0, 0.5),
                           (0.25, 0.0, 0.433013), (0.433013, 0.0, 0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, -0.25),
                           (0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (-0.25, 0.0, -0.433013), (-0.433013, 0.0, -0.25),
                           (-0.5, 0.0, 0.0)),
                          ((-0.5, 0.0, 0.0), (-0.433013, 0.0, 0.25), (-0.25, 0.0, 0.433013), (0.0, 0.0, 0.5),
                           (0.25, 0.0, 0.433013), (0.433012, 0.0, 0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, -0.25),
                           (0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (-0.25, 0.0, -0.433013), (-0.433013, 0.0, -0.25),
                           (-0.5, 0.0, 0.0)),
                          ((0.0, 0.5, 0.0), (-0.191342, 0.46194, 0.0), (-0.353553, 0.353553, 0.0), (-0.46194, 0.191342, 0.0),
                           (-0.5, 0.0, 0.0), (-0.5, 0.0, 0.0), (-0.46194, -0.191342, 0.0), (-0.353553, -0.353553, 0.0),
                           (-0.191342, -0.46194, 0.0), (0.0, -0.5, 0.0), (0.191342, -0.46194, 0.0), (0.353553, -0.353553, 0.0),
                           (0.46194, -0.191342, 0.0), (0.5, 0.0, 0.0), (0.5, 0.0, 0.0), (0.46194, 0.191342, 0.0),
                           (0.353553, 0.353553, 0.0), (0.191342, 0.46194, 0.0), (0.0, 0.5, 0.0)),
                          ((0.0, 0.5, 0.0), (0.0, 0.46194, -0.191341), (0.0, 0.353553, -0.353553), (0.0, 0.191342, -0.46194),
                           (0.0, 0.0, -0.5), (0.0, 0.0, -0.5), (0.0, -0.191342, -0.46194), (0.0, -0.353553, -0.353553),
                           (0.0, -0.46194, -0.191342), (0.0, -0.5, 0.0), (0.0, -0.46194, 0.191342), (0.0, -0.353553, 0.353553),
                           (0.0, -0.191342, 0.46194), (0.0, 0.0, 0.5), (0.0, 0.0, 0.5), (0.0, 0.191342, 0.46194),
                           (0.0, 0.353553, 0.353553), (0.0, 0.46194, 0.191342), (0.0, 0.5, 0.0))]

    return capsule_vertices, capsule_faces, capsule_wire_lines


def get_cylinder_data():
    """Returns data for cylinder including vertices, faces and definitions for wired model

    :return: lists of data for cylinder in this order: vertices, faces, wire_lines
    :rtype: list(tuple), list(tuple), list(tuple)
    """
    cylinder_vertices = [(-0.433013, 0.0, -0.25), (-0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (0.25, 0.0, -0.433013),
                         (0.433013, 0.0, -0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, 0.25), (0.25, 0.0, 0.433013),
                         (0.0, 0.0, 0.5), (-0.25, 0.0, 0.433013), (-0.433013, 0.0, 0.25), (-0.5, 0.0, 0.0),
                         (-0.433013, 0.0, -0.25), (-0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (0.25, 0.0, -0.433013),
                         (0.433013, 0.0, -0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, 0.25), (0.25, 0.0, 0.433013),
                         (0.0, 0.0, 0.5), (-0.25, 0.0, 0.433013), (-0.433013, 0.0, 0.25), (-0.5, 0.0, 0.0)]

    cylinder_faces = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
                      (0, 1, 13, 12), (1, 2, 14, 13), (2, 3, 15, 14), (3, 4, 16, 15), (4, 5, 17, 16), (5, 6, 18, 17),
                      (6, 7, 19, 18), (7, 8, 20, 19), (8, 9, 21, 20), (9, 10, 22, 21), (10, 11, 23, 22), (11, 0, 12, 23),
                      (23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12)]

    cylinder_wire_lines = [((-0.5, 0.0, 0.0), (-0.433013, 0.0, 0.25), (-0.25, 0.0, 0.433013), (0.0, 0.0, 0.5),
                            (0.25, 0.0, 0.433013), (0.433013, 0.0, 0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, -0.25),
                            (0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (-0.25, 0.0, -0.433013), (-0.433013, 0.0, -0.25),
                            (-0.5, 0.0, 0.0)),
                           ((-0.5, 0.0, 0.0), (-0.433013, 0.0, 0.25), (-0.25, 0.0, 0.433013), (0.0, 0.0, 0.5),
                            (0.25, 0.0, 0.433013), (0.433012, 0.0, 0.25), (0.5, 0.0, 0.0), (0.433013, 0.0, -0.25),
                            (0.25, 0.0, -0.433013), (0.0, 0.0, -0.5), (-0.25, 0.0, -0.433013), (-0.433013, 0.0, -0.25),
                            (-0.5, 0.0, 0.0)),
                           ((-0.5, 0.0, 0.0), (-0.5, 0.0, 0.0)), ((0.5, 0.0, 0.0), (0.5, 0.0, 0.0)),
                           ((0.0, 0.0, -0.5), (0.0, 0.0, -0.5)), ((0.0, 0.0, 0.5), (0.0, 0.0, 0.5))]

    return cylinder_vertices, cylinder_faces, cylinder_wire_lines


def draw_polygon_object(mat, vertices, faces, face_color, draw_faces, draw_wires,
                        wire_lines=None, wire_color=(0, 0, 0), face_transforms=None, wire_transforms=None):
    """
    Draw a collider polygon object. It takes matrix, vertices (coordinates),
    faces (vertex index references), face color (RGB), faces drawing state (bool),
    wires drawing state (bool) and optional values wire lines (list of lists
    of vertex positions resulting in closed lines), wire color (RGB),
    face transformations (list of vertex indices)
    and wire transformations (list of vertex indices).
    :param mat:
    :param vertices:
    :param faces:
    :param face_color:
    :param draw_faces:
    :param draw_wires:
    :param wire_lines:
    :param wire_color:
    :param face_transforms:
    :param wire_transforms:
    :return:
    """

    if draw_faces:
        color = (face_color[0], face_color[1], face_color[2], 1.0)
        for face in faces:
            face_vert_count = len(face)
            if face_vert_count == 3:  # only one triangle
                for vert in face:
                    if face_transforms:
                        trans = mat
                        for transformation in face_transforms:
                            if vert in transformation[1]:
                                trans = trans @ transformation[0]
                        append_tris_vertex(trans @ Vector(vertices[vert]), color)
                    else:
                        append_tris_vertex(mat @ Vector(vertices[vert]), color)
            else:  # fan like triangles
                i = 1
                while i < face_vert_count - 1:
                    for vert_i in (i, i + 1, 0):
                        vert = face[vert_i]
                        if face_transforms:
                            trans = mat
                            for transformation in face_transforms:
                                if vert in transformation[1]:
                                    trans = trans @ transformation[0]
                            append_tris_vertex(trans @ Vector(vertices[vert]), color)
                        else:
                            append_tris_vertex(mat @ Vector(vertices[vert]), color)
                    i += 1

    if draw_wires:
        color = (wire_color[0], wire_color[1], wire_color[2], 1.0)
        if wire_lines:
            # DRAW CUSTOM LINES
            vert_i_global = 0
            for line in wire_lines:
                for vert_i, vert1 in enumerate(line):
                    if vert_i + 1 < len(line):
                        vert2 = line[vert_i + 1]
                    else:
                        continue

                    # SEPARATE PART TRANSFORMATIONS
                    if wire_transforms:
                        trans1 = trans2 = mat
                        for transformation in wire_transforms:
                            if vert_i_global in transformation[1]:
                                trans1 = trans1 @ transformation[0]
                            if vert_i_global + 1 in transformation[1]:
                                trans2 = trans2 @ transformation[0]
                        append_line_vertex(trans1 @ Vector(vert1), color, is_stipple=True)
                        append_line_vertex(trans2 @ Vector(vert2), color, is_stipple=True)
                    else:
                        append_line_vertex(mat @ Vector(vert1), color, is_stipple=True)
                        append_line_vertex(mat @ Vector(vert2), color, is_stipple=True)
                    vert_i_global += 1
                vert_i_global += 1
        else:
            lines_to_draw = set()
            for face in faces:
                for vert_i, vert1 in enumerate(face):
                    if vert_i + 1 == len(face):
                        vert2 = face[0]
                    else:
                        vert2 = face[vert_i + 1]

                    if (vert1, vert2) in lines_to_draw or (vert2, vert1) in lines_to_draw:
                        continue

                    lines_to_draw.add((vert1, vert2))

            for vert1, vert2 in lines_to_draw:
                if face_transforms:
                    trans1 = mat
                    trans2 = mat
                    vec1 = Vector(vertices[vert1])
                    vec2 = Vector(vertices[vert2])
                    for transformation in face_transforms:
                        if vert1 in transformation[1]:
                            trans1 = trans1 @ transformation[0]
                        if vert2 in transformation[1]:
                            trans2 = trans2 @ transformation[0]
                    append_line_vertex((trans1 @ vec1), color, is_stipple=True)
                    append_line_vertex((trans2 @ vec2), color, is_stipple=True)
                else:
                    append_line_vertex(mat @ Vector(vertices[vert1]), color, is_stipple=True)
                    append_line_vertex(mat @ Vector(vertices[vert2]), color, is_stipple=True)


def draw_point(vector, color, size):
    """Draw point on given vector, with given color

    :param vector: position vector of point in Blender coordinates
    :type vector: mathutils.Vector
    :param color: tuple of RGB color
    :type color: tuple
    :param size: size of point
    :type size: float
    """

    append_point_vertex(vector, color, size)


def draw_circle(radius, steps, mat, scs_globals):
    """
    Draw a horizontal circle of given radius and using given number of steps.
    :param radius:
    :param steps:
    :param mat:
    :param scs_globals:
    :return:
    """
    import math

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    first_a = 0
    append_line_vertex((mat @ Vector((0 + radius * math.cos(first_a), 0 + radius * math.sin(first_a), 0.0))), color)

    for step in range(steps - 1):
        a = (math.pi * 2 / steps) * (step + 1)
        append_line_vertex((mat @ Vector((0 + radius * math.cos(a), 0 + radius * math.sin(a), 0.0))), color, is_strip=True)

    append_line_vertex((mat @ Vector((0 + radius * math.cos(first_a), 0 + radius * math.sin(first_a), 0.0))), color)


def draw_shape_x_axis(mat, size):
    """
    Draws X axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    color = (1.0, 0.2, 0.2, 1.0)
    append_line_vertex((mat @ Vector((size, 0.0, 0.0))), color)
    append_line_vertex((mat @ Vector((0.25, 0.0, 0.0))), color)
    color = (0.5, 0.0, 0.0, 1.0)
    append_line_vertex((mat @ Vector((-0.25, 0.0, 0.0))), color)
    append_line_vertex((mat @ Vector((size * -1, 0.0, 0.0))), color)


def draw_shape_y_axis(mat, size):
    """
    Draws Y axis for "Locator".
    :param mat:
    :param size
    :return:
    """
    color = (0.2, 1.0, 0.2, 1.0)
    append_line_vertex((mat @ Vector((0.0, size, 0.0))), color)
    append_line_vertex((mat @ Vector((0.0, 0.25, 0.0))), color)
    color = (0.0, 0.5, 0.0, 1.0)
    append_line_vertex((mat @ Vector((0.0, -0.25, 0.0))), color)
    append_line_vertex((mat @ Vector((0.0, size * -1, 0.0))), color)


def draw_shape_y_axis_neg(mat, size):
    """
    Draws negative Y axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    color = (0.0, 0.5, 0.0, 1.0)
    append_line_vertex((mat @ Vector((0.0, -0.25, 0.0))), color)
    append_line_vertex((mat @ Vector((0.0, size * -1, 0.0))), color)


def draw_shape_z_axis(mat, size):
    """
    Draws Z axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    color = (0.2, 0.2, 1.0, 1.0)
    append_line_vertex((mat @ Vector((0.0, 0.0, size))), color)
    append_line_vertex((mat @ Vector((0.0, 0.0, 0.25))), color)
    color = (0.0, 0.0, 0.5, 1.0)
    append_line_vertex((mat @ Vector((0.0, 0.0, -0.25))), color)
    append_line_vertex((mat @ Vector((0.0, 0.0, size * -1))), color)


def draw_shape_z_axis_neg(mat, size):
    """
    Draws negative Z axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    color = (0.0, 0.0, 0.5, 1.0)
    append_line_vertex((mat @ Vector((0.0, 0.0, -0.25))), color)
    append_line_vertex((mat @ Vector((0.0, 0.0, size * -1))), color)


def draw_shape_line(line, stipple, is_map_line, scs_globals):
    """Draw line from loc_0 to loc_1 with specified colors of the ends ("line_colorX").
    There is also middle point loc_btw which separates color sides

    :param line: with entries: ("line_color0" : (float, float, float)),
    "(line_color1" : (float, float, float)), ("loc_0" : (float, float, float)),
    ("loc_1" : (float, float, float)),
    ("loc_btw" : (float, float, float))
    :type line: dict
    :param stipple: flag indicating if line should be stipple or not
    :type stipple: bool
    :param is_map_line: boolean indicating if line is map line; if false it means it's trigger line
    :type is_map_line: bool
    :param scs_globals: SCS globals
    :type scs_globals: io_scs_tools.properties.world.GlobalSCSProps
    :return:
    :rtype:
    """
    if 'line_color0' in line:
        color0 = tuple(line['line_color0']) + (1.0,)
    else:
        if is_map_line:
            color0 = (scs_globals.mp_connection_base_color.r,
                      scs_globals.mp_connection_base_color.g,
                      scs_globals.mp_connection_base_color.b,
                      1.0)
        else:
            color0 = (scs_globals.tp_connection_base_color.r,
                      scs_globals.tp_connection_base_color.g,
                      scs_globals.tp_connection_base_color.b,
                      1.0)

    if 'line_color1' in line:
        color1 = tuple(line['line_color1']) + (1.0,)
    else:
        if is_map_line:
            color1 = (scs_globals.mp_connection_base_color.r,
                      scs_globals.mp_connection_base_color.g,
                      scs_globals.mp_connection_base_color.b,
                      1.0)
        else:
            color1 = (scs_globals.tp_connection_base_color.r,
                      scs_globals.tp_connection_base_color.g,
                      scs_globals.tp_connection_base_color.b,
                      1.0)

    append_line_vertex(line['loc_0'], color0, is_stipple=stipple)
    append_line_vertex(line['loc_btw'], color0, is_stipple=stipple)
    append_line_vertex(line['loc_btw'], color1, is_stipple=stipple)
    append_line_vertex(line['loc_1'], color1, is_stipple=stipple)


def draw_shape_curve(curve, stipple, scs_globals):
    """Draw curve from location points of dictionary entry "curve_points" with specified step
    in entry "curve_steps".
    First half of points will be drawn with color specified in "curve_color0" and second half
    of points will be drawn with color specified in "curve_color1"

    :param curve: with entries: ("curve_points" : list of locations),
    ("curve_steps" : int),
    ("curve_color0" : (float, float, float)),
    ("curve_color1" : (float, float, float)),
    :type curve: dict
    :param stipple: flag indicating if line should be stipple or not
    :type stipple: bool
    :param scs_globals: SCS globals
    :type scs_globals: io_scs_tools.properties.world.GlobalSCSProps
    :return:
    :rtype:
    """
    if 'curve_color0' in curve:
        color0 = tuple(curve['curve_color0']) + (1.0,)
    else:
        color0 = (scs_globals.np_connection_base_color.r,
                  scs_globals.np_connection_base_color.g,
                  scs_globals.np_connection_base_color.b,
                  1.0)

    if 'curve_color1' in curve:
        color1 = tuple(curve['curve_color1']) + (1.0,)
    else:
        color1 = (scs_globals.np_connection_base_color.r,
                  scs_globals.np_connection_base_color.g,
                  scs_globals.np_connection_base_color.b,
                  1.0)

    real_color = color0

    last_item_i = len(curve['curve_points']) - 1
    for vec_i, vec in enumerate(curve['curve_points']):
        if vec_i == int(curve['curve_steps'] / 2 + 1.5):  # if vec_i > curve['curve_steps'] / 2 and switch:
            real_color = color1

        if vec_i == 0 or vec_i == last_item_i:
            append_line_vertex(vec, real_color, is_stipple=stipple)
        else:
            append_line_vertex(vec, real_color, is_strip=True, is_stipple=stipple)


def draw_text(text, font_id, x, y):
    """Draws given text at x,y position.

    :param text: text to be drawn
    :type text: str
    :param font_id: font id with which text should be drawn
    :type font_id: int
    :param x: x position in 3d view region
    :type x: float
    :param y: y position in 3d view region
    :type y: float
    """

    # static offset to move from origin
    x += 15.0
    y += -4.0

    blf.position(font_id, x, y, 0.0)
    blf.draw(font_id, text)


def draw_rect_2d(positions, color):
    """Draw 2D rectangle with given color. Use it to draw in SpaceView3D on 'POST_PIXEL'.

    :param positions: 2D position in the region, that we want to draw to.
    :type positions: tuple(int, int)
    :param color: RGBA of rectangle
    :type color: tuple(float, float, float, float)
    """
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": positions,
        },
    )
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
