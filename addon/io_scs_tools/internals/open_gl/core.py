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
import blf
from bgl import (glColor3f, glPointSize, glLineWidth, glEnable, glDisable, glClear, glBegin, glEnd, glVertex3f, glBindTexture, glTexCoord2f,
                 GL_DEPTH_TEST, GL_DEPTH_BUFFER_BIT, GL_POLYGON, GL_TEXTURE_2D, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
from mathutils import Vector
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.open_gl import locators as _locators
from io_scs_tools.internals.open_gl import primitive as _primitive
from io_scs_tools.internals.open_gl.storage import terrain_points as _terrain_points_storage
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.operators.wm import Show3DViewReport as _Show3DViewReportOperator
from io_scs_tools.utils import info as _info_utils
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def disable_depth_test():
    glDisable(GL_DEPTH_TEST)


def draw_custom_3d_elements(mode):
    """Get's updated custom 3D elements and draws them

    :param mode: drawing mode for custom elements (can be: 'Normal' or 'X-ray')
    :type mode: str
    """
    if mode == "Normal":
        glEnable(GL_DEPTH_TEST)
        glClear(GL_DEPTH_BUFFER_BIT)
    else:  # X-ray mode
        disable_depth_test()

    scs_globals = _get_scs_globals()

    # TERRAIN POINTS
    glPointSize(5.0)

    for tp_position, tp_color in _terrain_points_storage.get_positions_and_colors():
        _primitive.draw_point(tp_position, tp_color)

    glPointSize(1.0)

    (prefab_locators, collision_locators, model_locators) = _get_custom_visual_elements()

    # reset point size to 1.0 and set line width to 2.0 before drawing curves and lines
    glPointSize(1.0)
    glLineWidth(2.0)

    # CURVES AND LINES
    if scs_globals.display_connections:
        _connections_group_wrapper.draw(prefab_locators)

    # reset line width to 1.0 after drawing curves and lines
    glLineWidth(1.0)

    # LOCATORS
    if scs_globals.display_locators:

        # PREFAB LOCATORS
        if prefab_locators:
            for obj in prefab_locators.values():
                _locators.prefab.draw_prefab_locator(obj, scs_globals)

        # COLLISION LOCATORS
        if collision_locators:
            for obj in collision_locators.values():
                _locators.collider.draw_collision_locator(obj, scs_globals)

        # MODEL LOCATORS
        if model_locators:
            for obj in model_locators.values():
                _locators.model.draw_model_locator(obj, scs_globals)


def draw_custom_2d_elements():
    context = bpy.context
    scs_globals = _get_scs_globals()

    font_id = 0  # TODO: Need to find out how best to get this.
    blf.size(font_id, 12, 72)

    region = context.region

    # draw 3d view import/export reports
    _draw_3dview_report(region)

    (prefab_locators, collision_locators, model_locators) = _get_custom_visual_elements()

    if not prefab_locators and not collision_locators and not model_locators:
        return

    glColor3f(
        scs_globals.info_text_color[0],
        scs_globals.info_text_color[1],
        scs_globals.info_text_color[2],
    )

    region3d = context.space_data.region_3d

    region_mid_width = region.width / 2.0
    region_mid_height = region.height / 2.0

    # VARS FOR PROJECTION
    perspective_matrix = region3d.perspective_matrix.copy()

    region_data = (perspective_matrix, region_mid_width, region_mid_height)

    # LOCATOR NAMES
    if scs_globals.display_info == 'locnames':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                mat = obj.matrix_world
                _primitive.draw_text(key, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

        if collision_locators:
            for key, obj in collision_locators.items():
                mat = obj.matrix_world
                _primitive.draw_text(key, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

        if model_locators:
            for key, obj in model_locators.items():
                mat = obj.matrix_world
                _primitive.draw_text(key, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

    # LOCATOR COMPREHENSIVE INFO
    elif scs_globals.display_info == 'locinfo':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                mat = obj.matrix_world
                textlines = ['"' + key + '"',
                             str(obj.scs_props.locator_type + " - " + obj.scs_props.locator_prefab_type)]

                if obj.scs_props.locator_prefab_type == 'Control Node':

                    textlines.append(str("Node Index: " + str(obj.scs_props.locator_prefab_con_node_index)))

                elif obj.scs_props.locator_prefab_type == 'Spawn Point':

                    spawn_type_i = int(obj.scs_props.locator_prefab_spawn_type)
                    textlines.append(str("Type: " + obj.scs_props.enum_spawn_type_items[spawn_type_i][1]))

                elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':

                    textlines.append(str("ID: " + str(obj.scs_props.locator_prefab_tsem_id)))
                    if obj.scs_props.locator_prefab_tsem_profile != '':
                        textlines.append(str("Profile: " + str(obj.scs_props.locator_prefab_tsem_profile)))
                    tsem_type_i = int(obj.scs_props.locator_prefab_tsem_type)
                    if tsem_type_i != _PL_consts.TST.PROFILE:
                        textlines.append(str("Type: " + obj.scs_props.enum_tsem_type_items[tsem_type_i][1]))
                        textlines.append(str("G: %.2f" % obj.scs_props.locator_prefab_tsem_gs +
                                             " - O: %.2f" % obj.scs_props.locator_prefab_tsem_os1 +
                                             " - R: %.2f" % obj.scs_props.locator_prefab_tsem_rs +
                                             " - O: %.2f" % obj.scs_props.locator_prefab_tsem_os2))
                        if obj.scs_props.locator_prefab_tsem_cyc_delay != 0:
                            textlines.append(str("Cycle Delay: " + "%.2f s" % obj.scs_props.locator_prefab_tsem_cyc_delay))

                elif obj.scs_props.locator_prefab_type == 'Navigation Point':

                    np_boundary_i = int(obj.scs_props.locator_prefab_np_boundary)
                    if np_boundary_i != 0:
                        textlines.append(str("Boundary: " + obj.scs_props.enum_np_boundary_items[np_boundary_i][1]))

                    textlines.append(str("B. Node: " + str(obj.scs_props.locator_prefab_np_boundary_node)))
                    if obj.scs_props.locator_prefab_np_traffic_semaphore != '-1':
                        textlines.append(str("T. Light ID: " + str(obj.scs_props.locator_prefab_np_traffic_semaphore)))

                elif obj.scs_props.locator_prefab_type == 'Map Point':

                    if obj.scs_props.locator_prefab_mp_road_over:
                        textlines.append("Road Over: YES")
                    if obj.scs_props.locator_prefab_mp_no_outline:
                        textlines.append("No Outline: YES")
                    if obj.scs_props.locator_prefab_mp_no_arrow:
                        textlines.append("No Arrow: YES")
                    if obj.scs_props.locator_prefab_mp_prefab_exit:
                        textlines.append("Prefab Exit: YES")

                    road_size_i = int(obj.scs_props.locator_prefab_mp_road_size)
                    textlines.append(str("Road Size: " + obj.scs_props.enum_mp_road_size_items[road_size_i][1]))

                    road_offset_i = int(obj.scs_props.locator_prefab_mp_road_offset)
                    if road_offset_i != _PL_consts.MPVF.ROAD_OFFSET_0:
                        textlines.append(str("Offset: " + obj.scs_props.enum_mp_road_offset_items[road_offset_i][1]))

                    custom_color_i = int(obj.scs_props.locator_prefab_mp_custom_color)
                    if custom_color_i != 0:
                        textlines.append(str("Custom Color: " + obj.scs_props.enum_mp_custom_color_items[custom_color_i][1]))

                    assigned_node_i = int(obj.scs_props.locator_prefab_mp_assigned_node)
                    if assigned_node_i != 0:
                        textlines.append(str("Node: " + obj.scs_props.enum_mp_assigned_node_items[assigned_node_i][1]))

                    des_nodes = "Destination Nodes:"
                    for index in obj.scs_props.locator_prefab_mp_dest_nodes:
                        des_nodes += " " + index
                    if des_nodes != "Destination Nodes:":
                        textlines.append(des_nodes)

                elif obj.scs_props.locator_prefab_type == 'Trigger Point':

                    textlines.append(str("Range: %.2f m" % obj.scs_props.locator_prefab_tp_range))
                    if obj.scs_props.locator_prefab_tp_reset_delay != 0:
                        textlines.append(str("Reset Delay: %.2f s" % obj.scs_props.locator_prefab_tp_reset_delay))
                    if obj.scs_props.locator_prefab_tp_sphere_trigger:
                        textlines.append("Sphere Trigger: YES")
                    if obj.scs_props.locator_prefab_tp_partial_activ:
                        textlines.append("Partial Activation: YES")
                    if obj.scs_props.locator_prefab_tp_onetime_activ:
                        textlines.append("One-Time Activation: YES")
                    if obj.scs_props.locator_prefab_tp_manual_activ:
                        textlines.append("Manual Activation: YES")

                for textline_i, textline in enumerate(textlines):
                    y_pos = ((len(textlines) * 15) / 2) + (textline_i * -15) - 7
                    _primitive.draw_text(textline, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data, 0, y_pos)

        if collision_locators:
            for key, obj in collision_locators.items():
                mat = obj.matrix_world
                textlines = ['"' + key + '"',
                             str(obj.scs_props.locator_type + " - " + obj.scs_props.locator_collider_type),
                             str("Mass: " + str(obj.scs_props.locator_collider_mass))]

                # if obj.scs_props.locator_collider_centered:
                # textlines.append("Locator Centered")
                if obj.scs_props.locator_collider_margin != 0:
                    textlines.append(str("Margin: " + str(obj.scs_props.locator_collider_margin)))

                for textline_i, textline in enumerate(textlines):
                    y_pos = ((len(textlines) * 15) / 2) + (textline_i * -15) - 7
                    _primitive.draw_text(textline, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data, 0, y_pos)

        if model_locators:
            for key, obj in model_locators.items():
                mat = obj.matrix_world
                textlines = ['"' + key + '"',
                             str(obj.scs_props.locator_type),
                             str(obj.scs_props.locator_model_hookup)]

                if obj.scs_props.locator_show_preview_model:
                    textlines.append(str(obj.scs_props.locator_preview_model_path))

                for textline_i, textline in enumerate(textlines):
                    y_pos = ((len(textlines) * 15) / 2) + (textline_i * -15) - 7
                    _primitive.draw_text(textline, font_id, Vector((mat[0][3], mat[1][3], mat[2][3])), region_data, 0, y_pos)

    # LOCATOR BOUNDARY NODES
    elif scs_globals.display_info == 'locnodes':
        for key, obj in prefab_locators.items():
            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                mat = obj.matrix_world
                _primitive.draw_text(str(obj.scs_props.locator_prefab_np_boundary_node), font_id,
                                     Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

    # LOCATOR BOUNDARY LANES
    elif scs_globals.display_info == 'loclanes':
        for key, obj in prefab_locators.items():
            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                if obj.scs_props.locator_prefab_np_boundary != 'no':
                    mat = obj.matrix_world
                    np_boundary_i = int(obj.scs_props.locator_prefab_np_boundary)
                    if np_boundary_i == 0:
                        continue

                    _primitive.draw_text(str(obj.scs_props.enum_np_boundary_items[np_boundary_i][1]), font_id,
                                         Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)


def _get_custom_visual_elements():
    """Returns dictionaries of elements, that require custom OpenGL drawing in 3D viewports."""
    prefab_locators = {}
    collision_locators = {}
    model_locators = {}

    scs_globals = _get_scs_globals()

    # print(' time: %s' % str(time()))

    def set_locators_original_draw_size(obj):
        """Set original drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        # _object.set_attr_if_different(obj, "empty_draw_size", obj.scs_props.locators_orig_draw_size)
        if obj.empty_draw_size != obj.scs_props.locators_orig_draw_size:
            obj.empty_draw_size = obj.scs_props.locators_orig_draw_size
            obj.scs_props.locators_orig_draw_size = 0.0
        if obj.empty_draw_type != obj.scs_props.locators_orig_draw_type:
            obj.empty_draw_type = obj.scs_props.locators_orig_draw_type
            obj.scs_props.locators_orig_draw_type = ''

    def store_locators_original_draw_size(obj):
        """Set Prefab Locator drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        if obj.scs_props.locators_orig_draw_size == 0.0:
            _object_utils.set_attr_if_different(obj.scs_props, "locators_orig_draw_size", obj.empty_draw_size)
            _object_utils.set_attr_if_different(obj.scs_props, "locators_orig_draw_type", obj.empty_draw_type)

    def set_locators_prefab_draw_size(obj):
        """Set Prefab Locator drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        new_draw_size = scs_globals.locator_empty_size * scs_globals.locator_size
        _object_utils.set_attr_if_different(obj, "empty_draw_size", new_draw_size)
        _object_utils.set_attr_if_different(obj, "empty_draw_type", 'PLAIN_AXES')

    def set_locators_model_draw_size(obj):
        """Set Model Locator drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        new_draw_size = scs_globals.locator_empty_size * scs_globals.locator_size
        _object_utils.set_attr_if_different(obj, "empty_draw_size", new_draw_size)
        _object_utils.set_attr_if_different(obj, "empty_draw_type", 'PLAIN_AXES')

    def set_locators_coll_draw_size(obj):
        """Set Collision Locator drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        new_draw_size = 0.5
        if obj.scs_props.locator_collider_type == 'Box':
            bigest_value = max(obj.scs_props.locator_collider_box_x, obj.scs_props.locator_collider_box_y, obj.scs_props.locator_collider_box_z)
            new_draw_size = (0.1 * bigest_value) * 12
        elif obj.scs_props.locator_collider_type in ('Sphere', 'Capsule', 'Cylinder'):
            new_draw_size = (0.1 * obj.scs_props.locator_collider_dia) * 12
        elif obj.scs_props.locator_collider_type == 'Convex':
            bbox = obj.scs_props.get("coll_convex_bbox", None)
            bbcenter = obj.scs_props.get("coll_convex_bbcenter", None)
            if bbox and bbcenter:
                scaling = _math_utils.scaling_width_margin(bbox, obj.scs_props.locator_collider_margin)
                val = []
                for axis in range(3):
                    val.append((bbox[axis] + abs(bbcenter[axis])) * scaling[axis])
                bigest_value = max(val)
                new_draw_size = (0.1 * bigest_value) * 12
        _object_utils.set_attr_if_different(obj, "empty_draw_size", new_draw_size)
        _object_utils.set_attr_if_different(obj, "empty_draw_type", 'PLAIN_AXES')

    for visib_obj in bpy.context.visible_objects:
        # print('object: "%s"' % obj.name)
        if visib_obj.type == 'EMPTY' and visib_obj.scs_props.empty_object_type == 'Locator':

            if visib_obj.scs_props.locator_type == 'Prefab':
                prefab_locators[visib_obj.name] = visib_obj
                if visib_obj.scs_props.locators_orig_draw_size == 0.0:
                    store_locators_original_draw_size(visib_obj)
                set_locators_prefab_draw_size(visib_obj)
            elif visib_obj.scs_props.locator_type == 'Model':
                model_locators[visib_obj.name] = visib_obj
                store_locators_original_draw_size(visib_obj)
                set_locators_model_draw_size(visib_obj)
            elif visib_obj.scs_props.locator_type == 'Collision':
                collision_locators[visib_obj.name] = visib_obj
                store_locators_original_draw_size(visib_obj)
                set_locators_coll_draw_size(visib_obj)
            else:
                if visib_obj.scs_props.locators_orig_draw_size != 0.0:
                    set_locators_original_draw_size(visib_obj)

            # load any lost preview models or switch their layers if needed
            if scs_globals.show_preview_models:
                if visib_obj.scs_props.locator_preview_model_path != "":
                    if visib_obj.scs_props.locator_preview_model_present is False:
                        _preview_models.load(visib_obj)
                    else:
                        # identify preview model and alter it's layers array to object layers array
                        _preview_models.fix_visibility(visib_obj)

        else:

            # fix all preview models which parents are not visible anymore
            is_scs_mesh = visib_obj.type == "MESH" and visib_obj.data and "scs_props" in visib_obj.data
            if is_scs_mesh and visib_obj.data.scs_props.locator_preview_model_path != "":

                if visib_obj.parent and visib_obj.parent not in bpy.context.visible_objects:
                    _preview_models.fix_visibility(visib_obj.parent)

    return prefab_locators, collision_locators, model_locators


def _draw_3dview_report(region):
    """Draws reports in 3d views.

    :param region: region of 3D viewport
    :type region: bpy.types.Region
    """
    pos = region.height - 62

    if _Show3DViewReportOperator.has_lines():

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(GL_TEXTURE_2D, _Show3DViewReportOperator.get_scs_logo_img_bindcode())

        # draw BT logo
        glBegin(GL_POLYGON)
        glColor3f(1, 1, 1)
        glTexCoord2f(0, 1)
        glVertex3f(_OP_consts.View3DReport.BT_LOGO_AREA[0], region.height - _OP_consts.View3DReport.BT_LOGO_AREA[2], 0)
        glTexCoord2f(1, 1)
        glVertex3f(_OP_consts.View3DReport.BT_LOGO_AREA[1], region.height - _OP_consts.View3DReport.BT_LOGO_AREA[2], 0)
        glTexCoord2f(1, 0)
        glVertex3f(_OP_consts.View3DReport.BT_LOGO_AREA[1], region.height - _OP_consts.View3DReport.BT_LOGO_AREA[3], 0)
        glTexCoord2f(0, 0)
        glVertex3f(_OP_consts.View3DReport.BT_LOGO_AREA[0], region.height - _OP_consts.View3DReport.BT_LOGO_AREA[3], 0)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # draw version string
        blf.size(0, 10, 72)
        glColor3f(.952, .635, .062)
        blf.position(0, 20, pos, 0)
        blf.draw(0, _info_utils.get_combined_ver_str(only_version_numbers=True))
        pos -= 20

        # draw actual operator title and message if shown
        if _Show3DViewReportOperator.is_shown():

            blf.size(0, 12, 72)
            glColor3f(1, 1, 1)
            blf.shadow(0, 5, 0, 0, 0, 1)

            if _Show3DViewReportOperator.get_title() != "":
                blf.position(0, 20, pos, 0)
                blf.draw(0, _Show3DViewReportOperator.get_title())
                pos -= 15

            blf.enable(0, blf.SHADOW)
            for line in _Show3DViewReportOperator.get_lines():

                # finish printing if running out of space
                if pos - 60 < 0:
                    blf.position(0, 20, pos, 0)
                    blf.draw(0, "...")
                    break

                blf.position(0, 20, pos, 0)
                if "ERROR" in line:
                    blf.shadow(0, 5, 0.5, 0., 0, 1)
                elif "WARNING" in line:
                    blf.shadow(0, 5, 0.3, 0.15, 0, 1)

                blf.draw(0, line)
                pos -= 15

            blf.disable(0, blf.SHADOW)

        # draw control buttons if controls are enabled
        if _Show3DViewReportOperator.has_controls():

            # draw close button
            glColor3f(.4, .4, .4)
            glBegin(GL_POLYGON)
            glVertex3f(_OP_consts.View3DReport.CLOSE_BTN_AREA[0], region.height - _OP_consts.View3DReport.CLOSE_BTN_AREA[2], 0)
            glVertex3f(_OP_consts.View3DReport.CLOSE_BTN_AREA[1], region.height - _OP_consts.View3DReport.CLOSE_BTN_AREA[2], 0)
            glVertex3f(_OP_consts.View3DReport.CLOSE_BTN_AREA[1], region.height - _OP_consts.View3DReport.CLOSE_BTN_AREA[3], 0)
            glVertex3f(_OP_consts.View3DReport.CLOSE_BTN_AREA[0], region.height - _OP_consts.View3DReport.CLOSE_BTN_AREA[3], 0)
            glEnd()

            # draw hide button
            glBegin(GL_POLYGON)
            glVertex3f(_OP_consts.View3DReport.HIDE_BTN_AREA[0], region.height - _OP_consts.View3DReport.HIDE_BTN_AREA[2], 0)
            glVertex3f(_OP_consts.View3DReport.HIDE_BTN_AREA[1], region.height - _OP_consts.View3DReport.HIDE_BTN_AREA[2], 0)
            glVertex3f(_OP_consts.View3DReport.HIDE_BTN_AREA[1], region.height - _OP_consts.View3DReport.HIDE_BTN_AREA[3], 0)
            glVertex3f(_OP_consts.View3DReport.HIDE_BTN_AREA[0], region.height - _OP_consts.View3DReport.HIDE_BTN_AREA[3], 0)
            glEnd()

            # gather texts and positions
            close_btn_text_pos = _OP_consts.View3DReport.CLOSE_BTN_TEXT_POS[int(not _Show3DViewReportOperator.is_shown())]
            close_btn_text = _OP_consts.View3DReport.CLOSE_BTN_TEXT[int(not _Show3DViewReportOperator.is_shown())]

            hide_btn_text_pos = _OP_consts.View3DReport.HIDE_BTN_TEXT_POS[int(not _Show3DViewReportOperator.is_shown())]
            hide_btn_text = _OP_consts.View3DReport.HIDE_BTN_TEXT[int(not _Show3DViewReportOperator.is_shown())]

            blf.size(0, 15, 72)

            # draw close button text
            glColor3f(1, 1, 1)
            blf.position(0, close_btn_text_pos[0], region.height - close_btn_text_pos[1], 0)
            blf.draw(0, close_btn_text)

            # draw hide button text
            blf.position(0, hide_btn_text_pos[0], region.height - hide_btn_text_pos[1], 0)
            blf.draw(0, hide_btn_text)
