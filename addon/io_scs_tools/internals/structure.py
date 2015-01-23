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


class SectionData(object):
    """SCS Section data structure (PIX files):
    type (str)\t- Type of the Section (mandatory)\n
    props (list)\t- Properties of the Section (optional)\n
    data (list)\t- Data of the Section (optional)\n
    sections (list)\t- Other Sections within the Section (optional)
    """
    _type_ = "section_data"

    def __init__(self, data_type):
        self.type = data_type
        self.props = []
        self.data = []
        self.sections = []

    def get_prop(self, prop_key):
        for prop in self.props:
            if prop[0] == prop_key:
                return prop
        return None

    def get_section(self, key):
        """Returns firstly found section of given name.

        :param key: Name of the section
        :type key: str
        :return: PIX section data
        :rtype: SectionData
        """
        for section in self.sections:
            if section.type == key:
                return section
        return None

    def get_sections(self, key):
        """Returns a list of sections of given name.

        :param key: Name of the sections
        :type key: str
        :return: list of PIX section data
        :rtype: list of SectionData
        """
        sections = []
        for section in self.sections:
            if section.type == key:
                sections.append(section)
        return sections

    def get_prop_value(self, prop_key):
        prop = self.get_prop(prop_key)
        if prop is not None and len(prop) > 1:
            return prop[1]
        return None


class UnitData(object):
    """Unit data structure (SII files):
    type (str)\t- Type of the Unit (mandatory)\n
    id (str)\t- ID of the Unit (mandatory)\n
    props (dict)\t- Properties of the Unit (optional)
    """
    _type_ = "unit"

    def __init__(self, data_type, data_id):
        self.type = data_type
        self.id = data_id
        self.props = {}
