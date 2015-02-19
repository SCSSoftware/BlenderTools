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
from bpy.app.handlers import persistent
from io_scs_tools.consts import Icons as _ICONS_consts


@persistent
def pre_save(scene):
    # remove custom icons from blender datablock
    icon_list = _ICONS_consts.Types.as_list()
    for icon in icon_list:
        if icon in bpy.data.images:
            img = bpy.data.images[icon]
            img.use_fake_user = False
            img.user_clear()

            bpy.data.images.remove(img)