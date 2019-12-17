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

from collections import OrderedDict
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class Material:
    __index = -1
    __alias = ""
    __effect = ""

    __global_material_counter = 0

    @staticmethod
    def reset_counter():
        Material.__global_material_counter = 0

    @staticmethod
    def get_global_material_count():
        return Material.__global_material_counter

    def __init__(self, index, alias, effect, blend_mat):
        """Constructs material for PIM.
        :param index: index of material in pim file
        :type index: int
        :param alias: name of the material in pim file
        :type alias: str
        :param effect: effect name of current material
        :type effect: str
        """
        self.__index = index
        self.__alias = alias
        self.__effect = effect

        self.__nmap_uv_layer_name = None  # saving uv layer name on which normal maps are used
        self.__used_textures_count = 0  # counter indicating number of used textures
        self.__used_textures_without_uv_count = 0  # counter indicating number of used textures which don't require uv layer

        # map uv layer names to corresponding "tex_coord_x" field
        tex_coord_map = {}
        if blend_mat and "scs_shader_attributes" in blend_mat and "textures" in blend_mat["scs_shader_attributes"]:
            for tex_entry in blend_mat["scs_shader_attributes"]["textures"].values():
                self.__used_textures_count += 1
                if "Tag" in tex_entry:
                    tex_type = tex_entry["Tag"].split(":")[1][8:].strip()
                    mappings = getattr(blend_mat.scs_props, "shader_texture_" + tex_type + "_uv")

                    # if imported just use custom mappings defined separetly
                    if blend_mat.scs_props.active_shader_preset_name == "<imported>":

                        custom_tex_coord_maps = blend_mat.scs_props.custom_tex_coord_maps
                        for custom_tex_coord_map in custom_tex_coord_maps:

                            if custom_tex_coord_map.value != "":

                                tex_coord = int(custom_tex_coord_map.name[10:])  # index of custom tex coord field is saved in name as "tex_coord_0"
                                tex_coord_map[tex_coord] = custom_tex_coord_map.value

                            if tex_type == "nmap" and not self.__nmap_uv_layer_name:
                                # try to extract uv field for normal maps from it's mapping
                                # otherwise use first defined mapping in custom mappings
                                if len(mappings) > 0 and mappings[0].value != "":
                                    self.__nmap_uv_layer_name = mappings[0].value
                                else:
                                    self.__nmap_uv_layer_name = custom_tex_coord_map.value
                                lprint("D Normal map layer for material '%s' set to: %s", (blend_mat.name, self.__nmap_uv_layer_name))
                    else:

                        for uv_map_i, uv_map in enumerate(mappings):
                            if uv_map.value != "":  # filter out none specified mappings

                                tex_coord_map[uv_map.tex_coord] = uv_map.value

                                if tex_type == "nmap" and uv_map_i == 0:  # if normal map texture has more tex_coord fields use first
                                    self.__nmap_uv_layer_name = uv_map.value

                            elif uv_map.tex_coord != -1:  # if tex coord is -1 texture doesn't use uvs
                                lprint("W Texture type '%s' on material '%s' is missing UV mapping value, expect problems in game!",
                                       (tex_type, blend_mat.name))

                        else:   # if texture doesn't have mappings it means uv is not required for it

                            self.__used_textures_without_uv_count += 1

        # create uv layer map with used tex_coord on it (this tex_coords now represents aliases for given uv layers)
        # It also uses ordered dictionary because order of keys now defines actually physical order for uvs in PIM file
        self.__uvs_map_by_name = OrderedDict()
        for tex_coord in sorted(tex_coord_map.keys()):
            uv_lay_name = tex_coord_map[tex_coord]

            if uv_lay_name not in self.__uvs_map_by_name:
                self.__uvs_map_by_name[uv_lay_name] = []

            self.__uvs_map_by_name[uv_lay_name].append(tex_coord)

        Material.__global_material_counter += 1

    def uses_textures_with_uv(self):
        """Tells if material is using any textures with required uv layers or not.
        :return: True if material has textures; False otherwise
        :rtype: bool
        """
        return (self.__used_textures_count - self.__used_textures_without_uv_count) > 0

    def get_nmap_uv_name(self):
        """Returns name of the uv layer on which normal maps are used.
        :return: name of the uv layer used for normal maps; None if material doesn't uses normal maps
        :rtype: str | None
        """
        return self.__nmap_uv_layer_name

    def get_tex_coord_map(self):
        """Gets the mapping dictionary which keys are physical uv layer names (ordered) and
        values are list of tex_coord integer aliases for this physical uv layer.
        EXAMPLE: { "UVMap0" : [ 0, 2 ], "UVMap1" : [ 1 ]}

        :return: dictionary of aliases which belongs to physical layer names (keys of dictionary)
        :rtype: collections.OrderedDict
        """
        return self.__uvs_map_by_name

    def get_index(self):
        """Gets index of material
        :return: index of material within PIM file
        :rtype: int
        """
        return self.__index

    def get_as_section(self):
        """Gets material represented with SectionData structure class.
        :return: packed material as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Material")
        section.props.append(("Index", self.__index))
        section.props.append(("Alias", self.__alias))
        section.props.append(("Effect", self.__effect))

        return section
