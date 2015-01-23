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

from collections import OrderedDict
from io_scs_tools.exp.pim.stream import Stream
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class Piece:
    _index = 0
    _vertex_count = 0
    _triangle_count = 0
    _stream_count = 0

    _material = None  # save whole material reference to get index out of it when packing
    _streams = OrderedDict()  # dict of Stream class
    _triangles = []  # list of Triangle class

    _vertices_hash = {}

    _global_piece_count = 0
    _global_vertex_count = 0
    _global_triangle_count = 0

    @staticmethod
    def reset_counters():
        Piece._global_piece_count = 0
        Piece._global_triangle_count = 0
        Piece._global_vertex_count = 0

    @staticmethod
    def get_global_piece_count():
        return Piece._global_piece_count

    @staticmethod
    def get_global_vertex_count():
        return Piece._global_vertex_count

    @staticmethod
    def get_global_triangle_count():
        return Piece._global_triangle_count

    @staticmethod
    def __calc_vertex_hash(index, uvs, rgba):
        """Calculates vertex hash from original vertex index, uvs components and vertex color.
        :param index: original index from Blender mesh
        :type index: int
        :param uvs: list of uvs used on vertex (each uv must be in SCS coordinates)
        :type uvs: list of (tuple | mathutils.Vector)
        :param rgba: rgba representation of vertex color in SCS values
        :type rgba: tuple | mathutils.Color
        :return: calculated vertex hash
        :rtype: str
        """

        frmt = "%.4f"

        vertex_hash = str(index)
        for uv in uvs:
            vertex_hash += frmt % uv[0] + frmt % uv[1]

        vertex_hash += frmt % rgba[0] + frmt % rgba[1] + frmt % rgba[2] + frmt % rgba[3]

        return vertex_hash

    def __init__(self, index, material):
        """Constructs empty piece.
        NOTE: empty piece will contain for mandatory stream which will be empty: POSITION, NORMAL, UV0, RGBA
        :param index:
        :type index:
        :param material: material that should be used on for this piece
        :type material: io_scs_tools.exp.pim.material.Material
        """
        self._vertex_count = 0
        self._triangle_count = 0
        self._stream_count = 0
        self._streams = OrderedDict()
        self._triangles = []
        self._vertices_hash = {}

        self._index = index
        self._material = material

        # CONSTRUCT ALL MANDATORY STREAMS
        stream = Stream(Stream.Types.POSITION, -1)
        self._streams[Stream.Types.POSITION] = stream

        stream = Stream(Stream.Types.NORMAL, -1)
        self._streams[Stream.Types.NORMAL] = stream

        Piece._global_piece_count += 1

    def add_triangle(self, triangle):
        """Adds new triangle to piece
        NOTE: if length of given triangle iterable is different than 3 it will be refused!
        :param triangle: tuple of 3 integers representing vertex indices
        :type triangle: tuple
        :return: True if added; False otherwise
        :rtype:
        """

        if len(triangle) != 3:
            return False
        else:
            # check indecies integrity
            for vertex in triangle:
                if vertex < 0 or vertex >= self._vertex_count:
                    return False

            self._triangles.append(tuple(triangle))
            Piece._global_triangle_count += 1

        return True

    def add_vertex(self, vert_index, position, normal, uvs, uvs_aliases, rgba, tangent):
        """Adds new vertex to position and normal streams
        :param vert_index: original vertex index from Blender mesh
        :type vert_index: int
        :param position: vector or tuple of vertex position in SCS coordinates
        :type position: tuple | mathutils.Vector
        :param normal: vector or tuple of vertex normal in SCS coordinates
        :type normal: tuple | mathutils.Vector
        :param uvs: list of uvs used on vertex (each uv must be in SCS coordinates)
        :type uvs: list of (tuple | mathutils.Vector)
        :param rgba: rgba representation of vertex color in SCS values
        :type rgba: tuple | mathutils.Color
        :return: vertex index inside piece streams ( use it for adding triangles )
        :rtype: int
        """

        vertex_hash = self.__calc_vertex_hash(vert_index, uvs, rgba)

        # save vertex if the vertex with the same properties doesn't exists yet in streams
        if not vertex_hash in self._vertices_hash:

            stream = self._streams[Stream.Types.POSITION]
            stream.add_entry(position)

            stream = self._streams[Stream.Types.NORMAL]
            stream.add_entry(normal)

            for i, uv in enumerate(uvs):
                uv_type = Stream.Types.UV + str(i)
                # create more uv streams on demand
                if uv_type not in self._streams:
                    self._streams[uv_type] = Stream(Stream.Types.UV, i)

                stream = self._streams[uv_type]
                """:type: Stream"""
                stream.add_entry(uv)

                for alias in uvs_aliases[i]:
                    stream.add_alias(alias)

            if tangent:
                # create tangent stream on demand
                if Stream.Types.TANGENT not in self._streams:
                    self._streams[Stream.Types.TANGENT] = Stream(Stream.Types.TANGENT, -1)

                stream = self._streams[Stream.Types.TANGENT]
                stream.add_entry(tangent)

            if Stream.Types.RGBA not in self._streams:
                self._streams[Stream.Types.RGBA] = Stream(Stream.Types.RGBA, -1)

            stream = self._streams[Stream.Types.RGBA]
            stream.add_entry(rgba)

            vert_index_internal = stream.get_size() - 1  # streams has to be alligned so I can take last one for the index
            self._vertices_hash[vertex_hash] = (vert_index, vert_index_internal)

            self._vertex_count = vert_index_internal + 1
            Piece._global_vertex_count += 1

        return self._vertices_hash[vertex_hash][1]

    def get_index(self):
        return self._index

    def get_as_section(self):
        """Gets piece represented with SectionData structure class.
        :return: packed piece as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        # UPDATE COUNTERS
        self._vertex_count = self._streams[Stream.Types.POSITION].get_size()
        self._triangle_count = len(self._triangles)
        self._stream_count = len(self._streams)

        section = _SectionData("Piece")
        section.props.append(("Index", self._index))
        if not self._material or self._material.get_index() == -1:
            lprint("W Piece with index %s doesn't have data about material, expect errors in game!", (self._index,))
            section.props.append(("Material", -1))
        else:
            section.props.append(("Material", self._material.get_index()))
        section.props.append(("VertexCount", self._vertex_count))
        section.props.append(("TriangleCount", self._triangle_count))
        section.props.append(("StreamCount", self._stream_count))

        stream_size = None
        for stream_tag in self._streams:
            stream = self._streams[stream_tag]

            # CHECK SYNC OF STREAMS
            if not stream_size:
                stream_size = stream.get_size()
            elif stream_size != stream.get_size():
                lprint("W Piece with index %s has desynced stream sizes, expect errors in game!", (self._index,))
                break

            # APPEND STREAMS
            section.sections.append(stream.get_as_section())

        # APPEND TRIANGLES
        triangle_section = _SectionData("Triangles")
        for triangle in self._triangles:
            triangle_section.data.append(triangle)

        section.sections.append(triangle_section)

        return section