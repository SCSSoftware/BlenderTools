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

import os
from io_scs_tools.utils.printout import lprint


def _write_raw_value(f, value):
    """Write raw basic type value to file object.

    :param f: file object to write to
    :type f: io.TextIOWrapper
    :param value: value to write
    :type value: str|float|int|bool
    """

    if isinstance(value, str):  # FIXME: distinguish between string and pointer
        f.write("\"%s\"" % value)
    elif isinstance(value, float):
        f.write("%.6f" % value)
    elif isinstance(value, bool):  # has to be before int otherwise isinstance for integer eats it
        f.write("%s" % str(value).lower())
    elif isinstance(value, int):
        f.write("%s" % value)
    else:
        raise TypeError("None expected type for SII property value! Shouldn't happen...")


def _write_property_value(f, item):
    """Write property value of the unit. Property can also be tuple of mupltiple basic values eg. three floats.

    :param f: file object to write to
    :type f: io.TextIOWrapper
    :param item: value of the property that can be also tuple of multiple basic types
    :type item: tuple|str|float|int|bool
    """

    if isinstance(item, tuple):

        f.write("(")
        count = len(item)
        for i, value in enumerate(item):
            _write_raw_value(f, value)

            if i < count - 1:
                f.write(", ")

        f.write(")")

    else:

        _write_raw_value(f, item)

    f.write("\n")


def _write_unit(f, unit, ind):
    """Write given unit object to file.

    :param f: file object to write to
    :type f: io.TextIOWrapper
    :param unit: unit from container to be written
    :type unit: io_scs_tools.internals.structure.UnitData
    :param ind: indentation for the properties of unit
    :type ind: str
    """

    if not unit.is_headless:
        f.write("%s : %s\n" % (unit.type, unit.id))
        f.write("{\n")

    for prop in unit.props:

        prop_data = unit.props[prop]

        if isinstance(prop_data, list):

            for item in prop_data:

                f.write("%s%s[]: " % (ind, prop))
                _write_property_value(f, item)

        elif isinstance(prop_data, tuple):

            f.write("%s%s: " % (ind, prop))
            _write_property_value(f, prop_data)

        elif isinstance(prop_data, str):

            # treat differently include directive
            if prop.startswith("@include"):
                f.write("@include ")
            else:
                f.write("%s%s: " % (ind, prop))

            _write_property_value(f, prop_data)

        elif isinstance(prop_data, (float, bool, int, str)):

            f.write("%s%s: " % (ind, prop))
            _write_property_value(f, prop_data)

        else:

            raise TypeError("Unable to write unit property of type %s. Shouldn't happen..." % type(prop_data))

    if not unit.is_headless:
        f.write("}\n")


def write_data(filepath, container, ind="\t", is_sui=False, create_dirs=False, print_on_success=True):
    """Write SII container into sii file onto given filepath. Addditonally user can select either
    directores should be first created.

    :param filepath: absolute file path where SII should be written to
    :type filepath: str
    :param container: iterable of unit data objects to be written
    :type container: tuple[io_scs_tools.internals.structure.UnitData]|list[io_scs_tools.internals.structure.UnitData]
    :param ind: indentation used for properties of units
    :type ind: str
    :param is_sui: True if unit should be written as SUI, meaning without SiiNunit header
    :type is_sui: bool
    :param create_dirs: True if directores should be created before writting a file, otherwise False
    :type create_dirs: bool
    :param print_on_success: print where file was printed
    :type print_on_success: bool
    :return: True if data were written; False otherwise
    :rtype: bool
    """

    if create_dirs:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, mode="w", encoding="utf8", newline="\r\n") as f:

        if not is_sui:
            f.write("SiiNunit\n")
            f.write("{\n")

        count = len(container)
        for i, unit in enumerate(container):
            _write_unit(f, unit, ind)

            if i < count - 1:
                f.write("\n")

        if not is_sui:
            f.write("}\n")

    if print_on_success:
        file_type = "SUI" if is_sui else "SII"
        lprint("I WRITTING %s FILE to: %r", (file_type, filepath))

    return True
