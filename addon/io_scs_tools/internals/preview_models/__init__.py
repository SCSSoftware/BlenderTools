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
from io_scs_tools.internals.preview_models.cache import PrevModelsCache
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint

_cache = PrevModelsCache()


def init():
    """Initialize preview models system
    """
    _cache.init()


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

    # link object to the scene
    scene = bpy.context.scene
    if not preview_model.name in scene.objects:
        scene.objects.link(preview_model)

    # fix scene objects count so it won't trigger another copy cycle
    scene.scs_cached_num_objects = len(scene.objects)

    # parenting
    preview_model.parent = locator
    preview_model.scs_props.parent_identity = locator.name

    # fix object children count so it won't trigger reparent code
    locator.scs_cached_num_children = len(locator.children)

    preview_model.scs_props.object_identity = preview_model.name
    preview_model.hide_select = True
    preview_model.layers = locator.layers

    _cache.add_entry(locator.name, preview_model.name)

    # set the correct draw type of the preview model
    preview_model.draw_type = locator.scs_props.locator_preview_model_type

    locator.scs_props.locator_preview_model_present = True


def unlink(preview_model):
    """Unlinks preview model from it's locator
    NOTE: given preview model must exists!


    :param preview_model: preview model object which should be removed
    :type preview_model: bpy.types.Object
    """

    lprint('D Preview model %r deleted', (preview_model.name,))

    _cache.delete_entry(preview_model.name)

    bpy.context.scene.objects.unlink(preview_model)
    bpy.data.objects.remove(preview_model)

    bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)


def load(locator):
    """Makes a preview model for a locator and link it to it
    NOTE: locator preview model path must be set

    :param locator: locator object to which preview model should be set
    :type locator: bpy.types.Object
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

        unload(locator)

        prem_name = str("prem_" + locator.name)
        obj = _get_model_mesh(locator, prem_name)

        if not obj:
            from io_scs_tools.imp import pim as _pim_import

            obj = _pim_import.load_pim_file(bpy.context, abs_filepath, preview_model=True)
            obj.name = prem_name
            obj.data.name = prem_name
            obj.data.scs_props.locator_preview_model_path = locator.scs_props.locator_preview_model_path
            obj.select = False

        link(locator, obj)

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
                # first uncache it
                _cache.delete_entry(child.name)

                bpy.context.scene.objects.unlink(child)
                bpy.data.objects.remove(child)

                # update scene children count to prevent delete to be triggered
                bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)

    locator.scs_props.locator_preview_model_present = False


def fix_visibility(locator):
    """Fix layers visibility and hide property for preview model on given locator

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
        if list(prevm_obj.layers) != list(locator.layers):
            prevm_obj.layers = tuple(locator.layers)

        # hide property check
        if prevm_obj.hide != locator.hide:
            prevm_obj.hide = locator.hide


def _get_model_mesh(locator, prem_name):
    """Creates and returns new object if mesh already exists in Blender data block

    :return: object if mesh exists; None otherwise
    :rtype: None | bpy.types.Object
    """
    for mesh in bpy.data.meshes:
        if mesh.scs_props.locator_preview_model_path == locator.scs_props.locator_preview_model_path:
            obj = bpy.data.objects.new(name=prem_name, object_data=mesh)
            return obj

    return None
