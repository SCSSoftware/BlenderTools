# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software you can redistribute it and/or
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

"""
Constants for data group of map and navigation curves
"""

from math import cos, pi
from enum import Enum
from zipfile import ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2


class ConnectionsStorage:
    """Constants related for storage of connections used in custom drawing
    """

    collection_name = ".scs_connection_storage"
    """Name of bpy.data.collection which will be used for storing Custom Property for connections dictionary"""
    custom_prop_name = "scs_locator_connections"
    """Name of the Blender Custom Property where dictionary for connections will be stored"""


class Operators:
    class SelectionType:
        """Constants related to type of selection in operators all over the tools
        """
        undecided = -1
        deselect = 0
        select = 1
        shift_select = 2
        ctrl_select = 3

    class ViewType:
        """Constants related to type of view in operators all over the tools
        """
        undecided = -1
        hide = 0
        viewonly = 1
        shift_view = 2
        ctrl_view = 3

    class TerrainPoints:
        """Constants related to terrain points operators.
        """
        vg_name_prefix = ".scs_terrain_points_node:"
        """Name prefix of terrain points vertex group."""
        vg_name_regex = "^" + vg_name_prefix.replace(".", "\\.") + "\d$"
        """Regex for matching terrain points vertex groups names on export."""

    class View3DReport:
        """Constants related to 3D view report operator.
        """
        # constants defining BT banner image and texts/positions of close/hide controls
        BT_BANNER_IMG_NAME = ".scs_bt_banner.tga"
        BT_BANNER_WITH_CTRLS_IMG_NAME = ".scs_bt_banner_with_ctrls.tga"
        CLOSE_BTN_AREA = (240, 260, -25, -5)
        CLOSE_BTN_TEXT_POS = (242, -9)
        CLOSE_BTN_TEXT = "×"
        HIDE_BTN_AREA = (215, 235, -25, -5)
        HIDE_BTN_TEXT_POS = (220, -5)
        HIDE_BTN_TEXT = "–"
        SCROLLUP_BTN_AREA = (-17, -3, 22, 47)
        SCROLLUP_BTN_TEXT_POS = (-18, 40)
        SCROLLUP_BTN_TEXT = "↑"
        SCROLLDOWN_BTN_AREA = (-17, -3, 52, 77)
        SCROLLDOWN_BTN_TEXT_POS = (-18, 71)
        SCROLLDOWN_BTN_TEXT = "↓"

    class InventoryMoveType:
        """Constants related to moving type in operators for inventories items moving.
        """
        move_down = "down"
        move_up = "up"


class Icons:
    """Constants related to loading of custom icons.
    """

    default_icon_theme = "white"

    class Types:
        """This class saves names of all custom icons for Blender Tools.
        """
        mesh = ".01_mesh_model_object.png"
        mesh_shadow_caster = ".02_object_with_shadow_caster_material.png"
        mesh_glass = ".03_object_with_glass_material.png"
        mesh_with_physics = ".04_object_with_physical_material.png"
        loc = ".05_locator_all_types.png"
        loc_model = ".06_locator_model.png"
        loc_prefab = ".07_locator_prefab.png"
        loc_collider = ".08_locator_collision.png"
        loc_prefab_node = ".09_locator_prefab_node.png"
        loc_prefab_sign = ".10_locator_prefab_sign.png"
        loc_prefab_spawn = ".11_locator_prefab_spawn.png"
        loc_prefab_semaphore = ".12_locator_prefab_semaphore.png"
        loc_prefab_navigation = ".13_locator_prefab_navigation.png"
        loc_prefab_map = ".14_locator_prefab_map.png"
        loc_prefab_trigger = ".15_locator_prefab_trigger.png"
        loc_collider_box = ".16_collider_box.png"
        loc_collider_sphere = ".17_collider_sphere.png"
        loc_collider_capsule = ".18_collider_capsule.png"
        loc_collider_cylinder = ".19_collider_cylinder.png"
        loc_collider_convex = ".20_collider_convex.png"
        scs_root = ".21_scs_root_object.png"
        scs_object_menu = ".22_scs_object_menu.png"
        scs_logo = ".icon_scs_bt_logo.png"

        @staticmethod
        def as_list():
            """Gets file names of all custom icons defined in Blender Tools
            :return: list of all custom icon files
            :rtype: list
            """
            return [Icons.Types.mesh, Icons.Types.mesh_shadow_caster, Icons.Types.mesh_glass, Icons.Types.mesh_with_physics,
                    Icons.Types.loc, Icons.Types.loc_model, Icons.Types.loc_prefab, Icons.Types.loc_collider,
                    Icons.Types.loc_prefab_node, Icons.Types.loc_prefab_sign, Icons.Types.loc_prefab_spawn, Icons.Types.loc_prefab_semaphore,
                    Icons.Types.loc_prefab_navigation, Icons.Types.loc_prefab_map, Icons.Types.loc_prefab_trigger,
                    Icons.Types.loc_collider_box, Icons.Types.loc_collider_sphere, Icons.Types.loc_collider_capsule,
                    Icons.Types.loc_collider_cylinder, Icons.Types.loc_collider_convex, Icons.Types.scs_root,
                    Icons.Types.scs_object_menu, Icons.Types.scs_logo]


class Part:
    """Constants related to 'SCS Parts'
    """
    default_name = "defaultpart"
    """Default name for part"""


class Variant:
    """Constants related to 'SCS Variants'
    """
    default_name = "default"
    """Default name for variant"""


class Look:
    """Constants related to 'SCS Looks'
    """
    custom_prop_name = "scs_looks_data"
    """Name of the Blender Custom Property where dictionary for looks will be stored"""
    default_name = "default"
    """Default name for look"""


class Material:
    """Constants related to materials
    """
    unset_bitmap_filepath = ""
    """Unset value of each texture filepath (used for identifying if this value in material was set)"""
    unset_substance = "None"
    """Unset value of material substance (used for identifying if this value in material was set)"""
    node_group_prefix = ".SCS_NG_"
    """Prefix for naming node groups used by SCS materials"""
    prevm_material_name = ".scs_prevm"
    """Name of the material used on SCS preview models."""


class Colors:
    """Constants related to colors in Blender
    """
    gamma = 2.2
    """Gamma value used by Blender for correcting display colors."""
    prevm_color = (0.36, 0.29, 0.57, 1)
    """Color array used for preview models."""


class LampTools:
    """Constants related to lampmask and it's tools
    """

    class VehicleSides(Enum):
        """Defined sides of vehicles.
        """
        FrontLeft = 0
        FrontRight = 1
        RearLeft = 2
        RearRight = 3
        Middle = 4

    class VehicleLampTypes(Enum):
        """Defined lamp types for vehicles.
        """
        LeftTurn = 0
        RightTurn = 1
        Brake = 2
        HighBeam = 3
        LowBeam = 4
        Reverse = 5
        DRL = 6
        Positional = 7

    class AuxiliaryLampColors(Enum):
        """Defined vehicle auxiliary light colors.
        """
        White = 0
        Orange = 1

    class AuxiliaryLampTypes(Enum):
        """Defined lamp types for vehicle auxiliary lights.
        """
        Dim = 0
        Bright = 1

    class TrafficLightTypes(Enum):
        """Defined lamp types for traffic lights.
        """
        Red = 0
        Yellow = 1
        Green = 2


class VertexColorTools:
    """Constants related to vertex color tools
    """

    class WrapType:
        All = "all"
        Selected = "selected"

    class ColoringLayersTypes:
        """Constants for vertex coloring that hold names of the layers we use.
        """

        Color = "color"
        Decal = "decal"
        AO = "ao"
        AO2 = "ao2"

        @staticmethod
        def as_list():
            """Gets assets vertex color layers names
            :return: list of all layer types as name
            :rtype: list
            """
            return [
                VertexColorTools.ColoringLayersTypes.Color,
                VertexColorTools.ColoringLayersTypes.Decal,
                VertexColorTools.ColoringLayersTypes.AO,
                VertexColorTools.ColoringLayersTypes.AO2
            ]


class Mesh:
    """Constants for mesh data used either on import or in general.
    """
    none_uv = "~"
    vcol_a_suffix = "_alpha"

    default_uv = "UV"
    default_vcol = "Col"


class PrefabLocators:
    """Constants for prefab locator properties, flags and exporter.
    """

    NAVIGATION_NEXT_PREV_MAX = 4
    """Maximun navigation next/previus curve count constant."""
    PREFAB_LANE_COUNT_MAX = 8
    """Maximum lane count constant."""
    PREFAB_NODE_COUNT_MAX = 6
    """Maximum node count constant."""

    # START: not in original constants

    TSEM_COUNT_MAX = 32
    """Maximum traffic semaphore count. NOTE: it can be bigger, but no need"""
    TP_NEIGHBOURS_COUNT_MAX = 2
    """Maximum neighbours count for trigger points."""
    CURVE_MEASURE_STEPS = 300
    """Number of segments that curves use for measuing it's length."""
    CURVE_STEPS_COUNT = 10
    """Number of segments that curves are using during export calculations"""
    CURVE_CLOSEST_POINT_ITER = 30
    """Number of iterations for closest point calculations."""
    CURVE_SPLIT_CROSS_DOT = cos(60.0 * pi / 180.0)
    """Dot product constante which marsk split croos intersection as sharp."""
    SAFE_DISTANCE = 4.0
    """Minimal distance between two intersecting curves to be meet until we reach safe point."""
    TERRAIN_POINTS_MIN_DISTANCE = 0.01
    """Minimal distance between two terrain points to be recognized as different."""

    # END: not in original constants

    class PNCF:
        """Constants used for calculation of navigation curve flag variable.
        """
        FORCE_NO_BLINKER = 0x00000004
        RIGHT_BLINKER = 0x00000008
        LEFT_BLINKER = 0x00000010
        SMALL_VEHICLES = 0x00000020
        LARGE_VEHICLES = 0x00000040
        ALLOWED_VEHICLES_MASK = (SMALL_VEHICLES | LARGE_VEHICLES)
        PRIORITY_MASK = 0x000F0000
        PRIORITY_SHIFT = 16
        LOW_PROBABILITY = 0x00002000
        LIMIT_DISPLACEMENT = 0x00004000
        ADDITIVE_PRIORITY = 0x00008000

        START_NAV_POINT_FLAGS = (FORCE_NO_BLINKER | RIGHT_BLINKER | LEFT_BLINKER |
                                 PRIORITY_MASK | ADDITIVE_PRIORITY | LIMIT_DISPLACEMENT)
        END_NAV_POINT_FLAGS = (ALLOWED_VEHICLES_MASK | LOW_PROBABILITY)

    class PNLF:
        """Constants used for calculation of navigation point leads to nodes variable.
        """
        END_NODE_MASK = 0x000000FF
        END_NODE_SHIFT = 0
        END_LANE_MASK = 0x0000FF00
        END_LANE_SHIFT = 8
        START_NODE_MASK = 0x00FF0000
        START_NODE_SHIFT = 16
        START_LANE_MASK = 0xFF000000
        START_LANE_SHIFT = 24

    class PSP:
        """Constants used for calculateion of spawn point flag variable.
        """
        NONE = 0
        TRAILER_POS = 1
        UNLOAD_EASY_POS = 2
        GAS_POS = 3
        SERVICE_POS = 4
        TRUCKSTOP_POS = 5
        WEIGHT_POS = 6
        TRUCKDEALER_POS = 7
        HOTEL = 8
        CUSTOM = 9
        PARKING = 10
        TASK = 11
        MEET_POS = 12
        COMPANY_POS = 13
        GARAGE_POS = 14
        BUY_POS = 15
        RECRUITMENT_POS = 16
        CAMERA_POINT = 17
        BUS_STATION = 18
        UNLOAD_MEDIUM_POS = 19
        UNLOAD_HARD_POS = 20
        UNLOAD_RIGID_POS = 21
        WEIGHT_CAT_POS = 22
        COMPANY_UNLOAD_POS = 23
        TRAILER_SPAWN = 24
        LONG_TRAILER_POS = 25

    class TST:
        """Constants representing type of traffic semaphores.
        """
        PROFILE = 0
        MODEL_ONLY = 1
        TRAFFIC_LIGHT = 2
        TRAFFIC_LIGHT_MINOR = 3
        TRAFFIC_LIGHT_MAJOR = 4
        BARRIER_MANUAL_TIMED = 5
        BARRIER_DISTANCE = 6
        TRAFFIC_LIGHT_BLOCKABLE = 7
        BARRIER_GAS = 8
        TRAFFIC_LIGHT_VIRTUAL = 9
        BARRIER_AUTOMATIC = 10

    class MPVF:
        """Constants represeting map point visual flags.
        """
        ROAD_SIZE_ONE_WAY = 0x00000000
        ROAD_SIZE_1_LANE = 0x00000100
        ROAD_SIZE_2_LANE = 0x00000200
        ROAD_SIZE_3_LANE = 0x00000300
        ROAD_SIZE_4_LANE = 0x00000400
        ROAD_SIZE_2_LANE_SPLIT = 0x00000500
        ROAD_SIZE_3_LANE_SPLIT = 0x00000600
        ROAD_SIZE_4_LANE_SPLIT = 0x00000700
        ROAD_SIZE_3_LANE_ONE_WAY = 0x00000800
        ROAD_SIZE_MANUAL = 0x00000D00
        ROAD_SIZE_AUTO = 0x00000E00
        ROAD_SIZE_MASK = 0x00000F00
        ROAD_OFFSET_0 = 0x00000000
        ROAD_OFFSET_1 = 0x00001000
        ROAD_OFFSET_2 = 0x00002000
        ROAD_OFFSET_5 = 0x00003000
        ROAD_OFFSET_10 = 0x00004000
        ROAD_OFFSET_15 = 0x00005000
        ROAD_OFFSET_20 = 0x00006000
        ROAD_OFFSET_25 = 0x00007000
        ROAD_OFFSET_LANE = 0x00008000
        ROAD_OFFSET_MASK = 0x0000F000
        ROAD_EXT_VALUE_MASK = 0x000000FF
        ROAD_OVER = 0x00010000
        CUSTOM_COLOR1 = 0x00020000
        CUSTOM_COLOR2 = 0x00040000
        CUSTOM_COLOR3 = 0x00080000
        NO_OUTLINE = 0x00100000
        NO_ARROW = 0x00200000

    class MPNF:
        """Constants representing map point navigation flags.
        """
        NAV_NODE_0 = 0x00000001
        NAV_NODE_1 = 0x00000002
        NAV_NODE_2 = 0x00000004
        NAV_NODE_3 = 0x00000008
        NAV_NODE_4 = 0x00000010
        NAV_NODE_5 = 0x00000020
        NAV_NODE_6 = 0x00000040
        NAV_NODE_CUSTOM_TARGET = 0x00000080
        NAV_NODE_ALL = 0x000000FF
        NAV_NODE_MASK = 0x000000FF
        NAV_NODE_START = 0x00000100
        NAV_BASE = 0x00000200
        PREFAB_EXIT = 0x00000400

    class TPF:
        """Constants represetning trigger point navigation flags.
        """
        MANUAL = 0x0001
        SPHERE = 0x0002
        PARTIAL = 0x0004
        ONETIME = 0x0008

    class PIF:
        """Constants for intersections flag.
        """
        SIBLING_COUNT_MASK = 0x000000F0
        SIBLING_COUNT_SHIFT = 4
        TYPE_START = 0x00010000
        TYPE_END = 0x00020000
        TYPE_CROSS_SHARP = 0x00040000


class Bones:
    init_scale_key = "scs_init_scale"
    """Pose bone custom property dictionary key for saving initial bone scale on PIS import."""


class ConvHlpr:
    """Conversion helper constants
    """
    NoZip = "No Archive"
    StoredZip = str(ZIP_STORED)
    DeflatedZip = str(ZIP_DEFLATED)
    Bzip2Zip = str(ZIP_BZIP2)


class SCSLigthing:
    """Constants for scs lighting.
    """
    scene_name = ".scs_lighting"
    """Name of lighting scene. It should be prefixed with dot to be partially hidden in scene selection theme."""

    sun_lamp_name = ".scs_sun"
    """Name of scs sun object in the lighting scene."""

    default_ambient = (0.3,) * 3
    default_diffuse = (0.9,) * 3
    default_specular = (0.5,) * 3
    default_env = 1.0
    """Default lighting values used when scs lighting is disabled, gotten from effect/eut/defaults.sii"""


class PaintjobTools:
    """Constants for paintjob tools.
    """

    class VehicleTypes:
        """Vehicle types, defining where vehicle will be placed in defs and model paths.
        """
        NONE = "none"
        TRUCK = "truck"
        TRAILER = "trailer_owned"

    uvs_name_2nd = "scs_paintjob_2nd"
    """2nd uvs layer name used during unification on export"""
    uvs_name_3rd = "scs_paintjob_3rd"
    """3rd uvs layer name used during unification on export."""

    model_refs_to_sii = ".scs_model_refs_to_sii_files"
    """Name of the property for saving references paths to models inside a group data-block."""
    export_tag_obj_name = ".scs_export_group"
    """Name of the object inside the group which visibility tells us either group should be exported or no."""
    model_variant_prop = ".scs_variant"
    """Name of the property for saving variant of the model inside group encapsulating imported paintable model."""
    main_coll_name = ".scs_main_collection"
    """Name of the collection where left over objects will be linked to, when importing from sii data."""

    id_mask_colors = (
        (51, 0, 0),
        (255, 136, 0),
        (217, 202, 0),
        (134, 179, 140),
        (0, 190, 204),
        (0, 31, 115),
        (117, 70, 140),
        (191, 96, 147),
        (242, 61, 61),
        (127, 68, 0),
        (102, 95, 0),
        (64, 255, 140),
        (0, 204, 255),
        (0, 0, 51),
        (41, 0, 51),
        (204, 0, 82),
        (204, 102, 102),
        (178, 137, 89),
        (173, 179, 89),
        (0, 77, 41),
        (0, 41, 51),
        (108, 108, 217),
        (230, 128, 255),
        (89, 0, 36),
        (230, 172, 172),
        (230, 203, 172),
        (100, 102, 77),
        (48, 191, 124),
        (0, 170, 255),
        (191, 191, 255),
        (83, 0, 89),
        (166, 124, 141),
        (140, 49, 35),
        (128, 113, 96),
        (57, 77, 19),
        (57, 77, 68),
        (64, 106, 128),
        (38, 38, 51),
        (217, 0, 202),
        (127, 0, 34),
        (255, 115, 64),
        (229, 172, 57),
        (234, 255, 191),
        (0, 51, 34),
        (0, 68, 128),
        (34, 0, 255),
        (64, 32, 62),
        (115, 57, 65),
        (76, 34, 19),
        (102, 77, 26),
        (133, 204, 51),
        (0, 255, 238),
        (0, 27, 51),
        (48, 0, 179),
        (255, 191, 251),
        (51, 26, 29),
        (191, 156, 143),
        (51, 38, 13),
        (68, 255, 0),
        (0, 115, 107),
        (153, 180, 204),
        (119, 54, 217),
        (153, 0, 122),
        (204, 112, 51),
        (51, 47, 38),
        (32, 128, 45),
        (143, 191, 188),
        (83, 116, 166),
        (119, 105, 140),
        (255, 64, 166)
    )
    """Array of unique colors for building ID mask texture."""


class Cache:
    dir_name = "blender_scs_blender_tools"
    """Name of the directory inside tmp directory, that will be used for cache storage."""
    max_size = 40 * 1024 * 1024  # 40MB
    """Maximum size of tmp directory cache."""
