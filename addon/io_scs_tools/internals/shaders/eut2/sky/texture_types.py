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


def get():
    """Returns texture types names used in eut2.sky shader.

    :return: set of names
    :rtype: tuple
    """
    return 'Base A', 'Base B', 'Over A', 'Over B'


def get_base_a():
    return get()[0]


def get_base_b():
    return get()[1]


def get_over_a():
    return get()[2]


def get_over_b():
    return get()[3]
