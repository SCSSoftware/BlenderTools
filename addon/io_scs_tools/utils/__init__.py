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


def __get_addon_prefs__():
    """Gets scs tools addon preferences.

    :return: scs tools addon preferences
    :rtype: io_scs_tools.properties.addon_preferences.SCSAddonPrefs
    """
    return bpy.context.preferences.addons["io_scs_tools"].preferences


def get_scs_globals():
    """Function for accessing SCS globals

    :return: global settings for SCS Blender Tools
    :rtype: io_scs_tools.properties.world.GlobalSCSProps
    """
    return __get_addon_prefs__().scs_globals


def get_scs_inventories():
    """Function for accessing SCS inventories

    :return: runtime loaded inventories for SCS Blender Tools
    :rtype: io_scs_tools.properties.addon_preferences.SCSInventories
    """
    return __get_addon_prefs__().scs_inventories


def save_scs_globals_to_blend():
    """Function saving scs globals into the blend file.
    We take first world data block and write scs_globals dictionary of our properties into it.
    """
    world = __get_world__()

    if world.users == 0:  # no users, use fake one
        world.use_fake_user = True
    elif world.users >= 2:  # multiple users, switch of fake one as data will get saved anyway
        world.use_fake_user = False

    global_props = {}

    scs_globals = get_scs_globals()
    for prop in scs_globals.get_writtable_keys():
        global_props[prop] = scs_globals[prop]

    world['scs_globals'] = global_props


def load_scs_globals_from_blend():
    """Loads scs globals saved in the blend file and silently applies them, without triggering properties update functions.
    If no entries is found nothing is loaded and no scs global property get changed.
    """
    world = __get_world__()

    if "scs_globals" not in world:
        return

    global_props = world['scs_globals']

    scs_globals = get_scs_globals()
    for prop in global_props.keys():
        scs_globals[prop] = global_props[prop]
