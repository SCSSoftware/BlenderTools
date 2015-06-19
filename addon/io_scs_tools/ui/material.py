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
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.ui import shared as _shared


class _MaterialPanelBlDefs(_shared.HeaderIconPanel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"


def _draw_shader_presets(layout, scs_props, scs_globals, read_only=False):
    """Creates Shader Presets sub-panel."""
    layout_box = layout.box()
    layout_box.enabled = not read_only
    if scs_props.shader_presets_expand:
        panel_header = layout_box.split(percentage=0.5)
        panel_header_1 = panel_header.row()
        panel_header_1.prop(scs_props, 'shader_presets_expand', text="Shader Presets:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        panel_header_2 = panel_header.row(align=True)
        panel_header_2.alignment = 'RIGHT'
        panel_header_2a = panel_header_2.row()
        panel_header_2a.prop(scs_globals, 'shader_preset_list_sorted', text='', icon='SORTALPHA', expand=True, toggle=True)

        layout_box_row = layout_box.row(align=True)
        if _path_utils.is_valid_shader_presets_library_path():
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
        layout_box_row.prop(scs_globals, 'shader_presets_filepath', text='', icon='FILE_TEXT')
        layout_box_row.operator('scene.select_shader_presets_filepath', text='', icon='FILESEL')

        layout_box_row = layout_box.column()
        layout_box_row.prop(scs_globals, 'shader_preset_list', expand=True, toggle=True)
    else:
        layout_box_row = layout_box.row().split(percentage=0.4)
        layout_box_row.prop(scs_props, 'shader_presets_expand', text="Shader Presets:", icon='TRIA_RIGHT', icon_only=True, emboss=False)

        column = layout_box_row.column(align=True)

        row = column.row(align=True)
        row.prop(scs_globals, 'shader_preset_list', text='')
        row.prop(scs_globals, "shader_preset_use_search", icon="VIEWZOOM", icon_only=True, toggle=True)

        if scs_globals.shader_preset_use_search:
            column.prop_search(scs_globals, "shader_preset_search_value", bpy.data.worlds[0], "scs_shader_presets_inventory", text="", icon="BLANK1")


def _draw_shader_attribute(layout, mat, split_perc, attribute):
    """Draws one material attribute.

    :param layout: layout to draw attribute to
    :type layout: bpy.types.UILayout
    :param mat: material from which data should be displayed
    :type mat: bpy.types.Material
    :param split_perc: split percentage for attribute name/value
    :type split_perc: float
    :param attribute: attribute data
    :type attribute: dict
    """

    linked_vals = False  # DEBUG: Side by side display of values

    tag = attribute.get('Tag', "")
    hide_state = attribute.get('Hide', None)
    lock_state = attribute.get('Lock', None)
    attribute_label = str(tag.replace('_', ' ').title() + ":")

    if hide_state == 'True':
        return

    attr_row = layout.row()
    item_space = attr_row.split(percentage=split_perc, align=True)

    label_icon = 'ERROR'
    if lock_state == 'True':
        item_space.enabled = False
        attribute_label = str(attribute_label[:-1] + " (locked):")
        label_icon = 'LOCKED'

    item_space.label(attribute_label)

    '''
    shader_attribute_id = str("shader_attribute_" + tag)
    if shader_attribute_id in mat.scs_props:
        item_space.prop(mat.scs_props, shader_attribute_id, text='')
    else:
        print(' %r is NOT defined in SCS Blender Tools...!' % shader_attribute_id)
    '''

    item_space = item_space.split(percentage=(1 - split_perc) * 0.2, align=True)
    props = item_space.operator("material.scs_looks_wt", text="WT")
    props.property_str = "shader_attribute_" + tag

    if tag == 'diffuse':
        item_space.prop(mat.scs_props, 'shader_attribute_diffuse', text='')
        if linked_vals:
            item_space.prop(mat, 'diffuse_color', text='')
    elif tag == 'specular':
        item_space.prop(mat.scs_props, 'shader_attribute_specular', text='')
        if linked_vals:
            item_space.prop(mat, 'specular_color', text='')
    elif tag == 'shininess':
        item_space.prop(mat.scs_props, 'shader_attribute_shininess', text='')
        # if linked_vals: item_space.prop(mat, 'specular_intensity', text='')
        if linked_vals:
            item_space.prop(mat, 'specular_hardness', text='')
    elif tag == 'add_ambient':
        item_space.prop(mat.scs_props, 'shader_attribute_add_ambient', text='')
        if linked_vals:
            item_space.prop(mat, 'ambient', text='')
    elif tag == 'reflection':
        item_space.prop(mat.scs_props, 'shader_attribute_reflection', text='')
        if linked_vals:
            item_space.prop(mat.raytrace_mirror, 'reflect_factor', text='')
    elif tag == 'reflection2':
        item_space.prop(mat.scs_props, 'shader_attribute_reflection2', text='')
    elif tag == 'shadow_bias':
        item_space.prop(mat.scs_props, 'shader_attribute_shadow_bias', text='')
        if linked_vals:
            item_space.prop(mat, 'shadow_buffer_bias', text='')
    elif tag == 'env_factor':
        item_space.prop(mat.scs_props, 'shader_attribute_env_factor', text='')
    elif tag == 'fresnel':
        item_space.column().prop(mat.scs_props, 'shader_attribute_fresnel', text='')
    elif tag == 'tint':
        item_space.prop(mat.scs_props, 'shader_attribute_tint', text='')
    elif tag == 'tint_opacity':
        item_space.prop(mat.scs_props, 'shader_attribute_tint_opacity', text='')
    elif tag.startswith("aux") and hasattr(mat.scs_props, "shader_attribute_" + tag):

        col = item_space.column().column(align=True)

        auxiliary_prop = getattr(mat.scs_props, "shader_attribute_" + tag, None)

        for item in auxiliary_prop:
            col.prop(item, 'value', text='')

    else:
        item_space.label('Undefined Shader Attribute Type!', icon=label_icon)


def _draw_shader_texture(layout, mat, split_perc, texture, read_only):
    """Draws texture box with it's properties.

    :param layout: layout to draw attribute to
    :type layout: bpy.types.UILayout
    :param mat: material from which data should be displayed
    :type mat: bpy.types.Material
    :param split_perc: split percentage for attribute name/value
    :type split_perc: float
    :param texture: texture data
    :type texture: dict
    :param read_only: if texture should be read only
    :type read_only: bool
    """

    tag = texture.get('Tag', None)
    hide_state = texture.get('Hide', None)
    tag_id = tag.split(':')
    tag_id_string = tag_id[1]
    texture_type = tag_id_string[8:]
    shader_texture_id = str('shader_' + tag_id_string)

    if hide_state == 'True':
        return

    texture_box = layout.box()

    header_split = texture_box.row().split(percentage=0.5)
    header_split.label(texture_type.title(), icon="TEXTURE_SHADED")

    if hasattr(mat.scs_props, shader_texture_id):

        shader_texture = mat.scs_props.get(shader_texture_id, "")
        # imported tobj boolean switch (only for imported shaders)
        use_imported_tobj = getattr(mat.scs_props, shader_texture_id + "_use_imported", False)
        if read_only:
            row = header_split.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(mat.scs_props, shader_texture_id + "_use_imported")

            if use_imported_tobj:

                texture_row = texture_box.row()
                item_space = texture_row.split(percentage=split_perc, align=True)
                item_space.label("TOBJ Path:")

                item_space = item_space.split(percentage=(1 - split_perc) * 0.2, align=True)
                props = item_space.operator("material.scs_looks_wt", text="WT")
                props.property_str = shader_texture_id
                item_space.prop(mat.scs_props, shader_texture_id + "_imported_tobj", text="")

        # disable whole texture layout if it's locked
        texture_box.enabled = not mat.scs_props.get(shader_texture_id + "_locked", False)

        texture_row = texture_box.row()
        item_space = texture_row.split(percentage=split_perc, align=True)

        # in case of custom tobj value texture is used only for preview
        if read_only and use_imported_tobj:
            item_space.label("Preview Tex:")
        else:
            item_space.label("Texture:")

        layout_box_col = item_space.column(align=True)
        layout_box_row = layout_box_col.row(align=True)

        if shader_texture:
            texture_icon = 'TEXTURE'
        else:
            texture_icon = 'MATPLANE'

        # MARK INVALID SLOTS
        if _material_utils.is_valid_shader_texture_path(shader_texture):
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
            texture_icon = 'ERROR'

        # MARK EMPTY SLOTS
        if shader_texture == "":
            layout_box_row.alert = True

        layout_box_row = layout_box_row.split(percentage=(1 - split_perc) * 0.2, align=True)
        props = layout_box_row.operator("material.scs_looks_wt", text="WT")
        props.property_str = shader_texture_id

        layout_box_row = layout_box_row.row(align=True)
        layout_box_row.prop(mat.scs_props, shader_texture_id, text='', icon=texture_icon)
        props = layout_box_row.operator('scene.select_shader_texture_filepath', text='', icon='FILESEL')
        props.shader_texture = shader_texture_id  # DYNAMIC ID SAVE (FOR FILE REQUESTER)

        # ADDITIONAL TEXTURE SETTINGS
        if (not read_only or (read_only and not use_imported_tobj)) and texture_box.enabled:

            tobj_exists = _material_utils.is_valid_shader_texture_path(shader_texture, True)

            if not tobj_exists:
                item_split = layout_box_col.split(percentage=(1 - split_perc) * 0.2, align=True)

                item_space = item_split.row(align=True)
                props = item_space.operator("material.scs_create_tobj", icon="NEW", text="")
                props.texture_type = texture_type

                item_space = item_split.row(align=True)
            else:
                item_space = layout_box_col.row(align=True)

            item_space.enabled = tobj_exists

            if tobj_exists:
                mtime = str(os.path.getmtime(_path_utils.get_abs_path(shader_texture[:-4] + ".tobj")))
                item_space.alert = (mtime != getattr(mat.scs_props, shader_texture_id + "_tobj_load_time", "NOT FOUND"))
            else:
                item_space.alert = True

            props = item_space.operator("material.scs_reload_tobj", icon="LOAD_FACTORY", text="")
            props.texture_type = texture_type

            item_space.prop_menu_enum(
                mat.scs_props,
                str('shader_' + tag_id_string + '_settings'),
                icon='SETTINGS',
            )

        # UV LAYERS FOR TEXTURE
        uv_mappings = getattr(mat.scs_props, "shader_" + tag_id_string + "_uv", None)

        if len(uv_mappings) > 0:

            texture_row = texture_box.row()
            item_space = texture_row.split(percentage=split_perc, align=True)
            if read_only:
                item_space.label("Preview UV Map:")
            else:
                item_space.label("Mapping:")
            layout_box_col = item_space.column(align=True)

            for mapping in uv_mappings:

                item_space_row = layout_box_col.row(align=True)

                # add info about normal map uv mapping property in case of imported shader
                if read_only and tag_id_string == "texture_nmap":
                    preview_nmap_msg = str("Maping value for normal maps is in the case of imported shader\n"
                                           "also used for defining uv map layer for tangent calculations!\n"
                                           "If the uv map is not provided first entry from Mappings list above will be used!")
                    _shared.draw_warning_operator(item_space_row, "Mapping Info", preview_nmap_msg, icon="INFO")

                # add ensuring operator for norma map uv mapping
                if tag_id_string == "texture_nmap":
                    props = item_space_row.operator("mesh.scs_ensure_active_uv", text="", icon="FILE_REFRESH")
                    props.mat_name = mat.name
                    props.uv_layer = uv_mappings[0].value

                if mapping.value and mapping.value != "" and mapping.value in bpy.context.active_object.data.uv_layers:
                    icon = "GROUP_UVS"
                else:
                    icon = "ERROR"

                item_space_row.prop_search(
                    data=mapping,
                    property="value",
                    search_data=bpy.context.active_object.data,
                    search_property='uv_layers',
                    text="",
                    icon=icon,
                )

    else:
        texture_box.row().label('Unsupported Shader Texture Type!', icon="ERROR")


def _draw_shader_parameters(layout, mat, scs_props, scs_globals, read_only=False):
    """Creates Shader Parameters sub-panel."""
    split_perc = 0.3
    # panel_header = layout_box.split(percentage=0.5)
    # panel_header_1 = panel_header.row()
    # panel_header_1.prop(scene.scs_props, 'shader_presets_expand', text="Shader Parameters:", icon='TRIA_DOWN', icon_only=True, emboss=False)
    # panel_header_1.label('Shader Parameters:', icon='NONE')

    shader_data = mat.get("scs_shader_attributes", {})
    # print(' shader_data: %s' % str(shader_data))

    if len(shader_data) == 0:
        info_box = layout.box()
        info_box.label('Select a shader from the preset list.', icon='ERROR')
    else:
        # PRESET INFO
        # print(' ...active_shader_preset_name: %r' % str(mat.scs_props.active_shader_preset_name))
        preset_name = mat.scs_props.active_shader_preset_name.upper()
        # effect_name = shader_data.get('effect', "NO EFFECT")
        effect_name = mat.scs_props.mat_effect_name
        effect_name = str('"' + effect_name + '"')
        preset_info_row = layout.row()
        preset_info_space = preset_info_row.split(percentage=split_perc, align=True)
        preset_info_space.label(preset_name, icon='NONE')
        preset_info_space.label(effect_name, icon='NONE')

        # MATERIAL SUBSTANCE
        substance_row = layout.row()
        substance_row.enabled = not read_only
        substance_row = substance_row.split(percentage=split_perc)
        substance_row.label("Substance:")
        substance_row = substance_row.split(percentage=(1 - split_perc) * 0.2, align=True)
        props = substance_row.operator("material.scs_looks_wt", text="WT")
        props.property_str = "substance"
        substance_row.prop_search(mat.scs_props, 'substance', scs_globals, 'scs_matsubs_inventory', icon='NONE', text="")

        if len(shader_data['attributes']) == 0 and len(shader_data['textures']) == 0:
            info_box = layout.box()
            if shader_data['effect'].endswith('mlaaweight'):
                info_box.label('"Multi Level Anti-Aliasing" shader has no parameters.', icon='INFO')
            else:
                info_box.label('No shader parameters!', icon='INFO')

        if 'attributes' in shader_data and len(shader_data["attributes"]) > 0:

            attributes_box = layout.box()
            attributes_box.enabled = not read_only

            if scs_props.shader_attributes_expand:
                panel_header = attributes_box.split(percentage=0.5)
                panel_header_1 = panel_header.row()
                panel_header_1.prop(
                    scs_props,
                    'shader_attributes_expand',
                    text="Material Attributes",
                    icon='TRIA_DOWN',
                    icon_only=True,
                    emboss=False
                )

                attributes_data = shader_data['attributes']
                if attributes_data:

                    for attribute_key in sorted(attributes_data.keys()):
                        _draw_shader_attribute(attributes_box, mat, split_perc, attributes_data[attribute_key])

            else:
                panel_header = attributes_box.split(percentage=0.5)
                panel_header_1 = panel_header.row()
                panel_header_1.prop(
                    scs_props,
                    'shader_attributes_expand',
                    text="Material Attributes",
                    icon='TRIA_RIGHT',
                    icon_only=True,
                    emboss=False
                )

        if 'textures' in shader_data and len(shader_data["textures"]) > 0:
            textures_box = layout.box()
            if scs_props.shader_textures_expand:
                panel_header = textures_box.split(percentage=0.5)
                panel_header_1 = panel_header.row()
                panel_header_1.prop(
                    scs_props,
                    'shader_textures_expand',
                    text="Material Textures",
                    icon='TRIA_DOWN',
                    icon_only=True,
                    emboss=False
                )

                textures_data = shader_data['textures']
                if textures_data:

                    if read_only:

                        mappings_box = textures_box.box()
                        row = mappings_box.row()
                        row.label("Mappings:", icon="GROUP_UVS")
                        row = mappings_box.row()
                        row.template_list(
                            'SCSMaterialCustomMappingSlot',
                            list_id="",
                            dataptr=mat.scs_props,
                            propname="custom_tex_coord_maps",
                            active_dataptr=mat.scs_props,
                            active_propname="active_custom_tex_coord",
                            rows=3,
                            maxrows=5,
                            type='DEFAULT',
                            columns=9
                        )

                        col = row.column(align=True)
                        col.operator('material.add_custom_tex_coord_map', text="", icon='ZOOMIN')
                        col.operator('material.remove_custom_tex_coord_map', text="", icon='ZOOMOUT')

                    for texture_key in sorted(textures_data.keys()):
                        _draw_shader_texture(textures_box, mat, split_perc, textures_data[texture_key], read_only)
            else:
                panel_header = textures_box.split(percentage=0.5)
                panel_header_1 = panel_header.row()
                panel_header_1.prop(scs_props, 'shader_textures_expand', text="Material Textures", icon='TRIA_RIGHT', icon_only=True, emboss=False)


def _draw_preset_shader_panel(layout, mat, scene_scs_props, scs_globals):
    """Creates provisional Shader Preset sub-panel."""

    has_imported_shader = mat.scs_props.active_shader_preset_name == "<imported>"

    # SHADER PRESETS PANEL
    _draw_shader_presets(layout, scene_scs_props, scs_globals, read_only=has_imported_shader)

    # PARAMETERS PANEL
    _draw_shader_parameters(layout, mat, scene_scs_props, scs_globals, read_only=has_imported_shader)


'''
def draw_cgfx_data(layout):
    """Creates CgFX parameter sub-panel."""
    layout_box = layout.box()
    if scene.scs_props.cgfx_data_expand:
        panel_header = layout_box.row()
        panel_header.prop(
            scene.scs_props,
            'cgfx_data_expand',
            text=str('"' + mat.scs_props.cgfx_filename + '" Parameters:'),
            icon='TRIA_DOWN',
            icon_only=True,
            emboss=False
        )
        if cgfx_utils.get_cgfx_filepath(mat.scs_props.cgfx_filename):
            # layout_box_row = layout_box.row()
            # layout_box_row.operator('scene.print_cgfx_inventory', text='Print CgFX Inventory')

            ## SUBSTANCE
            layout_box_row = layout_box.row()
            layout_box_row.prop_search(mat.scs_props, 'substance', scs_globals, 'scs_matsubs_inventory', icon='NONE')

            ## ----- ##
            # layout_box_row = layout_box.row()
            # layout_box_row.prop(bpy.context.window.scs_globals, 'dummy', icon='NONE')
            # layout_box_row.prop(screen.scs_test, 'dummy', icon='NONE')
            # layout_box_row.prop(bpy.context.window.scs_test, 'dummy', icon='NONE')
            ## ----- ##

            # layout_box_row = layout_box.row()
            # layout_box_row.prop(screen.scs_cgfx_ui, 'wt_enum', text='')#, icon='LIBRARY_DATA_DIRECT', emboss=False)

            # if mat.scs_cgfx_looks[actual_look].cgfx_data:
            if 0:
                layout_box_row = layout_box.row()
                layout_box_row.separator()

                ## MAKE A LIST OF UI ITEMS NAMES FOR SORTING...
                ui_items = []
                for item in mat.scs_cgfx_looks[actual_look].cgfx_sorter:
                    if not item.name.endswith("_mtplr"):
                        ui_items.append(item.name)
                # item_i = 0

                for item in sorted(ui_items):
                    if item[4:] in mat.scs_cgfx_looks[actual_look].cgfx_data:
                        if not mat.scs_cgfx_looks[actual_look].cgfx_data[item[4:]].hide:
                            # layout_boxSplit = layout_box.split(percentage=0.8)
                            # cgfx_params_1 = layout_boxSplit.row()
                            cgfx_params_1 = layout_box.row()
                            cgfx_params_1.enabled = mat.scs_cgfx_looks[actual_look].cgfx_data[item[4:]].enabled
                            # cgfx_params_1.prop_enum(
                            #     screen.scs_cgfx_ui,
                            #     'wt_enum',
                            #     str(item_i),
                            #     text='',
                            #     icon='LIBRARY_DATA_DIRECT'
                            # )#, emboss=False)
                            # cgfx_params_1.prop(screen.scs_cgfx_ui, item, icon='NONE')#, text=item.name, expand=True, toggle=True)
                            cgfx_params_1.operator('scene.wt', text='', icon='LIBRARY_DATA_DIRECT')#, emboss=False)
                            parameter = mat.scs_cgfx_looks[actual_look].cgfx_data[item[4:]]
                            if parameter.type == "color":
                                cgfx_params_1Split = cgfx_params_1.split(percentage=0.8)
                                cgfx_params_1a = cgfx_params_1Split.row()
                                cgfx_params_1a.prop(screen.scs_cgfx_ui, str("cgfx_" + item[4:]), icon='NONE')
                                cgfx_params_1b = cgfx_params_1Split.row()
                                cgfx_params_1b.prop(screen.scs_cgfx_ui, str("cgfx_" + item[4:] + "_mtplr"), text='', icon='NONE')
                            else:
                                cgfx_params_1.prop(screen.scs_cgfx_ui, str("cgfx_" + item[4:]), icon='NONE')
                            # cgfx_params_2 = layout_boxSplit.row()
                            # cgfx_params_2.prop(parameter, 'value', text='', icon='NONE')#, expand=True, toggle=True)
                            # item_i += 1
            else:
                layout_box_row = layout_box.column()
                layout_box_row.label('CgFX Shader needs re-compilation!', icon='ERROR')
                layout_box_row.operator('material.recompile_cgfx', text="Recompile Shader")
    else:
        panel_header = layout_box.row()
        panel_header.prop(
            scene.scs_props,
            'cgfx_data_expand',
            text=str('"' + mat.scs_props.cgfx_filename + '" Parameters:'),
            icon='TRIA_RIGHT',
            icon_only=True,
            emboss=False
        )

def draw_cgfx_templates(layout):
    """Creates CgFX template sub-panel."""
    layout_box = layout.box()
    if scene.scs_props.cgfx_templates_expand:
        panel_header = layout_box.split(percentage=0.5)
        panel_header_1 = panel_header.row()
        panel_header_1.prop(scene.scs_props,
                            'cgfx_templates_expand',
                            text="Shader Templates:",
                            icon='TRIA_DOWN',
                            icon_only=True,
                            emboss=False)
        panel_header_2 = panel_header.row(align=True)
        panel_header_2.alignment = 'RIGHT'
        panel_header_2a = panel_header_2.row()
        panel_header_2a.prop(scene.scs_props, 'cgfx_templates_list_sorted', text='', icon='SORTALPHA', expand=True, toggle=True)

        ## CgFX Templates File (FILE_PATH)
        layout_box_row = layout_box.row(align=True)
        if _utils.is_valid_cgfx_template_library_path():
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
        layout_box_row.prop(scs_globals, 'cgfx_templates_filepath', text='', icon='FILE_TEXT')
        layout_box_row.operator('scene.select_cgfx_templates_filepath', text='', icon='FILESEL')

        layout_box_row = layout_box.column()
        layout_box_row.prop(scene.scs_props, 'cgfx_templates_list', expand=True, toggle=True)
    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props,
                            'cgfx_templates_expand',
                            text="Shader Templates:",
                            icon='TRIA_RIGHT',
                            icon_only=True,
                            emboss=False)
        layout_box_row.prop(scene.scs_props, 'cgfx_templates_list', text='')

def draw_cgfx_file_library(layout):
    """Creates CgFX library sub-panel."""
    layout_box = layout.box()
    if scene.scs_props.cgfx_lib_expand:
        panel_header = layout_box.split(percentage=0.5)
        panel_header_1 = panel_header.row()
        panel_header_1.prop(scene.scs_props, 'cgfx_lib_expand', text="Shader Library:", icon='TRIA_DOWN', icon_only=True, emboss=False)
        panel_header_2 = panel_header.row(align=True)
        panel_header_2.alignment = 'RIGHT'
        # panel_header_2a = panel_header_2.row()
        # panel_header_2a.prop(scene.scs_props, 'cgfx_list_sorted', text='', icon='SORTALPHA', expand=True, toggle=True)

        ## CgFX Library Directory (DIR_PATH - relative)
        layout_box_row = layout_box.row(align=True)
        if _utils.is_valid_cgfx_library_rel_path():
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
        layout_box_row.prop(scs_globals, 'cgfx_library_rel_path', text='', icon='FILE_FOLDER')
        layout_box_row.operator('scene.select_cgfx_library_rel_path', text='', icon='FILESEL')

        layout_box_row.operator('scene.select_cgfx_library_rel_path', text='', icon='FILESEL')
        layout_box_row = layout_box.column()
        layout_box_row.prop(scene.scs_props, 'cgfx_file_list', expand=True, toggle=True)
    else:
        layout_box_row = layout_box.row()
        layout_box_row.prop(scene.scs_props, 'cgfx_lib_expand', text="Shader Library:", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        layout_box_row.prop(scene.scs_props, 'cgfx_file_list', text='')

def draw_cgfx_shader_panel(layout):
    """Creates CgFX Shader sub-panel."""
    layout_box = layout.box()
    if scene.scs_props.cgfx_shader_expand:
        panel_header = layout_box.split(percentage=0.5)
        panel_header_1 = panel_header.row()
        panel_header_1.prop(scene.scs_props, 'cgfx_shader_expand', text="CgFX Shader", icon='TRIA_DOWN', icon_only=True, emboss=False)
        panel_header_2 = panel_header.row(align=True)
        panel_header_2.alignment = 'RIGHT'
        panel_header_2.label('version ' + str(version()), icon='DOT')

        ## CgFX TEMPLATE PANEL
        draw_cgfx_templates(layout_box)

        # CgFX LIBRARY PANEL
        if scene.scs_cgfx_template_inventory["<custom>"].active:
            draw_cgfx_file_library(layout_box)

        # CgFX PARAMETERS PANEL
        draw_cgfx_data(layout_box)

        # CgFX VERTEX DATA PANEL
        try:
            if len(mat.scs_cgfx_looks[actual_look].cgfx_vertex_data) > 0:
                draw_cgfx_vertex_data(layout_box)
        except:
            pass
    else:
        panel_header = layout_box.split(percentage=0.5)
        panel_header_1 = panel_header.row()
        panel_header_1.prop(scene.scs_props, 'cgfx_shader_expand', text="CgFX Shader", icon='TRIA_RIGHT', icon_only=True, emboss=False)
        panel_header_2 = panel_header.row(align=True)
        panel_header_2.alignment = 'RIGHT'
        panel_header_2.label('version ' + str(version()), icon='DOT')

def draw_cgfx_vertex_data(layout):
    """Creates CgFX parameter sub-panel."""
    layout_box = layout.box()
    if scene.scs_props.cgfx_vertex_data_expand:
        panel_header = layout_box.row()
        panel_header.prop(scene.scs_props, 'cgfx_vertex_data_expand', text='Vertex Data:', icon='TRIA_DOWN', icon_only=True, emboss=False)
        panel_header.label('')
        if cgfx_utils.get_cgfx_filepath(mat.scs_props.cgfx_filename):

            ## MAKE A LIST OF UI ITEMS NAMES FOR SORTING...
            ui_items = []
            for item in mat.scs_cgfx_looks[actual_look].cgfx_vertex_sorter:
                ui_items.append(item.name)
            # item_i = 0
            layout_box_row = layout_box.column()
            for item in sorted(ui_items):
                layout_box_row.prop(screen.scs_cgfx_vertex_ui, "cgfx_" + item[4:], icon='NONE')#, expand=True, toggle=True)
    else:
        panel_header = layout_box.row()
        panel_header.prop(scene.scs_props, 'cgfx_vertex_data_expand', text='Vertex Data:', icon='TRIA_RIGHT', icon_only=True, emboss=False)
        panel_header.label('')
'''


class SCSMaterialCustomMappingSlot(bpy.types.UIList):
    """
    Draw custom tex coord item slot within Custom Mapping list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        line = layout.split(percentage=0.4, align=False)
        line.prop(item, "name", text="", emboss=False, icon_value=icon)

        if item.value == "" or item.value not in bpy.context.active_object.data.uv_layers:
            icon = "ERROR"
        else:
            icon = "GROUP_UVS"

        line.prop_search(
            data=item,
            property="value",
            search_data=bpy.context.active_object.data,
            search_property='uv_layers',
            text="",
            icon=icon,
        )


class SCSMaterialSpecials(_MaterialPanelBlDefs, bpy.types.Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = "SCS Materials"
    bl_idname = "MATERIAL_PT_SCS_materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        """UI draw function."""
        layout = self.layout
        scene = bpy.context.scene
        mat = context.material
        scs_globals = _get_scs_globals()

        if mat:
            # PROVISIONAL SHADER PRESET PANEL
            _draw_preset_shader_panel(layout.box(), mat, scene.scs_props, scs_globals)

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if active_object and scs_root_object:
                _shared.draw_scs_looks_panel(layout, scene, active_object, scs_root_object)
