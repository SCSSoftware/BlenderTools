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
from io_scs_tools.consts import ConnectionsStorage as _CS_consts
from io_scs_tools.internals.connections import core as _core
from io_scs_tools.internals.open_gl import primitive as _gl_primitive
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint as lprint

_GROUP_NAME = _CS_consts.group_name
_DATA_UP_TO_DATE = "up_to_date"
_CACHE = {_DATA_UP_TO_DATE: False}  # saving if connections data are up to date


class ConnEntry:
    def __init__(self, index, start, end, next_curves, prev_curves):
        """Constructs data storage class for representing connection data.

        :param index: curve index
        :type index: int
        :param start: start locator name
        :type start: str
        :param end: end locator name
        :type end: str
        :param next_curves: next connections indices
        :type next_curves: list[int]
        :param prev_curves: previous connections indices
        :type prev_curves: list[int]
        """
        self.index = index
        """Index of connection/curve"""
        self.start = start
        """Name of connection start locator"""
        self.end = end
        """Name of connection end locator"""
        self.next_curves = next_curves
        """List of next connections/curves keys in dictionary"""
        self.prev_curves = prev_curves
        """List of previous connections/curves keys in dictionary"""


def init():
    """Initialize storage for saving connections.
    Called if starting Blender or if all connections should be deleted
    """

    # create proper group if needed
    if not _GROUP_NAME in bpy.data.groups:
        bpy.data.groups.new(_GROUP_NAME)

    # just make sure that data block won't get deleted after several savings of blend file
    bpy.data.groups[_GROUP_NAME].use_fake_user = True

    # check if connections data block already exists then don't initilaze it
    if not _core.exists(bpy.data.groups[_GROUP_NAME]):
        _core.init(bpy.data.groups[_GROUP_NAME])


def create_connection(loc0_obj, loc1_obj):
    """Create connection between given SCS locator objects.
    If connection is not created function returns False, cases:
    1. wrong type of locator
    2. types of both locators is not the same
    3. connection is already established
    4. one of locators can not accept more connections
    NOTE: order does matter if given locators are "Navigation Point"
    otherwise it doesn't

    :param loc0_obj: SCS locator object FROM which connection should be established
    :type loc0_obj: bpy.types.Object
    :param loc1_obj: SCS locator object TO which connection should be established
    :type loc1_obj: bpy.types.Object
    :return: True if connection creation is successful otherwise False
    :rtype: bool
    """
    return _core.create_connection(bpy.data.groups[_GROUP_NAME], loc0_obj, loc1_obj)


def delete_connection(loc0_name, loc1_name):
    """Deletes connection if it exists and removes references in locators.

    :param loc0_name: name of first locator which should be chechked for connection
    :type loc0_name: str
    :param loc1_name: name of second locator which should be chechked for connection
    :type loc1_name: str
    :return: True if connection was deleted; False otherwise
    :rtype: bool
    """
    return _core.delete_connection(bpy.data.groups[_GROUP_NAME], loc0_name, loc1_name)


def has_connection(loc0_obj, loc1_obj):
    result = _core.get_connection(bpy.data.groups[_GROUP_NAME], loc0_obj.name, loc1_obj.name)
    return result is not None


def delete_locator(loc_name):
    """Deletes locator from connections. It takes care of all references in oposite side
    of connection and remove connection entries which given loc_obj is involved in.

    :param loc_name: name of locator that should be deleted from connections
    :type loc_name: str
    :return: True if locator and references were successfully deleted; False otherwise
    :rtype: bool
    """
    return _core.delete_locator(bpy.data.groups[_GROUP_NAME], loc_name)


def rename_locator(old_name, new_name):
    """Renames locator in connections storage. It also takes care of naming in
    connections references.

    :param old_name: old locator name
    :type old_name: str
    :param new_name: new locator name
    :type new_name: str
    :return: True if renaming was successfully done; False if new name is already taken
    :rtype: bool
    """
    return _core.rename_locator(bpy.data.groups[_GROUP_NAME], old_name, new_name)


def copy_check(old_objs, new_objs):
    """Try to copy connections for given objects list to new object list.
    Both list needs to be aligned and have same length, otherwise no connection
    will be copied

    :param old_objs: old Blender objects
    :type old_objs: list of bpy.types.Object
    :param new_objs: new Blender objects
    :type new_objs: list of bpy.types.Object
    """

    new_conns_count = _core.copy_connections(bpy.data.groups[_GROUP_NAME], old_objs, new_objs)
    lprint("D Copy connection opearation created: %s new connections", (new_conns_count,))


def cleanup_on_export():
    """Cleanups connections in the case that something was changed without making another
    redraw call to 3D view.
    """
    _core.cleanup_check(bpy.data.groups[_GROUP_NAME])


def get_neighbours(loc_obj):
    """Gets all neigbours of given locator.

    :param loc_obj: SCS locator object for which neighbours should be found
    :type loc_obj: bpy.types.Object
    :return: list of neighbour locator names
    :rtype: list
    """

    conns_entries = _core.get_connections(bpy.data.groups[_GROUP_NAME], loc_obj.name)

    neighbours = []

    if loc_obj.scs_props.locator_prefab_type in ("Map Point", "Trigger Point"):

        for conn_entry in conns_entries.values():

            # check validity of connection; if not valid don't add neighbour
            if conn_entry[_core.VALID]:

                # detect oposite
                if loc_obj.name == conn_entry[_core.IN]:
                    neighbours.append(conn_entry[_core.OUT])
                else:
                    neighbours.append(conn_entry[_core.IN])

    return neighbours


def get_curves(np_locators):
    """Gets all the connections within given Navigation Point locators list.
    If some of locators are not Navigation Point locators they are automaticly ignored

    :param np_locators: list of SCS Navigation Point locator objects
    :type np_locators: list of bpy.types.Object
    :return: dictionary of curves within given locators with given keys structure;
    :rtype: dict[int, ConnEntry]
    """

    connections = bpy.data.groups[_GROUP_NAME][_core.MAIN_DICT][_core.REFS][_core.CONNECTIONS][_core.ENTRIES]
    locators = bpy.data.groups[_GROUP_NAME][_core.MAIN_DICT][_core.REFS][_core.LOCATORS]

    # filter out all Navigation Point locators
    np_locs_names = {}
    for loc in np_locators:
        if loc.scs_props.locator_prefab_type == "Navigation Point":
            np_locs_names[loc.name] = 1

    # gather all the connections of navigation points
    conns_keys_dict = _core.gather_connections_upon_selected(bpy.data.groups[_GROUP_NAME], np_locs_names)

    curves = {}
    i = 0
    for conn_key in conns_keys_dict.keys():

        conn_entry = connections[conn_key]

        # check validity of connection; if not valid don't add to curves
        if conn_entry[_core.VALID]:

            start_node = conn_entry[_core.OUT]
            end_node = conn_entry[_core.IN]

            # find valid next curves keys
            next_curves = []
            for next_conn_key in locators[end_node][_core.OUT_CONNS]:

                next_conn_entry = connections[next_conn_key]
                if next_conn_entry[_core.VALID]:
                    next_curves.append(next_conn_key)

            # find valid previous curves keys
            prev_curves = []
            for prev_conn_key in locators[start_node][_core.IN_CONNS]:

                prev_conn_entry = connections[prev_conn_key]
                if prev_conn_entry[_core.VALID]:
                    prev_curves.append(prev_conn_key)

            curves[conn_key] = ConnEntry(i, start_node, end_node, next_curves, prev_curves)

            i += 1  # increment index of curve only if it was added

    return curves


def force_recalculate(object_list):
    """Forces connection recalculation for given objects.

    :param object_list: list of the objects for which connection update should be triggered
    :type object_list: list of bpy.types.Object
    """
    _core.update_for_redraw(bpy.data.groups[_GROUP_NAME], object_list)


def switch_to_update():
    """Switches state of connections drawing to update which will prevent connections to be drawn.
    NOTE: this will effect drawing only if optimized drawing is switched on
    """
    _CACHE[_DATA_UP_TO_DATE] = False


def switch_to_stall():
    """Switches state of connections drawing to stalling and will trigger check for connections recalculations
    if they are not yet up to date.
    NOTE: this will effect drawing only if optimized drawing is switched on
    """

    # if data was marked as updated
    if not _CACHE[_DATA_UP_TO_DATE]:
        # recalculate curves and lines whos locators were visiblly changed and force redraw
        _core.update_for_redraw(bpy.data.groups[_GROUP_NAME], None)
        bpy.context.scene.unit_settings.system = bpy.context.scene.unit_settings.system

    _CACHE[_DATA_UP_TO_DATE] = True


def _execute_draw(optimized_drawing):
    """Checks if connections should be drawn.

    :param optimized_drawing: optimized connections drawing property from SCS globals
    :type optimized_drawing: bool
    """

    # exclude optimization drawing
    if not optimized_drawing:
        _core.update_for_redraw(bpy.data.groups[_GROUP_NAME], None)
        return True

    return _CACHE[_DATA_UP_TO_DATE]


def draw(visible_loc_names):
    """Draws navigation curves, map lines and trigger lines from given dictionary of
    locator names as keys.

    :param visible_loc_names: dictionary of visible prefab locators names
    :type visible_loc_names: dict
    """

    scs_globals = _get_scs_globals()

    if _execute_draw(scs_globals.optimized_connections_drawing):

        connections = bpy.data.groups[_GROUP_NAME][_core.MAIN_DICT][_core.REFS][_core.CONNECTIONS][_core.ENTRIES]

        # gets visible connections and draw them
        conns_to_draw = _core.gather_connections_upon_selected(bpy.data.groups[_GROUP_NAME], visible_loc_names)
        for conn_key in conns_to_draw.keys():

            conn_entry = connections[conn_key]

            locator_type = bpy.data.objects[conn_entry[_core.IN]].scs_props.locator_prefab_type
            if locator_type == "Navigation Point":
                _gl_primitive.draw_shape_curve(conn_entry[_core.DATA], not conn_entry[_core.VALID], scs_globals)
            else:
                _gl_primitive.draw_shape_line(conn_entry[_core.DATA], not conn_entry[_core.VALID], locator_type == "Map Point", scs_globals)
