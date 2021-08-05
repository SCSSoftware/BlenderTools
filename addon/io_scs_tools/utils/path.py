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

# Copyright (C) 2013-2019: SCS Software


import bpy
import os
import subprocess
import shutil
from sys import platform
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

_KNOWN_PROJECT_BASES = ("base_vehicle", "base_share", "base")


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
        # presuming that equality of first two chars means we are on same mount point
        if startswith(repaired_path[:2], repaired_base_path[:2]):
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


def get_possible_project_infixes(include_zero_infix=False):
    """Gets possible project infixes in relation to currently selected SCS Project Path.
    If path is ending with "dlc_" prefixed directory, then first infix is parent dlc.
    Then possible base prefixes are added (sibling and parent known bases).

    If alternative bases are disabled no extra infixes are added except zero infix if requested.

    :param include_zero_infix: should empty infix be included into the list
    :type include_zero_infix: bool
    :return: list of possible project infixes
    :rtype: list[str]
    """

    infixes = []

    if include_zero_infix:
        infixes.append("")

    if not _get_scs_globals().use_alternative_bases:
        return infixes

    project_path = _get_scs_globals().scs_project_path
    project_path_basename = os.path.basename(project_path)

    # dlc infixes
    if project_path_basename.startswith("dlc_"):
        infixes.append(str((os.pardir + os.sep) * 2) + project_path_basename)

    # base infixes
    for known_base in _KNOWN_PROJECT_BASES:
        infixes.extend((os.pardir + os.sep + known_base, str((os.pardir + os.sep) * 2) + known_base))

    return infixes


def get_abs_path(path_in, subdir_path='', is_dir=False, skip_mod_check=False):
    """Gets absolute path to the "SCS Project Base Path" if given path is relative (starts with: "//"),
    otherwise original path is returned.
    If relative path is existing and valid, it returns the absolute path, otherwise None.
    Optionally a subdir_path can be provided, which will be added to the 'SCS Project Base Path'.
    If skipping of mod check is not specified then function will also try to look in two
    parent base directories, in the case "SCS Project Base Path" is currently set to mod/dlc package.

    :param path_in: Absolute or relative path to current 'SCS Project Base path'
    :type path_in: str
    :param subdir_path: Additional subdirs can be provided, they will be added to the 'SCS Project Base Path'
    :type subdir_path: str
    :param is_dir: flag specifying if given path should be directory
    :type is_dir: bool
    :param skip_mod_check: flag specifying if check for dlc/mod should be skipped
    :type skip_mod_check: bool
    :return: Absolute path or None
    :rtype: str
    """

    # correct skip mod check switch if usage of alternative bases is switched off by user
    skip_mod_check |= not _get_scs_globals().use_alternative_bases

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

    # use subdir_path as last item, so that if file/dir not found we return correct abs path, not the last checked from parents dir
    infixes = get_possible_project_infixes() + [subdir_path, ]
    existance_check = os.path.isdir if is_dir else os.path.isfile

    while infixes and result is not None and not existance_check(result) and not skip_mod_check:
        result = get_abs_path(path_in, subdir_path=infixes.pop(0), is_dir=is_dir, skip_mod_check=True)

    return result


def get_abs_paths(filepath, is_dir=False, include_nonexist_alternative_bases=False, use_infixed_search=False):
    """Gets existing absolute paths to the "SCS Project Base Path" including searching for "base" folder
    one and two levels higher in filesystem hierachy.

    :param filepath: relative or absolute filepath
    :type filepath: str
    :param is_dir: flag specifying if given path should be directory
    :type is_dir: bool
    :param include_nonexist_alternative_bases: flag specifying if none existing absolute filepaths from alternative bases should be included in result
    :type include_nonexist_alternative_bases: bool
    :param use_infixed_search: search also for infixed filepaths? Meant for infixed library SII file searching eg. sign.dlc_north.sii
    :type use_infixed_search: bool
    :return: list of absolute paths or empty list if path not found
    :rtype: list[str]
    """

    abs_paths = {}
    """
    Store paths in dictionary to easily filter out duplicated paths.
    So make sure to use normalized paths as keys and actual paths as values which should be returned as result.
    """

    existance_check = os.path.isdir if is_dir else os.path.isfile

    for sub_dir in get_possible_project_infixes(include_zero_infix=True):

        infixed_abs_path = get_abs_path(filepath, subdir_path=sub_dir, is_dir=is_dir, skip_mod_check=True)

        # additionally search for infixed files (eg. sign.dlc_north.sii)
        if use_infixed_search:
            infixed_files = get_all_infixed_file_paths(infixed_abs_path)
        else:
            infixed_files = [infixed_abs_path]

        for resulted_path in infixed_files:

            # ignore not found paths
            if resulted_path is None:
                continue

            # create normalized path to properly gather only unique paths
            normalized_resulted_path = full_norm(resulted_path)
            if (include_nonexist_alternative_bases or existance_check(resulted_path)) and normalized_resulted_path not in abs_paths:
                abs_paths[normalized_resulted_path] = resulted_path

    # we are returning de-normalized paths, as they might be used in printout and precious information
    # about origin of the path can be lost. (Eg. library was found in parent "base" directory,
    # but if we return normalized path this information will be lost)
    return abs_paths.values()


def is_valid_shader_texture_path(shader_texture):
    """It returns True if there is valid Shader Texture file, otherwise False.

    :param shader_texture: SCS texture path, can be absolute or relative
    :type shader_texture: str
    :return: True if there is valid Shader Texture file, otherwise False
    :rtype: bool
    """
    if shader_texture != "":

        if shader_texture.startswith("//"):  # RELATIVE PATH

            shader_texture_abs_path = get_abs_path(shader_texture)

            if shader_texture_abs_path and os.path.isfile(shader_texture_abs_path):
                return True

        else:  # ABSOLUTE PATH

            if os.path.isfile(shader_texture):
                return True

    return False


def is_valid_shader_presets_library_path():
    """It returns True if there is valid "*.txt" file in
    the Shader Presets Library directory, otherwise False."""

    scs_globals = _get_scs_globals()

    # check if default presets path is valid
    if not scs_globals.shader_presets_use_custom:
        return get_shader_presets_filepath() != ""

    # check if set custom preset path is valid
    shader_presets_filepath = scs_globals.shader_presets_filepath
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


def is_valid_trigger_actions_rel_path():
    """It returns True if there is valid "*.sii" file in
    the Trigger Actions directory, otherwise False."""
    trig_actions_abs_path = get_abs_path(_get_scs_globals().trigger_actions_rel_path)
    if trig_actions_abs_path:
        if os.path.isfile(trig_actions_abs_path):
            return True
        else:
            return False
    else:
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
    the resulting unit hookup directory or it's sub-directories, otherwise False."""
    hookup_library_abs_path = get_abs_path(_get_scs_globals().hookup_library_rel_path, is_dir=True)
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


def is_valid_sun_profiles_library_path():
    """It returns True if there is valid "*.sii" file in
    the Sun Profiles Library directory, otherwise False."""
    sun_profiles_lib_path = get_abs_path(_get_scs_globals().sun_profiles_lib_path)

    if sun_profiles_lib_path:
        if os.path.isfile(sun_profiles_lib_path):
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


def get_texture_path_from_tobj(tobj_filepath, raw_value=False):
    """Get absolute path of texture from given tobj filepath.
    If raw value is requested returned path is direct value written in TOBJ.
    NOTE: there is no safety check if file exists.

    :param tobj_filepath: absolute tobj file path
    :type tobj_filepath: str
    :param raw_value: flag for indicating if texture path shall be returned as it's written in TOBJ
    :type raw_value: bool
    :return: absolute texture file path if found or None
    :rtype: str | None
    """
    texture_paths = get_texture_paths_from_tobj(tobj_filepath, raw_value=raw_value, first_only=True)

    if not texture_paths:
        return None

    return texture_paths[0]


def get_texture_paths_from_tobj(tobj_filepath, raw_value=False, first_only=False):
    """Get absolute path(s) of textures from given tobj filepath.
    If raw value is requested returned path(s) are direct values written in TOBJ.
    If first only is requested only first path is returned.

    :param tobj_filepath: absolute tobj file path
    :type tobj_filepath: str
    :param raw_value: flag for indicating if texture path(s) shall be returned as it's written in TOBJ
    :type raw_value: bool
    :param first_only: flag for requesting only first entry from TOBJ map names (only first texture)
    :type first_only: bool
    :return: absolute texture file path(s) if found or None
    :rtype: tuple[str] | None
    """
    from io_scs_tools.internals.containers.tobj import TobjContainer

    container = TobjContainer.read_data_from_file(tobj_filepath, skip_validation=raw_value)
    tobj_dir, tobj_filename = os.path.split(tobj_filepath)

    if container is None:
        return None

    if raw_value:
        if first_only:
            return container.map_names[0],

        return tuple(container.map_names)

    abs_texture_paths = []
    for map_name in container.map_names:
        if map_name[0] == "/":
            curr_abs_tobj_path = get_abs_path("//" + map_name[1:])
        else:
            curr_abs_tobj_path = os.path.join(tobj_dir, map_name)

        # directly intercept and return first texture path
        if first_only:
            return curr_abs_tobj_path,

        abs_texture_paths.append(curr_abs_tobj_path)

    return tuple(abs_texture_paths)


def get_texture_extens_and_strip_path(texture_path):
    """Gets all supported texture extensions and strips given input path for any of it.

    :param texture_path: shader texture raw path value
    :type texture_path: str
    :return: list of extensions and stripped path as tuple
    :rtype: tuple[list[str], str]
    """

    extensions = [".tobj", ".tga", ".png"]

    # strip of any extensions ( endswith is most secure, because of possible multiple extensions )
    if texture_path.endswith(".tobj"):

        extensions.insert(0, texture_path[-5:])
        texture_path = texture_path[:-5]

    elif texture_path.endswith(".tga") or texture_path.endswith(".png"):

        extensions.insert(0, texture_path[-4:])
        texture_path = texture_path[:-4]

    return extensions, texture_path


def get_scs_texture_str(texture_string):
    """Get texture string as presented in SCS files: "/material/environment/vehicle_reflection"
    without any file extensions. Input path can also have texture object extension or supported images extensions.
    Path will be searched and returned in this order:
    1. relative path on current SCS Project Base Path
    2. relative path on parent base dirs of current SCS Project Base Path in the case of mod/dlc
    3. find absolute file path
    4. return unchanged texture string path

    :param texture_string: texture string for which texture should be found e.g.: "/material/environment/vehicle_reflection" or absolute path
    :type texture_string: str
    :return: relative path to texture object or absolute path to texture object or unchanged texture string
    :rtype: str
    """

    scs_project_path = _get_scs_globals().scs_project_path
    orig_texture_string = texture_string

    # remove any directory separators left overs from different platform
    texture_string = texture_string.replace("/", os.sep).replace("\\", os.sep)

    extensions, texture_string = get_texture_extens_and_strip_path(texture_string)

    # if texture string starts with scs project path we can directly strip of project path
    if startswith(texture_string, scs_project_path):
        texture_string = texture_string[len(scs_project_path):]
    else:  # check if texture string came from base project while scs project path is in dlc/mod folder

        # first find longest matching path
        try:
            common_path_len = len(os.path.commonpath([scs_project_path, texture_string]))
        except ValueError:  # if ValueError is raised then paths do not match for sure, thus set it to 0
            common_path_len = 0

        nonmatched_path_part = texture_string[common_path_len + 1:]

        if nonmatched_path_part.startswith("base" + os.sep) or nonmatched_path_part.startswith("base_") or nonmatched_path_part.startswith("dlc_"):

            # now check if provided texture string is the same as:
            # current scs project path + one or two directories up + non matched path of the part
            # NOTE: find calls is inverted in relation to number of parents dirs
            for infix, find_calls_count in (("..", 2), (".." + os.sep + "..", 1)):

                modif_texture_string = os.path.join(scs_project_path, infix + os.sep + nonmatched_path_part)

                # we got a hit if one or two directories up is the same path as texture string
                if is_samepath(modif_texture_string, texture_string):
                    slash_idx = 0
                    for _ in range(0, find_calls_count):
                        slash_idx = nonmatched_path_part.find(os.sep, slash_idx)

                    # catch invalid cases that needs investigation
                    assert slash_idx != -1

                    texture_string = nonmatched_path_part[slash_idx:]

    # check for relative TOBJ, TGA, PNG
    for ext in extensions:
        texture_path = get_abs_path("//" + texture_string.strip(os.sep) + ext)
        if texture_path and os.path.isfile(texture_path):
            return "//" + texture_string.replace(os.sep, "/").strip("/") + ext

    # check for absolute TOBJ, TGA, PNG
    for ext in extensions:
        texture_path = get_abs_path(texture_string + ext, skip_mod_check=True)
        if texture_path and os.path.isfile(texture_path):
            return texture_string.replace(os.sep, "/") + ext

    return orig_texture_string


def get_tobj_path_from_shader_texture(shader_texture, check_existance=True):
    """Gets TOBJ path from shader texture value if exists, otherwise returning None.

    :param shader_texture: shader texture raw path value
    :type shader_texture: str
    :param check_existance: flag indicating if tobj path should be also checked for existance
    :type check_existance: bool
    :return: TOBJ absolute path or None if not found
    :rtype: str | None
    """

    # strip of any extensions ( endswith is most secure, because of possible multiple extensions )
    if shader_texture.endswith(".tobj"):
        tobj_filpath = shader_texture
    elif shader_texture.endswith(".tga") or shader_texture.endswith(".png"):
        tobj_filpath = shader_texture[:-4] + ".tobj"
    else:
        tobj_filpath = shader_texture + ".tobj"

    # NOTE: if there is no existence check then we also shouldn't check for mods file system structure
    tobj_filpath = get_abs_path(tobj_filpath, skip_mod_check=not check_existance)
    if not check_existance or (tobj_filpath and os.path.isfile(tobj_filpath)):
        return tobj_filpath

    return None


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

            # if custom skeleton path and default skeleton path ere the same relpath will result in ".",
            # now if we use that in returning join function, then our skeleton path will look like "./skeleton.pis" which is not correct.
            # So instead just reset skeleton path to empty string and join will return only skeleton name as it should.
            if skeleton_path == ".":
                skeleton_path = ""

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
    is_blend_file_within_base = bpy.data.filepath != "" and startswith(bpy.data.filepath, scs_project_path)
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
    is_blend_file_within_base = bpy.data.filepath != "" and startswith(bpy.data.filepath, scs_project_path)

    custom_filepath = None
    if root_object.scs_props.scs_root_object_allow_custom_path:
        scs_root_export_path = root_object.scs_props.scs_root_object_export_filepath
        # if not set try to use Blender filepath
        if scs_root_export_path == "" and is_blend_file_within_base:
            custom_filepath = os.path.dirname(bpy.data.filepath)
        else:
            custom_filepath = os.path.join(scs_project_path, scs_root_export_path.strip("//"))

    return custom_filepath


def get_all_infixed_file_paths(filepath, include_given_path=True):
    """Gets files from same directory using any infixed word without,
    however dot can not appear in infix.

    :param filepath: absolute filepath which shall be checked for any infixed files
    :type filepath: str
    :param include_given_path: if True given file path will be included in returning list otherwise no
    :type include_given_path: bool
    :return: list of all infixed files; optionally given filepath can be added to result list too
    :rtype: list[str]
    """

    # in-fixed file paths can not be searched upon none, so return empty list
    if filepath is None:
        return []

    infixed_filepaths = [filepath] if include_given_path else []

    orig_dir, orig_file = os.path.split(filepath)

    # if original directory doesn't exists skip searching for any infix files
    if not os.path.isdir(orig_dir):
        return infixed_filepaths

    last_ext_i = orig_file.rfind(".")

    orig_file_prefix = orig_file[:last_ext_i]
    orig_file_postfix = orig_file[last_ext_i:]

    for file in os.listdir(orig_dir):

        # if given file path is already prefixed make sure to ignore it
        if file == orig_file:
            continue

        if file.startswith(orig_file_prefix) and file.endswith(orig_file_postfix) and file.count(".") == 2:
            infixed_filepaths.append(os.path.join(orig_dir, file))

    return infixed_filepaths


def get_projects_paths(game_project_path):
    """Gets list of all projects inside givem game project path.

    NOTE: function is not checking wether given path is real game project or not,
    rather it just searches for mod and dlc projects.

    :param game_project_path: directory where game repo is located
    :type game_project_path: str
    :return: paths of all mod and dlc projects found in game project
    :rtype: list[str]
    """

    project_paths = []
    for dir_entry in os.listdir(game_project_path):

        # projects can not be files so ignore them
        if os.path.isfile(os.path.join(game_project_path, dir_entry)):
            continue

        if dir_entry == "base" or dir_entry.startswith("base_") or dir_entry.startswith("dlc_"):

            project_paths.append(readable_norm(os.path.join(game_project_path, dir_entry)))

        elif dir_entry.startswith("mod_"):

            mod_dir = os.path.join(game_project_path, dir_entry)
            for dir_entry2 in os.listdir(mod_dir):

                # projects can not be files so ignore them
                if os.path.isfile(os.path.join(mod_dir, dir_entry)):
                    continue

                if dir_entry2 == "base" or dir_entry2.startswith("base_") or dir_entry2.startswith("dlc_"):
                    project_paths.append(readable_norm(os.path.join(mod_dir, dir_entry2)))

    return project_paths


def startswith(path1, path2):
    """Checks if first given path starts with second given path.
    It also takes into account windows drive letter which can be big or small.

    :param path1: first path
    :type path1: str
    :param path2: second path
    :type path2: str
    :return: True if path1 starts with path2; False otherwise
    :rtype: bool
    """

    norm_path1 = full_norm(path1)
    norm_path2 = full_norm(path2)

    return norm_path1.startswith(norm_path2)


def is_samepath(path1, path2):
    """Checks if paths are the same
    It also takes into account windows drive letter which can be big or small.

    :param path1: first path
    :type path1: str
    :param path2: second path
    :type path2: str
    :return: True if path1 starts with path2; False otherwise
    :rtype: bool
    """

    norm_path1 = full_norm(path1)
    norm_path2 = full_norm(path2)

    return norm_path1 == norm_path2


def full_norm(path1):
    """Normalize path.
    It also takes into account windows drive letter which can be big or small.

    :param path1: path
    :type path1: str
    :return: normalized path
    :rtype: str
    """

    norm_path1 = os.path.normpath(path1)
    norm_path1 = os.path.normcase(norm_path1)

    return norm_path1


def readable_norm(path):
    """Normalize path in nice human readable form.
    On windows it also converts backslashes to forward ones, to have cross platform output.

    :param path: path to normalize
    :type path: str
    :return: normalized path
    :rtype: str
    """
    norm_path = os.path.normpath(path)
    norm_path = norm_path.replace("\\", "/")

    return norm_path


def ensure_symlink(src, dest):
    """Ensures symbolic link from source to destination. On Windows junction links are used
    to avoid problems with link creation rights.

    :param src: directory or file path from which should be taken as source for creation of symbolic link
    :type src: str
    :param dest: directory or file path where symbolic link should be written
    :type dest: str
    """

    if os.path.isdir(dest):
        os.remove(dest)  # use os.remove instead os.unlink, as we can't remove mklink junction with os.unlink.

    if platform == "win32":
        subprocess.check_call(["mklink", "/J", dest, src], shell=True)
    else:
        os.symlink(src, dest)


def rmtree(src):
    """Remove directory or file. In case of directory all the content inside will also be removed.
    :param src: source path which should be recursively removed
    :type src: str
    """
    try:
        shutil.rmtree(src)
    except shutil.Error:
        lprint("E Problem removing directory: %r", (readable_norm(src),))


def copytree(src, dest):
    """Recursively copy whole tree of given source path to destination path.
    If directories doesn't exists they will be created.
    If directores/files exists then content will be overwritten.

    :param src: source path to copy from
    :type src: str
    :param dest: destination path to copy to
    :type dest: str
    """

    for root, dirs, files in os.walk(src):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(src, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)

            shutil.copyfile(os.path.join(root, file), os.path.join(dest_path, file))


def get_tree_size(src):
    """Return total size of files in given path and subdirs.

    :param src: source path to get size from
    :param src: str
    """
    total = 0

    if not os.path.isdir(src) and not os.path.isfile(src):
        return total

    for entry in os.scandir(src):
        if entry.is_dir(follow_symlinks=False):
            total += get_tree_size(entry.path)
        else:
            total += entry.stat(follow_symlinks=False).st_size

    return total
