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
import bmesh
from io_scs_tools.internals.preview_models.cache import PrevModelsCache
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.consts import Colors as _COL_consts
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

_cache = PrevModelsCache()


def init():
    """Initialize preview models system by initalizing cache and directly updating all preview models in blend file.
    """
    _cache.init()

    update()


def rename(old_name, new_name):
    """Renames entry in preview models system if it exists

    :param old_name: old name of locator/preview model
    :type old_name: str
    :param new_name: new name of locator/preview model
    :type new_name: str
    """
    _cache.rename_entry(old_name, new_name)


def link(locator, preview_model):
    """Links preview model to a locator and makes the proper setup

    :param locator: locator object to which given preview model will be linked
    :type locator: bpy.types.Object
    :param preview_model: preview model object which will be linked to given locator object
    :type preview_model: bpy.types.Object
    """

    # parenting
    preview_model.parent = locator
    preview_model.scs_props.parent_identity = locator.name

    # fix object children count so it won't trigger reparent code
    locator.scs_cached_num_children = len(locator.children)

    preview_model.scs_props.object_identity = preview_model.name
    preview_model.hide_select = True

    # now add preview model to all collections locator is in
    for col in locator.users_collection:
        if preview_model.name in col.objects:
            continue
        col.objects.link(preview_model)

    # fix scene objects count so it won't trigger another copy cycle
    bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)

    # insert it to preview models cache
    _cache.add_entry(locator.name, preview_model.name)

    # set the correct draw type of the preview model
    preview_model.display_type = locator.scs_props.locator_preview_model_type

    locator.scs_props.locator_preview_model_present = True


def unlink(preview_model):
    """Unlinks preview model from it's locator
    NOTE: given preview model must exists!


    :param preview_model: preview model object which should be removed
    :type preview_model: bpy.types.Object
    """

    lprint('D Preview model to be deleted: %r', (preview_model.name,))

    _cache.delete_entry(preview_model.name)

    bpy.data.objects.remove(preview_model)

    bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)


def load(locator, deep_reload=False):
    """Makes a preview model for a locator and link it to it
    NOTE: locator preview model path must be set

    :param locator: locator object to which preview model should be set
    :type locator: bpy.types.Object
    :param deep_reload: should model be reloaded completely? Use in case model mesh should be freshly loaded from disc
    :type deep_reload: bool
    :return: True if preview model was set; False otherwise
    :rtype: bool
    """

    load_model = True
    abs_filepath = ""
    if not locator.scs_props.locator_show_preview_model:
        load_model = False
    else:
        filepath = locator.scs_props.locator_preview_model_path
        if filepath:
            if filepath.lower().endswith(".pim"):
                abs_filepath = _path_utils.get_abs_path(filepath, skip_mod_check=True)
                if not os.path.isfile(abs_filepath):
                    lprint("W Locator %r has invalid path to Preview Model PIM file: %r",
                           (locator.name, _path_utils.readable_norm(abs_filepath)))
                    load_model = False
            else:
                lprint("W Locator %r has invalid path to Preview Model PIM file: %r",
                       (locator.name, _path_utils.readable_norm(filepath)))
                load_model = False
        else:
            load_model = False

    if load_model:
        prem_name = str("prem_" + locator.name)
        old_mesh = _get_model_mesh(locator)
        new_mesh = None

        # we need to load preview model, if old mesh is not found or deep reload is requested
        if not old_mesh or deep_reload:
            from io_scs_tools.imp import pim as _pim_import

            obj = _pim_import.load_pim_file(bpy.context, abs_filepath, preview_model=True)

            # in case used preview model doesn't have any mesh, abort loading, report error and reset path
            # Path has to be reset to prevent loading preview model over and over again
            # from possible callbacks trying to fix not present preview model
            if not obj:
                message = "Selected PIM model doesn't have any mesh inside, so it can not be used as a preview model."
                bpy.ops.wm.scs_tools_show_message_in_popup('INVOKE_DEFAULT',
                                                           is_modal=True, title="Preview Model Load Error!", message=message,
                                                           width=500,
                                                           height=100)
                lprint("E " + message)
                locator.scs_props.locator_preview_model_path = ""
                return False

            # got the new mesh!
            new_mesh = obj.data

            # set preview model path to mesh, so it can be reused next time user requests same preview model
            new_mesh.scs_props.locator_preview_model_path = locator.scs_props.locator_preview_model_path

            # now remove imported object, as we need only mesh
            bpy.data.objects.remove(obj, do_unlink=True)

        # if new mesh was created, make sure to copy it over to old one,
        # so any locator with same preview model path, will also get reloaded mesh.
        if new_mesh and old_mesh:

            # use bmesh module to copy data from mesh to mesh
            bm = bmesh.new()
            bm.from_mesh(new_mesh)
            bm.to_mesh(old_mesh)
            bm.free()

            # once copied new mesh can be removed
            bpy.data.meshes.remove(new_mesh)
        elif not old_mesh:  # there is no old mesh yet, thus just link new one to old
            old_mesh = new_mesh

        # (re)assign material to mesh
        old_mesh.materials.clear()
        old_mesh.materials.append(_get_material())

        # recover preview model object if exists, otherwise create new
        prev_model_name = _cache.get_entry(locator.name)
        if prev_model_name and prev_model_name in bpy.data.objects:
            prev_model = bpy.data.objects[prev_model_name]
        else:
            prev_model = bpy.data.objects.new(name=prem_name, object_data=old_mesh)

        # finally link preview model back to locator
        link(locator, prev_model)

        return True
    else:
        return False


def unload(locator):
    """Clears a preview model from a locator

    :param locator: locator object from which preview model should be deleted
    :type locator: bpy.types.Object
    """

    for child in locator.children:
        if child.data and "scs_props" in child.data:
            if child.data.scs_props.locator_preview_model_path != "":
                unlink(child)

    locator.scs_props.locator_preview_model_present = False


def fix_visibilites():
    """Fix preview model visibilites and collection assignemenet over all visible objects."""

    for obj in bpy.context.view_layer.objects:
        fix_visibility(obj)


def fix_visibility(locator):
    """Fix collections linking and hide property for preview model on given locator

    :param locator: locator object for which preview model layers should synced
    :type locator: bpy.types.Object
    """

    prevm_id = _cache.get_entry(locator.name)

    if prevm_id:

        # make sure that preview model is uncached if doesn't exists anymore
        if prevm_id not in bpy.data.objects:
            lprint("D Fix layers from preview model will uncache %r", (prevm_id,))
            _cache.delete_entry(prevm_id)
            return

        prevm_obj = bpy.data.objects[prevm_id]

        # layers check
        if prevm_obj.users_collection != locator.users_collection:

            # first remove from existing collections
            for col in prevm_obj.users_collection:
                col.objects.unlink(prevm_obj)

            # now add preview model back to all collections locator is in
            for col in locator.users_collection:
                col.objects.link(prevm_obj)

        # hide property check
        if prevm_obj.hide_get() != locator.hide_get():
            prevm_obj.hide_set(locator.hide_get())

        if prevm_obj.hide_viewport != locator.hide_viewport:
            prevm_obj.hide_viewport = locator.hide_viewport


def update(force=False):
    """Updates all locators with assigned preview models to current visibility settings.

    :param force: force reloads preview models even when they are flagged as loaded (however not a deep reload, existing mesh won't be re-imported)
    :type force: bool
    """
    show_preview_models = _get_scs_globals().show_preview_models

    # due to delete reasons collect names and operate on names instead directly on bpy.data.objects iterator, just to be safe
    obj_names = []
    for obj in bpy.data.objects:
        obj_names.append(obj.name)

    for obj_name in obj_names:

        if obj_name not in bpy.data.objects:
            continue

        obj = bpy.data.objects[obj_name]

        is_prev_model_locator = (
                obj.type == "EMPTY" and
                obj.scs_props.empty_object_type == "Locator" and
                obj.scs_props.locator_type in {"Prefab", "Model"}
        )

        if not is_prev_model_locator:
            continue

        should_have_prev_model = (
                show_preview_models and
                obj.scs_props.locator_show_preview_model and
                obj.scs_props.locator_preview_model_path != ''
        )

        if should_have_prev_model:
            if not obj.scs_props.locator_preview_model_present or force:
                if not load(obj):
                    unload(obj)
            else:
                fix_visibility(obj)
        elif obj.scs_props.locator_preview_model_path != '':
            unload(obj)


def _get_model_mesh(locator):
    """Creates and returns new object if mesh already exists in Blender data block

    :return: mesh if exists; None otherwise
    :rtype: None | bpy.types.Mesh
    """
    for mesh in bpy.data.meshes:
        if mesh.scs_props.locator_preview_model_path == locator.scs_props.locator_preview_model_path:
            return mesh

    return None


def _get_material(reload=False):
    """Creates and returns material for preview objects.

    :param reload: True if material should be rebuilt (use in case sth changes in implementation)
    :type reload: bool
    :return: preview model material
    :rtype:
    """

    # if exists return immediatelly
    if _MAT_consts.prevm_material_name in bpy.data.materials and not reload:
        return bpy.data.materials[_MAT_consts.prevm_material_name]

    # create new or get existing
    if _MAT_consts.prevm_material_name in bpy.data.materials:
        mat = bpy.data.materials[_MAT_consts.prevm_material_name]
    else:
        mat = bpy.data.materials.new(_MAT_consts.prevm_material_name)

    # enable nodes
    mat.use_nodes = True

    # sets viewport color for solid rendering
    mat.diffuse_color = _COL_consts.prevm_color

    # clear node tree
    node_tree = mat.node_tree
    node_tree.nodes.clear()

    pos_x_shift = 185

    # create nodes
    light_dir_n = node_tree.nodes.new("ShaderNodeVectorTransform")
    light_dir_n.location = (0, 150)
    light_dir_n.vector_type = "VECTOR"
    light_dir_n.convert_from = "CAMERA"
    light_dir_n.convert_to = "WORLD"
    light_dir_n.inputs[0].default_value = (0, 0.7071, -0.7071)

    geom_n = node_tree.nodes.new("ShaderNodeNewGeometry")
    geom_n.location = (0, -100)

    dot_product_n = node_tree.nodes.new("ShaderNodeVectorMath")
    dot_product_n.location = (pos_x_shift, 0)
    dot_product_n.operation = "DOT_PRODUCT"

    color_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
    color_mult_n.location = (pos_x_shift * 2, 0)
    color_mult_n.operation = "MULTIPLY"
    color_mult_n.inputs[1].default_value = _COL_consts.prevm_color[:3]

    emission_shader_n = node_tree.nodes.new("ShaderNodeEmission")
    emission_shader_n.location = (pos_x_shift * 3, 0)

    out_mat_n = node_tree.nodes.new("ShaderNodeOutputMaterial")
    out_mat_n.location = (pos_x_shift * 4, 0)

    # create links
    node_tree.links.new(dot_product_n.inputs[0], light_dir_n.outputs[0])
    node_tree.links.new(dot_product_n.inputs[1], geom_n.outputs['Normal'])

    node_tree.links.new(color_mult_n.inputs[0], dot_product_n.outputs['Value'])

    node_tree.links.new(emission_shader_n.inputs['Color'], color_mult_n.outputs[0])

    node_tree.links.new(out_mat_n.inputs['Surface'], emission_shader_n.outputs['Emission'])

    return mat
