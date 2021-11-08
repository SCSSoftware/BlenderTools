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
from collections import OrderedDict
from mathutils import Vector, Matrix, Euler, Quaternion
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container


def _get_custom_channels(scs_animation, action):
    custom_channels = []
    frame_start = scs_animation.anim_start
    frame_end = scs_animation.anim_end
    anim_export_step = action.scs_props.anim_export_step
    total_frames = (frame_end - frame_start) / anim_export_step

    loc_curves = {}  # dictionary for storing "location" curves of action

    # get curves which are related to moving of armature object
    for fcurve in action.fcurves:
        if fcurve.data_path == 'location':
            loc_curves[fcurve.array_index] = fcurve

    # write custom channel only if location curves were found
    if len(loc_curves) > 0:

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
            timings_stream.append(("__time__", scs_animation.length / total_frames), )
            movement_stream.append(frame_movement)
            actual_frame += anim_export_step

        anim_timing = ("_TIME", timings_stream)
        anim_movement = ("_MOVEMENT", movement_stream)
        bone_anim = (anim_timing, anim_movement)
        bone_data = ("Prism Movement", bone_anim)
        custom_channels.append(bone_data)

    rot_curves = {}  # dictionary for storing "rotation_quaternion" curves of action
    for fcurve in action.fcurves:
        if fcurve.data_path == 'rotation_quaternion':
            rot_curves[fcurve.array_index] = fcurve

    # write custom channel only if rotation curves were found
    if len(rot_curves) > 0:

        # GO THROUGH FRAMES
        actual_frame = frame_start
        previous_frame_value = None
        timings_stream = []
        rotation_stream = []
        while actual_frame <= frame_end:
            rotation = Quaternion()

            # ROTATION MATRIX
            if len(rot_curves) > 0:
                for index in range(4):
                    if index in rot_curves:
                        rotation[index] = rot_curves[index].evaluate(actual_frame)

                # COMPUTE SCS FRAME ROTATION
                frame_rot = _convert_utils.change_to_scs_quaternion_coordinates(rotation)

            if previous_frame_value is None:
                previous_frame_value = frame_rot

            frame_rotation = frame_rot.rotation_difference( previous_frame_value )
            previous_frame_value = frame_rot

            lprint('S actual_frame: %s - value: %s', (actual_frame, frame_rot))
            timings_stream.append(("__time__", scs_animation.length / total_frames), )
            rotation_stream.append(frame_rotation)
            actual_frame += anim_export_step

        anim_timing = ("_TIME", timings_stream)
        anim_movement = ("_ROTATION", rotation_stream)
        bone_anim = (anim_timing, anim_movement)
        bone_data = ("Prism Rotation", bone_anim)
        custom_channels.append(bone_data)

    return custom_channels


def _get_bone_channels(scs_root_obj, armature, scs_animation, action, export_scale):
    """Takes armature and action and returns bone channels.
    bone_channels structure example:
    [("Bone", [("_TIME", [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]), ("_MATRIX", [])])]"""
    bone_channels = []
    frame_start = scs_animation.anim_start
    frame_end = scs_animation.anim_end
    anim_export_step = action.scs_props.anim_export_step
    total_frames = (frame_end - frame_start) / anim_export_step

    # armature matrix stores transformation of armature object against scs root
    # and has to be added to all bones as they only armature space transformations
    armature_mat = scs_root_obj.matrix_world.inverted() @ armature.matrix_world

    invalid_data = False  # flag to indicate invalid data state
    curves_per_bone = OrderedDict()  # store all the curves we are interested in per bone names

    for bone in armature.data.bones:
        for fcurve in action.fcurves:

            # check if curve belongs to bone
            if '["' + bone.name + '"]' in fcurve.data_path:

                data_path = fcurve.data_path
                array_index = fcurve.array_index

                if data_path.endswith("location"):
                    curve_type = "location"
                elif data_path.endswith("rotation_euler"):
                    curve_type = "euler_rotation"
                elif data_path.endswith("rotation_quaternion"):
                    curve_type = "quat_rotation"
                elif data_path.endswith("scale"):
                    curve_type = "scale"
                else:
                    curve_type = None

                # write only recognized curves
                if curve_type is not None:
                    if bone.name not in curves_per_bone:
                        curves_per_bone[bone.name] = {
                            "location": {},
                            "euler_rotation": {},
                            "quat_rotation": {},
                            "scale": {}
                        }

                    curves_per_bone[bone.name][curve_type][array_index] = fcurve

    for bone_name, bone_curves in curves_per_bone.items():

        bone = armature.data.bones[bone_name]
        pose_bone = armature.pose.bones[bone_name]
        loc_curves = bone_curves["location"]
        euler_rot_curves = bone_curves["euler_rotation"]
        quat_rot_curves = bone_curves["quat_rotation"]
        sca_curves = bone_curves["scale"]

        bone_rest_mat = armature_mat @ bone.matrix_local
        if bone.parent:
            parent_bone_rest_mat = (Matrix.Scale(export_scale, 4) @
                                    _convert_utils.scs_to_blend_matrix().inverted() @
                                    armature_mat @
                                    bone.parent.matrix_local)
        else:
            parent_bone_rest_mat = Matrix()

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
            if len(euler_rot_curves) > 0:
                rotation = Euler()
                for index in range(3):
                    if index in euler_rot_curves:
                        rotation[index] = euler_rot_curves[index].evaluate(actual_frame)
                mat_rot = Euler(rotation, pose_bone.rotation_mode).to_matrix().to_4x4()  # calc rotation by pose rotation mode

            elif len(quat_rot_curves) > 0:
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

                        if scale[index] < 0:
                            lprint(str("E Negative scale detected on bone %r:\n\t   "
                                       "(Action: %r, keyframe no.: %s, SCS Animation: %r)."),
                                   (bone_name, action.name, actual_frame, scs_animation.name))
                            invalid_data = True

                mat_sca = Matrix()
                mat_sca[0] = (scale[0], 0, 0, 0)
                mat_sca[1] = (0, scale[1], 0, 0)
                mat_sca[2] = (0, 0, scale[2], 0)
                mat_sca[3] = (0, 0, 0, 1)

            # BLENDER FRAME MATRIX
            mat = mat_loc @ mat_rot @ mat_sca

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
            frame_matrix = (parent_bone_rest_mat.inverted() @
                            _convert_utils.scs_to_blend_matrix().inverted() @
                            scale_matrix.inverted() @
                            bone_rest_mat @
                            mat @
                            scale_removal_matrix.inverted())

            # print('          actual_frame: %s - value: %s' % (actual_frame, frame_matrix))
            timings_stream.append(("__time__", scs_animation.length / total_frames), )
            matrices_stream.append(("__matrix__", frame_matrix.transposed()), )
            actual_frame += anim_export_step

        anim_timing = ("_TIME", timings_stream)
        anim_matrices = ("_MATRIX", matrices_stream)
        bone_anim = (anim_timing, anim_matrices)
        bone_data = (bone_name, bone_anim)
        bone_channels.append(bone_data)

    # return empty bone channels if data are invalid
    if invalid_data:
        return []

    return bone_channels


def _fill_header_section(anim_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 3))
    section.props.append(("Source", get_combined_ver_str()))
    section.props.append(("Type", "Animation"))
    section.props.append(("Name", anim_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(skeleton_file, total_time, bone_channel_cnt, custom_channel_cnt):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("Skeleton", skeleton_file.replace("\\", "/")))
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


def export(scs_root_obj, armature, scs_animation, dirpath, name_suffix, skeleton_filepath):
    """Exports PIA animation

    :param scs_root_obj: root object of current animation
    :type scs_root_obj: bpy.types.Object
    :param armature: armature object of current animation
    :type armature: bpy.types.Object
    :param scs_animation: animation which should get exported
    :type scs_animation: io_scs_tools.properties.object.ObjectAnimationInventoryItem
    :param dirpath: path to export
    :type dirpath: str
    :param name_suffix: file name suffix
    :type name_suffix: str
    :param skeleton_filepath: name of skeleton file that this animation works on
    :type skeleton_filepath: str
    """

    # safety checks
    if scs_animation.action not in bpy.data.actions:
        lprint(str("E Action %r requested by %r animation doesn't exists. Animation won't be exported!\n\t   "
                   "Make sure proper action is assigned to SCS Animation."),
               (scs_animation.action, scs_animation.name))
        return False

    scs_globals = _get_scs_globals()
    print("\n************************************")
    print("**      SCS PIA Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    total_time = scs_animation.length
    action = bpy.data.actions[scs_animation.action]
    bone_channels = _get_bone_channels(scs_root_obj, armature, scs_animation, action, scs_globals.export_scale)
    custom_channels = _get_custom_channels(scs_animation, action)

    # DATA CREATION
    header_section = _fill_header_section(scs_animation.name, scs_globals.export_write_signature)
    custom_channel_sections = _fill_channel_sections(custom_channels, "CustomChannel")
    bone_channel_sections = _fill_channel_sections(bone_channels, "BoneChannel")
    global_section = _fill_global_section(skeleton_filepath, total_time, len(bone_channels), len(custom_channels))

    # post creation safety checks
    if len(bone_channels) + len(custom_channels) == 0:
        lprint(str("E PIA file won't be exported, as SCS Animation %r\n\t   "
                   "doesn't effect armature or it's bones or data are invalid."),
               (scs_animation.name,))
        return False

    # DATA ASSEMBLING
    pia_container = [header_section, global_section]
    for section in custom_channel_sections:
        pia_container.append(section)
    for section in bone_channel_sections:
        pia_container.append(section)

    # FILE EXPORT
    ind = "    "
    filepath = os.path.join(dirpath, scs_animation.name + ".pia" + name_suffix)

    # print("************************************")
    return _pix_container.write_data_to_file(pia_container, filepath, ind)
