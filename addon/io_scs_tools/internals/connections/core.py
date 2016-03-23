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
import hashlib
from collections import OrderedDict
from io_scs_tools.consts import ConnectionsStorage as _CS_consts
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.internals.connections import collector as _collector
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils.printout import lprint

MAIN_DICT = _CS_consts.custom_prop_name
REFS = "refs"
LOCATORS = "locators"
CACHE = "cache"
CONNECTIONS = "connections"
CONNS_TO_RECALC = "conns_to_recalc"

TYPE = "type"
IN = "in"
OUT = "out"
VALID = "valid"
IN_CONNS = "in_conns"
OUT_CONNS = "out_conns"
CONNS = "conns"
COUNT = "count"
ENTRIES = "entries"
DATA = "data"
OBJS_COUNT = "objs_count"


def init(data_block):
    """Initialize property in given Blender data block. If custom property with preset name is already taken
    function will output the warning that it will be overwritten.

    :param data_block: data block where custom property should be saved (currently this should be bpy.data.groups)
    :type data_block: bpy_struct
    """

    if MAIN_DICT in data_block:
        lprint("W Custom property on datablock %s will be reset to init value and used for connections storage.", (str(data_block),))
    else:
        lprint("D Just to inform that init was invoked!")

    data_block[MAIN_DICT] = {
        CACHE: {
            LOCATORS: {},
            OBJS_COUNT: 0
        },
        REFS: {
            LOCATORS: {},
            CONNECTIONS: {
                COUNT: 1,
                ENTRIES: {}
            }
        },
        CONNS_TO_RECALC: {}
    }


def exists(data_block):
    """Checks if connections storage is in given Blender data block.

    :param data_block: data block where custom property should be saved (currently this should be bpy.data.groups)
    :type data_block: bpy_struct
    :return: True if connections storage exists; otherwise False
    :rtype: bool
    """

    if MAIN_DICT in data_block:

        data = data_block[MAIN_DICT]

        if CACHE in data and REFS in data and CONNS_TO_RECALC in data:

            refs = data[REFS]

            if LOCATORS in refs and CONNECTIONS in refs:

                connections = refs[CONNECTIONS]

                if COUNT in connections and ENTRIES in connections:

                    cache = data[CACHE]

                    if LOCATORS in cache and OBJS_COUNT in cache:

                        # some kinda data integrity check
                        if len(cache[LOCATORS]) == len(refs[LOCATORS]):

                            if len(cache[LOCATORS]) == 0 or len(cache[LOCATORS].values()[0]) == 6:

                                return True

                    # try to reconstruct cache and entries
                    data[CACHE] = {
                        LOCATORS: {},
                        OBJS_COUNT: len(bpy.data.objects)
                    }

                    for loc_name in refs[LOCATORS].keys():
                        __create_locator_entries__(data_block, bpy.data.objects[loc_name])

                    return True

    return False


def update_for_redraw(data_block, selection):
    """Updates connections data according to change on selected objects. If there is no change data are not changed
    and no recalculation is made

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param selection: list of objects to update connections on; if None current Blender selection is taken as initial list
    :type selection: list of bpy.types.Object | None
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conns_to_recalc = data[CONNS_TO_RECALC]

    # first make cleanup and validation for all connections
    cleanup_check(data_block)

    # create a complete list of objects to recalculate connections
    if selection is None:
        objects_to_check = bpy.context.selected_objects  # this is entry point for selection because only selected objects can be transformed
    else:
        objects_to_check = selection

    final_obj_list = {}
    i = 0
    while i < len(objects_to_check):

        obj = objects_to_check[i]

        # if root is selected all of children should be checked too
        for child_obj in obj.children:

            if len(child_obj.children) > 0:

                objects_to_check.append(child_obj)

            elif child_obj.name in data[CACHE][LOCATORS]:

                final_obj_list[child_obj.name] = child_obj

        if obj.name in data[CACHE][LOCATORS]:

            final_obj_list[obj.name] = obj

        i += 1

    # go trough final selection and mark connection for recalculation
    for loc_obj in final_obj_list.values():

        # check if update of connections is needed
        if __locator_changed__(data_block, loc_obj):

            loc_ref = locators_refs[loc_obj.name]

            if loc_ref[TYPE] == "Navigation Point":
                # mark connections for recalculating
                for conn_key in loc_ref[IN_CONNS]:
                    conns_to_recalc[conn_key] = 1
                for conn_key in loc_ref[OUT_CONNS]:
                    conns_to_recalc[conn_key] = 1
            else:
                for conn_key in loc_ref[CONNS]:
                    conns_to_recalc[conn_key] = 1

    # now that curves are marked for recalculation recalculate them
    for conn_key in conns_to_recalc.keys():

        __recalculate_connection_entry__(data_block, conn_key)

    conns_to_recalc.clear()


def gather_connections_upon_selected(data_block, loc_names):
    """Gets connections of given locators if both locators of connection are members of loc_names dictionary.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_names: dictionary of prefab locator names upon which connections selection is made
    :type loc_names: dict
    :return: dictionary of connection keys which are visible inside given locators dictionary
    :rtype: dict
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conns_entries = data[REFS][CONNECTIONS][ENTRIES]

    conns_to_draw = OrderedDict()  # use ordered one so export with unchanged data will be the same every time
    for loc_name in sorted(loc_names):

        if loc_name in locators_refs:

            loc_ref = locators_refs[loc_name]

            if loc_ref[TYPE] == "Navigation Point":

                for conn_key in loc_ref[OUT_CONNS]:
                    if conns_entries[conn_key][IN] in loc_names:
                        conns_to_draw[conn_key] = 1

                for conn_key in loc_ref[IN_CONNS]:
                    if conns_entries[conn_key][OUT] in loc_names:
                        conns_to_draw[conn_key] = 1

            else:

                for conn_key in loc_ref[CONNS]:
                    if conns_entries[conn_key][OUT] == loc_name:
                        oposite = IN
                    else:
                        oposite = OUT

                    if conns_entries[conn_key][oposite] in loc_names:
                        conns_to_draw[conn_key] = 1

    return conns_to_draw


def get_connection(data_block, loc0_name, loc1_name):
    """Checks if connection exists between given locator names.
    If it does then connection key for connection is returned otherwise None
    NOTE: order of given locator names doesn't matter because
    for "Navigation Point" type in and out connections are checked
    But it returns loc_index indicating which locator is "out" locator

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc0_name: name of first locator
    :type loc0_name: str
    :param loc1_name: name of second locator
    :type loc1_name: str
    :return: None if no connection exists between given locators; otherwise tuple(conn_key, conn_type) or tuple(conn_key, conn_type, loc_index)
    :rtype: None or (str, str, int)
    """

    data = data_block[MAIN_DICT]

    # if one of them is not in data_block there is no connection for sure
    if loc0_name in data[REFS][LOCATORS] and loc1_name in data[REFS][LOCATORS]:

        loc0_ref = data[REFS][LOCATORS][loc0_name]
        loc1_ref = data[REFS][LOCATORS][loc1_name]

        # if they are not the same type connection can not exists
        if loc0_ref[TYPE] == loc1_ref[TYPE]:

            if loc0_ref[TYPE] == "Navigation Point":

                # NOTE: we don't allow directed connections to be made in both directions
                # that's why we need to check all "in" and "out" combinations
                for conn_key in loc0_ref[OUT_CONNS]:
                    if conn_key in loc1_ref[IN_CONNS]:
                        return conn_key, loc0_ref[TYPE], 0
                for conn_key in loc0_ref[IN_CONNS]:
                    if conn_key in loc1_ref[OUT_CONNS]:
                        return conn_key, loc0_ref[TYPE], 1

            elif loc0_ref[TYPE] in ("Map Point", "Trigger Point"):

                for conn_key in loc0_ref[CONNS]:
                    if conn_key in loc1_ref[CONNS]:
                        return conn_key, loc0_ref[TYPE]

    return None


def get_connections(data_block, loc_name):
    """Gets all connections that given locator is member of.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_name: SCS locator name
    :type loc_name: str
    :return: dictionary of connection entries of current locator
    :rtype: dict
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conns_entries = data[REFS][CONNECTIONS][ENTRIES]

    connections = OrderedDict()  # use ordered one so export with unchanged data will be the same every time
    if loc_name in locators_refs:

        loc_refs = locators_refs[loc_name]

        if loc_refs[TYPE] == "Navigation Point":

            for conn_key in loc_refs[IN_CONNS]:
                connections[conn_key] = conns_entries[conn_key]
            for conn_key in loc_refs[OUT_CONNS]:
                connections[conn_key] = conns_entries[conn_key]

        else:

            for conn_key in loc_refs[CONNS]:
                connections[conn_key] = conns_entries[conn_key]

    return connections


def create_connection(data_block, loc0_obj, loc1_obj):
    """Create connection between given SCS locator objects.
    If connection is not created function returns False, cases:
    1. wrong type of locator
    2. types of both locators is not the same
    3. connection is already established
    4. one of locators can not accept more connections
    NOTE: order does matter if given locators are "Navigation Point"
    otherwise it doesn't

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc0_obj: SCS locator object FROM which connection should be established
    :type loc0_obj: bpy.types.Object
    :param loc1_obj: SCS locator object TO which connection should be established
    :type loc1_obj: bpy.types.Object
    :return: True if connection creation is successful otherwise False
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    conn_entries = data[REFS][CONNECTIONS][ENTRIES]
    locators_refs = data[REFS][LOCATORS]

    # check for proper types of both locators
    loc0_type = loc0_obj.scs_props.locator_prefab_type
    loc1_type = loc1_obj.scs_props.locator_prefab_type
    objs_really_locators = loc0_obj.scs_props.empty_object_type == "Locator" and loc1_obj.scs_props.empty_object_type == "Locator"
    objs_really_locators = objs_really_locators and loc0_obj.scs_props.locator_type == "Prefab" and loc1_obj.scs_props.locator_type == "Prefab"
    if objs_really_locators and loc0_type == loc1_type and loc0_type in ("Navigation Point", "Map Point", "Trigger Point"):

        # if connection doesn't exists create it if possible
        if not get_connection(data_block, loc0_obj.name, loc1_obj.name):

            if loc0_type == "Navigation Point":

                # check if both are available (they have at least one more space in proper slot)
                loc0_avaliable = __np_locator_avaliable__(data_block, loc0_obj.name, True)
                loc1_avaliable = __np_locator_avaliable__(data_block, loc1_obj.name, False)
                if loc0_avaliable and loc1_avaliable:

                    # create connection
                    conn_key = __create_connection_entry__(data_block, loc0_obj.name, loc1_obj.name)

                    # create locator entries in CACHE and LOCATORS
                    if __create_locator_entries__(data_block, loc0_obj) and __create_locator_entries__(data_block, loc1_obj):
                        # now add connection to proper slots
                        locators_refs[loc0_obj.name][OUT_CONNS] = __extend_array__(locators_refs[loc0_obj.name][OUT_CONNS], conn_key)
                        locators_refs[loc1_obj.name][IN_CONNS] = __extend_array__(locators_refs[loc1_obj.name][IN_CONNS], conn_key)

                        # as everything went fine connection can now be recalculated
                        __recalculate_connection_entry__(data_block, conn_key)
                        return True
                    else:  # if not successful then delete already created connection
                        del conn_entries[conn_key]
                        return False

            elif loc0_type == "Map Point":

                # check if both are available (they have at least one more space in proper slot)
                loc0_avaliable = __mp_locator_avaliable__(data_block, loc0_obj.name)
                loc1_avaliable = __mp_locator_avaliable__(data_block, loc1_obj.name)
                if loc0_avaliable and loc1_avaliable:

                    # create connection and recalculate it
                    conn_key = __create_connection_entry__(data_block, loc0_obj.name, loc1_obj.name)

                    # create locator entries in CACHE and LOCATORS
                    if __create_locator_entries__(data_block, loc0_obj) and __create_locator_entries__(data_block, loc1_obj):
                        # now add connection to proper slots
                        locators_refs[loc0_obj.name][CONNS] = __extend_array__(locators_refs[loc0_obj.name][CONNS], conn_key)
                        locators_refs[loc1_obj.name][CONNS] = __extend_array__(locators_refs[loc1_obj.name][CONNS], conn_key)

                        # as everything went fine connection can now be recalculated
                        __recalculate_connection_entry__(data_block, conn_key)
                        return True
                    else:  # if not successful then delete already created connection
                        del conn_entries[conn_key]
                        return False

            elif loc0_type == "Trigger Point":

                # check if both are available (they have at least one more space in proper slot)
                (loc0_avaliable, loc0_conns_count) = __tp_locator_avaliable__(data_block, loc0_obj.name)
                (loc1_avaliable, loc1_conns_count) = __tp_locator_avaliable__(data_block, loc1_obj.name)
                if loc0_avaliable and loc1_avaliable:

                    # create connection and recalculate it
                    conn_key = __create_connection_entry__(data_block, loc0_obj.name, loc1_obj.name)

                    # create locator entries in CACHE and LOCATORS
                    if __create_locator_entries__(data_block, loc0_obj) and __create_locator_entries__(data_block, loc1_obj):
                        # now add connection to proper slots
                        locators_refs[loc0_obj.name][CONNS] = __extend_array__(locators_refs[loc0_obj.name][CONNS], conn_key)
                        locators_refs[loc1_obj.name][CONNS] = __extend_array__(locators_refs[loc1_obj.name][CONNS], conn_key)

                        # recalculate all lines because of coloring in case of trigger points
                        all_conn_keys = list(locators_refs[loc0_obj.name][CONNS])
                        all_conn_keys.extend(locators_refs[loc1_obj.name][CONNS])

                        for all_conn_key in all_conn_keys:
                            lprint("D Additional connection recalc requested: %s", (all_conn_key,))
                            __recalculate_connection_entry__(data_block, all_conn_key)

                        return True
                    else:  # if not successful then delete already created connection
                        del conn_entries[conn_key]
                        return False

    return False


def delete_connection(data_block, loc0_name, loc1_name):
    """Deletes connection if it exists and removes references in locators.
    Additionally it removes locators from LOCATORS and CACHE if they don't have any connection left


    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc0_name: name of first locator which should be chechked for connection
    :type loc0_name: str
    :param loc1_name: name of second locator which should be chechked for connection
    :type loc1_name: str
    :return: True if connection was deleted; False otherwise
    :rtype: bool
    """

    conn_data = get_connection(data_block, loc0_name, loc1_name)

    if conn_data:

        locators_refs = data_block[MAIN_DICT][REFS][LOCATORS]
        conn_entries = data_block[MAIN_DICT][REFS][CONNECTIONS][ENTRIES]

        conn_key = conn_data[0]
        conn_type = conn_data[1]

        # remove references to connection from locators
        if conn_type == "Navigation Point":

            out_index = conn_data[2]
            if out_index == 0:  # if first locator is "out" locator
                locators_refs[loc0_name][OUT_CONNS] = __shrink_array__(locators_refs[loc0_name][OUT_CONNS], conn_key)
                locators_refs[loc1_name][IN_CONNS] = __shrink_array__(locators_refs[loc1_name][IN_CONNS], conn_key)
            else:  # if second locator is "out" locator
                locators_refs[loc0_name][IN_CONNS] = __shrink_array__(locators_refs[loc0_name][IN_CONNS], conn_key)
                locators_refs[loc1_name][OUT_CONNS] = __shrink_array__(locators_refs[loc1_name][OUT_CONNS], conn_key)
        else:

            locators_refs[loc0_name][CONNS] = __shrink_array__(locators_refs[loc0_name][CONNS], conn_key)
            locators_refs[loc1_name][CONNS] = __shrink_array__(locators_refs[loc1_name][CONNS], conn_key)

            # additionally recalculate left lines because of coloring in case of trigger points
            if conn_type == "Trigger Point":

                left_conn_keys = list(locators_refs[loc0_name][CONNS])
                left_conn_keys.extend(locators_refs[loc1_name][CONNS])

                for left_conn_key in left_conn_keys:
                    conn_refs = conn_entries[left_conn_key]

                    # if massive delete of locators was done
                    # then it might happen that some objects are not accessible anymore
                    if conn_refs[OUT] in bpy.data.objects and conn_refs[IN] in bpy.data.objects:

                        lprint("D Recalculating connection: %s", (left_conn_key,))
                        __recalculate_connection_entry__(data_block, left_conn_key)

        # delete locators if they are empty
        __delete_locator_if_empty__(data_block, loc0_name)
        __delete_locator_if_empty__(data_block, loc1_name)

        # delete connection
        del data_block[MAIN_DICT][REFS][CONNECTIONS][ENTRIES][conn_key]

        return True

    return False


def rename_locator(data_block, old_name, new_name):
    """Renames locator in connections storage. It also takes care of naming in
    connections references.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param old_name: old locator name
    :type old_name: str
    :param new_name: new locator name
    :type new_name: str
    :return: True if renaming was successfully done; False if new name is already taken
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    locators_cache = data[CACHE][LOCATORS]

    if old_name != new_name:

        # make sure that old name is in cache
        if old_name in locators_cache:

            if new_name not in locators_cache:  # do the normal rename

                __rename_conns_of_locator__(data_block, old_name, new_name)

                # create copy of entries in CACHE and LOCATORS
                locators_refs[new_name] = locators_refs[old_name]
                locators_cache[new_name] = locators_cache[old_name]

                # delete old ones
                del locators_refs[old_name]
                del locators_cache[old_name]

            else:  # switch the names

                __rename_conns_of_locator__(data_block, old_name, new_name)
                __rename_conns_of_locator__(data_block, new_name, old_name)

                tmp = locators_refs.pop(new_name)
                locators_refs[new_name] = locators_refs[old_name]
                locators_refs[old_name] = tmp

                tmp = locators_cache.pop(new_name)
                locators_cache[new_name] = locators_cache[old_name]
                locators_cache[old_name] = tmp

        else:

            return False

    return True


def delete_locator(data_block, loc_name):
    """Deletes locator from connections. It takes care of all references in oposite side
    of connection and remove connection entries which given loc_obj is involved in.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_name: name of locator that should be deleted from connections
    :type loc_name: str
    :return: True if locator and references were successfully deleted; False otherwise
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conn_entries = data[REFS][CONNECTIONS][ENTRIES]

    if loc_name in data[CACHE][LOCATORS]:

        # clear references in opposite side of connection and delete locators if possible
        loc_refs = locators_refs[loc_name]
        if loc_refs[TYPE] == "Navigation Point":

            for conn_key in loc_refs[IN_CONNS]:

                oposite_loc_name = conn_entries[conn_key][OUT]
                locators_refs[oposite_loc_name][OUT_CONNS] = __shrink_array__(locators_refs[oposite_loc_name][OUT_CONNS], conn_key)
                __delete_locator_if_empty__(data_block, oposite_loc_name)

                # delete entry from given locator and connection after references was cleared
                loc_refs[IN_CONNS] = __shrink_array__(loc_refs[IN_CONNS], conn_key)
                del conn_entries[conn_key]

            for conn_key in loc_refs[OUT_CONNS]:

                oposite_loc_name = conn_entries[conn_key][IN]
                locators_refs[oposite_loc_name][IN_CONNS] = __shrink_array__(locators_refs[oposite_loc_name][IN_CONNS], conn_key)
                __delete_locator_if_empty__(data_block, oposite_loc_name)

                # delete entry from given locator and connection after references was cleared
                loc_refs[OUT_CONNS] = __shrink_array__(loc_refs[OUT_CONNS], conn_key)
                del conn_entries[conn_key]

        else:

            for conn_key in loc_refs[CONNS]:

                oposite_loc_name = conn_entries[conn_key][IN]
                if loc_name == oposite_loc_name:  # because of undirected connections we need to check if IN is really opposite
                    oposite_loc_name = conn_entries[conn_key][OUT]

                locators_refs[oposite_loc_name][CONNS] = __shrink_array__(locators_refs[oposite_loc_name][CONNS], conn_key)
                __delete_locator_if_empty__(data_block, oposite_loc_name)

                # delete entry from given locator and connection after references was cleared
                loc_refs[CONNS] = __shrink_array__(loc_refs[CONNS], conn_key)
                del conn_entries[conn_key]

        # delete the given locator object in parameter as last which MUST BE empty.
        # If something went wrong that will reflect in return value
        return __delete_locator_if_empty__(data_block, loc_name)

    else:

        return False


def copy_connections(data_block, old_objs, new_objs):
    """Creates copies of existing connections among old objects to new one.
    NOTE: if length of list will be different or objects won't match by type
    connections won't be copied.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param old_objs: list of old objects from which connections should be taken
    :type old_objs: list of bpy.types.Object
    :param old_objs: list of new objects to which old connections should be copied
    :type old_objs: list of bpy.types.Object
    :return: number of copied connections
    :rtype: int
    """
    new_connections_count = 0

    data = data_block[MAIN_DICT]

    conn_entries = data[REFS][CONNECTIONS][ENTRIES]
    locators_refs = data[REFS][LOCATORS]

    # safety check that length is the same
    if len(old_objs) != len(new_objs):
        return 0

    # filter out only the actual valid locators which has connections
    locator_objs = {}
    for i, old_obj in enumerate(old_objs):

        old_is_conn_loc = old_obj.scs_props.locator_prefab_type in ("Navigation Point", "Map Point", "Trigger Point")
        old_is_conn_loc = old_is_conn_loc and old_obj.scs_props.locator_type == "Prefab"
        old_is_conn_loc = old_is_conn_loc and old_obj.scs_props.empty_object_type == "Locator"
        old_is_conn_loc = old_is_conn_loc and old_obj.type == "EMPTY"

        new_is_conn_loc = new_objs[i].scs_props.locator_prefab_type in ("Navigation Point", "Map Point", "Trigger Point")
        new_is_conn_loc = new_is_conn_loc and new_objs[i].scs_props.locator_type == "Prefab"
        new_is_conn_loc = new_is_conn_loc and new_objs[i].scs_props.empty_object_type == "Locator"
        new_is_conn_loc = new_is_conn_loc and new_objs[i].type == "EMPTY"

        same_prefab_type = new_objs[i].scs_props.locator_prefab_type and old_obj.scs_props.locator_prefab_type

        if old_is_conn_loc and new_is_conn_loc and same_prefab_type:
            locator_objs[old_obj.name] = new_objs[i].name

    # create new connections from all selected old ones
    selected_conns = gather_connections_upon_selected(data_block, locator_objs)  # filter only connections inside
    for conn_key in selected_conns.keys():

        conn_entry = conn_entries[conn_key]

        old_loc0_name = conn_entry[OUT]
        old_loc1_name = conn_entry[IN]

        new_loc0_name = locator_objs[old_loc0_name]
        new_loc1_name = locator_objs[old_loc1_name]

        # prepare new entries of locators if necessary
        for new_loc, old_loc in ((new_loc0_name, old_loc0_name), (new_loc1_name, old_loc1_name)):

            # create new entries in references and cache
            if new_loc not in locators_refs:
                __create_locator_entries__(data_block, bpy.data.objects[new_loc])

        # create new connection entry and recalculate it
        new_conn_key = __create_connection_entry__(data_block, new_loc0_name, new_loc1_name)
        __recalculate_connection_entry__(data_block, new_conn_key)
        new_connections_count += 1

        # add new connection key to both locators
        if locators_refs[new_loc0_name][TYPE] == "Navigation Point":
            locators_refs[new_loc0_name][OUT_CONNS] = __extend_array__(locators_refs[new_loc0_name][OUT_CONNS], new_conn_key)
            locators_refs[new_loc1_name][IN_CONNS] = __extend_array__(locators_refs[new_loc1_name][IN_CONNS], new_conn_key)

        else:
            locators_refs[new_loc0_name][CONNS] = __extend_array__(locators_refs[new_loc0_name][CONNS], new_conn_key)
            locators_refs[new_loc1_name][CONNS] = __extend_array__(locators_refs[new_loc1_name][CONNS], new_conn_key)

    return new_connections_count


def cleanup_check(data_block):
    """Makes cleanup upon the locators which were deleted if any.
    It also clears the connection which are not valid anymore.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    """
    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conn_entries = data[REFS][CONNECTIONS][ENTRIES]

    # make a flag if any of the objects were deleted for preventing
    # of connections removal upon rename
    objects_were_deleted = len(bpy.data.objects) < data[CACHE][OBJS_COUNT]
    data[CACHE][OBJS_COUNT] = len(bpy.data.objects)

    i = j = 0
    for conn_key in conn_entries.keys():

        if conn_key in conn_entries:

            conn_entry = conn_entries[conn_key]

            loc0_name = conn_entry[OUT]
            loc1_name = conn_entry[IN]

            # if removal of locator is detected then make a cleanup for it
            if loc0_name not in bpy.data.objects or loc1_name not in bpy.data.objects:

                if objects_were_deleted:

                    delete_connection(data_block, loc0_name, loc1_name)
                    i += 1

            else:

                obj0 = bpy.data.objects[loc0_name]
                obj1 = bpy.data.objects[loc1_name]

                empty_type_valid = obj0.scs_props.empty_object_type == obj1.scs_props.empty_object_type
                empty_type_valid = empty_type_valid and obj0.scs_props.empty_object_type == "Locator"
                locator_type_valid = obj0.scs_props.locator_type == obj1.scs_props.locator_type
                locator_type_valid = locator_type_valid and obj0.scs_props.locator_type == "Prefab"
                prefab_type_valid = obj0.scs_props.locator_prefab_type == obj1.scs_props.locator_prefab_type

                if not empty_type_valid or not locator_type_valid or not prefab_type_valid:

                    delete_connection(data_block, loc0_name, loc1_name)

                    i += 1

                if loc0_name in locators_refs and locators_refs[loc0_name][TYPE] != obj0.scs_props.locator_prefab_type:
                    delete_locator(data_block, loc0_name)
                    j += 1

                if loc1_name in locators_refs and locators_refs[loc1_name][TYPE] != obj1.scs_props.locator_prefab_type:
                    delete_locator(data_block, loc1_name)
                    j += 1

    if j > 0 or i > 0:
        lprint("D Cleanup directly removed: %s connections and %s cached locators with it's connections.", (str(i), str(j)))


def __rename_conns_of_locator__(data_block, old_name, new_name):
    """Rename connections "in" and "out" ends of given old name locator

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param old_name: old name for locator
    :type old_name: str
    :param new_name: new name for locator
    :type new_name: str
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    conn_entries = data[REFS][CONNECTIONS][ENTRIES]

    loc_refs = locators_refs[old_name]

    # update names in connections
    if loc_refs[TYPE] == "Navigation Point":

        for conn_key in loc_refs[IN_CONNS]:
            conn_entries[conn_key][IN] = new_name

        for conn_key in loc_refs[OUT_CONNS]:
            conn_entries[conn_key][OUT] = new_name
    else:

        for conn_key in loc_refs[CONNS]:

            # because of undirected connection it has to check
            # on which side of connection current locator is
            if conn_entries[conn_key][IN] == old_name:
                conn_entries[conn_key][IN] = new_name
            else:
                conn_entries[conn_key][OUT] = new_name


def __locator_changed__(data_block, loc_obj):
    """Checks if locator object is different from current state in cache.
    In case that is, it returns True and already updates cached locator to current state

    :param loc_obj: Blender object which is locator
    :type loc_obj: bpy.types.Object
    :return: True if object was changed and False if there is no change
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    loc_cached = data[CACHE][LOCATORS][loc_obj.name]

    changed = False

    # in case we will extend caching properties we have to make sure
    # that existing models saved in blend file won't fail because of
    # index out of bounds during access.
    while len(loc_cached) <= 7:
        loc_cached.append("")

    matrix_hash = hashlib.md5(str(loc_obj.matrix_world).encode("utf-8")).hexdigest()
    if matrix_hash != loc_cached[0]:
        loc_cached[0] = matrix_hash
        changed = True

    if loc_obj.scs_props.locator_prefab_np_blinker != loc_cached[1]:
        loc_cached[1] = loc_obj.scs_props.locator_prefab_np_blinker
        changed = True

    if loc_obj.scs_props.locator_prefab_np_allowed_veh != loc_cached[2]:
        loc_cached[2] = loc_obj.scs_props.locator_prefab_np_allowed_veh
        changed = True

    if loc_obj.scs_props.locator_prefab_np_priority_modifier != loc_cached[3]:
        loc_cached[3] = loc_obj.scs_props.locator_prefab_np_priority_modifier
        changed = True

    if loc_obj.scs_props.locator_prefab_mp_custom_color != loc_cached[4]:
        loc_cached[4] = loc_obj.scs_props.locator_prefab_mp_custom_color
        changed = True

    prefab_exit = str(loc_obj.scs_props.locator_prefab_mp_prefab_exit)
    if prefab_exit != loc_cached[5]:
        loc_cached[5] = prefab_exit
        changed = True

    road_size = str(loc_obj.scs_props.locator_prefab_mp_road_size)
    if road_size != loc_cached[6]:
        loc_cached[6] = road_size
        changed = True

    root_hash = hashlib.md5(str(_object_utils.get_scs_root(loc_obj)).encode("utf-8")).hexdigest()
    if root_hash != loc_cached[7]:
        loc_cached[7] = root_hash
        changed = True

    data[CACHE][LOCATORS][loc_obj.name] = loc_cached
    return changed


def __np_locator_avaliable__(data_block, loc_name, out_direction):
    """Check if connection slots for given direction are still
    avaliable on current "Navigation Point" locator.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_name: name of locator
    :type loc_name: str
    :param out_direction: True for locator usage as out connection; False for locator usage as in connection
    :type out_direction: bool
    :return: False if connection slots for given direction are not avaliable anymore; otherwise True
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    if loc_name in data[REFS][LOCATORS]:
        loc_ref = data[REFS][LOCATORS][loc_name]
        if out_direction:
            if len(loc_ref[OUT_CONNS]) < _PL_consts.NAVIGATION_NEXT_PREV_MAX:
                return True
        else:
            if len(loc_ref[IN_CONNS]) < _PL_consts.NAVIGATION_NEXT_PREV_MAX:
                return True
    else:
        return True

    return False


def __mp_locator_avaliable__(data_block, loc_name):
    """Check if connection slots are still avaliable on current "Map Point" locator.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_name: name of locator
    :type loc_name: str
    :return: False if connection slots are not avaliable anymore; otherwise True
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    if loc_name in data[REFS][LOCATORS]:
        loc_ref = data[REFS][LOCATORS][loc_name]
        if len(loc_ref[CONNS]) < _PL_consts.PREFAB_NODE_COUNT_MAX:
            return True
    else:
        return True

    return False


def __tp_locator_avaliable__(data_block, loc_name):
    """Check if connection slots are still avaliable on current "Trigger Point" locator.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_name: name of locator
    :type loc_name: str
    :return: False if connection slots are not avaliable anymore; otherwise True; there is also empty slots count added as integer
    :rtype: tuple(bool, int)
    """

    data = data_block[MAIN_DICT]

    if loc_name in data[REFS][LOCATORS]:
        loc_ref = data[REFS][LOCATORS][loc_name]
        if len(loc_ref[CONNS]) < _PL_consts.TP_NEIGHBOURS_COUNT_MAX:
            return True, len(loc_ref[CONNS])
        else:
            return False, _PL_consts.TP_NEIGHBOURS_COUNT_MAX
    else:
        return True, 0


def __create_connection_entry__(data_block, loc0_name, loc1_name):
    """Creates new connection entry in CONNECTIONS dictionary under references with give locators name.
    First locator name is "out" locator and second locator name is "in" locator of connection.

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc0_name: "out" locator name
    :type loc0_name: str
    :param loc1_name: "in" locator name
    :type loc1_name: str
    :return: connection key under which connection is saved in references
    :rtype: str
    """

    data = data_block[MAIN_DICT]

    conns_dict = data[REFS][CONNECTIONS]

    conns_dict[COUNT] += 1  # increase counter of established connections

    conns_dict[ENTRIES][str(conns_dict[COUNT])] = {
        IN: loc1_name,
        OUT: loc0_name,
        VALID: False,
        DATA: {}
    }

    return str(conns_dict[COUNT])


def __recalculate_connection_entry__(data_block, conn_key):
    """Recalculates connection entry data for given connection key.
    NOTE: if key doesn't exists error stack trace will be printed and script execution cancelled

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param conn_key: connection key for connection which should be recalculated
    :type conn_key: str
    """
    conn_entries = data_block[MAIN_DICT][REFS][CONNECTIONS][ENTRIES]
    locators_refs = data_block[MAIN_DICT][REFS][LOCATORS]

    conn_ref = conn_entries[conn_key]

    loc0_obj = bpy.data.objects[conn_ref[OUT]]
    loc1_obj = bpy.data.objects[conn_ref[IN]]

    conn_type = locators_refs[conn_ref[IN]][TYPE]

    conn_ref[VALID] = _object_utils.get_scs_root(loc0_obj) == _object_utils.get_scs_root(loc1_obj)

    # recalculate curves depending on type
    if conn_type == "Navigation Point":
        conn_ref[DATA] = _collector.collect_nav_curve_data(loc0_obj, loc1_obj)
    elif conn_type == "Map Point":
        conn_ref[DATA] = _collector.collect_map_line_data(loc0_obj, loc1_obj)
    elif conn_type == "Trigger Point":
        (loc0_avaliable, loc0_conns_count) = __tp_locator_avaliable__(data_block, loc0_obj.name)
        (loc1_avaliable, loc1_conns_count) = __tp_locator_avaliable__(data_block, loc1_obj.name)
        conn_ref[DATA] = _collector.collect_trigger_line_data(loc0_obj, loc0_conns_count, loc1_obj, loc1_conns_count)


def __create_locator_entries__(data_block, loc_obj):
    """Creates new entries in LOCATORS and CACHE for given SCS locator object
    If type of given SCS locator object is not right entry is not created

    :param data_block: data block from where data should be read
    :type data_block: bpy_struct
    :param loc_obj: SCS locator object
    :type loc_obj: bpy.types.Object
    :return: True if creation was successfull otherwise False
    :rtype: bool
    """

    data = data_block[MAIN_DICT]

    locators_refs = data[REFS][LOCATORS]
    locators_cache = data[CACHE][LOCATORS]

    loc_type = loc_obj.scs_props.locator_prefab_type
    if loc_type in ("Navigation Point", "Map Point", "Trigger Point"):

        # create LOCATORS and CACHE entry if necessary
        if loc_obj.name not in locators_refs:
            if loc_type == "Navigation Point":
                locators_refs[loc_obj.name] = {
                    TYPE: loc_type,
                    IN_CONNS: [],
                    OUT_CONNS: []
                }

            elif loc_type in ("Map Point", "Trigger Point"):
                locators_refs[loc_obj.name] = {
                    TYPE: loc_type,
                    CONNS: []
                }

        locators_cache[loc_obj.name] = [
            hashlib.md5(str(loc_obj.matrix_world).encode('utf-8')).hexdigest(),
            loc_obj.scs_props.locator_prefab_np_blinker,
            loc_obj.scs_props.locator_prefab_np_allowed_veh,
            loc_obj.scs_props.locator_prefab_np_priority_modifier,
            loc_obj.scs_props.locator_prefab_mp_custom_color,
            str(loc_obj.scs_props.locator_prefab_mp_prefab_exit),
            str(loc_obj.scs_props.locator_prefab_mp_road_size),
            hashlib.md5(str(_object_utils.get_scs_root(loc_obj)).encode('utf-8')).hexdigest()
        ]

        return True

    else:
        return False


def __delete_locator_if_empty__(data_block, loc_name):
    """Delete locator if all of the connections are cleared and return True.
    Otherwise return False

    :param data_block: data block where custom property should be saved (currently this should be bpy.data.groups)
    :type data_block: bpy_struct
    :param loc_name: name of locator that should be deleted
    :type loc_name: str
    :return: True if success; otherwise False
    :rtype: bool
    """

    locators_refs = data_block[MAIN_DICT][REFS][LOCATORS]
    locators_cache = data_block[MAIN_DICT][CACHE][LOCATORS]

    if loc_name in locators_refs:

        loc_refs = locators_refs[loc_name]

        if loc_refs[TYPE] == "Navigation Point":

            if len(loc_refs[IN_CONNS]) == 0 and len(loc_refs[OUT_CONNS]) == 0:
                del locators_refs[loc_name]
                del locators_cache[loc_name]
                return True
        else:

            if len(loc_refs[CONNS]) == 0:
                del locators_refs[loc_name]
                del locators_cache[loc_name]
                return True

    return False


def __extend_array__(data, new_value):
    """Because of assigning empty list to Blender custom properties converts list to some array automaticlly
     we have to take care of list extension.
     NOTE: if there is any element then "data" is saved as list and can be append. If there is no element in
     "data" it will be saved as array and can not be extended


    :param data: object for what we believed it should be list
    :type data: list | IDPropertyArray
    :param new_value: new value to be saved in list (should be string)
    :type new_value: str
    :return: it always returns list with added new value
    :rtype: list of str
    """
    if hasattr(data, "append"):
        data.append(new_value)
        return data
    else:
        conns_list = data.to_list()
        conns_list.append(new_value)
        return conns_list


def __shrink_array__(data, value_to_delete):
    """Because of assigning empty list to Blender custom properties converts list to some array automaticlly
     we have to take care of list shrinking.
     NOTE: if there is any element then "data" is saved as list and can be append. If there is no element in
     "data" it will be saved as array and can not be extended


    :param data: object for what we believed it should be list
    :type data: list | IDPropertyArray
    :param value_to_delete: value which should be deleted from list (should be string)
    :type value_to_delete: str
    :return: it always returns list with added new value
    :rtype: list of str
    """
    if hasattr(data, "remove"):
        data.remove(value_to_delete)
        return data
    else:
        conns_list = data.to_list()
        conns_list.remove(value_to_delete)
        return conns_list
