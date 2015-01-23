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
import re

_GAME_TOKENS = {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10,
                'a': 11, 'b': 12, 'c': 13, 'd': 14, 'e': 15, 'f': 16, 'g': 17, 'h': 18, 'i': 19, 'j': 20,
                'k': 21, 'l': 22, 'm': 23, 'n': 24, 'o': 25, 'p': 26, 'q': 27, 'r': 28, 's': 29, 't': 30,
                'u': 31, 'v': 32, 'w': 33, 'x': 34, 'y': 35, 'z': 36, '_': 37}


def get_unique(name, sep="."):
    """
    Takes a name and adds a number or raise the number if there is already one.
    :type name: str
    :param sep: wanted seperator between name and number
    :type sep: str
    """
    # print(' > name: %r' % name)
    if len(name) > 4:
        if name[-4] == sep:
            try:
                new_name = str(name[:-4] + sep + str(int(name[-3:]) + 1).rjust(3, "0"))
            except:
                new_name = ""
                print('ERROR in "add_numbers"!')
        else:
            new_name = str(name + sep + "001")
    else:
        new_name = str(name + sep + "001")
    # print(' < name: %r' % new_name)
    return new_name


def really_make_the_unique_name(name, sep="."):
    """
    Takes a name and make a unique name for objects.
    (A custom replacement for "bpy_extras.io_utils.unique_name"
    function, which doesn't do what I expected.)
    :param name:
    :param sep:
    :return:
    """
    name_is_already_used = True
    while name_is_already_used:
        found = False
        for obj in bpy.data.objects:
            if obj.name == name:
                found = True
                name = get_unique(name, sep)
        # print('found = %s' % str(found))
        if found:
            name_is_already_used = True
        else:
            name_is_already_used = False
    return name


def make_unique_name(obj, name, sep="."):
    """
    Takes any object of target type and a name and returns its unique name.
    :param obj:
    :param name:
    :param sep:
    :return:
    """
    from bpy_extras.io_utils import unique_name

    # CUSTOM FUNCTION FOR UNIQUE NAMES
    new_name = really_make_the_unique_name(name, sep)

    # NOTE: Blender's "unique_name" function doesn't make the names unique
    # for a reason unknown to me, but it can make the names without
    # unwanted characters and restrict it to the correct length.
    new_name = unique_name(
        obj,
        new_name,
        {},
        name_max=-1,
        clean_func=None,
        sep=sep,
    )
    return new_name


def remove_diacritic(name):
    """
    Takes a string and returns it without any diacritical marks.
    :type name: str
    """
    import unicodedata

    new_name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
    return str(new_name)[2:-1]


def tokenize_name(name, default_name="default"):
    """
    Takes a string and returns it as a valid token.
    :type name: str
    """
    name = name.lower()  # lower case

    # strip of Blender naming convention of double objects .XXX
    if re.match(".+\.\d{3}", name):
        name = name[:-4]

    new_name = ""
    for token in name:
        if token in _GAME_TOKENS:
            new_name += token

    if len(new_name) > 12:
        new_name = new_name[0:3] + "_" + new_name[-8:]
    elif len(new_name) == 0:
        new_name = default_name

    return new_name


def get_lod_name(context):  # FIXME: Probably not reliable!
    """
    This function returns a LOD name as a string or an empty string
    if there is no actual LOD setting.
    :param context:
    :return:
    """
    lod_name = ""
    obj = context.active_object
    while obj.parent:
        obj = obj.parent
    else:
        lod_name = obj.name
    # print('LOD name: %r' % lod_name)
    return lod_name