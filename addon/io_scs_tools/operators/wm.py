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

# Copyright (C) 2013-2015: SCS Software

import bpy

from bpy.props import StringProperty, BoolProperty


class ShowWarningMessage(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.show_warning_message"

    static_message = ""
    """Used for saving message inside class to be able to retrieve it on popup draw."""

    is_modal = BoolProperty(default=False)
    title = StringProperty(default="UNKWOWN")
    message = StringProperty(default="NO MESSAGE")

    @staticmethod
    def popup_draw(self, context):
        lines = ShowWarningMessage.static_message.split("\n")
        for line in lines:
            self.layout.label(line)

    def draw(self, context):
        row = self.layout.row().split(0.05)
        row.label(" ")

        col = row.column()
        col.label(self.title, icon="ERROR")
        lines = self.message.split("\n")
        for line in lines:
            col.label(line)

    def execute_popup(self, context):
        context.window_manager.popup_menu(self.popup_draw, title=self.title, icon="ERROR")
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        ShowWarningMessage.static_message = self.message

        if self.is_modal:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute_popup(context)
