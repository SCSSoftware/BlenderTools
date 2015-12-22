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

def parse_file(filepath, print_info=False):
    """Reads data from TOBJ file and returns it's records as list.

    :param filepath: tobj file path
    :type filepath: str
    :param print_info: switch for printing parsing info
    :type print_info: bool
    :return: all TOBJ entries as list in the order they are saved in the file
    :rtype: list[str]
    """

    if print_info:
        print('** TOBJ Parser ...')
        print('   filepath: %r' % str(filepath))

    data = []
    with open(filepath) as f:
        for i, line in enumerate(f):
            line_split = line.strip().split()
            if len(line_split) != 0:

                # ignore C-like comment lines
                if line_split[0].startswith("//"):
                    continue

                # ignore comment lines starting with #
                if line_split[0].startswith("#"):
                    continue

                for word in line_split:
                    data.append(word)

    f.close()

    return data
