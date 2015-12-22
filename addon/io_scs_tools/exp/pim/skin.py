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

# Copyright (C) 2013-2015: SCS Software

from collections import OrderedDict
from io_scs_tools.exp.pim.skin_stream import SkinStream
from io_scs_tools.internals.structure import SectionData as _SectionData


class Skin:
    __skin_streams_count = 0
    __skin_streams = OrderedDict()

    def __init__(self, skin_stream):
        """Initialize skin with given skin stream object.
        :param skin_stream: position skin stream for this skin
        :type skin_stream: SkinStream
        """

        self.__skin_streams[skin_stream.get_tag()] = skin_stream

    def get_as_section(self):
        """Gets whole model skin represented with SectionData structure class.
        :return: packed skin as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        self.__skin_streams_count = len(self.__skin_streams)

        section = _SectionData("Skin")

        section.props.append(("StreamCount", self.__skin_streams_count))

        for skin_stream in self.__skin_streams.values():
            section.sections.append(skin_stream.get_as_section())

        return section
