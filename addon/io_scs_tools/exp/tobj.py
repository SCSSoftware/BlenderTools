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

from io_scs_tools.utils.printout import lprint


def export(filepath, texture_name, settings):
    """Exports TOBJ with settings.

    :param filepath: absolute file path with name for TOBJ
    :type filepath: str
    :param texture_name: name of texture file
    :type texture_name: str
    :param settings: settings of texture saved in material.scs_props
    :type settings: set
    :return: True if file was written successfully; False otherwise
    """

    try:

        file = open(filepath, "w", encoding="utf8", newline="\n")
        fw = file.write

        # MAP
        fw("map\t2d\t%s\n" % texture_name)

        # ADDR
        if "u_repeat" in settings:
            addr_u = "repeat"
        else:
            addr_u = "clamp_to_edge"

        if "v_repeat" in settings:
            addr_v = "repeat"
        else:
            addr_v = "clamp_to_edge"

        fw("addr\t%s\t%s\n" % (addr_u, addr_v))

        # USAGE
        if "tsnormal" in settings:
            fw("usage\ttsnormal\n")

        # NO MIPS
        if "nomips" in settings:
            fw("nomips\n")

        # NO COMPRESS
        if "nocompress" in settings:
            fw("nocompress\n")

        file.close()

        return True

    except IOError:

        lprint("W Can't write TOBJ file into path:\n\t   %r", (filepath,))

    return False