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
import bmesh
from bpy_extras import object_utils as bpy_object_utils
from mathutils import Vector
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import math as _math
from io_scs_tools.utils import name as _name
from io_scs_tools.utils import mesh as _mesh
from io_scs_tools.utils import convert as _convert
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def get_scs_root(obj):
    """Takes any object and returns it's 'SCS Root Object' or None."""

    parent = obj
    while parent and parent.scs_props.empty_object_type != 'SCS_Root':
        parent = parent.parent

    if parent and parent.scs_props.empty_object_type == 'SCS_Root':
        return parent
    else:
        return None


def gather_scs_roots(objs):
    """Gets all the SCS root objects from given objects.

    :param objs: Blender objects
    :type objs: collections.Iterable[bpy.types.Object]
    :return: list of roots, if none are found then empty list
    :rtype: list[bpy.types.Object]
    """
    roots = {}
    for obj in objs:
        curr_root = get_scs_root(obj)
        if curr_root and curr_root.name not in roots:
            roots[curr_root.name] = curr_root

    return roots.values()


def sort_out_game_objects_for_export(objects):
    """Takes initial selection (list of Blender Objects) and returns a dictionary where
    key is 'SCS Root Object' and its value is a list of Mesh and/or Locator Objects which
    makes the content of the 'SCS Game Object'.
    The function can print out on request some information about results to the console."""
    game_objects_dict = {}

    # PRE-SORTING
    data_objects = []
    rejected_objects = []
    for obj in objects:
        if obj.type == 'EMPTY':
            if obj.scs_props.empty_object_type == 'SCS_Root':
                game_objects_dict[obj] = []
            elif obj.scs_props.empty_object_type == 'Locator':
                data_objects.append(obj)
        elif obj.type == 'MESH':
            if obj.data.scs_props.locator_preview_model_path == "":  # Reject Preview Models...
                data_objects.append(obj)
            else:
                rejected_objects.append(obj)
        elif obj.type == 'ARMATURE':
            data_objects.append(obj)
        else:
            rejected_objects.append(obj)

    # SORTING
    for obj in data_objects:
        scs_root_object = get_scs_root(obj)
        if scs_root_object:
            if scs_root_object in game_objects_dict:

                # object insertion sorting by name
                i = 0
                while i < len(game_objects_dict[scs_root_object]) and obj.name > game_objects_dict[scs_root_object][i].name:
                    i += 1

                game_objects_dict[scs_root_object].insert(i, obj)
            else:
                game_objects_dict[scs_root_object] = [obj]
        else:
            rejected_objects.append(obj)

    # PRINTOUTS
    dump_level = int(_get_scs_globals().dump_level)
    if dump_level > 2:
        message = "D Rejected Objects:\n\t   "
        for obj in rejected_objects:
            message += ' - %r rejected\n\t   ' % obj.name

        lprint(message)

    if dump_level > 2:
        message = "D 'SCS Game Objects' to export:\n\t   "
        for scs_root_object in game_objects_dict:
            message += ' - filename: %r\n\t   ' % scs_root_object.name
            for scs_game_object in game_objects_dict[scs_root_object]:
                message += '     %r\n\t   ' % scs_game_object.name

        lprint(message)

    return game_objects_dict


def exclude_switched_off(game_objects_dict):
    """Takes 'SCS Game Object' dictionary and returns the same dictionary without
    the Game Objects which were turned off for export in UI."""
    new_game_objects_dict = {}
    for scs_root_object in game_objects_dict:
        if scs_root_object.scs_props.empty_object_type == 'SCS_Root':
            if scs_root_object.scs_props.scs_root_object_export_enabled:
                new_game_objects_dict[scs_root_object] = game_objects_dict[scs_root_object]
    return new_game_objects_dict


def get_children(obj, children=[], reset=True):
    """Takes an object and returns all its children objects in a list. (Recursive)"""
    if reset:
        children = []
    for child in obj.children:
        # filter out multilevel scs roots
        isnt_root = not (child.scs_props.empty_object_type == "SCS Root" and child.type == 'EMPTY')
        isnt_preview_model = not (child.type == "MESH" and child.data and "scs_props" in child.data and
                                  child.data.scs_props.locator_preview_model_path != "")
        if isnt_root and isnt_preview_model and child not in children:
            children.append(child)
            children = get_children(child, children, False)
    return children


def get_siblings(obj):
    """Gets sibling objects of given object within SCS Game Object. If no siblings empty list is returned"""
    root = get_scs_root(obj)
    if root:
        return get_children(root)
    else:
        return []


def collect_parts_on_root(scs_root_object):
    """Gathers used 'SCS Part' names and objects belonging to them.

    :param scs_root_object: Blender SCS root object
    :type scs_root_object: bpy.types.Object
    :return: dictionary of USED parts within given root object and list of objects for each entry
    :rtype: dict[str, list[bpy.types.Object]]
    """
    parts = {}

    children = get_children(scs_root_object)
    for child in children:

        if has_part_property(child):

            obj_part = child.scs_props.scs_part
            if obj_part not in parts:
                parts[obj_part] = []

            parts[obj_part].append(child)

    return parts


def update_convex_hull_margins(obj):
    """

    :param obj:
    :type obj:
    :return:
    :rtype:
    """
    bbox = obj.scs_props.get("coll_convex_bbox", None)
    bbcenter = obj.scs_props.get("coll_convex_bbcenter", None)
    # print(' oo bbox_width: %s - bbox_height: %s - bbox_depth: %s' % (bbox[0], bbox[1], bbox[2]))
    # print(' oo bbcenter: <%s, %s, %s>' % (bbcenter[0], bbcenter[1], bbcenter[2]))
    verts = obj.scs_props.get("coll_convex_verts", None)
    verts_orig = obj.scs_props.get("coll_convex_verts_orig", None)
    if bbox and bbcenter and verts and verts_orig:
        margin = obj.scs_props.locator_collider_margin
        scaling = _math.scaling_width_margin(bbox, margin)
        # print(' oo margin: %s - scaling: <%s, %s, %s>' % (margin, scaling[0], scaling[1], scaling[2]))

        # APPLY THE SCALE TO OBJECT VERTICES
        scaled_verts = []
        for vert_orig in verts_orig:
            vert_loc = []
            for axis in range(3):
                length = vert_orig[axis] - bbcenter[axis]
                new_length = length * scaling[axis]
                vert_loc.append(bbcenter[axis] + new_length)
            scaled_verts.append(tuple(vert_loc))
        obj.scs_props["coll_convex_verts"] = scaled_verts
    return


def get_collider_props(obj, convex_props):
    """

    :param obj: Blender Object
    :type obj: bpy.types.Object
    :param convex_props: ...
    :type convex_props: dict
    :return: ...
    :rtype: dict
    """
    convex_props['location'] = Vector(obj.location)
    convex_props['rotation_mode'] = obj.rotation_mode
    convex_props['rotation'] = Vector(obj.rotation_euler)
    convex_props['locator_collider_margin'] = obj.scs_props.locator_collider_margin
    convex_props['locator_collider_wires'] = obj.scs_props.locator_collider_wires
    convex_props['locator_collider_faces'] = obj.scs_props.locator_collider_faces
    convex_props['locator_collider_mass'] = obj.scs_props.locator_collider_mass
    convex_props['locator_collider_material'] = obj.scs_props.locator_collider_material
    return convex_props


def set_collider_props(obj, convex_props):
    if 'location' in convex_props:
        obj.location = convex_props['location']
    if 'rotation_mode' in convex_props:
        obj.rotation_mode = convex_props['rotation_mode']
    if 'rotation' in convex_props:
        obj.rotation_euler = convex_props['rotation']
    if 'locator_collider_margin' in convex_props:
        obj.scs_props.locator_collider_margin = convex_props['locator_collider_margin']
    if 'locator_collider_wires' in convex_props:
        obj.scs_props.locator_collider_wires = convex_props['locator_collider_wires']
    if 'locator_collider_faces' in convex_props:
        obj.scs_props.locator_collider_faces = convex_props['locator_collider_faces']
    if 'locator_collider_mass' in convex_props:
        obj.scs_props.locator_collider_mass = convex_props['locator_collider_mass']
    if 'locator_collider_material' in convex_props:
        obj.scs_props.locator_collider_material = convex_props['locator_collider_material']
    return obj


def make_mesh_from_verts_and_faces(verts, faces, convex_props):
    """Creates a new mesh object from provided vertices and faces and their properties."""
    new_mesh = bpy.data.meshes.new(convex_props['name'])
    new_bm = bmesh.new()

    # MAKE VERTICES
    _mesh.bm_make_vertices(new_bm, verts)

    # MAKE FACES
    _mesh.bm_make_faces(new_bm, faces, [])

    new_bm.to_mesh(new_mesh)
    new_mesh.update()
    new_bm.free()

    # Add the mesh as an object into the scene with this utility module.
    new_object = bpy_object_utils.object_data_add(bpy.context, new_mesh)
    new_object = set_collider_props(new_object, convex_props)
    new_object.location = convex_props['location']
    new_object.rotation_euler = convex_props['rotation']

    return new_object


def make_objects_selected(objects, active_object=None):
    """Select only the given objects. Deselect all others.

    :param objects: list of objects to be selected
    :type objects: list, tuple
    :param active_object: object to be made active; if None active object remains unchanged
    :type active_object: bpy.types.Object
    :rtype: None
    """
    bpy.ops.object.select_all(action='DESELECT')
    if len(objects) > 0:
        for obj in objects:
            # select only real objects
            if obj:
                obj.select_set(True)

    if active_object:
        bpy.context.view_layer.objects.active = active_object


def pick_objects_from_selection(operator_object, needs_active_obj=True, obj_type='MESH'):
    """Returns Mesh objects in selection and active object separately if it exists.
    If the active object is mandatory, it handles all kinds of context Errors.

    :param operator_object:
    :type operator_object: bpy.types.Operator
    :param needs_active_obj:
    :type needs_active_obj: bool
    :param obj_type:
    :type obj_type: str
    :return: mesh objects from selection and active object
    :rtype: tuple(list, object)
    """
    if needs_active_obj:
        if not bpy.context.active_object:
            operator_object.report({'ERROR_INVALID_CONTEXT'}, "No Active Object!")
            return None, None
        if bpy.context.active_object not in bpy.context.selected_objects:
            operator_object.report({'ERROR_INVALID_CONTEXT'}, "Active Object is not a part of selection!")
            return None, None
        if bpy.context.active_object.type not in ('MESH', 'EMPTY'):
            operator_object.report({'ERROR_INVALID_CONTEXT'}, "Active Object is not of Mesh type!")
            return None, None
    mesh_objects = []
    active_object = bpy.context.active_object
    for obj in bpy.context.selected_objects:
        if obj.type == obj_type:
            if needs_active_obj:
                if obj is not active_object:
                    mesh_objects.append(obj)
            else:
                mesh_objects.append(obj)
    if mesh_objects:
        return mesh_objects, active_object
    else:
        return None, active_object


def create_convex_data(objects, convex_props={}, return_hull_object=False, max_face_count=256):
    """Creates a convex hull from selected objects...

    :param objects: list of blender objects to make convex hull from
    :type objects: list[bpy.types.Object]
    :param convex_props: existing convexr properties gotten with get_collider_props
    :type convex_props: dict
    :param return_hull_object: should convex data be as normal blender mesh object?
    :type return_hull_object: bool
    :param max_face_count: maximum number of faces that returned hull object can have, in interval (256, 6)
    :type max_face_count: int
    :return: tuple[(verts, faces, bb_size, bb_center), convex_props, returned_hull_object)
    :rtype: tuple[tuple, dict, bpy.types.Object]
    """

    assert 6 <= max_face_count <= 256

    # save original selection
    original_selection = []
    for obj in bpy.context.selected_objects:
        original_selection.append(obj)

    # save original active
    original_active = bpy.context.active_object

    # make a selection from mesh objects
    make_objects_selected(objects)

    # if multiple objects, create joined mesh from all selected meshes
    bpy.ops.object.duplicate_move()
    if bpy.context.active_object not in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

    if len(original_selection) > 1:
        bpy.ops.object.join()

    obj = object_to_delete = bpy.context.active_object

    for modifier in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    # get properties from the resulting object
    if not convex_props:
        convex_props = {'name': obj.name}
        convex_props = get_collider_props(obj, convex_props)

    # create convex hull data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)

    # delete everything except verts, otherwise convex hull doesn't work as expected
    for face in bm.faces:
        bm.faces.remove(face)
    for edge in bm.edges:
        bm.edges.remove(edge)

    convex_hull_res = bmesh.ops.convex_hull(bm, input=bm.verts)

    # now again remove everything except real convex hull geometry
    for geom_type in ('geom_interior', 'geom_unused', 'geom_holes'):
        for item in convex_hull_res[geom_type]:
            try:
                if isinstance(item, bmesh.types.BMVert):
                    bm.verts.remove(item)
                elif isinstance(item, bmesh.types.BMEdge):
                    bm.edges.remove(item)
                elif isinstance(item, bmesh.types.BMFace):
                    bm.faces.remove(item)
            except ReferenceError:
                continue

    # transform back to mesh
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # if convex locator creation then decimate convex hull even more to make sure mesh is not to big for convex locator
    if not return_hull_object and len(mesh.polygons) > max_face_count:

        initial_polycount = len(mesh.polygons)

        modifier = obj.modifiers.new("decimate", "DECIMATE")
        bpy.context.view_layer.update()

        while (modifier.face_count > max_face_count or modifier.face_count < max(max_face_count - 10, 10)) and modifier.ratio > 0.01:

            # divide ratio by 2 until we get into desired count of faces
            diff = abs(modifier.ratio) / 2.0
            if modifier.face_count > max_face_count:
                diff *= -1.0

            modifier.ratio += diff
            bpy.context.view_layer.update()  # invoke depsgraph update to get updated modifier
            print("WHILE:", modifier.face_count, modifier.ratio)

        bpy.ops.object.modifier_apply(modifier=modifier.name)

        lprint("I Mesh used for convex locator was decimated because it had to many faces for convex locator.\n\t   " +
               "Maximum triangles count is %i but mesh had %s triangles.", (max_face_count, initial_polycount))

    # retrieve convex data
    verts = []
    faces = []
    min_val = [None, None, None]
    max_val = [None, None, None]
    for vert in mesh.vertices:
        verts.append(tuple(vert.co))

        # Bounding Box data evaluation
        min_val, max_val = _math.evaluate_minmax(verts[-1], min_val, max_val)

    for poly in mesh.polygons:
        assert len(poly.vertices) == 3
        faces.append(tuple(poly.vertices))

    # bbox data creation
    bbox, bbcenter = _math.get_bb(min_val, max_val)
    geom = (verts, faces, bbox, bbcenter)

    # should have volume, if it doesn't it's not really a shape
    for axis_size in bbox:
        if axis_size == 0:
            geom = None

    # create convex hull object to return
    resulting_convex_object = None
    if return_hull_object and geom:
        resulting_convex_object = make_mesh_from_verts_and_faces(verts, faces, convex_props)

        # make sure resulting object is on the same collections as joined object
        for col in resulting_convex_object.users_collection:
            col.objects.unlink(resulting_convex_object)

        for col in obj.users_collection:
            col.objects.link(resulting_convex_object)

    make_objects_selected((object_to_delete,))
    bpy.ops.object.delete(use_global=True)

    # make original active object active again
    if original_selection or original_active:
        make_objects_selected(original_selection, active_object=original_active)

    return geom, convex_props, resulting_convex_object


def add_collider_convex_locator(geom_data, convex_props, locator=None):
    """Takes geometry data array (vertices, faces), name, location and rotation
    and creates new Convex Collision Locator."""
    if not locator:
        bpy.ops.object.empty_add(
            location=convex_props['location'],
            rotation=convex_props['rotation'],
        )
        bpy.context.active_object.name = convex_props['name']
        locator = bpy.data.objects.get(convex_props['name'])
        locator.scs_props.empty_object_type = 'Locator'
        locator.scs_props.locator_type = 'Collision'
        locator = set_collider_props(locator, convex_props)
    locator.scs_props.object_identity = locator.name

    locator.scs_props.locator_collider_type = 'Convex'
    locator.scs_props["coll_convex_verts_orig"] = geom_data[0]
    locator.scs_props["coll_convex_verts"] = geom_data[0]
    locator.scs_props["coll_convex_faces"] = geom_data[1]
    locator.scs_props["coll_convex_bbox"] = geom_data[2]
    locator.scs_props["coll_convex_bbcenter"] = geom_data[3]
    locator.scs_props.locator_collider_vertices = len(geom_data[0])
    return locator


def make_mesh_convex_from_locator(obj):
    convex_props = {}
    verts = obj.scs_props.get("coll_convex_verts_orig", None)
    faces = obj.scs_props.get("coll_convex_faces", None)
    convex_props['name'] = obj.name
    convex_props = get_collider_props(obj, convex_props)

    new_object = make_mesh_from_verts_and_faces(verts, faces, convex_props)

    # DELETE ORIGINAL LOCATOR AND SELECT NEW CREATED MESH CONVEX
    make_objects_selected((obj,))
    bpy.ops.object.delete(use_global=True)
    return new_object


def create_collider_convex_locator(geom, convex_props, mesh_objects, delete_mesh_objects):
    locator = None
    if geom:
        locator = add_collider_convex_locator(geom, convex_props)

        # DEBUG PRINTOUT
        # print('\n > geom: %s' % str(geom))
        # for vert in geoms[geom][0]:
        # print('   > vert: %s' % str(vert))
        # for face in geoms[geom][1]:
        # print('   > face: %s' % str(face))

        # DELETE ORIGINAL LOCATOR AND SELECT NEW CREATED MESH CONVEX
        if delete_mesh_objects:
            make_objects_selected(mesh_objects)
            bpy.ops.object.delete(use_global=True)
            if locator:
                locator.select_set(True)

        update_convex_hull_margins(locator)
    return locator


def show_loc_type(objects, loc_type, pref_type=None, hide_state=None, view_only=True):
    """Shows/hides locators by type.

    :param objects: objects upon which show  function should be evaluated
    :type objects: list of bpy.types.Object
    :param loc_type: type of locator (item from locators enum property)
    :type loc_type: str
    :param pref_type: type of prefab locator (item from prefab locators enum property)
    :type pref_type: str
    :param hide_state: if hidden state is already known this is paramater that holds it
    :type hide_state: bool | None
    :param view_only: if view only should be used; it will hide all objects except thoose which are specified by type
    :type view_only: bool
    """

    for obj in objects:
        if obj.type == "EMPTY" and obj.scs_props.empty_object_type == "Locator" and obj.scs_props.locator_type == loc_type:
            if obj.scs_props.locator_type == 'Prefab' and pref_type:
                if obj.scs_props.locator_prefab_type == pref_type:

                    if hide_state is None:

                        hide_state = not obj.hide_get()

                    hide_set(obj, hide_state)

                elif view_only:

                    hide_set(obj, True)

            else:

                if hide_state is None:

                    hide_state = not obj.hide_get()

                hide_set(obj, hide_state)

        elif view_only:

            hide_set(obj, True)


def get_object_materials(obj):
    """
    Takes an object and returns all its materials or a string "_empty_material_" if object
    has no material. For every unused material (existing in a material slot, but unassigned
    to any face) it returns "None" value and for every empty material slot "_empty_slot_"
    string is returned.
    :param obj:
    :return:
    """
    object_materials = []
    if len(obj.material_slots) > 0:
        for slot_i, slot in enumerate(obj.material_slots):
            if slot.material is not None:
                mesh = obj.data
                mat_found = False
                for poly in mesh.polygons:
                    if poly.material_index == slot_i:
                        mat_found = True
                        break
                if not mat_found:
                    lprint('I Unused material "%s" in slot detected in object "%s"!', (slot.material, obj.name))
                    object_materials.append(None)
                else:
                    object_materials.append(slot.material)
            else:
                lprint('I Empty material slot detected in object "%s"! "_empty_material_" used for it.', obj.name)
                object_materials.append("_empty_slot_")
    else:
        lprint('I No material detected in object "%s"! "_empty_material_" used for it.', obj.name)
        object_materials.append("_empty_material_")
    return object_materials


def disable_modifier(modifier, disabled_modifiers):
    """
    Takes a Modifier and a list. If the Modifier is enabled in 3D Viewport it disables
    it and adds its name to the list.
    :param modifier:
    :param disabled_modifiers:
    :return:
    """
    if modifier.name not in disabled_modifiers:
        disabled_modifiers[modifier.name] = (modifier.show_viewport, modifier.show_render)
        modifier.show_viewport = False
        modifier.show_render = False
    return disabled_modifiers


def disable_modifiers(obj, modifier_type_to_disable='EDGE_SPLIT', inverse=False):
    """
    Disables all instances of given modifier type on provided Object and returns its names in a list.
    If 'inverse' is True, it disables all Modifiers except given modifier type.
    :param obj:
    :param modifier_type_to_disable:
    :param inverse:
    :return:
    """
    disabled_modifiers = dict()
    for modifier in obj.modifiers:
        if modifier_type_to_disable == 'ANY':
            disabled_modifiers = disable_modifier(modifier, disabled_modifiers)
        else:
            if modifier.type == modifier_type_to_disable:
                if not inverse:
                    disabled_modifiers = disable_modifier(modifier, disabled_modifiers)
            else:
                if inverse:
                    disabled_modifiers = disable_modifier(modifier, disabled_modifiers)
    return disabled_modifiers


def get_mesh(obj):
    """
    Returns Mesh data of provided Object (un)affected with specified Modifiers, which are
    evaluated as within provided Scene.
    """
    disabled_modifiers = dict()

    # always disable armature modifiers from SCS animations
    # to prevent vertex rest position change because of the animation
    sibling_objs = get_siblings(obj)
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE" and modifier.object in sibling_objs and modifier.object.type == "ARMATURE":
            disabled_modifiers = disable_modifier(modifier, disabled_modifiers)

    if _get_scs_globals().export_output_type.startswith('EF'):
        if _get_scs_globals().export_apply_modifiers:
            if _get_scs_globals().export_exclude_edgesplit:
                disabled_modifiers.update(disable_modifiers(obj, modifier_type_to_disable='EDGE_SPLIT'))
    else:
        if not _get_scs_globals().export_apply_modifiers:
            if _get_scs_globals().export_include_edgesplit:
                disabled_modifiers.update(disable_modifiers(obj, modifier_type_to_disable='EDGE_SPLIT', inverse=True))
            else:
                disabled_modifiers.update(disable_modifiers(obj, modifier_type_to_disable='ANY', inverse=True))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

    restore_modifiers(obj, disabled_modifiers)

    return mesh


def restore_modifiers(obj, disabled_modifiers):
    """
    Make modifiers settings as they were before calling "get_mesh".
    :param obj:
    :param disabled_modifiers:
    :return:
    """
    for modifier_name, show_states in disabled_modifiers.items():
        obj.modifiers[modifier_name].show_viewport = show_states[0]
        obj.modifiers[modifier_name].show_render = show_states[1]
        lprint("D Restored modifier with name: %r on object with name: %r", (modifier_name, obj.name))


def get_stream_vgs(obj):
    """
    Takes an object and returns all vertex group layers existing in the mesh and
    requested number of empty containers for streams ("section_data" data type).
    :param obj:
    :return:
    """
    if obj.vertex_groups:
        vg_layers_for_export = []
        streams_vg = []
        for group_i, group in enumerate(obj.vertex_groups):
            streams_vg.append(('_SCALAR' + str(group_i), []))
            vg_layers_for_export.append(group)
            # print('vg_layer: %s' % str(vg_layers_for_export))
            # for item in vg_layers_for_export:
            # print('\tvg_layer: %s' % str(item))
    else:
        vg_layers_for_export = None
        streams_vg = None
        lprint('I NO VG layers in "%s" object!' % obj.name)
    return vg_layers_for_export, streams_vg


def get_vertex_group(layer, vert_index):
    """
    Takes a vertex group layer and vertex index and returns
    weight value of the vertex in the specified layer.
    :param layer:
    :param vert_index:
    :return:
    """
    try:
        vg_weight = layer.weight(vert_index)
    except:
        vg_weight = 0.0
    # print('\tVG%i  w:%f' % (layer.index, vg_weight))
    return vg_weight


def create_locator_empty(name, loc, rot=(0, 0, 0), scale=(1, 1, 1), size=1.0, data_type='Prefab', hookup=None, blend_coords=False):
    """
    Creates an empty object for a Locator.
    :param name:
    :param loc:
    :param rot:
    :param scale:
    :param size:
    :param data_type:
    :param hookup:
    :param blend_coords:
    :return:
    """
    rot_quaternion = None
    if len(rot) == 4:
        rot_quaternion = rot
        rot = (0, 0, 0)

    if blend_coords:
        location = loc
    else:
        location = _convert.change_to_scs_xyz_coordinates(loc, _get_scs_globals().import_scale)

    unique_name = _name.get_unique(name, bpy.data.objects, sep=".")
    locator = bpy.data.objects.new(unique_name, None)
    locator.empty_display_type = 'PLAIN_AXES'
    locator.scs_props.object_identity = locator.name

    # link to active layer and scene and make it active and selected
    bpy.context.view_layer.active_layer_collection.collection.objects.link(locator)
    bpy.context.view_layer.objects.active = locator
    locator.select_set(True)

    # fix scene objects count to avoid callback of new object
    bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)

    locator.location = location

    if rot_quaternion:
        locator.rotation_mode = 'QUATERNION'
        if blend_coords:
            locator.rotation_quaternion = rot_quaternion
        else:
            locator.rotation_quaternion = _convert.change_to_blender_quaternion_coordinates(rot_quaternion)
    else:
        locator.rotation_mode = 'XYZ'
        locator.rotation_euler = rot

    locator.scale = scale
    locator.scs_props.empty_object_type = 'Locator'
    locator.scs_props.locator_type = data_type

    if data_type == "Prefab":
        locator.scs_props.scs_part = ""

    if hookup:
        locator.scs_props.locator_model_hookup = hookup

    return locator


def set_attr_if_different(obj, attr, value):
    """Set attribute on object only if its value differs from given value.
    \rIt also compensate for too precise float numbers, because of Python precision issue.
    \rNOTE: The problem here is, that if the numbers are always slightly different, it can trigger an endless update on Locators.

    :param obj: Object
    :type obj: object
    :param attr: Attribute
    :type attr: str
    :param value: Value
    :type value: object
    """
    if hasattr(obj, attr):
        if isinstance(value, float):
            different = abs(getattr(obj, attr) - value) > 0.00001
        else:
            different = getattr(obj, attr) != value
        if different:
            setattr(obj, attr, value)


def has_part_property(obj):
    """Return True if SCS object part property must exists on the object.
    NOTE: only prefab locators with exception of signs doesn't have SCS Part.

    :param obj: object which we want to test if it has SCS Part
    :type obj: bpy.types.Object
    :return: True if object has part property; False otherwise
    :rtype: bool
    """

    # NOTE: when changing make sure that "ui/object.py", "operators/object.py" and
    # import/export are checked for any changes
    return obj.type == "MESH" or not (obj.type == "EMPTY" and
                                      obj.scs_props.empty_object_type == "Locator" and
                                      obj.scs_props.locator_type == "Prefab" and
                                      obj.scs_props.locator_prefab_type != "Sign")


def can_assign_terrain_points(context):
    """Tells if user can assign terrain points with given context.

    :param context: blender context
    :type context: bpy.types.Context
    :return: True if given object is Control Node locator; False otherwise
    :rtype: bool
    """
    active_obj = context.active_object
    other_obj = get_other_object(context.selected_objects, active_obj)

    is_root_same_and_valid = get_scs_root(active_obj) is not None and get_scs_root(active_obj) == get_scs_root(other_obj)
    is_other_node_locator = other_obj and (other_obj.type == "EMPTY" and
                                           other_obj.scs_props.empty_object_type == "Locator" and
                                           other_obj.scs_props.locator_type == "Prefab" and
                                           other_obj.scs_props.locator_prefab_type == "Control Node")

    return (active_obj and is_other_node_locator and is_root_same_and_valid and
            active_obj.type == "MESH" and active_obj.mode == "EDIT")


def get_other_object(obj_iterable, original_obj):
    """Get first different object in the iterable from original object.

    NOTE: method looks only first two object, because of avoiding iterations
    in very long list which will slow down blender

    :param obj_iterable: list of objects in which other object should be searched for
    :type obj_iterable: collections.Iterable
    :param original_obj: original object from which other should be different
    :type original_obj: bpy.types.Object
    :return: other object if found; otherwise None
    :rtype: None | bpy.types.Object
    """
    for sel_obj_i, sel_obj in enumerate(obj_iterable):
        if sel_obj_i >= 2:
            return None

        if sel_obj != original_obj:
            return sel_obj

    return None


def set_locators_original_size_and_type(obj):
    """Set original drawing style for Empty object.

    :param obj: Blender Object
    :type obj: bpy.types.Object
    """
    # _object.set_attr_if_different(obj, "empty_display_size", obj.scs_props.locators_orig_display_size)
    if obj.empty_display_size != obj.scs_props.locators_orig_display_size:
        obj.empty_display_size = obj.scs_props.locators_orig_display_size
        obj.scs_props.locators_orig_display_size = 0.0
    if obj.empty_display_type != obj.scs_props.locators_orig_display_type:
        obj.empty_display_type = obj.scs_props.locators_orig_display_type
        obj.scs_props.locators_orig_display_type = ''


def store_locators_original_display_size_and_type(obj):
    """Set Prefab Locator drawing style for Empty object.

    :param obj: Blender Object
    :type obj: bpy.types.Object
    """
    if obj.scs_props.locators_orig_display_size == 0.0:
        set_attr_if_different(obj.scs_props, "locators_orig_display_size", obj.empty_display_size)
        set_attr_if_different(obj.scs_props, "locators_orig_display_type", obj.empty_display_type)


def set_locators_prefab_display_size_and_type(obj):
    """Set Prefab Locator drawing style for Empty object.

    :param obj: Blender Object
    :type obj: bpy.types.Object
    """
    new_draw_size = _get_scs_globals().locator_empty_size * _get_scs_globals().locator_size
    set_attr_if_different(obj, "empty_display_size", new_draw_size)
    set_attr_if_different(obj, "empty_display_type", 'PLAIN_AXES')


def set_locators_model_display_size_and_type(obj):
    """Set Model Locator drawing style for Empty object.

    :param obj: Blender Object
    :type obj: bpy.types.Object
    """
    new_draw_size = _get_scs_globals().locator_empty_size * _get_scs_globals().locator_size
    set_attr_if_different(obj, "empty_display_size", new_draw_size)
    set_attr_if_different(obj, "empty_display_type", 'PLAIN_AXES')


def set_locators_coll_display_size_and_type(obj):
    """Set Collision Locator drawing style for Empty object.

    :param obj: Blender Object
    :type obj: bpy.types.Object
    """
    new_draw_size = 0.5
    if obj.scs_props.locator_collider_type == 'Box':
        bigest_value = max(obj.scs_props.locator_collider_box_x, obj.scs_props.locator_collider_box_y, obj.scs_props.locator_collider_box_z)
        new_draw_size = bigest_value * 0.8
    elif obj.scs_props.locator_collider_type in ('Sphere', 'Capsule', 'Cylinder'):
        new_draw_size = obj.scs_props.locator_collider_dia * 0.8
    elif obj.scs_props.locator_collider_type == 'Convex':
        bbox = obj.scs_props.get("coll_convex_bbox", None)
        bbcenter = obj.scs_props.get("coll_convex_bbcenter", None)
        if bbox and bbcenter:
            scaling = _math.scaling_width_margin(bbox, obj.scs_props.locator_collider_margin)
            val = []
            for axis in range(3):
                val.append((bbox[axis] + abs(bbcenter[axis])) * scaling[axis])
            new_draw_size = max(val) * 0.5
    set_attr_if_different(obj, "empty_display_size", new_draw_size)
    set_attr_if_different(obj, "empty_display_type", 'PLAIN_AXES')


def hide_set(obj, state, view_layer=None):
    """Sets hide state on the object taking into account it's membership in current or given view layer.
    So in case object is not found in view layer, it's hide state doesn't change.

    :param obj: object to hide/unhide
    :type obj: bpy.types.Object
    :param state: True unhide; False hide
    :type state: bool
    :param view_layer: view layer on which hide state should be set; if None hide state is set on active view layer in the bpy context
    :type view_layer: bpy.types.ViewLayer
    :return: True if state was applied, False otherwise
    :rtype: bool
    """
    if view_layer:
        if obj.name in view_layer.objects:
            obj.hide_set(state, view_layer=view_layer)
            return True
    else:
        if obj.name in bpy.context.view_layer.objects:
            obj.hide_set(state)
            return True

    return False


def select_set(obj, state, view_layer=None):
    """Sets select state on the object taking into account it's membership in current or given view layer.
    So in case object is not found in view layer, it's hide state doesn't change.

    :param obj: object to select/deselect
    :type obj: bpy.types.Object
    :param state: True select; False deselect
    :type state: bool
    :param view_layer: view layer on which select state should be set; if None select state is set on active view layer in the bpy context
    :type view_layer: bpy.types.ViewLayer
    :return: True if state was applied, False otherwise
    :rtype: bool
    """
    if view_layer:
        if obj.name in view_layer.objects:
            obj.select_set(state, view_layer=view_layer)
            return True
    else:
        if obj.name in bpy.context.view_layer.objects:
            obj.select_set(state)
            return True

    return False
