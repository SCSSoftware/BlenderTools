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
from bpy.props import IntProperty
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.utils import object as _object_utils


class View:
    """Base class for operators for switching view state of objects which encorporates Shift and Ctrl viewing.
    NOTE: Can not be used directly, only trough inheriting!
    """

    bl_base_description = " ( Shift + Click for adding to already visible; Ctrl + Click to substract from already visible )"

    UNDECIDED = _OP_consts.ViewType.undecided
    HIDE = _OP_consts.ViewType.hide
    VIEWONLY = _OP_consts.ViewType.viewonly
    SHIFT_VIEW = _OP_consts.ViewType.shift_view
    CTRL_VIEW = _OP_consts.ViewType.ctrl_view

    view_type: IntProperty(default=VIEWONLY)

    @staticmethod
    def get_objects(context):
        if context.workspace.scs_props.visibility_tools_scope == "Global":

            objects = context.scene.objects

        else:

            scs_root_object = _object_utils.get_scs_root(context.view_layer.objects.active)
            if scs_root_object:
                objects = _object_utils.get_children(scs_root_object)
                _object_utils.hide_set(scs_root_object, False)
                _object_utils.select_set(scs_root_object, True)
                bpy.context.view_layer.objects.active = scs_root_object
            else:  # fallback don't do anything
                objects = []

        return objects

    def get_hide_state(self):
        """Define hide state for objects depending on current view_type state.

        :return: new hide state for the objects; or None if view_type was undecided
        :rtype: bool | None
        """

        object_hide = None

        # define type of (de)selection
        if self.view_type == self.VIEWONLY:
            object_hide = False
            bpy.ops.object.scs_tools_hide_objects_within_scs_root()

        elif self.view_type == self.SHIFT_VIEW:
            object_hide = False

        elif self.view_type in (self.CTRL_VIEW, self.HIDE):
            object_hide = True

        return object_hide

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):

        if event.shift:
            self.view_type = self.SHIFT_VIEW

        elif event.ctrl:
            self.view_type = self.CTRL_VIEW

        return self.execute(context)
