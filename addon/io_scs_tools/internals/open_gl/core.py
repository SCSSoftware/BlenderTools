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
from bgl import (glColor3f, glPointSize, glLineWidth, glEnable, glDisable, glClear,
                 GL_DEPTH_TEST, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT)
from mathutils import Vector
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.open_gl import locators as _locators
from io_scs_tools.internals.open_gl import primitive as _primitive
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import object as _object_utils


def disable_depth_test():
    glDisable(GL_DEPTH_TEST)


def draw_custom_3d_elements(mode):
    """Get's updated custom 3D elements and draws them

    :param mode: drawing mode for custom elements (can be: 'Normal' or 'X-ray')
    :type mode: str
    """
    if mode == "Normal":
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    else:  # X-ray mode
        disable_depth_test()

    context = bpy.context

    (prefab_locators, collision_locators, model_locators) = _get_custom_visual_elements()

    # PREFAB LOCATORS
    if context.scene.scs_props.display_locators:
        if prefab_locators:
            for obj in prefab_locators.values():
                _locators.prefab.draw_prefab_locator(obj, context.scene.scs_props)

    # reset point size to 1.0 and set line width to 2.0 before drawing curves and lines
    glPointSize(1.0)
    glLineWidth(2.0)

    # CURVES AND LINES
    if context.scene.scs_props.display_connections:
        _connections_group_wrapper.draw(prefab_locators)

    # reset line width to 1.0 after drawing curves and lines
    glLineWidth(1.0)

    # COLLISION LOCATORS
    if context.scene.scs_props.display_locators:
        if collision_locators:
            for obj in collision_locators.values():
                _locators.collider.draw_collision_locator(obj, context.scene.scs_props)

    # MODEL LOCATORS
    if context.scene.scs_props.display_locators:
        if model_locators:
            for obj in model_locators.values():
                _locators.model.draw_model_locator(obj, context.scene.scs_props)


def draw_custom_2d_elements():
    context = bpy.context

    font_id = 0  # TODO: Need to find out how best to get this.
    blf.size(font_id, 12, 72)

    (prefab_locators, collision_locators, model_locators) = _get_custom_visual_elements()

    if not prefab_locators and \
            not collision_locators and \
            not model_locators:
        return

    glColor3f(
        context.scene.scs_props.info_text_color[0],
        context.scene.scs_props.info_text_color[1],
        context.scene.scs_props.info_text_color[2],
    )

    region = context.region
    region3d = context.space_data.region_3d

    region_mid_width = region.width / 2.0
    region_mid_height = region.height / 2.0

    # VARS FOR PROJECTION
    perspective_matrix = region3d.perspective_matrix.copy()

    region_data = (perspective_matrix, region_mid_width, region_mid_height)

    # LOCATOR NAMES
    if context.scene.scs_props.display_info == 'locnames':
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
    elif context.scene.scs_props.display_info == 'locinfo':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                mat = obj.matrix_world
                textlines = ['"' + key + '"',
                             str(obj.scs_props.locator_type + " - " + obj.scs_props.locator_prefab_type)]

                if obj.scs_props.locator_prefab_type == 'Control Node':
                    textlines.append(str("Node Index: " + str(obj.scs_props.locator_prefab_con_node_index)))
                    if 1:  # TODO
                        textlines.append(str("Assigned Points: " + str(0)))
                elif obj.scs_props.locator_prefab_type == 'Spawn Point':
                    textlines.append(str("Type: " + str(obj.scs_props.locator_prefab_spawn_type)))
                elif obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
                    textlines.append(str("ID: " + str(obj.scs_props.locator_prefab_tsem_id)))
                    # if obj.scs_props.locator_prefab_tsem_model != '':
                    # textlines.append(str("Model: " + str(obj.scs_props.locator_prefab_tsem_model)))
                    if obj.scs_props.locator_prefab_tsem_profile != '':
                        textlines.append(str("Profile: " + str(obj.scs_props.locator_prefab_tsem_profile)))
                    if obj.scs_props.locator_prefab_tsem_type != '0':
                        textlines.append(str("Type: " + str(obj.scs_props.locator_prefab_tsem_type)))
                    textlines.append(str(
                        "G: " + str(obj.scs_props.locator_prefab_tsem_gm) + " - O: " + str(obj.scs_props.locator_prefab_tsem_om1) + " - R: " + str(
                            obj.scs_props.locator_prefab_tsem_rm)))
                    if obj.scs_props.locator_prefab_tsem_cyc_delay != 0:
                        textlines.append(str("Cycle Delay: " + str(obj.scs_props.locator_prefab_tsem_cyc_delay)))
                    textlines.append(str("Activation: " + str(obj.scs_props.locator_prefab_tsem_activation)))
                    if obj.scs_props.locator_prefab_tsem_ai_only:
                        textlines.append("AI Only")
                elif obj.scs_props.locator_prefab_type == 'Navigation Point':
                    # if obj.scs_props.locator_prefab_np_speed_limit != 0:
                    # textlines.append(str(str(obj.scs_props.locator_prefab_np_speed_limit) + " km/h"))
                    if obj.scs_props.locator_prefab_np_boundary != 'no':
                        textlines.append(str("Lane " + str(obj.scs_props.locator_prefab_np_boundary)))
                    textlines.append(str("B. Node: " + str(obj.scs_props.locator_prefab_np_boundary_node)))
                    if obj.scs_props.locator_prefab_np_traffic_light != '-1':
                        textlines.append(str("T. Light ID: " + str(obj.scs_props.locator_prefab_np_traffic_light)))
                elif obj.scs_props.locator_prefab_type == 'Map Point':
                    if obj.scs_props.locator_prefab_mp_road_over:
                        textlines.append("Road Over")
                    if obj.scs_props.locator_prefab_mp_no_outline:
                        textlines.append("No Outline")
                    if obj.scs_props.locator_prefab_mp_no_arrow:
                        textlines.append("No Arrow")
                    if obj.scs_props.locator_prefab_mp_prefab_exit:
                        textlines.append("Prefab Exit")
                    textlines.append(str("Road Size: " + str(obj.scs_props.locator_prefab_mp_road_size)))
                    if obj.scs_props.locator_prefab_mp_road_offset != '0m':
                        textlines.append(str("Offset: " + str(obj.scs_props.locator_prefab_mp_road_offset)))
                    if obj.scs_props.locator_prefab_mp_custom_color != 'none':
                        textlines.append(str("Color: " + str(obj.scs_props.locator_prefab_mp_custom_color)))
                    if obj.scs_props.locator_prefab_mp_assigned_node != 'none':
                        textlines.append(str("Node: " + str(obj.scs_props.locator_prefab_mp_assigned_node)))
                    des_nodes = "Destination Nodes:"
                    if obj.scs_props.locator_prefab_mp_des_nodes_0:
                        des_nodes += " 0"
                    if obj.scs_props.locator_prefab_mp_des_nodes_1:
                        des_nodes += " 1"
                    if obj.scs_props.locator_prefab_mp_des_nodes_2:
                        des_nodes += " 2"
                    if obj.scs_props.locator_prefab_mp_des_nodes_3:
                        des_nodes += " 3"
                    if des_nodes != "Destination Nodes:":
                        textlines.append(des_nodes)
                    if obj.scs_props.locator_prefab_mp_des_nodes_ct:
                        textlines.append("Custom Target")
                elif obj.scs_props.locator_prefab_type == 'Trigger Point':
                    if obj.scs_props.locator_prefab_tp_action != '':
                        textlines.append(str("Action: " + str(obj.scs_props.locator_prefab_tp_action)))
                    textlines.append(str("Range: " + str(obj.scs_props.locator_prefab_tp_range)))
                    if obj.scs_props.locator_prefab_tp_reset_delay != 0:
                        textlines.append(str("Reset Delay: " + str(obj.scs_props.locator_prefab_tp_reset_delay)))
                    if obj.scs_props.locator_prefab_tp_sphere_trigger:
                        textlines.append("Sphere Trigger")
                    if obj.scs_props.locator_prefab_tp_partial_activ:
                        textlines.append("Partial Activation")
                    if obj.scs_props.locator_prefab_tp_onetime_activ:
                        textlines.append("One-Time Activation")
                    if obj.scs_props.locator_prefab_tp_manual_activ:
                        textlines.append("Manual Activation")

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

    # LOCATOR SPEED LIMITS
    elif context.scene.scs_props.display_info == 'locspeed':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                if obj.scs_props.locator_prefab_type == 'Navigation Point':
                    if obj.scs_props.locator_prefab_np_speed_limit != 0:
                        mat = obj.matrix_world
                        _primitive.draw_text(str(str(obj.scs_props.locator_prefab_np_speed_limit) + " km/h"), font_id,
                                             Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

    # LOCATOR BOUNDARY NODES
    elif context.scene.scs_props.display_info == 'locnodes':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                if obj.scs_props.locator_prefab_type == 'Navigation Point':
                    mat = obj.matrix_world
                    _primitive.draw_text(str(obj.scs_props.locator_prefab_np_boundary_node), font_id,
                                         Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)

    # LOCATOR BOUNDARY LANES
    elif context.scene.scs_props.display_info == 'loclanes':
        if prefab_locators:
            for key, obj in prefab_locators.items():
                if obj.scs_props.locator_prefab_type == 'Navigation Point':
                    if obj.scs_props.locator_prefab_np_boundary != 'no':
                        mat = obj.matrix_world
                        _primitive.draw_text(str(obj.scs_props.locator_prefab_np_boundary), font_id,
                                             Vector((mat[0][3], mat[1][3], mat[2][3])), region_data)


def _get_custom_visual_elements():
    """Returns dictionaries of elements, that require custom OpenGL drawing in 3D viewports."""
    prefab_locators = {}
    collision_locators = {}
    model_locators = {}

    scene = bpy.context.scene

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
        new_draw_size = scene.scs_props.locator_empty_size * scene.scs_props.locator_size
        _object_utils.set_attr_if_different(obj, "empty_draw_size", new_draw_size)
        _object_utils.set_attr_if_different(obj, "empty_draw_type", 'PLAIN_AXES')

    def set_locators_model_draw_size(obj):
        """Set Model Locator drawing style for Empty object.

        :param obj: Blender Object
        :type obj: bpy.types.Object
        """
        # new_draw_size = (scene.scs_props.locator_empty_size * (scene.scs_props.locator_size * 10)) / 6
        new_draw_size = scene.scs_props.locator_empty_size * scene.scs_props.locator_size
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
            if bpy.context.scene.scs_props.show_preview_models:
                if visib_obj.scs_props.locator_preview_model_path != "":
                    if visib_obj.scs_props.locator_preview_model_present is False:
                        _preview_models.load(visib_obj)
                    else:
                        # identify preview model and alter it's layers array to object layers array
                        _preview_models.fix_visibility(visib_obj)

        else:

            # fix all preview models which parents are not visible anymore
            if visib_obj.data and "scs_props" in visib_obj.data and visib_obj.data.scs_props.locator_preview_model_path != "":

                if visib_obj.parent and not visib_obj.parent in bpy.context.visible_objects:
                    _preview_models.fix_visibility(visib_obj.parent)

    return prefab_locators, collision_locators, model_locators
