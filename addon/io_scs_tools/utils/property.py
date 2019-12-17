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

# Copyright (C) 2013-2019: SCS Software

import bpy
from bpy.props import EnumProperty
from idprop.types import IDPropertyArray, IDPropertyGroup


def get_default(from_object, prop_name):
    """Gets default value of Blender ID property

    :param from_object: instance of property object from which property value should be read
    :type from_object: bpy.types.bpy_struct
    :param prop_name: any Blender ID property name registred in given object
    :type prop_name: str
    :return: default value of Blender ID property; if given object doesn't have given property attribute or is None, then None is returned
    :rtype: any | None
    """

    if from_object is None:
        return None

    if prop_name not in from_object.bl_rna.properties:
        return None

    bl_rna_prop = from_object.bl_rna.properties[prop_name]
    if getattr(bl_rna_prop, "is_array", False):
        return bl_rna_prop.default_array[:]
    else:
        return bl_rna_prop.default


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


def get_id_prop_as_py_object(prop_value):
    """Get blender ID Property represented as with python native types.
    Nested group and collection properties are properly converted too, with the help of recursive calls.

    :param prop_value: id property to convert
    :type prop_value: IDProperty
    :return: ID Property converted to native python object types
    :rtype: any
    """

    if isinstance(prop_value, IDPropertyGroup):
        prop_dict = {}
        for sub_prop_key, sub_prop_value in prop_value.items():
            prop_dict[sub_prop_key] = get_id_prop_as_py_object(sub_prop_value)
        return prop_dict
    elif isinstance(prop_value, IDPropertyArray):
        return tuple(prop_value)
    elif isinstance(prop_value, list):
        prop_list = []
        for sub_prop_value in prop_value:
            prop_list.append(get_id_prop_as_py_object(sub_prop_value))
        return prop_list
    else:
        return prop_value
