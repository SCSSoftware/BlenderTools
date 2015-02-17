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

from io_scs_tools.internals.icons import core as _core


def init():
    """Initialize custom icons for usage in layouts!
    NOTE: This function should be called when all Blender data blocks are ready for usage!
    """
    _core.init()


def get_icon(icon_type):
    """Get the custom icon for given type.
    :param icon_type: type of the icon. IconTypes variables should be used for it.
    :type icon_type: str
    :return: integer of icon or 0 if icon is not found in dictionary
    :rtype: int
    """
    return _core.get_icon(icon_type)
