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
import pickle
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import property as _property_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.internals.containers import pix as _pix
from io_scs_tools.internals.containers import sii as _sii
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.operators.world import SCSPathsInitialization as _SCSPathsInitialization


def update_item_in_file(item_pointer, new_value):
    """Resaves config file with updated given item to a new value.
    The "item_pointer" variable must be in form of 'SectionName.PropertyName',
    example: 'Paths.ProjectPath'."""

    # interrupt if config update is locked
    if _get_scs_globals().config_update_lock:
        return False

    # interrupt if settings storage place is set to blend file (except when config storage place itself is being updated)
    if _get_scs_globals().config_storage_place == "BlendFile" and not item_pointer == "Header.ConfigStoragePlace":
        return False

    filepath = get_config_filepath()
    ind = '    '
    config_container = _pix.get_data_from_file(filepath, ind)

    # if config container is still none, there had to be permission denied
    # by it's creation, so no sense to try to write it again
    if config_container is None:
        return False

    new_settings_container = []
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

    _pix.write_data_to_file(new_settings_container, filepath, ind)

    return True


def update_shader_presets_path(shader_presets_filepath):
    """The function deletes and populates again a list of Shader Preset items in inventory. It also updates corresponding record in config file.

    :param shader_presets_filepath: Absolute or relative path to the file with Shader Presets
    :type shader_presets_filepath: str
    """
    shader_presets_abs_path = _path_utils.get_abs_path(shader_presets_filepath)

    if _shader_presets.is_library_initialized(shader_presets_abs_path):
        lprint("I Shader presets library is up-to date, no update will happen!")
        return

    # CLEAR INVENTORY AND CACHE
    _shader_presets.clear()

    # ADD DEFAULT PRESET ITEM "<none>" INTO INVENTORY
    _shader_presets.add_section("<none>", "<none>", "", None)

    if os.path.isfile(shader_presets_abs_path):

        presets_container = _pix.get_data_from_file(shader_presets_abs_path, '    ')

        # ADD ALL SHADER PRESET ITEMS FROM FILE INTO INVENTORY
        if presets_container:

            # load all supported effects from dump file of python set or dictionary, where keys represent supported effects
            # If file is not found then generate all combinations as before.
            supported_effects_dict = None
            supported_effects_path = os.path.join(_path_utils.get_addon_installation_paths()[0], "supported_effects.bin")
            if os.path.isfile(supported_effects_path):
                try:
                    supported_effects_dict = pickle.load(open(supported_effects_path, "rb"))
                except PermissionError:
                    lprint("W Can't load supported effects file (persmission denied), please ensure read/write permissions for:\n\t   %r\n\t   "
                           "Without supported effects file invalid combinations of shader and flavors can be created!",
                           (os.path.dirname(supported_effects_path),),
                           report_warnings=1)
            else:
                lprint("W Supported effects file is missing! Make sure latest SCS Blender Tools is installed.\n\t   "
                       "Without supported effects file invalid combinations of shader and flavors can be created!",
                       report_warnings=1)

            # sort sections to shaders and flavors
            shaders = []
            flavors = {}
            for section in presets_container:
                if section.type == "Shader":
                    shaders.append(section)
                elif section.type == "Flavor":
                    flavors[section.get_prop_value("Type")] = section

            for shader in shaders:
                unique_names = []
                shader_flavors = shader.get_prop_value("Flavors")

                # create new preset item
                shader_preset_name = shader.get_prop_value("PresetName")
                shader_preset_effect = shader.get_prop_value("Effect")
                unique_names.append("")
                _shader_presets.add_section(shader_preset_effect, shader_preset_name, "", shader)

                if shader_flavors:

                    for j, flavor_types in enumerate(shader_flavors):

                        # create new flavor item
                        _shader_presets.add_flavor(shader_preset_name)

                        new_unique_names = []
                        for i, flavor_type in enumerate(flavor_types.split("|")):

                            if flavor_type not in flavors:
                                lprint("D Flavor used by shader preset, but not defined: %s", (flavor_type,))
                                continue

                            # create new flavor variant item (there can be more variants eg. "BLEND_ADD|BLEND_OVER")
                            flavor_variant_name = flavors[flavor_type].get_prop_value("Name")
                            _shader_presets.add_flavor_variant(shader_preset_name, flavor_variant_name)

                            # modify and save section as string into cache
                            for unique_name in unique_names:

                                new_unique_str = unique_name + "." + flavor_variant_name
                                new_full_effect_name = shader_preset_effect + new_unique_str

                                # check if this shader-flavor combination can exists, if not skip it
                                if supported_effects_dict and new_full_effect_name not in supported_effects_dict:
                                    lprint("S Marking none existing effect as dirty: %r", (new_full_effect_name,))
                                    is_dirty = True
                                else:
                                    is_dirty = False

                                section = _shader_presets.get_section(shader_preset_name, unique_name)

                                for flavor_section in flavors[flavor_type].sections:

                                    flavor_section_tag = flavor_section.get_prop_value("Tag")
                                    # check if current flavor section already exists in section,
                                    # then override props and sections directly otherwise add flavor section
                                    for subsection in section.sections:

                                        subsection_tag = subsection.get_prop_value("Tag")
                                        if subsection_tag and subsection_tag == flavor_section_tag:

                                            subsection.props = flavor_section.props
                                            subsection.sections = flavor_section.sections
                                            break

                                    else:
                                        section.sections.append(flavor_section)

                                new_unique_names.append(new_unique_str)
                                assert section.set_prop_value("Effect", shader_preset_effect + new_unique_str)
                                _shader_presets.add_section(shader_preset_effect, shader_preset_name, new_unique_str, section, is_dirty=is_dirty)

                        unique_names.extend(new_unique_names)

            # now as we built library it's time to clean it up of dirty items (eg. none existing effect combinations) and
            # set path from which this library was initialized
            _shader_presets.set_library_initialized(shader_presets_abs_path)

    update_item_in_file('Paths.ShaderPresetsFilePath', shader_presets_filepath)


def update_trigger_actions_rel_path(scs_trigger_actions_inventory, trigger_actions_rel_path, readonly=False):
    """The function deletes and populates again a list of Trigger Actions in inventory. It also updates corresponding record in config file.

    :param trigger_actions_rel_path: Relative path to the directory with Trigger Action files
    :type trigger_actions_rel_path: str
    """

    gathered_library_filepaths = _path_utils.get_abs_paths(trigger_actions_rel_path,
                                                           use_infixed_search=_get_scs_globals().trigger_actions_use_infixed)

    # CLEAR INVENTORY
    scs_trigger_actions_inventory.clear()

    for trig_actions_path in gathered_library_filepaths:

        lprint("D Going to parse trigger actions file:\n\t   %r", (trig_actions_path,))

        trig_actions_container = _sii.get_data_from_file(trig_actions_path)
        if trig_actions_container:

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in trig_actions_container:
                if item.type == 'trigger_action':
                    if item.id.startswith('trig_action.'):
                        if 'name' in item.props:
                            trg_action_name = item.props['name']
                        else:
                            continue

                        trig_item = scs_trigger_actions_inventory.add()
                        trig_item.name = trg_action_name + " : " + item.id[12:]
                        trig_item.item_id = item.id[12:]

    if not readonly:
        update_item_in_file('Paths.TriggerActionsRelFilePath', trigger_actions_rel_path)


def update_sign_library_rel_path(scs_sign_model_inventory, sign_library_rel_path, readonly=False):
    """The function deletes and populates again a list of Sign names in inventory. It also updates corresponding record in config file.

    :param sign_library_rel_path: Relative path to the directory with Sign files
    :type sign_library_rel_path: str
    """

    gathered_library_filepaths = _path_utils.get_abs_paths(sign_library_rel_path,
                                                           use_infixed_search=_get_scs_globals().sign_library_use_infixed)

    # CLEAR INVENTORY
    scs_sign_model_inventory.clear()

    for sign_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse sign library file:\n\t   %r", (sign_library_filepath,))

        sign_container = _sii.get_data_from_file(sign_library_filepath)
        if sign_container:

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in sign_container:
                if item.type == 'sign_model':
                    if item.id.startswith('sign.'):
                        if 'sign_name' in item.props:
                            sign_name = item.props['sign_name']
                        else:
                            continue

                        sign_item = scs_sign_model_inventory.add()
                        sign_item.name = sign_name + " : " + item.id[5:]
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

    if not readonly:
        update_item_in_file('Paths.SignRelFilePath', sign_library_rel_path)


def update_tsem_library_rel_path(scs_tsem_profile_inventory, tsem_library_rel_path, readonly=False):
    """The function deletes and populates again a list of Traffic Semaphore Profile names in inventory. It also updates corresponding record in
    config file.

    :param tsem_library_rel_path: Relative path to the directory with Traffic Semaphore Profile files
    :type tsem_library_rel_path: str
    """

    gathered_library_filepaths = _path_utils.get_abs_paths(tsem_library_rel_path,
                                                           use_infixed_search=_get_scs_globals().tsem_library_use_infixed)

    # CLEAR INVENTORY
    scs_tsem_profile_inventory.clear()

    for tsem_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse tsem library file:\n\t   %r", (tsem_library_filepath,))

        tsem_container = _sii.get_data_from_file(tsem_library_filepath)
        if tsem_container:

            # ADD ALL ITEMS FROM CONTAINER INTO INVENTORY
            for item in tsem_container:
                if item.type == 'tr_semaphore_profile':
                    if item.id.startswith('tr_sem_prof.'):
                        if 'name' in item.props:
                            tsem_name = item.props['name']
                        else:
                            continue

                        tsem_item = scs_tsem_profile_inventory.add()
                        tsem_item.name = tsem_name + " : " + item.id[12:]
                        tsem_item.item_id = item.id[12:]

                        if 'model' in item.props:
                            tsem_item.model = item.props['model'][0]

    if not readonly:
        update_item_in_file('Paths.TSemProfileRelFilePath', tsem_library_rel_path)


def update_traffic_rules_library_rel_path(scs_traffic_rules_inventory, traffic_rules_library_rel_path, readonly=False):
    """The function deletes and populates again a list of Traffic Rules names in inventory. It also updates corresponding record in config file.

    :param traffic_rules_library_rel_path: Relative path to the directory with Traffic Rules files
    :type traffic_rules_library_rel_path: str
    """

    gathered_library_filepaths = _path_utils.get_abs_paths(traffic_rules_library_rel_path,
                                                           use_infixed_search=_get_scs_globals().traffic_rules_library_use_infixed)

    # CLEAR INVENTORY
    scs_traffic_rules_inventory.clear()

    for traffic_rules_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse traffic rules file:\n\t   %r", (traffic_rules_library_filepath,))

        trul_container = _sii.get_data_from_file(traffic_rules_library_filepath)
        if trul_container:

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

    if not readonly:
        update_item_in_file('Paths.TrafficRulesRelFilePath', traffic_rules_library_rel_path)


def update_hookup_library_rel_path(scs_hookup_inventory, hookup_library_rel_path, readonly=False):
    """The function deletes and populates again a list of Hookup names in inventory. It also updates corresponding record in config file.

    :param hookup_library_rel_path: Relative path to the directory with Hookup files
    :type hookup_library_rel_path: str
    """

    # CLEAR INVENTORY
    scs_hookup_inventory.clear()

    taken_hoookup_ids = {}  # temp dict for identifying unique hookups and preventing creation of duplicates (same type and id)
    for abs_path in _path_utils.get_abs_paths(hookup_library_rel_path, is_dir=True):

        if abs_path:

            # READ ALL "SII" FILES IN INVENTORY FOLDER
            for root, dirs, files in os.walk(abs_path):

                lprint("D Going to parse hookup directory:\n\t   %r", (root,))

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
                                    typeid = str(item.type + " : " + item.id)

                                    # ignore taken type&ids
                                    if typeid in taken_hoookup_ids:
                                        continue
                                    else:
                                        taken_hoookup_ids[typeid] = True

                                    hookup_file = scs_hookup_inventory.add()
                                    hookup_file.name = typeid
                                    hookup_file.item_id = item.id

                                    if 'model' in item.props:
                                        # if model is defined as array ( appears if additional lod models are defined )
                                        # then use first none lod model
                                        if isinstance(item.props['model'], type(list())):
                                            hookup_file.model = item.props['model'][0]
                                        else:
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

    if not readonly:
        update_item_in_file('Paths.HookupRelDirPath', hookup_library_rel_path)


def update_matsubs_inventory(scs_matsubs_inventory, matsubs_library_rel_path, readonly=False):
    """The function deletes and populates again a list of Material Substance names in inventory. It also updates corresponding record in config file.

    :param matsubs_library_rel_path: Relative path to the directory with Material Substance files
    :type matsubs_library_rel_path: str
    """
    matsubs_library_filepath = _path_utils.get_abs_path(matsubs_library_rel_path)
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

    if not readonly:
        update_item_in_file('Paths.MatSubsRelFilePath', matsubs_library_rel_path)


def update_sun_profiles_library_path(scs_sun_profiles_inventory, sun_profiles_library_path, readonly=False):
    """The function deletes and populates again a list of sun profiles used for scs ligthning inside Blednder.
    It also updates corresponding record in config file.

    :param scs_sun_profiles_inventory: sun profiles inventory from scs globals
    :type scs_sun_profiles_inventory: bpy.types.CollectionProperty
    :param sun_profiles_library_path: sun profiles library path (relative to SCS Project Base Path or absolute)
    :type sun_profiles_library_path: str
    :param readonly: flag indicating if path should be updated in config file or not
    :type readonly: bool
    """
    sun_profiles_lib_filepath = _path_utils.get_abs_path(sun_profiles_library_path)

    # CLEAR INVENTORY
    scs_sun_profiles_inventory.clear()

    if sun_profiles_lib_filepath:
        sun_profiles_container = _sii.get_data_from_file(sun_profiles_lib_filepath)
        if sun_profiles_container:

            for item in sun_profiles_container:
                if item.type == 'sun_profile':

                    sun_profile_item = scs_sun_profiles_inventory.add()
                    sun_profile_item.name = item.id

                    number_props = ("low_elevation", "high_elevation", "sun_direction", "ambient_hdr_coef", "diffuse_hdr_coef",
                                    "specular_hdr_coef", "sun_color_hdr_coef", "env", "env_static_mod")
                    color_props = ("ambient", "diffuse", "specular", "sun_color")

                    # fill in numeric sun profile props
                    for number_prop in number_props:

                        item_value = item.get_prop_as_number(number_prop)

                        if item_value is not None:
                            setattr(sun_profile_item, number_prop, item_value)
                        else:
                            lprint("E Property: %r could not be parsed! Sun profile loading is incomplete." % number_prop)

                    # fill in color sun profile props
                    for color_prop in color_props:

                        item_value = item.get_prop_as_color(color_prop)

                        if item_value is not None:
                            setattr(sun_profile_item, color_prop, item_value)
                        else:
                            lprint("E Property: %r could not be parsed! Sun profile loading is incomplete." % color_prop)

    if not readonly:
        update_item_in_file('Paths.SunProfilesFilePath', sun_profiles_library_path)


def gather_default():
    """Creates a new setting container for saving to the file."""

    def fill_header_section():
        """Fills up "Header" section."""
        section = _SectionData("Header")
        section.props.append(("FormatVersion", 1))
        section.props.append(("Source", get_combined_ver_str()))
        section.props.append(("Type", "Configuration"))
        section.props.append(("Note", "User settings of SCS Blender Tools"))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
        section.props.append(("ConfigStoragePlace", _property_utils.get_by_type(bpy.types.GlobalSCSProps.config_storage_place)))
        section.props.append(("DumpLevel", _property_utils.get_by_type(bpy.types.GlobalSCSProps.dump_level)))
        return section

    def fill_paths_section():
        """Fills up "Paths" section."""
        section = _SectionData("Paths")
        section.props.append(("ProjectPath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.scs_project_path)))
        section.props.append(("", ""))
        section.props.append(("ShaderPresetsFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.shader_presets_filepath)))
        section.props.append(("TriggerActionsRelFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.trigger_actions_rel_path)))
        section.props.append(("TriggerActionsUseInfixed", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.trigger_actions_use_infixed))))
        section.props.append(("SignRelFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.sign_library_rel_path)))
        section.props.append(("SignUseInfixed", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.sign_library_use_infixed))))
        section.props.append(("TSemProfileRelFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.tsem_library_rel_path)))
        section.props.append(("TSemProfileUseInfixed", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.tsem_library_use_infixed))))
        section.props.append(("TrafficRulesRelFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.traffic_rules_library_rel_path)))
        section.props.append(("TrafficRulesUseInfixed", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.traffic_rules_library_use_infixed))))
        section.props.append(("HookupRelDirPath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.hookup_library_rel_path)))
        section.props.append(("MatSubsRelFilePath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.matsubs_library_rel_path)))
        section.props.append(("ConvertersPath", _property_utils.get_by_type(bpy.types.GlobalSCSProps.conv_hlpr_converters_path)))
        section.props.append(("UseAlternativeBases", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.use_alternative_bases))))
        return section

    def fill_import_section():
        """Fills up "Import" section."""
        section = _SectionData("Import")
        section.props.append(("ImportScale", _property_utils.get_by_type(bpy.types.GlobalSCSProps.import_scale)))
        section.props.append(("PreservePathForExport", _property_utils.get_by_type(bpy.types.GlobalSCSProps.import_preserve_path_for_export)))
        section.props.append(("ImportPimFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pim_file))))
        section.props.append(("UseWelding", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_use_welding))))
        section.props.append(("WeldingPrecision", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_welding_precision))))
        section.props.append(("UseNormals", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_use_normals))))
        section.props.append(("ImportPitFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pit_file))))
        section.props.append(("LoadTextures", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_load_textures))))
        section.props.append(("ImportPicFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pic_file))))
        section.props.append(("ImportPipFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pip_file))))
        section.props.append(("ImportPisFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pis_file))))
        section.props.append(("ConnectedBones", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_connected_bones))))
        section.props.append(("BoneImportScale", _property_utils.get_by_type(bpy.types.GlobalSCSProps.import_bone_scale)))
        section.props.append(("ImportPiaFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_pia_file))))
        section.props.append(("IncludeSubdirsForPia", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.import_include_subdirs_for_pia))))
        return section

    def fill_export_section():
        """Fills up "Export" section."""
        section = _SectionData("Export")
        section.props.append(("ExportScale", _property_utils.get_by_type(bpy.types.GlobalSCSProps.export_scale)))
        section.props.append(("ApplyModifiers", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_apply_modifiers))))
        section.props.append(("ExcludeEdgesplit", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_exclude_edgesplit))))
        section.props.append(("IncludeEdgesplit", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_include_edgesplit))))
        section.props.append(("ActiveUVOnly", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_active_uv_only))))
        section.props.append(("ExportVertexGroups", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_vertex_groups))))
        section.props.append(("ExportVertexColor", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_vertex_color))))
        section.props.append(("ExportVertexColorType", _property_utils.get_by_type(bpy.types.GlobalSCSProps.export_vertex_color_type)))
        section.props.append(("ExportVertexColorType7", _property_utils.get_by_type(bpy.types.GlobalSCSProps.export_vertex_color_type_7)))
        # section.props.append(("ExportAnimFile", info.get_default_prop_value(bpy.types.GlobalSCSProps.export_anim_file)))
        section.props.append(("ExportPimFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_pim_file))))
        section.props.append(("OutputType", _property_utils.get_by_type(bpy.types.GlobalSCSProps.output_type)))
        section.props.append(("ExportPitFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_pit_file))))
        section.props.append(("ExportPicFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_pic_file))))
        section.props.append(("ExportPipFile", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_pip_file))))
        section.props.append(("SignExport", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.export_write_signature))))
        return section

    def fill_global_display_section():
        """Fills up "GlobalDisplay" section."""
        section = _SectionData("GlobalDisplay")
        section.props.append(("DisplayLocators", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.display_locators))))
        section.props.append(("LocatorSize", _property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_size)))
        section.props.append(("LocatorEmptySize", _property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_empty_size)))
        section.props.append(("DisplayConnections", int(_property_utils.get_by_type(bpy.types.GlobalSCSProps.display_connections))))
        section.props.append(("CurveSegments", _property_utils.get_by_type(bpy.types.GlobalSCSProps.curve_segments)))
        section.props.append(("DisplayTextInfo", _property_utils.get_by_type(bpy.types.GlobalSCSProps.display_info)))
        return section

    def fill_global_colors_section():
        """Fills up "GlobalColors" section."""
        section = _SectionData("GlobalColors")
        section.props.append(("PrefabLocatorsWire", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_prefab_wire_color))))
        section.props.append(("ModelLocatorsWire", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_model_wire_color))))
        section.props.append(("ColliderLocatorsWire", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_coll_wire_color))))
        section.props.append(("ColliderLocatorsFace", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.locator_coll_face_color))))
        section.props.append(("NavigationCurveBase", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.np_connection_base_color))))
        section.props.append(("MapLineBase", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.mp_connection_base_color))))
        section.props.append(("TriggerLineBase", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.tp_connection_base_color))))
        section.props.append(("InfoText", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.info_text_color))))
        section.props.append(("BasePaint", tuple(_property_utils.get_by_type(bpy.types.GlobalSCSProps.base_paint_color))))
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
    try:

        if _pix.write_data_to_file(config_container, filepath, ind):
            return filepath

    except PermissionError:

        # NOTE: as config.txt is crucial for running blender tools we have to warn user (even in 3D viewport)
        # so he can not miss the problem with creation of config file; solution also provided in message
        lprint("E Cannot create configuration file (permission denied), please ensure read/write permissions for:\n\t   %r\n\n\t   "
               "Without configuration file Blender Tools might not work as expected!",
               (os.path.dirname(filepath),),
               report_errors=1,
               report_warnings=1)

    return None


def get_config_filepath():
    """Returns a valid filepath to "config.txt" file. If the file doesn't exists it creates empty one."""
    scs_installation_dirs = _path_utils.get_addon_installation_paths()

    # SEARCH FOR CONFIG...
    scs_config_file = ''
    for i, location in enumerate(scs_installation_dirs):
        test_path = os.path.join(location, 'config.txt')
        if os.path.isfile(test_path):
            scs_config_file = test_path
            break

    # IF NO CONFIG FILE, CREATE ONE...
    if scs_config_file == '':
        lprint("S Creating new 'config.txt' file:\n\t   %r", (os.path.join(scs_installation_dirs[0], 'config.txt'),))
        scs_config_file = new_config_file(os.path.join(scs_installation_dirs[0], 'config.txt'))

    # print('SCS Blender Tools Config File:\n  "%s"\n' % os.path.join(scs_installation_dirs[0], 'config.txt'))
    return scs_config_file


def engage_config_lock():
    """Engages configuration lock to prevent writing to config.txt.

    Should be always used in pair with release_config_lock.

    Should be used when applying multiple properties to scs globals at once,
    as many of those propreties will try to update config file inside their update function.
    But we don't want another config update as we are just applying properties from the config.
    """
    _get_scs_globals().config_update_lock = True


def release_config_lock(use_paths_init_callback=False):
    """Release configuration lock.

    Should be always used in pair with engage_config_lock.

    :param use_paths_init_callback: True if paths initialization is in progress and lock should be release when done; False release lock immidiately
    :type use_paths_init_callback: bool
    """
    if use_paths_init_callback:
        _SCSPathsInitialization.append_callback(release_config_lock)
    else:
        _get_scs_globals().config_update_lock = False


def apply_settings():
    """Applies all the settings to the active scene."""

    scs_globals = _get_scs_globals()

    # avoid recursion if another apply settings is running already
    if scs_globals.config_update_lock:
        return False

    # NOTE: save file paths in extra variables and apply them on the end
    # to make sure all of the settings are loaded first.
    # This is needed as some libraries reading are driven by other values from config file.
    # For example: "use_infixed"
    scs_project_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.scs_project_path, scs_globals)
    shader_presets_filepath = _property_utils.get_by_type(bpy.types.GlobalSCSProps.shader_presets_filepath, scs_globals)
    trigger_actions_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.trigger_actions_rel_path, scs_globals)
    sign_library_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.sign_library_rel_path, scs_globals)
    tsem_library_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.tsem_library_rel_path, scs_globals)
    traffic_rules_library_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.traffic_rules_library_rel_path, scs_globals)
    hookup_library_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.hookup_library_rel_path, scs_globals)
    matsubs_library_rel_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.matsubs_library_rel_path, scs_globals)
    sun_profiles_library_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.sun_profiles_lib_path, scs_globals)
    conv_hlpr_converters_path = _property_utils.get_by_type(bpy.types.GlobalSCSProps.conv_hlpr_converters_path, scs_globals)

    # NOTE: as dump level is written in same section as config type
    # applying it directly might take place before we get information about config type
    # so it has to be saved into variable and applied only if global settings are loaded from config file
    dump_level = scs_globals.dump_level

    # lock update now, as we don't want any properties update functions to trigger rewrite of config file
    # which would lead to unwanted recursion
    engage_config_lock()

    config_container = _pix.get_data_from_file(get_config_filepath(), "    ")

    # avoid applying process of config if not present (most probably permission problems on config creation)
    if config_container is not None:

        settings_file_valid = 0
        for section in config_container:
            if settings_file_valid == 2:
                if section.type == "Paths":
                    for prop in section.props:
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "ProjectPath":
                            scs_project_path = prop[1]
                        elif prop[0] == "ShaderPresetsFilePath":
                            shader_presets_filepath = prop[1]
                        elif prop[0] == "TriggerActionsRelFilePath":
                            trigger_actions_rel_path = prop[1]
                        elif prop[0] == "TriggerActionsUseInfixed":
                            scs_globals.trigger_actions_use_infixed = prop[1]
                        elif prop[0] == "SignRelFilePath":
                            sign_library_rel_path = prop[1]
                        elif prop[0] == "SignUseInfixed":
                            scs_globals.sign_library_use_infixed = prop[1]
                        elif prop[0] == "TSemProfileRelFilePath":
                            tsem_library_rel_path = prop[1]
                        elif prop[0] == "TSemProfileUseInfixed":
                            scs_globals.tsem_library_use_infixed = prop[1]
                        elif prop[0] == "TrafficRulesRelFilePath":
                            traffic_rules_library_rel_path = prop[1]
                        elif prop[0] == "TrafficRulesUseInfixed":
                            scs_globals.traffic_rules_library_use_infixed = prop[1]
                        elif prop[0] == "HookupRelDirPath":
                            hookup_library_rel_path = prop[1]
                        elif prop[0] == "MatSubsRelFilePath":
                            matsubs_library_rel_path = prop[1]
                        elif prop[0] == "SunProfilesFilePath":
                            sun_profiles_library_path = prop[1]
                        elif prop[0] == "ConvertersPath":
                            conv_hlpr_converters_path = prop[1]
                        elif prop[0] == "UseAlternativeBases":
                            scs_globals.use_alternative_bases = prop[1]
                        else:
                            lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
                elif section.type == "Import":
                    for prop in section.props:
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "ImportScale":
                            scs_globals.import_scale = float(prop[1])
                        elif prop[0] == "PreservePathForExport":
                            scs_globals.import_preserve_path_for_export = prop[1]
                        elif prop[0] == "ImportPimFile":
                            scs_globals.import_pim_file = prop[1]
                        elif prop[0] == "UseWelding":
                            scs_globals.import_use_welding = prop[1]
                        elif prop[0] == "WeldingPrecision":
                            scs_globals.import_welding_precision = prop[1]
                        elif prop[0] == "UseNormals":
                            scs_globals.import_use_normals = prop[1]
                        elif prop[0] == "ImportPitFile":
                            scs_globals.import_pit_file = prop[1]
                        elif prop[0] == "LoadTextures":
                            scs_globals.import_load_textures = prop[1]
                        elif prop[0] == "ImportPicFile":
                            scs_globals.import_pic_file = prop[1]
                        elif prop[0] == "ImportPipFile":
                            scs_globals.import_pip_file = prop[1]
                        elif prop[0] == "ImportPisFile":
                            scs_globals.import_pis_file = prop[1]
                        elif prop[0] == "ConnectedBones":
                            scs_globals.import_connected_bones = prop[1]
                        elif prop[0] == "BoneImportScale":
                            scs_globals.import_bone_scale = float(prop[1])
                        elif prop[0] == "ImportPiaFile":
                            scs_globals.import_pia_file = prop[1]
                        elif prop[0] == "IncludeSubdirsForPia":
                            scs_globals.import_include_subdirs_for_pia = prop[1]
                elif section.type == "Export":
                    for prop in section.props:
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "ExportScale":
                            scs_globals.export_scale = float(prop[1])
                        elif prop[0] == "ApplyModifiers":
                            scs_globals.export_apply_modifiers = prop[1]
                        elif prop[0] == "ExcludeEdgesplit":
                            scs_globals.export_exclude_edgesplit = prop[1]
                        elif prop[0] == "IncludeEdgesplit":
                            scs_globals.export_include_edgesplit = prop[1]
                        elif prop[0] == "ActiveUVOnly":
                            scs_globals.export_active_uv_only = prop[1]
                        elif prop[0] == "ExportVertexGroups":
                            scs_globals.export_vertex_groups = prop[1]
                        elif prop[0] == "ExportVertexColor":
                            scs_globals.export_vertex_color = prop[1]
                        elif prop[0] == "ExportVertexColorType":
                            scs_globals.export_vertex_color_type = str(prop[1])
                        elif prop[0] == "ExportVertexColorType7":
                            scs_globals.export_vertex_color_type_7 = str(prop[1])
                        elif prop[0] == "ExportPimFile":
                            scs_globals.export_pim_file = prop[1]
                        elif prop[0] == "OutputType":
                            scs_globals.export_output_type = prop[1]
                        elif prop[0] == "ExportPitFile":
                            scs_globals.export_pit_file = prop[1]
                        elif prop[0] == "ExportPicFile":
                            scs_globals.export_pic_file = prop[1]
                        elif prop[0] == "ExportPipFile":
                            scs_globals.export_pip_file = prop[1]
                        elif prop[0] == "SignExport":
                            scs_globals.export_write_signature = prop[1]
                elif section.type == "GlobalDisplay":
                    for prop in section.props:
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "DisplayLocators":
                            scs_globals.display_locators = prop[1]
                        elif prop[0] == "LocatorSize":
                            scs_globals.locator_size = float(prop[1])
                        elif prop[0] == "LocatorEmptySize":
                            scs_globals.locator_empty_size = float(prop[1])
                        elif prop[0] == "DisplayConnections":
                            scs_globals.display_connections = prop[1]
                        elif prop[0] == "CurveSegments":
                            scs_globals.curve_segments = prop[1]
                        elif prop[0] == "OptimizedConnsDrawing":
                            scs_globals.optimized_connections_drawing = prop[1]
                        elif prop[0] == "DisplayTextInfo":
                            scs_globals.display_info = prop[1]
                        else:
                            lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
                elif section.type == "GlobalColors":
                    for prop in section.props:
                        if prop[0] in ("", "#"):
                            pass
                        elif prop[0] == "PrefabLocatorsWire":
                            scs_globals.locator_prefab_wire_color = prop[1]
                        elif prop[0] == "ModelLocatorsWire":
                            scs_globals.locator_model_wire_color = prop[1]
                        elif prop[0] == "ColliderLocatorsWire":
                            scs_globals.locator_coll_wire_color = prop[1]
                        elif prop[0] == "ColliderLocatorsFace":
                            scs_globals.locator_coll_face_color = prop[1]
                        elif prop[0] == "NavigationCurveBase":
                            scs_globals.np_connection_base_color = prop[1]
                        elif prop[0] == "MapLineBase":
                            scs_globals.mp_connection_base_color = prop[1]
                        elif prop[0] == "TriggerLineBase":
                            scs_globals.tp_connection_base_color = prop[1]
                        elif prop[0] == "InfoText":
                            scs_globals.info_text_color = prop[1]
                        elif prop[0] == "BasePaint":
                            scs_globals.base_paint_color = prop[1]
                        else:
                            lprint('W Unrecognised item "%s" has been found in setting file! Skipping...', (str(prop[0]),))
            elif section.type == "Header":
                for prop in section.props:
                    if prop[0] == "FormatVersion":
                        if prop[1] == 1:
                            settings_file_valid += 1
                    elif prop[0] == "Type":
                        if prop[1] == "Configuration":
                            settings_file_valid += 1
                    elif prop[0] == "DumpLevel":
                        dump_level = prop[1]
                    elif prop[0] == "ConfigStoragePlace":
                        scs_globals.config_storage_place = prop[1]

                        # if settings are read directly from blend file,
                        # release update lock and don't search/apply any settings further
                        if prop[1] == "BlendFile":
                            settings_file_valid += 1

                            # as dump level can be read already (it can be placed above config storage place property),
                            # reset local variable back to value that was saved with blend file
                            dump_level = scs_globals.dump_level

                            break  # to avoid further reading of header properties, so dump_level won't be overwritten unintentionally

    scs_globals.dump_level = dump_level

    # now as last apply all of the file paths
    # NOTE: applying paths is crucial for libraries
    # (they are reloaded/initiated in property update functions).
    if bpy.app.background:  # if blender runs without UI then apply libraries directly as async operator is UI depended

        scs_globals.scs_project_path = scs_project_path
        scs_globals.shader_presets_filepath = shader_presets_filepath
        scs_globals.trigger_actions_rel_path = trigger_actions_rel_path
        scs_globals.sign_library_rel_path = sign_library_rel_path
        scs_globals.tsem_library_rel_path = tsem_library_rel_path
        scs_globals.traffic_rules_library_rel_path = traffic_rules_library_rel_path
        scs_globals.hookup_library_rel_path = hookup_library_rel_path
        scs_globals.matsubs_library_rel_path = matsubs_library_rel_path
        scs_globals.sun_profiles_lib_path = sun_profiles_library_path
        scs_globals.conv_hlpr_converters_path = conv_hlpr_converters_path

    else:  # if blender is started normally use asynchronous operator to reload libraries

        bpy.ops.world.scs_paths_initialization('INVOKE_DEFAULT', paths_list=[
            {"name": "project base path", "attr": "scs_project_path", "path": scs_project_path},
            {"name": "shader presets", "attr": "shader_presets_filepath", "path": shader_presets_filepath},
            {"name": "trigger actions library", "attr": "trigger_actions_rel_path", "path": trigger_actions_rel_path},
            {"name": "sign library", "attr": "sign_library_rel_path", "path": sign_library_rel_path},
            {"name": "traffic semaphore library", "attr": "tsem_library_rel_path", "path": tsem_library_rel_path},
            {"name": "traffic rules library", "attr": "traffic_rules_library_rel_path", "path": traffic_rules_library_rel_path},
            {"name": "hookups library", "attr": "hookup_library_rel_path", "path": hookup_library_rel_path},
            {"name": "material substance library", "attr": "matsubs_library_rel_path", "path": matsubs_library_rel_path},
            {"name": "sun profiles library", "attr": "sun_profiles_lib_path", "path": sun_profiles_library_path},
            {"name": "converters file path", "attr": "conv_hlpr_converters_path", "path": conv_hlpr_converters_path},
        ])

    # release lock as properties are applied
    release_config_lock(use_paths_init_callback=not bpy.app.background)

    return True
