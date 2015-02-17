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
from bpy.props import (BoolProperty,
                       StringProperty,
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty)
import re
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.utils import material as _material_utils

'''
# class MaterialCgFXShaderData(bpy.types.PropertyGroup):
#     """
#     CgFX data record, which gets saved within "material.scs_cgfx_looks" into *.blend file.
#     """
#     name = StringProperty(name="Data Name", default="")
#     ui_name = StringProperty(name="UI Name", default="")
#     ui_description = StringProperty(name="UI Description", default="")
#     type = StringProperty(name="Data Type", default="")
#     value = StringProperty(name="Data Value", default="")
#     update_function = StringProperty(name="Update Function", default="")
#     hide = BoolProperty(name="Hide Data", default=False)
#     enabled = BoolProperty(name="Data Enabled", default=True)
#
#     enum_items = StringProperty(name="Enum Items", default="")
#     define = BoolProperty(name="Data Define", default=False)
#
#
# class CgFXItemSorter(bpy.types.PropertyGroup):
#     """CgFX item sorter."""
#     pass
#
#
# class MaterialCgFXVertexShaderData(bpy.types.PropertyGroup):
#     """
#     CgFX data record, which gets saved within "material.scs_cgfx_looks" into *.blend file.
#     """
#     name = StringProperty(name="Data Name", default="")
#     ui_name = StringProperty(name="UI Name", default="")
#     ui_description = StringProperty(name="UI Description", default="")
#     type = StringProperty(name="Data Type", default="")
#     value = StringProperty(name="Data Value", default="")
#     update_function = StringProperty(name="Update Function", default="")
#     hide = BoolProperty(name="Hide Data", default=False)
#     enabled = BoolProperty(name="Data Enabled", default=True)
#
#
# class CgFXVertexItemSorter(bpy.types.PropertyGroup):
#     """CgFX item sorter."""
#     pass
#
#
# class MaterialCgFXShaderLooks(bpy.types.PropertyGroup):
#     """
#     CgFX Shader data on Materials.
#     """
#     name = StringProperty(name="CgFX Shader Look Name", default="")
#     cgfx_data = CollectionProperty(type=MaterialCgFXShaderData)
#     cgfx_sorter = CollectionProperty(type=CgFXItemSorter)
#     cgfx_vertex_data = CollectionProperty(type=MaterialCgFXVertexShaderData)
#     cgfx_vertex_sorter = CollectionProperty(type=CgFXVertexItemSorter)
'''


class MaterialSCSTools(bpy.types.PropertyGroup):
    """
    SCS Tools Material Variables - ...Material.scs_props...
    :return:
    """

    _shader_texture_types = []

    # @staticmethod
    def get_shader_texture_types(self):
        """SCS shader texture types which are currently deffined in SCS Blender Tools.

        :return: SCS Shader Texture Types
        :rtype: tuple
        """
        return self._shader_texture_types

    # global matsubs_items
    # matsubs_items = []

    # # Following String property is fed from MATERIAL SUBSTANCE data list, which is usually loaded from
    # # "//base/material/material.db" file and stored at "scs_globals.scs_matsubs_inventory".
    substance = StringProperty(
        name="Substance",
        description="Substance",
        default="None",
        subtype='NONE',
    )

    # Shader Preset Attribute Values
    def update_diffuse(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            material.diffuse_color = self.shader_attribute_diffuse
            texture_slot = _material_utils.get_texture_slot(material, 'base')
            if texture_slot:
                _material_utils.set_diffuse(texture_slot, material, self.shader_attribute_diffuse)

    def update_specular(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            material.specular_color = self.shader_attribute_specular
            material.specular_intensity = self.shader_attribute_specular.v

    def update_shininess(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            # material.specular_intensity = self.shader_attribute_shininess
            material.specular_hardness = self.shader_attribute_shininess

    def update_add_ambient(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            material.ambient = self.shader_attribute_add_ambient

    def update_reflection(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            material.raytrace_mirror.reflect_factor = self.shader_attribute_reflection
            if self.shader_attribute_reflection == 0:
                material.raytrace_mirror.use = False
            else:
                material.raytrace_mirror.use = True

    def update_shadow_bias(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            material.shadow_buffer_bias = self.shader_attribute_shadow_bias

    def update_env_factor(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:

            texture_slot = _material_utils.get_texture_slot(material, 'reflection')
            # print('deBug --- texture_slot: %r' % str(texture_slot.name))
            if texture_slot:
                # print('deBug --- TEXTURE SLOT %r SET [update_env_factor()]' % str(texture_slot.name))
                _material_utils.set_env_factor(texture_slot, self.shader_attribute_env_factor)
                # else:
                # print('deBug --- NO TEXTURE SLOT [update_env_factor()]')

    shader_attribute_diffuse = FloatVectorProperty(
        name="Diffuse",
        description="SCS shader 'Diffuse' value",
        default=(0.0, 0.0, 0.0),
        min=0, max=5,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='COLOR',
        size=3,
        update=update_diffuse,
        # unit='NONE', get=None, set=None,
    )
    shader_attribute_specular = FloatVectorProperty(
        name="Specular",
        description="SCS shader 'Specular' value",
        default=(0.0, 0.0, 0.0),
        min=0, max=5,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='COLOR',
        size=3,
        update=update_specular,
        # unit='NONE', get=None, set=None,
    )
    shader_attribute_shininess = FloatProperty(
        name="Shininess",
        description="SCS shader 'Shininess' value",
        default=0.0,
        min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=100,
        precision=2,
        options={'HIDDEN'},
        update=update_shininess,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )
    shader_attribute_add_ambient = FloatProperty(
        name="Add Ambient",
        description="SCS shader 'Add Ambient' value",
        default=0.0,
        min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_add_ambient,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )
    shader_attribute_reflection = FloatProperty(
        name="Reflection",
        description="SCS shader 'Reflection' value",
        default=0.0,
        min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_reflection,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )
    shader_attribute_reflection2 = FloatProperty(
        name="Reflection 2",
        description="SCS shader 'Reflection 2' value",
        default=0.0,
        min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_reflection,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )
    shader_attribute_shadow_bias = FloatProperty(
        name="Shadow Bias",
        description="SCS shader 'Shadow Bias' value",
        default=0.0,
        min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_shadow_bias,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )
    shader_attribute_env_factor = FloatVectorProperty(
        name="Env Factor",
        description="SCS shader 'Env Factor' value",
        default=(1.0, 1.0, 1.0),
        min=0, max=5,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='COLOR',
        size=3,
        update=update_env_factor,
        # unit='NONE', get=None, set=None,
    )
    shader_attribute_fresnel = FloatVectorProperty(
        name="Fresnel",
        description="SCS shader 'Fresnel' value",
        default=(0.2, 0.9),
        min=0, max=5,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='NONE',
        size=2,
        # update=update_fresnel,
        # unit='NONE', get=None, set=None,
    )
    shader_attribute_tint = FloatVectorProperty(
        name="Tint",
        description="SCS shader 'Tint' value",
        default=(1.0, 1.0, 1.0),
        min=0, max=5,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='COLOR',
        size=3,
        # update=update_tint,
        # unit='NONE', get=None, set=None,
    )
    shader_attribute_tint_opacity = FloatProperty(
        name="Tint Opacity",
        description="SCS shader 'Tint Opacity' value",
        default=0.0,
        # min=0.0,
        # max=sys.float_info.max,
        # soft_min=sys.float_info.min,
        # soft_max=sys.float_info.max,
        step=1,
        precision=2,
        options={'HIDDEN'},
        # update=update_tint_opacity,
        # subtype='NONE', unit='NONE', get=None, set=None,
    )

    class AuxiliaryItem(bpy.types.PropertyGroup):
        """Class for saving flaot value of different auxiliary items
        """

        value = FloatProperty(
            default=0.0,
            options={'HIDDEN'}
        )

    shader_attribute_aux3 = CollectionProperty(
        name="Aux [3]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [3]' value",
        options={'HIDDEN'},
    )
    shader_attribute_aux5 = CollectionProperty(
        name="Aux [5]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [5]' value",
        options={'HIDDEN'},
    )
    shader_attribute_aux6 = CollectionProperty(
        name="Aux [6]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [6]' value",
        options={'HIDDEN'},
    )
    shader_attribute_aux7 = CollectionProperty(
        name="Aux [7]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [7]' value",
        options={'HIDDEN'},
    )
    shader_attribute_aux8 = CollectionProperty(
        name="Aux [8]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [8]' value",
        options={'HIDDEN'},
    )

    # # Shader Preset Texture Values
    texture_settings = [
        ('u_repeat', "U Repeat", "Repeat texture in U direction"),
        ('v_repeat', "V Repeat", "Repeat texture in V direction"),
        # ('rgb_only', "RGB Only", "When texture has an Alpha channel, use RGB channels only"),
        ('tsnormal', "TS Normal", "Tangent Space Normal for the texture"),
        # ('bias', "Bias", "MIP Maps Bias..."),
        ('nomips', "No MIP Maps", "Don't use MIP Maps for the texture"),
        ('nocompress', "No Compress", "Don't use compression on texture"),
        # ('quality:high', "High Quality", "") # TODO: ask around
    ]

    def update_shader_texture_base(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_base, 'base')

    shader_texture_base = StringProperty(
        name="Texture Base",
        description="Texture Base for active Material",
        default="",  # maxlen=0,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_base,
        # get=None, set=None,
    )
    _shader_texture_types.append("shader_texture_base")

    class UVMappingItem(bpy.types.PropertyGroup):

        def update_value(self, context):

            material = _material_utils.get_material_from_context(context)

            if material:
                tex_slot = _material_utils.get_texture_slot(material, self.texture_type)
                # if texture slot exists set "uv_layer" property to reflect choosen uv from our settings to viewport
                if tex_slot:
                    tex_slot.uv_layer = self.value

                # synchronize all scs textures mappings that uses the same tex_coord field in current material
                if "scs_shader_attributes" in material and "textures" in material["scs_shader_attributes"]:
                    for tex_entry in material["scs_shader_attributes"]["textures"].values():
                        if "Tag" in tex_entry:
                            curr_tex_type = tex_entry["Tag"].split(":")[1][8:]
                            if curr_tex_type != self.texture_type:  # if different texture from current
                                texture_mappings = getattr(material.scs_props, "shader_texture_" + curr_tex_type + "_uv")
                                if texture_mappings and len(texture_mappings) > 0:
                                    for tex_mapping in texture_mappings:
                                        # if tex_coord props are the same and uv mapping differs then set current uv mapping value to it
                                        if self.tex_coord != -1 and tex_mapping.tex_coord == self.tex_coord and tex_mapping.value != self.value:
                                            tex_mapping.value = self.value

        value = StringProperty(
            name="Texture UV Set",
            description="Mapping of UV Set to current texture type",
            default="",
            options={'HIDDEN'},
            update=update_value
        )

        tex_coord = IntProperty(default=-1)  # used upon export for mapping uv to tex_coord field
        texture_type = StringProperty()  # used in update fuction to be able to identify which texture should be updated

    shader_texture_base_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_base_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Base",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
        # update=None, get=None, set=None,
    )
    shader_texture_base_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_base_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_base_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_nmap(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_nmap, 'nmap')

    shader_texture_nmap = StringProperty(
        name="Texture NMap",
        description="Texture NMap for active Material",
        default="",  # maxlen=0,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_nmap,
        # get=None, set=None,
    )
    _shader_texture_types.append("shader_texture_nmap")

    shader_texture_nmap_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_nmap_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture NMap",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
        # update=None, get=None, set=None,
    )
    shader_texture_nmap_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_nmap_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_nmap_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_reflection(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_reflection, 'reflection')

    shader_texture_reflection = StringProperty(
        name="Texture Reflection",
        description="Texture Reflection for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_reflection,
    )
    _shader_texture_types.append("shader_texture_reflection")
    shader_texture_reflection_uv = CollectionProperty(
        name="Texture Reflection UV Sets",
        description="Texture Reflection UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_reflection_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Reflection",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_reflection_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_reflection_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_reflection_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_over(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_over, 'over')

    shader_texture_over = StringProperty(
        name="Texture Over",
        description="Texture Over for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_over,
    )
    _shader_texture_types.append("shader_texture_over")
    shader_texture_over_uv = CollectionProperty(
        name="Texture Over UV Sets",
        description="Texture Over UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_over_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Over",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_over_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_over_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_over_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_oclu(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_oclu, 'oclu')

    shader_texture_oclu = StringProperty(
        name="Texture Oclu",
        description="Texture Oclu for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_oclu,
    )
    _shader_texture_types.append("shader_texture_oclu")
    shader_texture_oclu_uv = CollectionProperty(
        name="Texture Oclu UV Sets",
        description="Texture Oclu UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_oclu_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Oclu",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_oclu_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_oclu_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_oclu_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_mask(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_mask, 'mask')

    shader_texture_mask = StringProperty(
        name="Texture Mask",
        description="Texture Mask for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_mask,
    )
    _shader_texture_types.append("shader_texture_mask")
    shader_texture_mask_uv = CollectionProperty(
        name="Texture Mask UV Sets",
        description="Texture Mask UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_mask_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Mask",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_mask_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_mask_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_mask_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_mult(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_mult, 'mult')

    shader_texture_mult = StringProperty(
        name="Texture Mult",
        description="Texture Mult for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_mult,
    )
    _shader_texture_types.append("shader_texture_mult")
    shader_texture_mult_uv = CollectionProperty(
        name="Texture Mult UV Sets",
        description="Texture Mult UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_mult_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Mult",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_mult_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_mult_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_mult_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_iamod(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_iamod, 'iamod')

    shader_texture_iamod = StringProperty(
        name="Texture Iamod",
        description="Texture Iamod for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_iamod,
    )
    _shader_texture_types.append("shader_texture_iamod")
    shader_texture_iamod_uv = CollectionProperty(
        name="Texture Iamod UV Sets",
        description="Texture Iamod UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_iamod_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Iamod",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_iamod_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_iamod_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_iamod_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_lightmap(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_lightmap, 'lightmap')

    shader_texture_lightmap = StringProperty(
        name="Texture Lightmap",
        description="Texture Lightmap for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_lightmap,
    )
    _shader_texture_types.append("shader_texture_lightmap")
    shader_texture_lightmap_uv = CollectionProperty(
        name="Texture Lightmap UV Sets",
        description="Texture Lightmap UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_lightmap_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Lightmap",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_lightmap_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_lightmap_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_lightmap_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_paintjob(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_paintjob, 'paintjob')

    shader_texture_paintjob = StringProperty(
        name="Texture Paintjob",
        description="Texture Paintjob for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_paintjob,
    )
    _shader_texture_types.append("shader_texture_paintjob")
    shader_texture_paintjob_uv = CollectionProperty(
        name="Texture Paintjob UV Sets",
        description="Texture Paintjob UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_paintjob_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Paintjob",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_paintjob_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_paintjob_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_paintjob_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    def update_shader_texture_flakenoise(self, context):

        material = _material_utils.get_material_from_context(context)

        if material:
            _material_utils.update_texture_slots(material, self.shader_texture_flakenoise, 'flakenoise')

    shader_texture_flakenoise = StringProperty(
        name="Texture Flakenoise",
        description="Texture Flakenoise for active Material",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_flakenoise,
    )
    _shader_texture_types.append("shader_texture_flakenoise")
    shader_texture_flakenoise_uv = CollectionProperty(
        name="Texture Flakenoise UV Sets",
        description="Texture Flakenoise UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )
    shader_texture_flakenoise_settings = EnumProperty(
        name="Settings",
        description="Additional settings for Texture Flakenoise",
        items=texture_settings,
        default=set(),
        options={'ENUM_FLAG'},
    )
    shader_texture_flakenoise_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False
    )
    shader_texture_flakenoise_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default=""
    )
    shader_texture_flakenoise_export_tobj = BoolProperty(
        name="Export TOBJ",
        description="Export TOBJ file (NOTE: if checked export will overwrite any existing one with the same name)",
        default=False
    )

    class TexCoordItem(bpy.types.PropertyGroup):
        """
        Property group holding data how to map uv maps to exported PIM file. It should be used only on material with imported shader.
        """

        def update_name(self, context):

            if hasattr(context, "active_object") and hasattr(context.active_object, "active_material"):
                material = context.active_object.active_material
                if material:

                    custom_maps = material.scs_props.shader_custom_tex_coord_maps
                    # force prescribed pattern for name ("tex_coord_X" where X is unsigned integer) and avoid duplicates
                    if not re.match("\Atex_coord_\d+\Z", self.name) or len(_inventory.get_indices(custom_maps, self.name)) == 2:
                        i = 0
                        new_name = "tex_coord_" + str(i)
                        while _inventory.get_index(custom_maps, new_name) != -1:
                            i += 1
                            new_name = "tex_coord_" + str(i)

                        if self.name != new_name:
                            self.name = new_name

        name = StringProperty(update=update_name)
        value = StringProperty(description="UV map used for this tex_coord field")

    shader_custom_tex_coord_maps = CollectionProperty(
        description="List of tex coord fields used for determinating how uv layers will be exported. The number of the tex coord field specify "
                    "order of exporting.",
        type=TexCoordItem,
    )
    active_custom_tex_coord = IntProperty(
        name="Active TexCoord Mapping",
        description="Must have for showing the TecCoord mappings in the template list",
        default=0
    )

    # # Active Shader Preset for Material
    active_shader_preset_name = StringProperty(
        name="Active Shader Preset Name",
        description="Active shader preset name for active Material",
        default="<none>",
        subtype='NONE',
    )
    mat_effect_name = StringProperty(
        name="Shader Effect Name",
        description="SCS shader effect name",
        default="eut2.dif",
        subtype='NONE',
    )