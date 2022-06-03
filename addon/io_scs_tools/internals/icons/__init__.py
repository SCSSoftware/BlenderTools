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

import os
from bpy.utils import previews
from io_scs_tools.consts import Icons as _ICON_consts
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint

PCOLLS = "custom_icons"
PCOLLS_IDX_MAP = PCOLLS + "_index_map"
PCOLLS_NAME_MAP = PCOLLS + "_name_map"
CURRENT_THEME = "theme"

_cache = {
    PCOLLS: {},  # multiple preview collections, one per theme
    PCOLLS_IDX_MAP: {},  # map of theme indices to theme names
    PCOLLS_NAME_MAP: {},  # map of theme names to theme indices
    CURRENT_THEME: _ICON_consts.default_icon_theme  # default theme
}


def register():
    """Initialization function for getting hold of preview collection variable with already created custom icon objects.
    """

    tools_paths = _path.get_addon_installation_paths()
    if len(tools_paths) <= 0:
        return

    # load icon themes
    icon_themes_dir = os.path.join(tools_paths[0], 'ui', 'icons')
    if not os.path.isdir(icon_themes_dir):
        return

    theme_idx = 0
    for theme_name in os.listdir(icon_themes_dir):
        icon_theme_dir = os.path.join(icon_themes_dir, theme_name)

        # ignore all none directory entries
        if not os.path.isdir(icon_theme_dir):
            continue

        # create new preview only once.
        # NOTE: We removed previews cleanup from code
        # because it was crashing Blender when rapidly enabling/disabling BT addon.
        # So instead of always creating new preview collection we rather reuse existing and
        # only load icons again with force reload flag, to ensure icons are always reloaded when init is called.
        if theme_name not in _cache[PCOLLS]:

            pcoll = previews.new()
            _cache[PCOLLS][theme_name] = pcoll
            _cache[PCOLLS_NAME_MAP][theme_idx] = theme_name
            _cache[PCOLLS_IDX_MAP][theme_name] = theme_idx
            theme_idx += 1
        else:

            pcoll = _cache[PCOLLS][theme_name]
            print("INFO\t- Icon collection is already in python memory, re-using it!")

        for icon_type in _ICON_consts.Types.as_list():

            # create path to current icon "ui/icons/<theme_name>/<icon_type>"
            icon_path = os.path.join(icon_theme_dir, icon_type)
            if os.path.isfile(icon_path):
                if icon_type not in pcoll:
                    pcoll.load(icon_type, icon_path, 'IMAGE', force_reload=True)
            else:
                print("WARNING\t- Icon %r is missing. Please try to install addon again!" % icon_type)

    # if current theme doesn't exists, use first instead
    if _cache[CURRENT_THEME] not in _cache[PCOLLS] and len(_cache[PCOLLS]) > 0:
        set_theme(get_theme_name(0))
        print("WARNING\t- Default icon theme doesn't exist, fallback to first available!")


def unregister():
    """Clearing preview collections for custom icons. Should be called on addon unregister.
    """
    for theme_name, pcoll in _cache[PCOLLS].items():
        pcoll.close()

    _cache[PCOLLS].clear()
    _cache[PCOLLS_IDX_MAP].clear()
    _cache[PCOLLS_NAME_MAP].clear()


def set_theme(theme):
    """Set current used icons theme

    :param theme: icons theme to use
    :type theme: str
    """
    _cache[CURRENT_THEME] = theme


def get_theme_name(idx):
    """Gets theme name from given index.
    NOTE: No safety checks, for performance reasons!

    :param idx: index of the desired theme
    :type idx: int
    :return: name of given theme index
    :rtype: str
    """
    return _cache[PCOLLS_NAME_MAP][idx]


def get_theme_idx(name):
    """Gets theme index from given name.
    NOTE: No safety checks, for performance reasons!

    :param name: name of the desired theme
    :type name: str
    :return: index of given theme name
    :rtype: int
    """
    return _cache[PCOLLS_IDX_MAP][name]


def get_current_theme_idx():
    """Gets current used theme index.

    :return: index of current theme
    :rtype: int
    """
    return get_theme_idx(_cache[CURRENT_THEME])


def get_loaded_themes():
    """Gets list of loaded theme names.

    :return: random ordered theme names
    :rtype: list[str]
    """
    return list(_cache[PCOLLS].keys())


def has_loaded_themes():
    """Tells if there are any loaded themes available.

    :return: True if any themes are currently loaded, False otherwise
    :rtype: bool
    """
    return len(_cache[PCOLLS]) > 0


def get_icon(icon_type):
    """Gets icon by given icon type.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: icon value for given icon type
    :rtype: int
    """

    current_theme = _cache[CURRENT_THEME]

    if current_theme not in _cache[PCOLLS]:
        lprint("E Icons not yet initialized, Blender Tools were not properply initialized!")
        return 0

    pcoll = _cache[PCOLLS][current_theme]

    if icon_type in pcoll:
        return pcoll[icon_type].icon_id
    else:
        return 0
