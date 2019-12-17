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

# Copyright (C) 2013-2017: SCS Software

import re
from collections import OrderedDict
from io_scs_tools.utils import convert as _convert_utils


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

    def set_prop_value(self, prop_key, value):
        """Set property to given value if exists.

        :param prop_key: string key for property
        :type prop_key: str
        :param value: object which shall be set to property
        :type value: object
        :return: True if property was found, value types matches; False otherwise
        :rtype: bool
        """
        for prop_i, prop in enumerate(self.props):
            if prop[0] == prop_key:

                if isinstance(value, type(prop[1])):
                    self.props[prop_i][1] = value
                    return True
                else:
                    return False

        return False

    def remove_section(self, sec_type, sec_prop, regex_str):
        """Remnoves section if section with given type, given property and given property value regex is found.

        :param sec_type: type of the section we are looking for
        :type sec_type: str
        :param sec_prop: type of property we are searching in section
        :type sec_prop: str
        :param regex_str: regex for matching property value
        :type regex_str: str
        :return: True if removed; False otherwise
        :rtype: bool
        """
        for sec in self.sections:
            if sec.type == sec_type:
                prop = sec.get_prop(sec_prop)
                if prop and re.search(regex_str, prop[1]):
                    self.sections.remove(sec)
                    return True

        return False


class UnitData(object):
    """Unit data structure (SII files):
    type (str)\t- Type of the Unit (mandatory)\n
    id (str)\t- ID of the Unit (mandatory)\n
    props (dict)\t- Properties of the Unit (optional)
    """
    _type_ = "unit"

    def __init__(self, data_type, data_id, is_headless=False):
        self.type = data_type
        self.id = data_id
        self.is_headless = is_headless  # used when exporting SUI to filter out unit header and writing only properties of it
        self.props = OrderedDict()  # use ordered dict just to be able to have order when exporting unit objects

    def get_prop_as_number(self, prop_name):
        """Gets given property as float value. If property is there
        it tries to conver it's value to float.

        :param prop_name: name of property that should hold float value
        :type prop_name: str
        :return: float or int if property exists and can be parsed, none otherwise
        :rtype: float | int | None
        """

        if prop_name not in self.props:
            return None

        prop_value = self.props[prop_name]

        if isinstance(prop_value, list):  # if property is array take first item
            prop_value = prop_value[0]

        if not isinstance(prop_value, str):
            return None

        return _convert_utils.string_to_number(prop_value)

    def get_prop_as_color(self, prop_name):
        """Gets given property as color. If property is there
        it tries to convert it's value of float vector array of length 3.

        :param prop_name: name of the property that should hold color values
        :type prop_name: str
        :return: list of 3 floats if property exists and can be parsed, none otherwise
        :rtype: list[float] | None
        """

        if prop_name not in self.props:
            return None

        prop_value = self.props[prop_name]

        if isinstance(prop_value, list):  # if property is array take first item
            prop_value = prop_value[0]

        if not isinstance(prop_value, list):
            return None

        if not len(prop_value) == 3:
            return None

        for i, key in enumerate(prop_value):
            convert_res = _convert_utils.string_to_number(key)
            prop_value[i] = convert_res

        return prop_value

    def get_prop(self, prop_name, default=None):
        """Gets properety from unit.

        :param prop_name: name of the property we are searching for
        :type prop_name: str
        :param default: default value that should be returned if property not found
        :type default: any
        :return: None if property not found, otherwise object representing it's data
        :rtype:  None | any
        """

        if prop_name not in self.props:
            return default

        return self.props[prop_name]
