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

from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.icons.wrapper import get_icon

_ICON_TYPES = _ICONS_consts.Types


class HeaderIconPanel:
    """
    Holds the function for drawing icon in header section of Panel
    """

    def draw_header(self, context):
        self.layout.label('', icon_value=get_icon(_ICON_TYPES.scs_logo))


def draw_scs_looks_panel(layout, scene, active_object, scs_root_object):
    """Creates 'SCS Looks' settings sub-panel.

    :param layout: Blender UI Layout to draw to
    :type layout: bpy.types.UILayout
    :param scene: Blender Scene
    :type scene: bpy.types.Scene
    :param active_object: active object
    :type active_object: bpy.types.Object
    :param scs_root_object: SCS Root Object
    :type scs_root_object: bpy.types.Object
    """

    layout_column = layout.column(align=True)
    layout_box = layout_column.box()

    if scene.scs_props.scs_look_panel_expand:

        # HEADER (COLLAPSIBLE - OPENED)
        row = layout_box.row()
        row.prop(scene.scs_props, 'scs_look_panel_expand', text="SCS Looks:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        row.prop(scene.scs_props, 'scs_look_panel_expand', text=" ", icon='NONE', icon_only=True, emboss=False)

        layout_box = layout_column.box()  # body box

        if len(_object_utils.gather_scs_roots(bpy.context.selected_objects)) > 1 and active_object is not scs_root_object:

            col = layout_box.box().column(align=True)
            row = col.row()
            row.label("WARNING", icon="ERROR")
            row = col.row()
            row.label("Can not edit looks! Selection has multiple game objects.")

        else:  # more roots or active object is root object

            row = layout_box.row()
            row.template_list(
                'SCSObjectLookSlots',
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
            col.operator('object.add_scs_look', text="", icon='ZOOMIN')
            col.operator('object.remove_scs_look', text="", icon='ZOOMOUT')

    else:
        row = layout_box.row()
        row.prop(scene.scs_props, 'scs_look_panel_expand', text="SCS Looks:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        row.prop(scene.scs_props, 'scs_look_panel_expand', text=" ", icon='NONE', icon_only=True, emboss=False)


def draw_export_panel(layout):
    box1 = layout.box()
    row = box1.row()
    row.prop(_get_scs_globals(), 'export_scale')
    col = box1.column()
    row = col.row()
    row.prop(_get_scs_globals(), 'apply_modifiers')
    row_2 = row.row()
    if _get_scs_globals().output_type.startswith('def'):
        if int(_get_scs_globals().apply_modifiers):
            row_2.enabled = True
        else:
            row_2.enabled = False
        row_2.prop(_get_scs_globals(), 'exclude_edgesplit')
    else:
        if not int(_get_scs_globals().apply_modifiers):
            row_2.enabled = True
        else:
            row_2.enabled = False
        row_2.prop(_get_scs_globals(), 'include_edgesplit')
    '''
    col.prop(_get_scs_globals(), 'active_uv_only')
    if not _get_scs_globals().output_type.startswith('def'):
        col.prop(_get_scs_globals(), 'export_vertex_groups')
    col.prop(_get_scs_globals(), 'export_vertex_color')
    if _get_scs_globals().export_vertex_color:
        row = box1.row()
        if not _get_scs_globals().output_type.startswith('def'):
            row.prop(_get_scs_globals(), 'export_vertex_color_type_7')
        else:
            row.prop(_get_scs_globals(), 'export_vertex_color_type')
    '''
    # row = box1.row()
    # row.prop(_get_scs_globals(), 'export_anim_file', expand=True)
    box2 = layout.box()
    box2.prop(_get_scs_globals(), 'output_type')
    '''
    col = box2.column()
    col.prop(_get_scs_globals(), 'export_pim_file', text="Export Model (PIM)", toggle=True)
    if _get_scs_globals().export_pim_file:
        col.prop(_get_scs_globals(), 'output_type')
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
    if not _get_scs_globals().output_type.startswith('def'):
        box3 = layout.box()
        row = box3.row()
        row.prop(_get_scs_globals(), 'sign_export')
    '''


def draw_debug_settings(layout):
    box4 = layout.box()
    row = box4.row()
    row.label("Printout Settings:", icon='MOD_EXPLODE')
    row = box4.row()
    row.prop(_get_scs_globals(), 'dump_level', text="Dump Level")


def draw_warning_operator(layout, title, message):
    """Draws operator for showing popup window with given title and message.

    :param layout: Blender UI layout to draw operator to
    :type layout: UILayout
    :param title: title used in popup window
    :type title: str
    :param message: message used in popup window
    :type message: str
    """
    props = layout.operator('wm.show_warning_message', text="", icon="ERROR")
    props.title = title
    props.message = message
    props.is_modal = False