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

# Copyright (C) 2013-2019: SCS Software

from collections import OrderedDict
from io_scs_tools.exp.pim.piece_skin_stream import PieceSkinStream
from io_scs_tools.internals.structure import SectionData as _SectionData


class PieceSkin:
    __global_piece_skin_counter = 0

    @staticmethod
    def reset_counter():
        PieceSkin.__global_piece_skin_counter = 0

    @staticmethod
    def get_global_piece_skin_count():
        return PieceSkin.__global_piece_skin_counter

    __piece = -1
    __skin_streams_count = 0
    __piece_skin_streams = None

    def __init__(self, piece_idx, skin_stream):
        """Initialize skin with given skin stream object.
        :param piece_idx: index of the piece inside SCS game object
        :type piece_idx: int
        :param skin_stream: position skin stream for this skin
        :type skin_stream: PieceSkinStream
        """

        self.__piece = piece_idx
        self.__skin_streams_count = 0
        self.__piece_skin_streams = OrderedDict()
        self.__piece_skin_streams[skin_stream.get_tag()] = skin_stream

        PieceSkin.__global_piece_skin_counter += 1

    def get_skin_stream_by_type(self, stream_type):
        """Gets skin stream by given type.

        :param stream_type: type of the stream to get, one of PieceSkinStream.Types
        :type stream_type: str
        :return: piece skin stream of given type or None if stream type deosn't exists
        :rtype: PieceSkinStream | None
        """

        skin_types = (PieceSkinStream.Types.POSITION, PieceSkinStream.Types.NORMAL, PieceSkinStream.Types.TANGENT)
        if stream_type in skin_types and stream_type in self.__piece_skin_streams:
            return self.__piece_skin_streams[stream_type]

        return None

    def get_as_section(self):
        """Gets whole model skin represented with SectionData structure class.
        :return: packed skin as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        self.__skin_streams_count = len(self.__piece_skin_streams)

        section = _SectionData("PieceSkin")

        section.props.append(("Piece", self.__piece))
        section.props.append(("StreamCount", self.__skin_streams_count))

        for piece_skin_stream in self.__piece_skin_streams.values():
            section.sections.append(piece_skin_stream.get_as_section())

        return section
