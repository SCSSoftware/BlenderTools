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

# Copyright (C) 2015: SCS Software

import re
import os
from io_scs_tools.internals.structure import UnitData as _UnitData
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


class _Token():
    def __init__(self, data_type, value):
        self.type = data_type  # Type (number, id, string, char, eof)
        self.value = value  # Value (1.5, some_name, "ab cd", ;)


class _Tokenizer():
    def __init__(self, data_input, filepath, include_paths):
        self.input = data_input  # Array of input lines
        self.filepath = filepath
        self.current_line = 0  # The currently processed line. If equal to length of input array, we are at end of the input
        self.current_pos = 0  # Character position in the line
        self.active_token = None  # Currently active token
        self.include_paths = include_paths

    def peek_token(self):
        """Returns the active token parsing it if necessary.
        Multiple calls to this function without interleaving consume_token() returns the same token."""
        if self.active_token is None:
            self.active_token = self.parse_token()
            # print(" ** type: %r value: %r" % (str(self.active_token.type), str(self.active_token.value)))
        return self.active_token

    def consume_token(self):
        """Consumes active token, peeking for it if necessary. Returns the consumed token."""
        result = self.peek_token()
        self.active_token = None
        return result

    def consume_token_if_of_type(self, data_type):
        """Consumes active token if it has specified type."""
        if self.peek_token().type != data_type:
            return None
        return self.consume_token()

    def consume_token_if_match(self, data_type, value):
        """Consumes active token if it has specified type and value."""
        if self.peek_token().type != data_type or self.peek_token().value != value:
            return None
        return self.consume_token()

    def parse_token(self):
        """Parses next token from the input."""
        while self.current_line < len(self.input):

            # If we processed entire line, advance to next one.
            line_length = len(self.input[self.current_line])
            if self.current_pos >= line_length:
                self.current_line += 1
                self.current_pos = 0
                continue

            # Unprocessed remainder of the line.
            # line_remainder = str(self.input[self.current_line][self.current_pos:])[2:-1]
            line_remainder = self.input[self.current_line][self.current_pos:]

            # Skip all leading whitespace.
            # print('line_remainder: %s' % str(line_remainder))
            match = re.match('[ \t\n\r]+', line_remainder)
            if match:
                self.current_pos += match.end(0)
                continue

            # Handle includes.
            match = re.match('@include\s+"([^"]+)"', line_remainder)
            if match:

                included_lines = []

                for include_path in self.include_paths:

                    file_name = include_path + match.group(1)

                    if not os.path.isfile(file_name):
                        continue

                    file = open(file_name, mode="r", encoding="utf8")
                    included_lines = file.readlines()
                    file.close()
                    break

                else:

                    lprint("W No included SII file found, ignoring include: %r\n\t   from: %r",
                           (match.group(1), self.filepath))

                new_array = self.input[:self.current_line]
                new_array.extend(included_lines)
                new_array.extend(self.input[self.current_line + 1:])

                self.input = new_array
                self.current_pos = 0
                continue

            # Skip comments up to end of the line.
            if re.match('(#|//).*$', line_remainder):
                self.current_line += 1
                self.current_pos = 0
                continue

            # Is this a identifier?
            match = re.match('\w+', line_remainder)
            if match:
                self.current_pos += match.end(0)
                return _Token('id', line_remainder[0:match.end(0)])

            # Is this a string? Currently does not support escape sequences.
            match = re.match('"([^"]*)"', line_remainder)
            if match:
                self.current_pos += match.end(0)
                return _Token('string', line_remainder[1:match.end(0) - 1])

            # Return the value as character.
            self.current_pos += 1
            return _Token('char', line_remainder[0])

        # Once we get to the end of the stream, always return the 'eof' token
        # even if we are called more than once for some reason.
        return _Token('eof', '')


def _parse_unit_name(tokenizer):
    result = ''

    # Optional leading dot.
    if tokenizer.consume_token_if_match('char', '.'):
        result += '.'

    # At least one component of the name is required.
    next_token = tokenizer.consume_token()
    if next_token.type == 'id':
        result += next_token.value
    else:
        print("Encountered unexpected token %r" % str(next_token.value))
        return None

    # Additional optional dot separated elements.
    while 1:
        if tokenizer.consume_token_if_match('char', '.') is None:
            return result
        result += '.'

        next_token = tokenizer.consume_token()
        if next_token.type == 'id':
            result += next_token.value
        else:
            print("Encountered unexpected token %r" % str(next_token.value))
            return None


def _parse_dot_separated_value(tokenizer):
    result = ''

    # At least one component is required.
    next_token = tokenizer.consume_token()
    if next_token.type == 'id':
        result += next_token.value
    else:
        print("Encountered unexpected token %r" % str(next_token.value))
        return None

    # Additional optional dot separated elements.
    while 1:
        if tokenizer.consume_token_if_match('char', '.') is None:
            return result
        result += '.'

        next_token = tokenizer.consume_token()
        if next_token.type == 'id':
            result += next_token.value
        else:
            print("Encountered unexpected token %r" % str(next_token.value))
            return None


def _parse_property_value(tokenizer):
    next_token = tokenizer.peek_token()
    if next_token.type == 'string':
        tokenizer.consume_token()
        return next_token.value
    elif next_token.type == 'char' and next_token.value == '.':
        return _parse_unit_name(tokenizer)
    elif next_token.type == 'char' and (next_token.value == '-' or next_token.value == '&'):
        tokenizer.consume_token()
        value = _parse_dot_separated_value(tokenizer)
        if value is None:
            return None
        return next_token.value + value
    elif next_token.type == 'id':
        return _parse_dot_separated_value(tokenizer)
    elif next_token.type == 'char' and next_token.value == '(':
        result = []
        tokenizer.consume_token()
        if tokenizer.consume_token_if_match('char', ')'):
            return result

        while 1:
            prefix = tokenizer.consume_token_if_of_type('char')
            if (prefix is not None) and (prefix.value != '-') and (prefix.value != '&'):
                print("Expected '-' or '&'")
                return None

            value = _parse_dot_separated_value(tokenizer)
            if value is None:
                print("Expected value")
                return None

            if prefix is None:
                result.append(value)
            else:
                result.append(prefix.value + value)

            if not tokenizer.consume_token_if_match('char', ','):
                if tokenizer.consume_token_if_match('char', ')'):
                    return result
                else:
                    print("Expected ')'")
                    return None


def _parse_unit_property(tokenizer, unit):
    name = tokenizer.consume_token_if_of_type('id')
    if name is None:
        print("Expected property name")
        return False

    is_array = False
    index = None
    if tokenizer.consume_token_if_match('char', '[') is not None:
        is_array = True
        index = tokenizer.consume_token_if_of_type('id')
        if tokenizer.consume_token_if_match('char', ']') is None:
            print("Expected ']'")
            return False

    if tokenizer.consume_token_if_match('char', ':') is None:
        print("Expected ':'")
        return False

    value = _parse_property_value(tokenizer)
    if value is None:
        print("Property value parsing failed")
        return False

    if not is_array:
        unit.props[name.value] = value
        return True

    value_array = []
    if name.value in unit.props:
        if isinstance(unit.props[name.value], list):
            value_array = unit.props[name.value]
        else:
            for i in range(int(unit.props[name.value], 10)):
                value_array.append(None)
            unit.props[name.value] = value_array
    else:
        unit.props[name.value] = value_array

    if index is None:
        value_array.append(value)
    else:
        index_value = int(index.value, 10)
        while index_value >= len(value_array):
            value_array.append(None)
        value_array[index_value] = value
    return True


def _parse_unit(tokenizer):
    data_type = tokenizer.consume_token_if_of_type('id')
    if data_type is None:
        print("Expected unit type")
        return None
    if tokenizer.consume_token_if_match('char', ':') is None:
        print("Expected ':'")
        return None
    name = _parse_unit_name(tokenizer)
    if name == '':
        print("Unit name parsing failed")
        return None

    unit = _UnitData(data_type.value, name)

    if tokenizer.consume_token_if_match('char', '{') is None:
        print("Expected unit opening bracket")
        return None

    while 1:
        if tokenizer.consume_token_if_match('char', '}') is not None:
            return unit

        if not _parse_unit_property(tokenizer, unit):
            print("Unit property parsing failed")
            return None


def _parse_bare_file(filepath, print_info=False):
    if print_info:
        print("** SII Parser ...")
    unit = _UnitData("", "", is_headless=True)

    file = open(filepath, mode="r", encoding="utf8")
    lines = file.readlines()
    file.close()

    tokenizer = _Tokenizer(lines, filepath, [])

    while 1:
        if tokenizer.consume_token_if_match('eof', '') is not None:
            if print_info:
                print("** Bare SII Parser END")
            return [unit]

        if not _parse_unit_property(tokenizer, unit):
            print("Unit property parsing failed")
            return None


def parse_file(filepath, is_sui=False, print_info=False):
    """
    Reads SCS SII definition file from disk, parse it and return its full content in a form of hierarchical structure.
    """

    if is_sui:
        return _parse_bare_file(filepath, print_info)

    if print_info:
        print("** SII Parser ...")
    sii_container = []

    file = open(filepath, mode="r", encoding="utf8")
    lines = file.readlines()
    file.close()

    # create proper paths for parsing any possible included sii files:
    # 1. is directory of given filepath
    # 2. is directory of current scs project path
    include_paths = [os.path.split(filepath)[0] + os.sep, _get_scs_globals().scs_project_path]

    tokenizer = _Tokenizer(lines, filepath, include_paths)
    if tokenizer.consume_token_if_match('id', 'SiiNunit') is None:
        print("Expected SiiNunit")
        return None
    if tokenizer.consume_token_if_match('char', '{') is None:
        print("Expected opening bracket")
        return None

    while 1:
        if tokenizer.consume_token_if_match('char', '}') is not None:
            if print_info:
                print("** SII Parser END")
            return sii_container

        unit = _parse_unit(tokenizer)
        if unit is None:
            print("Unit parsing failed")
            return None
        sii_container.append(unit)
