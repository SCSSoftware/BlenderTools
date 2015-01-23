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

"""
Constants for data group of map and navigation curves
"""


class ConnectionsStorage:
    """Constants related for storage of connections used in custom drawing
    """

    group_name = ".scs_connection_storage"
    """Name of bpy.data.group which will be used for storing Custom Property for connections dictionary"""
    custom_prop_name = "scs_locator_connections"
    """Name of the Blender Custom Property where dictionary for connections will be stored"""


class Operators:
    class SelectionType:
        """Constants related to type of selection in operators all over the tools
        """
        undecided = -1
        deselect = 0
        select = 1
        shift_select = 2
        ctrl_select = 3

    class ViewType:
        """Constants related to type of view in operators all over the tools
        """
        undecided = -1
        hide = 0
        viewonly = 1
        shift_view = 2
        ctrl_view = 3


class Part:
    """Constants related to 'SCS Parts'
    """
    default_name = "defaultpart"
    """Default name for part"""


class Variant:
    """Constants related to 'SCS Variants'
    """
    default_name = "default"
    """Default name for variant"""