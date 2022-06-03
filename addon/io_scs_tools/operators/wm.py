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
import os
from bpy.props import StringProperty, BoolProperty, IntProperty
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import path as _path_utils


class SCS_TOOLS_OT_ShowMessageInPopup(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.scs_tools_show_message_in_popup"

    static_message = ""
    """Used for saving message inside class to be able to retrieve it on popup draw."""

    is_modal: BoolProperty(default=False)
    icon: StringProperty(default="ERROR")
    title: StringProperty(default="UNKWOWN")
    message: StringProperty(default="NO MESSAGE")
    width: IntProperty(default=300)
    height: IntProperty(default=20)

    @staticmethod
    def popup_draw(self, context):
        lines = SCS_TOOLS_OT_ShowMessageInPopup.static_message.split("\n")
        for line in lines:
            self.layout.label(text=line)

    def draw(self, context):
        row = self.layout.row().split(factor=0.00001 * self.width)
        row.label(text=" ")

        col = row.column()
        col.label(text=self.title, icon=self.icon)
        col.separator()
        lines = self.message.split("\n")
        for line in lines:
            col.label(text=line.strip())
        col.separator()
        col.separator()

    def execute_popup(self, context):
        context.window_manager.popup_menu(self.popup_draw, title=self.title, icon=self.icon)
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        SCS_TOOLS_OT_ShowMessageInPopup.static_message = self.message

        if self.is_modal:
            return context.window_manager.invoke_props_dialog(self, width=self.width, height=self.height)
        else:
            return self.execute_popup(context)


class SCS_TOOLS_OT_Show3DViewReport(bpy.types.Operator):
    bl_label = ""
    bl_description = "Click for additional information."
    bl_idname = "wm.scs_tools_show_3dview_report"

    __static_is_shown = True
    """Used for indicating collapsed state of reporter."""
    __static_hide_controls = False
    """Used for indicating controls visibility. Controls can be hidden if user shouldn't be able to abort report operator."""
    __static_main_instance = None
    """Used for indication of main instance and abortion of the rest."""
    __static_window_instance = None
    """Used for indication on which window instance modal handler is currently added."""
    __static_title = ""
    """Used for saving BT version inside class to be able to retrieve it on open gl draw."""
    __static_message_l = []
    """Used for saving message inside class to be able to retrieve it on open gl draw."""
    __static_progress_message_l = []
    """Used for saving progress message inside class to be able to retrieve it on open gl draw."""
    __static_abort = False
    """Used to propage abort message to all instances, so when abort is requested all instances will kill itself."""
    __static_scroll_pos = 0
    """Used to designate current scroll position in case not all warnings can be shown in 3D view."""
    __static_x_offset = 0
    __static_y_offset = 0
    """Used to designate X and Y offset from corner of drawing region (compensation for header and tools panels dynamic width))"""
    __static_is_out_of_bounds = False
    """Used for indicating whether all lines could be drawn into the region."""

    title: StringProperty(default="")
    message: StringProperty(default="")
    abort: BoolProperty(default=False)
    hide_controls: BoolProperty(default=False)
    is_progress_message: BoolProperty(default=False)
    modal_handler_reassign: BoolProperty(default=False)

    @staticmethod
    def has_lines():
        """Tells if report operator has any message to display.

        :return: True if there is any lines; False otherwise
        :rtype: bool
        """
        return len(SCS_TOOLS_OT_Show3DViewReport.__static_message_l) > 0 or len(SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l) > 0

    @staticmethod
    def has_controls(window):
        """Tells if report operator currently has enabled controls and given window is the one having model handler added.

        :param window: window on which we should check for controls
        :type window: bpy.type.Window
        :return: True if controls are enabled; False otherwise
        :rtype: bool
        """
        return window == SCS_TOOLS_OT_Show3DViewReport.__static_window_instance and not SCS_TOOLS_OT_Show3DViewReport.__static_hide_controls

    @staticmethod
    def get_scs_banner_img_data(window):
        """Loads image to blender data block, loads it to gl memory and gets bindcode address that can be used in
        bgl module for image drawing.

        :param window: window for which we should get banner image
        :type window: bpy.type.Window
        :return: (bindcode of scs banner image, width of scs banner image, height of scs banner image
        :rtype: (int, int, int)
        """

        if SCS_TOOLS_OT_Show3DViewReport.has_controls(window):
            img_name = _OP_consts.View3DReport.BT_BANNER_WITH_CTRLS_IMG_NAME
        else:
            img_name = _OP_consts.View3DReport.BT_BANNER_IMG_NAME

        if img_name not in bpy.data.images:

            img_path = os.path.join(_path_utils.get_addon_installation_paths()[0], "ui", "banners", img_name)
            img = bpy.data.images.load(img_path, check_existing=True)
            img.colorspace_settings.name = 'sRGB'

        else:

            img = bpy.data.images[img_name]

        # ensure that image is loaded in GPU memory aka has proper bindcode,
        # we have to that each time because if operator is shown for long time blender might free it on it's own
        if img.bindcode == 0:
            img.gl_load()

        return img.bindcode, img.size[0], img.size[1]

    @staticmethod
    def get_lines():
        """Get message as lines, divided by new lines.

        :return: message in lines
        :rtype: list[str]
        """
        lines = []
        lines.extend(SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l)
        lines.extend(SCS_TOOLS_OT_Show3DViewReport.__static_message_l)

        # do scrolling

        lines_to_scroll = SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos
        while lines_to_scroll > 0:
            lines.pop(0)
            lines_to_scroll = lines_to_scroll - 1

        return lines

    @staticmethod
    def get_title():
        """Get title as string.

        :return: title which should be carrying info about Blender Tools version
        :rtype: str
        """
        return SCS_TOOLS_OT_Show3DViewReport.__static_title

    @staticmethod
    def is_shown():
        """Tells if report is currently shown.

        :return: True if shown; False otherwise
        :rtype: bool
        """
        return SCS_TOOLS_OT_Show3DViewReport.__static_is_shown

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
        return (btn_area[0] < (x - SCS_TOOLS_OT_Show3DViewReport.__static_x_offset) < btn_area[1] and
                btn_area[2] < (y - SCS_TOOLS_OT_Show3DViewReport.__static_y_offset) < btn_area[3])

    @staticmethod
    def is_scrolled():
        """Tells if text is scrolled down.

        :return: True if we are not on zero scroll position; False otherwise
        :rtype: bool
        """
        return SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos != 0 or SCS_TOOLS_OT_Show3DViewReport.__static_is_out_of_bounds

    @staticmethod
    def set_out_of_bounds(state):
        """Sets state of the 3D view drawing buffer. If set to true it means, that not all lines could be displayed.

        :param state: True if not all lines could be displayed; False otherwise
        :type state: bool
        """
        SCS_TOOLS_OT_Show3DViewReport.__static_is_out_of_bounds = state

    @staticmethod
    def set_btns_xy_offset(x, y):
        """Sets offset for controls area inclusion calculation in is_in_btn_area method.

        :param x: X offset in pixels designating left margin for drawing of our controls
        :type x: int
        :param y: Y offset in pixels designating top margin for drawing of our controls
        :type y: int
        """
        SCS_TOOLS_OT_Show3DViewReport.__static_x_offset = x
        SCS_TOOLS_OT_Show3DViewReport.__static_y_offset = y

    @staticmethod
    def discard_drawing_data():
        """Discards drawing by cleaning static messages and removing banner image.
        """

        # free BT logo image resources
        if _OP_consts.View3DReport.BT_BANNER_IMG_NAME in bpy.data.images:

            img = bpy.data.images[_OP_consts.View3DReport.BT_BANNER_IMG_NAME]
            img.gl_free()

            bpy.data.images.remove(img, do_unlink=True)

        SCS_TOOLS_OT_Show3DViewReport.__static_title = ""
        SCS_TOOLS_OT_Show3DViewReport.__static_message_l.clear()
        SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l.clear()

        # trigger redraw so 3d view reports will be removed
        _view3d_utils.tag_redraw_all_view3d()

    @classmethod
    def unregister(cls):
        """Called on unregister of class.
        """
        SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()

    def fill_drawing_data(self):
        """Fills drawing data into static variables, so they can be used by drawing methods of open gl.
        """

        # reset flags in static variables
        SCS_TOOLS_OT_Show3DViewReport.__static_is_shown = True
        SCS_TOOLS_OT_Show3DViewReport.__static_hide_controls = self.hide_controls
        SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos = 0

        # assign title to static variable
        SCS_TOOLS_OT_Show3DViewReport.__static_title = self.title

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
            SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l = message_l
        else:
            SCS_TOOLS_OT_Show3DViewReport.__static_message_l = message_l

    def cancel(self, context):
        # find oldest main window for possible re-call of the operator
        oldest_main_window = None
        if bpy.context.window_manager:
            for window in bpy.context.window_manager.windows:
                if not window.parent:
                    oldest_main_window = window
                    break

        # when operator get's cancelled, either user closed blender or window itself, in which our operator was handled.
        # Thus make sure to re-call on exisiting oldest main window, so that 3d view opearator "reopens"
        if oldest_main_window and SCS_TOOLS_OT_Show3DViewReport.__static_window_instance != oldest_main_window:
            override = bpy.context.copy()
            override["window"] = oldest_main_window
            bpy.ops.wm.scs_tools_show_3dview_report(override, 'INVOKE_DEFAULT', modal_handler_reassign=True)
            _view3d_utils.tag_redraw_all_view3d()
        else:
            SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()

    def modal(self, context, event):

        # if not main instance finish
        if SCS_TOOLS_OT_Show3DViewReport.__static_main_instance != self:
            return {'FINISHED'}

        # if global abort was requested finish this modal operator instance
        if SCS_TOOLS_OT_Show3DViewReport.__static_abort:
            return {'FINISHED'}

        # if operator doesn't have controls, then it can not be cancelled by user,
        # so we should simply pass trough
        if not SCS_TOOLS_OT_Show3DViewReport.has_controls(SCS_TOOLS_OT_Show3DViewReport.__static_window_instance):
            return {'PASS_THROUGH'}

        if (event.type == 'LEFTMOUSE' and event.value == 'PRESS') or (event.type == 'ESC' and event.value == 'CLICK'):

            # search for first 3d view region
            # we need this as a workaround since provided context region and area are None for some reason
            view3d_region = None
            view3d_area = None
            for area in context.screen.areas:
                if area.type != 'VIEW_3D':
                    continue

                for region in area.regions:
                    if region.type == 'WINDOW':
                        view3d_region = region
                        break

                if view3d_region:
                    view3d_area = area
                    break

            # cancel operator if no 3dview present
            if not view3d_region:
                SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()
                return {'FINISHED'}

            curr_x = event.mouse_x - view3d_region.x
            curr_y = view3d_region.height - (event.mouse_y - view3d_region.y)

            area_y_max = view3d_area.y + view3d_area.height
            aray_x_max = view3d_area.x + view3d_area.width

            # if mouse cursor is over 3D view and ESC was pressed then switch to hide mode or exit operator
            if event.type == 'ESC' and view3d_area.x < event.mouse_x < aray_x_max and view3d_area.y < event.mouse_y < area_y_max:

                # if shown first hide extended view and then if hidden it can be closed
                # NOTE: there is two stage exit on ESC because user might hit ESC unintentionally.
                # Plus in case some transformation was in progress (like translation) ESC will cancel it and
                # in worst case only hide 3d view logging operator, if stage ESC handling fails to capture that
                if SCS_TOOLS_OT_Show3DViewReport.__static_is_shown:

                    SCS_TOOLS_OT_Show3DViewReport.__static_is_shown = False

                    _view3d_utils.tag_redraw_all_view3d()
                    return {'RUNNING_MODAL'}

                else:

                    SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()
                    return {'FINISHED'}

            # also exit/cancel operator if Close button area was clicked
            if SCS_TOOLS_OT_Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.CLOSE_BTN_AREA):  # close
                SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()
                return {'FINISHED'}

            if SCS_TOOLS_OT_Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.HIDE_BTN_AREA):  # show/hide

                SCS_TOOLS_OT_Show3DViewReport.__static_is_shown = not SCS_TOOLS_OT_Show3DViewReport.__static_is_shown
                _view3d_utils.tag_redraw_all_view3d()
                return {'RUNNING_MODAL'}

            # scroll up/down
            if SCS_TOOLS_OT_Show3DViewReport.is_shown() and SCS_TOOLS_OT_Show3DViewReport.is_scrolled():

                if SCS_TOOLS_OT_Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.SCROLLUP_BTN_AREA):
                    new_position = SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos - 5
                    min_position = 0
                    SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos = max(new_position, min_position)
                    _view3d_utils.tag_redraw_all_view3d()
                    return {'RUNNING_MODAL'}

                if SCS_TOOLS_OT_Show3DViewReport.is_in_btn_area(curr_x, curr_y, _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA):
                    new_position = SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos + 5
                    max_position = (
                            len(SCS_TOOLS_OT_Show3DViewReport.__static_message_l) +
                            len(SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l) - 1
                    )
                    SCS_TOOLS_OT_Show3DViewReport.__static_scroll_pos = min(new_position, max_position)
                    _view3d_utils.tag_redraw_all_view3d()
                    return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        # propagate abort to all instances trough static variable
        SCS_TOOLS_OT_Show3DViewReport.__static_abort = self.abort

        # if abort is requested just cancel operator
        if self.abort:

            if self.is_progress_message:
                SCS_TOOLS_OT_Show3DViewReport.__static_progress_message_l.clear()

                if len(SCS_TOOLS_OT_Show3DViewReport.__static_message_l) > 0:
                    SCS_TOOLS_OT_Show3DViewReport.__static_hide_controls = False
                else:
                    SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()
            else:
                SCS_TOOLS_OT_Show3DViewReport.discard_drawing_data()

            return {'CANCELLED'}

        # use current instance as main
        SCS_TOOLS_OT_Show3DViewReport.__static_main_instance = self

        # save window on which modal handler will be added,
        # so we will be able to keep 3d view reports alive if user closes this window (see cancel method)
        SCS_TOOLS_OT_Show3DViewReport.__static_window_instance = context.window

        # data shouldn't be changed if we are reassiging modal handler
        if not self.modal_handler_reassign:
            self.fill_drawing_data()

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class SCS_TOOLS_OT_ShowDeveloperErrors(bpy.types.Operator):
    bl_label = ""
    bl_description = "Show errors from stack. This was intended to be used only from batch import/export scripts."
    bl_idname = "wm.scs_tools_show_developer_errors"

    def execute(self, context):
        from io_scs_tools.utils.printout import dev_lprint

        dev_lprint()

        return {'FINISHED'}


classes = (
    SCS_TOOLS_OT_Show3DViewReport,
    SCS_TOOLS_OT_ShowDeveloperErrors,
    SCS_TOOLS_OT_ShowMessageInPopup
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
