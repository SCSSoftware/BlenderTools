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
from bpy.types import Panel, UIList
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import view3d as _view_3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories
from io_scs_tools.ui import shared as _shared


class _WorldPanelBlDefs:
    """
    Defines class for showing in Blender World Properties window
    """
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return context.region.type in ('WINDOW', 'HEADER')

    def get_layout(self):
        """Returns layout depending where it's drawn into. If popover create extra box to make it distinguisable between different sub-panels."""
        if self.is_popover:
            layout = self.layout.box().column()
        else:
            layout = self.layout

        return layout


class SCS_TOOLS_UL_SunProfileSlot(UIList):
    """
    Draw sun profile entry within ui list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", icon_value=icon)


class SCS_TOOLS_PT_Lighting(_shared.HeaderIconPanel, _WorldPanelBlDefs, Panel):
    """Creates a Panel in the world properties window"""
    bl_label = "SCS Lighting"

    def draw_header(self, context):
        if not self.is_popover:
            scs_globals = _get_scs_globals()
            self.layout.prop(scs_globals, "use_scs_lighting", text="")

        _shared.HeaderIconPanel.draw_header(self, context)

    def draw(self, context):
        """UI draw function."""
        scs_globals = _get_scs_globals()
        scs_inventories = _get_scs_inventories()

        if self.is_popover:
            header_row = self.layout.row()
            header_row.prop(scs_globals, "use_scs_lighting", text="SCS Lighting")
            layout = self.layout.box().column()
        else:
            layout = self.get_layout()

        layout.enabled = _get_scs_globals().use_scs_lighting

        # prepare main layout containing header and body
        header = layout.column()
        body = layout.column()

        # 1. header
        # library path
        row = _shared.create_row(header, use_split=True, enabled=True)
        row.alert = not _path_utils.is_valid_sun_profiles_library_path()
        row.prop(scs_globals, "sun_profiles_lib_path", icon='FILE_CACHE')
        row.operator("scene.scs_tools_select_sun_profiles_lib_path", text="", icon='FILEBROWSER')

        # 2. body
        # lighting scene east direction
        row = body.row(align=True)

        left_col = row.row(align=True)
        left_col.enabled = not scs_globals.lighting_east_lock
        left_col.label(text="", icon='LIGHT_SPOT')
        left_col.prop(scs_globals, "lighting_scene_east_direction", slider=True)

        right_col = row.row(align=True)
        icon = 'LOCKED' if scs_globals.lighting_east_lock else 'UNLOCKED'
        right_col.prop(scs_globals, "lighting_east_lock", icon=icon, icon_only=True)

        # now if we have multiple 3D views locking has to be disabled,
        # as it can not work properly with multiple views because all views share same SCS Lighting lamps
        if _view_3d_utils.has_multiple_view3d_spaces(screen=context.screen):
            right_col.enabled = False
            _shared.draw_warning_operator(row.row(align=True),
                                          "SCS Lighting East Lock Disabled!",
                                          "East lock can not be used, because you are using multiple 3D views and\n"
                                          "tools can not decide on which view you want to lock the east.",
                                          icon='INFO')

        # disable any UI from now on if active sun profile is not valid
        body.enabled = (0 <= scs_globals.sun_profiles_active < len(scs_inventories.sun_profiles))

        # loaded sun profiles list
        body.template_list(
            SCS_TOOLS_UL_SunProfileSlot.__name__,
            list_id="",
            dataptr=scs_inventories,
            propname="sun_profiles",
            active_dataptr=scs_globals,
            active_propname="sun_profiles_active",
            rows=3,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )


class SCS_TOOLS_PT_ActiveSunProfileSettings(_WorldPanelBlDefs, Panel):
    """Creates a sub panel in the world properties window for active lighting settings."""

    bl_parent_id = SCS_TOOLS_PT_Lighting.__name__
    bl_label = "Active Sun Profile Settings"

    @classmethod
    def poll(cls, context):
        return 0 <= _get_scs_globals().sun_profiles_active < len(_get_scs_inventories().sun_profiles)

    def draw(self, context):
        """UI draw function."""
        scs_globals = _get_scs_globals()
        scs_inventories = _get_scs_inventories()

        layout = self.get_layout()
        layout.enabled = scs_globals.use_scs_lighting
        layout.use_property_split = True
        layout.use_property_decorate = False

        active_sun_profile = scs_inventories.sun_profiles[scs_globals.sun_profiles_active]

        layout.prop(active_sun_profile, "low_elevation")
        layout.prop(active_sun_profile, "high_elevation")
        layout.prop(active_sun_profile, "ambient")
        layout.prop(active_sun_profile, "diffuse")
        layout.prop(active_sun_profile, "specular")
        layout.prop(active_sun_profile, "env")
        layout.prop(active_sun_profile, "env_static_mod")


classes = (
    SCS_TOOLS_PT_Lighting,
    SCS_TOOLS_PT_ActiveSunProfileSettings,
    SCS_TOOLS_UL_SunProfileSlot,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_props_entry("World Properties", SCS_TOOLS_PT_Lighting.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
