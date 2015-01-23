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

from bpy.types import Panel
from io_scs_tools.ui import shared as _shared


class _MeshPanelBlDefs(_shared.HeaderIconPanel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"


class SCSTools(_MeshPanelBlDefs, Panel):
    """
    Creates "SCS Object Specials" panel in the Object properties window.
    """
    bl_label = "SCS Mesh Specials"
    bl_idname = "MESH_PT_SCS_specials"
    bl_context = "data"

    def draw(self, context):
        """UI draw function.

        :param context: Blender Context
        :type context: bpy.context
        """

        layout = self.layout
        mesh = context.mesh

        # show this only for meshes not for empties and other kinda objects
        if mesh:
            layout.prop(mesh.scs_props, "vertex_color_multiplier")
