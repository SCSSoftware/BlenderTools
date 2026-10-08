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

# Copyright (C) 2025: SCS Software

import bpy
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.utils import object as _object_utils
from bpy.app.handlers import persistent

@persistent
def sync_part(scene, depsgraph):
    scs_root_object = _object_utils.get_scs_root(bpy.context.active_object)
    if scs_root_object:
        scs_props = scs_root_object.scs_props
        if scs_root_object and bpy.context.active_object != scs_root_object:
            # if old active object is different than current
            # set the value for active part index from it
            if scs_props.active_scs_part_old_active != bpy.context.active_object.name:
                scs_props.active_scs_part_value = _inventory.get_index(scs_root_object.scs_object_part_inventory,
                                                                       bpy.context.active_object.scs_props.scs_part)

        if scs_props.active_scs_part_old_active != bpy.context.active_object.name:
            scs_props.active_scs_part_old_active = bpy.context.active_object.name
