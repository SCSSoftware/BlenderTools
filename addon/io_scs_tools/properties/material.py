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

# Copyright (C) 2013-2015: SCS Software

import bpy
from bpy.props import (BoolProperty,
                       StringProperty,
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty)
import os
import re
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.exp import tobj as _tobj_exp
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals.shaders import shader as _shader
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint


def __get_texture_settings__():
    """Returns texture settings relavant for artist.

    :return: items for texture settings enum property
    :rtype: list[tuple]
    """
    return [
        ('u_repeat', "U Repeat", "Repeat texture in U direction"),
        ('v_repeat', "V Repeat", "Repeat texture in V direction"),
        ('tsnormal', "TS Normal", "Tangent Space Normal for the texture"),
        ('color_space_linear', "Color Space Linear", "Texture is in linear color space (usually used for oclussion type of shaders)"),
    ]


def __update_look__(self, context):
    """Hookup function for triggering update look from material in internal module of looks.
    It should be used on any property which should be saved in exported into looks.
    :param context: Blender context
    :type context: bpy.types.Context
    """

    if hasattr(context, "active_object") and hasattr(context.active_object, "active_material") and context.active_object.active_material:

        is_preset_change = "preset_change" in self

        scs_roots = []
        if is_preset_change:  # on preset change we have to update all scs roots to sync shader type
            scs_roots = _object_utils.gather_scs_roots(bpy.data.objects)
        else:
            scs_root = _object_utils.get_scs_root(context.active_object)
            if scs_root:
                scs_roots.append(scs_root)

        for scs_root in scs_roots:
            _looks.update_look_from_material(scs_root, context.active_object.active_material, is_preset_change)


def __update_shader_attribute__(self, context, attr_type):
    """Hookup function for updating shader attributes in Blender.

    :param context: Blender context
    :type context: bpy.types.Context
    :param attr_type: type of attribute to update in shader
    :type attr_type: str
    """
    __update_look__(self, context)

    material = _material_utils.get_material_from_context(context)

    if material:
        _shader.set_attribute(material, attr_type, getattr(self, "shader_attribute_" + attr_type, None))


def __update_shader_texture_tobj_file__(self, context, tex_type):
    """Hookup function for updating TOBJ file on any texture type.

    :param context: Blender context
    :type context: bpy.types.Context
    :param tex_type: string representig texture type
    :type tex_type: str
    """

    # dummy context arg usage so IDE doesn't report it as unused
    if context == context:
        pass

    shader_texture_str = "shader_texture_" + tex_type

    texture_raw_path = getattr(self, shader_texture_str)
    texture_settings = getattr(self, shader_texture_str + "_settings")

    tobj_file = _path_utils.get_tobj_path_from_shader_texture(texture_raw_path)
    if tobj_file:

        # if raw path endswith tobj get raw texture path from existing tobj
        # otherwise we assume that tobj is referencing texture file directly by name
        if texture_raw_path.endswith(".tobj"):
            texture_name = _path_utils.get_texture_path_from_tobj(tobj_file, raw_value=True)
        else:
            texture_name = os.path.basename(texture_raw_path)

        # update last tobj load time if export was successful otherwise report saving problems
        if _tobj_exp.export(tobj_file, texture_name, texture_settings):
            self[shader_texture_str + "_tobj_load_time"] = str(os.path.getmtime(tobj_file))
        else:
            lprint("", report_warnings=-1, report_errors=-1)
            lprint("E Settings in TOBJ file not saved; content is malformed or referencing none existing textures!\n\t   "
                   "Please check TOBJ's content in your favorite text editor; file path:\n\t   %r",
                   (_path_utils.readable_norm(tobj_file),))
            lprint("", report_warnings=1, report_errors=1)


def __update_shader_texture__(self, context, tex_type):
    """Hookup function for update of shader texture of any texture type.

    :param context: Blender context
    :type context: bpy.types.Context
    :param tex_type: string representing texture type
    :type tex_type: str
    """

    __update_look__((), context)

    material = _material_utils.get_material_from_context(context)

    if material:
        shader_texture_str = "shader_texture_" + tex_type
        shader_texture_filepath = getattr(self, shader_texture_str)

        # always correct scs texture path string
        # NOTE: this is unified way to acquire proper texture string for
        # selected image entity with operator or direct user value input
        # Similar thing is done on import through set_shader_data_to_material.
        shader_texture_filepath = self[shader_texture_str] = _path_utils.get_scs_texture_str(shader_texture_filepath)

        # create texture and use it on shader
        texture = _material_utils.get_texture(shader_texture_filepath, tex_type, report_invalid=True)

        _shader.set_texture(material, tex_type, texture)

        # reload TOBJ settings
        _material_utils.reload_tobj_settings(material, tex_type)


class MaterialSCSTools(bpy.types.PropertyGroup):
    """
    SCS Tools Material Variables - ...Material.scs_props...
    :return:
    """

    class AuxiliaryItem(bpy.types.PropertyGroup):
        """Class for saving float value of different auxiliary items
        """

        def update_value(self, context):

            __update_look__(self, context)

            material = _material_utils.get_material_from_context(context)

            if material:
                _shader.set_attribute(material, self.aux_type, getattr(material.scs_props, "shader_attribute_" + self.aux_type, None))

        value = FloatProperty(
            default=0.0,
            step=0.1,
            precision=4,
            options={'HIDDEN'},
            update=update_value
        )
        aux_type = StringProperty()  # used in update function to be able to identify which auxiliary is owning this item

    class UVMappingItem(bpy.types.PropertyGroup):
        """Class for saving uv map reference for SCS texture
        """

        def update_value(self, context):
            __update_look__(self, context)

            material = _material_utils.get_material_from_context(context)

            if material:
                _shader.set_uv(material, self.texture_type, self.value, self.tex_coord)

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
        texture_type = StringProperty()  # used in update function to be able to identify which texture should be updated

    class TexCoordItem(bpy.types.PropertyGroup):
        """Property group holding data how to map uv maps to exported PIM file. It should be used only on material with imported shader.
        """

        def update_name(self, context):
            __update_look__(self, context)

            if hasattr(context, "active_object") and hasattr(context.active_object, "active_material"):
                material = context.active_object.active_material
                if material:

                    custom_maps = material.scs_props.custom_tex_coord_maps
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
        value = StringProperty(description="UV map used for this tex_coord field", update=__update_look__)

    @staticmethod
    def get_texture_types():
        """SCS texture types which are currently defined in SCS Blender Tools and their corresponding texture slot index.

        :return: SCS Shader Texture Types
        :rtype: dict
        """
        return {'base': 5, 'reflection': 6, 'over': 7, 'oclu': 8,
                'mask': 9, 'mult': 10, 'iamod': 11, 'lightmap': 12,
                'paintjob': 13, 'flakenoise': 14, 'nmap': 15,
                'base_1': 16, 'mult_1': 17, 'detail': 18, 'nmap_detail': 19,
                'layer0': 20, 'layer1': 21}

    def get_id(self):
        """Gets unique ID for material within current Blend file. If ID does not exists yet it's calculated.
        :return: unique ID
        :rtype: int
        """

        # make sure to fix cached mat num if some materials are deleted
        if MaterialSCSTools._cached_mat_num > len(bpy.data.materials):
            MaterialSCSTools._cached_mat_num = len(bpy.data.materials)

        if "mat_id" in self and len(bpy.data.materials) != MaterialSCSTools._cached_mat_num:
            mat_count = 0
            for mat in bpy.data.materials:
                if "mat_id" in mat.scs_props and mat.scs_props["mat_id"] == self["mat_id"]:
                    mat_count += 1
                    if mat_count > 1:
                        del self["mat_id"]
                        # update cached materials count only when duplicate is actually detected not on just any material
                        MaterialSCSTools._cached_mat_num = len(bpy.data.materials)
                        break

        # if this material doesn't yet have ID assign it
        if "mat_id" not in self:
            existing_ids = {}
            for material in bpy.data.materials:
                if "mat_id" in material.scs_props:
                    existing_ids[material.scs_props["mat_id"]] = 1

            value = 0
            while value in existing_ids:
                value += 1

            self["mat_id"] = value
            lprint("S material ID set: %s", (value,))

        lprint("S material ID get: %s", (self["mat_id"],))
        return self["mat_id"]

    def update_active_shader_preset_name(self, context):
        self["preset_change"] = True  # indicate that this is shader preset update
        __update_look__(self, context)
        del self["preset_change"]  # remove indicator of shader preset update

    def update_shader_attribute_add_ambient(self, context):
        __update_shader_attribute__(self, context, "add_ambient")

    def update_shader_attribute_diffuse(self, context):
        __update_shader_attribute__(self, context, "diffuse")

    def update_shader_attribute_env_factor(self, context):
        __update_shader_attribute__(self, context, "env_factor")

    def update_shader_attribute_fresnel(self, context):
        __update_shader_attribute__(self, context, "fresnel")

    def update_shader_attribute_shininess(self, context):
        __update_shader_attribute__(self, context, "shininess")

    def update_shader_attribute_specular(self, context):
        __update_shader_attribute__(self, context, "specular")

    def update_shader_attribute_tint(self, context):
        __update_shader_attribute__(self, context, "tint")

    def update_shader_attribute_tint_opacity(self, context):
        __update_shader_attribute__(self, context, "tint_opacity")

    def update_shader_texture_base(self, context):
        __update_shader_texture__(self, context, "base")

    def update_shader_texture_base_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "base")

    def update_shader_texture_base_1(self, context):
        __update_shader_texture__(self, context, "base_1")

    def update_shader_texture_base_1_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "base_1")

    def update_shader_texture_detail(self, context):
        __update_shader_texture__(self, context, "detail")

    def update_shader_texture_detail_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "detail")

    def update_shader_texture_flakenoise(self, context):
        __update_shader_texture__(self, context, "flakenoise")

    def update_shader_texture_flakenoise_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "flakenoise")

    def update_shader_texture_iamod(self, context):
        __update_shader_texture__(self, context, "iamod")

    def update_shader_texture_iamod_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "iamod")

    def update_shader_texture_layer0(self, context):
        __update_shader_texture__(self, context, "layer0")

    def update_shader_texture_layer0_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "layer0")

    def update_shader_texture_layer1(self, context):
        __update_shader_texture__(self, context, "layer1")

    def update_shader_texture_layer1_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "layer1")

    def update_shader_texture_lightmap(self, context):
        __update_shader_texture__(self, context, "lightmap")

    def update_shader_texture_lightmap_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "lightmap")

    def update_shader_texture_mask(self, context):
        __update_shader_texture__(self, context, "mask")

    def update_shader_texture_mask_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "mask")

    def update_shader_texture_mult(self, context):
        __update_shader_texture__(self, context, "mult")

    def update_shader_texture_mult_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "mult")

    def update_shader_texture_mult_1(self, context):
        __update_shader_texture__(self, context, "mult_1")

    def update_shader_texture_mult_1_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "mult_1")

    def update_shader_texture_nmap(self, context):
        __update_shader_texture__(self, context, "nmap")

    def update_shader_texture_nmap_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "nmap")

    def update_shader_texture_nmap_detail(self, context):
        __update_shader_texture__(self, context, "nmap_detail")

    def update_shader_texture_nmap_detail_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "nmap_detail")

    def update_shader_texture_oclu(self, context):
        __update_shader_texture__(self, context, "oclu")

    def update_shader_texture_oclu_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "oclu")

    def update_shader_texture_over(self, context):
        __update_shader_texture__(self, context, "over")

    def update_shader_texture_over_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "over")

    def update_shader_texture_paintjob(self, context):
        __update_shader_texture__(self, context, "paintjob")

    def update_shader_texture_paintjob_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "paintjob")

    def update_shader_texture_reflection(self, context):
        __update_shader_texture__(self, context, "reflection")

    def update_shader_texture_reflection_settings(self, context):
        __update_shader_texture_tobj_file__(self, context, "reflection")

    _cached_mat_num = -1
    """Caching number of all materials to properly fix material ids when duplicating material"""

    active_custom_tex_coord = IntProperty(
        name="Active TexCoord Mapping",
        description="Must have for showing the TexCoord mappings in the template list",
        default=0
    )

    active_shader_preset_name = StringProperty(
        name="Active Shader Preset Name",
        description="Active shader preset name for active Material",
        default="<none>",
        subtype='NONE',
        update=update_active_shader_preset_name
    )

    custom_tex_coord_maps = CollectionProperty(
        description="List of tex coord fields used for determinating order and number of exported uv layers. "
                    "The number of the tex coord field specify order of exporting.",
        type=TexCoordItem,
    )

    enable_aliasing = BoolProperty(
        name="Aliasing",
        description="Enabling material aliasing on this material.",
        default=True
    )

    id = IntProperty(
        name="Material ID",
        description="Material unique ID inside blend file, this way materials can be easily identified for looks",
        get=get_id
    )

    mat_effect_name = StringProperty(
        name="Shader Effect Name",
        description="SCS shader effect name",
        default="",
        subtype='NONE',
        update=__update_look__
    )

    # SHADER ATTRIBUTES
    shader_attribute_add_ambient = FloatProperty(
        name="Add Ambient",
        description="SCS shader 'Add Ambient' value",
        default=0.0,
        min=-10.0,
        max=10.0,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_shader_attribute_add_ambient,
    )

    shader_attribute_aux0 = CollectionProperty(
        name="Aux [0]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [0]' value",
        options={'HIDDEN'},
    )

    shader_attribute_aux1 = CollectionProperty(
        name="Aux [1]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [1]' value",
        options={'HIDDEN'},
    )

    shader_attribute_aux2 = CollectionProperty(
        name="Aux [2]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [2]' value",
        options={'HIDDEN'},
    )

    shader_attribute_aux3 = CollectionProperty(
        name="Aux [3]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [3]' value",
        options={'HIDDEN'},
    )

    shader_attribute_aux4 = CollectionProperty(
        name="Aux [4]",
        type=AuxiliaryItem,
        description="SCS shader 'Aux [4]' value",
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
        update=update_shader_attribute_diffuse,
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
        update=update_shader_attribute_env_factor,
    )

    shader_attribute_fresnel = FloatVectorProperty(
        name="Fresnel",
        description="SCS shader 'Fresnel' value",
        default=(0.2, 0.9),
        min=-3, max=3,
        soft_min=0, soft_max=1,
        step=3, precision=2,
        options={'HIDDEN'},
        subtype='NONE',
        size=2,
        update=update_shader_attribute_fresnel,
    )

    shader_attribute_reflection = FloatProperty(
        name="Reflection",
        description="SCS shader 'Reflection' value",
        default=0.0,
        min=0.0,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=__update_look__,
    )

    shader_attribute_reflection2 = FloatProperty(
        name="Reflection 2",
        description="SCS shader 'Reflection 2' value",
        default=0.0,
        min=0.0,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=__update_look__,
    )

    shader_attribute_shadow_bias = FloatProperty(
        name="Shadow Bias",
        description="SCS shader 'Shadow Bias' value",
        default=0.0,
        min=0.0,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=__update_look__,
    )

    shader_attribute_shininess = FloatProperty(
        name="Shininess",
        description="SCS shader 'Shininess' value",
        default=0.0,
        min=0.0,
        step=100,
        precision=2,
        options={'HIDDEN'},
        update=update_shader_attribute_shininess,
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
        update=update_shader_attribute_specular,
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
        update=update_shader_attribute_tint
    )

    shader_attribute_tint_opacity = FloatProperty(
        name="Tint Opacity",
        description="SCS shader 'Tint Opacity' value",
        default=0.0,
        step=1,
        precision=2,
        options={'HIDDEN'},
        update=update_shader_attribute_tint_opacity
    )

    shader_attribute_queue_bias = IntProperty(
        name="Queue Bias",
        description="SCS shader 'Queue Bias' value",
        default=2,
        options={'HIDDEN'},
        update=__update_look__
    )

    # TEXTURE: BASE
    shader_texture_base = StringProperty(
        name="Texture Base",
        description="Texture Base for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_base,
    )
    shader_texture_base_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_base_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_base_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_base_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_base_settings
    )
    shader_texture_base_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_base_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_base_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: BASE_1
    shader_texture_base_1 = StringProperty(
        name="Texture Base 1",
        description="Texture Base for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_base_1,
    )
    shader_texture_base_1_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_base_1_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_base_1_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_base_1_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_base_1_settings
    )
    shader_texture_base_1_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_base_1_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_base_1_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: DETAIL
    shader_texture_detail = StringProperty(
        name="Texture Detail",
        description="Texture Flakenoise for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_detail,
    )
    shader_texture_detail_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_detail_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_detail_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_detail_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_detail_settings
    )
    shader_texture_detail_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_detail_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_detail_uv = CollectionProperty(
        name="Texture Detail UV Sets",
        description="Texture Detail UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: FLAKENOISE
    shader_texture_flakenoise = StringProperty(
        name="Texture Flakenoise",
        description="Texture Flakenoise for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_flakenoise,
    )
    shader_texture_flakenoise_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_flakenoise_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_flakenoise_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_flakenoise_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_flakenoise_settings
    )
    shader_texture_flakenoise_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_flakenoise_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_flakenoise_uv = CollectionProperty(
        name="Texture Flakenoise UV Sets",
        description="Texture Flakenoise UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: IAMOD
    shader_texture_iamod = StringProperty(
        name="Texture Iamod",
        description="Texture Iamod for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_iamod,
    )
    shader_texture_iamod_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_iamod_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_iamod_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_iamod_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_iamod_settings
    )
    shader_texture_iamod_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_iamod_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_iamod_uv = CollectionProperty(
        name="Texture Iamod UV Sets",
        description="Texture Iamod UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: LAYER0
    shader_texture_layer0 = StringProperty(
        name="Texture Layer0",
        description="Texture Layer0 for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_layer0,
    )
    shader_texture_layer0_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_layer0_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_layer0_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_layer0_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_layer0_settings
    )
    shader_texture_layer0_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_layer0_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_layer0_uv = CollectionProperty(
        name="Texture Layer0 UV Sets",
        description="Texture Layer0 UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: LAYER1
    shader_texture_layer1 = StringProperty(
        name="Texture Layer1",
        description="Texture Layer1 for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_layer1,
    )
    shader_texture_layer1_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_layer1_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_layer1_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_layer1_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_layer1_settings
    )
    shader_texture_layer1_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_layer1_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_layer1_uv = CollectionProperty(
        name="Texture Layer1 UV Sets",
        description="Texture Layer1 UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: LIGHTMAP
    shader_texture_lightmap = StringProperty(
        name="Texture Lightmap",
        description="Texture Lightmap for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_lightmap,
    )
    shader_texture_lightmap_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_lightmap_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_lightmap_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_lightmap_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_lightmap_settings
    )
    shader_texture_lightmap_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_lightmap_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_lightmap_uv = CollectionProperty(
        name="Texture Lightmap UV Sets",
        description="Texture Lightmap UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: MASK
    shader_texture_mask = StringProperty(
        name="Texture Mask",
        description="Texture Mask for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_mask,
    )
    shader_texture_mask_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_mask_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_mask_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_mask_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_mask_settings
    )
    shader_texture_mask_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_mask_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_mask_uv = CollectionProperty(
        name="Texture Mask UV Sets",
        description="Texture Mask UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: MULT
    shader_texture_mult = StringProperty(
        name="Texture Mult",
        description="Texture Mult for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_mult,
    )
    shader_texture_mult_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_mult_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_mult_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_mult_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_mult_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_mult_settings
    )
    shader_texture_mult_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_mult_uv = CollectionProperty(
        name="Texture Mult UV Sets",
        description="Texture Mult UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: MULT_1
    shader_texture_mult_1 = StringProperty(
        name="Texture Mult 1",
        description="Texture Mult for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_mult_1,
    )
    shader_texture_mult_1_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_mult_1_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_mult_1_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_mult_1_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_mult_1_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_mult_1_settings
    )
    shader_texture_mult_1_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_mult_1_uv = CollectionProperty(
        name="Texture Mult UV Sets",
        description="Texture Mult UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: NMAP
    shader_texture_nmap = StringProperty(
        name="Texture NMap",
        description="Texture NMap for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_nmap,
    )
    shader_texture_nmap_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_nmap_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_nmap_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_nmap_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_nmap_settings
    )
    shader_texture_nmap_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_nmap_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_nmap_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: NMAP_DETAIL
    shader_texture_nmap_detail = StringProperty(
        name="Texture NMap Detail",
        description="Texture NMap Detail for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_nmap_detail,
    )
    shader_texture_nmap_detail_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_nmap_detail_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_nmap_detail_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_nmap_detail_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_nmap_detail_settings
    )
    shader_texture_nmap_detail_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_nmap_detail_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_nmap_detail_uv = CollectionProperty(
        name="Texture Base UV Sets",
        description="Texture base UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: OCCLUSION
    shader_texture_oclu = StringProperty(
        name="Texture Oclu",
        description="Texture Oclu for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_oclu,
    )
    shader_texture_oclu_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_oclu_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_oclu_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_oclu_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_oclu_settings
    )
    shader_texture_oclu_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_oclu_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_oclu_uv = CollectionProperty(
        name="Texture Oclu UV Sets",
        description="Texture Oclu UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: OVER
    shader_texture_over = StringProperty(
        name="Texture Over",
        description="Texture Over for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_over,
    )
    shader_texture_over_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_over_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_over_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_over_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_over_settings
    )
    shader_texture_over_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_over_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_over_uv = CollectionProperty(
        name="Texture Over UV Sets",
        description="Texture Over UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: PAINTJOB
    shader_texture_paintjob = StringProperty(
        name="Texture Paintjob",
        description="Texture Paintjob for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_paintjob,
    )
    shader_texture_paintjob_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_paintjob_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_paintjob_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_paintjob_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_paintjob_settings
    )
    shader_texture_paintjob_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_paintjob_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_paintjob_uv = CollectionProperty(
        name="Texture Paintjob UV Sets",
        description="Texture Paintjob UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # TEXTURE: REFLECTION
    shader_texture_reflection = StringProperty(
        name="Texture Reflection",
        description="Texture Reflection for active Material",
        default=_MAT_consts.unset_bitmap_filepath,
        options={'HIDDEN'},
        subtype='NONE',
        update=update_shader_texture_reflection,
    )
    shader_texture_reflection_imported_tobj = StringProperty(
        name="Imported TOBJ Path",
        description="Use imported TOBJ path reference which will be exported into material (NOTE: export will not take care of any TOBJ files!)",
        default="",
        update=__update_look__
    )
    shader_texture_reflection_locked = BoolProperty(
        name="Texture Locked",
        description="Tells if texture is locked and should not be changed by user(intended for internal usage only)",
        default=False
    )
    shader_texture_reflection_map_type = StringProperty(
        name="Texture Map Type",
        description="Stores texture mapping type and should not be changed by user(intended for internal usage only)",
        default="2d"
    )
    shader_texture_reflection_settings = EnumProperty(
        name="Settings",
        description="TOBJ settings for this texture",
        items=__get_texture_settings__(),
        default=set(),
        options={'ENUM_FLAG'},
        update=update_shader_texture_reflection_settings
    )
    shader_texture_reflection_tobj_load_time = StringProperty(
        name="Last TOBJ load time",
        description="Time string of last loading",
        default="",
    )
    shader_texture_reflection_use_imported = BoolProperty(
        name="Use Imported",
        description="Use custom provided path for TOBJ reference",
        default=False,
        update=__update_look__
    )
    shader_texture_reflection_uv = CollectionProperty(
        name="Texture Reflection UV Sets",
        description="Texture Reflection UV sets for active Material",
        type=UVMappingItem,
        options={'HIDDEN'},
    )

    # # Following String property is fed from MATERIAL SUBSTANCE data list, which is usually loaded from
    # # "//base/material/material.db" file and stored at "scs_globals.scs_matsubs_inventory".
    substance = StringProperty(
        name="Substance",
        description="Substance",
        default=_MAT_consts.unset_substance,
        subtype='NONE',
        update=__update_look__
    )
