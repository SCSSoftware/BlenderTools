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
from bgl import GL_NEAREST
from bpy.props import StringProperty, BoolProperty, IntProperty
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import path as _path_utils


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
    width = IntProperty(default=300)
    height = IntProperty(default=20)

    @staticmethod
    def popup_draw(self, context):
        lines = ShowWarningMessage.static_message.split("\n")
        for line in lines:
            self.layout.label(line)

    def draw(self, context):
        row = self.layout.row().split(0.05)
        row.label(" ")

        col = row.column()
        col.label(self.title, icon=self.icon)
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
            return context.window_manager.invoke_props_dialog(self, width=self.width, height=self.height)
        else:
            return self.execute_popup(context)


class Show3DViewReport(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.show_3dview_report"

    __static_is_shown = True
    """Used for indicating collapsed state of reporter."""
    __static_hide_controls = False
    """Used for indicating controls visibility. Controls can be hidden if user shouldn't be able to abort report operator."""
    __static_running_instances = 0
    """Used for indication of already running operator."""
    __static_title = ""
    """Used for saving BT version inside class to be able to retrieve it on open gl draw."""
    __static_message_l = []
    """Used for saving message inside class to be able to retrieve it on open gl draw."""
    __static_progress_message_l = []
    """Used for saving progress message inside class to be able to retrieve it on open gl draw."""

    esc_abort = 0
    """Used for staging ESC key press in operator:
    0 - no ESC request
    1 - ESC was pressed
    2 - ESC was released, ESC is finally captured
    """

    title = StringProperty(default="")
    message = StringProperty(default="")
    abort = BoolProperty(default=False)
    hide_controls = BoolProperty(default=False)
    is_progress_message = BoolProperty(default=False)

    @staticmethod
    def has_lines():
        """Tells if report operator has any message to display.

        :return: True if there is any lines; False otherwise
        :rtype: bool
        """
        return len(Show3DViewReport.__static_message_l) > 0 or len(Show3DViewReport.__static_progress_message_l) > 0

    @staticmethod
    def has_controls():
        """Tells if report operator currently has enabled controls.

        :return: True if controls are enabled; False otherwise
        :rtype: bool
        """
        return not Show3DViewReport.__static_hide_controls

    @staticmethod
    def get_scs_logo_img_bindcode():
        """Loads image to blender data block, loads it to gl memory and gets bindcode address that can be used in
        bgl module for image drawing.

        :return: bindcode of scs bt logo image
        :rtype: int
        """

        if _OP_consts.View3DReport.BT_LOGO_IMG_NAME not in bpy.data.images:

            img_path = _path_utils.get_addon_installation_paths()[0] + "/ui/icons/" + _OP_consts.View3DReport.BT_LOGO_IMG_NAME
            img = bpy.data.images.load(img_path, check_existing=True)

        else:

            img = bpy.data.images[_OP_consts.View3DReport.BT_LOGO_IMG_NAME]

        # ensure that image is loaded in GPU memory aka has proper bindcode,
        # we have to that each time because if operator is shown for long time blender might free it on his own
        if img.bindcode[0] == 0:
            img.gl_load(0, GL_NEAREST, GL_NEAREST)

        return img.bindcode[0]

    @staticmethod
    def get_lines():
        """Get message as lines, divided by new lines.

        :return: message in lines
        :rtype: list[str]
        """
        lines = []
        lines.extend(Show3DViewReport.__static_progress_message_l)
        lines.extend(Show3DViewReport.__static_message_l)
        return lines

    @staticmethod
    def get_title():
        """Get title as string.

        :return: title which should be carrying info about Blender Tools version
        :rtype: str
        """
        return Show3DViewReport.__static_title

    @staticmethod
    def is_shown():
        """Tells if report is currently shown.

        :return: True if shown; False otherwise
        :rtype: bool
        """
        return Show3DViewReport.__static_is_shown

    @staticmethod
    def is_in_btn_area(x, y, btn_area):
        """Tells if given x and y coordinates are inside given area.

        :param x: x
        :type x: int
        :param y: y
        :type y: int
        :param btn_area: tuple holding x and y borders (min_x, max_x, min_y, max_y)
        :type btn_area: tuple
        :return: True if x and y are inside button area; False otherwise
        :rtype: bool
        """
        return (btn_area[0] < x < btn_area[1] and
                btn_area[2] < y < btn_area[3])

    def __init__(self):
        Show3DViewReport.__static_running_instances += 1

    def __del__(self):
        if Show3DViewReport.__static_running_instances > 0:

            Show3DViewReport.__static_running_instances -= 1

        # if user disables add-on, destructor is called again, so cleanup static variables
        if Show3DViewReport.__static_running_instances <= 0:

            Show3DViewReport.__static_title = ""
            Show3DViewReport.__static_message_l.clear()
            Show3DViewReport.__static_progress_message_l.clear()

    def modal(self, context, event):

        # if operator doesn't have controls, then it can not be cancelled by user,
        # so we should simply pass trough
        if not Show3DViewReport.has_controls():
            return {'PASS_THROUGH'}

        # handle ESC press
        # NOTE: do it in stages to prevent canceling operator while user tries to abort
        # current action in blender (for example user entered scaling and then aborted with ESC)
        if event.type == "ESC" and event.value == "PRESS" and self.esc_abort == 0:
            self.esc_abort = 1
        elif event.type == "ESC" and event.value == "RELEASE" and self.esc_abort == 1:
            self.esc_abort = 2
        elif event.type != "MOUSEMOVE":
            self.esc_abort = 0

        if (event.type == "LEFTMOUSE" and event.value in {'PRESS'}) or self.esc_abort == 2:

            # make sure to reset ESC abort state to 0 so next press will be properly handled
            if self.esc_abort == 2:
                self.esc_abort = 0

            for area in context.screen.areas:
                if area.type != 'VIEW_3D':
                    continue

                for region in area.regions:
                    if region.type != 'WINDOW':
                        continue

                    curr_x = event.mouse_x - region.x
                    curr_y = region.height - (event.mouse_y - region.y)

                    # if mouse cursor is over 3D view and ESC was pressed then switch to hide mode or exit operator
                    if event.type == "ESC" and area.x < event.mouse_x < area.x + area.width and area.y < event.mouse_y < area.y + area.height:

                        # if shown first hide extended view and then if hidden it can be closed
                        # NOTE: there is two stage exit on ESC because user might hit ESC unintentionally.
                        # Plus in case some transformation was in progress (like translation) ESC will cancel it and
                        # in worst case only hide 3d view logging operator, if stage ESC handling fails to capture that
                        if Show3DViewReport.__static_is_shown:

                            Show3DViewReport.__static_is_shown = False

                            _view3d_utils.tag_redraw_all_view3d()
                            return {'RUNNING_MODAL'}

                        else:

                            self.cancel(context)
                            return {'FINISHED'}

                    # also exit/cancel operator if Close button area was clicked
                    if Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.CLOSE_BTN_AREA):  # close
                        self.cancel(context)
                        return {'FINISHED'}

                    if Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.HIDE_BTN_AREA):  # show/hide

                        Show3DViewReport.__static_is_shown = not Show3DViewReport.__static_is_shown

                        _view3d_utils.tag_redraw_all_view3d()
                        return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def cancel(self, context):

        # free BT logo image resources
        if _OP_consts.View3DReport.BT_LOGO_IMG_NAME in bpy.data.images:

            img = bpy.data.images[_OP_consts.View3DReport.BT_LOGO_IMG_NAME]
            img.gl_free()

            bpy.data.images.remove(img, do_unlink=True)

        Show3DViewReport.__static_message_l.clear()
        Show3DViewReport.__static_progress_message_l.clear()

        _view3d_utils.tag_redraw_all_view3d()

    def invoke(self, context, event):

        # if abort is requested just cancel operator
        if self.abort:

            if self.is_progress_message:
                Show3DViewReport.__static_progress_message_l.clear()

                if len(Show3DViewReport.__static_message_l) > 0:
                    Show3DViewReport.__static_hide_controls = False
                else:
                    self.cancel(context)
            else:
                self.cancel(context)

            return {'CANCELLED'}

        # reset flags in static variables
        Show3DViewReport.__static_is_shown = True
        Show3DViewReport.__static_hide_controls = self.hide_controls

        # assign title to static variable
        Show3DViewReport.__static_title = self.title

        # split message by new lines
        message_l = []
        for line in self.message.split("\n"):

            # remove tabulator simulated new lines from warnings and errors, written like: "\n\t     "
            line = line.replace("\t     ", " " * 4)

            # remove tabulator simulated empty space before warning or error line of summaries e.g "\t   > "
            line = line.replace("\t   ", "")

            message_l.append(line)

        # properly assign parsed message list depending on progress flag
        if self.is_progress_message:
            Show3DViewReport.__static_progress_message_l = message_l
        else:
            Show3DViewReport.__static_message_l = message_l

        # if report operator is already running don't add new modal handler
        if Show3DViewReport.__static_running_instances > 1:
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ShowDeveloperErrors(bpy.types.Operator):
    bl_label = ""
    bl_description = "Show errors from stack. This was intended to be used only from batch import/export scripts."
    bl_idname = "wm.show_dev_error_messages"

    def execute(self, context):
        from io_scs_tools.utils.printout import dev_lprint

        dev_lprint()

        return {'FINISHED'}
