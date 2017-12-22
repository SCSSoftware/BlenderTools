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

from collections import OrderedDict
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.exp.pim_ef.piece_stream import Stream
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class Face:
    __index = 0
    __material = None  # save whole material reference to get index out of it when packing
    __indicies = []
    __streams = OrderedDict()  # dict of Stream class

    def __init__(self, index, material, vert_indicies):
        """Creates new face instance with given index, PIM material and list of vertex indicies.

        :param index: index of the face
        :type index: int
        :param material: material that should be used on for this piece
        :type material: io_scs_tools.exp.pim.material.Material
        :param vert_indicies: list of vertex indices for this face
        :type vert_indicies: list[int] | tuple[int]
        """
        self.__index = index
        self.__material = material
        self.__indicies = list(vert_indicies)
        self.__streams = OrderedDict()

    def add_normal(self, normal):
        """Adds next vertex normal to the end of the stream.

        NOTE: There is no check between length of stream and number of indicies present in face

        :param normal: next vertex normal
        :type normal: tuple[float] | mathutils.Vector
        """

        if Stream.Types.NORMAL not in self.__streams:
            self.__streams[Stream.Types.NORMAL] = Stream(Stream.Types.NORMAL, -1)

        stream = self.__streams[Stream.Types.NORMAL]
        stream.add_entry(normal)

    def add_uvs(self, uvs, uvs_names, uvs_aliases):
        """Adds next vertex uvs to the end of the all uv streams.

        NOTE: There is no check between length of uv streams and number of indicies present in face.
        Also :param uvs: and :param uvs_names: should have same length.

        :param uvs: next vertex uvs
        :type uvs: tuple[tuple[float]] | tuple[mathutils.Vector]
        :param uvs_names: tuple or list of uv layer names used on vertex
        :type uvs_names: list[str] | tuple[str]
        :param uvs_aliases: list of strings for uv aliases
        :type uvs_aliases: list[str]
        """

        for i, uv in enumerate(uvs):

            uv_type = Stream.Types.UV + str(i)
            # create more uv streams on demand
            if uv_type not in self.__streams:
                self.__streams[uv_type] = Stream(Stream.Types.UV, i, uvs_names[i])

            stream = self.__streams[uv_type]
            """:type: Stream"""
            stream.add_entry(uv)

            for alias in uvs_aliases[i]:
                stream.add_alias(alias)

    def add_rgbas(self, rgbas, rgbas_names):
        """Adds next vertex colors to the end of the stream.

        NOTE: There is no check between length of stream and number of indicies present in face

        :param rgbas: next vertex vertex colors
        :type rgbas: tuple[tuple[float]] | tuple[mathutils.Vector]
        :param rgbas_names: tuple or list of uv vertex color layer names used on vertex
        :type rgbas_names: list[str] | tuple[str]
        """

        for i, rgba in enumerate(rgbas):

            rgba_type = Stream.Types.RGBA + str(i)
            if rgba_type not in self.__streams:
                self.__streams[rgba_type] = Stream(Stream.Types.RGBA, i, rgbas_names[i])

            stream = self.__streams[rgba_type]
            """:type: Stream"""
            stream.add_entry(rgba)

    def get_stream_count(self):
        """Gets count of all streams used in this face.

        :return: stream count
        :rtype: int
        """
        return len(self.__streams.keys())

    def get_as_section(self):
        """Gets face represented with SectionData structure class.
        :return: packed piece as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Face")
        section.props.append(("Index", self.__index))
        if not self.__material or self.__material.get_index() == -1:
            lprint("W Piece with face index %s doesn't have data about material, expect errors in game!", (self.__index,))
            section.props.append(("Material", -1))
        else:
            section.props.append(("Material", self.__material.get_index()))

        section.props.append(("Indices", list(self.__indicies)))

        stream_size = None
        for stream_tag in self.__streams:
            stream = self.__streams[stream_tag]

            # CHECK SYNC OF STREAMS
            if not stream_size:
                stream_size = stream.get_size()
            elif stream_size != stream.get_size():
                lprint("W Piece with face index %s has desynced stream sizes, expect errors in game!", (self.__index,))
                break

            # APPEND STREAMS
            section.sections.append(stream.get_as_section())

        return section
