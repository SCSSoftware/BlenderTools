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

# Copyright (C) 2015: SCS Software


import pickle
from os.path import getmtime, isfile

__PATH_DICT_KEY = "initialized_filepath"
__cache_presets_path = {}  # storing last initialized shader presets file path, to avoid multiple initializing of same path
__cache_dict = {}  # storing all combinations of shader presets and it's flavors
__dirty_items = []  # storing dirty combinations of shader presets and it's flavors that can be cleared with cleanup function


def clear():
    """Clears shader presets cache.
    """

    for key in __cache_dict:
        for key1 in __cache_dict[key]:
            __cache_dict[key][key1].clear()
        __cache_dict[key].clear()

    __cache_dict.clear()
    __cache_presets_path.clear()
    __dirty_items.clear()


def cleanup():
    """Cleanup dirty sections from cache.

    Any sections added with dirty flag, will now be removed from cache. Additional dirty items list is also cleared,
    so if this function is called two times in a row, second time will be for nothing.
    """

    for effect, item_name, flavor_str in __dirty_items:
        del __cache_dict[effect][item_name][flavor_str]

    __dirty_items.clear()


def add_section(inventory_item, flavors_str, section, is_dirty=False):
    """Adds section for current shader presets inventory item to the cache.

    :param inventory_item: shader presets item for which given section should be stored
    :type inventory_item: io_scs_tools.properties.world.ShaderPresetsInventoryItem
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :param section: Shader section that should be stored
    :type section: io_scs_tools.internals.structure.SectionData
    :param is_dirty: mark this section as dirty, set to true when inserting section only for time beeing of cache creation
    :type is_dirty: bool
    """

    if inventory_item.effect not in __cache_dict:
        __cache_dict[inventory_item.effect] = {}

    if inventory_item.name not in __cache_dict[inventory_item.effect]:
        __cache_dict[inventory_item.effect][inventory_item.name] = {}

    __cache_dict[inventory_item.effect][inventory_item.name][flavors_str] = pickle.dumps(section)

    if is_dirty:
        __dirty_items.append((inventory_item.effect, inventory_item.name, flavors_str))


def has_section(inventory_item, flavors_str):
    """Is shader data section for given inventory item and flavor string existing in shader presets cache?

    :param inventory_item: shader presets item for which should contain section with given flavors combination
    :type inventory_item: io_scs_tools.properties.world.ShaderPresetsInventoryItem
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :return: True if section exists; otherwise False
    :rtype: bool
    """
    return (
        inventory_item.effect in __cache_dict and
        inventory_item.name in __cache_dict[inventory_item.effect] and
        flavors_str in __cache_dict[inventory_item.effect][inventory_item.name]
    )


def get_section(inventory_item, flavors_str):
    """Get section from shader presets cache for given inventory item and flavor string

    :param inventory_item: shader presets item for which given section should be returned
    :type inventory_item: io_scs_tools.properties.world.ShaderPresetsInventoryItem
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :return: stored section data for given inventory item and flavor string
    :rtype: io_scs_tools.internals.structure.SectionData
    """
    return pickle.loads(__cache_dict[inventory_item.effect][inventory_item.name][flavors_str])


def effect_exists(effect_str):
    """Tells if giveen effect exists in cache.

    :param effect_str: shader effect string
    :type effect_str: str
    :return: True if exists; False otherwise
    :rtype: bool
    """
    return effect_str in __cache_dict


def find_sections(base_effect, flavors_str):
    """Gets all sections for given base effect that are stored in cache.

    :param flavors_str: flavors string for given base effect
    :type flavors_str: str
    :param base_effect: base effect name for which presets should be returned
    :type base_effect: str
    :return: list of found sections if any; otherwise empty list
    :rtype: list[io_scs_tools.internals.structure.SectionData]
    """

    found_sections = []
    for stored_preset in __cache_dict[base_effect].values():
        if flavors_str in stored_preset:

            found_sections.append(pickle.loads(stored_preset[flavors_str]))

    return found_sections


def set_initialized(path):
    """Cleanup dirty entries and set shader presets cache as initialized for given path.
    Should be called once all possible sections were added to cache for given path.

    :param path: path for which this cache was built
    :type path: str
    """

    cleanup()

    __cache_presets_path[__PATH_DICT_KEY] = (path, getmtime(path))


def is_initilized(path):
    """Tells if shader preset cache was initilized for given path.

    It also takes in consideration if shader presets file on given path was modified after
    cache was set as initilized.

    :param path:
    :type path:
    :return: True if cache was built upon given path; False if cache wasn't set as initilized for given path;
    :rtype: bool
    """
    return (__PATH_DICT_KEY in __cache_presets_path and
            __cache_presets_path[__PATH_DICT_KEY][0] == path and
            isfile(__cache_presets_path[__PATH_DICT_KEY][0]) and
            __cache_presets_path[__PATH_DICT_KEY][1] >= getmtime(path))
