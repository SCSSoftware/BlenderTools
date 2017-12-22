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

import re
from mathutils import Matrix
from io_scs_tools.utils.printout import print_section
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.convert import hex_string_to_float


def _get_prop(line):
    """Takes single data line and returns data properties.

    :param line: A single line from a file
    :type line: str
    :return: Data property value in appropriate data type
    :rtype: various
    """
    prop_split = re.split(r'[:\(\r\n]+', line, 1)
    prop = []
    if len(prop_split) == 2:
        # print('-prop_split: "%s"' % str(prop_split))
        prop.append(prop_split[0].strip())
        prop_value = prop_split[1].strip()
        if prop_value in ("FLOAT", "FLOAT2", "FLOAT3", "FLOAT4", "INT", "INT2", "STRING"):
            prop.append(prop_value)
            return prop
        elif prop_value in ("FLOAT4x4", ):
            # print('WARNING - UNHANDLED VALUE (prop_value: %s)' % str(prop_value))
            prop.append(prop_value)
            return prop
        else:
            try:
                if prop_value[0] == '"' and prop_value[-1] == '"':

                    # SINGLE STRING
                    prop_value = prop_value[1:-1]
                else:
                    try:

                        # SINGLE INTEGER
                        prop_value = int(prop_value)
                    except:
                        try:

                            # SINGLE FLOAT
                            prop_value = float(prop_value)
                        except:
                            if prop_value.count(' ') > 0:
                                # if prop_value.startswith("("):
                                if prop_value.endswith(")"):
                                    val_list = []
                                    prop_values_only = prop_value[1:-1]
                                    for string in re.split(r'[, ]+', prop_values_only):
                                        if string:
                                            val = "<error>"
                                            if string.startswith("&"):

                                                # LIST OF - HEX NUMBERS
                                                val = hex_string_to_float(string)
                                            else:
                                                try:

                                                    # LIST OF - INTEGERS
                                                    val = int(string)
                                                except:
                                                    try:

                                                        # LIST OF - FLOATS
                                                        val = float(string)
                                                    except:

                                                        # LIST OF - STRINGS
                                                        val = string[1:-1]
                                            val_list.append(val)

                                    # LIST OF HEX NUMBERS
                                    prop_value = tuple(val_list)
                                else:
                                    prop_values = re.split(r'[ ]+', prop_value)
                                    prop_value = []
                                    for val in prop_values:
                                        # SEQUENCE OF INTS (without brackets)
                                        prop_value.append(int(val))
                            else:
                                if prop_value.startswith("&"):

                                    # SINGLE HEX NUMBER
                                    prop_value = hex_string_to_float(prop_value)
                                elif prop_value in ("default", "true", "false"):

                                    # CERTAIN STRINGS WITHOUT ENCLOSING
                                    prop_value = str(prop_value)
                                else:

                                    # UNHANDLED DATA
                                    print('WARNING - "internals/parsers/pix.py" - Unhandled case! (prop_value = %s)' % str(prop_value))
            except:

                # NONE
                prop_value = None
            prop.append(prop_value)
    else:
        # print('WARNING - Unhandled case in "property" line "%s"! Skipped...' % line)
        return None
    return prop


def _read_matrix(file, line_split):
    """Reads the other lines to make a matrix."""
    matrix = Matrix()
    for row in range(4):
        for col in range(4):
            matrix[row][col] = hex_string_to_float(line_split[col])
        if row < 3:
            data_type, line = next_line(file)
            line_split = re.split(' +', line.strip())
    return matrix


def _get_data(file, line):
    """Takes single data line and returns data index and list of its values."""
    data_split = re.split(r'[()]+', line)
    # print('data_split: "%s"' % data_split)

    # SKINNING DATA
    if len(data_split) > 3:
        try:
            data_index = int(data_split[0].strip())
            data_gap = data_split[1].strip()
            data_vec = re.split(' +', data_split[2].strip())  # This value is not used anymore.
            data = {}
            if data_gap == "" and len(data_vec) == 3:
                # print('  %i - %r - %s' % (data_index, data_gap, data_vec))

                # WEIGHTS
                data_type, line = next_line(file)
                line_split = re.split(' +', line.strip())
                if line_split[0] == "Weights:":
                    # print('%s  =-> "%s"' % (data_type, line_split))
                    data['weights'] = []
                    for cnt in range(int(line_split[1])):
                        w_index = int(line_split[(cnt * 2) + 2])
                        w_value = hex_string_to_float(line_split[(cnt * 2) + 3])
                        # print('  %i---%s' % (w_index, w_value))
                        data['weights'].append((w_index, w_value))

                # CLONES
                data_type, line = next_line(file)
                line_split = re.split(' +', line.strip())
                if line_split[0] == "Clones:":
                    # print('%s  =-> "%s"' % (data_type, line_split))
                    data['clones'] = []
                    for cnt in range(int(line_split[1])):
                        c_piece = int(line_split[(cnt * 2) + 2])
                        c_vertex = int(line_split[(cnt * 2) + 3])
                        # print('  %i---%s' % (c_piece, c_vertex))
                        data['clones'].append((c_piece, c_vertex))

                # CLOSING BRACKET
                data_type, line = next_line(file)
                # line_split = re.split(' +', line.strip())
                # print('%s  =-> "%s"' % (data_type, line_split))
        except:
            print('WARNING - Unhandled case in "Skinning Data" line "%s"! Skipped...' % line)
            return None, []
    else:
        try:
            data_index = int(data_split[0].strip())
            data_str_values = re.split(r'[ ]+', data_split[1].strip())
            # print('data_str_values: "%s"' % data_str_values)

            # BONE LIST
            if data_str_values[0].startswith('"') and data_str_values[0].endswith('"'):
                data = data_str_values[0][1:-1]
                # print('data: "%s"' % data)

            # ANIMATION MATRICES
            elif len(data_str_values) == 4 and line[-1] != ")":
                # print(' line: %s' % line)
                try:
                    data_index = int(data_split[0].strip())
                except:
                    print('WARNING - Unhandled case in "Animation Matrices" line "%s"! Skipped...' % line)
                    return None, []
                data = _read_matrix(file, data_str_values)

            # BONE STRUCTURE
            elif data_str_values[0] == "Name:":
                data = {}
                if data_str_values[1].startswith('"') and data_str_values[1].endswith('"'):
                    name = data_str_values[1][1:-1]
                    data['name'] = name
                    # print('    data_str_values: "%s"' % data_str_values)

                    # PARENT
                    data_type, line = next_line(file)
                    line_split = re.split(' +', line.strip())
                    if line_split[0] == "Parent:":
                        parent = line_split[1][1:-1]
                        data['parent'] = parent
                    # print('%s  =-> "%s"' % (data_type, line_split))

                    # MATRIX - LINE 1
                    data_type, line = next_line(file)
                    line_split = re.split(' +', line.strip())
                    if line_split[0] == "Matrix:":
                        matrix = _read_matrix(file, line_split[2:])

                        # CLOSING BRACKET
                        data_type, line = next_line(file)
                        data['matrix'] = matrix
            else:
                data = []
                for data_str in data_str_values:
                    if data_str[0] == '&':
                        val = hex_string_to_float(data_str)
                    elif "." in data_str:
                        val = float(data_str)
                    else:
                        val = int(data_str)
                    data.append(val)
        except:
            print('WARNING - Unhandled case in "Data" line "%s"! Skipped...' % line)
            return None, []
    return data_index, data


def _read_section(file, section_ids, pix_container):
    """This function reads the nested sections. It recursively
    calls itself to read all levels of data hierarchy."""
    data_type = ''
    props = []
    data = []
    data_index = 0
    section_type = ''
    while data_type != 'SE_E':
        data_type, line = next_line(file)
        if data_type in ('EOF', 'ERR'):
            break
        # print('%s  =-> "%s"' % (type, line))
        if data_type == 'Prop':
            # print(' -++- line: %s' % line)
            prop = _get_prop(line)
            # print('prop: %s' % prop)
            if prop is not None:
                props.append(prop)
        elif data_type == 'data':
            # print('line: "%s"' % line)
            dat_index, dat = _get_data(file, line)
            if dat_index == data_index:
                # print('dat: %s' % dat)
                data_index += 1
                if dat != []:
                    data.append(dat)
            else:
                print('WARNING - Inconsistent data indexing in line: "%s"! Skipping...' % line)
        elif data_type == 'empty_line':
            props.append(("", ""))
        elif data_type == 'line_C':
            comment = line.strip()
            props.append(("#", comment[2:]))
        elif data_type == 'SE_C':
            # comment_section = data_structures.section_data("#comment")
            print('comment section: "%s"' % line)
        elif data_type == 'SE_S':
            # section_type = re.split(r'[ ]+', line)[0]
            type_line = re.split(r'[ ]+', line)
            for rec in type_line:
                if rec != '':
                    try:
                        section_type = re.split(r'[ ]+', line)[1]
                    except:
                        section_type = ''
                        print('WARNING - Unknown data in line: "%s"! Skipping...' % line)
                    break
            new_section_ids = _SectionData(section_type)
            new_section, pix_container = _read_section(file, new_section_ids, pix_container)
            section_ids.sections.append(new_section)
            # pix_container.append(new_section)
        if data_type != 'SE_E':
            section_ids.props = props
            section_ids.data = data
    return section_ids, pix_container


def next_line(file):
    """Takes a file..."""
    data_type = ''
    try:
        line = file.readline()
    except UnicodeDecodeError:
        return 'ERR', ''
    if not line:
        return 'EOF', ''
    if line[-1] in '\r\n':
        line = line[:-1]
    if line.startswith("#"):
        # print('  comment section "%s"' % line.strip())
        # type = 'SE_C'  # TODO: Parsing of Comment Sections isn't finished!
        data_type = 'line_C'
    elif line.strip().startswith("#"):
        # print('  comment line "%s"' % line.strip())
        data_type = 'line_C'
    elif line == "":
        data_type = 'empty_line'
    elif "{" in line:
        data_type = 'SE_S'
    elif "}" in line:
        data_type = 'SE_E'
    else:
        line_split = re.split(r'[ :\(]+', line.strip(), 1)
        try:
            line_index = int(line_split[0])
            # print('line_index: %s' % line_index)
        except:
            if "#" in line.strip():  # Cut off the comments in property lines
                line_split = re.split(r'#', line.strip(), 1)
                line = line_split[0]
            # print(' +--+ line: %s' % line)
            data_type = 'Prop'
        else:
            data_type = 'data'
            # if line_index == 0:
            # print(' xOx line: %s' % str(line))
            # print('"%s" - line_split: %s' % (type, line_split))
    return data_type, line


def read_data(filepath, ind, print_info=False):
    """This function is called from outside of this script. It loads
    all data form the file and returns data container.

    :param filepath: File path to be read
    :type filepath: str
    :param ind: Indentation which is expected in the file
    :type ind: str
    :param print_info: Whether to print the debug printouts
    :type print_info: bool
    :return: (PIX Section Object Data [io_scs_tools.internals.structures.SectionData], Data type [str])
    :rtype: tuple of (list of SectionData, str)
    """
    if print_info:
        print('** PIx Parser ...')
        print('   filepath: %r' % str(filepath))
    pix_container = []

    # if filepath:
    file = open(filepath, mode="r", encoding="utf8")
    while 1:
        data_type, line = next_line(file)
        if data_type in ('EOF', 'ERR'):
            break
        # print('%s  ==> "%s"' % (data_type, line))
        if data_type == 'SE_S':
            section_type = re.split(r'[ ]+', line)[0]
            section_ids = _SectionData(section_type)
            section, pix_container = _read_section(file, section_ids, pix_container)
            pix_container.append(section)
    file.close()

    if print_info:
        for section in pix_container:
            print('SEC.: "%s"' % section.type)
            for prop in section.props:
                print('%sProp: %s' % (ind, prop))
            for data in section.data:
                print('%sdata: %s' % (ind, data))
            for sec in section.sections:
                print_section(sec, ind)
        print('** PIx Parser END')
    return pix_container, data_type