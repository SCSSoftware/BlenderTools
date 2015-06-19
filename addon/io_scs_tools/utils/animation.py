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

from math import pi
from io_scs_tools.utils import name as _name


def add_animation_to_root(scs_root_object, animation_name):
    animation_inventory = scs_root_object.scs_object_animation_inventory

    # ENSURE, THAT THE NAME IS UNIQUE
    animation_name = _name.get_unique(animation_name, animation_inventory)

    # ADD THE ANIMATION
    animation = animation_inventory.add()
    animation.name = animation_name
    return animation


def set_fps_for_preview(scene, length, start_frame, end_frame):
    """

    :param scene:
    :type scene:
    :param length:
    :type length:
    :param start_frame:
    :type start_frame:
    :param end_frame:
    :type end_frame:
    :return:
    :rtype:
    """
    fps = ((end_frame - start_frame) / length)
    scene.render.fps = round(fps)


def set_frame_range(scene, start_frame, end_frame):
    """Sets scene frame range so animation will be player inside given interval

    :param scene: active scene
    :type scene: bpy.types.Scene
    :param start_frame: start frame
    :type start_frame: int
    :param end_frame: end frame
    :type end_frame: int
    """
    scene.use_preview_range = True
    scene.frame_set(start_frame)  # always set current frame to start frame
    scene.frame_preview_start = start_frame
    scene.frame_preview_end = end_frame


def get_armature_action(context):
    """
    If the active object is an Armature object and has an animation Action,
    this function returns that Action object or None.
    :param context:
    :return:
    """
    action = None
    if context.active_object:
        if context.active_object.type == 'ARMATURE':
            if context.active_object.animation_data.action:
                action = context.active_object.animation_data.action
    return action


def apply_euler_filter(fcv):
    """Applies euler filter for solving dicontinued rotation curve keys.
    NOTE: this will be used only on euler rotation curves; all other curves will be rejected

    :param fcv: euler rotation curve on which filter should be applied
    :type fcv: bpy.types.FCurve
    """

    # apply filter only on euler rotation curves
    if not fcv.data_path.endswith("rotation_euler"):
        return

    keys = []

    for k in fcv.keyframe_points:
        keys.append(k.co.copy())

    for i in range(len(keys)):
        curr_key = keys[i]
        prev_key = keys[i - 1] if i > 0 else None

        if prev_key is None:
            continue

        th = pi
        if abs(prev_key[1] - curr_key[1]) >= th:  # more than 180 degree jump
            fac = pi * 2
            if prev_key[1] > curr_key[1]:
                while abs(curr_key[1] - prev_key[1]) >= th:
                    curr_key[1] += fac
            elif prev_key[1] < curr_key[1]:
                while abs(curr_key[1] - prev_key[1]) >= th:
                    curr_key[1] -= fac

    # copy keys back to curve
    for i in range(len(keys)):
        for x in range(2):
            fcv.keyframe_points[i].co[x] = keys[i][x]