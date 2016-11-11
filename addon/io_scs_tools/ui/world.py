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

from bpy.types import Panel, UIList
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _WorldPanelBlDefs(_shared.HeaderIconPanel):
    """
    Defines class for showing in Blender Scene Properties window
    """
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"


class SCSSunProfileSlots(UIList):
    """
    Draw sun profile entry within ui list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            layout.prop(item, "name", text="", emboss=False)
            props = layout.operator("world.scs_use_sun_profile", icon="SAVE_PREFS", text="", emboss=False)
            props.sun_profile_index = index
        else:
            layout.label(text="", icon_value=icon)


class SCSLighting(_WorldPanelBlDefs, Panel):
    """Creates a Panel in the Scene properties window"""
    bl_label = "SCS Lighting"
    bl_idname = "WORLD_PT_SCS_Lighting"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scs_globals = _get_scs_globals()

        is_active_sun_profile_valid = (0 <= scs_globals.sun_profiles_inventory_active < len(scs_globals.sun_profiles_inventory))
        is_ligting_scene_used = (context.scene and context.scene.background_set and
                                 context.scene.background_set.name == _LIGHTING_consts.scene_name)

        # draw operator for disabling lighting scene
        if is_ligting_scene_used:
            layout.operator("world.scs_disable_lighting_in_scene", icon="QUIT")

        # draw warning if lighting scene is not used as background set in current scene
        if is_active_sun_profile_valid and not is_ligting_scene_used:
            _shared.draw_warning_operator(layout, "SCS Lighting Not Used",
                                          "Current scene is not using SCS Ligthing.\n"
                                          "If you want to enable it, you either press icon beside sun profile name in the list or\n"
                                          "use 'Apply Values to SCS Lighting' button located on the bottom of selected sun profile details.",
                                          text="SCS Lighting Not Used: Click For Info",
                                          icon="INFO")

        # prepare main box containing header and body
        col = layout.column(align=True)
        header = col.box()
        body = col.box()

        # 1. header
        # library path
        row = header.row(align=True)
        split = row.split(percentage=0.35)
        split.label("Sun Profiles Library:", icon="FILE_TEXT")
        row = split.row(align=True)
        row.alert = not _path_utils.is_valid_sun_profiles_library_path()
        row.prop(scs_globals, "sun_profiles_lib_path", text="")
        row.operator("scene.select_sun_profiles_lib_path", text="", icon='FILESEL')

        # 2. body
        # lighting scene east direction
        row = body.row()
        row.label("", icon="LAMP_SPOT")
        row.prop(scs_globals, "lighting_scene_east_direction", slider=True)

        # disable any UI from now on if active sun profile is not valid
        body.enabled = is_active_sun_profile_valid

        # loaded sun profiles list
        body.template_list(
            'SCSSunProfileSlots',
            list_id="",
            dataptr=scs_globals,
            propname="sun_profiles_inventory",
            active_dataptr=scs_globals,
            active_propname="sun_profiles_inventory_active",
            rows=3,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )

        # active/selected sun profile props
        if is_active_sun_profile_valid:

            layout = body.box().column()

            layout.label("Selected Sun Profile Details:", icon='LAMP')
            layout.separator()

            active_sun_profile = scs_globals.sun_profiles_inventory[scs_globals.sun_profiles_inventory_active]

            layout.row(align=True).prop(active_sun_profile, "low_elevation")
            layout.row(align=True).prop(active_sun_profile, "high_elevation")

            layout.row(align=True).prop(active_sun_profile, "ambient")
            layout.row(align=True).prop(active_sun_profile, "ambient_hdr_coef")

            layout.row(align=True).prop(active_sun_profile, "diffuse")
            layout.row(align=True).prop(active_sun_profile, "diffuse_hdr_coef")

            layout.row(align=True).prop(active_sun_profile, "specular")
            layout.row(align=True).prop(active_sun_profile, "specular_hdr_coef")

            # layout.row(align=True).prop(active_sun_profile, "sun_color")
            # layout.row(align=True).prop(active_sun_profile, "sun_color_hdr_coef")

            layout.row(align=True).prop(active_sun_profile, "env")
            layout.row(align=True).prop(active_sun_profile, "env_static_mod")

            layout.separator()
            row = layout.row()
            row.scale_y = 1.5
            props = row.operator("world.scs_use_sun_profile", icon="SAVE_PREFS", text="Apply Values to SCS Lighting")
            props.sun_profile_index = scs_globals.sun_profiles_inventory_active
