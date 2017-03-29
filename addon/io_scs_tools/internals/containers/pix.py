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
import re
from mathutils import Vector
from io_scs_tools.internals.containers.parsers import pix as _pix_parser
from io_scs_tools.internals.containers.writers import pix as _pix_writer
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint


def fast_check_for_pia_skeleton(pia_filepath, skeleton):
    """Check for the skeleton record in PIA file without parsing the whole file.
    It takes filepath and skeleton name (string) and returns True if the skeleton
    record in the file is the same as skeleton name provided, otherwise False."""
    file = open(pia_filepath, mode="r", encoding="utf8")
    while 1:
        data_type, line = _pix_parser.next_line(file)
        if data_type in ('EOF', 'ERR'):
            break
        # print('%s  ==> "%s"' % (data_type, line))
        if data_type == 'SE_S':
            section_type = re.split(r'[ ]+', line)[0]
            if section_type == "Global":
                # print('  %s' % section_type)
                data_type, line = _pix_parser.next_line(file)
                ske = re.split(r'"', line)[1]
                # print('  %r | %r' % (ske, skeleton))
                pia_skeleton = os.path.join(os.path.dirname(pia_filepath), ske)
                if os.path.isfile(pia_skeleton) and os.path.samefile(pia_skeleton, skeleton):
                    file.close()
                    return True
                break
    file.close()
    return False


def utter_check_for_pia_skeleton(pia_filepath, armature):
    """Skeleton analysis in PIA file with reasonably quick searching the whole file.
    It takes filepath and an Armature object and returns True if the skeleton in PIA file
    can be used for the skeleton in provided Armature object, otherwise it returns False."""
    file = open(pia_filepath, mode="r", encoding="utf8")
    skeleton = None
    bone_matches = []
    while 1:
        data_type, line = _pix_parser.next_line(file)
        if data_type == 'EOF':
            if len(bone_matches) > 0:
                break
            else:
                file.close()
                return False, None
        if data_type == 'ERR':
            file.close()
            return False, None
        # print('%s  ==> "%s"' % (data_type, line))
        if data_type == 'SE_S':
            section_type = re.split(r'[ ]+', line)[0]
            if section_type == "Global":
                # print('  %s' % section_type)
                data_type, line = _pix_parser.next_line(file)
                line_split = re.split(r'"', line)
                # print('  %r | %r' % (line_split, skeleton))
                if line_split[0].strip() == "Skeleton:":
                    skeleton = line_split[1].strip()
            elif section_type == "BoneChannel":
                data_type, line = _pix_parser.next_line(file)
                # print('  %s - %s' % (data_type, line))
                prop_name = re.split(r'"', line)[1]
                # print('  %r' % prop_name)
                if prop_name in armature.data.bones:
                    bone_matches.append(prop_name)
                else:
                    file.close()
                    return False, None
    file.close()
    return True, skeleton


def make_triangle_stream(stream_raw):
    """
    Takes a raw triangle list and returns valid
    "Triangle" data ("section_data" data type).
    :param stream_raw:
    :return:
    """
    stream = _SectionData("Triangles")
    for item in stream_raw:
        stream.data.append(item)
    return stream


def make_stream_section(data, data_tag, aliases):
    """Takes data and their tag returns a stream section.

    :param data: Section data
    :type data: list
    :param data_tag: Tag (name) for the Section
    :type data_tag: str
    :param aliases: tuple of strings (aliases)
    :type aliases: tuple
    :return: 'Stream' Section data
    :rtype: SectionData
    """
    # print('data: %s type: %s' % (str(data[0]), str(type(data[0]))))
    if type(data[0]) is Vector:
        data_type = 'NIC'
        if type(data[0][0]) is type(0.0):
            data_type = 'FLOAT'
        elif type(data[0][0]) is type(0):
            data_type = 'INT'
        data_format = str(data_type + str(len(data[0])))
    elif data[0][0] == "__matrix__":
        data_format = 'FLOAT4x4'
    elif data[0][0] == "__time__":
        data_format = 'FLOAT'
    else:
        data_format = 'UNKNOWN_FORMAT'
    # print(' format: %r' % format)
    stream_section = _SectionData("Stream")
    stream_section.props.append(("Format", data_format))
    stream_section.props.append(("Tag", data_tag))
    if aliases:
        stream_section.props.append(("AliasCount", len(aliases)))
        for alias in aliases:
            stream_section.props.append(("Aliases", alias))
    stream_section.data = data
    return stream_section


def make_vertex_stream(stream_raw, name=''):
    """
    Takes a raw stream and returns a valid stream data ("section_data" data type).
    If a name is provided, it is written to the stream.
    :param stream_raw:
    :param name:
    :return:
    """
    stream = _SectionData("Stream")
    # print('\nstream_raw:\n  %s' % str(stream_raw))
    # print('stream_raw[1]: %s' % stream_raw[1])
    if len(stream_raw[1]) > 0:
        float_cnt = len(stream_raw[1][0])
        if float_cnt > 1:
            float_lenght = str('FLOAT' + str(float_cnt))
        else:
            float_lenght = 'FLOAT'
        stream.props.append(("Format", float_lenght))
        if name != '':
            stream.props.append(("Name", name))
        stream.props.append(("Tag", stream_raw[0]))
        stream.data = stream_raw[1]
    else:
        stream.props.append(("Format", 'NO-DATA'))
        if name != '':
            stream.props.append(("Name", name))
        stream.props.append(("Tag", stream_raw[0]))
        stream.data = ((0.0,),)
    return stream


def get_data_from_file(filepath, ind, print_info=False):
    """Returns entire data in data container from specified PIX file.

    :param filepath: File path to be read
    :type filepath: str
    :param ind: Indentation which is expected in the file
    :type ind: str
    :param print_info: Whether to print the debug printouts
    :type print_info: bool
    :return: PIX Section Object Data
    :rtype: list of SectionData
    """

    if filepath is None:
        lprint("D Aborting PIX file read, 'None' file!")
        return None

    # print('    filepath: "%s"\n' % filepath)
    container, state = _pix_parser.read_data(filepath, ind, print_info)
    if len(container) < 1:
        lprint('\nE File "%s" is empty!', (_path_utils.readable_norm(filepath),))
        return None

    # print_container(container)  # TEST PRINTOUTS
    # write_config_file(container, filepath, ind, "_reex")  # TEST REEXPORT

    return container


def write_data_to_file(container, filepath, ind, print_info=False):
    """Exports given container in given filepath.

    :param container:
    :type container:
    :param filepath: path to file where container should be exported
    :type filepath: str
    :param ind: intendention for printout
    :type ind: str
    :param print_info: should infos be printed
    :type print_info: bool
    :return: True if export was successfull, otherwise False
    :rtype: bool
    """

    # convert filepath in readable form so when file writting will be logged
    # path will be properly readable even on windows. Without mixed back and forward slashes.
    filepath = _path_utils.readable_norm(filepath)

    result = _pix_writer.write_data(container, filepath, ind, print_info=print_info)
    if result != {'FINISHED'}:
        lprint("E Unable to export data into file:\n\t   %r\n\t   For details check printouts above.", (filepath,))
        return False
    else:
        lprint("I File created!")
        return True
