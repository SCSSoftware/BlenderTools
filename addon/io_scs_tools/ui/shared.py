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
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.icons import get_icon

_ICON_TYPES = _ICONS_consts.Types


class HeaderIconPanel:
    """
    Holds the function for drawing icon in header section of Panel
    """

    is_popover = None  # predefined Blender variable to avoid warnings in PyCharm

    def draw_header(self, context):
        if not self.is_popover:
            self.layout.label(text="", icon_value=get_icon(_ICON_TYPES.scs_logo))


class SCS_TOOLS_UL_ObjectLookSlots(bpy.types.UIList):
    """
    Draw look item slot within SCS Looks list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon)

        # DEBUG
        if int(_get_scs_globals().dump_level) > 2:
            layout.label(text="DEBUG - id: " + str(item.id))


def draw_scs_looks_panel(layout, active_object, scs_root_object, without_box=False):
    """Creates 'SCS Looks' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param active_object: active object
    :type active_object: bpy.types.Object
    :param scs_root_object: SCS Root Object
    :type scs_root_object: bpy.types.Object
    :param without_box: draw without extra box layout?
    :type without_box: bool
    """

    layout_column = layout.column(align=True)

    if without_box:
        layout_box = layout_column
    else:
        layout_box = layout_column.box()

    if len(_object_utils.gather_scs_roots(bpy.context.selected_objects)) > 1 and active_object is not scs_root_object:

        warning_box = layout_box.column(align=True)

        header = warning_box.box()
        header.label(text="WARNING", icon='ERROR')
        body = warning_box.box()
        col = body.column(align=True)
        col.label(text="Can not edit looks!")
        col.label(text="Selection has multiple game objects.")

    else:  # more roots or active object is root object

        row = layout_box.row()
        row.template_list(
            SCS_TOOLS_UL_ObjectLookSlots.__name__,
            list_id="",
            dataptr=scs_root_object,
            propname="scs_object_look_inventory",
            active_dataptr=scs_root_object.scs_props,
            active_propname="active_scs_look",
            rows=3,
            maxrows=5,
            type='DEFAULT',
            columns=9
        )

        # LIST BUTTONS
        col = row.column(align=True)
        col.operator('object.scs_tools_add_look', text="", icon='ADD')
        col.operator('object.scs_tools_remove_active_look', text="", icon='REMOVE')


def draw_export_panel(layout, ignore_extra_boxes=False):
    box1 = layout.box() if not ignore_extra_boxes else layout

    box1.use_property_split = True
    box1.use_property_decorate = False

    box1.prop(_get_scs_globals(), 'export_scale')

    flow = box1.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
    col = flow.column()
    col.prop(_get_scs_globals(), 'export_apply_modifiers')
    col = flow.column()
    if _get_scs_globals().export_output_type.startswith('EF'):
        col.enabled = _get_scs_globals().export_apply_modifiers
        col.prop(_get_scs_globals(), 'export_exclude_edgesplit')
    else:
        col.enabled = not _get_scs_globals().export_apply_modifiers
        col.prop(_get_scs_globals(), 'export_include_edgesplit')
    '''
    col.prop(_get_scs_globals(), 'export_active_uv_only')
    if not _get_scs_globals().export_output_type.startswith('EF'):
        col.prop(_get_scs_globals(), 'export_vertex_groups')
    col.prop(_get_scs_globals(), 'export_vertex_color')
    if _get_scs_globals().export_vertex_color:
        row = box1.row()
        if not _get_scs_globals().export_output_type.startswith('EF'):
            row.prop(_get_scs_globals(), 'export_vertex_color_type_7')
        else:
            row.prop(_get_scs_globals(), 'export_vertex_color_type')
    '''
    # row = box1.row()
    # row.prop(_get_scs_globals(), 'export_anim_file', expand=True)
    box2 = layout.box() if not ignore_extra_boxes else layout
    box2.use_property_split = True
    box2.use_property_decorate = False
    box2.prop(_get_scs_globals(), 'export_output_type')
    '''
    col = box2.column()
    col.prop(_get_scs_globals(), 'export_pim_file', text="Export Model (PIM)", toggle=True)
    if _get_scs_globals().export_pim_file:
        col.prop(_get_scs_globals(), 'export_output_type')
    col.prop(_get_scs_globals(), 'export_pit_file', text="Export Trait (PIT)", toggle=True)
    col.prop(_get_scs_globals(), 'export_pic_file', text="Export Collision (PIC)", toggle=True)
    col.prop(_get_scs_globals(), 'export_pip_file', text="Export Prefab (PIP)", toggle=True)
    row = col.row()
    if _get_scs_globals().export_anim_file == 'anim':
        row.enabled = True
    else:
        row.enabled = False
    row.prop(_get_scs_globals(), 'export_pis_file', text="Export Skeleton (PIS)", toggle=True)
    row = col.row()
    if _get_scs_globals().export_anim_file == 'anim':
        row.enabled = True
    else:
        row.enabled = False
    row.prop(_get_scs_globals(), 'export_pia_file', text="Export Animations (PIA)", toggle=True)
    if not _get_scs_globals().export_output_type.startswith('EF'):
        box3 = layout.box()
        row = box3.row()
        row.prop(_get_scs_globals(), 'export_write_signature')
    '''


def draw_common_settings(layout, log_level_only=False, without_box=False):
    """Draw common settings panel featuring log level and usage type of global settings if requested

    :param layout: Blender UI layout to draw operator to
    :type layout: UILayout
    :param log_level_only: draw only log level option
    :type log_level_only: bool
    :param without_box: draw without extra box layout?
    :type without_box: bool
    """

    if without_box:
        sub_layout = layout.column()
    else:
        sub_layout = layout.box().column()

    sub_layout.use_property_split = True
    sub_layout.use_property_decorate = False

    if not log_level_only:
        sub_layout.operator("scene.scs_tools_copy_log_to_clipboard", icon='COPYDOWN')

    sub_layout.prop(_get_scs_globals(), 'dump_level', text="Log Level", icon='MOD_EXPLODE')

    if not log_level_only:
        sub_layout.prop(_get_scs_globals(), 'config_storage_place')


def draw_warning_operator(layout, title, message, text="", icon='ERROR'):
    """Draws operator for showing popup window with given title and message.

    :param layout: Blender UI layout to draw operator to
    :type layout: UILayout
    :param title: title used in popup window
    :type title: str
    :param message: message used in popup window
    :type message: str
    :param text: text of warning operator button (optional)
    :type text: str
    :param icon: blender icon string (optional)
    :type icon: str
    """
    props = layout.operator('wm.scs_tools_show_message_in_popup', text=text, icon=icon)
    props.is_modal = False
    props.icon = icon
    props.title = title
    props.message = message


def create_row(layout, align=False, use_split=False, use_decorate=False, enabled=False):
    """Creates a row layout with givent options of the layout.

    :param layout:
    :type layout:
    :param align:
    :type align:
    :param use_split:
    :type use_split:
    :param use_decorate:
    :type use_decorate:
    :param enabled:
    :type enabled:
    :return:
    :rtype:
    """
    row = layout.row(align=align)
    row.use_property_split = use_split
    row.use_property_decorate = use_decorate
    row.enabled = enabled
    return row


def get_on_off_icon(is_state_on):
    """Returns icon string for on/off state. Should be used everywhere where we indicate on/off state in buttons.

    :param is_state_on: if True then ON icon is returned, OFF icon returned otherwise
    :type is_state_on: bool
    :return: icon string
    :rtype: str
    """
    return 'CHECKBOX_HLT' if is_state_on else 'CHECKBOX_DEHLT'


classes = (
    SCS_TOOLS_UL_ObjectLookSlots,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
