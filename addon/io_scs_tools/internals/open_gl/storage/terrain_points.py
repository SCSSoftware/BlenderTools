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

_terrain_points = {}


def add(position, is_visible):
    """Adds new terrain point to the storage for drawing.

    :param position: position of terrain point
    :type position: mathutils.Vector
    :param is_visible: boolean indicating wheather mesh belonging terrain point is currently visible
    :type is_visible: bool
    """
    key = str(position)
    if key not in _terrain_points:
        _terrain_points[key] = (position, (1, 1, 0, 1) if is_visible else (0.5, 0.5, 0, 1))


def clear():
    """Clear terrain points storage for drawing.
    """
    _terrain_points.clear()


def is_emtpy():
    """Tells if terrain point storage is empty.

    :return: True if empty; False otherwise
    :rtype: bool
    """
    return len(_terrain_points) == 0


def get_positions_and_colors():
    """Gets list of tuples representing positions and colors of terrian points.

    :return: list of positions and colors
    :rtype: list[tuple[mathutils.Vector, tuple]]
    """
    return _terrain_points.values()
