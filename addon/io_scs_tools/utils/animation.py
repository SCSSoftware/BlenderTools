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

from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import name as _name


def add_animation_to_root(scs_root_object, animation_name="Default"):
    animation_inventory = scs_root_object.scs_object_animation_inventory

    # ENSURE, THAT THE NAME IS UNIQUE
    while animation_name in animation_inventory:
        animation_name = _name.get_unique(animation_name)

    # ADD THE ANIMATION
    lprint('I Adding a Animation name: "%s"', animation_name)
    animation = animation_inventory.add()
    animation.name = animation_name
    animation.active = True
    return animation


def set_fps(scene, action, frame_range):
    """

    :param scene:
    :type scene:
    :param action:
    :type action:
    :param frame_range:
    :type frame_range:
    :return:
    :rtype:
    """
    action_length = action.scs_props.action_length
    fps = (frame_range[1] - frame_range[0]) / action_length
    scene.render.fps = round(fps)


def set_fps_for_preview(scene, length, anim_export_step, start_frame, end_frame):
    """

    :param scene:
    :type scene:
    :param length:
    :type length:
    :param anim_export_step:
    :type anim_export_step:
    :param start_frame:
    :type start_frame:
    :param end_frame:
    :type end_frame:
    :return:
    :rtype:
    """
    fps = ((end_frame - start_frame) / length) * anim_export_step
    scene.render.fps = round(fps)


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