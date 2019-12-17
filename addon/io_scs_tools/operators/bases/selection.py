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


class Selection:
    """Base class for selecting operator which encorporates Shift and Ctrl selection.
    NOTE: Can not be used directly, only trough inheriting!
    """

    bl_base_description = " ( Shift + Click for adding to selection; Ctrl + Click to substract from selection )"

    UNDECIDED = _OP_consts.SelectionType.undecided
    DESELECT = _OP_consts.SelectionType.deselect
    SELECT = _OP_consts.SelectionType.select
    SHIFT_SELECT = _OP_consts.SelectionType.shift_select
    CTRL_SELECT = _OP_consts.SelectionType.ctrl_select

    select_type: IntProperty()

    def get_select_state(self):
        """Define selection state for objects depending on current select_type state.

        :return: new select state for the objects; or None if select_type was undecided
        :rtype: bool | None
        """

        actual_select_state = None

        # define type of (de)selection
        if self.select_type == self.SELECT or self.select_type == self.DESELECT:
            actual_select_state = bool(self.select_type)
            bpy.ops.object.select_all(action='DESELECT')

        elif self.select_type == self.SHIFT_SELECT:
            actual_select_state = True

        elif self.select_type == self.CTRL_SELECT:
            actual_select_state = False

        return actual_select_state

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):

        if event.shift:
            self.select_type = self.SHIFT_SELECT

        elif event.ctrl:
            self.select_type = self.CTRL_SELECT

        return self.execute(context)
