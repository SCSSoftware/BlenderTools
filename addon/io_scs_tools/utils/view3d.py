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
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def switch_local_view(show):
    """Switches first space in VIEW_3D areas to local or switches back to normal

    :param show: True if local view should be shown; False for switching back to normal view
    :type show: bool
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            if show and area.spaces[0].local_view is None:
                lprint("D Going into local view!")
                override = {
                    'window': bpy.context.window,
                    'screen': bpy.context.screen,
                    'blend_data': bpy.context.blend_data,
                    'scene': bpy.context.scene,
                    'region': area.regions[4],
                    'area': area
                }
                bpy.ops.view3d.localview(override)
            elif not show and area.spaces[0].local_view is not None:
                lprint("D Returning from local view!")
                override = {
                    'window': bpy.context.window,
                    'screen': bpy.context.screen,
                    'blend_data': bpy.context.blend_data,
                    'scene': bpy.context.scene,
                    'region': area.regions[4],
                    'area': area
                }
                bpy.ops.view3d.localview(override)

    if _get_scs_globals().preview_export_selection_active != show:
        _get_scs_globals().preview_export_selection_active = show
        # redraw properties panels because of preview property change
        for area in bpy.context.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()


def get_all_spaces():
    """Gets all the spaces in Blender which are type of bpy.types.SpaceView3D

    :return: all the spaces of type bpy.types.SpaceView3D
    :rtype: list of bpy.types.SpaceView3D
    """
    spaces = []
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if isinstance(space, bpy.types.SpaceView3D):
                    spaces.append(space)

    return spaces


def has_view3d_space(screen):
    """Tells if given blender screen has 3D view or not.

    :param screen: blender screen
    :type screen: bpy.types.Screen
    :return: True if at leas one 3d view is present; False otherwise
    :rtype: bool
    """

    if screen is None:
        return False

    for area in screen.areas:
        if area.type == 'VIEW_3D':
            return True

    return False


def switch_layers_visibility(storage_list, show):
    """Switches visibility of layers in Blender. If show is True all layers on current scene
        and local layers of current 3D spaces are shown. If storage_list is provided it tries
        to restore visibilites from entries.

        WARNING: this function can restore only storage_list which was created with this function
        otherwise it may raise error.

    :param storage_list: list where previous layers visibility states are or should be stored into
    :type storage_list: list
    :param show: flag for indicating if all layers should be shown (value True) or restored (value False)
    :type show: bool
    :return: states of layers visibilites for scene and local layers of views
    :rtype: list of list(bool*20)
    """

    for space in get_all_spaces():
        if show:
            storage_list.append(list(space.layers))
            space.layers = [True] * 20
            lprint("D Layers visibility set to True")
        elif len(storage_list) > 0:
            space.layers = storage_list[0]
            storage_list = storage_list[1:]

    scene = bpy.context.scene
    if show:
        storage_list.append(list(scene.layers))
        scene.layers = [True] * 20
    elif len(storage_list) > 0:
        scene.layers = storage_list[0]
        storage_list = storage_list[1:]

    return storage_list


def tag_redraw_all_view3d():
    # NOTE: Py can't access notifiers!
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


def tag_redraw_all_view3d_and_props():
    # NOTE: Py can't access notifiers!
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type in {'VIEW_3D', 'PROPERTIES'}:
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


def tag_redraw_all_regions():
    # NOTE: Py can't access notifiers!
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for region in area.regions:
                region.tag_redraw()
