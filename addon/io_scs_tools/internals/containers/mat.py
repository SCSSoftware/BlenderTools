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

import os
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.containers.parsers import mat as _mat


class MatContainer:
    def __init__(self, data_dict, effect):
        """Create MAT file container with mapped data dictionary on attributes and textures.
        It also stores material effect name.

        :param data_dict: all attributes from material represented with dictionary,
        where key is the name of attribute and value is value of attribute
        :type data_dict: dict[str, object]
        :param effect: shader effect full name
        :type effect: str
        """

        self.__effect = ""
        self.__attributes = {}
        self.__textures = {}

        if effect is not None:
            self.__effect = effect

        for key in data_dict.keys():

            if key.startswith("texture"):

                tex_type = "texture_name"
                tex_val = "texture"

                # take care of texture saved as arrays eg: texture[0]
                if key.find("[") != -1:

                    tex_type = "texture_name" + key[key.find("["):]
                    tex_val = "texture" + key[key.find("["):]

                self.__textures[data_dict[tex_type]] = data_dict[tex_val]

            else:

                self.__attributes[key.replace("[", "").replace("]", "")] = data_dict[key]

    def get_textures(self):
        """Returns shader textures defined in MAT container.

        :rtype: dict[str, tuple]
        """
        return self.__textures

    def get_attributes(self):
        """Returns shader attributes defined in MAT container.

        :rtype: dict[str, tuple]
        """
        return self.__attributes

    def get_effect(self):
        """Returns effect name defined in MAT container.

        :rtype: str
        """
        return self.__effect


def get_data_from_file(filepath):
    """Returns entire data in data container from specified raw material file.

    :rtype: MatContainer | None
    """

    container = None
    if filepath:
        if os.path.isfile(filepath) and filepath.lower().endswith(".mat"):

            data_dict, effect = _mat.read_data(filepath)

            if data_dict:
                if len(data_dict) < 1:
                    lprint('\nI MAT file "%s" is empty!', (str(filepath).replace("\\", "/"),))
                    return None

                container = MatContainer(data_dict, effect)
            else:
                lprint('\nI MAT file "%s" is empty!', (str(filepath).replace("\\", "/"),))
                return None
        else:
            lprint('\nW Invalid MAT file path %r!', (str(filepath).replace("\\", "/"),))
    else:
        lprint('\nI No MAT file path provided!')

    return container
