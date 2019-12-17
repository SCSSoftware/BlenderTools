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
from bpy.types import Panel
from io_scs_tools.ui import shared as _shared


class _MeshPanelBlDefs(_shared.HeaderIconPanel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return hasattr(context, "active_object") and context.active_object and context.active_object.type == "MESH"

    def get_layout(self):
        """Returns layout depending where it's drawn into. If popover create extra box to make it distinguisable between different sub-panels."""
        if self.is_popover:
            layout = self.layout.box().column()
        else:
            layout = self.layout

        return layout


class SCS_TOOLS_PT_Mesh(_MeshPanelBlDefs, Panel):
    """
    Creates "SCS Mesh" panel in the Object properties window.
    """
    bl_label = "SCS Mesh"
    bl_context = "data"

    def draw(self, context):
        """UI draw function.

        :param context: Blender Context
        :type context: bpy.context
        """

        if not self.poll(context):
            self.layout.label(text="No active mesh object!", icon="INFO")
            return

        layout = self.get_layout()
        mesh = context.active_object.data

        layout.use_property_split = True
        layout.use_property_decorate = False

        # show this only for meshes not for empties and other kinda objects
        if mesh:
            layout.prop(mesh.scs_props, "vertex_color_multiplier")


classes = (
    SCS_TOOLS_PT_Mesh,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_props_entry("Mesh Properties", SCS_TOOLS_PT_Mesh.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
