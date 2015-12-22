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

from bpy.props import EnumProperty


def get_default(blender_property):
    """Gets default value of Blender ID property

    :param blender_property: any Blender ID property from "bpy.types" class
    :type blender_property: tuple
    :return: default value of Blender ID property
    :rtype: object
    """
    return blender_property[1]['default']


def get_filebrowser_display_type(is_image=False):
    """Gets enum property for specifying display type of file browser.
    If is_image argument is not passed or is False default display type is used.

    :param is_image: flag specifying if display type shall be image preview
    :type is_image: bool
    :return: enum property of display type for Blender file browser
    :rtype: bpy.types.EnumProperty
    """

    default_value = "FILE_IMGDISPLAY" if is_image else "FILE_DEFAULTDISPLAY"

    return EnumProperty(
        items=[
            ("FILE_DEFAULTDISPLAY", "", ""),
            ("FILE_SHORTDISPLAY", "", ""),
            ("FILE_LONGDISPLAY", "", ""),
            ("FILE_IMGDISPLAY", "", "")
        ],
        default=default_value,
        options={'HIDDEN'}
    )
