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
from bpy.types import Panel
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories
from io_scs_tools.ui import shared as _shared

_UI_SPLIT_PERC = 0.5


class _MaterialPanelBlDefs:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return hasattr(context, "active_object") and context.active_object and context.active_object.active_material

    def get_layout(self):
        """Returns layout depending where it's drawn into. If popover create extra box to make it distinguisable between different sub-panels."""
        if self.is_popover:
            layout = self.layout.box().column()
        else:
            layout = self.layout

        return layout


class SCS_TOOLS_UL_MaterialCustomMappingSlot(bpy.types.UIList):
    """
    Draw custom tex coord item slot within Custom Mapping list
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        line = layout.split(factor=0.4, align=False)
        line.prop(item, "name", text="", emboss=False, icon_value=icon)

        if item.value == "" or item.value not in bpy.context.active_object.data.uv_layers:
            icon = 'ERROR'
        else:
            icon = 'GROUP_UVS'

        line.prop_search(
            data=item,
            property="value",
            search_data=bpy.context.active_object.data,
            search_property='uv_layers',
            text="",
            icon=icon,
        )


class SCS_TOOLS_PT_Material(_shared.HeaderIconPanel, _MaterialPanelBlDefs, Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = "SCS Material"

    @staticmethod
    def draw_shader_presets(layout, scs_props, scs_globals, scs_inventories, is_imported_shader=False):
        """Creates Shader Presets sub-panel."""
        layout_box = layout.box()
        layout_box.enabled = not is_imported_shader
        if scs_props.shader_presets_expand:
            panel_header = layout_box.split(factor=0.5)
            panel_header_1 = panel_header.row()
            panel_header_1.prop(scs_props, 'shader_presets_expand', text="Shader Presets:", icon='TRIA_DOWN', icon_only=True, emboss=False)
            panel_header_2 = panel_header.row(align=True)
            panel_header_2.alignment = 'RIGHT'
            panel_header_2a = panel_header_2.row()
            panel_header_2a.prop(scs_props, 'shader_presets_sorted', text="", icon='SORTALPHA', expand=True, toggle=True)

            layout_box_row = layout_box.row(align=True)
            if _path_utils.is_valid_shader_presets_library_path():
                layout_box_row.alert = False
            else:
                layout_box_row.alert = True
            layout_box_row.prop(scs_globals, 'shader_presets_filepath', text="", icon='FILE_TEXT')
            layout_box_row.operator('scene.scs_tools_select_shader_presets_path', text="", icon='FILEBROWSER')

            layout_box_row = layout_box.column()
            layout_box_row.prop(scs_inventories, 'shader_presets', expand=True, toggle=True)
        else:
            layout_box_row = layout_box.row().split(factor=0.4)
            layout_box_row.prop(scs_props, 'shader_presets_expand', text="Shader Presets:", icon='TRIA_RIGHT', icon_only=True, emboss=False)

            column = layout_box_row.column(align=True)

            row = column.row(align=True)
            if is_imported_shader:
                row.prop(bpy.context.material.scs_props, "active_shader_preset_name", icon='COLOR', text="")
            else:
                row.prop(scs_inventories, 'shader_presets', text="")
            row.operator("material.scs_tools_search_shader_preset", text="", icon='VIEWZOOM')

    @staticmethod
    def draw_flavors(layout, mat):
        """Draws shader flavors if any.

        :param layout: layout to draw on
        :type layout: bpy.types.UILayout
        :param mat: material for which flavors should be drawn
        :type mat: bpy.types.Material
        """

        if mat.scs_props.active_shader_preset_name == "<none>":
            return

        preset = _shader_presets.get_preset(mat.scs_props.active_shader_preset_name)
        if preset:

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
            """:type: dict[int, io_scs_tools.internals.shader_presets.ui_shader_preset_item.FlavorVariant]"""
            flavor_rows = []  # store row UI layout of flavor operators, for later analyzing which rows should be disabled
            for i, flavor in enumerate(preset.flavors):

                row = column.row(align=True)
                flavor_rows.append(row)

                for flavor_variant in flavor.variants:

                    is_in_middle = "." + flavor_variant.suffix + "." in effect_flavor_part
                    is_on_end = effect_flavor_part.endswith("." + flavor_variant.suffix)
                    flavor_enabled = is_in_middle or is_on_end

                    icon = _shared.get_on_off_icon(flavor_enabled)
                    props = row.operator("material.scs_tools_switch_flavor", text=flavor_variant.suffix, icon=icon, depress=flavor_enabled)
                    props.flavor_name = flavor_variant.suffix
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
                            new_flavor_str += "." + flavor_variant.suffix
                            curr_flavor_added = True

                        new_flavor_str += "." + enabled_flavors[enabled_i].suffix

                    if not curr_flavor_added:
                        new_flavor_str += "." + flavor_variant.suffix

                    # 2. check if proposed new flavor combination exists in cache:
                    # if not then row on current flavor index has to be disabled
                    if not _shader_presets.has_section(preset.name, new_flavor_str):
                        flavor_rows[i].enabled = False
                        break

    @staticmethod
    def draw_parameters(layout, mat, scs_inventories, split_perc, is_imported_shader=False):
        """Creates Shader Parameters sub-panel."""
        shader_data = mat.get("scs_shader_attributes", {})
        # print(' shader_data: %s' % str(shader_data))

        if len(shader_data) == 0:
            info_box = layout.column()
            info_box.label(text="Select a shader from the preset list.", icon='ERROR')
        else:

            # MISSING VERTEX COLOR
            active_vcolors = bpy.context.active_object.data.vertex_colors
            is_valid_vcolor = _MESH_consts.default_vcol in active_vcolors
            is_valid_vcolor_a = _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix in active_vcolors
            if not is_valid_vcolor or not is_valid_vcolor_a:

                vcol_missing_box = layout.box()

                title_row = vcol_missing_box.row(align=True)
                title_row.label(text="Vertex color layer(s) missing!", icon='ERROR')

                col = vcol_missing_box.column(align=True)

                info_msg = "Currently active object is missing vertex color layers with names:\n"
                if not is_valid_vcolor:
                    info_msg += "-> '" + _MESH_consts.default_vcol + "'\n"

                if not is_valid_vcolor_a:
                    info_msg += "-> '" + _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix + "'\n"

                info_msg += "You can use 'Add Vertex Colors To (Active/All)' button to add needed layers or add layers manually."
                _shared.draw_warning_operator(col, "Vertex Colors Missing", info_msg, text="More Info", icon='INFO')

                col.operator("mesh.scs_tools_add_vertex_colors_to_active")
                col.operator("mesh.scs_tools_add_vertex_colors_to_all")

            global_mat_attr = layout.column(align=True)
            # global_mat_attr.alignment = 'RIGHT'
            global_mat_attr.enabled = not is_imported_shader

            # PRESET INFO
            preset_info_row = global_mat_attr.row(align=True)
            preset_info_space = preset_info_row.split(factor=split_perc, align=True)
            preset_info_space.alignment = 'RIGHT'
            preset_info_space.label(text="Effect")
            preset_info_space.alignment = 'LEFT'
            preset_info_space.prop(mat.scs_props, "mat_effect_name", emboss=False, text="")

            # MATERIAL ALIASING
            alias_row = global_mat_attr.row()
            alias_row = alias_row.split(factor=split_perc)
            alias_row.alignment = 'RIGHT'
            alias_row.label(text="Aliasing")

            alias_row = alias_row.row(align=True)
            alias_text = "Enabled" if mat.scs_props.enable_aliasing else "Disabled"
            alias_icon = _shared.get_on_off_icon(mat.scs_props.enable_aliasing)
            alias_row.prop(mat.scs_props, "enable_aliasing", icon=alias_icon, text=alias_text, toggle=True)

            normalized_base_tex_path = mat.scs_props.shader_texture_base.replace("\\", "/")
            is_aliasing_path = ("/material/road" in normalized_base_tex_path or
                                "/material/terrain" in normalized_base_tex_path or
                                "/material/custom" in normalized_base_tex_path)

            is_aliasable = ('textures' in shader_data and
                            (
                                    len(shader_data["textures"]) == 1 or
                                    (len(shader_data["textures"]) == 2 and "dif.spec.weight.mult2" in mat.scs_props.mat_effect_name)
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

                    _shared.draw_warning_operator(alias_row, "Aliasing Info", aliasing_info_msg, icon='INFO')

                alias_op_col = alias_row.column(align=True)
                alias_op_col.enabled = is_aliasing_path and is_aliasable
                alias_op_col.operator('material.scs_tools_load_aliased_material', icon='IMPORT', text="")

            # MATERIAL SUBSTANCE
            substance_row = global_mat_attr.split(factor=split_perc)
            tag_layout = substance_row.row()
            tag_layout.alignment = 'RIGHT'
            tag_layout.label(text="Substance")
            tag_value = substance_row.row(align=True)
            tag_value.prop_search(mat.scs_props, 'substance', scs_inventories, 'matsubs', icon='NONE', text="")
            props = tag_value.operator("material.scs_tools_material_item_extras", text="", icon="LAYER_USED")
            props.property_str = "substance"

            if len(shader_data['attributes']) == 0 and len(shader_data['textures']) == 0:
                if shader_data['effect'].endswith('mlaaweight'):
                    layout.label(text="'Multi Level Anti-Aliasing' shader has no parameters.", icon='INFO')
                else:
                    layout.label(text="No shader parameters!", icon='INFO')

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator("material.scs_tools_merge_materials", text="", emboss=True, icon="FULLSCREEN_EXIT")
        layout.separator(factor=0.1)

    def draw(self, context):
        """UI draw function."""

        # draw minimalistict info, so user knows what's going on
        if not self.poll(context):
            self.layout.label(text="No active material!", icon="INFO")
            return

        layout = self.get_layout()
        workspace = context.workspace
        mat = context.active_object.active_material
        scs_globals = _get_scs_globals()
        scs_inventories = _get_scs_inventories()

        # disable pane if config is being updated
        layout.enabled = not scs_globals.config_update_lock

        if mat:
            is_imported_shader = mat.scs_props.active_shader_preset_name == "<imported>"

            # COLOR MANAGEMENT WARNING
            if not _material_utils.has_valid_color_management(context.scene):
                warning_box = layout.box()
                warning_box.label(text="Scene color management invalid!", icon="ERROR")
                warning_box.operator("material.scs_tools_adapt_color_management", icon="COLOR")

            # SHADER PRESETS PANEL
            SCS_TOOLS_PT_Material.draw_shader_presets(layout, workspace.scs_props, scs_globals, scs_inventories,
                                                      is_imported_shader=is_imported_shader)

            # FLAVORS PANEL
            SCS_TOOLS_PT_Material.draw_flavors(layout, mat)

            # PARAMETERS PANEL
            SCS_TOOLS_PT_Material.draw_parameters(layout, mat, scs_inventories, _UI_SPLIT_PERC, is_imported_shader=is_imported_shader)


class SCS_TOOLS_PT_MaterialAttributes(_MaterialPanelBlDefs, Panel):
    """Draws attributes of current material in sub-panel."""
    bl_parent_id = SCS_TOOLS_PT_Material.__name__
    bl_label = "Material Attributes"

    @classmethod
    def poll(cls, context):
        if not _MaterialPanelBlDefs.poll(context):
            return False

        mat = context.active_object.active_material
        shader_data = mat.get("scs_shader_attributes", {})

        if len(shader_data) == 0:
            return False

        if 'attributes' not in shader_data:
            return False

        if len(shader_data["attributes"]) == 0:
            return False

        cls.attributes_data = shader_data['attributes']
        cls.is_imported_shader = mat.scs_props.active_shader_preset_name == "<imported>"
        return True

    @staticmethod
    def draw_attribute_item(layout, mat, split_perc, attribute):
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
        attribute_label = frendly_tag if frendly_tag else str(tag.replace('_', ' ').title())
        hide_state = attribute.get('Hide', None)
        lock_state = attribute.get('Lock', None)
        preview_only_state = attribute.get('PreviewOnly', None)

        # ignore substance from attributes because it's drawn before already
        if tag.lower() == "substance":
            return

        if hide_state == 'True':
            return

        attr_row = layout.row(align=True)
        item_space = attr_row.split(factor=split_perc, align=True)

        label_icon = 'ERROR'
        if lock_state == 'True':
            item_space.enabled = False
            attribute_label = str(attribute_label + " (locked)")
            label_icon = 'LOCKED'

        tag_layout = item_space.row()
        tag_layout.alignment = 'RIGHT'
        tag_layout.label(text=attribute_label)

        # create info operator for preview only attributes
        if preview_only_state == "True":
            _shared.draw_warning_operator(tag_layout,
                                          "Preview Attribute Info",
                                          "This attribute is used for preview only.\n"
                                          "It won't be exported so it doesn't matter what value is used.",
                                          icon='INFO')

        '''
        shader_attribute_id = str("shader_attribute_" + tag)
        if shader_attribute_id in mat.scs_props:
            item_space.prop(mat.scs_props, shader_attribute_id, text="")
        else:
            print(' %r is NOT defined in SCS Blender Tools...!' % shader_attribute_id)
        '''
        value_layout = item_space.row(align=True)

        if tag == 'diffuse':
            value_layout.prop(mat.scs_props, 'shader_attribute_diffuse', text="")
            if linked_vals:
                value_layout.prop(mat, 'diffuse_color', text="")
        elif tag == 'specular':
            value_layout.prop(mat.scs_props, 'shader_attribute_specular', text="")
            if linked_vals:
                value_layout.prop(mat, 'specular_color', text="")
        elif tag == 'shininess':
            value_layout.prop(mat.scs_props, 'shader_attribute_shininess', text="")
            # if linked_vals: value_layout.prop(mat, 'specular_intensity', text="")
            if linked_vals:
                value_layout.prop(mat, 'specular_hardness', text="")
        elif tag == 'add_ambient':
            value_layout.prop(mat.scs_props, 'shader_attribute_add_ambient', text="")
            if linked_vals:
                value_layout.prop(mat, 'ambient', text="")
        elif tag == 'reflection':
            value_layout.prop(mat.scs_props, 'shader_attribute_reflection', text="")
            if linked_vals:
                value_layout.prop(mat.raytrace_mirror, 'reflect_factor', text="")
        elif tag == 'reflection2':
            value_layout.prop(mat.scs_props, 'shader_attribute_reflection2', text="")
        elif tag == 'shadow_bias':
            value_layout.prop(mat.scs_props, 'shader_attribute_shadow_bias', text="")
            if linked_vals:
                value_layout.prop(mat, 'shadow_buffer_bias', text="")
        elif tag == 'env_factor':
            value_layout.prop(mat.scs_props, 'shader_attribute_env_factor', text="")
        elif tag == 'fresnel':
            value_layout.column().prop(mat.scs_props, 'shader_attribute_fresnel', text="")
        elif tag == 'tint':
            value_layout.prop(mat.scs_props, 'shader_attribute_tint', text="")
        elif tag == 'tint_opacity':
            value_layout.prop(mat.scs_props, 'shader_attribute_tint_opacity', text="")
        elif tag == 'queue_bias':
            value_layout.prop(mat.scs_props, 'shader_attribute_queue_bias', text="")
        elif tag.startswith("aux") and hasattr(mat.scs_props, "shader_attribute_" + tag):

            col = value_layout.column().column(align=True)

            auxiliary_prop = getattr(mat.scs_props, "shader_attribute_" + tag, None)

            for item in auxiliary_prop:
                col.prop(item, 'value', text="")

        else:
            value_layout.label(text="Undefined Shader Attribute Type!", icon=label_icon)

        props = value_layout.operator("material.scs_tools_material_item_extras", text="", icon="LAYER_USED", emboss=True)
        props.property_str = "shader_attribute_" + tag

    def draw(self, context):
        mat = context.active_object.active_material

        layout = self.get_layout()
        layout.enabled = not self.is_imported_shader

        attrs_column = layout.column()  # create column for compact display with alignment
        for attribute_key in sorted(self.attributes_data.keys()):
            self.draw_attribute_item(attrs_column, mat, _UI_SPLIT_PERC, self.attributes_data[attribute_key])


class SCS_TOOLS_PT_MaterialTextures(_MaterialPanelBlDefs, Panel):
    """Draws textures of current material in sub-panel."""
    bl_parent_id = SCS_TOOLS_PT_Material.__name__
    bl_label = "Material Textures"

    @classmethod
    def poll(cls, context):
        if not _MaterialPanelBlDefs.poll(context):
            return False

        mat = context.active_object.active_material
        shader_data = mat.get("scs_shader_attributes", {})

        if len(shader_data) == 0:
            return False

        if 'textures' not in shader_data:
            return False

        if len(shader_data["textures"]) == 0:
            return False

        cls.textures_data = shader_data['textures']
        cls.is_imported_shader = mat.scs_props.active_shader_preset_name == "<imported>"
        return True

    @staticmethod
    def draw_texture_item(layout, mat, split_perc, texture, read_only):
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

        header_split = texture_box.row(align=True)
        header_split.label(text=texture_type.title(), icon='TEXTURE')

        if hasattr(mat.scs_props, shader_texture_id):

            shader_texture = mat.scs_props.get(shader_texture_id, "")
            # imported tobj boolean switch (only for imported shaders)
            use_imported_tobj = getattr(mat.scs_props, shader_texture_id + "_use_imported", False)
            if read_only:
                row = header_split.row(align=True)
                row.prop(mat.scs_props, shader_texture_id + "_use_imported")

                if use_imported_tobj:

                    texture_row = texture_box.row(align=True)
                    texture_split = texture_row.split(factor=split_perc, align=True)
                    tag_layout = texture_split.row(align=True)
                    tag_layout.alignment = 'RIGHT'
                    tag_layout.label(text="TOBJ Path")

                    tag_value = texture_split.row(align=True)
                    tag_value.prop(mat.scs_props, shader_texture_id + "_imported_tobj", text="")

                    props = tag_value.operator("material.scs_tools_material_item_extras", text="", icon="LAYER_USED")
                    props.property_str = shader_texture_id + "_imported_tobj"

            # disable whole texture layout if it's locked
            texture_box.enabled = not mat.scs_props.get(shader_texture_id + "_locked", False)

            texture_row = texture_box.row(align=True)
            item_space = texture_row.split(factor=split_perc, align=True)
            item_space.alignment = 'RIGHT'

            # in case of custom tobj value texture is used only for preview
            if read_only and use_imported_tobj:
                item_space.label(text="Preview Tex")
            else:
                item_space.label(text="Texture")

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

            layout_box_row = layout_box_row.row(align=True)

            # MARK EMPTY SLOTS
            layout_box_row.alert |= (shader_texture == "")

            if layout_box_row.alert:
                _shared.draw_warning_operator(layout_box_row,
                                              title="Texture Not Found",
                                              message="Texture with given path doesn't exists or SCS Project Base Path is not properly set!")

            layout_box_row.prop(mat.scs_props, shader_texture_id, text="", icon=texture_icon)

            props = layout_box_row.operator('material.scs_tools_select_texture_path', text="", icon='FILEBROWSER')
            props.shader_texture = shader_texture_id  # DYNAMIC ID SAVE (FOR FILE REQUESTER)

            props = layout_box_row.operator("material.scs_tools_material_item_extras", text="", icon="LAYER_USED")
            props.property_str = shader_texture_id

            # ADDITIONAL TEXTURE SETTINGS
            if (not read_only or (read_only and not use_imported_tobj)) and texture_box.enabled:

                tobj_filepath = _path_utils.get_tobj_path_from_shader_texture(shader_texture)

                tobj_settings_row = layout_box_col.row(align=True)

                if not tobj_filepath:
                    props = tobj_settings_row.operator("mmaterial.scs_tools_create_tobj", icon='FILE_NEW', text="")
                    props.texture_type = texture_type
                    # creating extra column->row so it can be properly disabled as tobj doesn't exists
                    tobj_settings_row = tobj_settings_row.column(align=True).row(align=True)

                # enable settings only if tobj exists and map type of the tobj is 2d
                tobj_settings_row.enabled = tobj_filepath is not None and getattr(mat.scs_props, shader_texture_id + "_map_type", "") == "2d"

                if tobj_filepath:
                    mtime = str(os.path.getmtime(tobj_filepath))
                    tobj_settings_row.alert = (mtime != getattr(mat.scs_props, shader_texture_id + "_tobj_load_time", "NOT FOUND"))
                    props = tobj_settings_row.operator("material.scs_tools_reload_tobj", icon='FILE_REFRESH', text="")
                    props.texture_type = texture_type
                else:
                    tobj_settings_row.alert = True

                tobj_settings_row.prop_menu_enum(
                    mat.scs_props,
                    str('shader_' + tag_id_string + '_settings'),
                    icon='SETTINGS',
                )

            # UV LAYERS FOR TEXTURE
            uv_mappings = getattr(mat.scs_props, "shader_" + tag_id_string + "_uv", None)

            if len(uv_mappings) > 0:

                texture_row = texture_box.row(align=True)
                item_space = texture_row.split(factor=split_perc, align=True)
                item_space.alignment = 'RIGHT'
                if read_only:
                    item_space.label(text="Preview UV Map")
                else:
                    item_space.label(text="Mapping")
                layout_box_col = item_space.column(align=True)

                for mapping in uv_mappings:

                    item_space_row = layout_box_col.row(align=True)

                    # add info about normal map uv mapping property in case of imported shader
                    if read_only and tag_id_string == "texture_nmap":
                        preview_nmap_msg = str("Maping value for normal maps is in the case of imported shader\n"
                                               "also used for defining uv map layer for tangent calculations!\n"
                                               "If the uv map is not provided first entry from Mappings list above will be used!")
                        _shared.draw_warning_operator(item_space_row, "Mapping Info", preview_nmap_msg, icon='INFO')

                    if mapping.value and mapping.value != "" and mapping.value in bpy.context.active_object.data.uv_layers:
                        icon = 'GROUP_UVS'
                    else:
                        icon = 'ERROR'

                    item_space_row.prop_search(
                        data=mapping,
                        property="value",
                        search_data=bpy.context.active_object.data,
                        search_property='uv_layers',
                        text="",
                        icon=icon,
                    )

        else:
            texture_box.row().label(text="Unsupported Shader Texture Type!", icon='ERROR')

    def draw(self, context):
        mat = context.active_object.active_material

        if self.is_imported_shader:

            mappings_box = self.layout.box()
            row = mappings_box.row()
            row.label(text="Mappings:", icon='GROUP_UVS')
            row = mappings_box.row()
            row.template_list(
                SCS_TOOLS_UL_MaterialCustomMappingSlot.__name__,
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
            col.operator('material.scs_tools_add_custom_tex_coord_mapping', text="", icon='ADD')
            col.operator('material.scs_tools_remove_custom_tex_coord_mapping', text="", icon='REMOVE')

        col = self.layout.column(align=True)
        for texture_key in sorted(self.textures_data.keys()):
            self.draw_texture_item(col, mat, _UI_SPLIT_PERC, self.textures_data[texture_key], self.is_imported_shader)


class SCS_TOOLS_PT_LooksOnMaterial(_shared.HeaderIconPanel, _MaterialPanelBlDefs, Panel):
    """Draws SCS Looks panel on object tab."""

    bl_label = "SCS Looks"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not _MaterialPanelBlDefs.poll(context):
            return False

        cls.object = context.active_object
        cls.scs_root = _object_utils.get_scs_root(cls.object)
        return cls.object and cls.scs_root

    def draw(self, context):
        layout = self.get_layout()
        _shared.draw_scs_looks_panel(layout, self.object, self.scs_root, without_box=True)


classes = (
    SCS_TOOLS_PT_Material,
    SCS_TOOLS_PT_MaterialAttributes,
    SCS_TOOLS_PT_MaterialTextures,
    SCS_TOOLS_PT_LooksOnMaterial,
    SCS_TOOLS_UL_MaterialCustomMappingSlot,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from io_scs_tools import SCS_TOOLS_MT_MainMenu
    SCS_TOOLS_MT_MainMenu.append_props_entry("Material Properties", SCS_TOOLS_PT_Material.__name__)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
