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

# Copyright (C) 2015: SCS Software


import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       EnumProperty,
                       FloatVectorProperty)
from io_scs_tools.consts import ConvHlpr as _CONV_HLPR_consts
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_shader_presets_inventory as _get_shader_presets_inventory


class ShaderPresetsInventoryItem(bpy.types.PropertyGroup):
    """
    Shader Presets inventory on World.
    """

    class Flavor(bpy.types.PropertyGroup):
        class FlavorVariant(bpy.types.PropertyGroup):
            name = StringProperty(
                description="Name of flavor variant inside effect name"
            )
            preset_name = StringProperty(
                description="Name of the preset where this flavor variant belongs too"
            )

        variants = CollectionProperty(
            description="Represents one variant of same flavor (eg. tsnmap, tsnmapuv)",
            type=FlavorVariant
        )

    name = StringProperty(name="Shader Presets Name")
    effect = StringProperty(name="Full Effect Name")
    flavors = CollectionProperty(
        description="Collection of flavors for this shader ordered by the name of apperance in the effect name",
        type=Flavor
    )


class GlobalSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Global Variables - ...World.scs_globals...
    :return:
    """

    # TRIGGER LOCATOR ACTIONS INVENTORY
    class TriggerActionsInventory(bpy.types.PropertyGroup):
        """
        Triger Actions Inventory.
        """
        item_id = StringProperty(default="")

    scs_trigger_actions_inventory = CollectionProperty(
        type=TriggerActionsInventory,
        options={'SKIP_SAVE'},
    )

    # SIGN LOCATOR MODEL INVENTORY
    class SignModelInventory(bpy.types.PropertyGroup):
        """
        Sign Model Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model_desc = StringProperty(default="")
        look_name = StringProperty(default="")
        category = StringProperty(default="")
        dynamic = BoolProperty(default=False)

    scs_sign_model_inventory = CollectionProperty(
        type=SignModelInventory,
        options={'SKIP_SAVE'},
    )

    # TRAFFIC SEMAPHORE LOCATOR PROFILE INVENTORY
    class TSemProfileInventory(bpy.types.PropertyGroup):
        """
        Traffic Semaphore Profile Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model = StringProperty(default="")

    scs_tsem_profile_inventory = CollectionProperty(
        type=TSemProfileInventory,
        options={'SKIP_SAVE'},
    )

    # TRAFFIC RULES PROFILE INVENTORY
    class TrafficRulesInventory(bpy.types.PropertyGroup):
        """
        Traffic Rules Inventory.
        :return:
        """
        # item_id = StringProperty(default="")
        rule = StringProperty(default="")
        num_params = StringProperty(default="")

    scs_traffic_rules_inventory = CollectionProperty(
        type=TrafficRulesInventory,
        options={'SKIP_SAVE'},
    )

    # HOOKUP INVENTORY
    class HookupInventory(bpy.types.PropertyGroup):
        """
        Hookup Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        model = StringProperty(default="")
        brand_idx = IntProperty(default=0)
        dir_type = StringProperty(default="")
        low_poly_only = BoolProperty(default=False)

    scs_hookup_inventory = CollectionProperty(
        type=HookupInventory,
        options={'SKIP_SAVE'},
    )

    # MATERIAL SUBSTANCE INVENTORY
    class MatSubsInventory(bpy.types.PropertyGroup):
        """
        Material Substance Inventory.
        :return:
        """
        item_id = StringProperty(default="")
        item_description = StringProperty(default="")

    scs_matsubs_inventory = CollectionProperty(
        type=MatSubsInventory,
        options={'SKIP_SAVE'},
    )

    # TODO: rename this ShaderNamesDictionary to some generic name used for enumeration and move it to proper class
    class ShaderNamesDictionary:
        """
        Dictionary for saving unique names of shader names loaded from presets file.

        NOTE:
        Necessary to store dictionary of presets names because of blender
        restriction that enum ID properties which are generated with
        callback function needs to have references of it's items strings
        """

        def __init__(self):
            self.preset = {}

        def add(self, new_preset):
            if new_preset not in self.preset:
                self.preset[new_preset] = new_preset
            return self.preset[new_preset]

        def has(self, preset_name):
            if preset_name in self.preset:
                return True
            else:
                return False

    @staticmethod
    def get_shader_icon_str(preset_name):
        """
        Returns icon string for given preset name.

        :type preset_name: str
        :param preset_name: Name of shader preset
        :rtype: str
        """
        if preset_name != "<none>":  # The item already exists...
            if "spec" in preset_name:
                icon_str = 'MATERIAL'
            elif "glass" in preset_name:
                icon_str = 'MOD_LATTICE'
            elif "lamp" in preset_name:
                icon_str = 'LAMP_SPOT'
            elif "shadowonly" in preset_name:
                icon_str = 'MAT_SPHERE_SKY'
            elif "truckpaint" in preset_name:
                icon_str = 'AUTO'
            elif "mlaa" in preset_name:
                icon_str = 'GROUP_UVS'
            else:
                icon_str = 'SOLID'
        else:
            icon_str = None
        return icon_str

    def update_shader_presets(self, context):
        """
        Returns the actual Shader name list from "scs_shader_presets_inventory".
        It also updates "shader_presets_container", so the UI could contain all
        the items with no error. (necessary hack :-/)
        :param context:
        :return:
        """

        items = [("<none>", "<none>", "No SCS shader preset in use (may result in incorrect model output)", 'X_VEC', 0)]

        # print('  > update_shader_presets...')

        # save dictionary of preset names references in globals so that UI doesn't mess up strings
        if not "shader_presets_container" in globals():
            global shader_presets_container
            shader_presets_container = GlobalSCSProps.ShaderNamesDictionary()
            # print("Presets container created!")

        if self.shader_preset_list_sorted:
            inventory = {}
            for preset_i, preset in enumerate(_get_shader_presets_inventory()):
                inventory[preset.name] = preset_i
            for preset in sorted(inventory):
                preset_i = inventory[preset]
                act_preset = shader_presets_container.add(preset)
                # print(' + %i act_preset: %s (%s)' % (preset_i, str(act_preset), str(preset)))
                icon_str = GlobalSCSProps.get_shader_icon_str(act_preset)
                if icon_str is not None:  # if None then it's <none> preset which is already added
                    items.append((act_preset, act_preset, "", icon_str, preset_i))
        else:
            for preset_i, preset in enumerate(_get_shader_presets_inventory()):
                act_preset = shader_presets_container.add(preset.name)
                # print(' + %i act_preset: %s (%s)' % (preset_i, str(act_preset), str(preset)))
                icon_str = GlobalSCSProps.get_shader_icon_str(act_preset)
                if icon_str is not None:  # if None then it's <none> preset which is already added
                    items.append((act_preset, act_preset, "", icon_str, preset_i))
        return items

    def get_shader_presets_item(self):
        """
        Returns menu index of a Shader preset name of actual Material to set
        the right name in UI menu.
        :return:
        """
        # print('  > get_shader_presets_items...')
        material = bpy.context.active_object.active_material
        result = 0

        for preset_i, preset in enumerate(_get_shader_presets_inventory()):
            if preset.name == material.scs_props.active_shader_preset_name:
                result = preset_i

        return result

    def set_shader_presets_item(self, value):
        """
        Receives an actual index of currently selected Shader preset name in the menu,
        sets that Shader name as active in active Material.
        :param value:
        :return:
        """

        material = bpy.context.active_object.active_material
        if value == 0:  # No Shader...
            material.scs_props.active_shader_preset_name = "<none>"
            material.scs_props.mat_effect_name = "None"

            # reset material nodes when user selects none shader
            if material.node_tree:
                material.node_tree.nodes.clear()
                material.use_nodes = False

            material["scs_shader_attributes"] = {}
        else:
            for preset_i, preset in enumerate(_get_shader_presets_inventory()):
                if value == preset_i:

                    # Set Shader Preset in the Material
                    preset_section = _material_utils.get_shader_preset(_get_scs_globals().shader_presets_filepath, preset.name)

                    if preset_section:
                        preset_name = preset_section.get_prop_value("PresetName")
                        preset_effect = preset_section.get_prop_value("Effect")
                        material.scs_props.mat_effect_name = preset_effect

                        if preset_name:
                            _material_utils.set_shader_data_to_material(material, preset_section)
                            material.scs_props.active_shader_preset_name = preset_name
                        else:
                            material.scs_props.active_shader_preset_name = "<none>"
                            material["scs_shader_attributes"] = {}
                            print('    NO "preset_name"!')
                            # if preset_effect:
                            # print('      preset_effect: "%s"' % preset_effect)
                            # if preset_flags:
                            # print('      preset_flags: "%s"' % preset_flags)
                            # if preset_attribute_cnt:
                            # print('      preset_attribute_cnt: "%s"' % preset_attribute_cnt)
                            # if preset_texture_cnt:
                            # print('      preset_texture_cnt: "%s"' % preset_texture_cnt)
                    else:
                        print('''NO "preset_section"! (Shouldn't happen!)''')
                else:
                    preset.active = False

    shader_preset_list = EnumProperty(
        name="Shader Presets",
        description="Shader presets",
        items=update_shader_presets,
        get=get_shader_presets_item,
        set=set_shader_presets_item,
    )
    shader_preset_list_sorted = BoolProperty(
        name="Shader Preset List Sorted Alphabetically",
        description="Sort Shader preset list alphabetically",
        default=False,
    )

    def update_shader_preset_search_value(self, context):

        if self.shader_preset_search_value != "":

            for preset_i, preset in enumerate(_get_shader_presets_inventory()):

                if self.shader_preset_search_value == preset.name:
                    self.set_shader_presets_item(preset_i)

            self.shader_preset_search_value = ""
            self.shader_preset_use_search = False

    shader_preset_search_value = StringProperty(
        description="Search for shader preset by typing in the name. When selected shader preset will be used for this material.",
        options={'HIDDEN'},
        update=update_shader_preset_search_value
    )

    shader_preset_use_search = BoolProperty(
        description="Use search property for selecting shader preset.",
        options={'HIDDEN'}
    )

    # SCS TOOLS GLOBAL PATHS
    def scs_project_path_update(self, context):
        # Update all related paths so their libraries gets reloaded from new "SCS Project Path" location.
        if not _get_scs_globals().config_update_lock:
            _config_container.update_sign_library_rel_path(_get_scs_globals().scs_sign_model_inventory,
                                                           _get_scs_globals().sign_library_rel_path)

            _config_container.update_tsem_library_rel_path(_get_scs_globals().scs_tsem_profile_inventory,
                                                           _get_scs_globals().tsem_library_rel_path)

            _config_container.update_traffic_rules_library_rel_path(_get_scs_globals().scs_traffic_rules_inventory,
                                                                    _get_scs_globals().traffic_rules_library_rel_path)

            _config_container.update_hookup_library_rel_path(_get_scs_globals().scs_hookup_inventory,
                                                             _get_scs_globals().hookup_library_rel_path)

            _config_container.update_matsubs_inventory(_get_scs_globals().scs_matsubs_inventory,
                                                       _get_scs_globals().matsubs_library_rel_path)

            _config_container.update_item_in_file('Paths.ProjectPath', self.scs_project_path)

        return None

    def shader_presets_filepath_update(self, context):
        # print('Shader Presets Library Path UPDATE: "%s"' % self.shader_presets_filepath)
        _config_container.update_shader_presets_path(_get_shader_presets_inventory(), self.shader_presets_filepath)
        return None

    def trigger_actions_rel_path_update(self, context):
        _config_container.update_trigger_actions_rel_path(_get_scs_globals().scs_trigger_actions_inventory,
                                                          self.trigger_actions_rel_path)
        return None

    def trigger_actions_use_infixed_update(self, context):

        if not _get_scs_globals().config_update_lock:  # prevent reloading library when blender is starting
            _config_container.update_trigger_actions_rel_path(_get_scs_globals().scs_trigger_actions_inventory,
                                                              self.trigger_actions_rel_path,
                                                              readonly=True)

        _config_container.update_item_in_file('Paths.TriggerActionsUseInfixed', int(self.trigger_actions_use_infixed))

    def sign_library_rel_path_update(self, context):
        _config_container.update_sign_library_rel_path(_get_scs_globals().scs_sign_model_inventory,
                                                       self.sign_library_rel_path)
        return None

    def sign_library_use_infixed_update(self, context):

        if not _get_scs_globals().config_update_lock:  # prevent reloading library when blender is starting
            _config_container.update_sign_library_rel_path(_get_scs_globals().scs_sign_model_inventory,
                                                           self.sign_library_rel_path,
                                                           readonly=True)

        _config_container.update_item_in_file('Paths.SignUseInfixed', int(self.sign_library_use_infixed))

    def tsem_library_rel_path_update(self, context):
        _config_container.update_tsem_library_rel_path(_get_scs_globals().scs_tsem_profile_inventory,
                                                       self.tsem_library_rel_path)
        return None

    def tsem_library_use_infixed_update(self, context):

        if not _get_scs_globals().config_update_lock:  # prevent reloading library when blender is starting
            _config_container.update_tsem_library_rel_path(_get_scs_globals().scs_tsem_profile_inventory,
                                                           self.tsem_library_rel_path,
                                                           readonly=True)

        _config_container.update_item_in_file('Paths.TSemProfileUseInfixed', int(self.tsem_library_use_infixed))

    def traffic_rules_library_rel_path_update(self, context):
        _config_container.update_traffic_rules_library_rel_path(_get_scs_globals().scs_traffic_rules_inventory,
                                                                self.traffic_rules_library_rel_path)
        return None

    def traffic_rules_library_use_infixed_update(self, context):

        if not _get_scs_globals().config_update_lock:  # prevent reloading library when blender is starting
            _config_container.update_traffic_rules_library_rel_path(_get_scs_globals().scs_traffic_rules_inventory,
                                                                    self.traffic_rules_library_rel_path,
                                                                    readonly=True)

        _config_container.update_item_in_file('Paths.TrafficRulesUseInfixed', int(self.traffic_rules_library_use_infixed))
        return None

    def hookup_library_rel_path_update(self, context):
        # print('Hookup Library Path UPDATE: "%s"' % self.hookup_library_rel_path)
        _config_container.update_hookup_library_rel_path(_get_scs_globals().scs_hookup_inventory,
                                                         self.hookup_library_rel_path)
        return None

    def matsubs_library_rel_path_update(self, context):
        # print('Material Substance Library Path UPDATE: "%s"' % self.matsubs_library_rel_path)
        _config_container.update_matsubs_inventory(_get_scs_globals().scs_matsubs_inventory,
                                                   self.matsubs_library_rel_path)
        return None

    os_rs = "//"  # RELATIVE PATH SIGN - for all OSes we use // inside Blender Tools
    scs_project_path = StringProperty(
        name="SCS Project Main Directory",
        description="SCS project main directory (absolute path)",
        default="",
        # subtype="DIR_PATH",
        subtype='NONE',
        update=scs_project_path_update
    )
    shader_presets_filepath = StringProperty(
        name="Shader Presets Library",
        description="Shader Presets library file path (absolute file path; *.txt)",
        default=_path_utils.get_shader_presets_filepath(),
        subtype='NONE',
        # subtype="FILE_PATH",
        update=shader_presets_filepath_update,
    )
    trigger_actions_rel_path = StringProperty(
        name="Trigger Actions Lib",
        description="Trigger actions library (absolute or relative file path to 'SCS Project Base Directory'; *.sii)",
        default=str(os_rs + 'def/world/trigger_action.sii'),
        subtype='NONE',
        update=trigger_actions_rel_path_update,
    )
    trigger_actions_use_infixed = BoolProperty(
        name="Trigger Actions Use Infixed Files",
        description="Also load library items from any infixed SII files from same directory.",
        default=True,
        update=trigger_actions_use_infixed_update,
    )
    sign_library_rel_path = StringProperty(
        name="Sign Library",
        description="Sign library (absolute or relative file path to 'SCS Project Base Directory'; *.sii)",
        default=str(os_rs + 'def/world/sign.sii'),
        subtype='NONE',
        update=sign_library_rel_path_update,
    )
    sign_library_use_infixed = BoolProperty(
        name="Sign Library Use Infixed Files",
        description="Also load library items from any infixed SII files from same directory.",
        default=True,
        update=sign_library_use_infixed_update,
    )
    tsem_library_rel_path = StringProperty(
        name="Traffic Semaphore Profile Library",
        description="Traffic Semaphore Profile library (absolute or relative file path to 'SCS Project Base Directory'; *.sii)",
        default=str(os_rs + 'def/world/semaphore_profile.sii'),
        subtype='NONE',
        update=tsem_library_rel_path_update,
    )
    tsem_library_use_infixed = BoolProperty(
        name="Traffic Semaphore Lib Use Infixed Files",
        description="Also load library items from any infixed SII files from same directory.",
        default=True,
        update=tsem_library_use_infixed_update,
    )
    traffic_rules_library_rel_path = StringProperty(
        name="Traffic Rules Library",
        description="Traffic rules library (absolute or relative file path to 'SCS Project Base Directory'; *.sii)",
        default=str(os_rs + 'def/world/traffic_rules.sii'),
        subtype='NONE',
        update=traffic_rules_library_rel_path_update,
    )
    traffic_rules_library_use_infixed = BoolProperty(
        name="Traffic Rules Lib Use Infixed Files",
        description="Also load library items from any infixed SII files from same directory.",
        default=True,
        update=traffic_rules_library_use_infixed_update,
    )
    hookup_library_rel_path = StringProperty(
        name="Hookup Library Dir",
        description="Hookup library directory (absolute or relative path to 'SCS Project Base Directory')",
        default=str(os_rs + 'unit/hookup'),
        subtype='NONE',
        update=hookup_library_rel_path_update,
    )
    matsubs_library_rel_path = StringProperty(
        name="Material Substance Library",
        description="Material substance library (absolute or relative file path to 'SCS Project Base Directory'; *.db)",
        default=str(os_rs + 'material/material.db'),
        subtype='NONE',
        update=matsubs_library_rel_path_update,
    )

    # UPDATE LOCKS (FOR AVOIDANCE OF RECURSION)
    config_update_lock = BoolProperty(
        name="Update Lock For Config Items",
        description="Allows temporarily lock automatic updates for all items which are stored in config file",
        default=False,
    )
    import_in_progress = BoolProperty(
        name="Indicator of import process",
        description="Holds the state of SCS import process",
        default=False,
    )

    # DISPLAY SETTINGS
    def display_locators_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayLocators', int(self.display_locators))
        return None

    def locator_size_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.LocatorSize', self.locator_size)
        return None

    def locator_empty_size_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.LocatorEmptySize', self.locator_empty_size)
        return None

    def locator_prefab_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.PrefabLocatorsWire',
                                              tuple(self.locator_prefab_wire_color))
        return None

    def locator_model_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ModelLocatorsWire',
                                              tuple(self.locator_model_wire_color))
        return None

    def locator_coll_wire_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ColliderLocatorsWire',
                                              tuple(self.locator_coll_wire_color))
        return None

    def locator_coll_face_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.ColliderLocatorsFace',
                                              tuple(self.locator_coll_face_color))
        return None

    def display_connections_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayConnections', int(self.display_connections))
        return None

    def optimized_connections_drawing_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.OptimizedConnsDrawing', int(self.optimized_connections_drawing))
        return None

    def curve_segments_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.CurveSegments', self.curve_segments)
        return None

    def np_curve_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.NavigationCurveBase', tuple(self.np_connection_base_color))
        return None

    def mp_line_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.MapLineBase', tuple(self.mp_connection_base_color))
        return None

    def tp_line_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.TriggerLineBase', tuple(self.tp_connection_base_color))
        return None

    def display_info_update(self, context):
        _config_container.update_item_in_file('GlobalDisplay.DisplayTextInfo', self.display_info)
        return None

    def info_text_color_update(self, context):
        _config_container.update_item_in_file('GlobalColors.InfoText', tuple(self.info_text_color))
        return None

    def drawing_mode_update(self, context):
        from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback

        _open_gl_callback.enable(self.drawing_mode)

    def show_preview_models_update(self, context):
        """
        :param context:
        :return:
        """
        for obj in bpy.data.objects:
            if obj.type == 'EMPTY':
                if self.show_preview_models:
                    if not _preview_models.load(obj):
                        _preview_models.unload(obj)
                else:
                    _preview_models.unload(obj)
        return None

    def base_paint_color_update(self, context):
        from io_scs_tools.internals.shaders import set_base_paint_color

        for mat in bpy.data.materials:

            # ignore none-node based shaders
            if not mat.use_nodes or not mat.node_tree:
                continue

            set_base_paint_color(mat.node_tree, self.base_paint_color)

        _config_container.update_item_in_file('GlobalColors.BasePaint', tuple(self.base_paint_color))

    drawing_mode = EnumProperty(
        name="Custom Drawing Mode",
        description="Drawing mode for custom elements (Locators and Connections)",
        items=(
            ('Normal', "Normal", "Use normal depth testing drawing"),
            ('X-ray', "X-ray", "Use X-ray drawing"),
        ),
        update=drawing_mode_update
    )

    display_locators = BoolProperty(
        name="Display Locators",
        description="Display locators in 3D views",
        default=True,
        update=display_locators_update,
    )
    locator_size = FloatProperty(
        name="Locator Size",
        description="Locator display size in 3D views",
        default=1.0,
        min=0.1, max=50,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
        update=locator_size_update,
    )
    locator_empty_size = FloatProperty(
        name="Locator Empty Object Size",
        description="Locator Empty object display size in 3D views",
        default=0.05,
        min=0.05, max=0.2,
        step=0.1,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
        update=locator_empty_size_update,
    )
    locator_prefab_wire_color = FloatVectorProperty(
        name="Prefab Loc Color",
        description="Color for prefab locators in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.5, 0.5, 0.5),
        update=locator_prefab_wire_color_update,
    )
    locator_model_wire_color = FloatVectorProperty(
        name="Model Loc Color",
        description="Color for model locators in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        # default=(0.25, 0.25, 0.25),
        default=(0.08, 0.12, 0.25),
        update=locator_model_wire_color_update,
    )
    locator_coll_wire_color = FloatVectorProperty(
        name="Collider Loc Wire Color",
        description="Color for collider locators' wireframe in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.5, 0.3, 0.1),
        update=locator_coll_wire_color_update,
    )
    locator_coll_face_color = FloatVectorProperty(
        name="Collider Loc Face Color",
        description="Color for collider locators' faces in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.15, 0.05, 0.05),
        # default=(0.065, 0.18, 0.3),
        update=locator_coll_face_color_update,
    )
    display_connections = BoolProperty(
        name="Display Connections",
        description="Display connections in 3D views",
        default=True,
        update=display_connections_update,
    )
    curve_segments = IntProperty(
        name="Curve Segments",
        description="Curve segment number for displaying in 3D views",
        default=16,
        min=4, max=64,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
        update=curve_segments_update,
    )
    optimized_connections_drawing = BoolProperty(
        name="Optimized Connections Draw",
        description="Draw connections only when data are updated ( switching this off might give you FPS  )",
        default=False,
        update=optimized_connections_drawing_update,
    )
    np_connection_base_color = FloatVectorProperty(
        name="Nav Curves Color",
        description="Base color for navigation curves in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.0, 0.1167, 0.1329),
        update=np_curve_color_update,
    )
    mp_connection_base_color = FloatVectorProperty(
        name="Map Line Color",
        description="Base color for map line connections in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.0, 0.2234, 0.0982),
        update=mp_line_color_update,
    )
    tp_connection_base_color = FloatVectorProperty(
        name="Trigger Line Color",
        description="Base color for trigger line connections in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.1706, 0.0, 0.0593),
        update=tp_line_color_update,
    )
    display_info = EnumProperty(
        name="Display Text Info",
        description="Display additional text information in 3D views",
        items=(
            ('none', "None", "No additional information displayed in 3D view"),
            ('locnames', "Locator Names", "Display locator names only in 3D view"),
            # ('locspeed', "Locator Nav. Points - Speed Limits", "Display navigation point locator speed limits in 3D view"),
            ('locnodes', "Locator Nav. Points - Boundary Nodes", "Display navigation point locator boundary node numbers in 3D view"),
            ('loclanes', "Locator Nav. Points - Boundary Lanes", "Display navigation point locator boundary lanes in 3D view"),
            ('locinfo', "Locator Comprehensive Info", "Display comprehensive information for locators in 3D view"),
        ),
        default='none',
        update=display_info_update,
    )
    info_text_color = FloatVectorProperty(
        name="Info Text Color",
        description="Base color for information text in 3D views",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(1.0, 1.0, 1.0),
        update=info_text_color_update,
    )

    show_preview_models = BoolProperty(
        name="Show Preview Models",
        description="Show preview models for locators",
        default=True,
        update=show_preview_models_update
    )

    base_paint_color = FloatVectorProperty(
        name="Base Paint Color",
        description="Color used on shaders using paint flavor.\n"
                    "This color is mixed in any shader using base paint color from game e.g. paint flavored and truckpaint shader",
        options={'HIDDEN'},
        subtype='COLOR',
        min=0, max=1,
        default=(0.5, 0.0, 0.0),
        update=base_paint_color_update,
    )

    # IMPORT & EXPORT SETTINGS SAVED IN CONFIG
    def import_scale_update(self, context):
        _config_container.update_item_in_file('Import.ImportScale', float(self.import_scale))
        return None

    def import_pim_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPimFile', int(self.import_pim_file))
        return None

    def use_welding_update(self, context):
        _config_container.update_item_in_file('Import.UseWelding', int(self.use_welding))
        return None

    def welding_precision_update(self, context):
        _config_container.update_item_in_file('Import.WeldingPrecision', int(self.welding_precision))
        return None

    def use_normals_update(self, context):
        _config_container.update_item_in_file('Import.UseNormals', int(self.use_normals))
        return None

    def import_pit_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPitFile', int(self.import_pit_file))
        return None

    def load_textures_update(self, context):
        _config_container.update_item_in_file('Import.LoadTextures', int(self.load_textures))
        return None

    def import_pic_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPicFile', int(self.import_pic_file))
        return None

    def import_pip_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPipFile', int(self.import_pip_file))
        return None

    def import_pis_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPisFile', int(self.import_pis_file))
        return None

    def connected_bones_update(self, context):
        _config_container.update_item_in_file('Import.ConnectedBones', int(self.connected_bones))
        return None

    def bone_import_scale_update(self, context):
        _config_container.update_item_in_file('Import.BoneImportScale', float(self.bone_import_scale))
        return None

    def import_pia_file_update(self, context):
        _config_container.update_item_in_file('Import.ImportPiaFile', int(self.import_pia_file))
        return None

    def search_subdirs_for_pia_update(self, context):
        _config_container.update_item_in_file('Import.IncludeSubdirsForPia', int(self.include_subdirs_for_pia))
        return None

    def export_scale_update(self, context):
        _config_container.update_item_in_file('Export.ExportScale', float(self.export_scale))
        return None

    def apply_modifiers_update(self, context):
        _config_container.update_item_in_file('Export.ApplyModifiers', int(self.apply_modifiers))
        return None

    def exclude_edgesplit_update(self, context):
        _config_container.update_item_in_file('Export.ExcludeEdgesplit', int(self.exclude_edgesplit))
        return None

    def include_edgesplit_update(self, context):
        _config_container.update_item_in_file('Export.IncludeEdgesplit', int(self.include_edgesplit))
        return None

    def active_uv_only_update(self, context):
        _config_container.update_item_in_file('Export.ActiveUVOnly', int(self.active_uv_only))
        return None

    def export_vertex_groups_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexGroups', int(self.export_vertex_groups))
        return None

    def export_vertex_color_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColor', int(self.export_vertex_color))
        return None

    def export_vertex_color_type_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColorType', self.export_vertex_color_type)
        return None

    def export_vertex_color_type_7_update(self, context):
        _config_container.update_item_in_file('Export.ExportVertexColorType7', self.export_vertex_color_type_7)
        return None

    '''
    # def export_anim_file_update(self, context):
    #     utils.update_item_in_config_file(utils.get_config_filepath(), 'Export.ExportAnimFile', self.export_anim_file)
    #     # if self.export_anim_file == 'anim':
    #         # _get_scs_globals().export_pis_file = True
    #         # _get_scs_globals().export_pia_file = True
    #     # else:
    #         # _get_scs_globals().export_pis_file = False
    #         # _get_scs_globals().export_pia_file = False
    #     return None
    '''

    def export_pim_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPimFile', int(self.export_pim_file))
        return None

    def output_type_update(self, context):
        _config_container.update_item_in_file('Export.OutputType', self.output_type)
        return None

    def export_pit_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPitFile', int(self.export_pit_file))
        return None

    def export_pic_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPicFile', int(self.export_pic_file))
        return None

    def export_pip_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPipFile', int(self.export_pip_file))
        return None

    def export_pis_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPisFile', int(self.export_pis_file))
        return None

    def export_pia_file_update(self, context):
        _config_container.update_item_in_file('Export.ExportPiaFile', int(self.export_pia_file))
        return None

    def sign_export_update(self, context):
        _config_container.update_item_in_file('Export.SignExport', int(self.sign_export))
        return None

    # IMPORT OPTIONS
    import_scale = FloatProperty(
        name="Scale",
        description="Import scale of model",
        min=0.001, max=1000.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        update=import_scale_update,
    )
    import_pim_file = BoolProperty(
        name="Import Model (PIM)",
        description="Import Model data from PIM file",
        default=True,
        update=import_pim_file_update,
    )
    use_welding = BoolProperty(
        name="Use Welding",
        description="Use automatic routine for welding of divided mesh surfaces",
        default=True,
        update=use_welding_update,
    )
    welding_precision = IntProperty(
        name="Welding Precision",
        description="Number of decimals which has to be equal for welding to take place.",
        min=1, max=6,
        default=4,
        update=welding_precision_update
    )
    use_normals = BoolProperty(
        name="Use Normals",
        description="When used meshes will get custom normals data from PIM file; "
                    "otherwise Blender calculated normals will be used.",
        default=True,
        update=use_normals_update
    )
    import_pit_file = BoolProperty(
        name="Import Trait (PIT)",
        description="Import Trait information from PIT file",
        default=True,
        update=import_pit_file_update,
    )
    load_textures = BoolProperty(
        name="Load Textures",
        description="Load textures",
        default=True,
        update=load_textures_update,
    )
    import_pic_file = BoolProperty(
        name="Import Collision (PIC)",
        description="Import Collision envelops from PIC file",
        default=True,
        update=import_pic_file_update,
    )
    import_pip_file = BoolProperty(
        name="Import Prefab (PIP)",
        description="Import Prefab from PIP file",
        default=True,
        update=import_pip_file_update,
    )
    import_pis_file = BoolProperty(
        name="Import Skeleton (PIS)",
        description="Import Skeleton from PIS file",
        default=True,
        update=import_pis_file_update,
    )
    connected_bones = BoolProperty(
        name="Create Connected Bones",
        description="Create connected Bones whenever possible",
        default=False,
        update=connected_bones_update,
    )
    bone_import_scale = FloatProperty(
        name="Bone Scale",
        description="Import scale for Bones",
        min=0.0001, max=10.0,
        soft_min=0.001, soft_max=1.0,
        default=0.1,
        update=bone_import_scale_update,
    )
    import_pia_file = BoolProperty(
        name="Import Animations (PIA)",
        description="Import Animations from all corresponding PIA files found in the same directory",
        default=True,
        update=import_pia_file_update,
    )
    include_subdirs_for_pia = BoolProperty(
        name="Search Subdirectories",
        description="Search also all subdirectories for animation files (PIA)",
        default=True,
        update=search_subdirs_for_pia_update,
    )

    # EXPORT OPTIONS
    export_scope = EnumProperty(
        name="Export Scope",
        items=(
            ('selection', "Selection", "Export selected objects only"),
            ('scene', "Active Scene", "Export only objects within active scene"),
            ('scenes', "All Scenes", "Export objects from all scenes"),
        ),
        default='scene',
    )
    export_scale = FloatProperty(
        name="Scale",
        description="Export scale of model",
        min=0.01, max=1000.0,
        soft_min=0.01, soft_max=1000.0,
        default=1.0,
        update=export_scale_update,
    )
    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Export meshes as modifiers were applied",
        default=True,
        update=apply_modifiers_update,
    )
    exclude_edgesplit = BoolProperty(
        name="Exclude 'Edge Split'",
        description="When you use Sharp Edge flags, then prevent 'Edge Split' modifier from "
                    "dismemberment of the exported mesh - the correct smoothing will be still "
                    "preserved with use of Sharp Edge Flags",
        default=True,
        update=exclude_edgesplit_update,
    )
    include_edgesplit = BoolProperty(
        name="Apply Only 'Edge Split'",
        description="When you use Sharp Edge flags and don't want to apply modifiers, "
                    "then use only 'Edge Split' modifier for dismemberment of the exported mesh "
                    "- the only way to preserve correct smoothing",
        default=True,
        update=include_edgesplit_update,
    )
    active_uv_only = BoolProperty(
        name="Only Active UVs",
        description="Export only active UV layer coordinates",
        default=False,
        update=active_uv_only_update,
    )
    export_vertex_groups = BoolProperty(
        name="Vertex Groups",
        description="Export all existing 'Vertex Groups'",
        default=True,
        update=export_vertex_groups_update,
    )
    export_vertex_color = BoolProperty(
        name="Vertex Color",
        description="Export active vertex color layer",
        default=True,
        update=export_vertex_color_update,
    )
    export_vertex_color_type = EnumProperty(
        name="Vertex Color Type",
        description="Vertex color type",
        items=(
            ('rgbda', "RGBA (Dummy Alpha)", "RGB color information with dummy alpha set to 1 (usually necessary)"),
            ('rgba', "RGBA (Alpha From Another Layer)", "RGB color information + alpha from other layer"),
        ),
        default='rgbda',
        update=export_vertex_color_type_update,
    )
    export_vertex_color_type_7 = EnumProperty(
        name="Vertex Color Type",
        description="Vertex color type",
        items=(
            ('rgb', "RGB", "Only RGB color information is exported"),
            ('rgbda', "RGBA (Dummy Alpha)", "RGB color information with dummy alpha set to 1 (usually necessary)"),
            ('rgba', "RGBA (Alpha From Another Layer)", "RGB color information + alpha from other layer"),
        ),
        default='rgbda',
        update=export_vertex_color_type_7_update,
    )
    export_pim_file = BoolProperty(
        name="Export Model",
        description="Export model automatically with file save",
        default=True,
        update=export_pim_file_update,
    )
    output_type = EnumProperty(
        name="Output Format",
        items=(
            ('5', "Game Data Format, ver. 5", "Export PIM (version 5) file formats for SCS Game Engine"),
            ('def1', "Data Exchange Format, ver. 1",
             "Export 'PIM Data Exchange Formats' (version 1) file formats designed for data exchange between different modeling tools"),
            # ('7', "PIM Data Exchange Formats, ver. 1", "Export 'PIM Data Exchange Formats' (version 1) file formats designed for data
            # exchange between different modeling tools"),
        ),
        default='5',
        update=output_type_update,
    )
    export_pit_file = BoolProperty(
        name="Export PIT",
        description="PIT...",
        default=True,
        update=export_pit_file_update,
    )
    export_pic_file = BoolProperty(
        name="Export Collision",
        description="Export collision automatically with file save",
        default=True,
        update=export_pic_file_update,
    )
    export_pip_file = BoolProperty(
        name="Export Prefab",
        description="Export prefab automatically with file save",
        default=True,
        update=export_pip_file_update,
    )
    export_pis_file = BoolProperty(
        name="Export Skeleton",
        description="Export skeleton automatically with file save",
        default=True,
        update=export_pis_file_update,
    )
    export_pia_file = BoolProperty(
        name="Export Animations",
        description="Export animations automatically with file save",
        default=True,
        update=export_pia_file_update,
    )
    sign_export = BoolProperty(
        name="Write A Signature To Exported Files",
        description="Add a signature to the header of the output files with some additional information",
        default=False,
        update=sign_export_update,
    )

    # COMMON SETTINGS - SAVED IN CONFIG
    def dump_level_update(self, context):
        _config_container.update_item_in_file('Header.DumpLevel', self.dump_level)
        return None

    def config_storage_place_update(self, context):

        _config_container.update_item_in_file('Header.ConfigStoragePlace', self.config_storage_place)

        if self.config_storage_place == "ConfigFile":
            _config_container.apply_settings()

        return None

    dump_level = EnumProperty(
        name="Printouts",
        items=(
            ('0', "0 - Errors Only", "Print only Errors to the console"),
            ('1', "1 - Errors and Warnings", "Print Errors and Warnings to the console"),
            ('2', "2 - Errors, Warnings, Info", "Print Errors, Warnings and Info to the console"),
            ('3', "3 - Errors, Warnings, Info, Debugs", "Print Errors, Warnings, Info and Debugs to the console"),
            ('4', "4 - Errors, Warnings, Info, Debugs, Specials", "Print Errors, Warnings, Info, Debugs and Specials to the console"),
            ('5', "5 - Test mode (DEVELOPER ONLY)", "Extra developer mode. (Don't use it if you don't know what you are doing!)"),
        ),
        default='2',
        update=dump_level_update,
    )
    config_storage_place = EnumProperty(
        name="Use Global Settings",
        description="Defines place for storage of Global Settings. By default Common Config File is used for globals to be stored per machine.",
        items=(
            ('ConfigFile', 'From Common Config File', "Global settings stored per machine"),
            ('BlendFile', 'From Blend File', "Global settings stored per each blend file"),
        ),
        default='ConfigFile',
        update=config_storage_place_update,
    )

    # COMMON SETTINGS - NOT SAVED IN CONFIG
    preview_export_selection = BoolProperty(
        name="Preview selection",
        description="Preview selection which will be exported",
        default=True,
    )
    preview_export_selection_active = BoolProperty(
        name="Flag indication if selection preview is active",
        description="",
        default=False,
    )
    last_load_bt_version = StringProperty(
        name="Last Load BT Version",
        description="Version string of SCS Blender Tools on last file load (used for applying fixes on older versions)",
        default="0.0",
    )

    # CONVERSION HELPER SETTINGS
    def conv_hlpr_converters_path_update(self, context):

        # if relative path detected convert it to absolute
        if self.conv_hlpr_converters_path.startswith("//") or self.conv_hlpr_converters_path.startswith("\\"):

            self.conv_hlpr_converters_path = _path_utils.repair_path(self.conv_hlpr_converters_path)
            return None  # interrupt update, as another one will be called for saving item into config.txt (as we changed converters path)

        _config_container.update_item_in_file('Paths.ConvertersPath', self.conv_hlpr_converters_path)

    conv_hlpr_converters_path = StringProperty(
        name="Converters Path",
        description="Path to SCS conversion tools directory (needed only if you use Conversion Helper).",
        subtype="DIR_PATH",
        update=conv_hlpr_converters_path_update,
        default="<Select Converters Path>"
    )

    class ConvHlprCustomPathEntry(bpy.types.PropertyGroup):

        def path_update(self, context):

            # if relative path detected convert it to absolute
            if self.path.startswith("//") or self.path.startswith("\\"):
                from io_scs_tools.utils.path import repair_path
                self.path = repair_path(self.path)

        path = StringProperty(subtype='DIR_PATH')

    conversion_helper_expand = BoolProperty(
        name="Expand Conversion Helper",
        description="Expand Conversion Helper",
        default=True,
    )
    conv_hlpr_custom_paths = CollectionProperty(
        type=ConvHlprCustomPathEntry,
        description="Custom paths used for converting more targets to one"
    )
    conv_hlpr_custom_paths_active = IntProperty(
        description="Currently selected custom path"
    )
    conv_hlpr_mod_destination = StringProperty(
        name="Mod Destination",
        description="Destination folder where mod will be packed to.",
        subtype="DIR_PATH",
        default="<Mod Folder Path>"
    )
    conv_hlpr_mod_name = StringProperty(
        name="Mod Name",
        description="Name of the packed mod zip file",
        default="<Mod Name>"
    )
    conv_hlpr_clean_on_packing = BoolProperty(
        name="Auto Clean",
        description="Clean converted data directory before exporting & converting & packing (usually used when firstly packing a mod).",
        default=False
    )
    conv_hlpr_export_on_packing = BoolProperty(
        name="Auto Export",
        description="Export before converting & packing (it will use last successful batch export action).",
        default=True
    )
    conv_hlpr_convert_on_packing = BoolProperty(
        name="Auto Convert",
        description="Execute convert before packing.",
        default=True
    )
    conv_hlpr_mod_compression = EnumProperty(
        description="Compression method for mod packing",
        items=(
            (_CONV_HLPR_consts.NoZip, "No Archive", "Create mod folder package instead of ZIP"),
            (_CONV_HLPR_consts.StoredZip, "No Compression", "No compression done to package"),
            (_CONV_HLPR_consts.DeflatedZip, "Deflated", "Use ZIP deflated compression method"),
            (_CONV_HLPR_consts.Bzip2Zip, "BZIP2", "Uses bzip2 compression method"),
        ),
        default=_CONV_HLPR_consts.DeflatedZip
    )
