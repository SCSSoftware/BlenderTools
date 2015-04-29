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
    bpy.types.Object.scs_cached_num_children = property(_get_num_children, _set_num_children)
    bpy.types.Object.scs_cached_materials_ids = property(_get_materials_ids, _set_materials_ids)


def _get_num_children(self):
    if "scs_cached_num_children" not in self:
        _set_num_children(self, len(self.children))

    return self["scs_cached_num_children"]


def _set_num_children(self, value):
    self["scs_cached_num_children"] = value


def _get_materials_ids(self):
    if "scs_cached_materials_ids" not in self:
        _set_materials_ids(self, {})

    return self["scs_cached_materials_ids"]


def _set_materials_ids(self, value):
    self["scs_cached_materials_ids"] = value