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
from io_scs_tools.utils.printout import lprint


class PrevModelsCache:
    """Cache for pairs of locators and their preview model names
    """

    _prev_models = {}
    """Dictonary holding cached locator and it's preview model name (entry looks like: (locator_name: prev_model_name))
    """

    def __contains__(self, item):
        """Overriden contains method for querying if given locator name exists in preview models cache

        :param item: querying item
        :type item: str
        :return: True if exists; False otherwise
        :rtype: bool
        """

        return item in self._prev_models

    def get_entry(self, loc_name):
        """Gets name of preview model for given locator name.

        :param loc_name: name of locator
        :type loc_name: str
        :return: name of preview model if exists; otherwise None
        :rtype: None | str
        """

        if self.__contains__(loc_name):
            return self._prev_models[loc_name]
        else:
            return None

    def init(self):
        """Initilize preview models cache to be able to control visibility layers for all the locators with preview models
        """

        for obj in bpy.data.objects:

            # if prefab or model locator
            if obj.type == "EMPTY" and obj.scs_props.empty_object_type == "Locator" and obj.scs_props.locator_type in ("Prefab", "Model"):

                # if preview model present
                if obj.scs_props.locator_preview_model_present:
                    for child in obj.children:

                        # find mesh child objects
                        if child.data and "scs_props" in child.data:

                            # if child object is preview model of locator
                            if child.data.scs_props.locator_preview_model_path == obj.scs_props.locator_preview_model_path:
                                self.add_entry(obj.name, child.name)
                                # every locator can have only one preview model so we can break it
                                break

    def rename_entry(self, old_name, new_name):
        """Rename entry from old name to new one. It first tries to rename locator names as keys,
        but if old name is not in dictionary then it tries to rename actual preview model

        :param old_name: old name of locator/preview model
        :type old_name: str
        :param new_name: new name of locator/preview model
        :type new_name: str
        """

        if self.__contains__(old_name):  # rename entries keys

            if self.__contains__(new_name):  # switch values
                tmp = self._prev_models[new_name]
                self._prev_models[new_name] = self._prev_models[old_name]
                self._prev_models[old_name] = tmp

            else:
                self._prev_models[new_name] = self._prev_models[old_name]
                del self._prev_models[old_name]

        else:  # check if any preview model was renamed

            old_key = new_key = None
            for key in self._prev_models:
                if self._prev_models[key] == old_name:
                    old_key = key
                if self._prev_models[key] == new_name:
                    new_key = key

            if old_key is not None:
                if new_key is not None:  # switch values
                    tmp = self._prev_models[new_key]
                    self._prev_models[new_key] = self._prev_models[old_key]
                    self._prev_models[old_key] = tmp
                else:  # normal preview model rename
                    self._prev_models[old_key] = new_name

    def add_entry(self, locator_name, prem_name):
        """Adds or overwrites entry for locator name with given new preview model name

        :param locator_name: locator name for which we want to cache given preview model
        :type locator_name: str
        :param prem_name: name of preview model to assign to given locator name
        :type prem_name: str
        """

        lprint("D Caching preview model %r to locator %r", (prem_name, locator_name))
        self._prev_models[locator_name] = prem_name

    def delete_entry(self, prem_name):
        """Delete cache entry with given preview model name. It searches for appearance
        of given preview model name end deletes it

        :param prem_name: name of preview model which should be uncached
        :type prem_name: str
        """

        key_to_delete = None

        for key in self._prev_models:
            if self._prev_models[key] == prem_name:
                key_to_delete = key
                break

        if key_to_delete:
            lprint("D Uncaching preview model %r from locator %r", (self._prev_models[key_to_delete], key_to_delete))
            del self._prev_models[key_to_delete]


