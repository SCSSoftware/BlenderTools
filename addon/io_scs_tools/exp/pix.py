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
import os
from collections import OrderedDict
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.printout import handle_unused_arg
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.exp import pia as _pia
from io_scs_tools.exp import pic as _pic
from io_scs_tools.exp import pip as _pip
from io_scs_tools.exp import pis as _pis
from io_scs_tools.exp import pit as _pit
from io_scs_tools.exp.pim import exporter as _pim_exporter


def _get_objects_by_type(blender_objects):
    """Gets lists for different types of objects used by SCS.
    It actually returns: mesh objects, locators (prefab, model, collision) and armature object.

    :param blender_objects: list of the objects that should be sorted by type
    :type blender_objects: list of bpy.types.Object
    :return: more lists of objects in order: meshes, prefab_locators, model_locators, collision_locators and armutare object as last
    :rtype: list of [list]
    """

    prefab_locator_list = []
    model_locator_list = []
    collision_locator_list = []
    mesh_object_list = []
    armature_object = None

    for obj in blender_objects:

        # LOCATORS
        if obj.type == 'EMPTY':
            if obj.scs_props.locator_type == 'Prefab':
                prefab_locator_list.append(obj)
            elif obj.scs_props.locator_type == 'Model':
                model_locator_list.append(obj)
            elif obj.scs_props.locator_type == 'Collision':
                collision_locator_list.append(obj)

        # ARMATURES
        elif obj.type == 'ARMATURE':
            if not armature_object:
                armature_object = obj
            else:
                lprint("W More armatures detected on SCS Root object, only first one will be used!")

        # MESHES
        elif obj.type == 'MESH':

            # MESH OBJECTS
            if obj.data.scs_props.locator_preview_model_path == "":  # Export object only if it's not a Preview Model...
                mesh_object_list.append(obj)

        else:
            print('!!! - Unhandled object type: %r' % str(obj.type))

    return mesh_object_list, prefab_locator_list, model_locator_list, collision_locator_list, armature_object


def _get_initial_selection(content_type):
    """
    Takes content type and returns initial object list.
    :param content_type:
    :return:
    """
    if content_type == 'selection':
        init_obj_list = bpy.context.selected_objects
    elif content_type == 'scene':
        init_obj_list = bpy.context.scene.objects
    elif content_type == 'scenes':
        init_obj_list = bpy.data.objects
    else:
        init_obj_list = bpy.context.selected_objects
        lprint('W Unkown "Selection type" - %r. Using "Selection Only".', content_type)
    return init_obj_list


def export_from_menu(context, filepath):
    handle_unused_arg(__file__, export_from_menu.__name__, "context", context)
    handle_unused_arg(__file__, export_from_menu.__name__, "filepath", filepath)

    scs_globals = _get_scs_globals()

    # MAKE INITIAL SELECTION
    init_obj_list = _get_initial_selection(scs_globals.content_type)
    lprint("D initial number of objects: %i" % len(init_obj_list))

    # SORT OUT OBJECTS
    # game_objects_dict = _object_utils.sort_out_game_objects_for_export(init_obj_list)
    # export(context, filepath, filepath, init_obj_list)

    # ## EXPORT OBJECTS
    # ## TODO: Export from menu TURNED OF TEMPORARILY!
    # for root_object in game_objects_dict:
    # game_object_list = game_objects_dict[root_object]
    # status = export(context, filepath, filepath, root_object, game_object_list)


def export(dirpath, root_object, game_object_list):
    """The main export function.

    :param dirpath: The main Filepath where most of the Files will be exported
    :type dirpath: str
    :param root_object: This is the "SCS Root Object" and parent object of all objects in "game_object_list" and carries many settings for the
    whole "SCS Game Object"
    :type root_object: bpy.types.Object
    :param game_object_list: This is a simple list of all objects belonging to the "SCS Game Object", which can be further reduced of invalid objects
    :type game_object_list: list
    :return: Return state statuses (Usually 'FINISHED')
    :rtype: dict
    """
    import time

    t = time.time()
    context = bpy.context
    context.window.cursor_modal_set('WAIT')

    # GROUP OBJECTS BY TYPE
    (
        mesh_objects,
        prefab_locators,
        model_locators,
        collision_locators,
        armature_object
    ) = _get_objects_by_type(game_object_list)

    # EXPORT
    scs_globals = _get_scs_globals()
    export_success = True
    used_parts = OrderedDict()  # dictionary of parts which are actually used in this game object
    used_materials = []

    # EXPORT PIM
    if scs_globals.export_pim_file:
        export_success = _pim_exporter.execute(dirpath, root_object, mesh_objects, model_locators, used_parts, used_materials)

        # EXPORT PIC
        if scs_globals.export_pic_file and export_success:
            if collision_locators:
                export_success = _pic.export(collision_locators, dirpath + os.sep + root_object.name, root_object.name, used_parts)
            else:
                lprint("I No collider locator objects to export.")

    # EXPORT PIT
    if scs_globals.export_pit_file and used_materials and export_success:
        export_success = _pit.export(root_object, used_parts, used_materials, context.scene, dirpath + os.sep + root_object.name)

    # EXPORT PIP
    if scs_globals.export_pip_file and prefab_locators and export_success:
        export_success = _pip.export(prefab_locators, dirpath + os.sep + root_object.name, root_object.name, root_object.matrix_world)

    """
    # PIS, PIA
    if root_object.scs_props.scs_root_animated == 'anim':
        # EXPORT PIS
        if scs_globals.export_pis_file and bone_list and export_success:
            export_success = _pis.export(bone_list, dirpath, root_object.name)

        # EXPORT PIA
        if scs_globals.export_pia_file and bone_list and export_success:
            if armature.animation_data:
                export_success = _pia.export(armature, bone_list, dirpath, root_object.name)
            else:
                lprint('E No animation data! Skipping PIA export...\n')
    """

    # FINAL FEEDBACK
    context.window.cursor_modal_restore()
    if export_success:
        lprint('\nI Export compleeted in %.3f sec. Files were saved to folder:\n\t   %r\n', (time.time() - t, dirpath),
               report_errors=True,
               report_warnings=True)
    else:
        lprint("E Nothing to export! Please set a 'SCS Root Object'...", report_errors=True)

    return {'FINISHED'}