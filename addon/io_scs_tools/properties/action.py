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
from io_scs_tools.utils import animation as _animation
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty)


class ActionSCSTools(bpy.types.PropertyGroup):
    """
    SCS Tools Action Variables - ...Action.scs_props...
    :return:
    """

    def action_length_update(self, context):
        """
        :param context:
        :return:
        """
        if context.active_object:
            if context.active_object.animation_data:
                action = context.active_object.animation_data.action
                if action:
                    frame_range = action.frame_range
                    _animation.set_fps(context.scene, action, frame_range)

    export_action = BoolProperty(
        name="Export With Model",
        description="Status specifying whether this Action is automatically exported upon Model export",
        default=True,
    )
    action_length = FloatProperty(
        name="Action Length",
        description="Action total length (in seconds)",
        default=10.0,
        min=0.1,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
        precision=6,
        update=action_length_update,
    )
    anim_export_step = IntProperty(
        name="Export Step",
        description="Skip this amount of frames upon animation export",
        default=1,
        min=0, max=128,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
    )
    anim_export_filepath = StringProperty(
        name="Alternative Export Path",
        description="Alternative custom file path for export of animation",
        # default=utils.get_cgfx_templates_filepath(),
        default="",
        subtype="FILE_PATH",
        # update=anim_export_filepath_update,
    )