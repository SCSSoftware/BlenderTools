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
from bpy.props import StringProperty, FloatProperty


class MeshSCSTools(bpy.types.PropertyGroup):
    """
    SCS Tools Mesh Variables - ...Mesh.scs_props...
    :return:
    """
    locator_preview_model_path = StringProperty(
        name="Preview Model",
        description="Preview model filepath",
        default="",
        subtype="FILE_PATH",
        # subtype='NONE',
    )
    vertex_color_multiplier = FloatProperty(
        name="Vertex Color Multiplier",
        description="All of the vertices will have their color multiplied for this factor upon export.",
        default=1,
        min=0,
        max=10,
        step=0.1
    )