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

__cache_dict = {}  # storing all combinations of shader presets and it's flavors


def clear():
    """Clears shader presets cache.
    """

    for key in __cache_dict:
        for key1 in __cache_dict[key]:
            __cache_dict[key][key1].clear()
        __cache_dict[key].clear()

    __cache_dict.clear()


def add_section(inventory_item, flavors_str, section):
    """Adds section for current shader presets inventory item to the cache.

    :param inventory_item: shader presets item for which given section should be stored
    :type inventory_item: io_scs_tools.properties.world.ShaderPresetsInventoryItem
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :param section: Shader section that should be stored
    :type section: io_scs_tools.internals.structure.SectionData
    :return:
    :rtype:
    """

    if inventory_item.effect not in __cache_dict:
        __cache_dict[inventory_item.effect] = {}

    if inventory_item.name not in __cache_dict[inventory_item.effect]:
        __cache_dict[inventory_item.effect][inventory_item.name] = {}

    __cache_dict[inventory_item.effect][inventory_item.name][flavors_str] = pickle.dumps(section)


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
