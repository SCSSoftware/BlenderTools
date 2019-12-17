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

import bpy
from io_scs_tools.internals.persistent import initialization as _persistent_init
from io_scs_tools.internals.persistent import loop_check as _persistent_loop
from io_scs_tools.internals.persistent import file_save as _persistent_file_save
from io_scs_tools.internals.persistent import file_load as _persistent_file_load
from io_scs_tools.internals.persistent import open_gl as _persistent_open_gl
from io_scs_tools.internals.persistent import shaders_update as _persistent_shaders_update


def enable():
    """Append scene_update_post and load_post callbacks
    Used for:
     1. initialization of SCS Tools
     2. checking object data (unique naming etc.)
     3. applying fixes for blend files saved with old blender tools versions
     4. removing not needed and securing needed data before file save
    """
    # covers: enable/disable
    if bpy.context.preferences.is_dirty:
        bpy.app.timers.register(_persistent_init.on_enable)

    # covers: reload, start-up, open file
    bpy.app.handlers.load_post.append(_persistent_init.post_load)

    bpy.app.handlers.depsgraph_update_pre.append(_persistent_loop.object_data_check)

    # register custom drawing and shaders callbacks only in none-background mode
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.append(_persistent_open_gl.post_depsgraph)
        bpy.app.handlers.frame_change_post.append(_persistent_open_gl.post_frame_change)
        bpy.app.handlers.frame_change_post.append(_persistent_shaders_update.post_frame_change)
        bpy.app.handlers.undo_post.append(_persistent_open_gl.post_undo)
        bpy.app.handlers.redo_post.append(_persistent_open_gl.post_redo)

    bpy.app.handlers.load_post.append(_persistent_file_load.post_load)

    bpy.app.handlers.save_pre.append(_persistent_file_save.pre_save)


def disable():
    """Remove callbacks added with enable function call.
    """

    if _persistent_init.post_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_persistent_init.post_load)
    if _persistent_loop.object_data_check in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(_persistent_loop.object_data_check)
    if _persistent_open_gl.post_depsgraph in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_persistent_open_gl.post_depsgraph)
    if _persistent_open_gl.post_frame_change in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(_persistent_open_gl.post_frame_change)
    if _persistent_shaders_update.post_frame_change in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(_persistent_shaders_update.post_frame_change)
    if _persistent_open_gl.post_undo in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_persistent_open_gl.post_undo)
    if _persistent_open_gl.post_redo in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_persistent_open_gl.post_redo)
    if _persistent_file_load.post_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_persistent_file_load.post_load)
    if _persistent_file_save.pre_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(_persistent_file_save.pre_save)
