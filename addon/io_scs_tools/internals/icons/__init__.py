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
import os
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint

CUSTOM_ICONS = "custom_icons"

# Multiple preview collections can be stored in this dictionary, but we will use only one
_preview_collections = {}


def _load_image(icon_type):
    """Loads image for given icon type if path exists.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: True if image is succesfully loaded; False otherwise
    :rtype: bool
    """

    pcoll = _preview_collections[CUSTOM_ICONS]

    tools_paths = _path.get_addon_installation_paths()
    if len(tools_paths) > 0:
        # create path to current icon "ui/icons/icon_type"
        icon_path = os.path.join(tools_paths[0], 'ui' + os.sep + 'icons' + os.sep + icon_type)
        if os.path.isfile(icon_path):
            if icon_type not in pcoll:
                pcoll.load(icon_type, icon_path, 'IMAGE')
            return True
        else:
            lprint("W Icon %r is missing. Please try to install addon again!", (icon_type,))
            return False


def _init():
    """Initialization function for getting hold of preview collection variable where icons will be stored.
    :return: custom icons preview collection
    :rtype: dict
    """

    if CUSTOM_ICONS not in _preview_collections:

        import bpy.utils.previews

        pcoll = bpy.utils.previews.new()
        _preview_collections[CUSTOM_ICONS] = pcoll

    return _preview_collections[CUSTOM_ICONS]


def release_icons_data():
    """Release custom icons internal data. This results in deleting of preview collections entries
    and preview collections dictionary itself.
    """

    if CUSTOM_ICONS in _preview_collections:

        import bpy.utils.previews

        for pcoll in _preview_collections.values():
            bpy.utils.previews.remove(pcoll)

        _preview_collections.clear()


def get_icon(icon_type):
    """Gets icon by given icon type.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: icon value for given icon type
    :rtype: int
    """

    # get custom icons preview collection
    pcoll = _init()

    # load image on request only (in some cases images might get deleted for example on Undo action)
    image_loaded = True
    if icon_type not in pcoll:
        image_loaded = _load_image(icon_type)

    # if layout exists create icon
    if image_loaded:
        return pcoll[icon_type].icon_id
    else:
        return 0
