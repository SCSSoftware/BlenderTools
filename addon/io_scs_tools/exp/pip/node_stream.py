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

from io_scs_tools.internals.structure import SectionData as _SectionData


class Stream:
    class Types:
        """Enumerator class for storing types of possible PIP streams
        """
        POSITION = "_POSITION"
        NORMAL = "_NORMAL"
        VARIANT_BLOCK = "_VARIANT_BLOCK"

    __format = ""  # defined by type of tag
    __tag = Types.POSITION

    __data = []

    def __init__(self, stream_type):
        """Constructor for stream with given type.

        :param stream_type: type of stream (eg. Node.Stream.Types.POSITION)
        :type stream_type: str
        """

        self.__aliases = {}
        self.__data = []

        self.__tag = stream_type

        if stream_type == Stream.Types.POSITION:
            self.__format = "FLOAT3"
        elif stream_type == Stream.Types.NORMAL:
            self.__format = "FLOAT3"
        elif stream_type == Stream.Types.VARIANT_BLOCK:
            self.__format = "INT2"

    def add_entry(self, value):
        """Adds new entry to data of stream.

        :param value: tuple or list value
        :type value: tuple | list
        :return: True if length is correct; otherwise false
        :rtype: bool
        """

        if self.__tag == Stream.Types.POSITION and len(value) != 3:
            return False
        if self.__tag == Stream.Types.NORMAL and len(value) != 3:
            return False
        if self.__tag == Stream.Types.VARIANT_BLOCK and len(value) != 2:
            return False

        self.__data.append(tuple(value))
        return True

    def get_size(self):
        """Gets size of the stream

        :return: size of stream
        :rtype: int
        """
        return len(self.__data)

    def get_tag(self):
        """Gets the tag of the stream

        :return: complete tag of the stream
        :rtype: str
        """
        return self.__tag

    def get_as_section(self):
        """Gets stream represented with SectionData structure class.

        :return: packed stream as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Stream")
        section.props.append(("Format", self.__format))
        section.props.append(("Tag", self.__tag))

        section.data = self.__data

        return section
