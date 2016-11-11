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
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shader_presets import cache as _shader_presets_cache
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_shader_presets_inventory as _get_shader_presets_inventory
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


def _draw_shader_flavors(layout, mat):
    """Draws shader flavors if any.

    :param layout: layout to draw on
    :type layout: bpy.types.UILayout
    :param mat: material for which flavors should be drawn
    :type mat: bpy.types.Material
    """

    if mat.scs_props.active_shader_preset_name == "<none>":
        return

    for preset in _get_shader_presets_inventory():
        if preset.name == mat.scs_props.active_shader_preset_name:

            # if there is no flavors in found preset,
            # then we don't have to draw anything so exit drawing shader flavors right away
            if len(preset.flavors) <= 0:
                return

            # strip of base effect name, to avoid any flavor matching in base effect name
            effect_flavor_part = mat.scs_props.mat_effect_name[len(preset.effect):]

            column = layout.column(align=True)
            column.alignment = "LEFT"

            # draw switching operator for each flavor (if there is more variants draw operator for each variant)
            enabled_flavors = {}  # store enabled flavors, for later analyzing which rows should be disabled
            flavor_rows = []  # store row UI layout of flavor operators, for later analyzing which rows should be disabled
            for i, flavor in enumerate(preset.flavors):

                row = column.row(align=True)
                flavor_rows.append(row)

                for flavor_variant in flavor.variants:

                    is_in_middle = "." + flavor_variant.name + "." in effect_flavor_part
                    is_on_end = effect_flavor_part.endswith("." + flavor_variant.name)
                    flavor_enabled = is_in_middle or is_on_end

                    icon = "FILE_TICK" if flavor_enabled else "X"
                    props = row.operator("material.scs_switch_flavor", text=flavor_variant.name, icon=icon)
                    props.flavor_name = flavor_variant.name
                    props.flavor_enabled = flavor_enabled

                    if flavor_enabled:
                        enabled_flavors[i] = flavor_variant

            # now as we drawn the flavors and we know which ones are enabled,
            # search the ones that are not compatible with currently enabled flavors and disable them in UI!
            for i, flavor in enumerate(preset.flavors):

                # enabled flavors have to stay enabled so skip them
                if i in enabled_flavors:
                    continue

                for flavor_variant in flavor.variants:

                    # 1. construct proposed new flavor string:
                    # combine strings of enabled flavors and current flavor variant
                    new_flavor_str = ""
                    curr_flavor_added = False
                    for enabled_i in enabled_flavors.keys():

                        if i < enabled_i and not curr_flavor_added:
                            new_flavor_str += "." + flavor_variant.name
                            curr_flavor_added = True

                        new_flavor_str += "." + enabled_flavors[enabled_i].name

                    if not curr_flavor_added:
                        new_flavor_str += "." + flavor_variant.name

                    # 2. check if proposed new flavor combination exists in cache:
                    # if not then row on current flavor index has to be disabled
                    if not _shader_presets_cache.has_section(preset, new_flavor_str):
                        flavor_rows[i].enabled = False
                        break

            # once preset was found just use return to skip other presets
            return


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
    frendly_tag = attribute.get('FriendlyTag', None)
    attribute_label = frendly_tag + ":" if frendly_tag else str(tag.replace('_', ' ').title() + ":")
    hide_state = attribute.get('Hide', None)
    lock_state = attribute.get('Lock', None)
    preview_only_state = attribute.get('PreviewOnly', None)

    # ignore substance from attributes because it's drawn before already
    if tag.lower() == "substance":
        return

    if hide_state == 'True':
        return

    attr_row = layout.row(align=True)
    item_space = attr_row.split(percentage=split_perc, align=True)

    label_icon = 'ERROR'
    if lock_state == 'True':
        item_space.enabled = False
        attribute_label = str(attribute_label[:-1] + " (locked):")
        label_icon = 'LOCKED'

    tag_layout = item_space.row()
    tag_layout.label(attribute_label)

    # create info operator for preview only attributes
    if preview_only_state == "True":
        _shared.draw_warning_operator(tag_layout,
                                      "Preview Attribute Info",
                                      "This attribute is used for preview only.\n"
                                      "It won't be exported so it doesn't matter what value is used.",
                                      icon="INFO")

    '''
    shader_attribute_id = str("shader_attribute_" + tag)
    if shader_attribute_id in mat.scs_props:
        item_space.prop(mat.scs_props, shader_attribute_id, text='')
    else:
        print(' %r is NOT defined in SCS Blender Tools...!' % shader_attribute_id)
    '''

    item_space = item_space.split(percentage=1 / (1 - split_perc + 0.000001) * 0.1, align=True)
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

    texture_box = layout.box().column()  # create column for compact display with alignment

    header_split = texture_box.row(align=True).split(percentage=0.5)
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

                texture_row = texture_box.row(align=True)
                item_space = texture_row.split(percentage=split_perc, align=True)
                item_space.label("TOBJ Path:")

                item_space = item_space.split(percentage=1 / (1 - split_perc + 0.000001) * 0.1, align=True)
                props = item_space.operator("material.scs_looks_wt", text="WT")
                props.property_str = shader_texture_id
                item_space.prop(mat.scs_props, shader_texture_id + "_imported_tobj", text="")

        # disable whole texture layout if it's locked
        texture_box.enabled = not mat.scs_props.get(shader_texture_id + "_locked", False)

        texture_row = texture_box.row(align=True)
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
        if _path_utils.is_valid_shader_texture_path(shader_texture):
            layout_box_row.alert = False
        else:
            layout_box_row.alert = True
            texture_icon = 'NONE'  # info operator will have icon, so texture path should use none

        # MARK EMPTY SLOTS
        if shader_texture == "":
            layout_box_row.alert = True

        layout_box_row = layout_box_row.split(percentage=1 / (1 - split_perc + 0.000001) * 0.1, align=True)
        props = layout_box_row.operator("material.scs_looks_wt", text="WT")
        props.property_str = shader_texture_id

        layout_box_row = layout_box_row.row(align=True)
        layout_box_row.prop(mat.scs_props, shader_texture_id, text='', icon=texture_icon)

        if layout_box_row.alert:  # add info operator when texture path is invalid
            _shared.draw_warning_operator(layout_box_row,
                                          title="Texture Not Found",
                                          message="Texture with given path doesn't exists or SCS Project Base Path is not properly set!")

        props = layout_box_row.operator('material.scs_select_shader_texture_filepath', text='', icon='FILESEL')
        props.shader_texture = shader_texture_id  # DYNAMIC ID SAVE (FOR FILE REQUESTER)

        # ADDITIONAL TEXTURE SETTINGS
        if (not read_only or (read_only and not use_imported_tobj)) and texture_box.enabled:

            tobj_filepath = _path_utils.get_tobj_path_from_shader_texture(shader_texture)

            tobj_settings_row = layout_box_col.row(align=True)
            tobj_settings_row = tobj_settings_row.split(percentage=1 / (1 - split_perc + 0.000001) * 0.1, align=True)

            if not tobj_filepath:
                props = tobj_settings_row.operator("material.scs_create_tobj", icon="NEW", text="")
                props.texture_type = texture_type
                # creating extra column->row so it can be properly disabled as tobj doesn't exists
                tobj_settings_row = tobj_settings_row.column(align=True).row(align=True)

            # enable settings only if tobj exists and map type of the tobj is 2d
            tobj_settings_row.enabled = tobj_filepath is not None and getattr(mat.scs_props, shader_texture_id + "_map_type", "") == "2d"

            if tobj_filepath:
                mtime = str(os.path.getmtime(tobj_filepath))
                tobj_settings_row.alert = (mtime != getattr(mat.scs_props, shader_texture_id + "_tobj_load_time", "NOT FOUND"))
            else:
                tobj_settings_row.alert = True

            props = tobj_settings_row.operator("material.scs_reload_tobj", icon="LOAD_FACTORY", text="")
            props.texture_type = texture_type

            tobj_settings_row.prop_menu_enum(
                mat.scs_props,
                str('shader_' + tag_id_string + '_settings'),
                icon='SETTINGS',
            )

        # UV LAYERS FOR TEXTURE
        uv_mappings = getattr(mat.scs_props, "shader_" + tag_id_string + "_uv", None)

        if len(uv_mappings) > 0:

            texture_row = texture_box.row(align=True)
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
    split_perc = scs_props.shader_item_split_percentage
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

        # MISSING VERTEX COLOR
        active_vcolors = bpy.context.active_object.data.vertex_colors
        is_valid_vcolor = _MESH_consts.default_vcol in active_vcolors
        is_valid_vcolor_a = _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix in active_vcolors
        if not is_valid_vcolor or not is_valid_vcolor_a:

            vcol_missing_box = layout.box()

            title_row = vcol_missing_box.row(align=True)
            title_row.label("Vertex color layer(s) missing!", icon="ERROR")

            info_msg = "Currently active object is missing vertex color layers with names:\n"
            if not is_valid_vcolor:
                info_msg += "-> '" + _MESH_consts.default_vcol + "'\n"

            if not is_valid_vcolor_a:
                info_msg += "-> '" + _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix + "'\n"

            info_msg += "You can use 'Add Vertex Colors To (Active/All)' button to add needed layers or add layers manually."
            _shared.draw_warning_operator(title_row, "Vertex Colors Missing", info_msg, text="More Info", icon="INFO")

            col = vcol_missing_box.column(align=True)
            col.operator("mesh.scs_add_vcolors_to_active")
            col.operator("mesh.scs_add_vcolors_to_all")

        global_mat_attr = layout.column(align=False)

        # UI SPLIT PERCENTAGE PROPERTY
        global_mat_attr.row().prop(scs_props, "shader_item_split_percentage", slider=True)

        # PRESET INFO
        effect_name = mat.scs_props.mat_effect_name
        effect_name = str('"' + effect_name + '"')
        preset_info_row = global_mat_attr.row()
        preset_info_space = preset_info_row.split(percentage=split_perc, align=True)
        preset_info_space.label("Effect:", icon='NONE')
        preset_info_space.label(effect_name, icon='NONE')

        # MATERIAL ALIASING
        alias_row = global_mat_attr.row()
        alias_row.enabled = not read_only
        alias_row = alias_row.split(percentage=split_perc)
        alias_row.label("Aliasing:")

        alias_row = alias_row.row(align=True)
        alias_text = "Enabled" if mat.scs_props.enable_aliasing else "Disabled"
        alias_icon = "FILE_TICK" if mat.scs_props.enable_aliasing else "X_VEC"
        alias_row.prop(mat.scs_props, "enable_aliasing", icon=alias_icon, text=alias_text, toggle=True)

        normalized_base_tex_path = mat.scs_props.shader_texture_base.replace("\\", "/")
        is_aliasing_path = ("/material/road" in normalized_base_tex_path or
                            "/material/terrain" in normalized_base_tex_path or
                            "/material/custom" in normalized_base_tex_path)

        is_aliasable = ('textures' in shader_data and
                        (
                            len(shader_data["textures"]) == 1 or
                            (len(shader_data["textures"]) == 2 and "dif.spec.weight.mult2" in effect_name)
                        ))

        if mat.scs_props.enable_aliasing:

            if not (is_aliasing_path and is_aliasable):

                aliasing_info_msg = str("Material aliasing will work only for materials which 'Base' texture\n"
                                        "is loaded from this directories and their subdirectories:\n"
                                        "-> '/material/road'\n"
                                        "-> '/material/terrain'\n"
                                        "-> '/material/custom'\n"
                                        "Additional requirement for aliasing is also single texture material or\n"
                                        "exceptionally multi texture material of 'dif.spec.weight.mult2' family.\n\n"
                                        "Currently aliasing can not be done because:")

                if not is_aliasing_path:
                    aliasing_info_msg += "\n-> Your 'Base' texture doesn't point to any of this (sub)directories."
                if not is_aliasable:
                    aliasing_info_msg += "\n-> Current shader type use multiple textures or it's not 'dif.spec.weight.mult2' family type."

                _shared.draw_warning_operator(alias_row, "Aliasing Info", aliasing_info_msg, icon="INFO")

            alias_op_col = alias_row.column(align=True)
            alias_op_col.enabled = is_aliasing_path and is_aliasable
            alias_op_col.operator('material.load_aliased_material', icon="LOAD_FACTORY", text="")

        # MATERIAL SUBSTANCE
        substance_row = global_mat_attr.row()
        substance_row.enabled = not read_only
        substance_row = substance_row.split(percentage=split_perc)
        substance_row.label("Substance:")
        substance_row = substance_row.split(percentage=1 / (1 - split_perc + 0.000001) * 0.1, align=True)
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
                    attrs_column = attributes_box.column()  # create column for compact display with alignment
                    for attribute_key in sorted(attributes_data.keys()):
                        _draw_shader_attribute(attrs_column, mat, split_perc, attributes_data[attribute_key])

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

    # FLAVORS PANEL
    _draw_shader_flavors(layout, mat)

    # PARAMETERS PANEL
    _draw_shader_parameters(layout, mat, scene_scs_props, scs_globals, read_only=has_imported_shader)


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

        # disable pane if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        if mat:
            # PROVISIONAL SHADER PRESET PANEL
            _draw_preset_shader_panel(layout.box(), mat, scene.scs_props, scs_globals)

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if active_object and scs_root_object:
                _shared.draw_scs_looks_panel(layout, scene, active_object, scs_root_object)
