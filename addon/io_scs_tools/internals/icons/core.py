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

LAYOUT = "layout"

_cache = {
    LAYOUT: None
}


def _load_image(icon_type):
    """Loads image for given icon type if path exists.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: True if image is succesfully loaded; False otherwise
    :rtype: bool
    """
    tools_paths = _path.get_addon_installation_paths()
    if len(tools_paths) > 0:
        # create path to current icon "ui/icons/icon_type"
        icon_path = os.path.join(tools_paths[0], 'ui' + os.sep + 'icons' + os.sep + icon_type)
        if os.path.isfile(icon_path):
            if not icon_type in bpy.data.images:
                bpy.data.images.load(icon_path)
            return True
        else:
            lprint("W Icon %r is missing. Please try to install addon again!", (icon_type,))
            return False


def _draw(self, context):
    self.layout.row().label("Everything should be set to go...")
    self.layout.row().label("Check the console for result and happy Blending :)")

    _cache[LAYOUT] = self.layout


def init():
    """Initialization function for getting hold of layout variable with which icons can be created afterwards.
    """
    if not _cache[LAYOUT]:
        bpy.context.window_manager.popup_menu(_draw, title="SCS Blender Tools", icon="INFO")


def get_icon(icon_type):
    """Gets icon by given icon type.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: icon value for given icon type
    :rtype: int
    """

    # load image on request only (in some cases images might get deleted for example on Undo action)
    image_loaded = True
    if icon_type not in bpy.data.images:
        image_loaded = _load_image(icon_type)

    # if layout exists create icon
    if _cache[LAYOUT] and image_loaded:
        return _cache[LAYOUT].icon(bpy.data.images[icon_type])
    else:
        return 0

