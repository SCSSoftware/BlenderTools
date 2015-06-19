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
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       FloatProperty,
                       FloatVectorProperty)
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.internals import preview_models as _preview_models

'''
# CgFX TEMPLATES (on Scenes)
# class SceneCgFXTemplateInventory(bpy.types.PropertyGroup):
# """
# CgFX Shader Templates inventory on Scene.
#     """
#     name = StringProperty(name="CgFX Template Name", default="")
#     active = BoolProperty(name="CgFX Template Activation Status", default=False)
#
#
# CgFX SHADERS (on Scenes)
# class SceneCgFXShaderInventory(bpy.types.PropertyGroup):
#     """
#     CgFX Shader file inventory on Scene.
#     """
#     name = StringProperty(name="CgFX Shader Name", default="")
#     filepath = StringProperty(name="CgFX Shader Absolute File Path", default="")
#     active = BoolProperty(name="CgFX Shader Activation Status", default=False)
'''


class SceneSCSProps(bpy.types.PropertyGroup):
    """
    SCS Tools Scene Variables - ...Scene.scs_props...
    :return:
    """

    part_list_sorted = BoolProperty(
        name="Part List Sorted Alphabetically",
        description="Sort Part list alphabetically",
        default=False,
    )

    variant_list_sorted = BoolProperty(
        name="Variant List Sorted Alphabetically",
        description="Sort Variant list alphabetically",
        default=False,
    )
    variant_views = EnumProperty(
        name="Variant View Setting",
        description="Variant view style options",
        items=(
            ('compact', "Compact", "Compact view (settings just for one Variant at a time)", 'FULLSCREEN', 0),
            ('vertical', "Vertical", "Vertical long view (useful for larger number of Variants)", 'LONGDISPLAY', 1),
            ('horizontal', "Horizontal", "Horizontal table view (best for smaller number of Variants)", 'SHORTDISPLAY', 2),
            ('integrated', "Integrated", "Integrated in Variant list (best for smaller number of Parts)", 'LINENUMBERS_OFF', 3),
        ),
        default='horizontal',
    )

    '''
    CGFX SHADERS
    def update_cgfx(self, context):
        """Returns the actual CgFX name list from "scs_cgfx_inventory".
        It also updates "cgfx_container", so the UI could contain all
        the items with no error. (necessary hack :-/)"""
        # print('  > update_cgfx...')
        global cgfx_container

        def append_cgfx(items, act_cgfx, cgfx_i):
            """Appends CgFX shader item and choose the icon for it."""
            if ".dif" in act_cgfx:
                items.append((act_cgfx, act_cgfx, "", 'SOLID', cgfx_i), )
            else:
                items.append((act_cgfx, act_cgfx, "", 'SMOOTH', cgfx_i), )
            return items

        items = []
        if context.scene.scs_props.cgfx_list_sorted:
            inventory = {}
            for cgfx_i, cgfx in enumerate(context.scene.scs_cgfx_inventory):
                inventory[cgfx.name] = cgfx_i
            for cgfx in sorted(inventory):
                cgfx_i = inventory[cgfx]
                act_cgfx = cgfx_container.add(cgfx)
                items = append_cgfx(items, act_cgfx, cgfx_i)
        else:
            for cgfx_i, cgfx in enumerate(context.scene.scs_cgfx_inventory):
                act_cgfx = cgfx_container.add(cgfx.name)
                items = append_cgfx(items, act_cgfx, cgfx_i)
        return tuple(items)

    def get_cgfx_items(self):
        """Returns menu index of a CgFX shader name of actual Material to set
        the right name in UI menu."""
        # print('  > get_cgfx_items...')
        result = 0
        for cgfx_i, cgfx in enumerate(bpy.context.scene.scs_cgfx_inventory):
            if cgfx.active:
                result = cgfx_i
                break
        return result

    def set_cgfx_items(self, value):
        """Receives an actual index of currently selected CgFX shader name in the menu,
        sets that CgFX shader name as active in CgFX shader Inventory and sets
        the same shader name in active Material."""
        # print('  > set_cgfx_items...')
        for cgfx_i, cgfx in enumerate(bpy.context.scene.scs_cgfx_inventory):
            if value == cgfx_i:
                cgfx.active = True
                ## Set CgFX in the material
                material = bpy.context.active_object.active_material
                cgfx_templates_list = bpy.context.scene.scs_props.cgfx_templates_list
                if cgfx_templates_list == "custom": cgfx_templates_list = "<custom>"
                material.scs_props.cgfx_template = cgfx_templates_list
                print('material: "%s"\t- CgFX: "%s" (%i)' % (material.name, cgfx.name, cgfx_i))
                material.scs_props.cgfx_filename = cgfx.name
                ## Get a valid path to CgFX Shader file
                cgfx_filepath = cgfx_utils.get_cgfx_filepath(cgfx.name)
                if cgfx_filepath:
                    ## Compile CgFX Shader file
                    output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                    cgfx_utils.register_cgfx_ui(material, utils.get_actual_look())
            else:
                cgfx.active = False

    cgfx_file_list = EnumProperty(
            name="Active CgFX Shader",
            description="Active CgFX shader",
            items=update_cgfx,
            get=get_cgfx_items,
            set=set_cgfx_items,
            )
    cgfx_list_sorted = BoolProperty(
            name="CgFX Shader List Sorted Alphabetically",
            description="Sort CgFX shader list alphabetically",
            default=True,
            )

    CGFX TEMPLATES
    def update_cgfx_template(self, context):
        """Returns the actual CgFX name list from "scs_cgfx_template_inventory".
        It also updates "cgfx_template_container", so the UI could contain all
        the items with no error. (necessary hack :-/)"""
        #print('  > update_cgfx_template...')
        global cgfx_template_container

        def append_cgfx_template(items, act_template, template_i):
            """Appends given Template item and choose the icon for it."""
            if act_template != "<custom>":  # The item already exists...
                if "dif" in act_template:
                    items.append((act_template, act_template, "", 'SOLID', template_i), )
                else:
                    items.append((act_template, act_template, "", 'TEXTURE_SHADED', template_i), )
            return items

        # items = []
        items = [("custom", "<custom>", "Use CgFX shader definition files for manual material setup", 'SOLID', 0)]
        if context.scene.scs_props.cgfx_templates_list_sorted:
            inventory = {}
            for template_i, template in enumerate(context.scene.scs_cgfx_template_inventory):
                inventory[template.name] = template_i
            for template in sorted(inventory):
                template_i = inventory[template]
                act_template = cgfx_template_container.add(template)
                # print(' + %i act_template: %s (%s)' % (template_i, str(act_template), str(template)))
                items = append_cgfx_template(items, act_template, template_i)
        else:
            for template_i, template in enumerate(context.scene.scs_cgfx_template_inventory):
                act_template = cgfx_template_container.add(template.name)
                # print(' + %i act_template: %s (%s)' % (template_i, str(act_template), str(template)))
                items = append_cgfx_template(items, act_template, template_i)
        return tuple(items)

    def get_cgfx_templates_items(self):
        """Returns menu index of a CgFX shader name of actual material to set
        the right name in UI menu."""
        #print('  > get_cgfx_templates_items...')
        result = 0
        for template_i, template in enumerate(bpy.context.scene.scs_cgfx_template_inventory):
            if template.active:
                result = template_i
        return result

    def set_cgfx_templates_items(self, value):
        """Receives an actual index of currently selected CgFX shader name in the menu,
        sets that CgFX shader name as active in CgFX shader Inventory and sets
        the same shader name in active material."""
        print('  > set_cgfx_templates_items...')

        def apply_template_setting(material, actual_look, prop_name, prop_type, prop_value, prop_enabled):
            """."""
            # print('  > apply_template_setting()')
            all_values = {}
            if prop_name in material.scs_cgfx_looks[actual_look].cgfx_data:
                if material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].type == prop_type:
                    # print('prop_name: "%s"' % str(prop_name))
                    # print('prop_value: %s' % str(prop_value))
                    if prop_type == "bool":
                        prop_value = prop_value.lower()
                    elif prop_type == "enum":
                        pass
                    elif prop_type == "float":
                        prop_value = str(prop_value)
                        all_values["cgfx_" + prop_name] = prop_value
                    elif prop_type in ("float2", "float3"):
                        prop_value = "(" + str(prop_value)[1:-1] + ")"
                        all_values["cgfx_" + prop_name] = prop_value
                    elif prop_type == "color":
                        rgb, mult = utils.make_color_mtplr(prop_value)
                        prop_value = "(" + str(rgb)[1:-1] + ", " + str(mult) + ")"
                        all_values["cgfx_" + prop_name] = prop_value
                    else:
                        all_values["cgfx_" + prop_name] = str('"' + prop_value + '"')
                    material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].value = prop_value
                    if prop_enabled == "True":
                        material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].enabled = True
                    elif prop_enabled == "False":
                        material.scs_cgfx_looks[actual_look].cgfx_data[prop_name].enabled = False
                    else:
                        print('WARNING - unknown property "enabled" state found: "%s"' % prop_enabled)

            cgfx_utils.update_ui_props_from_matlook_record(all_values)

        def read_template_settings(material, actual_look, section):
            """."""
            print('  > read_template_settings()')
            #actual_look = utils.get_actual_look()
            for item in section.sections:
                # print('  item:\n%s' % repr(item))
                # print('      type: %s - props: "%s"' % (item.type, str(item.props)))
                if item.type == "Item":
                    prop_name = prop_type = prop_value = prop_enabled = None
                    for prop in item.props:
                        # print('      prop: "%s"' % str(prop))
                        if prop[0] == "#":
                            continue
                        elif prop[0] == "Name":
                            prop_name = prop[1]
                        elif prop[0] == "Type":
                            prop_type = prop[1]
                        elif prop[0] == "Value":
                            prop_value = prop[1]
                        elif prop[0] == "Enabled":
                            prop_enabled = prop[1]
                        else:
                            print('WARNING - unknown property found: "%s"' % str(prop))
                    # if prop_name and prop_type and prop_value and prop_enabled:
                    # print('      prop_name: %s - prop_type: %s - prop_value: %s - prop_enabled: %s' % (prop_name, prop_type, prop_value,
    prop_enabled))
                    apply_template_setting(material, actual_look, prop_name, prop_type, prop_value, prop_enabled)

        scene = bpy.context.scene
        for template_i, template in enumerate(scene.scs_cgfx_template_inventory):
            if value == template_i:
                template.active = True
                material = bpy.context.active_object.active_material
                actual_look = utils.get_actual_look()
                material.scs_props.cgfx_template = template.name
                if value == 0:  # Custom CgFX shader...
                    print('    custom CgFX shader...')
                    print('      cgfx_file_list: "%s"' % scene.scs_props.cgfx_file_list)
                    print('      cgfx_filename:  "%s"' % material.scs_props.cgfx_filename)
                    material.scs_props.cgfx_filename = scene.scs_props.cgfx_file_list
                    # Compile CgFX Shader file
                    output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                    cgfx_utils.register_cgfx_ui(material, actual_look)
                    for item in material.scs_cgfx_looks[actual_look].cgfx_data: item.enabled = True
                else:
                    # Set CgFX in the Material
                    # print('    material: "%s"\t- CgFX: "%s" (%i)' % (material.name, template.name, template_i))
                    template_section = utils.get_cgfx_template(_get_scs_globals().cgfx_templates_filepath, template.name)
                    # template_settings = {}
                    if template_section:
                        cgfx_name = utils.get_prop_value_from_section(template_section, "CgFXFile")
                        if cgfx_name:
                            if cgfx_name.endswith(".cgfx"): cgfx_name = cgfx_name[:-5]
                            material.scs_props.cgfx_filename = cgfx_name
                            # Get a valid path to CgFX Shader file
                            cgfx_filepath = cgfx_utils.get_cgfx_filepath(cgfx_name)
                            # print('    cgfx_filepath: "%s"' % cgfx_filepath)
                            if cgfx_filepath:
                                # Compile CgFX Shader file
                                output, vertex_data = cgfx_utils.recompile_cgfx_shader(material, "", True)
                                cgfx_utils.register_cgfx_ui(material, actual_look)
                            read_template_settings(material, actual_look, template_section)
                        else:
                            print('NO "cgfx_name"!')
                    else:
                        print('NO "template_section"!')
            else:
                template.active = False

    cgfx_templates_list = EnumProperty(
            name="CgFX Shader Templates",
            description="CgFX shader templates",
            items=update_cgfx_template,
            get=get_cgfx_templates_items,
            set=set_cgfx_templates_items,
            )
    cgfx_templates_list_sorted = BoolProperty(
            name="CgFX Shader Template List Sorted Alphabetically",
            description="Sort CgFX shader template list alphabetically",
            default=True,
            )
    '''

    # VISIBILITY VARIABLES
    scs_look_panel_expand = BoolProperty(
        name="Expand SCS Look Panel",
        description="Expand SCS Look panel",
        default=True,
    )
    scs_part_panel_expand = BoolProperty(
        name="Expand SCS Part Panel",
        description="Expand SCS Part panel",
        default=True,
    )
    scs_variant_panel_expand = BoolProperty(
        name="Expand SCS Variant Panel",
        description="Expand SCS Variant panel",
        default=True,
    )
    empty_object_settings_expand = BoolProperty(
        name="Expand SCS Object Settings",
        description="Expand SCS Object settings panel",
        default=True,
    )
    locator_settings_expand = BoolProperty(
        name="Expand Locator Settings",
        description="Expand locator settings panel",
        default=True,
    )
    locator_display_settings_expand = BoolProperty(
        name="Expand Locator Display Settings",
        description="Expand locator display settings panel",
        default=False,
    )
    shader_attributes_expand = BoolProperty(
        name="Expand SCS Material Attributes",
        description="Expand SCS material attributes panel",
        default=True,
    )
    shader_textures_expand = BoolProperty(
        name="Expand SCS Material Textures",
        description="Expand SCS material textures panel",
        default=True,
    )
    '''
    cgfx_shader_expand = BoolProperty(
    name="Expand CgFX Shader Settings",
    description="Expand CgFX shader settings panel",
    default=True,
    )
    cgfx_parameter_expand = BoolProperty(
        name="Expand CgFX Parameters",
        description="Expand CgFX parameters panel",
        default=True,
    )
    cgfx_data_expand = BoolProperty(
        name="Expand CgFX Parameters",
        description="Expand CgFX parameters panel",
        default=True,
    )
    cgfx_vertex_data_expand = BoolProperty(
        name="Expand CgFX Vertex Data",
        description="Expand CgFX vertex data panel",
        default=True,
    )
    cgfx_lib_expand = BoolProperty(
        name="Expand Shader Library",
        description="Expand CgFX shader library panel",
        default=False,
    )
    cgfx_templates_expand = BoolProperty(
        name="Expand Shader Templates",
        description="Expand CgFX shader template panel",
        default=False,
    )
    '''
    shader_presets_expand = BoolProperty(
        name="Expand Shader Presets",
        description="Expand shader presets panel",
        default=False,
    )
    global_display_settings_expand = BoolProperty(
        name="Expand Global Display Settings",
        description="Expand global display settings panel",
        default=True,
    )
    global_paths_settings_expand = BoolProperty(
        name="Expand Global Paths Settings",
        description="Expand global paths settings panel",
        default=True,
    )
    scs_root_panel_settings_expand = BoolProperty(
        name="Expand 'SCS Root Object' Settings",
        description="Expand 'SCS Root Object' settings panel",
        default=True,
    )
    global_settings_expand = BoolProperty(
        name="Expand Global Settings",
        description="Expand global settings panel",
        default=True,
    )
    scene_settings_expand = BoolProperty(
        name="Expand Scene Settings",
        description="Expand scene settings panel",
        default=True,
    )
    scs_animation_settings_expand = BoolProperty(
        name="Expand Animation Settings",
        description="Expand animation settings panel",
        default=True,
    )
    scs_animplayer_panel_expand = BoolProperty(
        name="Expand Animation Player Settings",
        description="Expand animation player panel",
        default=True,
    )
    scs_skeleton_panel_expand = BoolProperty(
        name="Expand Skeleton Settings",
        description="Expand skeleton settings panel",
        default=True,
    )
    default_export_filepath = StringProperty(
        name="Default Export Path",
        description="Relative export path (relative to SCS Project Base Path) for all SCS Game Objects without custom export path "
                    "(this path does not apply when exporting via menu)",
        default="",
        # subtype="FILE_PATH",
        subtype='NONE',
    )
    export_panel_expand = BoolProperty(
        name="Expand Export Panel",
        description="Expand Export panel",
        default=True,
    )
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

    # VISIBILITY TOOLS SCOPE
    visibility_tools_scope = EnumProperty(
        name="Visibility Tools Scope",
        description="Selects the scope upon visibility tools are working",
        items=(
            ('Global', "Global", "Use scope of the whole scene"),
            ('SCS Root', "SCS Root", "Use the scope of current SCS Root"),
        ),
    )

    # DRAWING MODE SETTINGS
    def drawing_mode_update(self, context):
        from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback

        _open_gl_callback.enable(self.drawing_mode)

    drawing_mode = EnumProperty(
        name="Custom Drawing Mode",
        description="Drawing mode for custom elements (Locators and Connections)",
        items=(
            ('Normal', "Normal", "Use normal depth testing drawing"),
            ('X-ray', "X-ray", "Use X-ray drawing"),
        ),
        update=drawing_mode_update
    )

    # PREVIEW SETTINGS
    def show_preview_models_update(self, context):
        """
        :param context:
        :return:
        """
        scene = context.scene

        for obj in bpy.data.objects:
            if obj.type == 'EMPTY':
                if scene.scs_props.show_preview_models:
                    if not _preview_models.load(obj):
                        _preview_models.unload(obj)
                else:
                    _preview_models.unload(obj)
        return None

    show_preview_models = BoolProperty(
        name="Show Preview Models",
        description="Show preview models for locators",
        default=True,
        update=show_preview_models_update
    )

    # SETTINGS WHICH GET SAVED IN CONFIG FILE
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

    # SCS TOOLS GLOBAL SETTINGS - DISPLAY SETTINGS
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
    # DATA GROUP NAMING
    group_name = StringProperty(name="Data Group Name", default="SCS_connection_numbers")
    nav_curve_data_name = StringProperty(name="Navigation Curve Data Name", default="nav_curves_used_numbers")
    map_line_data_name = StringProperty(name="Map Line Data Name", default="map_lines_used_numbers")
    tp_line_data_name = StringProperty(name="Trigger Line Data Name", default="tp_lines_used_numbers")

    view_hide_tools = BoolProperty(
        name="",
        description="Switch View / Hide Tools",
        default=True,
    )
