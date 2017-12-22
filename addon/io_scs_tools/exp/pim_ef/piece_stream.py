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

# Copyright (C) 2017: SCS Software

from io_scs_tools.exp.pim.piece_stream import Stream as _Stream


class Stream(_Stream):
    __name = ""

    def __init__(self, stream_type, index, name=""):
        """Constructor for stream with given type, index and optional name.
        NOTE: index is used only for SCALAR, UV and TUV stream types

        :param stream_type: type of stream (eg. Stream.Types.POSITION)
        :type stream_type: str
        :param index: index of stream, used only for SCALAR, UV and TUV
        :type index: int
        :type name: optional name of the stream, in case of UVs this will be used to save layer name
        :type name: str
        """

        super().__init__(stream_type, index)

        # exchange format support multiple vertex color layers
        if stream_type == Stream.Types.RGBA:
            self.__tag_index = index
            self.__format = "FLOAT4"

        self.__name = name

    def get_as_section(self):
        """Gets stream represented with SectionData structure class.

        :return: packed stream as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = super().get_as_section()

        section.props.insert(1, ("Name", self.__name))

        return section
