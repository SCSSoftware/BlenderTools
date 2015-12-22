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
import bpy
from mathutils import Vector
from io_scs_tools.consts import Bones as _BONE_consts
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.containers import pix as _pix_container


def _get_header(pis_container):
    """Receives PIS container and returns all its Header properties in its own variables.
    For any item that fails to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pis_container:
        if section.type == "Header":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "FormatVersion":
                    format_version = prop[1]
                elif prop[0] == "Source":
                    source = prop[1]
                elif prop[0] == "Type":
                    f_type = prop[1]
                elif prop[0] == "Name":
                    f_name = prop[1]
                elif prop[0] == "SourceFilename":
                    source_filename = prop[1]
                elif prop[0] == "Author":
                    author = prop[1]
                else:
                    lprint('\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, f_name, source_filename, author


def _get_global(pis_container):
    """Receives PIS container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    bone_count = None
    for section in pis_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "BoneCount":
                    bone_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return bone_count


def _get_bones(pis_container):
    """Receives a Bones section and returns its data in a dictionary:
    bones[bone_name] = (bone_parent, bone_matrix)"""
    bones = {}
    for section in pis_container:
        if section.type == "Bones":
            for data_rec in section.data:
                bones[data_rec['name']] = [data_rec['parent'], data_rec['matrix']]
                # print('data_rec: %s' % str(data_rec))
    return bones


def load(filepath, armature, get_only=False):
    scs_globals = _get_scs_globals()
    import_scale = scs_globals.import_scale
    bone_import_scale = scs_globals.bone_import_scale
    connected_bones = scs_globals.connected_bones

    print("\n************************************")
    print("**      SCS PIS Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # scene = context.scene
    ind = '    '
    pis_container = _pix_container.get_data_from_file(filepath, ind)

    # TEST PRINTOUTS
    # ind = '  '
    # for section in pis_container:
    # print('SEC.: "%s"' % section.type)
    # for prop in section.props:
    # print('%sProp: %s' % (ind, prop))
    # for data in section.data:
    # print('%sdata: %s' % (ind, data))
    # for sec in section.sections:
    # print_section(sec, ind)
    # print('\nTEST - Source: "%s"' % pis_container[0].props[1][1])
    # print('')

    # TEST EXPORT
    # path, file = os.path.splitext(filepath)
    # export_filepath = str(path + '_reex' + file)
    # result = pix_write.write_data(pis_container, export_filepath, ind)
    # if result == {'FINISHED'}:
    # Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
    # else:
    # Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)

    # LOAD HEADER
    '''
    NOTE: skipped for now as no data needs to be readed
    format_version, source, f_type, f_name, source_filename, author = _get_header(pis_container)
    '''

    # LOAD GLOBALS
    '''
    NOTE: skipped for now as no data needs to be readed
    # bone_count = _get_global(pis_container)
    '''

    # LOAD BONES
    bones = _get_bones(pis_container)

    if get_only:  # only return bones (used when importing PIA from panel)
        return bones

    # PROVIDE AN ARMATURE
    if not armature:
        lprint('\nE No Armature for file "%s"!', (os.path.basename(filepath),))
        return {'CANCELLED'}, None

    bpy.context.scene.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # CONNECTED BONES - Add information about all children...
    if connected_bones:
        for bone in bones:
            # print('  bone: %r - %r\n%s\n' % (bone, bones[bone][0], str(bones[bone][1])))
            children = []
            for item in bones:
                if bone == bones[item][0]:
                    children.append(item)
            bones[bone].append(children)
            # print('  bone: %r - %r\n%s\n' % (bone, bones[bone][0], str(bones[bone][2])))

    for bone_i, bone in enumerate(armature.data.bones):
        # print('----- bone: %r ------------------------------' % bone.name)

        # SET PARENT
        if bones[bone.name][0] != "":  # if bone has parent...
            # print('  %r --> %r' % (bone.name, bones[bone.name][0]))
            # armature.data.edit_bones[bone.name].use_connect = False
            armature.data.edit_bones[bone.name].parent = armature.data.edit_bones[bones[bone.name][0]]
            # else:
            # print('  %r - NO parent' % bone.name)

        # COMPUTE BONE TRANSFORMATION
        matrix = bones[bone.name][1]
        bone_matrix = _convert_utils.scs_to_blend_matrix() * matrix.transposed()
        axis, angle = _convert_utils.mat3_to_vec_roll(bone_matrix)
        # print(' * %r - angle: %s' % (bone.name, angle))

        # SET BONE TRANSFORMATION
        armature.data.edit_bones[bone.name].head = bone_matrix.to_translation().to_3d() * import_scale
        armature.data.edit_bones[bone.name].tail = (armature.data.edit_bones[bone.name].head +
                                                    Vector(axis).normalized() *
                                                    bone_import_scale *
                                                    import_scale)
        armature.data.edit_bones[bone.name].roll = angle

        # save initial bone scaling to use it in calculation when importing PIA animations
        # NOTE: bones after import always have scale of 1:
        # 1. because edit bones don't have scale, just tail and head
        # 2. because any scaling in pose bones will be overwritten by animation itself
        armature.pose.bones[bone.name][_BONE_consts.init_scale_key] = bone_matrix.to_scale()

        # CONNECTED BONES
        # NOTE: Doesn't work as expected! Disabled for now in UI.
        # Child bones gets position offset and there is also a problem when translation
        # is animated, for which connected bones doesn't allow.
        if connected_bones:
            if len(bones[bone.name][2]) == 1:
                matrix = bones[bones[bone.name][2][0]][1]
                bone_matrix = _convert_utils.scs_to_blend_matrix() * matrix.transposed()
                armature.data.edit_bones[bone.name].tail = bone_matrix.to_translation().to_3d() * import_scale
                armature.data.edit_bones[bones[bone.name][2][0]].use_connect = True

    bpy.ops.object.mode_set(mode='OBJECT')
    armature.data.show_axes = True
    armature.draw_type = 'WIRE'

    # WARNING PRINTOUTS
    # if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
    # if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
    # if dump_level > 1: print('')

    print("************************************")
    return bones
