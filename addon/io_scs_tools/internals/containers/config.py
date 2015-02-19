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
from io_scs_tools.utils import path as _path
from io_scs_tools.utils import property as _property
from io_scs_tools.utils import info as _info
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.containers import pix as _pix
from io_scs_tools.internals.containers import sii as _sii
from io_scs_tools.internals.structure import SectionData as _SectionData


def write_file(container, filepath, ind, postfix=""):
    """Data container export into file.

    :param container: List of SCS PIx Sections
    :type container: list[structures.SectionData]
    :param filepath: Config absolute Filepath
    :type filepath: str
    :param ind: Indentation string for the File
    :type ind: str
    :param postfix: Postfix to be added to the end of the filename (optional)
    :type postfix: str
    """
    path, ext = os.path.splitext(filepath)
    export_filepath = str(path + postfix + ext)
    _pix.write_data_to_file(container, export_filepath, ind)


def update_item_in_file(item_pointer, new_value):
    """Resaves config file with updated given item to a new value.
    The "item_pointer" variable must be in form of 'SectionName.PropertyName',
    example: 'Paths.ProjectPath'."""
    # print('  > update_item_in_config_file...')
    filepath = get_config_filepath()
    ind = '    '
    config_container = _pix.get_data_from_file(filepath, ind)

    if _get_scs_globals().config_update_lock:
        return False
    else:
        new_settings_container = []
        if config_container:

            new_value_changed = False
            item_pointer_split = item_pointer.split('.', 1)
            for section in config_container:

                new_section = _SectionData(section.type)
                for prop in section.props:
                    if section.type == item_pointer_split[0] and prop[0] == item_pointer_split[1]:
                        new_section.props.append((prop[0], new_value))
                        new_value_changed = True
                    else:
                        new_section.props.append((prop[0], prop[1]))

                # append new properties if they are not yet there
                if not new_value_changed and section.type == item_pointer_split[0]:
                    new_section.props.append((item_pointer_split[1], new_value))

                new_settings_container.append(new_section)

        write_file(new_settings_container, filepath, ind)
    return True


def update_shader_presets_path(scs_shader_presets_inventory, shader_presets_filepath):
    """The function deletes and populates again a list of Shader Preset items in inventory. It also updates corresponding record in config file.

    :param shader_presets_filepath: Absolute or relative path to the file with Shader Presets
    :type shader_presets_filepath: str
    """
    # print('shader_presets_filepath: %r' % shader_presets_filepath)
    if shader_presets_filepath.startswith(str(os.sep + os.sep)):  # RELATIVE PATH
        shader_presets_abs_path = _path.get_abs_path(shader_presets_filepath)
    else:
        shader_presets_abs_path = shader_presets_filepath

    # CLEAR INVENTORY
    scs_shader_presets_inventory.clear()

    if os.path.isfile(shader_presets_abs_path):

        # ADD DEFAULT PRESET ITEM "<none>" INTO INVENTORY
        new_shader_preset = scs_shader_presets_inventory.add()
        new_shader_preset.name = "<none>"
        presets_container = _pix.get_data_from_file(shader_presets_abs_path, '    ')

        # ADD ALL PRESET ITEMS FROM FILE INTO INVENTORY
        if presets_container:
            for section in presets_container:
                if section.type == "Shader":
                    for prop in section.props:
                        if prop[0] == "PresetName":
                            preset_name = prop[1]
                            # print(' + preset name: "%s"' % preset_name)
                            new_shader_preset = scs_shader_presets_inventory.add()
                            new_shader_preset.name = preset_name
    else:
        lprint('\nW The file path "%s" is not valid!', shader_presets_abs_path)

    update_item_in_file('Paths.ShaderPresetsFilePath', shader_presets_filepath)


def update_sign_library_rel_path(scs_sign_model_inventory, sign_library_rel_path):
    """The function deletes and populates again a list of Sign names in inventory. It also updates corresponding record in config file.

    :param sign_library_rel_path: Relative path to the directory with Sign files
    :type sign_library_rel_path: str
    """
    sign_library_filepath = _path.get_abs_path(sign_library_rel_path)
    if sign_library_filepath:
        sign_container = _sii.get_data_from_file(sign_library_filepath)
        if sign_container:

            # CLEAR INVENTORY
            scs_sign_model_inventory.clear()

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in sign_container:
                if item.type == 'sign_model':
                    if item.id.startswith('sign.'):
                        if 'sign_name' in item.props:
                            sign_name = item.props['sign_name']
                        else:
                            continue

                        sign_item = scs_sign_model_inventory.add()
                        sign_item.name = sign_name
                        sign_item.item_id = item.id[5:]

                        if 'model_desc' in item.props:
                            sign_item.model_desc = item.props['model_desc']

                        if 'look_name' in item.props:
                            sign_item.look_name = item.props['look_name']

                        if 'category' in item.props:
                            sign_item.category = item.props['category']

                        if 'dynamic' in item.props:
                            if item.props['dynamic'] == 'true':
                                sign_item.dynamic = True

        else:
            print('   sign_library_rel_path: "%s"' % str(sign_library_rel_path))
        # print('  sign_library_filepath:\n%s' % str(sign_library_filepath))

        update_item_in_file('Paths.SignRelFilePath', sign_library_rel_path)


def update_tsem_library_rel_path(scs_tsem_profile_inventory, tsem_library_rel_path):
    """The function deletes and populates again a list of Traffic Semaphore Profile names in inventory. It also updates corresponding record in
    config file.

    :param tsem_library_rel_path: Relative path to the directory with Traffic Semaphore Profile files
    :type tsem_library_rel_path: str
    """
    tsem_library_filepath = _path.get_abs_path(tsem_library_rel_path)
    if tsem_library_filepath:
        tsem_container = _sii.get_data_from_file(tsem_library_filepath)
        if tsem_container:

            # CLEAR INVENTORY
            scs_tsem_profile_inventory.clear()

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in tsem_container:
                if item.type == 'tr_semaphore_profile':
                    if item.id.startswith('tr_sem_prof.'):
                        if 'name' in item.props:
                            tsem_name = item.props['name']
                        else:
                            continue

                        tsem_item = scs_tsem_profile_inventory.add()
                        tsem_item.name = tsem_name
                        tsem_item.item_id = item.id[12:]

                        if 'model' in item.props:
                            tsem_item.model = item.props['model'][0]

        else:
            print('   tsem_library_rel_path: "%s"' % str(tsem_library_rel_path))

        update_item_in_file('Paths.TSemProfileRelFilePath', tsem_library_rel_path)


def update_traffic_rules_library_rel_path(scs_traffic_rules_inventory, traffic_rules_library_rel_path):
    """The function deletes and populates again a list of Traffic Rules names in inventory. It also updates corresponding record in config file.

    :param traffic_rules_library_rel_path: Relative path to the directory with Traffic Rules files
    :type traffic_rules_library_rel_path: str
    """
    traffic_rules_library_filepath = _path.get_abs_path(traffic_rules_library_rel_path)
    if traffic_rules_library_filepath:
        trul_container = _sii.get_data_from_file(traffic_rules_library_filepath)
        if trul_container:

            # CLEAR INVENTORY
            scs_traffic_rules_inventory.clear()

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in trul_container:
                if item.type == 'traffic_rule_data':
                    if item.id.startswith('traffic_rule.'):
                        traffic_rule_item = scs_traffic_rules_inventory.add()
                        traffic_rule_item.name = item.id[13:]
                        # traffic_rule_item.item_id = item.id[13:]

                        if 'rule' in item.props:
                            traffic_rule_item.rule = item.props['rule']

                        if 'num_params' in item.props:
                            traffic_rule_item.num_params = str(item.props['num_params'])

        else:
            print('   traffic_rules_library_rel_path: "%s"' % str(traffic_rules_library_rel_path))

        update_item_in_file('Paths.TrafficRulesRelFilePath', traffic_rules_library_rel_path)


def update_hookup_library_rel_path(scs_hookup_inventory, hookup_library_rel_path):
    """The function deletes and populates again a list of Hookup names in inventory. It also updates corresponding record in config file.

    :param hookup_library_rel_path: Relative path to the directory with Hookup files
    :type hookup_library_rel_path: str
    """
    abs_path = _path.get_abs_path(hookup_library_rel_path)
    if abs_path:

        # CLEAR INVENTORY
        scs_hookup_inventory.clear()

        # READ ALL "SII" FILES IN INVENTORY FOLDER
        for root, dirs, files in os.walk(abs_path):
            # print('   root: "%s"\n  dirs: "%s"\n files: "%s"' % (root, dirs, files))
            for file in files:
                if file.endswith(".sii"):
                    filepath = os.path.join(root, file)
                    # print('   filepath: "%s"' % str(filepath))
                    hookup_container = _sii.get_data_from_file(filepath)

                    # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
                    if hookup_container:
                        for item in hookup_container:
                            # if item.type == 'sign_model':
                            if item.id.startswith('_'):
                                continue
                            else:
                                hookup_file = scs_hookup_inventory.add()
                                hookup_file.name = str(item.type + " : " + item.id)
                                hookup_file.item_id = item.id

                                if 'model' in item.props:
                                    hookup_file.model = item.props['model']

                                if 'brand_idx' in item.props:
                                    try:
                                        hookup_file.brand_idx = int(item.props['brand_idx'])
                                    except:
                                        pass

                                if 'dir_type' in item.props:
                                    hookup_file.dir_type = item.props['dir_type']

                                if 'low_poly_only' in item.props:
                                    if item.props['low_poly_only'] == 'true':
                                        hookup_file.low_poly_only = True

            if '.svn' in dirs:
                dirs.remove('.svn')  # ignore SVN

    update_item_in_file('Paths.HookupRelDirPath', hookup_library_rel_path)


def update_matsubs_inventory(scs_matsubs_inventory, matsubs_library_rel_path):
    """The function deletes and populates again a list of Material Substance names in inventory. It also updates corresponding record in config file.

    :param matsubs_library_rel_path: Relative path to the directory with Material Substance files
    :type matsubs_library_rel_path: str
    """
    matsubs_library_filepath = _path.get_abs_path(matsubs_library_rel_path)
    if matsubs_library_filepath:
        matsubs_container = _sii.get_data_from_file(matsubs_library_filepath)
        if matsubs_container:

            # CLEAR INVENTORY
            scs_matsubs_inventory.clear()

            # ADD "NONE" ITEM IN INVENTORY
            matsubs_item = scs_matsubs_inventory.add()
            matsubs_item.name = "None"
            matsubs_item.item_id = 'none'
            matsubs_item.item_description = "No Material Substance"

            # ADD ALL THE OTHER ITEMS FROM CONTAINER INTO INVENTORY
            for item in matsubs_container:
                if item.type == 'game_substance':
                    if item.id.startswith('.'):
                        if 'name' in item.props:
                            matsubs_name = item.props['name']
                        else:
                            continue
                        matsubs_item = scs_matsubs_inventory.add()
                        matsubs_item.name = matsubs_name
                        matsubs_item.item_id = item.id[1:]
                        # matsubs_item.item_description = ""

        else:
            print('   matsubs_library_rel_path: "%s"' % str(matsubs_library_rel_path))

        update_item_in_file('Paths.MatSubsRelFilePath', matsubs_library_rel_path)


def gather_default():
    """Creates a new setting container for saving to the file."""

    def fill_header_section():
        """Fills up "Header" section."""
        section = _SectionData("Header")
        section.props.append(("FormatVersion", 1))
        blender_version, blender_build = _info.get_blender_version()
        section.props.append(("Source", "Blender " + blender_version + blender_build + ", SCS Blender Tools " + str(_info.get_tools_version(

        ))))
        section.props.append(("Type", "Configuration"))
        section.props.append(("Note", "User settings of SCS Blender Tools"))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
        section.props.append(("DumpLevel", _property.get_default(bpy.types.GlobalSCSProps.dump_level)))
        return section

    def fill_paths_section():
        """Fills up "Paths" section."""
        section = _SectionData("Paths")
        section.props.append(("ProjectPath", _property.get_default(bpy.types.GlobalSCSProps.scs_project_path)))
        section.props.append(("", ""))
        section.props.append(("ShaderPresetsFilePath", _property.get_default(bpy.types.GlobalSCSProps.shader_presets_filepath)))
        # section.props.append(("CgFXTemplatesFilePath", _get_scs_globals().cgfx_templates_filepath))
        # section.props.append(("CgFXRelDirPath", _get_scs_globals().cgfx_library_rel_path))
        section.props.append(("SignRelFilePath", _property.get_default(bpy.types.GlobalSCSProps.sign_library_rel_path)))
        section.props.append(("TSemProfileRelFilePath", _property.get_default(bpy.types.GlobalSCSProps.tsem_library_rel_path)))
        section.props.append(("TrafficRulesRelFilePath", _property.get_default(bpy.types.GlobalSCSProps.traffic_rules_library_rel_path)))
        section.props.append(("HookupRelDirPath", _property.get_default(bpy.types.GlobalSCSProps.hookup_library_rel_path)))
        section.props.append(("MatSubsRelFilePath", _property.get_default(bpy.types.GlobalSCSProps.matsubs_library_rel_path)))
        return section

    def fill_import_section():
        """Fills up "Import" section."""
        section = _SectionData("Import")
        section.props.append(("ImportScale", _property.get_default(bpy.types.GlobalSCSProps.import_scale)))
        section.props.append(("ImportPimFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pim_file))))
        section.props.append(("AutoWelding", int(_property.get_default(bpy.types.GlobalSCSProps.auto_welding))))
        section.props.append(("ImportPitFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pit_file))))
        section.props.append(("LoadTextures", int(_property.get_default(bpy.types.GlobalSCSProps.load_textures))))
        section.props.append(("ImportPicFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pic_file))))
        section.props.append(("ImportPipFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pip_file))))
        section.props.append(("ImportPisFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pis_file))))
        section.props.append(("ConnectedBones", int(_property.get_default(bpy.types.GlobalSCSProps.connected_bones))))
        section.props.append(("BoneImportScale", _property.get_default(bpy.types.GlobalSCSProps.bone_import_scale)))
        section.props.append(("ImportPiaFile", int(_property.get_default(bpy.types.GlobalSCSProps.import_pia_file))))
        section.props.append(("IncludeSubdirsForPia", int(_property.get_default(bpy.types.GlobalSCSProps.include_subdirs_for_pia))))
        section.props.append(("MeshCreationType", _property.get_default(bpy.types.GlobalSCSProps.mesh_creation_type)))
        return section

    def fill_export_section():
        """Fills up "Export" section."""
        section = _SectionData("Export")
        section.props.append(("ContentType", _property.get_default(bpy.types.GlobalSCSProps.content_type)))
        section.props.append(("ExportScale", _property.get_default(bpy.types.GlobalSCSProps.export_scale)))
        section.props.append(("ApplyModifiers", int(_property.get_default(bpy.types.GlobalSCSProps.apply_modifiers))))
        section.props.append(("ExcludeEdgesplit", int(_property.get_default(bpy.types.GlobalSCSProps.exclude_edgesplit))))
        section.props.append(("IncludeEdgesplit", int(_property.get_default(bpy.types.GlobalSCSProps.include_edgesplit))))
        section.props.append(("ActiveUVOnly", int(_property.get_default(bpy.types.GlobalSCSProps.active_uv_only))))
        section.props.append(("ExportVertexGroups", int(_property.get_default(bpy.types.GlobalSCSProps.export_vertex_groups))))
        section.props.append(("ExportVertexColor", int(_property.get_default(bpy.types.GlobalSCSProps.export_vertex_color))))
        section.props.append(("ExportVertexColorType", _property.get_default(bpy.types.GlobalSCSProps.export_vertex_color_type)))
        section.props.append(("ExportVertexColorType7", _property.get_default(bpy.types.GlobalSCSProps.export_vertex_color_type_7)))
        # section.props.append(("ExportAnimFile", info.get_default_prop_value(bpy.types.GlobalSCSProps.export_anim_file)))
        section.props.append(("ExportPimFile", int(_property.get_default(bpy.types.GlobalSCSProps.export_pim_file))))
        section.props.append(("OutputType", _property.get_default(bpy.types.GlobalSCSProps.output_type)))
        section.props.append(("ExportPitFile", int(_property.get_default(bpy.types.GlobalSCSProps.export_pit_file))))
        section.props.append(("ExportPicFile", int(_property.get_default(bpy.types.GlobalSCSProps.export_pic_file))))
        section.props.append(("ExportPipFile", int(_property.get_default(bpy.types.GlobalSCSProps.export_pip_file))))
        section.props.append(("SignExport", int(_property.get_default(bpy.types.GlobalSCSProps.sign_export))))
        return section

    def fill_global_display_section():
        """Fills up "GlobalDisplay" section."""
        section = _SectionData("GlobalDisplay")
        section.props.append(("DisplayLocators", int(_property.get_default(bpy.types.SceneSCSProps.display_locators))))
        section.props.append(("LocatorSize", _property.get_default(bpy.types.SceneSCSProps.locator_size)))
        section.props.append(("LocatorEmptySize", _property.get_default(bpy.types.SceneSCSProps.locator_empty_size)))
        section.props.append(("DisplayCurves", int(_property.get_default(bpy.types.SceneSCSProps.display_connections))))
        section.props.append(("CurveSegments", _property.get_default(bpy.types.SceneSCSProps.curve_segments)))
        section.props.append(("DisplayTextInfo", _property.get_default(bpy.types.SceneSCSProps.display_info)))
        return section

    def fill_global_colors_section():
        """Fills up "GlobalColors" section."""
        section = _SectionData("GlobalColors")
        section.props.append(("PrefabLocatorsWire", tuple(_property.get_default(bpy.types.SceneSCSProps.locator_prefab_wire_color))))
        section.props.append(("ModelLocatorsWire", tuple(_property.get_default(bpy.types.SceneSCSProps.locator_model_wire_color))))
        section.props.append(("ColliderLocatorsWire", tuple(_property.get_default(bpy.types.SceneSCSProps.locator_coll_wire_color))))
        section.props.append(("ColliderLocatorsFace", tuple(_property.get_default(bpy.types.SceneSCSProps.locator_coll_face_color))))
        section.props.append(("NavigationCurveBase", tuple(_property.get_default(bpy.types.SceneSCSProps.np_connection_base_color))))
        section.props.append(("MapLineBase", tuple(_property.get_default(bpy.types.SceneSCSProps.mp_connection_base_color))))
        section.props.append(("TriggerLineBase", tuple(_property.get_default(bpy.types.SceneSCSProps.tp_connection_base_color))))
        section.props.append(("InfoText", tuple(_property.get_default(bpy.types.SceneSCSProps.info_text_color))))
        return section

    '''
    def fill_various_section():
        """Fills up "Various" section."""
        section = data_SectionData("Various")
        section.props.append(("DumpLevel", _get_scs_globals().dump_level))
        return section
    '''

    # DATA CREATION
    header_section = fill_header_section()
    paths_section = fill_paths_section()
    import_section = fill_import_section()
    export_section = fill_export_section()
    global_display_section = fill_global_display_section()
    global_colors_section = fill_global_colors_section()
    # various_section = fill_various_section()

    # DATA ASSEMBLING
    config_container = [header_section, paths_section, import_section, export_section, global_display_section, global_colors_section]
    # config_container.append(various_section)

    return config_container


def new_config_file(filepath):
    """Creates a new config file at given location and name."""
    config_container = gather_default()
    ind = "    "
    success = _pix.write_data_to_file(config_container, filepath, ind)
    if success:
        return filepath
    else:
        return None


def get_config_filepath():
    """Returns a valid filepath to "config.txt" file. If the file doesn't exists it creates empty one."""
    scs_installation_dirs = _path.get_addon_installation_paths()

    # SEARCH FOR CONFIG...
    scs_config_file = ''
    for i, location in enumerate(scs_installation_dirs):
        test_path = os.path.join(location, 'config.txt')
        if os.path.isfile(test_path):
            scs_config_file = test_path
            break

    # IF NO CONFIG FILE, CREATE ONE...
    if scs_config_file == '':
        scs_config_file = new_config_file(os.path.join(scs_installation_dirs[0], 'config.txt'))
        # print('\tMaking "config.txt" file:\n\t  "%s"\n' % os.path.join(scs_installation_dirs[0], 'config.txt'))

    # print('SCS Blender Tools Config File:\n  "%s"\n' % os.path.join(scs_installation_dirs[0], 'config.txt'))
    return scs_config_file


def apply_settings():
    """Applies all the settings to the active scene."""

    config_container = _pix.get_data_from_file(get_config_filepath(), "    ")

    _get_scs_globals().config_update_lock = True
    # print('  > apply_settings...')
    settings_file_valid = 0
    for section in config_container:
        if settings_file_valid == 2:
            if section.type == "Paths":
                for prop in section.props:
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "ProjectPath":
                        _get_scs_globals().scs_project_path = prop[1]
                    elif prop[0] == "ShaderPresetsFilePath":
                        _get_scs_globals().shader_presets_filepath = prop[1]
                    # elif prop[0] == "CgFXTemplatesFilePath":
                    # _get_scs_globals().cgfx_templates_filepath = prop[1]
                    # elif prop[0] == "CgFXRelDirPath":
                    # _get_scs_globals().cgfx_library_rel_path = prop[1]
                    elif prop[0] == "SignRelFilePath":
                        _get_scs_globals().sign_library_rel_path = prop[1]
                    elif prop[0] == "TSemProfileRelFilePath":
                        _get_scs_globals().tsem_library_rel_path = prop[1]
                    elif prop[0] == "TrafficRulesRelFilePath":
                        _get_scs_globals().traffic_rules_library_rel_path = prop[1]
                    elif prop[0] == "HookupRelDirPath":
                        _get_scs_globals().hookup_library_rel_path = prop[1]
                    elif prop[0] == "MatSubsRelFilePath":
                        _get_scs_globals().matsubs_library_rel_path = prop[1]
                    else:
                        lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
            elif section.type == "Import":
                for prop in section.props:
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "ImportScale":
                        _get_scs_globals().import_scale = float(prop[1])
                    elif prop[0] == "ImportPimFile":
                        _get_scs_globals().import_pim_file = prop[1]
                    elif prop[0] == "AutoWelding":
                        _get_scs_globals().auto_welding = prop[1]
                    elif prop[0] == "ImportPitFile":
                        _get_scs_globals().import_pit_file = prop[1]
                    elif prop[0] == "LoadTextures":
                        _get_scs_globals().load_textures = prop[1]
                    elif prop[0] == "ImportPicFile":
                        _get_scs_globals().import_pic_file = prop[1]
                    elif prop[0] == "ImportPipFile":
                        _get_scs_globals().import_pip_file = prop[1]
                    elif prop[0] == "ImportPisFile":
                        _get_scs_globals().import_pis_file = prop[1]
                    elif prop[0] == "ConnectedBones":
                        _get_scs_globals().connected_bones = prop[1]
                    elif prop[0] == "BoneImportScale":
                        _get_scs_globals().bone_import_scale = float(prop[1])
                    elif prop[0] == "ImportPiaFile":
                        _get_scs_globals().import_pia_file = prop[1]
                    elif prop[0] == "IncludeSubdirsForPia":
                        _get_scs_globals().include_subdirs_for_pia = prop[1]
                    elif prop[0] == "MeshCreationType":
                        _get_scs_globals().mesh_creation_type = prop[1]
            elif section.type == "Export":
                for prop in section.props:
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "ContentType":
                        _get_scs_globals().content_type = prop[1]
                    elif prop[0] == "ExportScale":
                        _get_scs_globals().export_scale = float(prop[1])
                    elif prop[0] == "ApplyModifiers":
                        _get_scs_globals().apply_modifiers = prop[1]
                    elif prop[0] == "ExcludeEdgesplit":
                        _get_scs_globals().exclude_edgesplit = prop[1]
                    elif prop[0] == "IncludeEdgesplit":
                        _get_scs_globals().include_edgesplit = prop[1]
                    elif prop[0] == "ActiveUVOnly":
                        _get_scs_globals().active_uv_only = prop[1]
                    elif prop[0] == "ExportVertexGroups":
                        _get_scs_globals().export_vertex_groups = prop[1]
                    elif prop[0] == "ExportVertexColor":
                        _get_scs_globals().export_vertex_color = prop[1]
                    elif prop[0] == "ExportVertexColorType":
                        _get_scs_globals().export_vertex_color_type = str(prop[1])
                    elif prop[0] == "ExportVertexColorType7":
                        _get_scs_globals().export_vertex_color_type_7 = str(prop[1])
                    # elif prop[0] == "ExportAnimFile":
                    # _get_scs_globals().export_anim_file = prop[1]
                    elif prop[0] == "ExportPimFile":
                        _get_scs_globals().export_pim_file = prop[1]
                    elif prop[0] == "OutputType":
                        _get_scs_globals().output_type = prop[1]
                    elif prop[0] == "ExportPitFile":
                        _get_scs_globals().export_pit_file = prop[1]
                    elif prop[0] == "ExportPicFile":
                        _get_scs_globals().export_pic_file = prop[1]
                    elif prop[0] == "ExportPipFile":
                        _get_scs_globals().export_pip_file = prop[1]
                    elif prop[0] == "SignExport":
                        _get_scs_globals().sign_export = prop[1]
            elif section.type == "GlobalDisplay":
                for prop in section.props:
                    pass
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "DisplayLocators":
                    bpy.context.scene.scs_props.display_locators = prop[1]
                elif prop[0] == "LocatorSize":
                    bpy.context.scene.scs_props.locator_size = float(prop[1])
                elif prop[0] == "LocatorEmptySize":
                    bpy.context.scene.scs_props.locator_empty_size = float(prop[1])
                elif prop[0] == "DisplayConnections":
                    bpy.context.scene.scs_props.display_connections = prop[1]
                elif prop[0] == "CurveSegments":
                    bpy.context.scene.scs_props.curve_segments = prop[1]
                elif prop[0] == "OptimizedConnsDrawing":
                    bpy.context.scene.scs_props.optimized_connections_drawing = prop[1]
                elif prop[0] == "DisplayTextInfo":
                    bpy.context.scene.scs_props.display_info = prop[1]
                else:
                    lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
            elif section.type == "GlobalColors":
                for prop in section.props:
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "PrefabLocatorsWire":
                        bpy.context.scene.scs_props.locator_prefab_wire_color = prop[1]
                    elif prop[0] == "ModelLocatorsWire":
                        bpy.context.scene.scs_props.locator_model_wire_color = prop[1]
                    elif prop[0] == "ColliderLocatorsWire":
                        bpy.context.scene.scs_props.locator_coll_wire_color = prop[1]
                    elif prop[0] == "ColliderLocatorsFace":
                        bpy.context.scene.scs_props.locator_coll_face_color = prop[1]
                    elif prop[0] == "NavigationCurveBase":
                        bpy.context.scene.scs_props.np_connection_base_color = prop[1]
                    elif prop[0] == "MapLineBase":
                        bpy.context.scene.scs_props.mp_connection_base_color = prop[1]
                    elif prop[0] == "TriggerLineBase":
                        bpy.context.scene.scs_props.tp_connection_base_color = prop[1]
                    elif prop[0] == "InfoText":
                        bpy.context.scene.scs_props.info_text_color = prop[1]
                    else:
                        lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
            elif section.type == "Various":
                for prop in section.props:
                    # if prop[0] == "#":
                    if prop[0] in ("", "#"):
                        pass
                    elif prop[0] == "DumpLevel":
                        _get_scs_globals().dump_level = prop[1]
        elif section.type == "Header":
            for prop in section.props:
                if prop[0] == "FormatVersion":
                    if prop[1] == 1:
                        settings_file_valid += 1
                elif prop[0] == "Type":
                    if prop[1] == "Configuration":
                        settings_file_valid += 1
                elif prop[0] == "DumpLevel":
                    _get_scs_globals().dump_level = prop[1]

    _get_scs_globals().config_update_lock = False
    return True