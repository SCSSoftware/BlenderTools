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

# Copyright (C) 2019: SCS Software

import bpy
from bpy.props import (BoolProperty,
                       EnumProperty, )


class WorkspaceSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Workspace Variables - ...Workspace.scs_props...
    """

    part_list_sorted: BoolProperty(
        name="Part List Sorted Alphabetically",
        description="Sort Part list alphabetically",
        default=False,
    )

    variant_list_sorted: BoolProperty(
        name="Variant List Sorted Alphabetically",
        description="Sort Variant list alphabetically",
        default=False,
    )

    variant_views: EnumProperty(
        name="Variant View Setting",
        description="Variant view style options",
        items=(
            ('compact', "Compact", "Compact view (settings just for one Variant at a time)", 'WINDOW', 0),
            ('vertical', "Vertical", "Vertical long view (useful for larger number of Variants)", 'LONGDISPLAY', 1),
            ('horizontal', "Horizontal", "Horizontal table view (best for smaller number of Variants)", 'SHORTDISPLAY', 2),
            ('integrated', "Integrated", "Integrated in Variant list (best for smaller number of Parts)", 'LINENUMBERS_OFF', 3),
        ),
        default='horizontal',
    )

    shader_presets_sorted: BoolProperty(
        name="Shader Preset List Sorted Alphabetically",
        description="Sort Shader preset list alphabetically",
        default=True,
    )

    # VISIBILITY VARIABLES
    shader_presets_expand: BoolProperty(
        name="Expand Shader Presets",
        description="Expand shader presets panel",
        default=False,
    )

    # VISIBILITY TOOLS SCOPE
    visibility_tools_scope: EnumProperty(
        name="Visibility Tools Scope",
        description="Selects the scope upon visibility tools are working",
        items=(
            ('Global', "Global", "Use scope of the whole scene"),
            ('SCS Root', "SCS Root", "Use the scope of current SCS Root"),
        ),
    )


classes = (
    WorkspaceSCSProps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
