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
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def strip_sep(path):
    """Strips double path separators (slashes and backslashes) on the start and the end of the given path
    :param path: path to strip separators from
    :type path: str
    :return: new stripped path
    :rtype: str
    """
    return path.strip("\\\\").strip("//")


def get_filename(path, with_ext=True):
    """Returns file name from given file, with or without extension.
    It finds last "os.sep" inside string and returns tail.
    :param path: path with file name
    :type path: str
    :param with_ext: return file name with extension or not
    :type with_ext: bool
    :return: file name with or without extension
    :rtype: str
    """

    # find last separator; prefer os.sep otherwise search for normal slash
    last_sep = path.rfind(os.sep)
    if last_sep < 0:
        last_sep = path.rfind("/")

    new_path = path[last_sep + 1:]
    if not with_ext and new_path.rfind(".") > 0:
        new_path = new_path[:new_path.rfind(".")]
    return new_path


def repair_path(filepath):
    """Takes a Blender filepath and tries to make it a valid absolute path."""
    if filepath != '':
        # print('0 filepath:\n"%s"' % filepath)
        filepath = bpy.path.abspath(filepath, start=None, library=None)  # make the path absolute
        # print('1 filepath:\n"%s"' % filepath)
        filepath = os.path.normpath(filepath)  # repair things like "...\dir\dir\..\dir\..."
        # print('2 filepath:\n"%s"' % filepath)
    return filepath


def relative_path(base_path, path):
    """Takes a base path and other path and returns the relative version of the second path
    if possible, otherwise it returns the original one (absolute path)."""
    repaired_base_path = repair_path(base_path)
    # print('repaired_base_path:\n\t"%s"' % repaired_base_path)
    repaired_path = repair_path(path)
    # print('repaired_path:\n\t"%s"' % repaired_path)
    if len(repaired_base_path) > 2:
        # presuming that first equality of first two chars means we are on same mount point
        if repaired_path[:2] == repaired_base_path[:2]:
            rel_path = os.path.relpath(repaired_path, repaired_base_path).replace("\\", "/")
            # print('rel_path:\n\t"%s"' % rel_path)
            if not rel_path.startswith("//"):
                rel_path = "//" + rel_path
            return rel_path
        else:
            lprint("W Not possible to create a relative path! Returning absolute path (%s)", (repaired_path,))
            return repaired_path
    else:
        lprint("W No base path specified! It's not possible to create a relative path! Returning absolute path (%s)", (repaired_path,))
        return repaired_path


def get_abs_path(path_in, subdir_path=''):
    """Takes a path, which can be either absolute or relative to the 'SCS Project Base Path'.
    If the path is existing and valid, it returns the absolute path, otherwise None.
    Optionally a subdir_path can be provided, which will be added to the 'SCS Project Base Path'.

    :param path_in: Absolute or relative path to current 'SCS Project Base path'
    :type path_in: str
    :param subdir_path: Additional subdirs can be provided, they will be added to the 'SCS Project Base Path'
    :type subdir_path: str
    :return: Absolute path or None
    :rtype: str
    """
    root_path = _get_scs_globals().scs_project_path
    if subdir_path != '':
        root_path = os.path.join(root_path, subdir_path)

    if path_in.startswith("//"):
        if len(root_path) > 2:
            result = os.path.join(root_path, path_in[2:])
        else:
            result = None
    else:
        result = path_in

    return result


'''
def is_valid_cgfx_template_library_path():
    """It returns True if there is valid "*.txt" file in
    the CgFX Template Library directory, otherwise False."""
    cgfx_templates_filepath = _get_scs_globals().cgfx_templates_filepath
    if cgfx_templates_filepath != "":
        if cgfx_templates_filepath.startswith(str(os.sep + os.sep)):  # RELATIVE PATH
            cgfx_templates_abs_path = get_abs_path(cgfx_templates_filepath)
            if cgfx_templates_abs_path:
                if os.path.isfile(cgfx_templates_abs_path):
                    return True
        else:  # ABSOLUTE PATH
            if os.path.isfile(cgfx_templates_filepath):
                return True
    return False


def is_valid_cgfx_library_rel_path():
    """It returns True if there is at least one "*.cgfx" file in
    the resulting CgFX Library directory, otherwise False."""
    cgfx_library_abs_path = get_abs_path(_get_scs_globals().cgfx_library_rel_path)
    if cgfx_library_abs_path:
        for root, dirs, files in os.walk(cgfx_library_abs_path):
            for file in files:
                if file.endswith(".cgfx"):
                    return True
            return False
    else:
        return False


def get_cgfx_templates_filepath():
    """Returns a valid filepath to "cgfx_templates.txt" file. If the file doesn't exists,
    the empty string is returned and CgFX templates won't be available."""
    scs_installation_dirs = get_addon_installation_paths()

    cgfx_templates_file = ''
    for location in scs_installation_dirs:
        test_path = os.path.join(location, 'cgfx_templates.txt')
        if os.path.isfile(test_path):
            cgfx_templates_file = test_path
            break

    return cgfx_templates_file
'''


def is_valid_shader_presets_library_path():
    """It returns True if there is valid "*.txt" file in
    the Shader Presets Library directory, otherwise False."""
    shader_presets_filepath = _get_scs_globals().shader_presets_filepath
    if shader_presets_filepath != "":
        if shader_presets_filepath.startswith("//"):  # RELATIVE PATH
            shader_presets_abs_path = get_abs_path(shader_presets_filepath)
            if shader_presets_abs_path:
                if os.path.isfile(shader_presets_abs_path):
                    return True
        else:  # ABSOLUTE PATH
            if os.path.isfile(shader_presets_filepath):
                return True
    return False


def is_valid_sign_library_rel_path():
    """It returns True if there is valid "*.sii" file in
    the Sign Library directory, otherwise False."""
    sign_library_abs_path = get_abs_path(_get_scs_globals().sign_library_rel_path)
    if sign_library_abs_path:
        if os.path.isfile(sign_library_abs_path):
            return True
        else:
            return False
    else:
        return False


def is_valid_tsem_library_rel_path():
    """It returns True if there is valid "*.sii" file in
    the Traffic Semaphore Profile Library directory, otherwise False."""
    tsem_library_abs_path = get_abs_path(_get_scs_globals().tsem_library_rel_path)
    if tsem_library_abs_path:
        if os.path.isfile(tsem_library_abs_path):
            return True
        else:
            return False
    else:
        return False


def is_valid_traffic_rules_library_rel_path():
    """It returns True if there is valid "*.sii" file in
    the Traffic Rules Library directory, otherwise False."""
    traffic_rules_library_abs_path = get_abs_path(_get_scs_globals().traffic_rules_library_rel_path)
    if traffic_rules_library_abs_path:
        if os.path.isfile(traffic_rules_library_abs_path):
            return True
        else:
            return False
    else:
        return False


def is_valid_hookup_library_rel_path():
    """It returns True if there is at least one "*.sii" file in
    the resulting CgFX Library directory, otherwise False."""
    hookup_library_abs_path = get_abs_path(_get_scs_globals().hookup_library_rel_path)
    if hookup_library_abs_path:
        for root, dirs, files in os.walk(hookup_library_abs_path):
            for file in files:
                if file.endswith(".sii"):
                    return True
            return False
    else:
        return False


def is_valid_matsubs_library_rel_path():
    """It returns True if there is valid "*.db" file in
    the Material Substance Library directory, otherwise False."""
    matsubs_library_abs_path = get_abs_path(_get_scs_globals().matsubs_library_rel_path)
    # print(' matsubs_library_abs_path: %r' % str(matsubs_library_abs_path))
    if matsubs_library_abs_path:
        if os.path.isfile(matsubs_library_abs_path):
            return True
        else:
            return False
    else:
        return False


def get_addon_installation_paths():
    """Returns a list of paths to the directories where the addon can be installed."""
    script_paths = bpy.utils.script_paths()
    addon_dirs = ('addons', 'addons_contrib')
    script_locations = []

    for script_path in script_paths:
        for addon_dir in addon_dirs:
            script_locations.append(os.path.join(script_path, addon_dir, 'io_scs_tools'))

    scs_installation_dirs = []
    for location in script_locations:
        if os.path.isdir(location):
            scs_installation_dirs.append(location)

    if len(scs_installation_dirs) == 0:
        lprint('''\n\nE The installation directory of "SCS Blender Tools" couldn't be detected! (Shouldn't happen!)\n''')
    elif len(scs_installation_dirs) > 1:
        lprint('\n\nW More than one installation of "SCS Blender Tools" detected!\n\t  Please remove redundant installations so the only one '
               'remain.\n')

    return scs_installation_dirs


def get_shader_presets_filepath():
    """Returns a valid filepath to "shader_presets.txt" file. If the file doesn't exists,
    the empty string is returned and Shader Presets won't be available."""
    scs_installation_dirs = get_addon_installation_paths()

    shader_presets_file = ''
    for location in scs_installation_dirs:
        test_path = os.path.join(location, 'shader_presets.txt')
        if os.path.isfile(test_path):
            shader_presets_file = test_path
            break

    return shader_presets_file


def make_texture_filepath(tobj_filepath, bitmap_filename):
    """Combine give two paths

    :param tobj_filepath:
    :type tobj_filepath:
    :param bitmap_filename:
    :type bitmap_filename:
    :return:
    :rtype:
    """
    tobj_path, tobj_filename = os.path.split(tobj_filepath)
    # print(' tobj_path: %s' % str(tobj_path))
    bitmap_filepath = os.path.join(tobj_path, bitmap_filename)
    # print(' bitmap_filepath: %s' % str(bitmap_filepath))
    if os.path.isfile(bitmap_filepath):
        # print(' bitmap_filepath: %s' % str(bitmap_filepath))
        base_path = _get_scs_globals().scs_project_path
        filepath = relative_path(base_path, bitmap_filepath)
    else:
        filepath = bitmap_filepath
    return filepath


def get_bitmap_filepath(texture_tobj_string):
    """Returns bitmap file path from tobj file

    :param texture_tobj_string:
    :type texture_tobj_string:
    :return:
    :rtype:
    """

    def get_tobj_filepath(texture_data_value):
        # print(' texture_data_value: %r' % texture_data_value)
        if texture_data_value != '':

            # exception for Windows so os.path.join can correctly join paths
            texture_data_value = texture_data_value.replace("/", os.sep)

            base_path = _get_scs_globals().scs_project_path
            if os.path.isdir(base_path):
                # print(' base_path: %r' % base_path)
                head, tail = os.path.split(texture_data_value)
                if head.startswith(os.sep):
                    head = head[1:]
                    # print(' head: %r' % head)
                tobj_path = os.path.join(base_path, head)
                # print(' tobj_path: %r' % tobj_path)
                tobj_name = str(tail + ".tobj")
                # print(' tobj_name: %r' % tobj_name)
                tobj_path = os.path.join(tobj_path, tobj_name)
                # print(' tobj_filepath: %r' % tobj_filepath)
                if os.path.isfile(tobj_path):
                    return tobj_path
                else:
                    lprint("E Texture file %r not found!", (tobj_path,))
            else:
                lprint("E No 'base' directory!")
        return None

    def get_tobj_data(tobj_path):
        """Takes a filepath of TOBJ file and returns its data as a list of keywords."""
        data = []
        with open(tobj_path) as file_open:
            for i, line in enumerate(file_open):
                # print(' ** line: %r' % str(line))
                line_split = line.strip().split()
                if len(line_split) != 0:
                    # print(' ** line_split: %s' % str(line_split))
                    for word in line_split:
                        data.append(word)
        file_open.close()
        return data

    filepath = ""
    tobj_filepath = get_tobj_filepath(texture_tobj_string)
    # print(' tobj_filepath: %s' % str(tobj_filepath))

    if tobj_filepath:
        tobj_data = get_tobj_data(tobj_filepath)
        # print(' tobj_data:\n%s' % str(tobj_data))
        rec_i = 0
        while rec_i < len(tobj_data):
            rec = tobj_data[rec_i]
            # print('  rec: %s' % str(rec))
            if rec.startswith('#'):
                rec_i += 1
                continue
            elif rec == 'map':
                if tobj_data[rec_i + 1] == '2d':
                    bitmap_filename = tobj_data[rec_i + 2]
                    filepath = make_texture_filepath(tobj_filepath, bitmap_filename)
                    rec_i += 3
                elif tobj_data[rec_i + 1] == 'cube':
                    bitmap_filename = tobj_data[rec_i + 2]  # NOTE: Only first bitmap from Cube Map is used here.
                    # print('  bitmap_filename: %s' % str(bitmap_filename))
                    filepath = make_texture_filepath(tobj_filepath, bitmap_filename)
                    rec_i += 8
                    break  # NOTE: Stop searching the file after first texture. (temporal)
            elif rec == 'addr':
                pass
            rec_i += 1
    return filepath


def get_skeleton_relative_filepath(armature, directory, default_name):
    """Get's skeleton relative path to given directory. This path can be used for linking
    skeletons in PIM and PIA files.

    :param armature: armature object which will be used as scs skeleton
    :type armature: bpy.types.Object
    :param directory: directory from which relative path of skeleton should be gotten
    :type directory: str
    :param default_name: if custom path is empty this name will be used as the name of pis file
    :type default_name: str
    :return: relative path to predicted PIS file of given armature
    :rtype: str
    """

    skeleton_custom_dir = armature.scs_props.scs_skeleton_custom_export_dirpath
    skeleton_custom_name = armature.scs_props.scs_skeleton_custom_name

    skeleton_path = ""
    if skeleton_custom_dir != "":
        if skeleton_custom_dir.startswith("//"):
            skeleton_path = os.path.relpath(os.path.join(_get_scs_globals().scs_project_path, skeleton_custom_dir[2:]), directory)
        else:
            lprint("E Custom skeleton export path is not relative to SCS Project Base Path.\n\t   " +
                   "Custom path will be ignored, which might lead to wrongly linked skeleton file inside PIM and PIA files.")

    skeleton_name = (skeleton_custom_name if skeleton_custom_name != "" else default_name) + ".pis"

    return os.path.join(skeleton_path, skeleton_name)


def get_animations_relative_filepath(scs_root, directory):
    """Get's skeleton relative path to given directory. This path can be used for linking
    skeletons in PIM and PIA files.

    :param scs_root: scs root object of this animation
    :type scs_root: bpy.types.Object
    :param directory: directory from which relative path of animaton should be gotten
    :type directory: str
    :return: relative path to predicted PIS file of given armature
    :rtype: str
    """

    anims_path = ""

    if scs_root.scs_props.scs_root_object_allow_anim_custom_path:
        animations_custom_dir = scs_root.scs_props.scs_root_object_anim_export_filepath

        if animations_custom_dir != "":

            if animations_custom_dir.startswith("//"):
                anims_path = os.path.relpath(os.path.join(_get_scs_globals().scs_project_path, animations_custom_dir[2:]), directory)
            else:
                return None

    return anims_path


def get_global_export_path():
    """Gets global export path.
    If default export path is empty and blend file is saved inside current scs project path  -> return blend file dir;
    Otherwise return scs project path combined with default export path.
    :return: global export path defined by directory of saved blend file and default export path from settings
    :rtype: str
    """

    scs_project_path = _get_scs_globals().scs_project_path
    is_blend_file_within_base = bpy.data.filepath != "" and bpy.data.filepath.startswith(scs_project_path)
    default_export_path = bpy.context.scene.scs_props.default_export_filepath

    # if not set try to use Blender filepath
    if default_export_path == "" and is_blend_file_within_base:
        return os.path.dirname(bpy.data.filepath)
    else:
        return os.path.join(scs_project_path, default_export_path.strip("//"))


def get_custom_scs_root_export_path(root_object):
    """Gets custom export file path for given SCS Root Object.
    If custom export path is empty and blend file is saved inside current scs project path -> return blend file dir;
    Otherwise return scs porject path combined with custom scs root export path.
    :param root_object: scs root object
    :type root_object: bpy.types.Object
    :return: custom export directory path of given SCS Root Object; None if custom export for SCS Root is disabled
    :rtype: str | None
    """
    scs_project_path = _get_scs_globals().scs_project_path
    is_blend_file_within_base = bpy.data.filepath != "" and bpy.data.filepath.startswith(scs_project_path)

    custom_filepath = None
    if root_object.scs_props.scs_root_object_allow_custom_path:
        scs_root_export_path = root_object.scs_props.scs_root_object_export_filepath
        # if not set try to use Blender filepath
        if scs_root_export_path == "" and is_blend_file_within_base:
            custom_filepath = os.path.dirname(bpy.data.filepath)
        else:
            custom_filepath = os.path.join(scs_project_path, scs_root_export_path.strip("//"))

    return custom_filepath
