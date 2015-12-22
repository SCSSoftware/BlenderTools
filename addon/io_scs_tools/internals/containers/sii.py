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
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.containers.parsers import sii as _sii


def get_data_from_file(filepath):
    """Returns entire data in data container from specified SII definition file."""

    container = None
    if filepath:
        if os.path.isfile(filepath):
            container = _sii.parse_file(filepath)
            if container:
                if len(container) < 1:
                    lprint('D SII file "%s" is empty!', (str(filepath).replace("\\", "/"),))
                    return None
            else:
                lprint('D SII file "%s" is empty!', (str(filepath).replace("\\", "/"),))
                return None
        else:
            lprint('W Invalid SII file path %r!', (str(filepath).replace("\\", "/"),))
    else:
        lprint('I No SII file path provided!')

    return container
