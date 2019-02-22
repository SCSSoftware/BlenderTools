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


def __get_world__():
    """Ensures and gets world data block.

    :return: world data block
    :rtype: bpy.types.World
    """
    if len(bpy.data.worlds) == 0:
        bpy.data.worlds.new('World')

    return bpy.data.worlds[0]


def get_scs_globals():
    """Function for accessing SCS globals

    :return: global settings for SCS Blender Tools
    :rtype: io_scs_tools.properties.world.GlobalSCSProps
    """
    return __get_world__().scs_globals


def ensure_scs_globals_save():
    """Function for ensuring that scs globals get's saved into the blend file,
    even if world is unliked by the user.
    """
    world = __get_world__()

    if world.users == 0:  # no users, use fake one
        world.use_fake_user = True
    elif world.users >= 2:  # multiple users, switch of fake one as data will get saved anyway
        world.use_fake_user = False
