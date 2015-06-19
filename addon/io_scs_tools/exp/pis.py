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
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container


def _fill_header_section(file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 1))
    section.props.append(("Source", get_combined_ver_str()))
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


def _fill_bones_sections(scs_root_obj, armature_obj, used_bones, export_scale):
    """Creates "Bones" section."""
    section = _SectionData("Bones")
    for bone_name in used_bones:
        bone = armature_obj.data.bones[bone_name]

        # armature matrix stores transformation of armature object against scs root
        # and has to be added to all bones as they only armature space transformations
        armature_mat = scs_root_obj.matrix_world.inverted() * armature_obj.matrix_world

        bone_mat = (Matrix.Scale(export_scale, 4) * _convert_utils.scs_to_blend_matrix().inverted() *
                    armature_mat * bone.matrix_local)
        section.data.append(("__bone__", bone.name, bone.parent, bone_mat.transposed()))
    return section


def export(filepath, scs_root_obj, armature_object, used_bones):
    print("\n************************************")
    print("**      SCS PIS Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    scs_globals = _get_scs_globals()

    # DATA CREATION
    header_section = _fill_header_section(scs_root_obj.name, scs_globals.sign_export)
    bones_section = _fill_bones_sections(scs_root_obj, armature_object, used_bones, scs_globals.export_scale)
    global_section = _fill_global_section(len(used_bones))

    # DATA ASSEMBLING
    pis_container = [header_section, global_section, bones_section]

    # FILE EXPORT
    ind = "    "
    result = _pix_container.write_data_to_file(pis_container, filepath, ind)

    # print("************************************")
    return result
