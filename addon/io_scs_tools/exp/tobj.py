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

import os
from io_scs_tools.internals.containers.tobj import TobjContainer as _TobjContainer
from io_scs_tools.utils.printout import lprint


def export(filepath, texture_name, settings):
    """Exports TOBJ with settings.

    :param filepath: absolute file path with name for TOBJ
    :type filepath: str
    :param texture_name: name of texture file
    :type texture_name: str
    :param settings: settings of texture saved in material.scs_props
    :type settings: set
    :return: True if file was written successfully; False otherwise
    """

    # try to load tobj container from file path
    # to be able to keep all the settings from before
    # and overwrite only what settings we support
    container = None
    if os.path.isfile(filepath):
        container = _TobjContainer.read_data_from_file(filepath)

    # if container for some reason wasn't loaded create new one
    if container is None:
        container = _TobjContainer()
        container.map_type = "2d"
        if texture_name is not None:
            container.map_names.append(texture_name)

    # change settings only on supported 2d texture type
    if container.map_type == "2d":

        # MAP NAMES
        # try to change map names with current texture name
        # otherwise add new value
        if len(container.map_names) > 0:
            container.map_names[0] = texture_name
        elif texture_name is not None:
            container.map_names.append(texture_name)

        # ADDR
        if "u_repeat" in settings:
            addr_u = "repeat"
        else:
            addr_u = "clamp_to_edge"

        if "v_repeat" in settings:
            addr_v = "repeat"
        else:
            addr_v = "clamp_to_edge"

        container.addr.clear()
        container.addr.append(addr_u)
        container.addr.append(addr_v)

        # USAGE
        container.usage = "tsnormal" if "tsnormal" in settings else ""

    else:

        lprint("D Ignoring TOBJ settings save as TOBJ is featuring non 2d map type!")

    return container.write_data_to_file(filepath)
