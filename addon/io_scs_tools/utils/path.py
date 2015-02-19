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
        if path.startswith(repaired_base_path):
            rel_path = repaired_path.replace(repaired_base_path, os.sep)
            # print('rel_path:\n\t"%s"' % rel_path)
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

    if path_in.startswith(str(os.sep + os.sep)):
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
        if shader_presets_filepath.startswith(str(os.sep + os.sep)):  # RELATIVE PATH
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


def get_blenderfilewise_abs_filepath(raw_filepath, data_type="Global export"):
    """Takes a file path and path type and returns the same file path as absolute
    (relatively to the current saved Blender file) or None (if no/invalid path has
    been set and Blender file wasn't saved yet).

    :param raw_filepath: Filepath as obtained from a source
    :type raw_filepath: str
    :param data_type: Type of filepath (optional - only for messages)
    :type data_type: str
    :return: Absolute filepath or None
    :rtype: str
    """
    # print(' RAW filepath:\n%r' % str(raw_filepath))

    blend_dir = os.path.split(str(bpy.data.filepath))[0]

    if raw_filepath == str(os.sep + os.sep):
        filepath = str(blend_dir + os.sep)
        # print(' ABS filepath:\n%r' % str(filepath))
        return filepath
    else:
        if os.path.isdir(raw_filepath):
            filepath = raw_filepath
            # print(' ABS filepath:\n%r' % str(filepath))
        else:
            if raw_filepath == "":
                if blend_dir == "":
                    filepath = ""
                else:
                    filepath = str(blend_dir + os.sep)
            else:
                filepath = str(blend_dir + os.sep + raw_filepath.strip(os.sep) + os.sep)
                # print(' REL filepath:\n%r' % str(filepath))

        # NOTE: The following condition is just a quick solution for this to make it work in various OS
        # (on Linux the valid path can be theoretically only "/", but on Windows the shortest path can be "C:\").
        if len(filepath) > 3:
            if os.path.isdir(filepath):
                return filepath
            else:
                # message = str("%s path %r is not valid!" % (data_type, str(filepath).replace("\\", "/")))
                # lprint(0, 'E ' + message)
                return None
        else:
            # message = str("Please set a valid %s path (%r doesn't appear to be valid)"
            # " or save the Blender file!" % (data_type, str(filepath).replace("\\", "/")))
            # lprint(0, 'E ' + message)
            return None