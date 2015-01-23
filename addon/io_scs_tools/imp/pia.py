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

import re
import os
import bpy
from mathutils import Matrix, Vector
from io_scs_tools.internals.parsers import pix as _pix_parser
from io_scs_tools.imp import pis as _pis
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import animation as _animation_utils
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def _get_header(pia_container):
    """Receives PIA container and returns all its Header properties in its own variables.
    For any item that fails to be found, it returns None."""
    format_version = source = f_type = animation_name = source_filename = author = None
    for section in pia_container:
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
                    animation_name = prop[1]
                elif prop[0] == "SourceFilename":
                    source_filename = prop[1]
                elif prop[0] == "Author":
                    author = prop[1]
                else:
                    lprint('\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, animation_name, source_filename, author


def _get_globals(pia_container):
    """Receives PIA container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    skeleton = total_time = bone_channel_count = custom_channel_count = None
    for section in pia_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "Skeleton":
                    skeleton = prop[1]
                elif prop[0] == "TotalTime":
                    total_time = prop[1]
                elif prop[0] == "BoneChannelCount":
                    bone_channel_count = prop[1]
                elif prop[0] == "CustomChannelCount":
                    custom_channel_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return skeleton, total_time, bone_channel_count, custom_channel_count


def _get_anim_channels(pia_container, section_name="BoneChannel"):
    """Receives PIA container and returns all its Bone Channels in a list."""
    channels = {}
    for section in pia_container:
        bone_name = stream_count = keyframe_count = None
        streams = []
        if section.type == section_name:
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "Name":
                    bone_name = prop[1]
                elif prop[0] == "StreamCount":
                    stream_count = prop[1]
                elif prop[0] == "KeyframeCount":
                    keyframe_count = prop[1]
                else:
                    lprint('\nW Unknown property in "%s" data: "%s"!', (section_name, prop[0]))
            for sec in section.sections:
                for prop in sec.props:
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "Format":
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_format = prop[1]
                        '''
                        pass
                    elif prop[0] == "Tag":
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_tag = prop[1]
                        '''
                        pass
                    else:
                        lprint('\nW Unknown property in "%s" data: "%s"!', (section_name, prop[0]))
                data_block = []
                for data_line in sec.data:
                    data_block.append(data_line)
                streams.append(data_block)
            channels[bone_name] = (stream_count, keyframe_count, streams)
    return channels


def _fast_check_for_pia_skeleton(pia_filepath, skeleton):
    """Check for the skeleton record in PIA file without parsing the whole file.
    It takes filepath and skeleton name (string) and returns True if the skeleton
    record in the file is the same as skeleton name provided, otherwise False."""
    file = open(pia_filepath, 'r')
    while 1:
        data_type, line = _pix_parser.next_line(file)
        if data_type in ('EOF', 'ERR'):
            break
        # print('%s  ==> "%s"' % (data_type, line))
        if data_type == 'SE_S':
            section_type = re.split(r'[ ]+', line)[0]
            if section_type == "Global":
                # print('  %s' % section_type)
                data_type, line = _pix_parser.next_line(file)
                ske = re.split(r'"', line)[1]
                # print('  %r | %r' % (ske, skeleton))
                if ske == skeleton:
                    file.close()
                    return True
                break
    file.close()
    return False


def _utter_check_for_pia_skeleton(pia_filepath, armature):
    """Skeleton analysis in PIA file with reasonably quick searching the whole file.
    It takes filepath and an Armature object and returns True if the skeleton in PIA file
    can be used for the skeleton in provided Armature object, otherwise it returns False."""
    bone_names = [bone.name for bone in armature.data.bones]
    file = open(pia_filepath, 'r')
    skeleton = None
    bone_matches = []
    while 1:
        data_type, line = _pix_parser.next_line(file)
        if data_type == 'EOF':
            if len(bone_matches) > 0:
                break
            else:
                file.close()
                return False, None
        if data_type == 'ERR':
            file.close()
            return False, None
        # print('%s  ==> "%s"' % (data_type, line))
        if data_type == 'SE_S':
            section_type = re.split(r'[ ]+', line)[0]
            if section_type == "Global":
                # print('  %s' % section_type)
                data_type, line = _pix_parser.next_line(file)
                line_split = re.split(r'"', line)
                # print('  %r | %r' % (line_split, skeleton))
                if line_split[0].strip() == "Skeleton:":
                    skeleton = line_split[1].strip()
            elif section_type == "BoneChannel":
                data_type, line = _pix_parser.next_line(file)
                # print('  %s - %s' % (data_type, line))
                prop_name = re.split(r'"', line)[1]
                # print('  %r' % prop_name)
                if prop_name in bone_names:
                    bone_matches.append(prop_name)
                else:
                    file.close()
                    return False, None
    file.close()
    return True, skeleton


def _create_fcurves(anim_action, anim_group, anim_curve, rot_euler=True, types='LocRotSca'):
    """Creates animation curves for provided Action / Group (Bone).

    :return: Tuple of position vector, rotation quaternion and scaling vector
    :rtype (fcurve, fcurve, fcurve)
    """
    pos_fcurves = rot_fcurves = sca_fcurves = None
    if 'Loc' in types:
        fcurve_pos_x = anim_action.fcurves.new(str(anim_curve + '.location'), 0)
        fcurve_pos_y = anim_action.fcurves.new(str(anim_curve + '.location'), 1)
        fcurve_pos_z = anim_action.fcurves.new(str(anim_curve + '.location'), 2)
        fcurve_pos_x.group = anim_group
        fcurve_pos_y.group = anim_group
        fcurve_pos_z.group = anim_group
        pos_fcurves = (fcurve_pos_x, fcurve_pos_y, fcurve_pos_z)
    if 'Rot' in types:
        if rot_euler:
            fcurve_rot_x = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), 0)
            fcurve_rot_y = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), 1)
            fcurve_rot_z = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), 2)
            fcurve_rot_x.group = anim_group
            fcurve_rot_y.group = anim_group
            fcurve_rot_z.group = anim_group
            rot_fcurves = (fcurve_rot_x, fcurve_rot_y, fcurve_rot_z)
        else:
            fcurve_rot_w = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), 0)
            fcurve_rot_x = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), 1)
            fcurve_rot_y = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), 2)
            fcurve_rot_z = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), 3)
            fcurve_rot_w.group = anim_group
            fcurve_rot_x.group = anim_group
            fcurve_rot_y.group = anim_group
            fcurve_rot_z.group = anim_group
            rot_fcurves = (fcurve_rot_w, fcurve_rot_x, fcurve_rot_y, fcurve_rot_z)
    if 'Sca' in types:
        fcurve_sca_x = anim_action.fcurves.new(str(anim_curve + '.scale'), 0)
        fcurve_sca_y = anim_action.fcurves.new(str(anim_curve + '.scale'), 1)
        fcurve_sca_z = anim_action.fcurves.new(str(anim_curve + '.scale'), 2)
        fcurve_sca_x.group = anim_group
        fcurve_sca_y.group = anim_group
        fcurve_sca_z.group = anim_group
        sca_fcurves = (fcurve_sca_x, fcurve_sca_y, fcurve_sca_z)
    # print(' fcurve: %s' % str(fcurve))
    return pos_fcurves, rot_fcurves, sca_fcurves


def _get_delta_matrix(bone_rest_matrix, bone_rest_matrix_scs, parent_bone_rest_matrix_scs, bone_animation_matrix_scs, import_scale):
    """."""
    rest_location, rest_rotation, rest_scale = bone_rest_matrix_scs.decompose()
    # print(' BONES rest_scale: %s' % str(rest_scale))
    rest_scale = rest_scale * import_scale
    scale_removal_matrix = Matrix()
    scale_removal_matrix[0] = (1.0 / rest_scale[0], 0, 0, 0)
    scale_removal_matrix[1] = (0, 1.0 / rest_scale[1], 0, 0)
    scale_removal_matrix[2] = (0, 0, 1.0 / rest_scale[2], 0)
    scale_removal_matrix[3] = (0, 0, 0, 1)
    scale_matrix = Matrix.Scale(import_scale, 4)
    return (bone_rest_matrix.inverted() *
            scale_matrix *
            _convert_utils.scs_to_blend_matrix() *
            parent_bone_rest_matrix_scs *
            bone_animation_matrix_scs *
            scale_removal_matrix)


def load(root_object, pia_files, armature, skeleton=None, bones=None):
    if not bones:
        bones = {}

    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIA Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    import_scale = scs_globals.import_scale
    ind = '    '
    for pia_filepath in pia_files:
        # Check if PIA file is for the actual skeleton...
        if skeleton:
            skeleton_match = _fast_check_for_pia_skeleton(pia_filepath, skeleton)
        else:
            skeleton_match, skeleton = _utter_check_for_pia_skeleton(pia_filepath, armature)
            # print('%r - %s' %(os.path.basename(pia_filepath), skeleton_match))
            # print('  skeleton: %r' % skeleton)
            if skeleton_match:
                path = os.path.split(pia_filepath)[0]
                pis_filepath = os.path.join(path, skeleton)
                if os.path.isfile(pis_filepath):
                    # print('  pis_filepath: %r' % pis_filepath)
                    bones = _pis.load(pis_filepath, armature)
                else:
                    lprint("""\nE The filepath "%s" doesn't exist!""", (pis_filepath.replace("\\", "/"),))

        if skeleton_match:
            lprint('I ++ "%s" IMPORTING animation data...', (os.path.basename(pia_filepath),))
            pia_container, state = _pix_parser.read_data(pia_filepath, ind)
            if not pia_container:
                lprint('\nE File "%s" is empty!', (pia_filepath.replace("\\", "/"),))
                return {'CANCELLED'}
            if state == 'ERR':
                lprint('\nE File "%s" is not SCS Animation file!', (pia_filepath.replace("\\", "/"),))
                return {'CANCELLED'}

            # TEST PRINTOUTS
            # ind = '  '
            # for section in pia_container:
            # print('SEC.: "%s"' % section.type)
            # for prop in section.props:
            # print('%sProp: %s' % (ind, prop))
            # for data in section.data:
            # print('%sdata: %s' % (ind, data))
            # for sec in section.sections:
            # print_section(sec, ind)
            # print('\nTEST - Source: "%s"' % pia_container[0].props[1][1])
            # print('')

            # TEST EXPORT
            # path, file = os.path.splitext(pia_filepath)
            # export_filepath = str(path + '_reex' + file)
            # result = pix_write.write_data(pia_container, export_filepath, ind)
            # if result == {'FINISHED'}:
            # Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
            # else:
            # Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)

            # LOAD HEADER
            format_version, source, f_type, animation_name, source_filename, author = _get_header(pia_container)
            if format_version != 3 or f_type != "Animation":
                return {'CANCELLED'}

            # LOAD GLOBALS
            skeleton, total_time, bone_channel_count, custom_channel_count = _get_globals(pia_container)

            # CREATE ANIMATION ACTIONS
            anim_action = bpy.data.actions.new(animation_name)
            anim_action.use_fake_user = True
            if total_time:
                anim_action.scs_props.action_length = total_time
            anim_data = armature.animation_data_create()
            anim_data.action = anim_action

            # LOAD BONE CHANNELS
            # print(' * armature: %r' % armature.name)
            if bone_channel_count > 0:
                bone_channels = _get_anim_channels(pia_container, section_name="BoneChannel")

                # ...
                for bone_name in bone_channels:
                    # bone_name = channel[0]
                    if bone_name in armature.data.bones:
                        # print('%r is in armature %r' % (bone_name, armature.name))
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_count = bone_channels[bone_name][0]
                        keyframe_count = bone_channels[bone_name][1]
                        '''
                        streams = bone_channels[bone_name][2]
                        # print('  channel %r - streams %s - keyframes %s' % (bone_name, stream_count, keyframe_count))

                        # CREATE ANIMATION GROUP
                        anim_group = anim_action.groups.new(bone_name)
                        armature.pose.bones[bone_name].rotation_mode = 'XYZ'  # Set rotation mode.
                        active_bone = armature.data.bones[bone_name]
                        # parent_bone = active_bone.parent

                        # CREATE FCURVES
                        (pos_fcurves,
                         rot_fcurves,
                         sca_fcurves) = _create_fcurves(anim_action, anim_group, str('pose.bones["' + bone_name + '"]'))

                        # GET BONE REST POSITION MATRIX
                        bone_rest_matrix = active_bone.matrix_local
                        bone_rest_matrix_scs = bones[bone_name][1].transposed()
                        parent_bone_name = bones[bone_name][0]
                        if parent_bone_name in bones:
                            parent_bone_rest_matrix_scs = bones[parent_bone_name][1].transposed()
                        else:
                            parent_bone_rest_matrix_scs = Matrix()
                            parent_bone_rest_matrix_scs.identity()

                            # if bone_name in ('LeftHand1', 'LeftHand'):
                            # print('\n  %r - bone_rest_matrix_scs:\n%s' % (bone_name, bone_rest_matrix_scs))
                            # print('  %r - bone_rest_matrix:\n%s' % (bone_name, bone_rest_matrix))
                            # print('  %r - parent_bone_rest_matrix_scs:\n%s' % (bone_name, parent_bone_rest_matrix_scs))

                        for key_time_i, key_time in enumerate(streams[0]):
                            # print(' key_time: %s' % str(key_time[0]))
                            # keyframe = key_time_i * (key_time[0] * 10) ## TODO: Do proper timing...
                            keyframe = key_time_i + 1

                            # GET BONE ANIMATION MATRIX
                            bone_animation_matrix_scs = streams[1][key_time_i].transposed()
                            # if bone_name in ('LeftHand1', 'LeftHand') and key_time_i == 0: print('  %r - bone_animation_matrix_scs (%i):\n%s' % (
                            # bone_name, key_time_i, bone_animation_matrix_scs))

                            # CREATE DELTA MATRIX
                            delta_matrix = _get_delta_matrix(bone_rest_matrix, bone_rest_matrix_scs,
                                                             parent_bone_rest_matrix_scs, bone_animation_matrix_scs, import_scale)

                            # DECOMPOSE ANIMATION MATRIX
                            location, rotation, scale = delta_matrix.decompose()
                            # if bone_name in ('left_leg', 'root') and key_time_i == 0: print('  location:\n%s' % str(location))
                            rotation = rotation.to_euler('XYZ')

                            # BUILD TRANSLATION CURVES
                            pos_fcurves[0].keyframe_points.insert(frame=float(keyframe), value=location[0], options={'FAST'})
                            pos_fcurves[1].keyframe_points.insert(frame=float(keyframe), value=location[1], options={'FAST'})
                            pos_fcurves[2].keyframe_points.insert(frame=float(keyframe), value=location[2], options={'FAST'})

                            # BUILD ROTATION CURVES
                            rot_fcurves[0].keyframe_points.insert(frame=float(keyframe), value=rotation[0], options={'FAST'})
                            rot_fcurves[1].keyframe_points.insert(frame=float(keyframe), value=rotation[1], options={'FAST'})
                            rot_fcurves[2].keyframe_points.insert(frame=float(keyframe), value=rotation[2], options={'FAST'})

                            # BUILD SCALE CURVES
                            sca_fcurves[0].keyframe_points.insert(frame=float(keyframe), value=scale[0], options={'FAST'})
                            sca_fcurves[1].keyframe_points.insert(frame=float(keyframe), value=scale[1], options={'FAST'})
                            sca_fcurves[2].keyframe_points.insert(frame=float(keyframe), value=scale[2], options={'FAST'})

                        # SET LINEAR INTERPOLATION FOR ALL CURVES
                        color_mode = 'AUTO_RAINBOW'  # Or better 'AUTO_RGB'?
                        for curve in pos_fcurves:
                            curve.color_mode = color_mode
                            for keyframe in curve.keyframe_points:
                                keyframe.interpolation = 'LINEAR'
                        for curve in rot_fcurves:
                            curve.color_mode = color_mode
                            for keyframe in curve.keyframe_points:
                                keyframe.interpolation = 'LINEAR'
                        for curve in sca_fcurves:
                            curve.color_mode = color_mode
                            for keyframe in curve.keyframe_points:
                                keyframe.interpolation = 'LINEAR'

                                # LOAD CUSTOM CHANNELS (ARMATURE OFFSET ANIMATION)
            # if custom_channel_count > 0: ## NOTE: Can't be used because exporter from Maya saves always 0 even if there are Custom Channels.
            custom_channels = _get_anim_channels(pia_container, section_name="CustomChannel")
            if len(custom_channels) > 0:
                for channel_name in custom_channels:
                    # print(' >>> channel %r - %s' % (channel_name, str(custom_channels[channel_name])))
                    if channel_name == 'Prism Movement':
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_count = custom_channels[channel_name][0]
                        keyframe_count = custom_channels[channel_name][1]
                        '''
                        streams = custom_channels[channel_name][2]
                        # print('  channel %r - streams %s - keyframes %s' % (channel_name, stream_count, keyframe_count))

                        # CREATE ANIMATION GROUP
                        # anim_group = anim_action.groups.new(channel_name)
                        anim_group = anim_action.groups.new('Location')
                        # armature.[channel_name].rotation_mode = 'XYZ' ## Set rotation mode.
                        # active_bone = armature.data.bones[channel_name]
                        # parent_bone = active_bone.parent

                        # CREATE FCURVES
                        # pos_fcurves, rot_fcurves, sca_fcurves = _create_fcurves(anim_action, anim_group, anim_curve, rot_euler=True,
                        # types='LocRotSca')
                        # pos_fcurves, rot_fcurves, sca_fcurves = _create_fcurves(anim_action, anim_group, anim_curve, types='Loc')
                        fcurve_pos_x = anim_action.fcurves.new('location', 0)
                        fcurve_pos_y = anim_action.fcurves.new('location', 1)
                        fcurve_pos_z = anim_action.fcurves.new('location', 2)
                        fcurve_pos_x.group = anim_group
                        fcurve_pos_y.group = anim_group
                        fcurve_pos_z.group = anim_group
                        pos_fcurves = (fcurve_pos_x, fcurve_pos_y, fcurve_pos_z)

                        location = None
                        for key_time_i, key_time in enumerate(streams[0]):
                            # print(' key_time: %s' % str(key_time[0]))
                            # keyframe = key_time_i * (key_time[0] * 10) ## TODO: Do proper timing...
                            keyframe = key_time_i + 1
                            scs_offset = _convert_utils.change_to_scs_xyz_coordinates(custom_channels[channel_name][2][1][key_time_i], import_scale)
                            offset = Vector(scs_offset)
                            if location is None:
                                location = offset
                            else:
                                location = location + offset
                            # print(' > location: %s' % str(location))

                            # BUILD TRANSLATION CURVES
                            pos_fcurves[0].keyframe_points.insert(frame=float(keyframe), value=location[0], options={'FAST'})
                            pos_fcurves[1].keyframe_points.insert(frame=float(keyframe), value=location[1], options={'FAST'})
                            pos_fcurves[2].keyframe_points.insert(frame=float(keyframe), value=location[2], options={'FAST'})

                        # SET LINEAR INTERPOLATION FOR ALL CURVES
                        for curve in pos_fcurves:
                            for keyframe in curve.keyframe_points:
                                keyframe.interpolation = 'LINEAR'
                    else:
                        lprint('W Unknown channel %r in "%s" file.', (channel_name, os.path.basename(pia_filepath)))

                        # CREATE SCS ANIMATION
            animation = _animation_utils.add_animation_to_root(root_object, animation_name)
            animation.export = True
            animation.action = anim_action.name
            animation.anim_start = anim_action.frame_range[0]
            animation.anim_end = anim_action.frame_range[1]
            # animation.anim_export_step =
            # animation.anim_export_filepath =
            if total_time:
                animation.length = total_time

                # WARNING PRINTOUTS
                # if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
                # if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
                # if dump_level > 1: print('')
        else:
            lprint('I    "%s" file REJECTED', (os.path.basename(pia_filepath),))

    print("************************************")
    return {'FINISHED'}