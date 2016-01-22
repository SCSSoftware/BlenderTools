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

# Copyright (C) 2013-2014: SCS Software

from bgl import (glEnable, glDisable, glColor3f, glVertex3f, glPointSize,
                 glLineWidth, glBegin, glEnd, GL_POINTS,
                 GL_LINE_STRIP, GL_LINES, GL_LINE_LOOP, GL_LINE_STIPPLE)

from io_scs_tools.internals.open_gl import primitive as _primitive
from mathutils import Vector, Matrix


def draw_shape_control_node(mat, scs_globals):
    """Draws shape for "Locator" of "Control Node" type.

    :param mat:
    :param scs_globals:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(scs_globals.locator_prefab_wire_color.r,
              scs_globals.locator_prefab_wire_color.g,
              scs_globals.locator_prefab_wire_color.b)
    glVertex3f(*(mat * Vector((0.0, scs_globals.locator_empty_size, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((-0.15, 0.45, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((0.15, 0.45, 0.0))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_sign(mat, scs_globals):
    """
    Draws shape for "Locator" of "Sign" type.
    :param mat:
    :param scs_globals:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(scs_globals.locator_prefab_wire_color.r,
              scs_globals.locator_prefab_wire_color.g,
              scs_globals.locator_prefab_wire_color.b)
    glVertex3f(*(mat * Vector((0.0, 0.0, scs_globals.locator_empty_size))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.45))))
    glEnd()
    glBegin(GL_LINE_STRIP)
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.75))))
    glVertex3f(*(mat * Vector((0.1299, 0.0, 0.675))))
    glVertex3f(*(mat * Vector((0.1299, 0.0, 0.525))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.45))))
    glVertex3f(*(mat * Vector((-0.1299, 0.0, 0.525))))
    glVertex3f(*(mat * Vector((-0.1299, 0.0, 0.675))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.75))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_spawn_point(mat, scs_globals):
    """
    Draws shape for "Locator" of "Spawn Point" type.
    :param mat:
    :param scs_globals:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(scs_globals.locator_prefab_wire_color.r,
              scs_globals.locator_prefab_wire_color.g,
              scs_globals.locator_prefab_wire_color.b)
    glVertex3f(*(mat * Vector((0.0, 0.0, scs_globals.locator_empty_size))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.75))))
    glVertex3f(*(mat * Vector((-0.1299, 0.0, 0.525))))
    glVertex3f(*(mat * Vector((0.1299, 0.0, 0.675))))
    glVertex3f(*(mat * Vector((0.1299, 0.0, 0.525))))
    glVertex3f(*(mat * Vector((-0.1299, 0.0, 0.675))))
    glVertex3f(*(mat * Vector((0.0, -0.1299, 0.525))))
    glVertex3f(*(mat * Vector((0.0, 0.1299, 0.675))))
    glVertex3f(*(mat * Vector((0.0, 0.1299, 0.525))))
    glVertex3f(*(mat * Vector((0.0, -0.1299, 0.675))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_traffic_light(mat, scs_globals):
    """
    Draws shape for "Locator" of "Traffic Semaphore" type.
    :param mat:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    glColor3f(scs_globals.locator_prefab_wire_color.r,
              scs_globals.locator_prefab_wire_color.g,
              scs_globals.locator_prefab_wire_color.b)
    glVertex3f(*(mat * Vector((0.0, 0.0, scs_globals.locator_empty_size))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.45))))
    glVertex3f(*(mat * Vector((-0.0866, 0.0, 0.5))))
    glVertex3f(*(mat * Vector((-0.0866, 0.0, 0.84))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.89))))
    glVertex3f(*(mat * Vector((0.0866, 0.0, 0.84))))
    glVertex3f(*(mat * Vector((0.0866, 0.0, 0.5))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.45))))
    glEnd()
    for val in (0.5, 0.62, 0.74):
        glBegin(GL_LINE_LOOP)
        glVertex3f(*(mat * Vector((0.0, 0.0, val))))
        glVertex3f(*(mat * Vector((-0.0433, 0.0, 0.025 + val))))
        glVertex3f(*(mat * Vector((-0.0433, 0.0, 0.075 + val))))
        glVertex3f(*(mat * Vector((0.0, 0.0, 0.1 + val))))
        glVertex3f(*(mat * Vector((0.0433, 0.0, 0.075 + val))))
        glVertex3f(*(mat * Vector((0.0433, 0.0, 0.025 + val))))
        glEnd()
    glLineWidth(1.0)


def draw_shape_map_point(mat, scs_globals):
    """
    Draws shape for "Locator" of "Map Point" type.
    :param mat:
    :param scs_globals:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(scs_globals.locator_prefab_wire_color.r,
              scs_globals.locator_prefab_wire_color.g,
              scs_globals.locator_prefab_wire_color.b)
    glVertex3f(*(mat * Vector((-0.17678, -0.17678, 0.17678))))
    glVertex3f(*(mat * Vector((0.17678, 0.17678, -0.17678))))
    glVertex3f(*(mat * Vector((-0.17678, 0.17678, 0.17678))))
    glVertex3f(*(mat * Vector((0.17678, -0.17678, -0.17678))))
    glVertex3f(*(mat * Vector((-0.17678, -0.17678, -0.17678))))
    glVertex3f(*(mat * Vector((0.17678, 0.17678, 0.17678))))
    glVertex3f(*(mat * Vector((-0.17678, 0.17678, -0.17678))))
    glVertex3f(*(mat * Vector((0.17678, -0.17678, 0.17678))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_trigger_point(mat, mat_orig, radius, scs_globals, draw_range):
    """
    Draws shape for "Locator" of "Trigger Point" type.
    :param mat:
    :param mat_orig:
    :param radius:
    :param scs_globals:
    :param draw_range:
    :return:
    """
    glLineWidth(2.0)
    _primitive.draw_circle(0.25, 8, mat, scs_globals)
    _primitive.draw_circle(0.4, 8, mat, scs_globals)
    glEnable(GL_LINE_STIPPLE)
    if draw_range:
        _primitive.draw_circle(radius, 32, mat_orig, scs_globals)
    glDisable(GL_LINE_STIPPLE)
    glLineWidth(1.0)


def draw_prefab_locator(obj, scs_globals):
    """
    Draw Prefab locator.
    :param obj:
    :return:
    """

    size = scs_globals.locator_size
    empty_size = scs_globals.locator_empty_size
    mat_sca = Matrix.Scale(size, 4)
    mat_orig = obj.matrix_world
    mat = mat_orig * mat_sca
    if obj.scs_props.locator_prefab_type == 'Control Node':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis_neg(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_control_node(mat, scs_globals)

        glPointSize(12.0)
        glBegin(GL_POINTS)
        if obj.scs_props.locator_prefab_con_node_index == '0':
            glColor3f(1, 0, 0)
        else:
            glColor3f(0, 1, 0)
        glVertex3f(*(mat * Vector((0.0, 0.0, 0.0))))
        glEnd()
        glPointSize(1.0)

    elif obj.scs_props.locator_prefab_type == 'Sign':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            draw_shape_sign(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Spawn Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            draw_shape_spawn_point(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            draw_shape_traffic_light(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Navigation Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis_neg(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_control_node(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Map Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_map_point(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Trigger Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        is_sphere = obj.scs_props.locator_prefab_tp_sphere_trigger
        draw_shape_trigger_point(mat, mat_orig, obj.scs_props.locator_prefab_tp_range, scs_globals, is_sphere)
