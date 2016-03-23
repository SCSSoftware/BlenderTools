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

import os
from io_scs_tools.internals.containers.parsers import tobj as _tobj
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint


class TobjContainer:
    MAP_TYPES = ("1d", "2d", "3d", "cube")
    ADDR_TYPES = ("clamp", "clamp_to_edge", "clamp_to_border", "repeat", "mirror", "mirror_clamp", "mirror_clamp_to_edge")
    FILTER_TYPES = ("", "linear", "nearest")
    TARGET_TYPES = ("", "2d", "cube")
    COLOR_SPACE_TYPES = ("", "linear", "srgb")
    USAGE_TYPES = ("", "default", "tsnormal", "ui")

    def __init__(self):
        """Constructs empty TOBJ container.
        """

        self.filepath = ""
        """Absolute filepath of the TOBJ file."""

        self.map_type = ""
        """One value from MAP_TYPES."""
        self.map_names = []
        """List of texture names. Length is defined by map type: 2d -> 2; cube -> 6;"""
        self.addr = []
        """List of up to 3 values from ADDR_TYPES. Length depends on map type.
        """

        self.nomips = False
        """Optional. No value only flag."""
        self.trilinear = False
        """Optional. No value only flag."""
        self.bias = -1
        """Optional. Possible values are integers."""
        self.filter = []
        """Optional. Two values from FILTER_TYPES."""
        self.noanisotropic = False
        """Optional. No value only flag."""
        self.nocompress = False
        """Optional. No value only flag."""
        self.transparent = False
        """Optional. No value only flag."""
        self.target = ""
        """Optional. One value from TARGET_TYPES."""
        self.border_color = []
        """Optional. Possible values are 4 floats."""
        self.black_border = False
        """Optional. No value only flag."""
        self.color_space = ""
        """Optional. One value from COLOR_SPACE_TYPES."""
        self.usage = ""
        """Optional. One value from USAGE_TYPES."""

    def validate(self):
        """Validates content of TOBJ container. If any problem is found, validation is canceled
        and problems reported.

        :return: True if content is valid; False otherwise
        :rtype: bool
        """

        if self.map_type not in self.MAP_TYPES:
            lprint("E Unknown TOBJ map type %r, should be one of: %r.", (self.map_type, self.MAP_TYPES))
            return False

        tex_count = 6 if self.map_type == "cube" else 1  # only cube map has 6 textures
        if len(self.map_names) != tex_count:
            lprint("E Not enough textures referenced %s/%s in TOBJ.", (len(self.map_names), tex_count))
            return False

        for map_name in self.map_names:

            # use None string for invalid map names
            if map_name is None or len(map_name) < 1:
                tex_path = "None"
            elif map_name[0] == "/":
                tex_path = _path_utils.get_abs_path("//" + map_name[1:])
            else:
                tex_path = os.path.join(os.path.split(self.filepath)[0], map_name)

            if not os.path.isfile(tex_path):
                lprint("E Texture %r used in TOBJ doesn't exists.", (tex_path,))
                return False

        addr_count = 3 if self.map_type == "cube" else int(self.map_type[0])
        if len(self.addr) > 0:
            if len(self.addr) != addr_count:
                lprint("E Not enough address values %s/%s in TOBJ.", (len(self.addr), addr_count))
                return False

        for addr_entry in self.addr:
            if addr_entry not in self.ADDR_TYPES:
                lprint("E Unknown TOBJ texture address type: %r, should be one of: %r.", (addr_entry, self.ADDR_TYPES))
                return False

        if self.bias != -1:
            try:
                self.bias = int(self.bias)
            except ValueError:
                lprint("E Invalid TOBJ bias value: %r, should be non-negative integer.", (self.bias,))
                return False

        if len(self.filter) > 0:
            if len(self.filter) != 2:
                lprint("E Invalid number of filter values %s/2 in TOBJ.", (len(self.filter),))
                return False

            for i in range(2):
                if self.filter[i] not in self.FILTER_TYPES:
                    lprint("E Invalid TOBJ filter value: %s, should be one of: %r.", (self.filter[i], self.FILTER_TYPES))
                    return False

        if self.target not in self.TARGET_TYPES:
            lprint("E Invalid TOBJ target value: %s, should be one of: %r.", (self.target, self.TARGET_TYPES))
            return False

        if len(self.border_color) > 0:
            if len(self.border_color) != 4:
                lprint("E Not enough border color values %s/4 in TOBJ.", (len(self.border_color),))
                return False

            for i in range(4):

                try:
                    self.border_color[i] = float(self.border_color[i])
                except ValueError:
                    lprint("E Invalid TOBJ border color value: %s, should be float.", (self.border_color[i],))
                    return False

        if self.color_space not in self.COLOR_SPACE_TYPES:
            lprint("E Invalid TOBJ color_space value: %s, should be one of: %r.", (self.color_space, self.COLOR_SPACE_TYPES))
            return False

        if self.usage not in self.USAGE_TYPES:
            lprint("E Invalid TOBJ usage value: %s, should be one of: %r.", (self.usage, self.USAGE_TYPES))
            return False

        return True

    def write_data_to_file(self, filepath=None):
        """Validates and writes container to TOBJ file into file path set in "filepath" variable.
        If extra file path is given it tries to export TOBJ there.

        :param filepath: optional extra absolute filepath where container should be exported as TOBJ file
        :type filepath: str
        :return: True if successful; False otherwise
        :rtype: bool
        """

        if filepath:
            self.filepath = filepath

        if not self.validate():
            lprint("E TOBJ data are invalid, aborting file save:\n\t   %r", (self.filepath,))
            return False

        try:

            file = open(self.filepath, "w", encoding="utf8", newline="\n")

        except IOError:

            lprint("E Can't write TOBJ file into path:\n\t   %r", (self.filepath,))
            return False

        fw = file.write

        # MAP
        fw("map")
        if self.map_type == "cube":
            frmt = " %s\n"
        else:
            frmt = "\t%s"

        fw(frmt % self.map_type)

        for map_name in self.map_names:
            fw("\t%s\n" % map_name)

        # ADDR
        if len(self.addr) > 0:

            fw("addr")
            if self.map_type == "cube" or self.map_type == "3d":
                sep = "\n\t"
            else:
                sep = "\t"

            for addr_value in self.addr:
                fw("%s%s" % (sep, addr_value))

            fw("\n")

        # NO MIPS
        if self.nomips:
            fw("nomips\n")

        # TRILINEAR
        if self.trilinear:
            fw("trilinear\n")

        # BIAS
        if self.bias != -1:
            fw("bias\t%s\n" % self.bias)

        # FILTER
        if len(self.filter) > 0:
            fw("filter\t%s\t%s\n" % (self.filter[0], self.filter[1]))

        # NO ANISOTROPIC
        if self.noanisotropic:
            fw("noanisotropic\n")

        # NO COMPRESS
        if self.nocompress:
            fw("nocompress\n")

        # TRANSPARENT
        if self.transparent:
            fw("transparent\n")

        # TARGET
        if self.target != "":
            fw("target\t%s\n" % self.target)

        # BORDER COLOR
        if len(self.border_color) > 0:
            fw("border_color\t{%s,%s,%s,%s}\n" % (self.border_color[0], self.border_color[1], self.border_color[2], self.border_color[3]))

        # BLACK BORDER
        if self.black_border:
            fw("black_border\n")

        # COLOR SPACE
        if self.color_space != "":
            fw("color_space\t%s\n" % self.color_space)

        # USAGE
        if self.usage != "":
            fw("usage\t%s\n" % self.usage)

        file.close()

        return True

    @classmethod
    def read_data_from_file(cls, filepath, skip_validation=False):
        """Reads data from given TOBJ file path, validates it and returns container with data.
        If validation process fails nothing will be returned,
        except if skipping of validation is requested container will be returned as it is.

        :param filepath: absolute TOBJ filepath from which to read data
        :type filepath: str
        :param skip_validation: True if reading should skip validation process
        :type skip_validation: bool
        :return: TOBJ container if everything is valid and TOBJ file exists; None otherwise
        :rtype: TobjContainer | None
        """

        if not filepath:
            lprint("I No TOBJ file path provided!")
            return None

        if not (os.path.isfile(filepath) and filepath.lower().endswith(".tobj")):
            lprint("W Invalid TOBJ file path %r!", (_path_utils.readable_norm(filepath),))
            return None

        records = _tobj.parse_file(filepath)
        records_len = len(records)
        records_iter = iter(records)

        if records is None or records_len <= 0:
            lprint("I TOBJ file %r is empty!", (_path_utils.readable_norm(filepath),))
            return None

        container = cls()
        container.filepath = os.path.normpath(filepath)
        for curr_rec in records_iter:

            # if "map" then we are expecting map type and texture/textures
            if curr_rec.lower() == "map":

                try:
                    curr_rec = next(records_iter).lower()
                except StopIteration:
                    break

                if curr_rec not in cls.MAP_TYPES:
                    break

                container.map_type = curr_rec
                tex_count = 6 if container.map_type == "cube" else 1  # only cube map has 6 textures
                not_enough_records = False
                while tex_count > 0:

                    try:
                        container.map_names.append(next(records_iter))
                    except StopIteration:
                        not_enough_records = True
                        break

                    tex_count -= 1

                if not_enough_records:
                    break

            # if "addr" we are expecting address types
            elif curr_rec.lower() == "addr":

                addr_count = 3 if container.map_type == "cube" else int(container.map_type[0])
                not_enough_records = False
                while addr_count > 0:

                    try:
                        container.addr.append(next(records_iter).lower())
                    except StopIteration:
                        not_enough_records = True
                        break

                    addr_count -= 1

                if not_enough_records:
                    break

            # if "border_color" we are expecting 9 records after it, each second is actual value
            elif curr_rec.lower() == "border_color":

                not_enough_records = False
                for i in range(9):

                    try:
                        curr_rec = next(records_iter)
                        if i % 2 == 1:
                            container.border_color.append(curr_rec)
                    except StopIteration:
                        not_enough_records = True
                        break

                if not_enough_records:
                    break

            # if "filter" we are expecting two values after it
            elif curr_rec.lower() == "filter":

                not_enough_records = False
                for i in range(2):

                    try:
                        container.filter.append(next(records_iter).lower())
                    except StopIteration:
                        not_enough_records = True
                        break

                if not_enough_records:
                    break

            elif curr_rec.lower() in ("bias", "target", "color_space", "usage"):

                try:
                    setattr(container, curr_rec.lower(), next(records_iter).lower())
                except StopIteration:
                    break

            # ignore obsolete "quality"
            elif curr_rec == "quality":

                try:
                    _ = next(records_iter)
                except StopIteration:
                    break

                continue

            # set any other known flag attribute to True
            elif hasattr(container, curr_rec.lower()):

                setattr(container, curr_rec.lower(), True)

            else:

                lprint("D Unkown TOBJ attribute: %r; TOBJ file:\n\t   %r", (curr_rec, container.filepath))

        # if not valid or not
        if not skip_validation and not container.validate():
            lprint("E TOBJ file: %r settings reading aborted, check printings above.", (container.filepath,))
            return None

        return container
