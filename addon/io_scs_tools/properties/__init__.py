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

from io_scs_tools.properties import action
from io_scs_tools.properties import addon_preferences
from io_scs_tools.properties import dynamic
from io_scs_tools.properties import material
from io_scs_tools.properties import mesh
from io_scs_tools.properties import object
from io_scs_tools.properties import scene
from io_scs_tools.properties import workspace


def register():
    action.register()
    addon_preferences.register()
    dynamic.register()
    material.register()
    mesh.register()
    object.register()
    scene.register()
    workspace.register()


def unregister():
    action.unregister()
    addon_preferences.unregister()
    dynamic.unregister()
    material.unregister()
    mesh.unregister()
    object.unregister()
    scene.unregister()
    workspace.unregister()
