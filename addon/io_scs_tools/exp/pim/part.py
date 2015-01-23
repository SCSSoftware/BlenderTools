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


class Part:
    _name = ""
    _piece_count = 0
    _locator_count = 0

    _pieces = {}  # references to Piece classes used in this part
    _locators = {}  # references to Locator classes used in this part

    _global_part_counter = 0

    @staticmethod
    def reset_counter():
        Part._global_part_counter = 0

    @staticmethod
    def get_global_material_count():
        return Part._global_part_counter

    def __init__(self, name):
        """Constructor for part with it's name.
        NOTE: all of the pieces and locators are added later with methods.
        :param name: name of the part
        :type name: str
        """
        self._pieces = {}
        self._locators = {}

        self._name = name
        Part._global_part_counter += 1

    def add_piece(self, piece):
        """Adds piece to part.
        NOTE: if piece is already in it won't be added

        :param piece: piece that should be in part
        :type piece: io_scs_tools.exp.pim.piece.Piece
        :return: True if piece was added; False otherwise
        :rtype: bool
        """
        if piece.get_index() in self._pieces:
            return False

        self._pieces[piece.get_index()] = piece
        return True

    def add_locator(self, locator):
        """Adds locator to part.
        NOTE: if locator is already in it won't be added
        :param locator: locator that should be in part
        :type locator: io_scs_tools.exp.pim.locator.Locator
        :return: True if locator was added; False otherwise
        :rtype: bool
        """
        if locator.get_index() in self._locators:
            return False

        self._locators[locator.get_index()] = locator
        return True

    def get_as_section(self):
        """Gets part represented with SectionData structure class.
        :return: packed part as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        # update counters first
        self._piece_count = len(self._pieces)
        self._locator_count = len(self._locators)

        section = _SectionData("Part")
        section.props.append(("Name", self._name))
        section.props.append(("PieceCount", self._piece_count))
        section.props.append(("LocatorCount", self._locator_count))
        if self._piece_count == 0:
            section.props.append(("Pieces", None))
        else:
            section.props.append(("Pieces", list(self._pieces.keys())))
        if self._locator_count == 0:
            section.props.append(("Locators", None))
        else:
            section.props.append(("Locators", list(self._locators.keys())))

        return section

