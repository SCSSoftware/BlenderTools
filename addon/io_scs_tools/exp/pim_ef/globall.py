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

# Copyright (C) 2017-2019: SCS Software

from io_scs_tools.exp.pim_ef.piece import Piece
from io_scs_tools.exp.pim.material import Material
from io_scs_tools.exp.pim.locator import Locator
from io_scs_tools.exp.pim.bones import Bones
from io_scs_tools.exp.pim.piece_skin import PieceSkin
from io_scs_tools.internals.structure import SectionData as _SectionData


class Globall:
    __skeleton = ""

    def __init__(self, part_count, skeleton):
        """Constructs global for PIM
        :param part_count: parts counter for current game object (including any parts from PIC and PIT
        :type part_count: int
        :param skeleton: file name of the skeleton file
        :type skeleton: str
        """

        Piece.reset_counters()
        Material.reset_counter()
        Locator.reset_counter()
        Bones.reset_counter()
        PieceSkin.reset_counter()

        self.__part_count = part_count
        self.__skeleton = skeleton.replace("\\", "/")  # make sure to replace backslashes for windows paths

    def get_as_section(self):
        """Gets global model information represented with SectionData structure class.
        :return: packed globals as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Global")
        section.props.append(("VertexCount", Piece.get_global_vertex_count()))
        section.props.append(("FaceCount", Piece.get_global_face_count()))
        section.props.append(("MaterialCount", Material.get_global_material_count()))
        section.props.append(("PieceCount", Piece.get_global_piece_count()))
        section.props.append(("PartCount", self.__part_count))
        section.props.append(("BoneCount", Bones.get_global_bones_count()))
        section.props.append(("LocatorCount", Locator.get_global_locator_count()))
        section.props.append(("Skeleton", self.__skeleton))
        section.props.append(("PieceSkinCount", PieceSkin.get_global_piece_skin_count()))

        return section
