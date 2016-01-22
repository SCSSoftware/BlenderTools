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
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       FloatProperty, )


class SceneSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Scene Variables - ...Scene.scs_props...
    :return:
    """

    part_list_sorted = BoolProperty(
        name="Part List Sorted Alphabetically",
        description="Sort Part list alphabetically",
        default=False,
    )

    variant_list_sorted = BoolProperty(
        name="Variant List Sorted Alphabetically",
        description="Sort Variant list alphabetically",
        default=False,
    )
    variant_views = EnumProperty(
        name="Variant View Setting",
        description="Variant view style options",
        items=(
            ('compact', "Compact", "Compact view (settings just for one Variant at a time)", 'FULLSCREEN', 0),
            ('vertical', "Vertical", "Vertical long view (useful for larger number of Variants)", 'LONGDISPLAY', 1),
            ('horizontal', "Horizontal", "Horizontal table view (best for smaller number of Variants)", 'SHORTDISPLAY', 2),
            ('integrated', "Integrated", "Integrated in Variant list (best for smaller number of Parts)", 'LINENUMBERS_OFF', 3),
        ),
        default='horizontal',
    )

    # VISIBILITY VARIABLES
    scs_look_panel_expand = BoolProperty(
        name="Expand SCS Look Panel",
        description="Expand SCS Look panel",
        default=True,
    )
    scs_part_panel_expand = BoolProperty(
        name="Expand SCS Part Panel",
        description="Expand SCS Part panel",
        default=True,
    )
    scs_variant_panel_expand = BoolProperty(
        name="Expand SCS Variant Panel",
        description="Expand SCS Variant panel",
        default=True,
    )
    empty_object_settings_expand = BoolProperty(
        name="Expand SCS Object Settings",
        description="Expand SCS Object settings panel",
        default=True,
    )
    locator_settings_expand = BoolProperty(
        name="Expand Locator Settings",
        description="Expand locator settings panel",
        default=True,
    )
    locator_display_settings_expand = BoolProperty(
        name="Expand Locator Display Settings",
        description="Expand locator display settings panel",
        default=False,
    )
    shader_item_split_percentage = FloatProperty(
        name="UI Split Percentage",
        description="This property defines percentage of UI space spliting between material item names and values.",
        min=0.000001, max=1.0,
        default=0.35,
    )
    shader_attributes_expand = BoolProperty(
        name="Expand SCS Material Attributes",
        description="Expand SCS material attributes panel",
        default=True,
    )
    shader_textures_expand = BoolProperty(
        name="Expand SCS Material Textures",
        description="Expand SCS material textures panel",
        default=True,
    )
    shader_presets_expand = BoolProperty(
        name="Expand Shader Presets",
        description="Expand shader presets panel",
        default=False,
    )
    global_display_settings_expand = BoolProperty(
        name="Expand Global Display Settings",
        description="Expand global display settings panel",
        default=True,
    )
    global_paths_settings_expand = BoolProperty(
        name="Expand Global Paths Settings",
        description="Expand global paths settings panel",
        default=True,
    )
    scs_root_panel_settings_expand = BoolProperty(
        name="Expand 'SCS Root Object' Settings",
        description="Expand 'SCS Root Object' settings panel",
        default=True,
    )
    global_settings_expand = BoolProperty(
        name="Expand Global Settings",
        description="Expand global settings panel",
        default=True,
    )
    scene_settings_expand = BoolProperty(
        name="Expand Scene Settings",
        description="Expand scene settings panel",
        default=True,
    )
    scs_animation_settings_expand = BoolProperty(
        name="Expand Animation Settings",
        description="Expand animation settings panel",
        default=True,
    )
    scs_animplayer_panel_expand = BoolProperty(
        name="Expand Animation Player Settings",
        description="Expand animation player panel",
        default=True,
    )
    scs_skeleton_panel_expand = BoolProperty(
        name="Expand Skeleton Settings",
        description="Expand skeleton settings panel",
        default=True,
    )
    default_export_filepath = StringProperty(
        name="Default Export Path",
        description="Relative export path (relative to SCS Project Base Path) for all SCS Game Objects without custom export path "
                    "(this path does not apply when exporting via menu)",
        default="",
        # subtype="FILE_PATH",
        subtype='NONE',
    )
    export_panel_expand = BoolProperty(
        name="Expand Export Panel",
        description="Expand Export panel",
        default=True,
    )

    # VISIBILITY TOOLS SCOPE
    visibility_tools_scope = EnumProperty(
        name="Visibility Tools Scope",
        description="Selects the scope upon visibility tools are working",
        items=(
            ('Global', "Global", "Use scope of the whole scene"),
            ('SCS Root', "SCS Root", "Use the scope of current SCS Root"),
        ),
    )
