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

import bpy
from mathutils import Matrix
from io_scs_tools.utils.info import get_tools_version as _get_tools_version
from io_scs_tools.utils.info import get_blender_version as _get_blender_version
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container


def _fill_header_section(file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 1))
    blender_version, blender_build = _get_blender_version()
    section.props.append(("Source", "Blender " + blender_version + blender_build + ", PIS Exporter: " + str(_get_tools_version())))
    section.props.append(("Type", "Skeleton"))
    # section.props.append(("Name", str(os.path.basename(bpy.data.filepath)[:-6])))
    section.props.append(("Name", file_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(bone_cnt):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("BoneCount", bone_cnt))
    return section


def _fill_bones_sections(bones, export_scale):
    """Creates "Bones" section."""
    section = _SectionData("Bones")
    for bone_i, bone in enumerate(bones):
        bone_mat = (Matrix.Scale(export_scale, 4) * _convert_utils.scs_to_blend_matrix().inverted() * bone.matrix_local).transposed()
        section.data.append(("__bone__", bone.name, bone.parent, bone_mat))
    return section


def export(bone_list, filepath, filename):
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIS Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    # bone_list = []

    # BONES...
    # TODO: SORT "bone_list"...

    # DATA CREATION
    header_section = _fill_header_section(filename, scs_globals.sign_export)
    bones_section = _fill_bones_sections(bone_list, scs_globals.export_scale)
    global_section = _fill_global_section(len(bone_list))

    # DATA ASSEMBLING
    pis_container = [header_section, global_section, bones_section]

    # FILE EXPORT
    ind = "    "
    pis_filepath = str(filepath + ".pis")
    result = _pix_container.write_data_to_file(pis_container, pis_filepath, ind)

    # print("************************************")
    return result