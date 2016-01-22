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

from io_scs_tools.utils.printout import lprint


def remove_items_by_id(inventory, index):
    """Removes item from inventory (if given index is within inventory range)

    :param inventory:  Blender collection property instance
    :type inventory: bpy.types.CollectionProperty
    :param index: id which should be removed from inventory
    :type index: int
    :return: True if item was removed; False otherwise;
    :rtype: bool
    """
    if index < len(inventory):
        inventory.remove(index)
        return True

    return False


def remove_items_by_name(inventory, name_list):
    """Removes all given items from the inventory by their name (if they are present).

    :param inventory:  Blender collection property instance
    :type inventory: bpy.types.CollectionProperty
    :param name_list: list of names which should be removed from inventory
    :type name_list: list of str
    """
    for part_name in name_list:
        for rec_i, rec in enumerate(inventory):
            if rec.name == part_name:
                inventory.remove(rec_i)
                break


def has_item(inventory, item_name):
    """Returns True if provided name is already in inventory, otherwise False."""
    result = False
    for item in inventory:
        if item.name == item_name:
            result = True
            break
    return result


def get_index(inventory, item_name):
    """Gets the index of item in inventory

    :param inventory:  Blender collection property instance
    :type inventory: bpy.types.CollectionProperty
    :param item_name: name of the item you are searching for
    :type item_name: str
    :return: if item is found it returns index of it; otherwise -1
    :rtype: int
    """
    for i, item in enumerate(inventory):
        if item.name == item_name:
            return i

    return -1


def get_indices(inventory, item_name, starts_with=False):
    """Gets all of the indices of items in inventory

    :param inventory:  Blender collection property instance
    :type inventory: bpy.types.CollectionProperty
    :param item_name: name of the item you are searching for
    :type item_name: str
    :param starts_with: use startswith function for name string comparsion
    :type starts_with: bool
    :return: if on or more items is found it returns list of indices; otherwise empty list
    :rtype: list
    """

    indices = []
    for i, item in enumerate(inventory):
        if starts_with:
            if item.name.startswith(item_name):
                indices.append(i)
        else:
            if item.name == item_name:
                indices.append(i)

    return indices


def add_item(inventory, new_item_name, conditional=True):
    """Adds new item into directory and sets it's name given by new_item_name.

    :param inventory: SCS collection property inventory
    :type inventory: bpy.types.CollectionProperty
    :param new_item_name: desired name of new item in inventory
    :type new_item_name: str
    :param conditional: condition if item should be added even if it already exists
    :type conditional: bool
    :return: new item is returned if added; None otherwise
    :rtype: bpy.types.PropertyGroup
    """

    if conditional and has_item(inventory, new_item_name):
        return None
    else:
        item = inventory.add()
        item.name = new_item_name
        return item


def get_item_name(inventory, data_id, report_errors=False):
    """Takes data Inventory and an item ID and returns item's name.

    NOTE: don't use it on inventories without "item_id" attribute!

    :param inventory: inventory
    :type inventory: bpy.types.PropertyGroup
    :param data_id: ID of the item we are searching for
    :type data_id: str
    :param report_errors: True if errors shall be printed out; False otherwise
    :type report_errors: bool
    """
    result = ""

    for rec in inventory:
        if rec.item_id == data_id:
            result = rec.name
            break
    else:

        if report_errors:

            if len(inventory) > 0:
                inventory_class_name = type(inventory[0]).__name__.replace("Inventory", "")

                lprint("W Entry with ID: %r not found in %r inventory.", (data_id, inventory_class_name))

            else:
                inventory.add()
                inventory_class_name = type(inventory[0]).__name__.replace("Inventory", "")
                inventory.remove(0)

                lprint(str("W Searching %r inventory for entry with ID: %r failed because inventory is empty.\n\t   "
                           "Please check inventory path in SCS Tools Path Settings!"),
                       (inventory_class_name, data_id))

    return result
