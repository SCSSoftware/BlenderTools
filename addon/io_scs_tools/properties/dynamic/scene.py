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


def register():
    bpy.types.Scene.scs_cached_num_objects = property(_get_num_objects, _set_num_objects)
    bpy.types.Scene.scs_cached_active_scs_root = property(_get_active_scs_root, _set_active_scs_root)


def _get_num_objects(self):
    if "scs_cached_num_objects" not in self:
        _set_num_objects(self, len(self.objects))

    return self["scs_cached_num_objects"]


def _set_num_objects(self, value):
    self["scs_cached_num_objects"] = value


def _get_active_scs_root(self):
    if "scs_cached_active_scs_root" not in self:

        # if there is no active object set empty string
        if self.objects.active:
            name = self.objects.active.name
        else:
            name = ""

        _set_active_scs_root(self, name)

    return self["scs_cached_active_scs_root"]


def _set_active_scs_root(self, value):
    self["scs_cached_active_scs_root"] = value
