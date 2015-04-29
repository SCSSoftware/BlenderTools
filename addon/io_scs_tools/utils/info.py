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

import bpy


def get_tools_version():
    return 0.5


def get_blender_version():
    """Returns Blender's version and the build identifications as strings.

    :return: Blender's version number and its build identification as two formated strings
    :rtype: tuple(str, str)
    """
    b_ver = bpy.app.version
    b_ver_str = str(str(b_ver[0]) + "." + str(b_ver[1]) + "." + str(b_ver[2]))
    if b_ver[0] == 2 and b_ver[1] <= 69:
        build_str = str(" (r" + str(bpy.app.build_revision)[2:-1] + ")")
    else:
        build_str = str(" (hash: " + str(bpy.app.build_hash)[2:-1] + ")")
    return b_ver_str, build_str


