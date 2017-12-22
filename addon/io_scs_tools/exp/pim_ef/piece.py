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
from io_scs_tools.exp.pim_ef.piece_stream import Stream
from io_scs_tools.exp.pim_ef.piece_face import Face
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.utils.printout import lprint


class Piece:
    __index = 0
    __vertex_count = 0
    __face_count = 0
    __stream_count = 0

    __material = None  # save whole material reference to get index out of it when packing
    __streams = OrderedDict()  # dict of Stream class
    __faces = []  # list of Triangle class

    __vertices_hash = {}
    __vert_i_to_internal = {}

    __global_piece_count = 0
    __global_vertex_count = 0
    __global_face_count = 0

    @staticmethod
    def reset_counters():
        Piece.__global_piece_count = 0
        Piece.__global_face_count = 0
        Piece.__global_vertex_count = 0

    @staticmethod
    def get_global_piece_count():
        return Piece.__global_piece_count

    @staticmethod
    def get_global_vertex_count():
        return Piece.__global_vertex_count

    @staticmethod
    def get_global_face_count():
        return Piece.__global_face_count

    @staticmethod
    def __calc_vertex_hash(index, position):
        """Calculates vertex hash from original vertex index, uvs components and vertex color.
        :param index: original index from Blender mesh
        :type index: int
        :param position: vector of 3 floats presenting vertex position in SCS values
        :type position: tuple | mathutils.Vector
        :return: calculated vertex hash
        :rtype: str
        """

        frmt = "%.4f"

        vertex_hash = str(index)

        vertex_hash += frmt % position[0] + frmt % position[1] + frmt % position[2]

        return vertex_hash

    def __init__(self, index):
        """Constructs empty piece.
        NOTE: empty piece will contain mandatory stream which will be empty: POSITION
        :param index:
        :type index:
        """
        self.__vertex_count = 0
        self.__face_count = 0
        self.__edge_count = 0
        self.__stream_count = 0
        self.__streams = OrderedDict()
        self.__faces = []
        """:type: list[Face]"""
        self.__edges = []
        self.__vertices_hash = {}
        self.__vert_i_to_internal = {}

        self.__index = index

        # CONSTRUCT ALL MANDATORY STREAMS
        stream = Stream(Stream.Types.POSITION, -1)
        self.__streams[Stream.Types.POSITION] = stream

        Piece.__global_piece_count += 1

    def add_face(self, material, vert_indicies, vert_normals, vert_uvs, uvs_names, uvs_aliases, vert_rgbas, rgbas_names):
        """Adds new face to piece.

        :param material: material that should be used on for this piece
        :type material: io_scs_tools.exp.pim.material.Material
        :param vert_indicies: tuple of integers representing vertex indices
        :type vert_indicies: list[int] | tuple[int]
        :param vert_normals: tuple of float vectors representing vertex normals
        :type vert_normals: list[mathutils.Vector] | tuple[mathutils.Vector]
        :param vert_uvs: tuple of list of uvs used on vertex (each uv must be in SCS coordinates)
        :type vert_uvs: list[tuple] | tuple[tuple]
        :param uvs_names: tuple or list of uv layer names used on vertex
        :type uvs_names: list[str] | tuple[str]
        :param uvs_aliases: list of strings for uv aliases
        :type uvs_aliases: list[str] | tuple[str]
        :param vert_rgbas: list of rgba vertex colors in SCS values
        :type vert_rgbas: list[tuple | mathutils.Color] | tuple[tuple | mathutils.Color]
        :param rgbas_names: tuple or list of vertex color layer names used on vertex
        :type rgbas_names: list[str] | tuple[str]
        :return: True if added; False otherwise
        :rtype: bool
        """

        if len(vert_indicies) < 3:
            return False

        # check indices integrity
        for vertex in vert_indicies:
            if vertex < 0 or vertex >= self.__vertex_count:
                return False

        # check integrity between all parameters
        if not len(vert_indicies) == len(vert_normals) == len(vert_uvs) == len(vert_rgbas):
            return False

        face = Face(len(self.__faces), material, vert_indicies)

        for i in range(0, len(vert_indicies)):

            # add normal per vertex
            face.add_normal(vert_normals[i])

            # add uvs per vertex
            face.add_uvs(vert_uvs[i], uvs_names, uvs_aliases)

            # add rgbas per vertex
            face.add_rgbas(vert_rgbas[i], rgbas_names)

        self.__faces.append(face)
        Piece.__global_face_count += 1

        return True

    def add_edge(self, vert1_index, vert2_index, blender_mesh_indices=False):
        """Adds new edge to hard edge list. Indices are parsed depending on control parameter,
        either directly as internal indices or as indices of vertices from Blender mesh.

        :param vert1_index: index of first vertex
        :type vert1_index: int
        :param vert2_index: index of second vertex
        :type vert2_index: int
        :param blender_mesh_indices: True if indices should be treated as Blender mesh indices; False otherwise
        :type blender_mesh_indices: bool
        :return: True if added; False otherwise
        :rtype: bool
        """

        if blender_mesh_indices:

            # check indices integrity
            if vert1_index not in self.__vert_i_to_internal or vert2_index not in self.__vert_i_to_internal:
                return False

            self.__edges.append((self.__vert_i_to_internal[vert1_index], self.__vert_i_to_internal[vert2_index]))
            return True

        else:

            # check indices integrity
            for vertex in (vert1_index, vert2_index):
                if vertex < 0 or vertex >= self.__vertex_count:
                    return False

            self.__edges.append((vert1_index, vert2_index))
            return True

    def add_vertex(self, vert_index, position):
        """Adds new vertex with position.

        :param vert_index: original vertex index from Blender mesh
        :type vert_index: int
        :param position: vector or tuple of vertex position in SCS coordinates
        :type position: tuple | mathutils.Vector
        :return: vertex index inside piece streams ( use it for adding triangles )
        :rtype: int
        """

        vertex_hash = self.__calc_vertex_hash(vert_index, position)

        # save vertex if the vertex with the same properties doesn't exists yet in streams
        if vertex_hash not in self.__vertices_hash:

            stream = self.__streams[Stream.Types.POSITION]
            stream.add_entry(position)

            vert_index_internal = stream.get_size() - 1  # streams has to be aligned so I can take last one for the index
            self.__vertices_hash[vertex_hash] = (vert_index, vert_index_internal)
            self.__vert_i_to_internal[vert_index] = vert_index_internal

            self.__vertex_count = vert_index_internal + 1
            Piece.__global_vertex_count += 1

        return self.__vertices_hash[vertex_hash][1]

    def get_index(self):
        return self.__index

    def get_as_section(self):
        """Gets piece represented with SectionData structure class.

        :return: packed piece as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        # UPDATE COUNTERS
        self.__vertex_count = self.__streams[Stream.Types.POSITION].get_size()
        self.__face_count = len(self.__faces)
        self.__edge_count = len(self.__edges)
        self.__stream_count = len(self.__streams)

        section = _SectionData("Piece")
        section.props.append(("Index", self.__index))
        section.props.append(("VertexCount", self.__vertex_count))
        section.props.append(("FaceCount", self.__face_count))
        section.props.append(("EdgeCount", self.__edge_count))
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

        # APPEND FACES
        faces_section = _SectionData("Faces")
        faces_section.props.append(("StreamCount", self.__faces[0].get_stream_count()))

        for face in self.__faces:
            faces_section.sections.append(face.get_as_section())

        section.sections.append(faces_section)

        # APPEND (HARD) EDGES
        edges_section = _SectionData("Edges")
        for edge in self.__edges:
            edges_section.data.append(edge)

        section.sections.append(edges_section)

        return section
