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

import re

_GAME_TOKENS = {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10,
                'a': 11, 'b': 12, 'c': 13, 'd': 14, 'e': 15, 'f': 16, 'g': 17, 'h': 18, 'i': 19, 'j': 20,
                'k': 21, 'l': 22, 'm': 23, 'n': 24, 'o': 25, 'p': 26, 'q': 27, 'r': 28, 's': 29, 't': 30,
                'u': 31, 'v': 32, 'w': 33, 'x': 34, 'y': 35, 'z': 36, '_': 37}


def get_unique(name, iterable, sep="_"):
    """Creates unique name iniside given iterable with appending XXX number postfix.

    :param name: original name without postfix
    :type name: str
    :param iterable: iterable object inside which name should be unique
    :type iterable: iter
    :param sep: separator for number postfix
    :type sep: str
    :return: unique name inside given iterable
    :rtype: str
    """

    if name in iterable:

        original_name = name
        n_copies = 1
        while name in iterable:
            name = original_name + sep + str(n_copies).zfill(3)
            n_copies += 1

    return name


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
    :type default_name: str
    """
    name = name.lower()  # lower case

    # strip of Blender naming convention of double objects .XXX
    if re.match(".+(\.\d{3})$", name):
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
