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

import re
from io_scs_tools.utils.printout import lprint


def get_settings(filepath, as_set=False):
    """Loads TOBJ and gets setting out of it. Which should be used in "scs_props.shader_texture_XXX_settings"
    on material.

    :param filepath: tobj filepath
    :type filepath: str
    :param as_set: optional flag indicating type of result
    :type as_set: bool
    :return: if as_set param is set it returns set; otherwise binary representation is returned
    :rtype: string | set
    """
    addr = "00"
    tsnormal = "0"
    nomips = "0"
    nocompress = "0"

    for i, line in enumerate(__get_lines__(filepath)):
        i += 1  # increase line for 1 to get actual line number
        (prop, data) = __parse_line__(line)

        if prop == "map":

            continue

        elif prop == "bias":  # IGNORE: not implemented in SCS Blender Tools yet

            continue

        elif prop == "addr":

            if len(data) != 2:
                lprint("W Malformed \"addr\" in line:%s. TOBJ file:\n\t   %r!", (i, filepath))
                continue

            addr = ""
            for val_i, value in enumerate(data):
                if value == "clamp_to_edge":
                    addr += "0"
                elif value == "repeat":
                    addr += "1"
                else:
                    addr += "0"
                    lprint("W Malformed \"addr\" data in line:%s. Expected \"repeat\" or \"clamp_to_edge\""
                           "got %r instead. TOBJ file:\n\t   %r!", (i, value, filepath))

            addr = addr[::-1]

        elif prop == "usage":

            if len(data) != 1:
                lprint("W Malformed \"usage\" in line:%s. TOBJ file:\n\t   %r!", (i, filepath))
                continue

            if data[0] == "tsnormal":
                tsnormal = "1"
            else:
                lprint("W Unknown \"usage\" data in line:%s. TOBJ file:\n\t   %r", (i, filepath))

        elif prop == "nomips":

            if len(data) != 0:
                lprint("W Malformed \"nomips\" in line:%s. TOBJ file:\n\t   %r!", (i, filepath))
                continue

            nomips = "1"

        elif prop == "nocompress":

            if len(data) != 0:
                lprint("W Malformed \"nocompress\" in line:%s. TOBJ file:\n\t   %r!", (i, filepath))
                continue

            nocompress = "1"

        else:

            lprint("W Unknown property %r in line:%s. TOBJ file:\n\t   %r", (prop, i, filepath))

    # return result as set
    if as_set:
        return __get_as_set(addr, tsnormal, nomips, nocompress)

    return nocompress + nomips + tsnormal + addr


def __get_as_set(addr, tsnormal, nomips, nocompress):
    set_list = []

    if addr[0] == "1":
        set_list.append("u_repeat")
    if addr[1] == "1":
        set_list.append("v_repeat")

    if tsnormal == "1":
        set_list.append("tsnormal")

    if nomips == "1":
        set_list.append("nomips")

    if nocompress == "1":
        set_list.append("nocompress")

    return set(set_list)


def __parse_line__(line):
    vals = re.sub(r"\s+", "\t", line.strip()).split("\t")
    return vals[0], vals[1:]


def __get_lines__(filepath):
    with open(filepath) as f:
        lines = f.readlines()

        f.close()

    return lines