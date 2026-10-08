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
# Copyright (C) 2024-2026: Michaleczeq

from mathutils import Vector, Matrix
from .. import primitive as _primitive
from ....consts import PrefabLocators as _PL_consts


def draw_shape_control_node(mat, scs_globals):
    """Draws shape for "Locator" of "Control Node" type.

    :param mat:
    :param scs_globals:
    :return:
    """

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    _primitive.append_line_vertex((mat @ Vector((0.0, scs_globals.locator_empty_size, 0.0))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.75, 0.0))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.15, 0.45, 0.0))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.75, 0.0))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.75, 0.0))), color)
    _primitive.append_line_vertex((mat @ Vector((0.15, 0.45, 0.0))), color)


def draw_shape_sign(mat, scs_globals):
    """
    Draws shape for "Locator" of "Sign" type.
    :param mat:
    :param scs_globals:
    :return:
    """

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, scs_globals.locator_empty_size))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.45))), color)

    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.75))), color)
    _primitive.append_line_vertex((mat @ Vector((0.1299, 0.0, 0.675))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.1299, 0.0, 0.525))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.45))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((-0.1299, 0.0, 0.525))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((-0.1299, 0.0, 0.675))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.75))), color)


def draw_shape_spawn_point(mat, scs_globals):
    """
    Draws shape for "Locator" of "Spawn Point" type.
    :param mat:
    :param scs_globals:
    :return:
    """

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, scs_globals.locator_empty_size))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.75))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.1299, 0.0, 0.525))), color)
    _primitive.append_line_vertex((mat @ Vector((0.1299, 0.0, 0.675))), color)
    _primitive.append_line_vertex((mat @ Vector((0.1299, 0.0, 0.525))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.1299, 0.0, 0.675))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, -0.1299, 0.525))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.1299, 0.675))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.1299, 0.525))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, -0.1299, 0.675))), color)

def draw_shape_spawn_point_custom(mat, scs_globals, obj):
    """
    Draws shape for "Custom" type "Locator" of "Spawn Point" type.
    :param mat:
    :param scs_globals:
    :param obj:
    :return:
    """

    # Draw main Spawn Point shape
    draw_shape_spawn_point(mat, scs_globals)

    # Get locator properties
    depot_type = int(obj.scs_props.locator_prefab_custom_depot_type) >> 2
    cust_lenght = int(obj.scs_props.locator_prefab_custom_lenght) >> 4
    parking_diff = int(obj.scs_props.locator_prefab_custom_parking_difficulty)
    cust_rule = int(obj.scs_props.locator_prefab_custom_rule) >> 16

    # Matrix without "Locator Size"
    mat_orig = obj.matrix_world

    # Local variables
    width = 3.4                 # Full width of depot shape
    height = 0.05               # Height above ground to prevent z-fight
    lenght = 14 + cust_lenght   # Lenght of depo shape (we assume that cust_lenght (index) corresponds to additional lenght in meters eg. 14m + (idx) 0 = 14m)
    lenght_t = 5.0/2            # Lenght of trailer type shape

    # Load
    if depot_type == 1:
        match parking_diff:
            case 1:   # Easy
                color = scs_globals.trailer_load_easy_color
            case 2:   # Medium
                color = scs_globals.trailer_load_medium_color
            case 3:   # Hard
                color = scs_globals.trailer_load_hard_color
            case _:
                color = (0.0, 1.0, 1.0, 1.0)
    # Unload
    else:
        match parking_diff:
            case 1:   # Easy
                color = scs_globals.trailer_unload_easy_color
            case 2:   # Medium
                color = scs_globals.trailer_unload_medium_color
            case 3:   # Hard
                color = scs_globals.trailer_unload_hard_color
            case _:
                color = (1.0, 1.0, 0.0, 1.0)

    # Set diffrent shape for "Unlimited" lenght (max size of last fixed lenght)
    if lenght == 29.0:
        lenght = 20.0

        _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght + 3.0, height))), color)
        _primitive.append_line_vertex((mat_orig @ Vector((width/2, lenght + 1.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((width/2, lenght + 8.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght + 10.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((-width/2, lenght + 8.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((-width/2, lenght + 1.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght + 3.0, height))), color)
    
    # Depot
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, 0.0, height))), color)
    _primitive.append_line_vertex((mat_orig @ Vector((-width/2, 0.0, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((-width/2, lenght, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght + 2.0, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, lenght, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, 0.0, height))), color)

    # Set shape for "Trailer Type"
    height = height + 0.20   # Height override to move shape a little bit above ground
    if (cust_rule != 0) and scs_globals.show_trailer_type:
        match cust_rule:
            case 1:   # Box Trailer
                # Bottom rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)

                # Top rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 2))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 2))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 2))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 2))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 2))), color)
                
                # Edges
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 2))), color)

            case 2:   # Tank Trailer
                # Rear hexagon
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 - lenght_t, height + 0.25))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 - lenght_t, height + 0.75))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 - lenght_t, height + 1.00))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 - lenght_t, height + 0.75))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 - lenght_t, height + 0.25))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.00, lenght/2 - lenght_t, height))), color)

                # Front hexagon
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 + lenght_t, height + 0.25))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 + lenght_t, height + 0.75))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 + lenght_t, height + 1.00))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 + lenght_t, height + 0.75))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 + lenght_t, height + 0.25))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.00, lenght/2 + lenght_t, height))), color)

                # Edges
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 + lenght_t, height))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 - lenght_t, height + 0.25))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 + lenght_t, height + 0.25))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 - lenght_t, height + 0.75))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.433, lenght/2 + lenght_t, height + 0.75))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 - lenght_t, height + 1.00))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.000, lenght/2 + lenght_t, height + 1.00))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 - lenght_t, height + 0.75))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 + lenght_t, height + 0.75))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 - lenght_t, height + 0.25))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.433, lenght/2 + lenght_t, height + 0.25))), color)

            case 3:   # Dump & Bulk
                # Top rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 1))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 1))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 1))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 1))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 1))), color)
                
                # Edges
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 1))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 1))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 1))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 1))), color)

            case 4:   # Platform, Log & Container
                # Bottom rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)

                # Top rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 0.5))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 0.5))), color)
                
                # Edges
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 0.5))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 0.5))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 0.5))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 0.5))), color)

            case 5:   # Livestock
                # left-right
                _primitive.append_line_vertex((mat_orig @ Vector((-1.0, lenght/2, height + 1.0))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((1.0, lenght/2, height + 1.0))), color)

                # front-back
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2 + 1.0, height + 1.0))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2 - 1.0, height + 1.0))), color)

                # up-down
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2, height + 2.0))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.0, lenght/2, height))), color)

            case 6:   # Log Trailer
                # Bottom rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)

                # Top rectangle
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 0.5))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 0.5))), color, is_strip=True)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 0.5))), color)
                
                # Edges
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 - lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((0.5, lenght/2 + lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 - lenght_t, height + 2))), color)

                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height))), color)
                _primitive.append_line_vertex((mat_orig @ Vector((-0.5, lenght/2 + lenght_t, height + 2))), color)


def draw_shape_spawn_point_trailer(mat, scs_globals, obj, style_idx):
    """
    Draws fixed shape for old trailer rails of "Spawn Point" type.
    :param mat:
    :param scs_globals:
    :param obj:
    :param style_idx: Index style with custom colors, shape etc.
    :type style_idx: int
    :return:
    """

    # Draw main Spawn Point shape
    draw_shape_spawn_point(mat, scs_globals)

    # Matrix without "Locator Size"
    mat_orig = obj.matrix_world

    # Local default variables
    width = 3.4                 # Full width of depot shape
    height = 0.05               # Height above ground to prevent z-fight
    lenght = 25                 # Full lenght of depo shape (including "Unlimited" shape)
    pos_0 = 0.0                 # Default "0" position of shape (required when we need to move whole shape)
    unlimited = True            # If true, draw additional shape for "Unlimited" lenght 

    # Load colors from settings
    match style_idx:
        case 0:   # Trailer
            color = scs_globals.trailer_load_easy_color
        case 1:   # Long Trailer
            color = scs_globals.trailer_load_easy_color
            lenght = 33
        case 2:   # Unload (Easy)
            color = scs_globals.trailer_unload_easy_color
            lenght = 33
        case 3:   # Unload (Medium)
            color = scs_globals.trailer_unload_medium_color
        case 4:   # Unload (Hard)
            color = scs_globals.trailer_unload_hard_color
        case 5:   # Owned Trailer
            color = scs_globals.owned_trailer_color
            lenght = 33
        case 6:   # Service Station
            color = scs_globals.service_station_color
            lenght = 33
            pos_0 = -29.0   # Move shape position 29m back, because service station uses truck point, not trailer rear as position 0.
        case _:
            color = (1.0, 1.0, 0.0, 1.0)

    if unlimited:
        # Shrink main shape lenght to make space for "Unlimited" shape
        lenght = lenght - 8

        # Shape for "Unlimited" lenght (default for old rail system)
        _primitive.append_line_vertex((mat_orig @ Vector((0.0, pos_0 + lenght + 3.0, height))), color)
        _primitive.append_line_vertex((mat_orig @ Vector((width/2, pos_0 + lenght + 1.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((width/2, pos_0 + lenght + 8.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((0.0, pos_0 + lenght + 10.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((-width/2, pos_0 + lenght + 8.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((-width/2, pos_0 + lenght + 1.0, height))), color, is_strip=True)
        _primitive.append_line_vertex((mat_orig @ Vector((0.0, pos_0 + lenght + 3.0, height))), color)

    # Depot
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, pos_0, height))), color)
    _primitive.append_line_vertex((mat_orig @ Vector((-width/2, pos_0, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((-width/2, pos_0 + lenght, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((0.0, pos_0 + lenght + 2.0, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, pos_0 + lenght, height))), color, is_strip=True)
    _primitive.append_line_vertex((mat_orig @ Vector((width/2, pos_0, height))), color)


def draw_shape_traffic_light(mat, scs_globals):
    """
    Draws shape for "Locator" of "Traffic Semaphore" type.
    :param mat:
    :return:
    """

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, scs_globals.locator_empty_size))), color)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.45))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((-0.0866, 0.0, 0.5))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((-0.0866, 0.0, 0.84))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.89))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0866, 0.0, 0.84))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0866, 0.0, 0.5))), color, is_strip=True)
    _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.45))), color)

    for val in (0.5, 0.62, 0.74):
        _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, val))), color)
        _primitive.append_line_vertex((mat @ Vector((-0.0433, 0.0, 0.025 + val))), color, is_strip=True)
        _primitive.append_line_vertex((mat @ Vector((-0.0433, 0.0, 0.075 + val))), color, is_strip=True)
        _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, 0.1 + val))), color, is_strip=True)
        _primitive.append_line_vertex((mat @ Vector((0.0433, 0.0, 0.075 + val))), color, is_strip=True)
        _primitive.append_line_vertex((mat @ Vector((0.0433, 0.0, 0.025 + val))), color, is_strip=True)
        _primitive.append_line_vertex((mat @ Vector((0.0, 0.0, val))), color)


def draw_shape_map_point(mat, scs_globals):
    """
    Draws shape for "Locator" of "Map Point" type.
    :param mat:
    :param scs_globals:
    :return:
    """

    color = (
        scs_globals.locator_prefab_wire_color.r,
        scs_globals.locator_prefab_wire_color.g,
        scs_globals.locator_prefab_wire_color.b,
        1.0
    )

    _primitive.append_line_vertex((mat @ Vector((-0.17678, -0.17678, 0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((0.17678, 0.17678, -0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.17678, 0.17678, 0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((0.17678, -0.17678, -0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.17678, -0.17678, -0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((0.17678, 0.17678, 0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((-0.17678, 0.17678, -0.17678))), color)
    _primitive.append_line_vertex((mat @ Vector((0.17678, -0.17678, 0.17678))), color)


def draw_shape_trigger_point(mat, mat_orig, radius, scs_globals, draw_range):
    """
    Draws shape for "Locator" of "Trigger Point" type.
    :param mat:
    :param mat_orig:
    :param radius:
    :param scs_globals:
    :param draw_range:
    :return:
    """
    _primitive.draw_circle(0.25, 8, mat, scs_globals)
    _primitive.draw_circle(0.4, 8, mat, scs_globals)

    if draw_range:
        _primitive.draw_circle(radius, 32, mat_orig, scs_globals)


def draw_prefab_locator(obj, scs_globals):
    """
    Draw Prefab locator.
    :param obj:
    :return:
    """

    size = scs_globals.locator_size
    empty_size = scs_globals.locator_empty_size
    mat_sca = Matrix.Scale(size, 4)
    mat_orig = obj.matrix_world
    mat = mat_orig @ mat_sca
    if obj.scs_props.locator_prefab_type == 'Control Node':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis_neg(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_control_node(mat, scs_globals)

        if obj.scs_props.locator_prefab_con_node_index == '0':
            color = (1, 0, 0, 1)
        else:
            color = (0, 1, 0, 1)
        _primitive.draw_point((mat @ Vector((0.0, 0.0, 0.0))), color, 12.0)

    elif obj.scs_props.locator_prefab_type == 'Sign':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            draw_shape_sign(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Spawn Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            if obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.CUSTOM):
                draw_shape_spawn_point_custom(mat, scs_globals, obj)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.TRAILER_POS):    # Load (Easy) OLD
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 0)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.LONG_TRAILER_POS):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 1)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.UNLOAD_EASY_POS):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 2)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.UNLOAD_MEDIUM_POS):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 3)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.UNLOAD_HARD_POS):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 4)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.TRAILER_SPAWN):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 5)
            elif obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.SERVICE_POS):
                draw_shape_spawn_point_trailer(mat, scs_globals, obj, 6)
            else:
                draw_shape_spawn_point(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis_neg(mat, empty_size)
        if not obj.scs_props.locator_preview_model_present or not scs_globals.show_preview_models:
            draw_shape_traffic_light(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Navigation Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis_neg(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_control_node(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Map Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        draw_shape_map_point(mat, scs_globals)

    elif obj.scs_props.locator_prefab_type == 'Trigger Point':
        _primitive.draw_shape_x_axis(mat, empty_size)
        _primitive.draw_shape_y_axis(mat, empty_size)
        _primitive.draw_shape_z_axis(mat, empty_size)
        is_sphere = obj.scs_props.locator_prefab_tp_sphere_trigger
        draw_shape_trigger_point(mat, mat_orig, obj.scs_props.locator_prefab_tp_range, scs_globals, is_sphere)


def get_prefab_locator_comprehensive_info(obj):
    """Gets comprehensive info from prefab locator.

    :param obj: prefab locator to get infos from
    :type obj: bpy.types.Object
    :return: formatted string ready to be drawn with blf.draw()
    :rtype: str
    """
    textlines = ['"%s"' % obj.name,
                 "%s - %s" % (obj.scs_props.locator_type, obj.scs_props.locator_prefab_type)]

    if obj.scs_props.locator_prefab_type == 'Control Node':

        textlines.append("Node Index: %s" % obj.scs_props.locator_prefab_con_node_index)

    elif obj.scs_props.locator_prefab_type == 'Spawn Point':

        spawn_type_i = int(obj.scs_props.locator_prefab_spawn_type)
        textlines.append("Type: %s" % obj.scs_props.enum_spawn_type_items[spawn_type_i][1])
        if obj.scs_props.locator_prefab_spawn_type == str(_PL_consts.PSP.CUSTOM):
            depot_type_i = int(obj.scs_props.locator_prefab_custom_depot_type)
            difficulty_i = int(obj.scs_props.locator_prefab_custom_parking_difficulty)
            lenght_i = int(obj.scs_props.locator_prefab_custom_lenght)
            trailer_i = int(obj.scs_props.locator_prefab_custom_rule)

            textlines.append("Difficulty: %s (%s)" % (obj.scs_props.enum_custom_depot_type_items[depot_type_i][1],
                                                       obj.scs_props.enum_custom_parking_difficulty_items[difficulty_i][1]))
            textlines.append("Lenght: %s" % obj.scs_props.enum_custom_lenght_items[lenght_i][1])
            textlines.append("Trailer: %s" % obj.scs_props.enum_custom_rule_items[trailer_i][1])

    elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':

        textlines.append("ID: %s" % obj.scs_props.locator_prefab_tsem_id)
        if obj.scs_props.locator_prefab_tsem_profile != '':
            textlines.append("Profile: %s" % obj.scs_props.locator_prefab_tsem_profile)
        tsem_type_i = int(obj.scs_props.locator_prefab_tsem_type)
        if tsem_type_i != _PL_consts.TST.PROFILE:
            textlines.append("Type: %s" + obj.scs_props.enum_tsem_type_items[tsem_type_i][1])
            textlines.append("G: %.2f" % obj.scs_props.locator_prefab_tsem_gs +
                             " - O: %.2f" % obj.scs_props.locator_prefab_tsem_os1 +
                             " - R: %.2f" % obj.scs_props.locator_prefab_tsem_rs +
                             " - O: %.2f" % obj.scs_props.locator_prefab_tsem_os2)
            if obj.scs_props.locator_prefab_tsem_cyc_delay != 0:
                textlines.append("Cycle Delay: %.2f s" % obj.scs_props.locator_prefab_tsem_cyc_delay)

    elif obj.scs_props.locator_prefab_type == 'Navigation Point':

        np_boundary_i = int(obj.scs_props.locator_prefab_np_boundary)
        if np_boundary_i != 0:
            textlines.append("Boundary: %s" % obj.scs_props.enum_np_boundary_items[np_boundary_i][1])

        textlines.append("B. Node: %s" % obj.scs_props.locator_prefab_np_boundary_node)
        if obj.scs_props.locator_prefab_np_traffic_semaphore != '-1':
            textlines.append("T. Light ID: %s" % obj.scs_props.locator_prefab_np_traffic_semaphore)

    elif obj.scs_props.locator_prefab_type == 'Map Point':

        if obj.scs_props.locator_prefab_mp_road_over:
            textlines.append("Road Over: YES")
        if obj.scs_props.locator_prefab_mp_no_outline:
            textlines.append("No Outline: YES")
        if obj.scs_props.locator_prefab_mp_no_arrow:
            textlines.append("No Arrow: YES")
        if obj.scs_props.locator_prefab_mp_prefab_exit:
            textlines.append("Prefab Exit: YES")

        road_size_i = int(obj.scs_props.locator_prefab_mp_road_size)
        textlines.append("Road Size: %s" % obj.scs_props.enum_mp_road_size_items[road_size_i][1])

        road_offset_i = int(obj.scs_props.locator_prefab_mp_road_offset)
        if road_offset_i != _PL_consts.MPVF.ROAD_OFFSET_0:
            textlines.append("Offset: %s" % obj.scs_props.enum_mp_road_offset_items[road_offset_i][1])

        custom_color_i = int(obj.scs_props.locator_prefab_mp_custom_color)
        if custom_color_i != 0:
            textlines.append("Custom Color: %s" % obj.scs_props.enum_mp_custom_color_items[custom_color_i][1])

        assigned_node_i = int(obj.scs_props.locator_prefab_mp_assigned_node)
        if assigned_node_i != 0:
            textlines.append("Node: %s" % obj.scs_props.enum_mp_assigned_node_items[assigned_node_i][1])

        if len(obj.scs_props.locator_prefab_mp_dest_nodes) > 0:
            textlines.append("Destination Nodes: %s" % " ".join(obj.scs_props.locator_prefab_mp_dest_nodes))

    elif obj.scs_props.locator_prefab_type == 'Trigger Point':

        textlines.append("Range: %.2f m" % obj.scs_props.locator_prefab_tp_range)
        if obj.scs_props.locator_prefab_tp_reset_delay != 0:
            textlines.append("Reset Delay: %.2f s" % obj.scs_props.locator_prefab_tp_reset_delay)
        if obj.scs_props.locator_prefab_tp_sphere_trigger:
            textlines.append("Sphere Trigger: YES")
        if obj.scs_props.locator_prefab_tp_partial_activ:
            textlines.append("Partial Activation: YES")
        if obj.scs_props.locator_prefab_tp_onetime_activ:
            textlines.append("One-Time Activation: YES")
        if obj.scs_props.locator_prefab_tp_manual_activ:
            textlines.append("Manual Activation: YES")

    return "\n".join(textlines)
