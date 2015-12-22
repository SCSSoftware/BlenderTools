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

from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import info as _info_utils


class ShowWarningMessage(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.show_warning_message"

    static_message = ""
    """Used for saving message inside class to be able to retrieve it on popup draw."""

    is_modal = BoolProperty(default=False)
    icon = StringProperty(default="ERROR")
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
        context.window_manager.popup_menu(self.popup_draw, title=self.title, icon=self.icon)
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        ShowWarningMessage.static_message = self.message

        if self.is_modal:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute_popup(context)


class Show3DViewReport(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.show_3dview_report"

    __static_is_shown = True
    """Used for indicating collapsed state of reporter."""
    __static_running_instances = 0
    """Used for indication of already running operator."""
    __static_message_l = []
    """Used for saving message inside class to be able to retrieve it on open gl draw."""

    title = StringProperty(default="UNKWOWN")
    message = StringProperty(default="NO MESSAGE")
    abort = BoolProperty(default=False)

    @staticmethod
    def has_lines():
        """Tells if report operator has any message to display.

        :return: True if there is any lines; False otherwise
        :rtype: bool
        """
        return len(Show3DViewReport.__static_message_l) > 0

    @staticmethod
    def get_lines():
        """Get message as lines, divided by new lines.

        :return: message in lines
        :rtype: list[str]
        """
        return Show3DViewReport.__static_message_l

    @staticmethod
    def is_shown():
        """Tells if report is currently shown.

        :return: True if shown; False otherwise
        :rtype: bool
        """
        return Show3DViewReport.__static_is_shown

    def __del__(self):
        Show3DViewReport.__static_running_instances -= 1

    def __init__(self):
        Show3DViewReport.__static_running_instances += 1

    def modal(self, context, event):

        if event.type == "LEFTMOUSE" and event.value in {'PRESS'}:

            for area in context.screen.areas:
                if area.type != 'VIEW_3D':
                    continue

                for region in area.regions:
                    if region.type != 'WINDOW':
                        continue

                    curr_x = event.mouse_x - region.x
                    curr_y = region.height - (event.mouse_y - region.y)

                    if 20 < curr_x < 95 and 38 < curr_y < 62:  # close
                        self.cancel(context)
                        return {'FINISHED'}

                    if 100 < curr_x < 250 and 38 < curr_y < 62:  # show/hide

                        Show3DViewReport.__static_is_shown = not Show3DViewReport.__static_is_shown

                        _view3d_utils.tag_redraw_all_view3d()
                        return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def cancel(self, context):

        Show3DViewReport.__static_message_l.clear()

        _view3d_utils.tag_redraw_all_view3d()

    def invoke(self, context, event):

        # if abort is requested just cancel operator
        if self.abort:
            self.cancel(context)
            return {'FINISHED'}

        # reset messages array and shown state
        Show3DViewReport.__static_is_shown = True
        Show3DViewReport.__static_message_l.clear()

        # add blender tools version in the header
        Show3DViewReport.__static_message_l.append(_info_utils.get_combined_ver_str())

        # split message by new lines
        for line in self.message.split("\n"):

            # adapt number of spaces by message type
            space_count = 22 if line.startswith("WARNING") else 18

            # remove tabulator simulated new lines from warnings and errors, written like: "\n\t   "
            line = line.replace("\t   ", " " * space_count)

            # make sure to get rid of any other tabulators and change them for space eg: "INFO\t-"
            line = line.replace("\t", " ")

            Show3DViewReport.__static_message_l.append(line)

        # if report operator is already running don't add new modal handler
        if Show3DViewReport.__static_running_instances == 1:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'FINISHED'}


class ShowDeveloperErrors(bpy.types.Operator):
    bl_label = ""
    bl_description = "Show errors from stack"
    bl_idname = "wm.show_dev_error_messages"

    def execute(self, context):
        from io_scs_tools.utils.printout import dev_lprint

        dev_lprint()

        return {'FINISHED'}
