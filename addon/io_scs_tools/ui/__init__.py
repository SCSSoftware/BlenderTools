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

from . import mesh
from . import world
from . import object
from . import output
from . import shared
from . import material
from . import workspace
from . import tool_shelf


def register():
    # order matters for scs tools main menu items ordering, items registered soner will appear on top
    shared.register()
    tool_shelf.register()
    workspace.register()
    world.register()
    object.register()
    mesh.register()
    material.register()
    output.register()


def unregister():
    shared.unregister()
    tool_shelf.unregister()
    workspace.unregister()
    world.unregister()
    object.unregister()
    mesh.unregister()
    material.unregister()
    output.unregister()
