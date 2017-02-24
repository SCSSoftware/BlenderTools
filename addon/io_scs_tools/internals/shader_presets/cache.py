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


import pickle
from os.path import getmtime, isfile


class ShaderPresetsCache:
    def __init__(self):
        """Constructor.
        """
        self.__initialized_path = (None, None)
        """Storing last initialized shader presets file path, to avoid multiple initializing of same path."""
        self.__cache = {}
        """Storing all combinations of shader presets and it's flavors."""
        self.__dirty_items = []
        """Storing dirty combinations of shader presets and it's flavors that can be cleared with cleanup function.
           Used for temporarly save sections even the ones that are not supported by the game,
           just to be able to create further flavor combinations.
        """

    def clear(self):
        """Clears shader presets cache.
        """

        for key1 in self.__cache:
            self.__cache[key1].clear()

        self.__cache.clear()
        self.__dirty_items.clear()
        self.__initialized_path = (None, None)

    def cleanup(self):
        """Cleanup dirty sections from cache.
    
        Any sections added with dirty flag, will now be removed from cache. Additional dirty items list is also cleared,
        so if this function is called two times in a row, second time will be for nothing.
        """

        for i, flavor_str in self.__dirty_items:
            del self.__cache[i][flavor_str]

            if len(self.__cache[i].keys()) == 0:
                del self.__cache[i]

        self.__dirty_items.clear()

    def add_section(self, preset_idx, flavors_str, section, is_dirty=False):
        """Adds section for current shader presets inventory item to the cache.
    
        :param preset_idx: index of shader presets item for which should contain section with given flavors combination
        :type preset_idx: int
        :param flavors_str: flavors part of effect name
        :type flavors_str: str
        :param section: Shader section that should be stored
        :type section: io_scs_tools.internals.structure.SectionData
        :param is_dirty: mark this section as dirty, set to true when inserting section only for time beeing of cache creation
        :type is_dirty: bool
        """

        if preset_idx not in self.__cache:
            self.__cache[preset_idx] = {}

        self.__cache[preset_idx][flavors_str] = pickle.dumps(section)

        if is_dirty:
            self.__dirty_items.append((preset_idx, flavors_str))

    def has_section(self, preset_idx, flavors_str):
        """Is shader data section for given inventory item and flavor string existing in shader presets cache?
    
        :param preset_idx: index of shader presets item for which should contain section with given flavors combination
        :type preset_idx: int
        :param flavors_str: flavors part of effect name
        :type flavors_str: str
        :return: True if section exists; otherwise False
        :rtype: bool
        """
        return (
            preset_idx in self.__cache and
            flavors_str in self.__cache[preset_idx]
        )

    def get_section(self, preset_idx, flavors_str=""):
        """Get section from shader presets cache for given inventory item and flavor string

        NOTE: There is no safety check if preset for given index exists.
              So for safety use "has_section" before using this method.
    
        :param preset_idx: index of shader presets item for which should contain section with given flavors combination
        :type preset_idx: int
        :param flavors_str: flavors part of effect name
        :type flavors_str: str
        :return: stored section data for given inventory item and flavor string
        :rtype: io_scs_tools.internals.structure.SectionData
        """
        return pickle.loads(self.__cache[preset_idx][flavors_str])

    def set_initialized(self, path):
        """Cleanup dirty entries and set shader presets cache as initialized for given path.
        Should be called once all possible sections were added to cache for given path.
    
        :param path: path for which this cache was built
        :type path: str
        """

        self.cleanup()

        self.__initialized_path = (path, getmtime(path))

    def is_initialized(self, path):
        """Tells if shader preset cache was initilized for given path.
    
        It also takes in consideration if shader presets file on given path was modified after
        cache was set as initilized.
    
        :param path:
        :type path:
        :return: True if cache was built upon given path; False if cache wasn't set as initilized for given path;
        :rtype: bool
        """
        return (
            self.__initialized_path[0] == path and
            isfile(self.__initialized_path[0]) and
            self.__initialized_path[1] >= getmtime(path)
        )
