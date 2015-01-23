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

import blf
import bpy
from bgl import (glEnable, glDisable, glColor3f, glVertex3f, glPointSize,
                 glLineWidth, glBegin, glEnd, GL_POINTS,
                 GL_LINE_STRIP, GL_LINES, GL_LINE_LOOP, GL_POLYGON, GL_LINE_STIPPLE)
from mathutils import Vector


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
        for face in faces:
            glBegin(GL_POLYGON)
            glColor3f(face_color[0], face_color[1], face_color[2])
            for vert in face:
                if face_transforms:
                    trans = mat
                    for transformation in face_transforms:
                        if vert in transformation[1]:
                            trans = trans * transformation[0]
                    glVertex3f(*(trans * Vector(vertices[vert])))
                else:
                    glVertex3f(*(mat * Vector(vertices[vert])))
            glEnd()
    if draw_wires:
        if wire_lines:

            # DRAW CUSTOM LINES
            vert_i_global = 0
            for line in wire_lines:
                # glLineWidth(2.0)
                glEnable(GL_LINE_STIPPLE)
                glBegin(GL_LINES)
                glColor3f(wire_color[0], wire_color[1], wire_color[2])

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
                                trans1 = trans1 * transformation[0]
                            if vert_i_global + 1 in transformation[1]:
                                trans2 = trans2 * transformation[0]
                        glVertex3f(*(trans1 * Vector(vert1)))
                        glVertex3f(*(trans2 * Vector(vert2)))
                    else:
                        glVertex3f(*(mat * Vector(vert1)))
                        glVertex3f(*(mat * Vector(vert2)))
                    vert_i_global += 1
                vert_i_global += 1
                glEnd()
                glDisable(GL_LINE_STIPPLE)
                # glLineWidth(1.0)
        else:
            for face in faces:
                # glLineWidth(2.0)
                glEnable(GL_LINE_STIPPLE)
                glBegin(GL_LINES)
                glColor3f(wire_color[0], wire_color[1], wire_color[2])
                for vert_i, vert1 in enumerate(face):
                    if vert_i + 1 == len(face):
                        vert2 = face[0]
                    else:
                        vert2 = face[vert_i + 1]
                    if face_transforms:
                        trans1 = mat
                        trans2 = mat
                        vec1 = Vector(vertices[vert1])
                        vec2 = Vector(vertices[vert2])
                        for transformation in face_transforms:
                            if vert1 in transformation[1]:
                                trans1 = trans1 * transformation[0]
                            if vert2 in transformation[1]:
                                trans2 = trans2 * transformation[0]
                        glVertex3f(*(trans1 * vec1))
                        glVertex3f(*(trans2 * vec2))
                    else:
                        glVertex3f(*(mat * Vector(vertices[vert1])))
                        glVertex3f(*(mat * Vector(vertices[vert2])))
                glEnd()
                glDisable(GL_LINE_STIPPLE)
                # glLineWidth(1.0)
    if 0:  # DEBUG: draw points from faces geometry
        glPointSize(3.0)
        glBegin(GL_POINTS)
        glColor3f(0.5, 0.5, 1)
        for vertex_i, vertex in enumerate(vertices):
            vec = Vector(vertex)
            if face_transforms:
                trans = mat
                for transformation in face_transforms:
                    if vertex_i in transformation[1]:
                        trans = trans * transformation[0]
                glVertex3f(*(trans * vec))
            else:
                glVertex3f(*(mat * vec.to_3d()))
        glEnd()
        glPointSize(1.0)
    if 0:  # DEBUG: draw points from lines geometry
        if wire_lines:
            glPointSize(3.0)
            glBegin(GL_POINTS)
            glColor3f(1, 0, 0.5)
            vert_i_global = 0
            for line in wire_lines:
                for vert_i, vertex in enumerate(line):
                    if vert_i + 1 < len(line):
                        vec = Vector(vertex)
                    else:
                        continue
                    if wire_transforms:
                        trans = mat
                        for transformation in wire_transforms:
                            if vert_i_global in transformation[1]:
                                trans = trans * transformation[0]
                        glVertex3f(*(trans * vec.to_3d()))
                    else:
                        glVertex3f(*(mat * vec.to_3d()))
                    vert_i_global += 1
                vert_i_global += 1
            glEnd()
            glPointSize(1.0)


def draw_circle(radius, steps, mat, scene_scs_props):
    """
    Draw a horizontal circle of given radius and using given number of steps.
    :param radius:
    :param steps:
    :param mat:
    :param scene_scs_props:
    :return:
    """
    import math

    glBegin(GL_LINE_LOOP)
    glColor3f(scene_scs_props.locator_prefab_wire_color.r,
              scene_scs_props.locator_prefab_wire_color.g,
              scene_scs_props.locator_prefab_wire_color.b)
    for step in range(steps):
        a = (math.pi * 2 / steps) * step
        glVertex3f(*(mat * Vector((0 + radius * math.cos(a), 0 + radius * math.sin(a), 0.0))))
    glEnd()


def draw_shape_x_axis(mat, size):
    """
    Draws X axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.2, 0.2)
    glVertex3f(*(mat * Vector((size, 0.0, 0.0))))
    glVertex3f(*(mat * Vector((0.25, 0.0, 0.0))))
    glColor3f(0.5, 0.0, 0.0)
    glVertex3f(*(mat * Vector((-0.25, 0.0, 0.0))))
    glVertex3f(*(mat * Vector((size * -1, 0.0, 0.0))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_y_axis(mat, size):
    """
    Draws Y axis for "Locator".
    :param mat:
    :param size
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(0.2, 1.0, 0.2)
    glVertex3f(*(mat * Vector((0.0, size, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.25, 0.0))))
    glColor3f(0.0, 0.5, 0.0)
    glVertex3f(*(mat * Vector((0.0, -0.25, 0.0))))
    glVertex3f(*(mat * Vector((0.0, size * -1, 0.0))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_y_axis_neg(mat, size):
    """
    Draws negative Y axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(0.0, 0.5, 0.0)
    glVertex3f(*(mat * Vector((0.0, -0.25, 0.0))))
    glVertex3f(*(mat * Vector((0.0, size * -1, 0.0))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_z_axis(mat, size):
    """
    Draws Z axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(0.2, 0.2, 1.0)
    glVertex3f(*(mat * Vector((0.0, 0.0, size))))
    glVertex3f(*(mat * Vector((0.0, 0.0, 0.25))))
    glColor3f(0.0, 0.0, 0.5)
    glVertex3f(*(mat * Vector((0.0, 0.0, -0.25))))
    glVertex3f(*(mat * Vector((0.0, 0.0, size * -1))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_z_axis_neg(mat, size):
    """
    Draws negative Z axis for "Locator".
    :param mat:
    :param size:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.5)
    glVertex3f(*(mat * Vector((0.0, 0.0, -0.25))))
    glVertex3f(*(mat * Vector((0.0, 0.0, size * -1))))
    glEnd()
    glLineWidth(1.0)


def draw_shape_line(line, stipple, is_map_line):
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
    :return:
    :rtype:
    """
    if 'line_color0' in line:
        color0 = line['line_color0']
    else:
        if is_map_line:
            color0 = (bpy.context.scene.scs_props.mp_connection_base_color.r,
                      bpy.context.scene.scs_props.mp_connection_base_color.g,
                      bpy.context.scene.scs_props.mp_connection_base_color.b)
        else:
            color0 = (bpy.context.scene.scs_props.tp_connection_base_color.r,
                      bpy.context.scene.scs_props.tp_connection_base_color.g,
                      bpy.context.scene.scs_props.tp_connection_base_color.b)

    if 'line_color1' in line:
        color1 = line['line_color1']
    else:
        if is_map_line:
            color1 = (bpy.context.scene.scs_props.mp_connection_base_color.r,
                      bpy.context.scene.scs_props.mp_connection_base_color.g,
                      bpy.context.scene.scs_props.mp_connection_base_color.b)
        else:
            color1 = (bpy.context.scene.scs_props.tp_connection_base_color.r,
                      bpy.context.scene.scs_props.tp_connection_base_color.g,
                      bpy.context.scene.scs_props.tp_connection_base_color.b)

    if stipple:
        glEnable(GL_LINE_STIPPLE)
    glBegin(GL_LINES)
    glColor3f(color0[0], color0[1], color0[2])
    glVertex3f(*line['loc_0'])
    glVertex3f(*line['loc_btw'])
    glColor3f(color1[0], color1[1], color1[2])
    glVertex3f(*line['loc_btw'])
    glVertex3f(*line['loc_1'])
    glEnd()
    if stipple:
        glDisable(GL_LINE_STIPPLE)


def draw_shape_curve(curve, stipple):
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
    :return:
    :rtype:
    """
    if 'curve_color0' in curve:
        color0 = curve['curve_color0']
    else:
        color0 = (bpy.context.scene.scs_props.np_connection_base_color.r,
                  bpy.context.scene.scs_props.np_connection_base_color.g,
                  bpy.context.scene.scs_props.np_connection_base_color.b)

    if 'curve_color1' in curve:
        color1 = curve['curve_color1']
    else:
        color1 = (bpy.context.scene.scs_props.np_connection_base_color.r,
                  bpy.context.scene.scs_props.np_connection_base_color.g,
                  bpy.context.scene.scs_props.np_connection_base_color.b)

    glColor3f(color0[0], color0[1], color0[2])

    if stipple:
        glEnable(GL_LINE_STIPPLE)
    # switch = 1
    glBegin(GL_LINE_STRIP)
    for vec_i, vec in enumerate(curve['curve_points']):
        if vec_i == int(curve['curve_steps'] / 2 + 1.5):  # if vec_i > curve['curve_steps'] / 2 and switch:
            glColor3f(color1[0], color1[1], color1[2])
            # switch = 0
        glVertex3f(*vec)
    glEnd()
    if stipple:
        glDisable(GL_LINE_STIPPLE)


def draw_text(text, font_id, vec, region_data, x_offset=0, y_offset=0):
    """

    :param text:
    :type text:
    :param vec:
    :type vec:
    :param font_id:
    :type font_id:
    :param region_data: (region3d_perspective_matrix, region2d_mid_width, region2d_mid_height)
    :type region_data: tuple
    :param x_offset:
    :type x_offset:
    :param y_offset:
    :type y_offset:
    :return:
    :rtype:
    """
    vec_4d = region_data[0] * vec.to_4d()
    if vec_4d.w > 0.0:
        x = region_data[1] + region_data[1] * (vec_4d.x / vec_4d.w)
        y = region_data[2] + region_data[2] * (vec_4d.y / vec_4d.w)

        blf.position(font_id, x + 15.0 + x_offset, y - 4.0 + y_offset, 0.0)
        blf.draw(font_id, text)


'''
def draw_matrix(mat):
    """
    Draw Matrix lines.
    :param mat:
    :return:
    """
    zero_tx = mat * zero

    glLineWidth(2.0)

    # X
    glColor3f(1.0, 0.2, 0.2)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * x_p))
    glEnd()

    glColor3f(0.6, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * x_n))
    glEnd()

    ## Y
    glColor3f(0.2, 1.0, 0.2)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * y_p))
    glEnd()

    glColor3f(0.0, 0.6, 0.0)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * y_n))
    glEnd()

    ## Z
    glColor3f(0.2, 0.2, 1.0)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * z_p))
    glEnd()

    glColor3f(0.0, 0.0, 0.6)
    glBegin(GL_LINES)
    glVertex3f(*zero_tx)
    glVertex3f(*(mat * z_n))
    glEnd()

    ## BOUNDING BOX
    i = 0
    glColor3f(1.0, 1.0, 1.0)
    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            for z in (-1.0, 1.0):
                bb[i][:] = x, y, z
                bb[i] = mat * bb[i]
                i += 1

    ## STRIP
    glLineWidth(1.0)
    glLineStipple(1, 0xAAAA)
    glEnable(GL_LINE_STIPPLE)

    glBegin(GL_LINE_STRIP)
    for i in 0, 1, 3, 2, 0, 4, 5, 7, 6, 4:
        glVertex3f(*bb[i])
    pnt = mat * Vector((0.75, -0.75, -0.75))
    glVertex3f(pnt[0], pnt[1], pnt[2])
    glEnd()

    ## NOT DONE BY THE STRIP
    glBegin(GL_LINES)
    glVertex3f(*bb[1])
    glVertex3f(*bb[5])

    glVertex3f(*bb[2])
    glVertex3f(*bb[6])

    glVertex3f(*bb[3])
    glVertex3f(*bb[7])
    glEnd()
    glDisable(GL_LINE_STIPPLE)
'''
