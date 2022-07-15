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

# Copyright (C) 2013-2022: SCS Software

from collections import OrderedDict
from io_scs_tools.exp.pim.piece_stream import Stream
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class Piece:
    __index = 0
    __vertex_count = 0
    __triangle_count = 0
    __stream_count = 0

    __material = None  # save whole material reference to get index out of it when packing
    __streams = OrderedDict()  # dict of Stream class
    __triangles = []  # list of Triangle class

    __vertices_hash = {}

    __global_piece_count = 0
    __global_vertex_count = 0
    __global_triangle_count = 0

    @staticmethod
    def reset_counters():
        Piece.__global_piece_count = 0
        Piece.__global_triangle_count = 0
        Piece.__global_vertex_count = 0

    @staticmethod
    def get_global_piece_count():
        return Piece.__global_piece_count

    @staticmethod
    def get_global_vertex_count():
        return Piece.__global_vertex_count

    @staticmethod
    def get_global_triangle_count():
        return Piece.__global_triangle_count

    @staticmethod
    def __calc_vertex_hash(index, normal, uvs, rgba, tangent):
        """Calculates vertex hash from original vertex index, uvs components and vertex color.
        :param index: original index from Blender mesh
        :type index: str
        :param normal: normalized vector representation of the normal
        :type normal: tuple | mathutils.Vector
        :param uvs: list of uvs used on vertex (each uv must be in SCS coordinates)
        :type uvs: list of (tuple | mathutils.Vector)
        :param rgba: rgba representation of vertex color in SCS values
        :type rgba: tuple | mathutils.Color
        :param tangent: vertex tangent in SCS coordinates or none, if piece doesn't have tangents
        :type tangent: tuple | None
        :return: calculated vertex hash
        :rtype: str
        """
        fprec = 10 * 4

        if tangent:
            vertex_hash = (index,
                           int(normal[0] * fprec),
                           int(normal[1] * fprec),
                           int(normal[2] * fprec),
                           int(rgba[0] * fprec),
                           int(rgba[1] * fprec),
                           int(rgba[2] * fprec),
                           int(rgba[3] * fprec),
                           int(tangent[0] * fprec),
                           int(tangent[1] * fprec),
                           int(tangent[2] * fprec),
                           int(tangent[3] * fprec))
        else:
            vertex_hash = (index,
                           int(normal[0] * fprec),
                           int(normal[1] * fprec),
                           int(normal[2] * fprec),
                           int(rgba[0] * fprec),
                           int(rgba[1] * fprec),
                           int(rgba[2] * fprec),
                           int(rgba[3] * fprec))

        for uv in uvs:
            vertex_hash += (int(uv[0] * fprec),
                            int(uv[1] * fprec))

        return vertex_hash

    def __init__(self, index, material):
        """Constructs empty piece.
        NOTE: empty piece will contain for mandatory stream which will be empty: POSITION, NORMAL, UV0, RGBA
        :param index:
        :type index:
        :param material: material that should be used on for this piece
        :type material: io_scs_tools.exp.pim.material.Material
        """
        self.__vertex_count = 0
        self.__triangle_count = 0
        self.__stream_count = 0
        self.__streams = OrderedDict()
        self.__triangles = []
        self.__vertices_hash = {}

        self.__index = index
        self.__material = material

        # CONSTRUCT ALL MANDATORY STREAMS
        stream = Stream(Stream.Types.POSITION, -1)
        self.__streams[Stream.Types.POSITION] = stream

        stream = Stream(Stream.Types.NORMAL, -1)
        self.__streams[Stream.Types.NORMAL] = stream

        Piece.__global_piece_count += 1

    def add_triangle(self, triangle):
        """Adds new triangle to piece
        NOTE: if length of given triangle iterable is different than 3 it will be refused!
        :param triangle: tuple of 3 integers representing vertex indices
        :type triangle: tuple
        :return: True if added; False otherwise
        :rtype:
        """

        # expensive safety checks not needed for release but keep them for debug purposes
        # if len(triangle) != 3:
        #     return False

        # check indecies integrity
        for vertex in triangle:
            if vertex < 0 or vertex >= self.__vertex_count:
                return False

        self.__triangles.append(tuple(triangle))
        Piece.__global_triangle_count += 1

        return True

    def add_vertex(self, vert_index, position, normal, uvs, uvs_aliases, rgba, tangent):
        """Adds new vertex to position and normal streams
        :param vert_index: original vertex index from Blender mesh
        :type vert_index: str
        :param position: vector or tuple of vertex position in SCS coordinates
        :type position: tuple | mathutils.Vector
        :param normal: vector or tuple of vertex normal in SCS coordinates
        :type normal: tuple | mathutils.Vector
        :param uvs: list of uvs used on vertex (each uv must be in SCS coordinates)
        :type uvs: list of (tuple | mathutils.Vector)
        :param uvs_aliases: list of uv aliases names per uv layer
        :type uvs_aliases: list[list[str]]
        :param rgba: rgba representation of vertex color in SCS values
        :type rgba: tuple | mathutils.Color
        :param tangent: tuple representation of vertex tangent in SCS values or None if piece doesn't have tangents
        :type tangent: tuple | None
        :return: vertex index inside piece streams ( use it for adding triangles )
        :rtype: int
        """

        vertex_hash = self.__calc_vertex_hash(vert_index, normal, uvs, rgba, tangent)

        # save vertex if the vertex with the same properties doesn't exists yet in streams
        if vertex_hash not in self.__vertices_hash:

            stream = self.__streams[Stream.Types.POSITION]
            stream.add_entry(position)

            stream = self.__streams[Stream.Types.NORMAL]
            stream.add_entry(normal)

            for i, uv in enumerate(uvs):
                uv_type = "%s%i" % (Stream.Types.UV, i)
                # create more uv streams on demand
                if uv_type not in self.__streams:
                    self.__streams[uv_type] = Stream(Stream.Types.UV, i)

                stream = self.__streams[uv_type]
                """:type: Stream"""
                stream.add_entry(uv)

                for alias in uvs_aliases[i]:
                    stream.add_alias(alias)

            if tangent:
                # create tangent stream on demand
                if Stream.Types.TANGENT not in self.__streams:
                    self.__streams[Stream.Types.TANGENT] = Stream(Stream.Types.TANGENT, -1)

                stream = self.__streams[Stream.Types.TANGENT]
                stream.add_entry(tangent)

            if Stream.Types.RGBA not in self.__streams:
                self.__streams[Stream.Types.RGBA] = Stream(Stream.Types.RGBA, -1)

            stream = self.__streams[Stream.Types.RGBA]
            stream.add_entry(rgba)

            vert_index_internal = stream.get_size() - 1  # streams has to be alligned so I can take last one for the index
            self.__vertices_hash[vertex_hash] = vert_index_internal

            self.__vertex_count = vert_index_internal + 1
            Piece.__global_vertex_count += 1

        return self.__vertices_hash[vertex_hash]

    def get_index(self):
        return self.__index

    def get_vertex_count(self):
        return self.__streams[Stream.Types.POSITION].get_size()

    def get_as_section(self):
        """Gets piece represented with SectionData structure class.
        :return: packed piece as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        # UPDATE COUNTERS
        self.__vertex_count = self.__streams[Stream.Types.POSITION].get_size()
        self.__triangle_count = len(self.__triangles)
        self.__stream_count = len(self.__streams)

        section = _SectionData("Piece")
        section.props.append(("Index", self.__index))
        if not self.__material or self.__material.get_index() == -1:
            lprint("W Piece with index %s doesn't have data about material, expect errors in game!", (self.__index,))
            section.props.append(("Material", -1))
        else:
            section.props.append(("Material", self.__material.get_index()))
        section.props.append(("VertexCount", self.__vertex_count))
        section.props.append(("TriangleCount", self.__triangle_count))
        section.props.append(("StreamCount", self.__stream_count))

        stream_size = None
        for stream_tag in self.__streams:
            stream = self.__streams[stream_tag]

            # CHECK SYNC OF STREAMS
            if not stream_size:
                stream_size = stream.get_size()
            elif stream_size != stream.get_size():
                lprint("W Piece with index %s has desynced stream sizes, expect errors in game!", (self.__index,))
                break

            # APPEND STREAMS
            section.sections.append(stream.get_as_section())

        # APPEND TRIANGLES
        triangle_section = _SectionData("Triangles")
        triangle_section.data = self.__triangles

        section.sections.append(triangle_section)

        return section
