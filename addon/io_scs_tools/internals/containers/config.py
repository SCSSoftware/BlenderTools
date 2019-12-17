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
import pickle
import tempfile
from hashlib import sha256
from time import time
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.consts import Cache as _CACHE_consts
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories
from io_scs_tools.utils import load_scs_globals_from_blend as _load_scs_globals_from_blend
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.utils.property import get_default
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.internals.containers import pix as _pix
from io_scs_tools.internals.containers import sii as _sii
from io_scs_tools.internals.structure import SectionData as _SectionData


class _PathsCache:
    """Class for caching loaded inventory paths, preventing multiple inventory reload for same paths.

    The thing is that most of the time users are operating on same projects and same configurations,
    which means they will be loading same inventories all over again. Now as our inventories are saved
    globally in the addon we can skip their reload.

    So this serves as high level cache which only saves paths last modified times for each inventory type and
    gets invalid as soon as one of the paths is missing or last modified time of at least one file has changed.
    """
    __cache = {}
    """Main cache static variable, saving all cached entries."""

    def __init__(self, inventory_type):
        """Construct cache instance, for given inventory type.

        :param inventory_type: uniquse string representing invetory type for which cache will be used.
        :type inventory_type: str
        """
        self.__dict_key = inventory_type

    def is_valid(self, paths):
        """Check if given paths are cached inside the dictionary for given paths type.

        :param paths: file paths to be checked against cache
        :type paths: collections.Sequence
        :return: True if all given paths are cached and thier last modified date is recent enough; False otherwise;
        :rtype: bool
        """

        # no path is provided, also treat as invalid
        if not paths:
            return False

        # empty paths iterable, invalid
        paths_count = len(paths)
        if paths_count <= 0:
            return False

        # no entries yet, invalid
        if self.__dict_key not in _PathsCache.__cache:
            return False

        # different number of paths, invalid because
        # if more/less paths is provided, than we cached alredy,
        # we have potentially different entries in library
        if paths_count != len(_PathsCache.__cache[self.__dict_key]):
            return False

        # finally check cache for already loaded paths
        for path in paths:
            # path not yet cached, invalid
            if path not in _PathsCache.__cache[self.__dict_key]:
                break
            # last modified time is more recent than the cached one, invalid
            if os.path.getmtime(path) > _PathsCache.__cache[self.__dict_key][path]:
                break
        else:
            return True

        return False

    def clear(self):
        """Clear cached paths.
        """
        if self.__dict_key in _PathsCache.__cache:
            _PathsCache.__cache[self.__dict_key].clear()

    def add_path(self, path):
        """Adds a path last modified time into the cache. If entry exists, it will be overwritten.

        :param path: file path to be saved to cache
        :type path: str
        """

        if self.__dict_key not in _PathsCache.__cache:
            _PathsCache.__cache[self.__dict_key] = {}

        if os.path.isfile(path):
            _PathsCache.__cache[self.__dict_key][path] = os.path.getmtime(path)


class _ContainersCache:
    """Class for caching SII containers using pickle module and temporary directory, speeding up
    usage of same containers all over again.

    Once paths cache (:class: _PathsCache) fails (user restarts blender, opens multiple instances),
    this low level cache kicks in, as inventories in blend data are empty, we need to refill them,
    thus load/dump pickles, which is way faster then loading SIIs from scratch.

    During reload of inventory each opened container is dumped into temporary directory
    and next time this path is requested, cache first recovers container from temp directory or
    if not found loads SII file from scratch.
    """

    # TODO: Rather then tmp dir, we should use cache directory, which currently is not implemented in blender API, so either:
    # 1. use "user_cache_dir" from https://developer.blender.org/diffusion/BCA/browse/master/blender_cloud/appdirs.py
    # 2. wait for Blender to have implemented: https://developer.blender.org/T47684
    __tmp_dir = os.path.join(tempfile.gettempdir(), _CACHE_consts.dir_name)
    """Temporary direcrtory to which we dump loaded SII container for later reuse."""

    @staticmethod
    def __hashed_path(path):
        """Returns hashed path.

        :param path: absolute path of the container
        :type path: str
        :return: hash of concatenated last modified date string and full path name; empty string if path is non-existing
        :rtype: str
        """

        if not os.path.exists(path):
            return ""

        str_to_hash = str(os.path.getmtime(path)) + _path_utils.full_norm(path)
        file_name_hash = sha256(str_to_hash.encode('utf-8')).hexdigest()

        return os.path.join(_ContainersCache.__tmp_dir, file_name_hash)

    @staticmethod
    def __retrieve_from_cache(path):
        """Retrieves container that is cached for given path. None if not entry is found.

        :param path: absolute path to the continer we want to retrieve
        :type path: str
        :return: list of SII Units if parsing succeded; otherwise None
        :rtype: list[io_scs_tools.internals.structure.UnitData] | None
        """

        hashed_path = _ContainersCache.__hashed_path(path)

        hashed_file_exists = os.path.isfile(hashed_path)
        original_file_exists = os.path.isfile(path)

        container = None
        if original_file_exists and hashed_file_exists:  # both need to exist to retrieve
            with open(hashed_path, mode='rb') as file:
                container = pickle.load(file)
        elif hashed_file_exists:  # remove hashed entry if original file was deleted
            _path_utils.rmtree(hashed_path)

        return container

    @staticmethod
    def __cache_it(path, container):
        """Caches given container for given path. If container is None nothing will be cached.

        :param path: absolute path of the container
        :type path: str
        :param container: list of SII Units
        :type container: list[io_scs_tools.internals.structure.UnitData] | None
        """

        if not container:
            return

        tmp_dir = _ContainersCache.__tmp_dir

        # check temp directory max size and do a cleanup if cache exceeded it
        if _path_utils.get_tree_size(tmp_dir) >= _CACHE_consts.max_size:
            _path_utils.rmtree(tmp_dir)

        # ensure temp directory
        os.makedirs(tmp_dir, exist_ok=True)

        # dump the container into hashed path
        with open(_ContainersCache.__hashed_path(path), mode='wb') as file:
            pickle.dump(container, file)

    @staticmethod
    def retrieve(path):
        """Retrieve SII container for given path.

        If item is not yet in cache SII file is accessed and read directly, then cached and returned.

        :param path: absolute path of the container
        :type path: str
        :return: list of SII Units if parsing succeded; otherwise None
        :rtype: list[io_scs_tools.internals.structure.UnitData] | None
        """

        # try to retrieve cached container
        cached_container = _ContainersCache.__retrieve_from_cache(path)
        if cached_container:
            return cached_container

        # otherwise get fresh data
        sii_container = _sii.get_data_from_file(path)

        # and cache it before return
        _ContainersCache.__cache_it(path, sii_container)

        return sii_container


class _ConfigSection:
    """Class implementing common functionalities of all config sections."""

    def __init__(self, section_type):
        self.type = section_type
        self.props = {}

    def apply_settings(self, settings_to_apply=None):
        """Applies settings of this config section to scs globals in blend data.

        :param settings_to_apply: set of properties that should be applied
        :type settings_to_apply: set[str] | None
        """
        scs_globals = _get_scs_globals()

        for prop_name, prop_data in self.props.items():
            (cast_type, value, attr) = prop_data

            # if filter set is provided, ignore all props not included in it.
            if settings_to_apply and prop_name not in settings_to_apply:
                continue

            # ignore props without attribute info
            if not attr:
                continue

            setattr(scs_globals, attr, value)

    def fill_from_pix_section(self, section):
        """Fill config section with data from given pix section.

        NOTE: Unrecognized properties are ignored!

        :param section: section from which properties should be taken
        :type section: io_scs_tools.internals.structure.SectionData
        :return: fill status: True if successfully filled, False otherwise
        :rtype: bool
        """
        if section.type != self.type:
            return False

        for prop_name, prop_value in section.props:
            if prop_name in self.props:
                (cast_type, old_value, attr) = self.props[prop_name]
                self.props[prop_name] = (cast_type, cast_type(prop_value), attr)

        return True

    def get_as_pix_section(self):
        """Gets header data represented with SectionData structure class.

        :return: packed header as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData(self.type)

        for prop_name, prop_data in self.props.items():
            (cast_type, value, attr) = prop_data
            section.props.append((prop_name, cast_type(value)))

        return section


class Header(_ConfigSection):
    """Class defining main configuration settings."""

    def __init__(self):
        """Constructor."""
        super().__init__("Header")

        scs_globals = _get_scs_globals()

        self.props = {
            "FormatVersion": (int, 1, None),
            "Source": (str, get_combined_ver_str(), None),
            "Type": (str, "Configuration", None),
            "Note": (str, "User settings of SCS Blender Tools", None),
            # "Author": (str, bpy.context.user_preferences.system.author, None),
            "ConfigStoragePlace": (str, get_default(scs_globals, 'config_storage_place'), 'config_storage_place'),
            "DumpLevel": (str, get_default(scs_globals, 'dump_level'), 'dump_level')
        }

    def apply_config_storage_place(self):
        """Applies config storage place."""
        self.apply_settings(settings_to_apply=set(["ConfigStoragePlace", ]))

    def is_valid(self):
        """Tells if currently loaded header is valid or no.

        :return: True if format version and type are correct; False otherwise
        :rtype: bool
        """
        return self.props["FormatVersion"][1] == 1 and self.props["Type"][1] == "Configuration"

    def is_applicable(self):
        """Tells if settings can be applied to blender data.

        :return: True if header is valid and config storage place is set to config; False otherwise
        :rtype: bool
        """
        return self.is_valid() and self.props["ConfigStoragePlace"][1] == "ConfigFile"


class Paths(_ConfigSection):
    """Class for path settings and handling of their reload."""

    def __init__(self):
        """Constructor."""
        super().__init__("Paths")

        scs_globals = _get_scs_globals()

        self.props = {
            "ProjectPath": (str, get_default(scs_globals, 'scs_project_path'), None),
            "ShaderPresetsFilePath": (str, get_default(scs_globals, 'shader_presets_filepath'), None),
            "ShaderPresetsUseCustom": (int, get_default(scs_globals, 'shader_presets_use_custom'), 'shader_presets_use_custom'),
            "TriggerActionsRelFilePath": (str, get_default(scs_globals, 'trigger_actions_rel_path'), None),
            "TriggerActionsUseInfixed": (int, get_default(scs_globals, 'trigger_actions_use_infixed'), 'trigger_actions_use_infixed'),
            "SignRelFilePath": (str, get_default(scs_globals, 'sign_library_rel_path'), None),
            "SignUseInfixed": (int, get_default(scs_globals, 'sign_library_use_infixed'), 'sign_library_use_infixed'),
            "TSemProfileRelFilePath": (str, get_default(scs_globals, 'tsem_library_rel_path'), None),
            "TSemProfileUseInfixed": (int, get_default(scs_globals, 'tsem_library_use_infixed'), 'tsem_library_use_infixed'),
            "TrafficRulesRelFilePath": (str, get_default(scs_globals, 'traffic_rules_library_rel_path'), None),
            "TrafficRulesUseInfixed": (int, get_default(scs_globals, 'traffic_rules_library_use_infixed'), 'traffic_rules_library_use_infixed'),
            "HookupRelDirPath": (str, get_default(scs_globals, 'hookup_library_rel_path'), None),
            "MatSubsRelFilePath": (str, get_default(scs_globals, 'matsubs_library_rel_path'), None),
            "SunProfilesFilePath": (str, get_default(scs_globals, 'sun_profiles_lib_path'), None),
            "ConvertersPath": (str, get_default(scs_globals, 'conv_hlpr_converters_path'), None),
            "UseAlternativeBases": (int, get_default(scs_globals, 'use_alternative_bases'), 'use_alternative_bases'),

        }

    def apply_paths(self, load_internal=False):
        """Apllies paths settings from config or from blend file. Settings are applied directly or via asynchronous paths init operator.

        NOTE: Applying paths is crucial for libraries/inventories (they are reloaded/initiated in property update functions).
        """
        scs_globals = _get_scs_globals()

        if load_internal:
            scs_project_path = scs_globals.scs_project_path
            shader_presets_filepath = scs_globals.shader_presets_filepath
            trigger_actions_rel_path = scs_globals.trigger_actions_rel_path
            sign_library_rel_path = scs_globals.sign_library_rel_path
            tsem_library_rel_path = scs_globals.tsem_library_rel_path
            traffic_rules_library_rel_path = scs_globals.traffic_rules_library_rel_path
            hookup_library_rel_path = scs_globals.hookup_library_rel_path
            matsubs_library_rel_path = scs_globals.matsubs_library_rel_path
            sun_profiles_library_path = scs_globals.sun_profiles_lib_path
            conv_hlpr_converters_path = scs_globals.conv_hlpr_converters_path
        else:
            scs_project_path = self.props["ProjectPath"][1]
            shader_presets_filepath = self.props["ShaderPresetsFilePath"][1]
            trigger_actions_rel_path = self.props["TriggerActionsRelFilePath"][1]
            sign_library_rel_path = self.props["SignRelFilePath"][1]
            tsem_library_rel_path = self.props["TSemProfileRelFilePath"][1]
            traffic_rules_library_rel_path = self.props["TrafficRulesRelFilePath"][1]
            hookup_library_rel_path = self.props["HookupRelDirPath"][1]
            matsubs_library_rel_path = self.props["MatSubsRelFilePath"][1]
            sun_profiles_library_path = self.props["SunProfilesFilePath"][1]
            conv_hlpr_converters_path = self.props["ConvertersPath"][1]

        if bpy.app.background:  # without UI apply libraries directly as we want our tools to be to be ready for any scripts execution
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

            AsyncPathsInit.execute([
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


class Import(_ConfigSection):
    """Class for import settings."""

    def __init__(self):
        """Constructor."""
        super().__init__("Import")

        scs_globals = _get_scs_globals()

        self.props = {
            "ImportScale": (float, get_default(scs_globals, 'import_scale'), 'import_scale'),
            "PreservePathForExport": (int, get_default(scs_globals, 'import_preserve_path_for_export'), 'import_preserve_path_for_export'),
            "ImportPimFile": (int, get_default(scs_globals, 'import_pim_file'), 'import_pim_file'),
            "UseWelding": (int, get_default(scs_globals, 'import_use_welding'), 'import_use_welding'),
            "WeldingPrecision": (int, get_default(scs_globals, 'import_welding_precision'), 'import_welding_precision'),
            "UseNormals": (int, get_default(scs_globals, 'import_use_normals'), 'import_use_normals'),
            "ImportPitFile": (int, get_default(scs_globals, 'import_pit_file'), 'import_pit_file'),
            "LoadTextures": (int, get_default(scs_globals, 'import_load_textures'), 'import_load_textures'),
            "ImportPicFile": (int, get_default(scs_globals, 'import_pic_file'), 'import_pic_file'),
            "ImportPipFile": (int, get_default(scs_globals, 'import_pip_file'), 'import_pip_file'),
            "ImportPisFile": (int, get_default(scs_globals, 'import_pis_file'), 'import_pis_file'),
            "ConnectedBones": (int, get_default(scs_globals, 'import_connected_bones'), 'import_connected_bones'),
            "BoneImportScale": (float, get_default(scs_globals, 'import_bone_scale'), 'import_bone_scale'),
            "ImportPiaFile": (int, get_default(scs_globals, 'import_pia_file'), 'import_pia_file'),
            "IncludeSubdirsForPia": (int, get_default(scs_globals, 'import_include_subdirs_for_pia'), 'import_include_subdirs_for_pia'),
        }


class Export(_ConfigSection):
    """Class for export settings."""

    def __init__(self):
        """Constructor."""
        super().__init__("Export")

        scs_globals = _get_scs_globals()

        self.props = {
            "ExportScale": (float, get_default(scs_globals, 'export_scale'), 'export_scale'),
            "ApplyModifiers": (int, get_default(scs_globals, 'export_apply_modifiers'), 'export_apply_modifiers'),
            "ExcludeEdgesplit": (int, get_default(scs_globals, 'export_exclude_edgesplit'), 'export_exclude_edgesplit'),
            "IncludeEdgesplit": (int, get_default(scs_globals, 'export_include_edgesplit'), 'export_include_edgesplit'),
            "ActiveUVOnly": (int, get_default(scs_globals, 'export_active_uv_only'), 'export_active_uv_only'),
            "ExportVertexGroups": (int, get_default(scs_globals, 'export_vertex_groups'), 'export_vertex_groups'),
            "ExportVertexColor": (int, get_default(scs_globals, 'export_vertex_color'), 'export_vertex_color'),
            "ExportVertexColorType": (str, get_default(scs_globals, 'export_vertex_color_type'), 'export_vertex_color_type'),
            "ExportVertexColorType7": (str, get_default(scs_globals, 'export_vertex_color_type_7'), 'export_vertex_color_type_7'),
            # "ExportAnimFile": (int, get_default(scs_globals, 'export_anim_file'), 'export_anim_file'),
            "ExportPimFile": (int, get_default(scs_globals, 'export_pim_file'), 'export_pim_file'),
            "OutputType": (str, get_default(scs_globals, 'export_output_type'), 'export_output_type'),
            "ExportPitFile": (int, get_default(scs_globals, 'export_pit_file'), 'export_pit_file'),
            "ExportPicFile": (int, get_default(scs_globals, 'export_pic_file'), 'export_pic_file'),
            "ExportPipFile": (int, get_default(scs_globals, 'export_pip_file'), 'export_pip_file'),
            "SignExport": (int, get_default(scs_globals, 'export_write_signature'), 'export_write_signature'),
        }


class GlobalDisplay(_ConfigSection):
    """Class for global display settings."""

    def __init__(self):
        """Constructor."""
        super().__init__("GlobalDisplay")

        scs_globals = _get_scs_globals()
        self.props = {
            "DisplayLocators": (int, get_default(scs_globals, 'display_locators'), 'display_locators'),
            "DisplayPreviewModels": (int, get_default(scs_globals, 'show_preview_models'), 'show_preview_models'),
            "LocatorSize": (float, get_default(scs_globals, 'locator_size'), 'locator_size'),
            "LocatorEmptySize": (float, get_default(scs_globals, 'locator_empty_size'), 'locator_empty_size'),
            "DisplayConnections": (int, get_default(scs_globals, 'display_connections'), 'display_connections'),
            "OptimizedConnsDrawing": (int, get_default(scs_globals, 'optimized_connections_drawing'), 'optimized_connections_drawing'),
            "CurveSegments": (int, get_default(scs_globals, 'curve_segments'), 'curve_segments'),
            "DisplayTextInfo": (str, get_default(scs_globals, 'display_info'), 'display_info'),
            "IconTheme": (str, _ICONS_consts.default_icon_theme, 'icon_theme'),
        }


class GlobalColors(_ConfigSection):
    """Class for global color settings."""

    def __init__(self):
        """Constructor."""
        super().__init__("GlobalColors")

        scs_globals = _get_scs_globals()

        self.props = {
            "PrefabLocatorsWire": (tuple, get_default(scs_globals, 'locator_prefab_wire_color'), 'locator_prefab_wire_color'),
            "ModelLocatorsWire": (tuple, get_default(scs_globals, 'locator_model_wire_color'), 'locator_model_wire_color'),
            "ColliderLocatorsWire": (tuple, get_default(scs_globals, 'locator_coll_wire_color'), 'locator_coll_wire_color'),
            "ColliderLocatorsFace": (tuple, get_default(scs_globals, 'locator_coll_face_color'), 'locator_coll_face_color'),
            "NavigationCurveBase": (tuple, get_default(scs_globals, 'np_connection_base_color'), 'np_connection_base_color'),
            "MapLineBase": (tuple, get_default(scs_globals, 'mp_connection_base_color'), 'mp_connection_base_color'),
            "TriggerLineBase": (tuple, get_default(scs_globals, 'tp_connection_base_color'), 'tp_connection_base_color'),
            "InfoText": (tuple, get_default(scs_globals, 'info_text_color'), 'info_text_color'),
            "BasePaint": (tuple, get_default(scs_globals, 'base_paint_color'), 'base_paint_color'),
        }


class ConfigContainer:
    """Class implementing config container handler."""

    def __init__(self):
        """Constructor."""
        self.sections = {
            "Header": Header(),
            "Paths": Paths(),
            "Import": Import(),
            "Export": Export(),
            "GlobalDisplay": GlobalDisplay(),
            "GlobalColors": GlobalColors(),
        }

    def set_property(self, section_type, prop_name, value):
        """Set property of given section and name with new value.

        :param section_type: section type property belongs to
        :type section_type: str
        :param prop_name: name of the property that should be set
        :type prop_name: str
        :param value: new value that should be set
        :type value: any
        :return: True if section exists and property could be inserted/rewritten, False otherwise
        :rtype: bool
        """
        if section_type not in self.sections:
            return False

        cast_type, _, attr = self.sections[section_type].props[prop_name]
        self.sections[section_type].props[prop_name] = (cast_type, cast_type(value), attr)
        return True

    def apply_settings(self):
        """Apllies currently loaded settings from config container to blender data.

        :return: True if settings were applicable; False otherwise
        :rtype: bool
        """

        settings_applied = False

        if self.sections["Header"].is_valid() and not self.sections["Header"].is_applicable():
            self.sections["Header"].apply_config_storage_place()
        elif self.sections["Header"].is_applicable():
            for _, section in self.sections.items():
                section.apply_settings()
            settings_applied = True

        # apply paths on the end to make sure all of the settings are applied first.
        # This is needed as some libraries are dependend on applied settings, for example: "*_use_infixed"
        self.sections["Paths"].apply_paths(load_internal=not settings_applied)

        return settings_applied

    def fill_from_pix_container(self, pix_container):
        """Fill container from given PIX container.

        :param pix_container: pix continer from which configs should be loaded
        :type pix_container: list[io_scs_tools.internals.structure.SectionData]
        :return: True if fill was successful; False otherwise
        :rtype: bool
        """

        for section in pix_container:
            if section.type not in self.sections:
                return False

            section_filled = self.sections[section.type].fill_from_pix_section(section)
            if not section_filled:
                return False

        return True

    def get_pix_container(self):
        """Returns currently set section read for writting to with PIX writter.

        :return: all sections data as list, ready to be used by PIX writter
        :rtype: list[io_scs_tools.internals.structure.SectionData]
        """

        container = []

        for section in self.sections.values():
            container.append(section.get_as_pix_section())

        return container


class AsyncPathsInit:
    """Class for fake-asychronous paths intialization, implemented with app.timers API."""

    DUMP_LEVEL = 3
    """Constant for log level index according in SCS Globals, on which operator should printout extended report."""

    # Static running variables
    __paths_count = 0
    """Static variable holding number of all paths that had to be processed. Used for reporting progress eg. 'X of Y paths done'."""
    __paths_done = 0
    """Static variable holding number of already processed paths. Used for reporting progress eg. 'X of Y paths done'."""

    # Static data storage
    __message = ""
    """Static variable holding printout extended message. This message used only if dump level is high enough."""
    __paths_list = []
    """Static variable holding list with dictonariy entries each of them representing Filepath class entry that needs in initialization.
    Processed paths are removed on the fly.
    """
    __callbacks = []
    """Static variable holding list of callbacks that will be executed once operator is finished or cancelled.
    """

    @staticmethod
    def _report_progress(message="", abort=False, hide_controls=False):
        """Reports progress into 3D view report mechanism.

        :param message: message to report
        :type message: str
        :param abort: should abort any 3D view reports?
        :type abort: bool
        :param hide_controls: controls can be hidden if user shouldn't be able to abort 3D view reports
        :type hide_controls: bool
        """

        windows = bpy.data.window_managers[0].windows

        # we need window, otherwise 3d view report can't add modal handler for user close/minimize/scroll actions
        assert len(windows) > 0

        override = bpy.context.copy()
        override["window"] = windows[-1]  # using first one borks filebrowser UI for unknown reason, but last one works
        bpy.ops.wm.scs_tools_show_3dview_report(override, 'INVOKE_DEFAULT',
                                                message=message,
                                                abort=abort,
                                                hide_controls=hide_controls,
                                                is_progress_message=True)

    @staticmethod
    def _finish():
        """Cleanup and callbacks execution.
        """

        # reset static variables
        AsyncPathsInit.__message = ""
        AsyncPathsInit.__paths_list.clear()

        # report finished progress to 3d view report mechanism
        if int(_get_scs_globals().dump_level) < AsyncPathsInit.DUMP_LEVEL:
            AsyncPathsInit._report_progress(abort=True)

        # when done, tag everything for redraw in the case some UI components
        # are reporting status of this operator
        _view3d_utils.tag_redraw_all_regions()

        # as last invoke any callbacks and afterwards delete them
        while len(AsyncPathsInit.__callbacks) > 0:

            callback = AsyncPathsInit.__callbacks[0]

            callback()
            AsyncPathsInit.__callbacks.remove(callback)

        lprint("D Paths initialization finish invoked!")

    @staticmethod
    def _process_paths():
        """Timer function for processing paths that are currently saved in static paths list.

        :return: time after which next path should be processed; None when all paths are being processed
        :rtype: float | None
        """

        # do not proceed if list is already empty
        if len(AsyncPathsInit.__paths_list) <= 0:
            AsyncPathsInit._finish()
            lprint("I Paths initialization finished, timer unregistered!")
            return None

        scs_globals = _get_scs_globals()

        start_time = time()

        # update message with current path and apply it
        AsyncPathsInit.__message += "Initializing " + AsyncPathsInit.__paths_list[0]["name"] + "..."
        setattr(scs_globals, AsyncPathsInit.__paths_list[0]["attr"], AsyncPathsInit.__paths_list[0]["path"])

        # calculate execution time, remove processed path, update message and counter
        execution_time = time() - start_time
        AsyncPathsInit.__paths_list = AsyncPathsInit.__paths_list[1:]  # remove just processed item
        AsyncPathsInit.__message += " Done in %.2f s!\n" % execution_time
        AsyncPathsInit.__paths_done += 1

        # when executing last one, also print out hiding message
        if len(AsyncPathsInit.__paths_list) == 0:
            AsyncPathsInit.__message += "SCS Blender Tools are ready!"
            _view3d_utils.tag_redraw_all_view3d()

        # if debug then report whole progress message otherwise print out condensed message
        if int(scs_globals.dump_level) >= AsyncPathsInit.DUMP_LEVEL:
            message = AsyncPathsInit.__message
            hide_controls = False
        else:
            message = "Paths and libraries initialization %s/%s ..." % (AsyncPathsInit.__paths_done,
                                                                        AsyncPathsInit.__paths_count)
            hide_controls = True

        AsyncPathsInit._report_progress(message=message, hide_controls=hide_controls)

        # if execution was ligthing fast, process another one or more, to shorten time of initialization
        if len(AsyncPathsInit.__paths_list) > 0 and execution_time < 0.01:
            lprint("S Initalizing next path directly ...")
            return 0.01

        return 0.2

    @staticmethod
    def is_running():
        """Tells if paths initialization is still in progress.

        :return: True if scs paths initialization is still in progress; False if none instances are running
        :rtype: bool
        """
        return len(AsyncPathsInit.__paths_list) > 0 and bpy.app.timers.is_registered(AsyncPathsInit._process_paths)

    @staticmethod
    def append_callback(callback):
        """Appends given callback function to callback list. Callbacks are called once paths initialization is done.
        If operator is not running then False is returned and callback is not added to the list!
        NOTE: there is no check if given callback is already in list.

        :param callback: callback function without arguments
        :type callback: object
        :return: True if operator is running and callback is added to the list properly; False if callback won't be added and executed
        :rtype: bool
        """
        if AsyncPathsInit.is_running():
            AsyncPathsInit.__callbacks.append(callback)
            return True

        return False

    @staticmethod
    def execute(paths_list):
        """Executes asynchronous paths initialization for given paths list.

        :param paths_list: list of dictionaries of path entries: dict("name": "UI name", "attr": "name_of_attribute","path": "path_string")
        :type paths_list: list[dict[str, str]]
        """

        AsyncPathsInit.__paths_done = 0  # reset done paths counter as everything starts here

        # now fill up new paths to static inventory
        for filepath_prop in paths_list:

            # sort out only unique paths and merge them with current static path list
            old_item = None
            for item in AsyncPathsInit.__paths_list:
                if item["attr"] == filepath_prop["attr"]:
                    old_item = item
                    break

            # if old item is found just reuse it instead of adding new item to list
            if old_item:
                old_item["name"] = filepath_prop["name"]
                old_item["path"] = filepath_prop["path"]
            else:
                AsyncPathsInit.__paths_list.append(
                    {
                        "name": filepath_prop["name"],
                        "attr": filepath_prop["attr"],
                        "path": filepath_prop["path"]
                    }
                )

        # update paths counter to the current paths list length
        AsyncPathsInit.__paths_count = len(AsyncPathsInit.__paths_list)

        AsyncPathsInit.__message = "Starting initialization...\n"
        AsyncPathsInit._report_progress(message=AsyncPathsInit.__message, hide_controls=True)

        # in case any operator was previously invoked timer might still be running, so only register timer if needed
        if not bpy.app.timers.is_registered(AsyncPathsInit._process_paths):
            bpy.app.timers.register(AsyncPathsInit._process_paths, first_interval=0.2)

        lprint("I Paths initialization started...")


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

    # create config container
    config = ConfigContainer()

    filepath = get_config_filepath()
    ind = '    '
    pix_container = _pix.get_data_from_file(filepath, ind)

    # now load pix data into config container
    if pix_container and not config.fill_from_pix_container(pix_container):
        # no pix container or invalid, no sense to continue.
        lprint("E Updating item inside config file failed!")
        return False

    # update property
    section_type, prop_name = item_pointer.split('.', 1)
    config.set_property(section_type, prop_name, new_value)

    # always update source!
    config.set_property("Header", "Source", get_combined_ver_str())

    # write updated config back
    _pix.write_data_to_file(config.get_pix_container(), filepath, ind)

    return True


def update_scs_project_path(scs_project_path, reload_only=False):
    """The function triggeres reload of paths that are dependend on scs project path and updates corresponding record in config file.

    :param scs_project_path: Absolute path to the desired scs project
    :type scs_project_path: str
    :param reload_only: flag for triggereing libraries reload only
    :type reload_only: bool
    """

    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if scs_globals.config_update_lock:
        return

    # before we are locking config, we need to update project path
    if not reload_only:
        update_item_in_file('Paths.ProjectPath', scs_project_path)

    # enable update lock because we only want to reload libraries, as their paths are not changed
    engage_config_lock()

    # trigger update functions via asynchronous operator for library paths initialization
    AsyncPathsInit.execute([
        {"name": "trigger actions library", "attr": "trigger_actions_rel_path", "path": scs_globals.trigger_actions_rel_path},
        {"name": "sign library", "attr": "sign_library_rel_path", "path": scs_globals.sign_library_rel_path},
        {"name": "traffic semaphore library", "attr": "tsem_library_rel_path", "path": scs_globals.tsem_library_rel_path},
        {"name": "traffic rules library", "attr": "traffic_rules_library_rel_path", "path": scs_globals.traffic_rules_library_rel_path},
        {"name": "hookups library", "attr": "hookup_library_rel_path", "path": scs_globals.hookup_library_rel_path},
        {"name": "material substance library", "attr": "matsubs_library_rel_path", "path": scs_globals.matsubs_library_rel_path},
        {"name": "sun profiles library", "attr": "sun_profiles_lib_path", "path": scs_globals.sun_profiles_lib_path},
    ])

    # release lock as properties are applied
    release_config_lock(use_paths_init_callback=True)


def update_shader_presets_path(shader_presets_filepath, reload_only=False):
    """The function deletes and populates again a list of Shader Preset items in inventory. It also updates corresponding record in config file.

    :param shader_presets_filepath: Absolute or relative path to the file with Shader Presets
    :type shader_presets_filepath: str
    :param reload_only: flag for triggereing libraries reload only
    :type reload_only: bool
    """
    shader_presets_abs_path = _path_utils.get_abs_path(shader_presets_filepath)

    if _shader_presets.is_library_initialized(shader_presets_abs_path):
        lprint("I Shader presets library is up-to date, no update will happen!")
        return

    # prevent updating if config update is in progress ...
    if reload_only and _get_scs_globals().config_update_lock:
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
                    supported_effects_dict = pickle.load(open(supported_effects_path, mode="rb"))
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
                            _shader_presets.add_flavor_variant(shader_preset_name, flavor_type, flavor_variant_name)

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

    if not reload_only:
        update_item_in_file('Paths.ShaderPresetsFilePath', shader_presets_filepath)


def update_trigger_actions_rel_path(trigger_actions_rel_path, reload_only=False):
    """The function deletes and populates again a list of Trigger Actions in inventory. It also updates corresponding record in config file.

    :param trigger_actions_rel_path: Relative path to the directory with Trigger Action files
    :type trigger_actions_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if reload_only and scs_globals.config_update_lock:
        return

    # first update path in config file
    if not reload_only:
        update_item_in_file('Paths.TriggerActionsRelFilePath', trigger_actions_rel_path)

    gathered_library_filepaths = _path_utils.get_abs_paths(trigger_actions_rel_path, use_infixed_search=scs_globals.trigger_actions_use_infixed)
    scs_trigger_actions_inventory = _get_scs_inventories().trigger_actions

    # get cache for trigger actions
    cache = _PathsCache("TriggerActions")

    # check cache for validity and end if valid
    if cache.is_valid(gathered_library_filepaths):
        lprint("I Trigger actions library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_trigger_actions_inventory.clear()

    for trig_actions_path in gathered_library_filepaths:

        lprint("D Going to parse trigger actions file:\n\t   %r", (trig_actions_path,))

        trig_actions_container = _ContainersCache.retrieve(trig_actions_path)
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

        # now as it's loaded add it to cache
        cache.add_path(trig_actions_path)


def update_sign_library_rel_path(sign_library_rel_path, reload_only=False):
    """The function deletes and populates again a list of Sign names in inventory. It also updates corresponding record in config file.

    :param sign_library_rel_path: Relative path to the directory with Sign files
    :type sign_library_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if reload_only and scs_globals.config_update_lock:
        return

    # first update path in config file
    if not reload_only:
        update_item_in_file('Paths.SignRelFilePath', sign_library_rel_path)

    gathered_library_filepaths = _path_utils.get_abs_paths(sign_library_rel_path, use_infixed_search=scs_globals.sign_library_use_infixed)
    scs_sign_model_inventory = _get_scs_inventories().sign_models

    # get cache for sign models
    cache = _PathsCache("SignModels")

    # check cache for validity and end if valid
    if cache.is_valid(gathered_library_filepaths):
        lprint("I Sign models library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_sign_model_inventory.clear()

    for sign_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse sign library file:\n\t   %r", (sign_library_filepath,))

        sign_container = _ContainersCache.retrieve(sign_library_filepath)
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

        # now as it's loaded add it to cache
        cache.add_path(sign_library_filepath)


def update_tsem_library_rel_path(tsem_library_rel_path, reload_only=False):
    """The function deletes and populates again a list of Traffic Semaphore Profile names in inventory. It also updates corresponding record in
    config file.

    :param tsem_library_rel_path: Relative path to the directory with Traffic Semaphore Profile files
    :type tsem_library_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if reload_only and scs_globals.config_update_lock:
        return

    # first update path in config file
    if not reload_only:
        update_item_in_file('Paths.TSemProfileRelFilePath', tsem_library_rel_path)

    gathered_library_filepaths = _path_utils.get_abs_paths(tsem_library_rel_path, use_infixed_search=scs_globals.tsem_library_use_infixed)
    scs_tsem_profile_inventory = _get_scs_inventories().tsem_profiles

    # get cache for tsem profiles
    cache = _PathsCache("TsemProfiles")

    # check cache for validity and end if valid
    if cache.is_valid(gathered_library_filepaths):
        lprint("I Traffic semaphore profiles library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_tsem_profile_inventory.clear()

    for tsem_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse tsem library file:\n\t   %r", (tsem_library_filepath,))

        tsem_container = _ContainersCache.retrieve(tsem_library_filepath)
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

        # now as it's loaded add it to cache
        cache.add_path(tsem_library_filepath)


def update_traffic_rules_library_rel_path(traffic_rules_library_rel_path, reload_only=False):
    """The function deletes and populates again a list of Traffic Rules names in inventory. It also updates corresponding record in config file.

    :param traffic_rules_library_rel_path: Relative path to the directory with Traffic Rules files
    :type traffic_rules_library_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if reload_only and scs_globals.config_update_lock:
        return

    # first update path in config file
    if not reload_only:
        update_item_in_file('Paths.TrafficRulesRelFilePath', traffic_rules_library_rel_path)

    gathered_library_filepaths = _path_utils.get_abs_paths(traffic_rules_library_rel_path,
                                                           use_infixed_search=scs_globals.traffic_rules_library_use_infixed)
    scs_traffic_rules_inventory = _get_scs_inventories().traffic_rules

    # get cache for traffic rules
    cache = _PathsCache("TrafficRules")

    # check cache for validity and end if valid
    if cache.is_valid(gathered_library_filepaths):
        lprint("I Traffic rules library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_traffic_rules_inventory.clear()

    for traffic_rules_library_filepath in gathered_library_filepaths:

        lprint("D Going to parse traffic rules file:\n\t   %r", (traffic_rules_library_filepath,))

        trul_container = _ContainersCache.retrieve(traffic_rules_library_filepath)
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

        # now as it's loaded add it to cache
        cache.add_path(traffic_rules_library_filepath)


def update_hookup_library_rel_path(hookup_library_rel_path, reload_only=False):
    """The function deletes and populates again a list of Hookup names in inventory. It also updates corresponding record in config file.

    :param hookup_library_rel_path: Relative path to the directory with Hookup files
    :type hookup_library_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    scs_globals = _get_scs_globals()

    # prevent updating if config update is in progress ...
    if reload_only and scs_globals.config_update_lock:
        return

    # first update path in config file
    if not reload_only:
        update_item_in_file('Paths.HookupRelDirPath', hookup_library_rel_path)

    gathered_hookups_paths = _path_utils.get_abs_paths(hookup_library_rel_path, is_dir=True)
    scs_hookup_inventory = _get_scs_inventories().hookups

    # collect final hookups SII files from all directories
    final_hookups_sii_paths = []
    for abs_path in gathered_hookups_paths:

        if abs_path:

            # READ ALL "SII" FILES IN INVENTORY FOLDER
            for root, dirs, files in os.walk(abs_path):

                lprint("D Going to collect hookup files from directory:\n\t   %r", (root,))

                # print('   root: "%s"\n  dirs: "%s"\n files: "%s"' % (root, dirs, files))
                for file in files:
                    if file.endswith(".sii"):
                        filepath = os.path.join(root, file)
                        final_hookups_sii_paths.append(filepath)

                if '.svn' in dirs:
                    dirs.remove('.svn')  # ignore SVN

    # get cache for hookups
    cache = _PathsCache("Hookups")

    # check cache for validity and end if valid
    if cache.is_valid(final_hookups_sii_paths):
        lprint("I Hookups library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_hookup_inventory.clear()

    taken_hoookup_ids = {}  # temp dict for identifying unique hookups and preventing creation of duplicates (same type and id)
    for filepath in final_hookups_sii_paths:
        # print('   filepath: "%s"' % str(filepath))
        hookup_container = _ContainersCache.retrieve(filepath)

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

        # now as it's loaded add it to cache
        cache.add_path(filepath)


def update_matsubs_inventory(matsubs_library_rel_path, reload_only=False):
    """The function deletes and populates again a list of Material Substance names in inventory. It also updates corresponding record in config file.

    :param matsubs_library_rel_path: Relative path to the directory with Material Substance files
    :type matsubs_library_rel_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """

    # prevent updating if config update is in progress ...
    if reload_only and _get_scs_globals().config_update_lock:
        return

    matsubs_library_filepath = _path_utils.get_abs_path(matsubs_library_rel_path)
    scs_matsubs_inventory = _get_scs_inventories().matsubs

    # get cache for material substances
    cache = _PathsCache("MatSubs")

    # check cache for validity and end if valid
    if cache.is_valid((matsubs_library_filepath,)):
        lprint("I Material substance library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_matsubs_inventory.clear()

    if matsubs_library_filepath:
        matsubs_container = _ContainersCache.retrieve(matsubs_library_filepath)
        if matsubs_container:

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

        # now as it's loaded add it to cache
        cache.add_path(matsubs_library_filepath)

    if not reload_only:
        update_item_in_file('Paths.MatSubsRelFilePath', matsubs_library_rel_path)


def update_sun_profiles_library_path(sun_profiles_library_path, reload_only=False):
    """The function deletes and populates again a list of sun profiles used for scs ligthning inside Blednder.
    It also updates corresponding record in config file.

    :param sun_profiles_library_path: sun profiles library path (relative to SCS Project Base Path or absolute)
    :type sun_profiles_library_path: str
    :param reload_only: flag for triggering reload only, which will be executed under condition that config lock is not engaged
    :type reload_only: bool
    """
    if not reload_only:
        update_item_in_file('Paths.SunProfilesFilePath', sun_profiles_library_path)

    # prevent updating if config update is in progress ...
    if reload_only and _get_scs_globals().config_update_lock:
        return

    sun_profiles_lib_filepath = _path_utils.get_abs_path(sun_profiles_library_path)
    scs_sun_profiles_inventory = _get_scs_inventories().sun_profiles

    # get cache for sun profiles
    cache = _PathsCache("SunProfiles")

    # check cache for validity and end if valid
    if cache.is_valid((sun_profiles_lib_filepath,)):
        lprint("I Sun profiles library is up-to date, no update will happen!")
        return

    # clear cache & inventory
    cache.clear()
    scs_sun_profiles_inventory.clear()

    if sun_profiles_lib_filepath:
        sun_profiles_container = _ContainersCache.retrieve(sun_profiles_lib_filepath)
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

                    # as last unlock profile
                    sun_profile_item.is_blocked = False

        # now as it's loaded add it to cache
        cache.add_path(sun_profiles_lib_filepath)


def new_config_file(filepath):
    """Creates a new config file at given location and name."""
    config_container = ConfigContainer().get_pix_container()
    try:

        if _pix.write_data_to_file(config_container, filepath, "    "):
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
        AsyncPathsInit.append_callback(release_config_lock)
    else:
        _get_scs_globals().config_update_lock = False


def apply_settings(preload_from_blend=False):
    """Applies all the settings to the active scene.

    :param preload_from_blend: should load scs globals from blend file before trying to apply settings?
    :param preload_from_blend: bool
    """

    if preload_from_blend:
        _load_scs_globals_from_blend()

    scs_globals = _get_scs_globals()

    # avoid recursion if another apply settings is running already
    if scs_globals.config_update_lock:
        return False

    config_container = _pix.get_data_from_file(get_config_filepath(), "    ")

    # avoid applying process of config if not present (most probably permission problems on config creation)
    if config_container is not None:

        # lock update now, as we don't want any properties update functions to trigger
        # rewrite of config file which would lead to unwanted recursion
        engage_config_lock()

        config = ConfigContainer()
        config.fill_from_pix_container(config_container)
        config.apply_settings()

        # release lock as properties are applied
        release_config_lock(use_paths_init_callback=not bpy.app.background)

    return True
