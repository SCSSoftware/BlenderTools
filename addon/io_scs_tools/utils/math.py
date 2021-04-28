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

import math
from mathutils import Vector


def get_distance(loc1, loc2):
    """Get distance between two points

    :param loc1: first location
    :type loc1: mathutils.Vector | tuple
    :param loc2: second location
    :type loc2: mathutils.Vector | tuple
    :return: distance between points
    :rtype: float
    """
    return math.sqrt(((loc1[0] - loc2[0]) ** 2) + ((loc1[1] - loc2[1]) ** 2) + ((loc1[2] - loc2[2]) ** 2))


def middle_point(loc1, loc2):
    """Takes two locations (list or tuple of three floats) and returns their midpoint."""
    return ((loc1[0] + loc2[0]) / 2), ((loc1[1] + loc2[1]) / 2), ((loc1[2] + loc2[2]) / 2)


def evaluate_minmax(vec, min_vec, max_vec):
    """Takes Vector or list of three values and MIN, MAX lists and evaluate its values."""
    for axis in range(3):
        if min_vec[axis] is None or min_vec[axis] > vec[axis]:
            min_vec[axis] = vec[axis]
        if max_vec[axis] is None or max_vec[axis] < vec[axis]:
            max_vec[axis] = vec[axis]
    return min_vec, max_vec


def get_bb(min_vec, max_vec):
    """Takes minimal and maximal values for each axis and returns
    BBox values (width, height, depth) and their center point."""
    bbox = (
        max_vec[0] - min_vec[0],
        max_vec[1] - min_vec[1],
        max_vec[2] - min_vec[2]
    )
    bbcenter = (
        max_vec[0] - ((max_vec[0] - min_vec[0]) / 2),
        max_vec[1] - ((max_vec[1] - min_vec[1]) / 2),
        max_vec[2] - ((max_vec[2] - min_vec[2]) / 2)
    )
    return bbox, bbcenter


def scaling_width_margin(bbox, margin):
    """

    :param bbox:
    :type bbox:
    :param margin:
    :type margin:
    :return:
    :rtype:
    """
    min_scale = 0.01
    scaling = []
    for axis in range(3):
        axis_scale = (bbox[axis] - 2.0 * margin) / bbox[axis]
        if axis_scale < min_scale:
            axis_scale = min_scale
        scaling.append(axis_scale)
    return tuple(scaling)


def angle_normalized_v3v3(v1, v2):
    """
    :param v1:
    :param v2:
    :return:
    """
    if v1.dot(v2) < 0.0:
        vec = Vector(-v2)
        return math.pi - 2.0 * saasin((vec - v1).length / 2.0)
    else:
        return 2.0 * saasin((v2 - v1).length / 2.0)


def saasin(fac):
    """
    :param fac:
    :return:
    """
    if fac <= -1.0:
        return -math.pi / 2.0
    elif fac >= 1.0:
        return math.pi / 2.0
    else:
        return math.asin(fac)


def clamp(value, min_value=0, max_value=1):
    """Clamp value to given interval. Default interval is [0,1].

    :param value: value to clamp
    :type value: float|int
    :param min_value: minimum value allowed
    :type min_value: float|int
    :param max_value: maximum value allowed
    :type max_value: float|int
    :return: clamped value
    :rtype: float|int
    """
    assert min_value < max_value

    return min(max_value, max(min_value, value))
