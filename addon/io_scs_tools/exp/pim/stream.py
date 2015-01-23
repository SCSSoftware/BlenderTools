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


from io_scs_tools.internals.structure import SectionData as _SectionData


class Stream:
    class Types:
        """Enumerator class for storing types of possible PIM streams
        """
        POSITION = "_POSITION"
        NORMAL = "_NORMAL"
        TANGENT = "_TANGENT"
        RGB = "_RGB"
        RGBA = "_RGBA"
        UV = "_UV"  # NOTE: there can be up to 9 uv streams
        TUV = "_TUV"  # NOTE: there can be up to 9 tuv streams

    format = ""  # defined by type of tag
    tag = Types.POSITION
    tag_index = -1  # used for UV and TUV

    aliases = {}
    data = []

    def __init__(self, stream_type, index):
        """Constructor for stream with given type and index.
        NOTE: index is used only for SCALAR, UV and TUV stream types

        :param stream_type: type of stream (eg. Stream.Types.POSITION)
        :type stream_type: str
        :param index: index of stream, used only for SCALAR, UV and TUV
        :type index: int
        """

        self.aliases = {}
        self.data = []

        self.tag = stream_type

        if stream_type == Stream.Types.POSITION:
            self.format = "FLOAT3"
        elif stream_type == Stream.Types.NORMAL:
            self.format = "FLOAT3"
        elif stream_type == Stream.Types.TANGENT:
            self.format = "FLOAT4"
        elif stream_type == Stream.Types.RGB:
            self.format = "FLOAT3"
        elif stream_type == Stream.Types.RGBA:
            self.format = "FLOAT4"
        elif stream_type == Stream.Types.UV:
            self.tag_index = index
            self.format = "FLOAT2"
        elif stream_type == Stream.Types.TUV:
            self.tag_index = index
            self.format = "UNKNOWN"  # TODO: ask someone what is actually tuv stream

    def add_entry(self, value):
        """Adds new entry to data of stream.

        :param value: tuple or list value
        :type value: tuple | list
        :return: True if length is correct; otherwise false
        :rtype: bool
        """

        if self.tag == Stream.Types.POSITION and len(value) != 3:
            return False
        if self.tag == Stream.Types.NORMAL and len(value) != 3:
            return False
        if self.tag == Stream.Types.TANGENT and len(value) != 4:
            return False
        if self.tag == Stream.Types.RGB and len(value) != 3:
            return False
        if self.tag == Stream.Types.RGBA and len(value) != 4:
            return False
        if self.tag == Stream.Types.UV and len(value) != 2:
            return False

        self.data.append(tuple(value))
        return True

    def add_alias(self, alias):
        """Adds alias to stream.
        NOTE: only unique aliases will be kept

        :param alias: string representing alias
        :type alias: str
        :return: True if alias is added; otherwise false
        :rtype: bool
        """

        if alias not in self.aliases:
            self.aliases[alias] = 1
            return True

        return False

    def get_size(self):
        """Gets size of the stream

        :return: size of stream
        :rtype: int
        """
        return len(self.data)

    def get_tag(self):
        """Gets the tag of the stream

        :return: complete tag of the stream
        :rtype: str
        """

        if -1 < self.tag_index < 10:
            return self.tag + str(self.tag_index)
        else:
            return self.tag

    def get_as_section(self):
        """Gets stream represented with SectionData structure class.

        :return: packed stream as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Stream")
        section.props.append(("Format", self.format))

        if -1 < self.tag_index < 10:
            section.props.append(("Tag", self.tag + str(self.tag_index)))
        else:
            section.props.append(("Tag", self.tag))

        if len(self.aliases) > 0:
            aliases = sorted(self.aliases.keys())
            section.props.append(("AliasCount", len(aliases)))
            section.props.append(("Aliases", aliases))

        section.data = self.data

        return section