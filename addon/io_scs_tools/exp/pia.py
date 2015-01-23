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
import os
from mathutils import Vector, Matrix, Euler, Quaternion
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.info import get_tools_version as _get_tools_version
from io_scs_tools.utils.info import get_blender_version as _get_blender_version
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container


def _get_custom_channels(action):
    custom_channels = []
    frame_start = action.frame_range[0]
    frame_end = action.frame_range[1]
    total_time = action.scs_props.action_length
    anim_export_step = action.scs_props.anim_export_step
    total_frames = (frame_end - frame_start) / anim_export_step
    for group in action.groups:
        if group.name == 'Location':
            # print(' A -> %s' % str(group))
            loc_curves = {}
            for channel in group.channels:
                if channel.data_path.endswith("location"):
                    # data_path = channel.data_path
                    array_index = channel.array_index
                    # print(' a -> %s (%i)' % (data_path, array_index))
                    loc_curves[array_index] = channel

            # GO THOUGH FRAMES
            actual_frame = frame_start
            previous_frame_value = None
            timings_stream = []
            movement_stream = []
            while actual_frame <= frame_end:
                location = Vector()

                # LOCATION MATRIX
                if len(loc_curves) > 0:
                    for index in range(3):
                        if index in loc_curves:
                            location[index] = loc_curves[index].evaluate(actual_frame)

                    # COMPUTE SCS FRAME LOCATION
                    frame_loc = _convert_utils.convert_location_to_scs(location)

                if previous_frame_value is None:
                    previous_frame_value = frame_loc
                frame_movement = frame_loc - previous_frame_value
                previous_frame_value = frame_loc

                lprint('S actual_frame: %s - value: %s', (actual_frame, frame_loc))
                timings_stream.append(("__time__", total_time / total_frames), )
                movement_stream.append(frame_movement)
                actual_frame += anim_export_step
            anim_timing = ("_TIME", timings_stream)
            anim_movement = ("_MOVEMENT", movement_stream)
            bone_anim = (anim_timing, anim_movement)
            bone_data = ("Prism Movement", bone_anim)
            custom_channels.append(bone_data)

    # TODO: Channels can be outside of action groups, but I'm not sure if it practically can occur.
    # for x in action.fcurves:
    # if x.data_path == 'location':
    # print(' B -> %s' % str(x.data_path))

    return custom_channels


def _get_bone_channels(bone_list, action, export_scale):
    """Takes a bone list and action and returns bone channels.
    bone_channels structure example:
    [("Bone", [("_TIME", [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]), ("_MATRIX", [])])]"""
    bone_channels = []
    frame_start = action.frame_range[0]
    frame_end = action.frame_range[1]
    total_time = action.scs_props.action_length
    anim_export_step = action.scs_props.anim_export_step
    total_frames = (frame_end - frame_start) / anim_export_step
    # print(' -- action: %r' % str(action))
    for bone in bone_list:
        # print(' oo bone: %r' % str(bone))
        if bone:
            # print(' -- bone_name: %r' % bone.name)
            bone_name = bone.name
            bone_rest_mat = bone.matrix_local
            if bone.parent:
                parent_bone_rest_mat = Matrix.Scale(export_scale, 4) * _convert_utils.scs_to_blend_matrix().inverted() * bone.parent.matrix_local
            else:
                parent_bone_rest_mat = Matrix()
            for group in action.groups:
                if group.name == bone_name:
                    # print(' -- group: %r' % str(group))

                    # GET CHANELS' CURVES
                    loc_curves = {}
                    euler_rot_curves = {}
                    quat_rot_curves = {}
                    sca_curves = {}
                    rot_mode = ''
                    for channel in group.channels:
                        data_path = channel.data_path
                        array_index = channel.array_index
                        # channel_start = channel.range()[0]
                        # channel_end = channel.range()[1]
                        # print('      channel: %r (%s) [%s - %s]' % (data_path, array_index, channel_start, channel_end))
                        if data_path.endswith("location"):
                            loc_curves[array_index] = channel
                        elif data_path.endswith("rotation_euler"):
                            euler_rot_curves[array_index] = channel
                            rot_mode = 'euler'
                        elif data_path.endswith("rotation_quaternion"):
                            quat_rot_curves[array_index] = channel
                            rot_mode = 'quat'
                        elif data_path.endswith("scale"):
                            sca_curves[array_index] = channel

                    # GO THOUGH FRAMES
                    actual_frame = frame_start
                    timings_stream = []
                    matrices_stream = []
                    while actual_frame <= frame_end:
                        mat_loc = Matrix()
                        mat_rot = Matrix()
                        mat_sca = Matrix()

                        # LOCATION MATRIX
                        if len(loc_curves) > 0:
                            location = Vector()
                            for index in range(3):
                                if index in loc_curves:
                                    location[index] = loc_curves[index].evaluate(actual_frame)
                            mat_loc = Matrix.Translation(location)

                        # ROTATION MATRIX
                        if rot_mode == 'euler' and len(euler_rot_curves) > 0:
                            rotation = Euler()
                            for index in range(3):
                                if index in euler_rot_curves:
                                    rotation[index] = euler_rot_curves[index].evaluate(actual_frame)
                            mat_rot = Euler(rotation, 'XYZ').to_matrix().to_4x4()  # TODO: Solve the other rotation modes.
                        if rot_mode == 'quat' and len(quat_rot_curves) > 0:
                            rotation = Quaternion()
                            for index in range(4):
                                if index in quat_rot_curves:
                                    rotation[index] = quat_rot_curves[index].evaluate(actual_frame)
                            mat_rot = rotation.to_matrix().to_4x4()

                        # SCALE MATRIX
                        if len(sca_curves) > 0:
                            scale = Vector((1.0, 1.0, 1.0))
                            for index in range(3):
                                if index in sca_curves:
                                    scale[index] = sca_curves[index].evaluate(actual_frame)
                            mat_sca = Matrix()
                            mat_sca[0] = (scale[0], 0, 0, 0)
                            mat_sca[1] = (0, scale[2], 0, 0)
                            mat_sca[2] = (0, 0, scale[1], 0)
                            mat_sca[3] = (0, 0, 0, 1)

                        # BLENDER FRAME MATRIX
                        mat = mat_loc * mat_rot * mat_sca

                        # SCALE REMOVAL MATRIX
                        rest_location, rest_rotation, rest_scale = bone_rest_mat.decompose()
                        # print(' BONES rest_scale: %s' % str(rest_scale))
                        rest_scale = rest_scale * export_scale
                        scale_removal_matrix = Matrix()
                        scale_removal_matrix[0] = (1.0 / rest_scale[0], 0, 0, 0)
                        scale_removal_matrix[1] = (0, 1.0 / rest_scale[1], 0, 0)
                        scale_removal_matrix[2] = (0, 0, 1.0 / rest_scale[2], 0)
                        scale_removal_matrix[3] = (0, 0, 0, 1)

                        # SCALE MATRIX
                        scale_matrix = Matrix.Scale(export_scale, 4)

                        # COMPUTE SCS FRAME MATRIX
                        frame_matrix = (parent_bone_rest_mat.inverted() * _convert_utils.scs_to_blend_matrix().inverted() *
                                        scale_matrix.inverted() * bone_rest_mat * mat * scale_removal_matrix.inverted())

                        # print('          actual_frame: %s - value: %s' % (actual_frame, frame_matrix))
                        timings_stream.append(("__time__", total_time / total_frames), )
                        matrices_stream.append(("__matrix__", frame_matrix.transposed()), )
                        actual_frame += anim_export_step
                    anim_timing = ("_TIME", timings_stream)
                    anim_matrices = ("_MATRIX", matrices_stream)
                    bone_anim = (anim_timing, anim_matrices)
                    bone_data = (bone_name, bone_anim)
                    bone_channels.append(bone_data)
        else:
            lprint('W bone %r is not part of the actual Armature!', bone.name)
            # print(' -- bone.name: %r' % (bone.name))
    return bone_channels


def _fill_header_section(action, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 3))
    blender_version, blender_build = _get_blender_version()
    section.props.append(("Source", "Blender " + blender_version + blender_build + ", SCS Blender Tools: " + str(_get_tools_version())))
    section.props.append(("Type", "Animation"))
    # section.props.append(("Name", str(os.path.basename(bpy.data.filepath)[:-6])))
    section.props.append(("Name", action.name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(skeleton_file, total_time, bone_channel_cnt, custom_channel_cnt):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("Skeleton", skeleton_file))
    section.props.append(("TotalTime", total_time))
    # section.props.append(("#", "...in seconds"))
    section.props.append(("BoneChannelCount", bone_channel_cnt))
    section.props.append(("CustomChannelCount", custom_channel_cnt))
    return section


def _fill_channel_sections(data_list, channel_type="BoneChannel"):
    """Fills up Channel sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData(channel_type)
        section.props.append(("Name", item[0]))
        section.props.append(("StreamCount", len(item[1])))
        section.props.append(("KeyframeCount", len(item[1][0][1])))
        for stream in item[1]:
            # print(' stream[0]: %s\n stream[1]: %s' % (str(stream[0]), str(stream[1])))
            section.sections.append(_pix_container.make_stream_section(stream[1], stream[0], ()))
        sections.append(section)
    return sections


def export(armature, bone_list, filepath, filename):
    """Exports PIA animation


    :param armature:
    :type armature:
    :param bone_list:
    :type bone_list:
    :param filepath: path to export
    :type filepath: str
    :param filename: name of exported file
    :type filename: str
    :return:
    :rtype:
    """
    scs_globals = _get_scs_globals()
    # anim_file_name = os.path.splitext(os.path.split(filepath)[1])[0]

    print("\n************************************")
    print("**      SCS PIA Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    skeleton_file = str(filename + ".pis")
    action = armature.animation_data.action
    total_time = action.scs_props.action_length
    anim_export_filepath = action.scs_props.anim_export_filepath
    bone_channels = _get_bone_channels(bone_list, action, scs_globals.export_scale)
    custom_channels = _get_custom_channels(action)

    # DATA CREATION
    header_section = _fill_header_section(action, scs_globals.sign_export)
    custom_channel_sections = _fill_channel_sections(custom_channels, "CustomChannel")
    bone_channel_sections = _fill_channel_sections(bone_channels, "BoneChannel")
    global_section = _fill_global_section(skeleton_file, total_time, len(bone_channels), len(custom_channels))

    # DATA ASSEMBLING
    pia_container = [header_section, global_section]
    for section in custom_channel_sections:
        pia_container.append(section)
    for section in bone_channel_sections:
        pia_container.append(section)

    # EXPORT PIA TO CUSTOM LOCATION
    # pia_filepath = str(filepath[:-1] + "a")
    dir_path = os.path.dirname(filepath)
    if anim_export_filepath:
        if os.path.isdir(anim_export_filepath):
            dir_path = anim_export_filepath
        else:
            pass  # TODO: Create location?

    # FILE EXPORT
    ind = "    "
    pia_filepath = os.path.join(dir_path, str(action.name + ".pia"))
    _pix_container.write_data_to_file(pia_container, pia_filepath, ind)

    # print("************************************")
    return {'FINISHED'}