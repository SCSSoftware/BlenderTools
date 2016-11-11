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
from io_scs_tools import bl_info


def __get_bl_info_version__(key):
    """Gets version string from bl_info dictonary for given key.

    :param key: key in bl_info contaning version tuple (X, X, X, ..) where X is int number
    :type key: str
    :return: string representation of bl_info dictionary value for given key
    :rtype: str
    """
    ver = ""
    for ver_num in bl_info[key]:
        ver += str(ver_num) + "."
    return ver[:-1]


def get_tools_version():
    """Returns Blender Tools version as string from bl_info["version"] dictonary value.

    :return: string representation of bl_info["version"] tuple
    :rtype: str
    """
    return __get_bl_info_version__("version")


def get_required_blender_version():
    """Returns required Blender version as string from bl_info["blender"] dictonary value.

    :return: string representation of bl_info["blender"] tuple
    :rtype: str
    """
    return __get_bl_info_version__("blender")


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


def get_combined_ver_str(only_version_numbers=False):
    """Returns combined version string from Blender version and Blender Tools version.

    :param only_version_numbers: True to return only versions without "Blender" and "SCS Blender Tools" strings
    :type only_version_numbers: bool
    :return: combined version string
    :rtype: str
    """
    (version, build) = get_blender_version()
    if only_version_numbers:
        return version + build + ", " + get_tools_version()
    else:
        return "Blender " + version + build + ", SCS Blender Tools: " + get_tools_version()


def is_blender_able_to_run_tools():
    """Tells if Blender version is good enough to run Blender Tools.

    :return: True if current blender version meets required version for Blender Tools; False otherwise
    :rtype: bool
    """
    return cmp_ver_str(bpy.app.version_string, get_required_blender_version()) > -1


def cmp_ver_str(version_str, version_str2):
    """Compers two version string of format "X.X.X..." where X is number.

    :param version_str: version string to check (should be in format: "X.Y" where X and Y are version numbers)
    :type version_str: str
    :param version_str2: version string to check (should be in format: "X.Y" where X and Y are version numbers)
    :type version_str2: str
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
