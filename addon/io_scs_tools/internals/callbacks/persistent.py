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
from io_scs_tools.internals.persistent import initialization as _persistent_init
from io_scs_tools.internals.persistent import loop_check as _persistent_loop
from io_scs_tools.internals.persistent import file_save as _persistent_file_save


def enable():
    """Append scene_update_post and load_post callbacks
    Used for:
     1. initialization of SCS Tools
     2. checking object data (unique naming etc.)
     3. removing of custom icons datablock before saving blend file
    """
    # covers: start-up, reload, enable/disable
    bpy.app.handlers.scene_update_post.append(_persistent_init.initialise_scs_dict)
    # covers: opening file manually from Blender
    bpy.app.handlers.load_post.append(_persistent_init.initialise_scs_dict)

    bpy.app.handlers.scene_update_post.append(_persistent_loop.object_data_check)
    bpy.app.handlers.save_pre.append(_persistent_file_save.pre_save)


def disable():
    """Remove scene_update_post and load_post callbacks
    """
    if _persistent_init.initialise_scs_dict in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_persistent_init.initialise_scs_dict)
    if _persistent_loop.object_data_check in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(_persistent_loop.object_data_check)
    if _persistent_file_save.pre_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(_persistent_file_save.pre_save)