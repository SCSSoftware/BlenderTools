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
from bpy.app.handlers import persistent
from io_scs_tools.utils import save_scs_globals_to_blend as _save_scs_globals_to_blend


@persistent
def pre_save(scene):
    # make sure to save actions used in at least one scs game object
    for obj in bpy.data.objects:
        if obj.type == "EMPTY" and obj.scs_props.empty_object_type == "SCS_Root":
            for scs_anim in obj.scs_object_animation_inventory:
                if scs_anim.action in bpy.data.actions:
                    bpy.data.actions[scs_anim.action].use_fake_user = True

    # save SCS globals into world settings, so they get saved with blend file
    _save_scs_globals_to_blend()
