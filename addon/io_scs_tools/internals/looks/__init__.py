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

# Copyright (C) 2015-2022: SCS Software

from collections.abc import Iterable
from io_scs_tools.consts import Look as _LOOK_consts
from io_scs_tools.utils import property as _property_utils
from io_scs_tools.utils.printout import lprint

_MAIN_DICT = _LOOK_consts.custom_prop_name

_IGNORED_TEXTURE_PROPS = ("_settings", "_locked", "_map_type")
_IGNORED_PROPS = ("mat_id", "enable_aliasing")


def add_look(root_obj, look_id):
    """Creates and adds look with given ID to SCS root object.
    If look is not yet in dictionary it will be added otherwise nothing will be done.
    NOTE: new look collects values from curent material values

    :param root_obj: scs root object on which new look should be added
    :type root_obj: bpy.types.Object
    :param look_id: ID of new look
    :type look_id: int
    """

    if not root_obj:
        return

    # init if not yet done
    if _MAIN_DICT not in root_obj:
        root_obj[_MAIN_DICT] = {}

    look_id_str = str(look_id)
    if look_id_str not in root_obj[_MAIN_DICT]:
        new_look = {}

        for material in __collect_materials__(root_obj):
            mat_id_str = str(material.scs_props.id)
            new_look[mat_id_str] = __create_material_entry__(material)

        root_obj[_MAIN_DICT][look_id_str] = new_look
        lprint("D Look with id %r added to %r", (look_id_str, root_obj.name))


def remove_look(root_obj, look_id):
    """Removes active look from given SCS root object.
    If look does not exists nothing will happen.

    :param root_obj: scs root object from which look should be removed
    :type root_obj: bpy.types.Object
    :param look_id: look id which should be removed
    :type look_id: int
    """

    if not root_obj or _MAIN_DICT not in root_obj:
        return

    look_id_str = str(look_id)
    if look_id_str in root_obj[_MAIN_DICT]:
        del root_obj[_MAIN_DICT][look_id_str]
        lprint("D Look with id %r removed from %r", (look_id_str, root_obj.name))


def apply_active_look(root_obj, force_apply=False):
    """Applies currently active look, which results in updating all "scs_props" of materials
    saved in material entries of active look.
    It will also try to unset any unused properties.

    :param root_obj: scs root object on from which active look should be applied
    :type root_obj: bpy.types.Object
    :param force_apply: optional flag indicating if apply has to be forced even if only one look is defined
    :type force_apply: bool
    """

    if not root_obj or _MAIN_DICT not in root_obj:
        return

    looks_count = len(root_obj.scs_object_look_inventory)
    if not (0 <= root_obj.scs_props.active_scs_look < looks_count) or (looks_count <= 1 and not force_apply):
        return

    look_id_str = str(root_obj.scs_object_look_inventory[root_obj.scs_props.active_scs_look].id)

    if look_id_str not in root_obj[_MAIN_DICT]:
        lprint("D Look entry with ID: %s does not exists in %r", (look_id_str, root_obj.name))
        return

    look_data = root_obj[_MAIN_DICT][look_id_str]
    for material in __collect_materials__(root_obj):
        lprint("D Applying material: %r:", (material.name,))
        mat_id_str = str(material.scs_props.id)

        if mat_id_str not in look_data:
            lprint("D Can't properly apply look! Look entry with ID: %s is missing data for material: %r", (look_id_str, material.name))
            continue

        mat_data = look_data[mat_id_str]
        for prop in mat_data:
            lprint("S |- attr set: %r => %r", (prop, mat_data[prop]))

            different = False  # apply value change and invoke update only if property is different
            if isinstance(mat_data[prop], Iterable) and "CollectionProperty" in mat_data[prop]:
                coll_property = getattr(material.scs_props, prop, None)
                if coll_property:
                    different = True
                    last_entry = None
                    coll_property.clear()
                    for entry in mat_data[prop]["entries"]:
                        new_entry = coll_property.add()
                        for key in entry:
                            new_entry[key] = entry[key]

                        last_entry = new_entry

                    # apply update_value function if exists only on last collection property item
                    # this will update: aux and uv layer items
                    update_func = getattr(last_entry, "update_value", None)
                    if update_func and different:
                        update_func(material)
            else:
                different = (prop not in material.scs_props or material.scs_props[prop] != mat_data[prop])
                if different:
                    material.scs_props[prop] = mat_data[prop]

            update_func = getattr(material.scs_props, "update_" + prop, None)
            # invoke update function on property if exists
            if update_func and different:
                update_func(material)

        # unset any unused
        for prop in list(material.scs_props.keys()):
            valid_prefix = (prop.startswith("shader_attribute") or prop.startswith("shader_texture"))
            is_not_ignored = not ((prop.startswith("shader_texture") and prop.endswith(_IGNORED_TEXTURE_PROPS)) or prop in _IGNORED_PROPS)
            if prop not in mat_data and valid_prefix and is_not_ignored:
                lprint("S |- attr unset: %r", (prop,))
                material.scs_props.property_unset(prop)


def update_look_from_material(root_obj, material, preset_change=False):
    """Updates look entry from given material. If look or material inside look doesn't exists update will fail.
    There is also extra option for preset change, which will overwrite shader type specific properties
    on all looks and remove all unused properties from looks.

    :param root_obj: scs root object on which looks are written
    :type root_obj: bpy.types.Object
    :param material: material to update from
    :type material: bpy.types.Material
    :param preset_change: flag indicating if there was preset change
    :type preset_change: bool
    """

    if not root_obj or not material:
        return

    if _MAIN_DICT not in root_obj or not (0 <= root_obj.scs_props.active_scs_look < len(root_obj.scs_object_look_inventory)):
        return

    look_id_str = str(root_obj.scs_object_look_inventory[root_obj.scs_props.active_scs_look].id)

    if look_id_str not in root_obj[_MAIN_DICT]:
        lprint("D Cant't update look! Look entry with ID: %s does not exists in %r", (look_id_str, root_obj.name))
        return

    look_data = root_obj[_MAIN_DICT][look_id_str]
    mat_id_str = str(material.scs_props.id)
    if mat_id_str not in look_data:
        lprint("D Can't update look! Look entry with ID: %s is missing data for material: %r", (look_id_str, material.name))
        return

    new_mat = __create_material_entry__(material)
    # apply new material entry only if it's not preset change
    # if there is preset change we don't want to overwrite data rather reuse old values
    if not preset_change:
        look_data[mat_id_str] = new_mat

    # cleanup and sync of all looks
    for look_id in root_obj[_MAIN_DICT]:
        if look_id != look_id_str or preset_change:

            # skip desynced material entry in the look
            if mat_id_str not in root_obj[_MAIN_DICT][look_id]:
                lprint("D Can't update material: %r on look entry with ID: %s", (material.name, look_id))
                continue

            curr_mat = root_obj[_MAIN_DICT][look_id][mat_id_str]

            for key in list(curr_mat.keys()):

                if preset_change:  # preset change write through

                    if key in ("active_shader_preset_name", "mat_effect_name") or __is_texture_locked__(material, key):  # overwrite

                        curr_mat[key] = new_mat[key]

                    elif key.startswith("shader_attribute_aux") and key in new_mat:

                        new_mat_key_size = len(new_mat[key]["entries"])
                        curr_mat_key_size = len(curr_mat[key]["entries"])

                        # don't sync if size is the same
                        if new_mat_key_size == curr_mat_key_size:
                            continue

                        # since dynamic update of collection property is not possible we have to create new one
                        coll_prop_entry = {"CollectionProperty": 1, "entries": []}
                        for coll_entry in curr_mat[key]["entries"]:
                            entry = dict(coll_entry)
                            coll_prop_entry["entries"].append(entry)

                        # clip unused values
                        while len(coll_prop_entry["entries"]) > new_mat_key_size:
                            coll_prop_entry["entries"].pop()

                        # add default ones if missing
                        while curr_mat_key_size < new_mat_key_size:
                            entry_copy = dict(new_mat[key]["entries"][curr_mat_key_size])
                            coll_prop_entry["entries"].append(entry_copy)
                            curr_mat_key_size = curr_mat_key_size + 1

                        curr_mat[key] = coll_prop_entry

                    elif key not in new_mat:  # delete if not in newly created material entry

                        del curr_mat[key]

                else:  # general write through

                    overwrite = (key.endswith("_uv"))  # UV mappings, because this property is not look related

                    if overwrite:
                        curr_mat[key] = new_mat[key]

            # additionally add any new properties from current material
            for key in new_mat:
                if key not in curr_mat:
                    curr_mat[key] = new_mat[key]


def write_through(root_obj, material, prop):
    """Writes given property from material to all looks within this SCS game object.

    :param root_obj: scs root object from which looks data will be taken
    :type root_obj: bpy.types.Object
    :param material: material from which property value should be taken
    :type material: bpy.types.Material
    :param prop: property string which should be written through
    :type prop: str
    :return: number of overwritten looks; If something goes wrong -1 is returned
    :rtype: int
    """
    if not root_obj or not material:
        return -1

    if _MAIN_DICT not in root_obj or not hasattr(material.scs_props, prop):
        return -1

    written_looks_count = 0

    mat_id_str = str(material.scs_props.id)
    for look_id in root_obj[_MAIN_DICT]:
        curr_look = root_obj[_MAIN_DICT][look_id]

        if mat_id_str not in curr_look:
            lprint("D Look with ID: %s doesn't have entry for material %r in SCS Root %r,\n\t   " +
                   "property %r won't be updated!",
                   (look_id, material.name, root_obj.name, prop))
            continue
        elif prop not in curr_look[mat_id_str]:
            lprint("D Look with ID: %s is not synced, property %r won't be updated!", (look_id, prop))
            continue

        curr_prop = getattr(material.scs_props, prop)
        curr_prop_type = material.scs_props.bl_rna.properties[prop].bl_rna.identifier
        if "CollectionProperty" in curr_prop_type:

            coll_prop_entry = {"CollectionProperty": 1, "entries": []}

            for coll_entry in curr_prop:
                entry = {}
                for coll_key in coll_entry.keys():
                    entry[coll_key] = getattr(coll_entry, coll_key)

                coll_prop_entry["entries"].append(entry)

            curr_look[mat_id_str][prop] = coll_prop_entry
        else:
            curr_look[mat_id_str][prop] = curr_prop

        written_looks_count += 1

    return written_looks_count


def write_prop_to_look(root_obj, look_id, material, prop):
    """Writes given property from material to given look of given SCS game object.

    :param root_obj: scs root object from which looks data will be taken
    :type root_obj: bpy.types.Object
    :param look_id: look id to which property should be written
    :type look_id: int
    :param material: material from which property value should be taken
    :type material: bpy.types.Material
    :param prop: property string which should be written through
    :type prop: str
    :return: True if property was written successfully; False otherwise
    :rtype: bool
    """
    if not root_obj or not material:
        return False

    if _MAIN_DICT not in root_obj or not hasattr(material.scs_props, prop):
        return False

    mat_id_str = str(material.scs_props.id)

    if str(look_id) not in root_obj[_MAIN_DICT]:
        lprint("D SCS Root: %r doesn't have entry for look ID: %s.", (root_obj.name, look_id))
        return False

    look_entry = root_obj[_MAIN_DICT][str(look_id)]
    if mat_id_str not in look_entry:
        lprint("D Look with ID: %s doesn't have entry for material %r in SCS Root %r,\n\t   " +
               "property %r won't be updated!",
               (look_id, material.name, root_obj.name, prop))
        return False

    if prop not in look_entry[mat_id_str]:
        lprint("D Look with ID: %s is not synced, property %r won't be updated!", (look_id, prop))
        return False

    curr_prop = getattr(material.scs_props, prop)
    curr_prop_type = material.scs_props.bl_rna.properties[prop].bl_rna.identifier
    if "CollectionProperty" in curr_prop_type:

        coll_prop_entry = {"CollectionProperty": 1, "entries": []}

        for coll_entry in curr_prop:
            entry = {}
            for coll_key in coll_entry.keys():
                entry[coll_key] = getattr(coll_entry, coll_key)

            coll_prop_entry["entries"].append(entry)

        look_entry[mat_id_str][prop] = coll_prop_entry
    else:
        look_entry[mat_id_str][prop] = curr_prop

    return True


def add_materials(root_obj, mat_list):
    """Adds material entries to all of the looks in given SCS root object.
    Only none existing materials from given list are added.

    :param root_obj: scs root object on which looks datablock new materials should be added
    :type root_obj: bpy.types.Object
    :param mat_list: list of blender materials that should be added
    :type mat_list: iter of bpy.types.Material
    """

    if not root_obj or not mat_list:
        return

    if _MAIN_DICT not in root_obj or len(root_obj[_MAIN_DICT]) <= 0:
        return

    first_look_id = next(iter(root_obj[_MAIN_DICT].keys()))
    existing_mats_ids = root_obj[_MAIN_DICT][first_look_id].keys()
    new_mats_added = 0
    for new_mat in mat_list:

        new_mat_id_str = str(new_mat.scs_props.id)

        # add material to looks only if it doesn't yet exists in dictionary
        if new_mat_id_str not in existing_mats_ids:

            # add new entry to all of the looks
            for look_id in root_obj[_MAIN_DICT]:
                root_obj[_MAIN_DICT][look_id][new_mat_id_str] = __create_material_entry__(new_mat)

            new_mats_added += 1

    lprint("D %s/%s (actual/requested) new materials added to looks dictionary in %r", (new_mats_added, len(mat_list), root_obj.name))


def clean_unused(root_obj):
    """Removes all unused material entries from looks dictionary in given SCS root object.

    :param root_obj: scs root object which should be cleaned
    :type root_obj: bpy.types.Object
    """
    if not root_obj:
        return

    if _MAIN_DICT not in root_obj or len(root_obj[_MAIN_DICT]) <= 0:
        return

    # create unused materials id list with removing used materials ids from exisiting
    first_look_id = next(iter(root_obj[_MAIN_DICT].keys()))
    unused_mats_ids = list(root_obj[_MAIN_DICT][first_look_id].keys())
    for mat in __collect_materials__(root_obj):

        mat_id_str = str(mat.scs_props.id)
        if mat_id_str in unused_mats_ids:
            unused_mats_ids.remove(mat_id_str)

    # remove unused material entry from every look
    for unused_mat_id in unused_mats_ids:
        for look_id in root_obj[_MAIN_DICT]:

            look_data = root_obj[_MAIN_DICT][look_id]

            if unused_mat_id in look_data:
                del look_data[unused_mat_id]

    lprint("D %s material entries cleaned from looks dictionary in %r", (len(unused_mats_ids), root_obj.name))


def reassign_material(root_obj, new_mat, old_mat):
    """Re-assign material entries from old material to new material in all of the looks in given SCS root object.

    NOTE: once reassign is triggered old material entry is removed from looks for given root object,
    so it won't be accessible anymore

    :param root_obj: scs root object on which looks datablock new materials should be added
    :type root_obj: bpy.types.Object
    :param new_mat: new material to assign to
    :type new_mat: bpy.types.Material
    :param old_mat: old material to assign from
    :type old_mat: bpy.types.Material
    """

    if not root_obj or not new_mat or not old_mat:
        return

    if _MAIN_DICT not in root_obj or len(root_obj[_MAIN_DICT]) <= 0:
        return

    first_look_id = next(iter(root_obj[_MAIN_DICT].keys()))
    existing_mats_ids = root_obj[_MAIN_DICT][first_look_id].keys()

    new_mat_id_str = str(new_mat.scs_props.id)
    old_mat_id_str = str(old_mat.scs_props.id)

    # old material not found, nothing to do
    if old_mat_id_str not in existing_mats_ids:
        return

    # add material to looks only if it doesn't yet exists in dictionary
    if new_mat_id_str not in existing_mats_ids:

        # re-assign old entry in all of the looks and remove it
        for look_id in root_obj[_MAIN_DICT]:
            old_mat_entries = root_obj[_MAIN_DICT][look_id][old_mat_id_str]

            root_obj[_MAIN_DICT][look_id][new_mat_id_str] = old_mat_entries
            del root_obj[_MAIN_DICT][look_id][old_mat_id_str]


def get_material_entries(root_obj, material):
    """Get material entries from all looks for given material on given root object.

    :param root_obj: scs root object on which looks datablock should be read from
    :type root_obj: bpy.types.Object
    :param material: blender material for which material entries should be gathered
    :type material: bpy.type.Material
    :return:
    :rtype:
    """
    if not root_obj or not material:
        return {}

    if _MAIN_DICT not in root_obj or len(root_obj[_MAIN_DICT]) <= 0:
        return {}

    first_look_id = next(iter(root_obj[_MAIN_DICT].keys()))
    existing_mats_ids = root_obj[_MAIN_DICT][first_look_id].keys()

    mat_id_str = str(material.scs_props.id)

    # material not found, nothing to do
    if mat_id_str not in existing_mats_ids:
        return {}

    material_entries = {}
    for look_id in root_obj[_MAIN_DICT]:
        mat_entries = {}

        # construct material look entries as native python objects so we can compare for equality
        for prop_name, prop_value in root_obj[_MAIN_DICT][look_id][mat_id_str].items():
            mat_entries[prop_name] = _property_utils.get_id_prop_as_py_object(prop_value)

        material_entries[look_id] = mat_entries

    return material_entries


def __collect_materials__(root_obj):
    """Collect all materials on given SCS root object.

    :param root_obj: scs root object on which material collection will be executed
    :type root_obj: bpy.types.Object
    :return: list of materials used on objects of given SCS game object
    :rtype: list of bpy.types.Material
    """
    from io_scs_tools.utils import object as _object

    collected_mats = {}

    children = _object.get_children(root_obj)
    for child in children:
        for slot in child.material_slots:
            if slot.material and slot.material.name not in collected_mats:
                collected_mats[slot.material.name] = slot.material

    return collected_mats.values()


def __create_material_entry__(material):
    """Create material entry for looks dictionary from given material.

    :param material: material from which dictionary entry should be created
    :type material: bpy.types.Material
    :return: dictionary of all currently set "scs_props"
    :rtype: dict
    """
    mat_entry = {}
    for key in material.scs_props.keys():

        if (key.startswith("shader_texture_") and key.endswith(_IGNORED_TEXTURE_PROPS)) or key in _IGNORED_PROPS:
            lprint("S Ignoring property in create material entry: %r", (key,))
            continue

        curr_prop = getattr(material.scs_props, key, "INVALID")

        if curr_prop != "INVALID":

            curr_prop_type = material.scs_props.bl_rna.properties[key].bl_rna.identifier
            if "CollectionProperty" in curr_prop_type:

                coll_prop_entry = {"CollectionProperty": 1, "entries": []}

                for coll_entry in curr_prop:
                    entry = {}
                    for coll_key in coll_entry.keys():
                        entry[coll_key] = getattr(coll_entry, coll_key)

                    coll_prop_entry["entries"].append(entry)

                mat_entry[key] = coll_prop_entry
            else:
                mat_entry[key] = curr_prop

        else:
            lprint("D Create material entry requested invalid property: %r", (key,))

    return mat_entry


def __is_texture_locked__(material, any_key):
    """Tries to extract texture type out of given key.
    If extraction is successfull then it returns locked state of extracted texture.

    :param material: material in which we are looking for locked texture
    :type material: bpy.types.Material
    :param any_key: any key from scs_props properties
    :type any_key: str
    :return: True if texture is locked; False if extraction from key is not possible or texture isn't locked
    :rtype: bool
    """

    if any_key.startswith("shader_texture_"):
        tex_type = any_key[len("shader_texture_"):]
        end = tex_type.find("_")
        if end > 0:
            tex_type = tex_type[:end]
        return getattr(material.scs_props, "shader_texture_" + tex_type + "_locked", False)

    return False
