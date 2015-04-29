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

from time import time

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils.printout import lprint


class _Timer:
    _interval = 0.125
    _last_execute_time = 0

    updated = 0
    """Marking object update iterations during stalling."""
    data_updated = 0
    """Marking object data update iteration during stalling."""

    @staticmethod
    def can_execute():
        if time() - _Timer._last_execute_time > _Timer._interval:
            _Timer._last_execute_time = time()
            return True
        else:
            return False


@persistent
def object_data_check(scene):

    # during rendering in Blender active_object doesn't exists so ignore this case
    if not hasattr(bpy.context, "active_object"):
        return

    active_obj = bpy.context.active_object
    selected_objs = bpy.context.selected_objects

    # skip persistent check if import is in the process
    if _get_scs_globals().import_in_progress:
        return

    # CHECK FOR DATA CHANGE UPON SELECTION
    if active_obj:

        if active_obj.is_updated_data:
            _Timer.data_updated += 1

        if active_obj.is_updated:
            _Timer.updated += 1

        elif len(selected_objs) > 0:
            # search for any updated object
            for sel_obj in selected_objs[:2]:
                if sel_obj.is_updated:
                    _Timer.updated += 1
                    break
    if _Timer.updated > 0:
        _connections_group_wrapper.switch_to_update()

    # BREAK EXECUTION IF TIMER SAYS SO
    if not _Timer.can_execute():
        return

    # GET UPDATE STATES
    updated = _Timer.updated > 0
    data_updated = _Timer.data_updated > 0
    _Timer.updated = _Timer.data_updated = 0

    if not updated:
        _connections_group_wrapper.switch_to_stall()

    # NEW/COPY
    if len(scene.objects) > scene.scs_cached_num_objects:

        scene.scs_cached_num_objects = len(scene.objects)

        if len(selected_objs) > 0:

            # create real selected list
            # (in case that one of selected objects is parent then children are not in this list)
            real_sel_objs = selected_objs.copy()
            for sel_obj in selected_objs:
                for child in sel_obj.children:
                    if child.select:
                        real_sel_objs.append(child)

            if real_sel_objs[0].scs_props.object_identity != "":

                old_objects = []
                for obj in real_sel_objs:
                    old_objects.append(bpy.data.objects[obj.scs_props.object_identity])
                    obj.scs_props.object_identity = obj.name

                __objects_copy__(old_objects, real_sel_objs)

                lprint("D ---> COPY of the objects: %s", (len(real_sel_objs),))
                return
            else:

                for obj in real_sel_objs:
                    obj.scs_props.object_identity = obj.name

                lprint("D ---> NEW objects: %s", (len(real_sel_objs),))
                return

    # DELETE
    if len(scene.objects) < scene.scs_cached_num_objects:

        scene.scs_cached_num_objects = len(scene.objects)

        unparented_objects = []
        for obj in scene.objects:

            if obj.scs_props.parent_identity != "" and not obj.scs_props.parent_identity in bpy.data.objects:
                obj.scs_props.parent_identity = ""
                unparented_objects.append(obj)

            obj.scs_cached_num_children = len(obj.children)

        __objects_delete__(unparented_objects)

        lprint("D ---> DELETE of the objects!")
        return

    # if there is no active object then all of rest actions can not be executed at all
    if active_obj:

        # RENAME
        active_obj_identity = active_obj.scs_props.object_identity
        if active_obj.name != active_obj_identity and active_obj_identity != "":

            old_name = active_obj_identity
            new_name = active_obj.name

            active_obj.scs_props.object_identity = active_obj.name
            _fix_children(active_obj)

            __object_rename__(old_name, new_name)

            if old_name in bpy.data.objects:

                lprint("D ---> NAME SWITCHING")
                bpy.data.objects[old_name].scs_props.object_identity = old_name
                _fix_children(bpy.data.objects[old_name])

                # switching names causes invalid connections data so recalculate curves for these objects
                _connections_group_wrapper.force_recalculate([bpy.data.objects[old_name], bpy.data.objects[new_name]])

            lprint("D ---> RENAME of the active object!")
            return

        # RE/PARENT
        active_obj_children_count = len(active_obj.children)
        if active_obj_children_count > active_obj.scs_cached_num_children:

            active_obj.scs_cached_num_children = active_obj_children_count

            for obj in selected_objs:
                if obj != active_obj:

                    _fix_ex_parent(obj)
                    obj.scs_props.parent_identity = active_obj.name
                    obj.scs_cached_num_children = len(obj.children)

            __objects_reparent__(active_obj, selected_objs)

            lprint("D ---> RE/PARENT selected objects to active object %s", (len(selected_objs),))
            return

        if active_obj.parent and active_obj.parent.name != active_obj.scs_props.parent_identity:

            _fix_ex_parent(active_obj)
            active_obj.scs_props.parent_identity = active_obj.parent.name

            __objects_reparent__(active_obj.parent, [active_obj])

            lprint("D ---> RE/PARENT active object to some other parent")
            return

        # UNPARENT
        if not active_obj.select and not active_obj.parent and active_obj.scs_props.parent_identity != "":

            _fix_ex_parent(active_obj)
            active_obj.scs_props.parent_identity = ""

            lprint("D ---> UNPARENT active object in panel")
            return

        if ((not active_obj.parent and active_obj.scs_props.parent_identity != "") or
                (len(selected_objs) > 0 and not selected_objs[0].parent and selected_objs[0].scs_props.parent_identity != "")):

            for obj in selected_objs:

                _fix_ex_parent(obj)
                obj.scs_props.parent_identity = ""

            lprint("D ---> UNPARENT selected objects in 3D view: %s", (len(selected_objs),))
            return

        # ACTIVE SCS ROOT CHANGED
        active_scs_root = _object_utils.get_scs_root(active_obj)
        if active_scs_root and scene.scs_cached_active_scs_root != active_scs_root.name:

            __active_scs_root_change__(active_scs_root)

            scene.scs_cached_active_scs_root = active_scs_root.name
            lprint("D ---> ACTIVE SCS ROOT CHANGE: %r", (active_scs_root.name,))
            return

        # MATERIAL ASSIGNEMENT ACTION
        if data_updated or updated:

            mats_ids = {}
            new_mats = {}
            removed_mats = dict(active_obj.scs_cached_materials_ids)
            for slot in active_obj.material_slots:
                if slot.material:
                    curr_id = str(slot.material.scs_props.id)
                    mats_ids[curr_id] = 1
                    if curr_id not in active_obj.scs_cached_materials_ids:  # if not in cached -> it's newly assigned
                        new_mats[curr_id] = 1
                    elif curr_id in removed_mats:  # if in cached remove it from dictionary which stores removed materials
                        del removed_mats[curr_id]

            if len(new_mats) > 0 or len(removed_mats) > 0:
                active_obj.scs_cached_materials_ids = mats_ids

                __material_assignement__(active_obj, new_mats.keys(), removed_mats.keys())

                lprint("D ---> MATERIAL ASSIGNEMENT CHANGED")
                return


def __active_scs_root_change__(new_scs_root_obj):
    """Hookup function for changing active object.

    :param new_scs_root_obj: new active SCS Root Object
    :type new_scs_root_obj: bpy.types.Object
    """

    _looks.apply_active_look(new_scs_root_obj)


def __material_assignement__(obj, new_mat_ids, removed_mat_ids):
    """Hookup function for material reassignement on object.

    :param obj: object on which material assignement happend
    :type obj: bpy.types.Object
    :param new_mat_ids: ID of newly added materials
    :type new_mat_ids: iter
    :param removed_mat_ids: ID of removed materials
    :type removed_mat_ids: iter
    """

    # create actual new materials list
    new_mats = []
    for mat in bpy.data.materials:
        curr_mat_id = str(mat.scs_props.id)
        if curr_mat_id in new_mat_ids:
            new_mats.append(mat)

    scs_root = _object_utils.get_scs_root(obj)
    if scs_root:
        _looks.add_materials(scs_root, new_mats)
        if len(removed_mat_ids) > 0:
            _looks.clean_unused(scs_root)


def __objects_reparent__(parent, new_objs):
    """Hookup function for objects reparent operation.

    :param parent: parent object where all of the objects were parented
    :type parent: bpy.types.Object
    :param new_objs: list of object which were parented to object
    :type new_objs: list of bpy.types.Object
    """

    # fixing parts on newly parented object
    scs_root_object = _object_utils.get_scs_root(parent)
    if scs_root_object:

        part_inventory = scs_root_object.scs_object_part_inventory
        assign_part_index = scs_root_object.scs_props.active_scs_part

        # if active is out of range assign first one
        if assign_part_index >= len(part_inventory) or assign_part_index < 0:
            assign_part_index = 0

        new_mats = []
        for new_obj in new_objs:
            if _object_utils.has_part_property(new_obj):
                new_obj.scs_props.scs_part = part_inventory[assign_part_index].name

            for slot in new_obj.material_slots:
                if slot.material and slot.material not in new_mats:
                    new_mats.append(slot.material)

        _looks.add_materials(scs_root_object, new_mats)


def __objects_copy__(old_objects, new_objects):
    """Hookup function for objects copy operation.

    :param old_objects: old objects from which new ones were created
    :type old_objects: list of bpy.types.Object
    :param new_objects: copies of old objects
    :type new_objects: list of bpy.types.Object
    """

    # try to copy connections for new objects
    _connections_group_wrapper.copy_check(old_objects, new_objects)
    _view3d_utils.tag_redraw_all_view3d()

    # also check for any preview models which should be also copied to new ones
    for i, old_obj in enumerate(old_objects):

        if old_obj.scs_props.locator_preview_model_present:
            _preview_models.load(new_objects[i])


def __objects_delete__(unparented_objects):
    """Hookup function for objects delete operation

    :param unparented_objects: objects which were unparented during delete
    :type unparented_objects: list of bpy.types.Objects
    """

    # fix connections recalculations for unparented
    _connections_group_wrapper.force_recalculate(unparented_objects)
    _view3d_utils.tag_redraw_all_view3d()

    # delete unused previe models
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if "scs_props" in obj.data and obj.data.scs_props.locator_preview_model_path != "" and not obj.parent:

                _preview_models.unlink(obj)


def __object_rename__(old_name, new_name):
    """Hookup function for object rename operation

    :param old_name: old name of an object
    :type old_name: str
    :param new_name: new name of an object
    :type new_name: str
    """

    # send rename notify into connections storage
    if _connections_group_wrapper.rename_locator(old_name, new_name):
        _view3d_utils.tag_redraw_all_view3d()

    # send rename notify to preview models
    _preview_models.rename(old_name, new_name)


def _fix_ex_parent(obj):
    """Fixes ex parent settings which were caused by re/unparenting.
    NOTE: ex parent is readed from parent identity property

    :param obj: SCS Blender object from which ex parent object should be taken
    :type obj: bpy.types.Object
    """

    # fix children count for ex parent
    if obj.scs_props.parent_identity in bpy.data.objects:
        ex_parent_obj = bpy.data.objects[obj.scs_props.parent_identity]
        ex_parent_obj.scs_cached_num_children = len(ex_parent_obj.children)

        ex_parent_scs_root = _object_utils.get_scs_root(ex_parent_obj)
        if ex_parent_scs_root:
            _looks.clean_unused(ex_parent_scs_root)


def _fix_children(obj):
    for child in obj.children:
        child.scs_props.parent_identity = obj.name