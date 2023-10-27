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
from mathutils import Matrix, Vector, Quaternion
from io_scs_tools.consts import Bones as _BONE_consts
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.imp import pis as _pis
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import animation as _animation_utils
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import path as _path_utils
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


def _create_fcurves(anim_action, anim_group, anim_curve, rot_euler=True, types='LocRotSca'):
    """Creates animation curves for provided Action / Group (Bone).

    :return: Tuple of position vector, rotation quaternion and scaling vector
    :rtype (fcurve, fcurve, fcurve)
    """
    pos_fcurves = rot_fcurves = sca_fcurves = None
    if 'Loc' in types:
        fcurve_pos_x = anim_action.fcurves.new(str(anim_curve + '.location'), index=0)
        fcurve_pos_y = anim_action.fcurves.new(str(anim_curve + '.location'), index=1)
        fcurve_pos_z = anim_action.fcurves.new(str(anim_curve + '.location'), index=2)
        fcurve_pos_x.group = anim_group
        fcurve_pos_y.group = anim_group
        fcurve_pos_z.group = anim_group
        pos_fcurves = (fcurve_pos_x, fcurve_pos_y, fcurve_pos_z)
    if 'Rot' in types:
        if rot_euler:
            fcurve_rot_x = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), index=0)
            fcurve_rot_y = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), index=1)
            fcurve_rot_z = anim_action.fcurves.new(str(anim_curve + '.rotation_euler'), index=2)
            fcurve_rot_x.group = anim_group
            fcurve_rot_y.group = anim_group
            fcurve_rot_z.group = anim_group
            rot_fcurves = (fcurve_rot_x, fcurve_rot_y, fcurve_rot_z)
        else:
            fcurve_rot_w = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), index=0)
            fcurve_rot_x = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), index=1)
            fcurve_rot_y = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), index=2)
            fcurve_rot_z = anim_action.fcurves.new(str(anim_curve + '.rotation_quaternion'), index=3)
            fcurve_rot_w.group = anim_group
            fcurve_rot_x.group = anim_group
            fcurve_rot_y.group = anim_group
            fcurve_rot_z.group = anim_group
            rot_fcurves = (fcurve_rot_w, fcurve_rot_x, fcurve_rot_y, fcurve_rot_z)
    if 'Sca' in types:
        fcurve_sca_x = anim_action.fcurves.new(str(anim_curve + '.scale'), index=0)
        fcurve_sca_y = anim_action.fcurves.new(str(anim_curve + '.scale'), index=1)
        fcurve_sca_z = anim_action.fcurves.new(str(anim_curve + '.scale'), index=2)
        fcurve_sca_x.group = anim_group
        fcurve_sca_y.group = anim_group
        fcurve_sca_z.group = anim_group
        sca_fcurves = (fcurve_sca_x, fcurve_sca_y, fcurve_sca_z)
    # print(' fcurve: %s' % str(fcurve))
    return pos_fcurves, rot_fcurves, sca_fcurves


def _get_delta_matrix(bone_rest_matrix_scs, parent_bone_rest_matrix_scs, bone_animation_matrix_scs, import_scale):
    """."""
    scale_matrix = Matrix.Scale(import_scale, 4)

    # NOTE: apply scaling bone rest matrix, because it's subtracted by bone rest matrix inverse
    loc, rot, sca = bone_rest_matrix_scs.decompose()
    scale = Matrix.Identity(4)
    scale[0] = (sca[0], 0, 0, 0)
    scale[1] = (0, sca[1], 0, 0)
    scale[2] = (0, 0, sca[2], 0)

    return (scale_matrix @
            scale @
            bone_rest_matrix_scs.inverted() @
            parent_bone_rest_matrix_scs @
            bone_animation_matrix_scs)


def load(root_object, pia_files, armature, pis_filepath=None, bones=None):
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIA Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    import_scale = scs_globals.import_scale
    ind = '    '
    imported_count = 0
    for pia_filepath in pia_files:
        # Check if PIA file is for the actual skeleton...
        if pis_filepath and bones:
            skeleton_match = _pix_container.fast_check_for_pia_skeleton(pia_filepath, pis_filepath)
        else:
            skeleton_match, pia_skeleton = _pix_container.utter_check_for_pia_skeleton(pia_filepath, armature)

            if skeleton_match:

                path = os.path.split(pia_filepath)[0]
                pia_skeleton = os.path.join(path, pia_skeleton)
                if os.path.isfile(pia_skeleton):
                    bones = _pis.load(pia_skeleton, armature, get_only=True)
                else:
                    lprint("\nE The filepath %r doesn't exist!", (_path_utils.readable_norm(pia_skeleton),))

            else:
                lprint(str("E Animation doesn't match the skeleton. Animation won't be loaded!\n\t   "
                           "Animation file: %r"), (pia_filepath,))

        if skeleton_match:
            lprint('I ++ "%s" IMPORTING animation data...', (os.path.basename(pia_filepath),))
            pia_container = _pix_container.get_data_from_file(pia_filepath, ind)
            if not pia_container:
                lprint('\nE File "%s" is empty!', (_path_utils.readable_norm(pia_filepath),))
                continue

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
                continue

            # LOAD GLOBALS
            skeleton, total_time, bone_channel_count, custom_channel_count = _get_globals(pia_container)

            # CREATE ANIMATION ACTIONS
            anim_action = bpy.data.actions.new(animation_name + "_action")
            anim_action.use_fake_user = True
            anim_data = armature.animation_data if armature.animation_data else armature.animation_data_create()
            anim_data.action = anim_action

            # LOAD BONE CHANNELS
            bone_channels = _get_anim_channels(pia_container, section_name="BoneChannel")
            if len(bone_channels) > 0:

                for bone_name in bone_channels:

                    if bone_name in armature.data.bones:
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_count = bone_channels[bone_name][0]
                        keyframe_count = bone_channels[bone_name][1]
                        '''
                        streams = bone_channels[bone_name][2]

                        # CREATE ANIMATION GROUP
                        anim_group = anim_action.groups.new(bone_name)
                        armature.pose.bones[bone_name].rotation_mode = 'XYZ'  # Set rotation mode.

                        # use pose bone scale set on PIS import
                        init_scale = Vector((1, 1, 1))
                        if _BONE_consts.init_scale_key in armature.pose.bones[bone_name]:
                            init_scale = armature.pose.bones[bone_name][_BONE_consts.init_scale_key]

                        # CREATE FCURVES
                        (pos_fcurves,
                         rot_fcurves,
                         sca_fcurves) = _create_fcurves(anim_action, anim_group, str('pose.bones["' + bone_name + '"]'), rot_euler=True)

                        # GET BONE REST POSITION MATRIX
                        bone_rest_matrix_scs = bones[bone_name][1].transposed()
                        parent_bone_name = bones[bone_name][0]
                        if parent_bone_name in bones:
                            parent_bone_rest_matrix_scs = bones[parent_bone_name][1].transposed()
                        else:
                            parent_bone_rest_matrix_scs = Matrix()
                            parent_bone_rest_matrix_scs.identity()

                        for key_time_i, key_time in enumerate(streams[0]):
                            keyframe = key_time_i + 1

                            # GET BONE ANIMATION MATRIX
                            bone_animation_matrix_scs = streams[1][key_time_i].transposed()

                            # CREATE DELTA MATRIX
                            delta_matrix = _get_delta_matrix(bone_rest_matrix_scs, parent_bone_rest_matrix_scs, bone_animation_matrix_scs,
                                                             import_scale)

                            # DECOMPOSE ANIMATION MATRIX
                            location, rotation, scale = delta_matrix.decompose()

                            # CALCULATE CURRENT SCALE - subtract difference between initial bone scale and current scale from 1
                            # NOTE: if imported PIS had initial bone scale different than 1,
                            # initial scale was saved into pose bones custom properties and
                            # has to be used here as bones after import in Blender always have scale of 1
                            scale = Vector((1 + scale[0] - init_scale[0],
                                            1 + scale[1] - init_scale[1],
                                            1 + scale[2] - init_scale[2]))

                            # NOTE: this scaling rotation switch came from UK variants which had scale -1
                            loc, rot, sca = bone_rest_matrix_scs.decompose()
                            if sca.y < 0:
                                rotation.y *= -1
                            if sca.z < 0:
                                rotation.z *= -1

                            rotation = rotation.to_euler('XYZ')

                            # BUILD TRANSFORMATION CURVES
                            for i in range(0, 3):
                                pos_fcurves[i].keyframe_points.insert(frame=float(keyframe), value=location[i], options={'FAST'})
                                rot_fcurves[i].keyframe_points.insert(frame=float(keyframe), value=rotation[i], options={'FAST'})
                                sca_fcurves[i].keyframe_points.insert(frame=float(keyframe), value=scale[i], options={'FAST'})

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

                        for curve in rot_fcurves:
                            _animation_utils.apply_euler_filter(curve)

            # LOAD CUSTOM CHANNELS (ARMATURE OFFSET ANIMATION)
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
                        fcurve_pos_x = anim_action.fcurves.new('location', index=0)
                        fcurve_pos_y = anim_action.fcurves.new('location', index=1)
                        fcurve_pos_z = anim_action.fcurves.new('location', index=2)
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
                    elif channel_name == 'Prism Rotation':
                        '''
                        NOTE: skipped for now as no data needs to be readed
                        stream_count = custom_channels[channel_name][0]
                        keyframe_count = custom_channels[channel_name][1]
                        '''
                        streams = custom_channels[channel_name][2]
                        # print('  channel %r - streams %s - keyframes %s' % (channel_name, stream_count, keyframe_count))

                        anim_group = anim_action.groups.new('Rotation')

                        fcurve_rot_w = anim_action.fcurves.new('rotation_quaternion', index=0)
                        fcurve_rot_x = anim_action.fcurves.new('rotation_quaternion', index=1)
                        fcurve_rot_y = anim_action.fcurves.new('rotation_quaternion', index=2)
                        fcurve_rot_z = anim_action.fcurves.new('rotation_quaternion', index=3)
                        fcurve_rot_w.group = anim_group
                        fcurve_rot_x.group = anim_group
                        fcurve_rot_y.group = anim_group
                        fcurve_rot_z.group = anim_group
                        rot_fcurves = (fcurve_rot_w, fcurve_rot_x, fcurve_rot_y, fcurve_rot_z)

                        rotation = None
                        for key_time_i, key_time in enumerate(streams[0]):
                            # print(' key_time: %s' % str(key_time[0]))
                            # keyframe = key_time_i * (key_time[0] * 10) ## TODO: Do proper timing...
                            keyframe = key_time_i + 1
                            scs_offset = _convert_utils.change_to_scs_quaternion_coordinates(custom_channels[channel_name][2][1][key_time_i])
                            offset = Quaternion(scs_offset)
                            if rotation is None:
                                rotation = offset
                            else:
                                rotation.rotate(offset)
                            #print(' > rotation: %s' % str(rotation))

                            rot_fcurves[0].keyframe_points.insert(frame=float(keyframe), value=rotation.w, options={'FAST'})
                            rot_fcurves[1].keyframe_points.insert(frame=float(keyframe), value=rotation.x, options={'FAST'})
                            rot_fcurves[2].keyframe_points.insert(frame=float(keyframe), value=rotation.y, options={'FAST'})
                            rot_fcurves[3].keyframe_points.insert(frame=float(keyframe), value=rotation.z, options={'FAST'})

                        # SET LINEAR INTERPOLATION FOR ALL CURVES
                        for curve in rot_fcurves:
                            for keyframe in curve.keyframe_points:
                                keyframe.interpolation = 'LINEAR'
                    else:
                        lprint('W Unknown channel %r in "%s" file.', (channel_name, os.path.basename(pia_filepath)))

            # CREATE SCS ANIMATION
            animation = _animation_utils.add_animation_to_root(root_object, animation_name)
            animation.export = True
            animation.action = anim_action.name
            animation.anim_start = int(anim_action.frame_range[0])
            animation.anim_end = int(anim_action.frame_range[1])

            if total_time:
                animation.length = total_time

                # WARNING PRINTOUTS
                # if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
                # if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
                # if dump_level > 1: print('')

            imported_count += 1
        else:
            lprint('I    "%s" file REJECTED', (os.path.basename(pia_filepath),))

    # at the end of batch import make sure to select last animation always
    if imported_count > 0:
        root_object.scs_props.active_scs_animation = len(root_object.scs_object_animation_inventory) - 1

    print("************************************")
    return imported_count
