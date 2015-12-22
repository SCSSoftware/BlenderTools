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


def get_combined_ver_str():
    """Returns combined version string from Blender version and Blender Tools version.
    :return: combined version string
    :rtype: str
    """
    from io_scs_tools import get_tools_version

    (version, build) = get_blender_version()
    return "Blender " + version + build + ", SCS Blender Tools: " + get_tools_version()


def cmp_ver_str(version_str, version_str2):
    """Compers two version string of format "X.X.X..." where X is number.

    :param version_str: version string to check (should be in format: "X.Y" where X and Y are version numbers)
    :type version_str: str
    :return: -1 if first is greater; 0 if equal; 1 if second is greater;
    :rtype: int
    """

    version_str = version_str.split(".")
    version_str2 = version_str2.split(".")

    ver_cmp = []
    for ver_i in range(0, 2):
        if version_str[ver_i] < version_str2[ver_i]:
            ver_cmp.append(-1)
        elif version_str[ver_i] == version_str2[ver_i]:
            ver_cmp.append(0)
        else:
            ver_cmp.append(1)

        ver_i += 1

    # first version smaller than second
    if ver_cmp[0] < 0 or (ver_cmp[0] == 0 and ver_cmp[1] <= 0):
        return -1

    # equal versions
    if ver_cmp[0] == 0 and ver_cmp[1] == 0:
        return 0

    # otherwise we directly assume that second is greater
    return 1
