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

from io_scs_tools.internals.containers.tobj import TobjContainer as _TobjContainer


def get_settings_and_type(filepath, as_set=False):
    """Loads TOBJ and gets setting and map type out of it.
    Settings should be used in "scs_props.shader_texture_XXX_settings" on material.
    Map type can be used to for identifying of visiblity of settings in UI

    NOTE: settings are read only if map type is "2d" for any other map types defaults are returened

    :param filepath: tobj filepath
    :type filepath: str
    :param as_set: optional flag indicating type of result
    :type as_set: bool
    :return: if as_set returns set and map type; otherwise binary representation of settings and map type is returned
    :rtype: tuple[string, str] | tuple[set, str]
    """
    addr = "00"
    tsnormal = "0"

    container = _TobjContainer.read_data_from_file(filepath)

    if container and container.map_type == "2d":

        addr = ""
        for addr_value in container.addr:
            if addr_value == "clamp_to_edge":
                addr += "0"
            elif addr_value == "repeat":
                addr += "1"
            else:
                # NOTE: there are also other options for addr like: mirror etc.
                # But artists are not encouraged to really used them, so use default: "clamp_to_edge".
                addr += "0"

        addr = addr[::-1]

        if container.usage == "tsnormal":
            tsnormal = "1"

    # if container is still empty create default one so map type can be returned
    if not container:
        container = _TobjContainer()

    # return result as set
    if as_set:
        return __get_as_set(addr, tsnormal), container.map_type

    return tsnormal + addr, container.map_type


def __get_as_set(addr, tsnormal):
    set_list = []

    if addr[0] == "1":
        set_list.append("u_repeat")
    if addr[1] == "1":
        set_list.append("v_repeat")

    if tsnormal == "1":
        set_list.append("tsnormal")

    return set(set_list)
