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


def get_all_spaces(screen=None):
    """Gets all the spaces in Blender which are type of bpy.types.SpaceView3D

    :param screen: blender screen; if None is given all screens are taken from window manager
    :type screen: bpy.types.Screen
    :return: all the spaces of type bpy.types.SpaceView3D
    :rtype: list of bpy.types.SpaceView3D
    """
    screens = set()
    if not screen:
        for wnd in bpy.context.window_manager.windows:
            screens.add(wnd.screen)
    else:
        screens.add(screen)

    spaces = []
    for screen in screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if isinstance(space, bpy.types.SpaceView3D):
                        spaces.append(space)

    return spaces


def has_multiple_view3d_spaces(screen=None):
    """Tells if given blender screen has multile 3D views or not.

    :param screen: blender screen; if None is given all screens are taken from window manager
    :type screen: bpy.types.Screen
    :return: True if at leas one 3d view is present; False otherwise
    :rtype: bool
    """

    screens = set()
    if not screen:
        for wnd in bpy.context.window_manager.windows:
            screens.add(wnd.screen)
    else:
        screens.add(screen)

    spaces_count = 0
    for scr in screens:
        for area in scr.areas:

            if area.type == 'VIEW_3D':
                spaces_count += 1

            if spaces_count > 1:
                return True

    return False


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


def get_spaces_with_local_view(screen=None):
    """Gets all spaces of current screen that currently have active local view.

    :param screen: blender screen; if None is given all screens are taken from window manager
    :type screen: bpy.types.Screen
    :return: list of local view spaces
    :rtype: list[bpy.types.SpaceView3D]
    """
    spaces = []
    for space in get_all_spaces(screen):
        if space.local_view:
            spaces.append(space)

    return spaces


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
