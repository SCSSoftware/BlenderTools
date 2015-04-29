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

from mathutils import Vector
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.structure import SectionData as _SectionData


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
    from io_scs_tools.internals.parsers import pix

    # print('    filepath: "%s"\n' % filepath)
    container, state = pix.read_data(filepath, ind, print_info)
    if len(container) < 1:
        lprint('\nE File "%s" is empty!', (str(filepath).replace("\\", "/"),))
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
    from io_scs_tools.internals.writers import pix

    result = pix.write_data(container, filepath, ind, print_info=print_info)
    if result != {'FINISHED'}:
        lprint('\nE Unable to export data into file:\n  "%s"\nFor details check printouts above.', (str(filepath).replace("\\", "/"),))
        return False
    else:
        lprint('I File created!\n')
        return True


