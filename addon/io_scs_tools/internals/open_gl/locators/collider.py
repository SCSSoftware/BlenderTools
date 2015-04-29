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

from io_scs_tools.internals.open_gl import primitive as _primitive
from mathutils import Matrix


def draw_shape_box(mat, obj_scs_props, scene_scs_props):
    """Draw box collider.

    :param mat: Object matrix 4x4
    :type mat: Matrix
    :param obj_scs_props: SCS Object properties
    :type obj_scs_props: prop
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """

    if obj_scs_props.locator_collider_centered:
        shift = 0.0
    else:
        shift = -obj_scs_props.locator_collider_box_y / 2

    mat1 = mat * Matrix.Translation((0.0, shift, 0.0)) * (
        Matrix.Scale(obj_scs_props.locator_collider_box_x, 4, (1.0, 0.0, 0.0)) *
        Matrix.Scale(obj_scs_props.locator_collider_box_y, 4, (0.0, 1.0, 0.0)) *
        Matrix.Scale(obj_scs_props.locator_collider_box_z, 4, (0.0, 0.0, 1.0)))

    cube_vertices, cube_faces, cube_wire_lines = _primitive.get_box_data()

    _primitive.draw_polygon_object(mat1,
                                   cube_vertices,
                                   cube_faces,
                                   scene_scs_props.locator_coll_face_color,
                                   obj_scs_props.locator_collider_faces,
                                   obj_scs_props.locator_collider_wires,
                                   cube_wire_lines,
                                   scene_scs_props.locator_coll_wire_color)


def draw_shape_sphere(mat, obj_scs_props, scene_scs_props):
    """Draw sphere collider.

    :param mat: Object matrix 4x4
    :type mat: Matrix
    :param obj_scs_props: SCS Object properties
    :type obj_scs_props: prop
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """

    if obj_scs_props.locator_collider_centered:
        shift = 0.0
    else:
        shift = -obj_scs_props.locator_collider_dia / 2
    mat1 = mat * Matrix.Translation((0.0, shift, 0.0)) * Matrix.Scale(obj_scs_props.locator_collider_dia, 4)

    sphere_vertices, sphere_faces, sphere_wire_lines = _primitive.get_sphere_data()

    _primitive.draw_polygon_object(mat1,
                                   sphere_vertices,
                                   sphere_faces,
                                   scene_scs_props.locator_coll_face_color,
                                   obj_scs_props.locator_collider_faces,
                                   obj_scs_props.locator_collider_wires,
                                   sphere_wire_lines,
                                   scene_scs_props.locator_coll_wire_color)


def draw_shape_capsule(mat, obj_scs_props, scene_scs_props):
    """Draw capsule collider.

    :param mat: Object matrix 4x4
    :type mat: Matrix
    :param obj_scs_props: SCS Object properties
    :type obj_scs_props: prop
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """

    if obj_scs_props.locator_collider_centered:
        shift = obj_scs_props.locator_collider_len / 2
    else:
        shift = 0.0
    mat1 = Matrix.Translation((0.0, shift, 0.0)) * Matrix.Scale(obj_scs_props.locator_collider_dia, 4)
    mat2 = Matrix.Translation((0.0, shift - obj_scs_props.locator_collider_len, 0.0)) * Matrix.Scale(obj_scs_props.locator_collider_dia, 4)

    capsule_vertices, capsule_faces, capsule_wire_lines = _primitive.get_capsule_data()

    face_transforms = []
    vertices = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44)
    face_transforms.append((mat1, vertices), )
    vertices = (45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
                73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89)
    face_transforms.append((mat2, vertices), )

    wire_transforms = []
    vertices = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 26, 27, 28, 29, 30, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 59, 60, 61, 62, 63)
    wire_transforms.append((mat1, vertices), )
    vertices = (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 36, 37, 38, 39, 50, 51, 52, 53, 54, 55, 56, 57, 58)
    wire_transforms.append((mat2, vertices), )

    _primitive.draw_polygon_object(mat,
                                   capsule_vertices,
                                   capsule_faces,
                                   scene_scs_props.locator_coll_face_color,
                                   obj_scs_props.locator_collider_faces,
                                   obj_scs_props.locator_collider_wires,
                                   capsule_wire_lines,
                                   scene_scs_props.locator_coll_wire_color,
                                   face_transforms,
                                   wire_transforms)


def draw_shape_cylinder(mat, obj_scs_props, scene_scs_props):
    """Draw cylinder collider.

    :param mat: Object matrix 4x4
    :type mat: Matrix
    :param obj_scs_props: SCS Object properties
    :type obj_scs_props: prop
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """

    if obj_scs_props.locator_collider_centered:
        shift = obj_scs_props.locator_collider_len / 2
    else:
        shift = 0.0
    mat1 = Matrix.Translation((0.0, shift, 0.0)) * Matrix.Scale(obj_scs_props.locator_collider_dia, 4)
    mat2 = Matrix.Translation((0.0, shift - obj_scs_props.locator_collider_len, 0.0)) * Matrix.Scale(obj_scs_props.locator_collider_dia, 4)

    cylinder_vertices, cylinder_faces, cylinder_wire_lines = _primitive.get_cylinder_data()

    face_transforms = []
    vertices = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    face_transforms.append((mat1, vertices), )
    vertices = (12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
    face_transforms.append((mat2, vertices), )

    wire_transforms = []
    vertices = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 26, 28, 30, 32)
    wire_transforms.append((mat1, vertices), )
    vertices = (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 29, 31, 33)
    wire_transforms.append((mat2, vertices), )

    _primitive.draw_polygon_object(mat,
                                   cylinder_vertices,
                                   cylinder_faces,
                                   scene_scs_props.locator_coll_face_color,
                                   obj_scs_props.locator_collider_faces,
                                   obj_scs_props.locator_collider_wires,
                                   cylinder_wire_lines,
                                   scene_scs_props.locator_coll_wire_color,
                                   face_transforms,
                                   wire_transforms)


def draw_shape_convex(mat, obj_scs_props, scene_scs_props):
    """Draw convex collider.

    :param mat: Object matrix 4x4
    :type mat: Matrix
    :param obj_scs_props: SCS Object properties
    :type obj_scs_props: prop
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """
    verts = obj_scs_props.get("coll_convex_verts", None)
    faces = obj_scs_props.get("coll_convex_faces", None)

    if verts and faces:
        _primitive.draw_polygon_object(mat,
                                       verts,
                                       faces,
                                       scene_scs_props.locator_coll_face_color,
                                       obj_scs_props.locator_collider_faces,
                                       obj_scs_props.locator_collider_wires,
                                       None,
                                       scene_scs_props.locator_coll_wire_color)


def draw_collision_locator(obj, scene_scs_props):
    """Draw Collision locator.

    :param obj: Blender Object
    :type obj: Object
    :param scene_scs_props: Blender Scene properties
    :type scene_scs_props: prop
    """

    tran, rot, sca = obj.matrix_world.decompose()
    mat_orig = Matrix.Translation(tran).to_4x4() * rot.to_matrix().to_4x4()

    if obj.scs_props.locator_collider_type == 'Box':
        draw_shape_box(mat_orig, obj.scs_props, scene_scs_props)
    if obj.scs_props.locator_collider_type == 'Sphere':
        draw_shape_sphere(mat_orig, obj.scs_props, scene_scs_props)
    if obj.scs_props.locator_collider_type == 'Capsule':
        draw_shape_capsule(mat_orig, obj.scs_props, scene_scs_props)
    if obj.scs_props.locator_collider_type == 'Cylinder':
        draw_shape_cylinder(mat_orig, obj.scs_props, scene_scs_props)
    if obj.scs_props.locator_collider_type == 'Convex':
        draw_shape_convex(mat_orig, obj.scs_props, scene_scs_props)