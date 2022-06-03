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

from time import time
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from io_scs_tools.internals.open_gl import locators as _locators

INFOS_CACHE = "infos"
INFOS_LAST_UPDATE = "infos_last_update"
INFOS_DATA = "infos_data"

LOC_2D_CACHE = "loc_2d"
LOC_2D_VALID = "loc_2d_valid_locators"
LOC_2D_DATA = "loc_2d_data"


class LocatorsCache:
    """Class for implementing drawn locators info cache storing it's 2d location in region and info text that should be drawn.

    There are two caches:
    1. Info cache which will store locators infos (same for all views, can be calculated only once per second)
    2. 2D region locations cache per view matrix (this has to be calculated each time view matrix changes, as each view has it's own matrix)
    """

    def __init__(self):
        self.__cache = {
            INFOS_CACHE: {
                INFOS_LAST_UPDATE: -99.9,
                INFOS_DATA: {}
            },
            LOC_2D_CACHE: {
                LOC_2D_VALID: {},
                LOC_2D_DATA: {}
            },
        }

    def cache_locations_2d(self, objs, region, region_3d):
        """Caches given objects 2d locations in given region and saves list of valid objects for this given region perspective matrix.

        :param objs: list of locators that should be cached and checked for visibility
        :type objs: collections.Sequence[bpy.types.Object]
        :param region: blender area 2d region for which for which locators 2d location should be calculated
        :type region: bpy.types.Region
        :param region_3d: blender area 3d region from which locators 2d locations should be calculated
        :type region_3d: bpy.types.RegionView3D
        """
        cache = self.__cache[LOC_2D_CACHE][LOC_2D_DATA]

        persp_matrix_str = str(region_3d.perspective_matrix)

        if persp_matrix_str not in cache:  # this perspective matrix not yet in cache, create new entry, continue to caching

            # pop first element if we have too many of entries already
            if len(cache) >= 10:
                first_key = next(iter(cache.keys()))
                del cache[first_key]

            cache[persp_matrix_str] = {}

        elif len(cache[persp_matrix_str]) != len(objs):  # matrix found, but objects count changed, cleaar and continue to caching
            cache[persp_matrix_str].clear()

        # cache given locator objects one by one & filter out of bounds objects
        valid_locators = []
        for obj in objs:

            loc_ws = Vector((obj.matrix_world[0][3], obj.matrix_world[1][3], obj.matrix_world[2][3]))
            loc_ws_str = str(loc_ws)

            # same location already cached for this locator, ignore it!
            if obj in cache[persp_matrix_str] and loc_ws_str == cache[persp_matrix_str][obj][0]:
                valid_locators.append(obj)
                continue

            # calculate 2d location!
            loc_2d = location_3d_to_region_2d(region, region_3d, loc_ws, default=None)

            # if out of bounds, ignore it!
            if not loc_2d or loc_2d.x < 0 or loc_2d.x > region.width or loc_2d.y < 0 or loc_2d.y > region.height:
                continue

            valid_locators.append(obj)
            cache[persp_matrix_str][obj] = (loc_ws_str, loc_2d)

        self.__cache[LOC_2D_CACHE][LOC_2D_VALID][persp_matrix_str] = valid_locators

    def cache_infos(self, objs):
        """Caches given objects comprehensive infos.

        :param objs: list of locators that should be cached for infos
        :type objs: collections.Sequence[bpy.types.Object]
        """
        cache = self.__cache[INFOS_CACHE]

        # cache infos once per second (also eliminates caching for same redraw, if called from multiple 3d views)
        now_time = time()
        if now_time - cache[INFOS_LAST_UPDATE] < 1.0:
            return

        # set last updated time and clear old cache
        cache[INFOS_LAST_UPDATE] = now_time
        cache[INFOS_DATA].clear()

        for obj in objs:
            if obj.scs_props.locator_type == 'Prefab':
                info_txt = _locators.prefab.get_prefab_locator_comprehensive_info(obj)
            elif obj.scs_props.locator_type == 'Model':
                info_txt = _locators.model.get_model_locator_comprehensive_info(obj)
            elif obj.scs_props.locator_type == 'Collision':
                info_txt = _locators.collider.get_collision_locator_comprehensive_info(obj)
            else:
                raise TypeError("Unsupported locator type: %s" % obj.scs_props.locator_type)

            cache[INFOS_DATA][obj] = info_txt

    def get_valid_locators(self, persp_matrix_str):
        """Gets list of locator objects that were cached for 2d locations for given perspective matrix string.

        :param persp_matrix_str: perspective matrix of 3d region converted to string
        :type persp_matrix_str: str
        :return: list of valid object or empty list if given perspective matrix has no cached 2d locations
        :rtype: list[bpy.types.Object]
        """
        cache = self.__cache[LOC_2D_CACHE][LOC_2D_VALID]

        if persp_matrix_str in cache:
            return cache[persp_matrix_str]
        else:
            return []

    def get_locator_location_2d(self, obj, persp_matrix_str):
        """Gets cached 2d location for given locator object with given perspective matrix string.

        :param obj: locator for which 2d location should be returned
        :type obj: bpy.types.Object
        :param persp_matrix_str: perspective matrixs of 3d region converted to string
        :type persp_matrix_str: str
        :return: vector of size 2 with cached x and y positions for given perspective matrix
        :rtype: mathutils.Vector
        """
        cache = self.__cache[LOC_2D_CACHE][LOC_2D_DATA]

        if obj in cache[persp_matrix_str]:
            return cache[persp_matrix_str][obj][1]
        else:
            raise KeyError("Given perspective matrix has no entries in locations cache, contact developer!")

    def get_locator_info(self, obj):
        """Gets cached comprehensive info of given locator object.

        :param obj: locator for which comprehensive info should be returned
        :type obj: bpy.types.Object
        :return: formatted string including new line separators
        :rtype: str
        """
        cache = self.__cache[INFOS_CACHE][INFOS_DATA]

        if obj in cache:
            return cache[obj]
        else:
            return "n/a"
