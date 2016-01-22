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

import os
from bpy.utils import previews
from io_scs_tools.consts import Icons as _ICON_consts
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint

CUSTOM_ICONS = "custom_icons"

# Multiple preview collections can be stored in this dictionary, but we will use only one
_preview_collections = {}


def init():
    """Initialization function for getting hold of preview collection variable with already created custom icon objects.
    """

    if CUSTOM_ICONS not in _preview_collections:

        pcoll = previews.new()

        # load icons
        tools_paths = _path.get_addon_installation_paths()
        if len(tools_paths) > 0:

            for icon_type in _ICON_consts.Types.as_list():

                # create path to current icon "ui/icons/icon_type"
                icon_path = os.path.join(tools_paths[0], 'ui' + os.sep + 'icons' + os.sep + icon_type)
                if os.path.isfile(icon_path):
                    if icon_type not in pcoll:
                        pcoll.load(icon_type, icon_path, 'IMAGE')
                else:
                    lprint("W Icon %r is missing. Please try to install addon again!", (icon_type,))

        _preview_collections[CUSTOM_ICONS] = pcoll


def cleanup():
    """Release custom icons internal data. This results in deleting of preview collections entries
    and preview collections dictionary itself.
    """

    if CUSTOM_ICONS in _preview_collections:

        for pcoll in _preview_collections.values():
            previews.remove(pcoll)

        _preview_collections.clear()


def get_icon(icon_type):
    """Gets icon by given icon type.
    :param icon_type: one of icons type from "io_scs_tools.consts.Icons.Types"
    :type icon_type: str
    :return: icon value for given icon type
    :rtype: int
    """

    if CUSTOM_ICONS not in _preview_collections:
        lprint("E Icons not yet initialized, Blender Tools were not properply initialized!")
        return 0

    pcoll = _preview_collections[CUSTOM_ICONS]

    if icon_type in pcoll:
        return pcoll[icon_type].icon_id
    else:
        return 0
