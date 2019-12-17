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

# Copyright (C) 2019: SCS Software

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.internals.shaders import update_shaders as _update_shaders


@persistent
def post_frame_change(scene):
    """Shader update on post frame change.

    :param scene: current scene
    :type scene: bpy.type.Scene
    """

    # do any shader related time updates when animation playback is active
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        _update_shaders(scene)
