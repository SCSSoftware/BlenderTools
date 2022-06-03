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

import os
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.containers.parsers import sii as _sii_reader
from io_scs_tools.internals.containers.writers import sii as _sii_writer


def get_data_from_file(filepath, is_sui=False):
    """Returns entire data in data container from specified SII definition file.

    :param filepath: absolute file path where SII should be read from
    :type filepath: str
    :param is_sui: True if file should be read as SUI, in that case only one unit will be returned
    :type is_sui: bool
    :return: list of SII Units if parsing succeded; otherwise None
    :rtype: list[io_scs_tools.internals.structure.UnitData] | None
    """

    container = None
    if filepath:
        if os.path.isfile(filepath):
            container = _sii_reader.parse_file(filepath, is_sui=is_sui)
            if container:
                if len(container) < 1:
                    lprint('D SII file "%s" is empty!', (_path_utils.readable_norm(filepath),))
                    return None
            else:
                lprint('D SII file "%s" is empty!', (_path_utils.readable_norm(filepath),))
                return None
        else:
            lprint('W Invalid SII file path %r!', (_path_utils.readable_norm(filepath),))
    else:
        lprint('I No SII file path provided!')

    return container


def write_data_to_file(filepath, container, is_sui=False, create_dirs=False):
    """Write given unit data container into SII file.

    :param filepath: absolute file path where SII should be written to
    :type filepath: str
    :param container: iterable of unit data objects to be written
    :type container: tuple[io_scs_tools.internals.structure.UnitData]|list[io_scs_tools.internals.structure.UnitData]
    :param is_sui: True if unit should be written as SUI, meaning without SiiNunit header
    :type is_sui: bool
    :param create_dirs: True if directories should be created before export
    :type create_dirs: bool
    :return: True if container was successfully written; otherwise False
    :rtype: bool
    """

    file_type = "SUI" if is_sui else "SII"

    if filepath:
        if container:
            return _sii_writer.write_data(filepath, container, is_sui=is_sui, create_dirs=create_dirs)
        else:
            lprint("W Empty %s container, abort file write: %r!", (file_type, _path_utils.readable_norm(filepath),))
    else:
        lprint('I No %s file path provided!', (file_type,))

    return False


def has_valid_unit_instance(container, unit_type, req_props=tuple(), one_of_props=tuple(), unit_instance=0):
    """Valides unit instance with given unit type, required properties and one of properties lists.

    :param container: container as list of unit instances
    :type container: list[io_scs_tools.internals.structure.UnitData]
    :param unit_type: type of the unit we are validating represented in string
    :type unit_type: str
    :param req_props: required properties that has to be inside unit instance to be valid
    :type req_props: iterable
    :param one_of_props: one of properties from this list has to be inside unit instance to be valid
    :type one_of_props: iterable
    :param unit_instance: index of unit instance in container list that we are validating
    :type unit_instance: int
    :return: True if valid; False otherwise
    :rtype: bool
    """

    if container is None:
        lprint("D Validation failed: None SII container!")
        return False

    # there should be only one unit instance inside file
    if len(container) < unit_instance + 1:
        lprint("D Validation failed: Not enough unit instances!")
        return False

    # invalid unit type
    if unit_type != "" and container[unit_instance].type != unit_type:
        lprint("D Validation failed: Invalid unit instance type (wanted: %r actual: %r)!", (unit_type, container[unit_instance].type))
        return False

    for prop in req_props:
        if prop not in container[unit_instance].props:
            lprint("D Validation failed: Required prop %r not found!", (prop,))
            return False

    one_of_props_found = False
    for prop in one_of_props:
        if prop in container[unit_instance].props:
            one_of_props_found = True
            break

    if not one_of_props_found and len(one_of_props) > 0:
        lprint("D Validation failed: None property found from one of: %r!", (one_of_props,))
        return False

    return True


def get_unit_property(container, prop, unit_instance=0):
    """Gets property value from unit instance.
    NOTE: No validation is done if unit instance exists in container,
    so make sure to use validation function before.

    :param container: container as list of unit instances
    :type container: list[io_scs_tools.internals.structure.UnitData]
    :param prop: name of the property we are looking for
    :type prop: str
    :param unit_instance: index of unit instance in container list that we are validating
    :type unit_instance: int
    :return: None if property is not found insde unit instance; otherwise value of the property
    :rtype: None|any
    """

    value = None

    if prop in container[unit_instance].props:
        value = container[unit_instance].props[prop]

    return value


def get_direct_unit_property(unit, prop):
    """Gets property value from unit instance.
    NOTE: No validation is done if unit instance exists in container,
    so make sure to use validation function before.

    :param unit: container as list of unit instances
    :type unit: io_scs_tools.internals.structure.UnitData
    :param prop: name of the property we are looking for
    :type prop: str
    :return: None if property is not found insde unit instance; otherwise value of the property
    :rtype: None|any
    """

    value = None

    if prop in unit.props:
        value = unit.props[prop]

    return value


def get_unit_by_id(container, unit_id, unit_type):
    """Gets first found unit instance from container with given id and type.

    :param container: container as list of unit instances
    :type container: list[io_scs_tools.internals.structure.UnitData]
    :param unit_id: id of the unit we are searching for eg ".truck.cabin"
    :type unit_id: str
    :param unit_type: type of the unit representing it's class name we are searching for
    :type unit_type: str
    :return: None if unit is not found; otherwise unit data representation of it's content
    :rtype: None|io_scs_tools.internals.structure.UnitData
    """
    unit = None

    for unit_instance in range(0, len(container)):

        if container[unit_instance].type != unit_type:
            continue

        if container[unit_instance].id != unit_id:
            continue

        unit = container[unit_instance]
        break

    return unit
