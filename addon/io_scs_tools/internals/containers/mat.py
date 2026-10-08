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
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.containers.parsers import mat as _mat


class MatContainer:
    def __init__(self, data_dict, effect, mat_format):
        """Create MAT file container with mapped data dictionary on attributes, textures and tobjs data.
        It also stores material effect name.

        :param data_dict: all attributes from material represented with dictionary,
        where key is the name of attribute and value is value of attribute
        :type data_dict: dict[str, object]
        :param effect: shader effect full name
        :type effect: str
        :param mat_format: material format (material|effect)
        :type mat_format: str
        """

        self.__effect = ""
        self.__mat_format = ""
        self.__attributes = {}
        self.__textures = {}
        self.__tobjs = {}

        if effect is not None:
            self.__effect = effect

        if format is not None:
            self.__mat_format = mat_format

        for key in data_dict.keys():

            if mat_format == "material":

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
                
            elif mat_format == "effect":

                # parse textures & tobjs
                if key == "texture":

                    for tex_type in data_dict[key].keys():
                        tex_val = data_dict[key][tex_type]
                        self.__textures[tex_type] = tex_val["source"]
                        
                        # w_address for 3d cube reflections? not used in blender
                        attr_keys = ["u_address", "v_address"]

                        # initialize empty tobj data
                        tobjs = [None] * len(attr_keys)

                        # technically, i can return true/false if "repeat", but for eventual future use,
                        # it's better to return the actual value for now.
                        for i, attr in enumerate(attr_keys):
                            if "sampler" in tex_val:
                                tobjs[i] = "repeat"

                            elif attr in tex_val:
                                if tex_val[attr].startswith("repeat"):
                                    tobjs[i] = "repeat"
                                elif tex_val[attr].startswith("clamp"):
                                    tobjs[i] = "extend"
                                elif tex_val[attr].startswith("mirror"):
                                    tobjs[i] = "mirror"

                        self.__tobjs[tex_type] = tuple(tobjs)
                
                # parse attributes
                else:

                    self.__attributes[key.replace("[", "").replace("]", "")] = data_dict[key]

            else:
                lprint("E Unsupported MAT format %r!", (mat_format,))

    def get_textures(self):
        """Returns shader textures defined in MAT container.

        :rtype: dict[str, tuple]
        """
        return self.__textures

    def get_tobjs(self):
        """Returns textures tobj data defined in MAT container.

        :rtype: dict[str, tuple]
        """
        return self.__tobjs

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

    def get_format(self):
        """Returns material format defined in MAT container.

        :rtype: str
        """
        return self.__mat_format


def get_data_from_file(filepath):
    """Returns entire data in data container from specified raw material file.

    :rtype: MatContainer | None
    """

    container = None
    if filepath:
        if os.path.isfile(filepath) and filepath.lower().endswith(".mat"):

            data_dict, effect, mat_format = _mat.read_data(filepath)

            if data_dict:
                if len(data_dict) < 1:
                    lprint('\nI MAT file "%s" is empty!', (_path_utils.readable_norm(filepath),))
                    return None

                container = MatContainer(data_dict, effect, mat_format)
            else:
                lprint('\nI MAT file "%s" is empty!', (_path_utils.readable_norm(filepath),))
                return None
        else:
            lprint('\nW Invalid MAT file path %r!', (_path_utils.readable_norm(filepath),))
    else:
        lprint('\nI No MAT file path provided!')

    return container
