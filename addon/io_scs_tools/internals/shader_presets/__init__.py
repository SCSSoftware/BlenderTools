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

# Copyright (C) 2017: SCS Software


from io_scs_tools.internals.shader_presets.cache import ShaderPresetsCache
from io_scs_tools.internals.shader_presets.ui_shader_preset_item import UIShaderPresetItem

__cache = ShaderPresetsCache()
__ui_inventory = {}  # shader presets inventory saving preset items for usage in UI and flavor parsing
""":type:dict[str,UIShaderPresetItem]"""

__effects_to_indices_map = {}
__names_to_indices_map = {}
__indices_to_names_map = {}


def is_library_initialized(path):
    """Tells if shader presets library is already initialized for given shader presets path.

    :param path: shader presets file path
    :type path: str
    :return: True if initialized; False for the cases that file doesn't exists or last modified time hasn't changed
    :rtype: bool
    """
    return __cache.is_initialized(path)


def set_library_initialized(path):
    """Sets shader presets library initilized for given shader presets path.

    :param path: shader presets file path
    :type path: str
    """
    __cache.set_initialized(path)


def clear():
    """Clears shader presets library.
    """

    __cache.clear()

    __effects_to_indices_map.clear()
    __names_to_indices_map.clear()
    __indices_to_names_map.clear()


def add_section(base_effect, preset_name, flavors_str, section, is_dirty=False):
    """Adds section for given preset name and it's effect to the library.

    :param base_effect: effect string of current preset without any flavors
    :type base_effect: str
    :param preset_name: name of the shader preset
    :type preset_name: str
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :param section: Shader section that should be stored
    :type section: io_scs_tools.internals.structure.SectionData
    :param is_dirty: mark this section as dirty, set to true when inserting section only for time beeing of cache creation
    :type is_dirty: bool
    """

    # save only pure preset sections into mapping system
    if flavors_str == "":

        shader_index = len(__names_to_indices_map) + 1

        # as there can be more presets with same base effect we have to store indices in list
        if base_effect not in __effects_to_indices_map:
            __effects_to_indices_map[base_effect] = []

        __effects_to_indices_map[base_effect].append(shader_index)

        __names_to_indices_map[preset_name] = shader_index
        __indices_to_names_map[shader_index] = preset_name

        __ui_inventory[preset_name] = UIShaderPresetItem(base_effect, preset_name)

    __cache.add_section(__names_to_indices_map[preset_name], flavors_str, section, is_dirty=is_dirty)


def get_section(preset_name, flavors_str=""):
    """Get section from shader presets library for given inventory item and flavor string

    :param preset_name: name of the shader preset
    :type preset_name: str
    :param flavors_str: flavors part of effect name
    :type flavors_str: str
    :return: stored section data for given inventory item and flavor string
    :rtype: io_scs_tools.internals.structure.SectionData
    """
    return __cache.get_section(__names_to_indices_map[preset_name], flavors_str=flavors_str)


def find_sections(base_effect, flavors_str):
    """Gets all sections for given base effect that are stored in the library.

    :param flavors_str: flavors string for given base effect
    :type flavors_str: str
    :param base_effect: base effect name for which presets should be returned
    :type base_effect: str
    :return: list of found sections if any; otherwise empty list
    :rtype: list[io_scs_tools.internals.structure.SectionData]
    """

    if base_effect not in __effects_to_indices_map:
        return []

    found_sections = []
    for preset_idx in __effects_to_indices_map[base_effect]:

        # Normally we should use local has_section and get_section functions,
        # but as we already have preset index, we can access cache directly,
        # it will save some time because of smaller call stack
        if __cache.has_section(preset_idx, flavors_str):
            found_sections.append(__cache.get_section(preset_idx, flavors_str))

    return found_sections


def has_preset(preset_name):
    """Tells if shader preset with given name exists in the library.

    :param preset_name: name of the preset
    :type preset_name: str
    :return: True if preset exists; False otherwise
    :rtype: bool
    """
    return preset_name in __names_to_indices_map


def has_effect(base_effect):
    """Tells if there is any existing preset inside shader presets library with given base effect.

    :param base_effect: effect string which are we searching
    :type base_effect: str
    :return: True if any shader presets for given base effect exists; False otherwise
    :rtype: bool
    """
    return base_effect in __effects_to_indices_map


def has_section(preset_name, flavors_str=""):
    """Tells if shader presets library holds shader presets data section for given preset name and correpsonding flavor string suffix.

    :param preset_name: name of the preset
    :type preset_name: str
    :param flavors_str: combined flavors postfix for which section should be searched for
    :type flavors_str: str
    :return: True if data section for given preset nam and flavor string exists; False otherwise
    :rtype: bool
    """
    if preset_name not in __names_to_indices_map:
        return False

    return __cache.has_section(__names_to_indices_map[preset_name], flavors_str=flavors_str)


def get_preset_names(sort=False):
    """Gets avaliable presets from the library as a list of their names.

    :param sort: should list be ordered alphabetically?
    :type sort: bool
    :return: list of strings representing names of avaliable presets in the library
    :rtype: list[str]
    """
    if sort:
        return sorted(__names_to_indices_map)
    else:
        return __names_to_indices_map


def get_preset_index(preset_name, default=0):
    """Gets index of given preset inside shader presets library.

    :param preset_name: name of the preset
    :type preset_name: str
    :param default: default index returned when preset name does not exists in library
    :type default: int
    :return: index of shader preset inside the library; if not found default index is returned
    :rtype: int
    """
    if preset_name not in __names_to_indices_map:
        return default

    return __names_to_indices_map[preset_name]


def get_preset_name(index):
    """Gets preset name for given preset index inside shader presets libraray.

    NOTE: Assert when preset index is not found!

    :param index: index of the preset inside library
    :type index: int
    :return: name of shader preset inside the library
    :rtype: str
    """
    assert index in __indices_to_names_map

    return __indices_to_names_map[index]


def get_preset(preset_name):
    """Get UI shader preset item for given preset name.

    :param preset_name: name of the preset
    :type preset_name: str
    :return: object holding UI shader preset item
    :rtype: io_scs_tools.internals.shader_presets.ui_shader_preset_item.UIShaderPresetItem | None
    """
    if preset_name not in __ui_inventory:
        return None

    return __ui_inventory[preset_name]


def add_flavor(preset_name):
    """Adds new flavor item to UI shader preset object.

    NOTE: Assert when preset name is not found!

    :param preset_name: name of the preset, where new flavor should be added
    :type preset_name: str
    """
    assert preset_name in __ui_inventory

    __ui_inventory[preset_name].append_flavor()


def add_flavor_variant(preset_name, flavor_variant_effect_suffix):
    """Adds new variant of the flavor to the last added flavor inside UI shader preset object with given name.

    :param preset_name: name of the preset, where flavor variant should be added
    :type preset_name: str
    :param flavor_variant_effect_suffix:
    :type flavor_variant_effect_suffix:
    """
    assert preset_name in __ui_inventory

    __ui_inventory[preset_name].append_flavor_variant(flavor_variant_effect_suffix)
