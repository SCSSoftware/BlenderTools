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

# Copyright (C) 2017: SCS Software

import bpy
import os
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.exp.pit import default_material
from io_scs_tools.exp.pit import get_texture_path_from_material
from io_scs_tools.exp.pit import fill_material_sections
from io_scs_tools.exp.pit import fill_part_list
from io_scs_tools.exp.pit import fill_header_section
from io_scs_tools.exp.pit import fill_look_sections
from io_scs_tools.exp.pit import fill_variant_sections
from io_scs_tools.exp.pit import fill_comment_header_section
from io_scs_tools.exp.pit import fill_global_section
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def _get_flavor_types(preset, flavors_str):
    """Get enabled flavor types from given preset and flavor string.

    :param preset: ui shader preset item
    :type preset: io_scs_tools.internals.shader_presets.ui_shader_preset_item.UIShaderPresetItem
    :param flavors_str:
    :type flavors_str: str
    :return: tuple of found flavors from flavor string; otherwise empty tuple is returned
    :rtype: tuple
    """

    enabled_flavors = []
    for flavor in preset.flavors:
        for flavor_variant in flavor.variants:

            is_in_middle = "." + flavor_variant.suffix + "." in flavors_str
            is_on_end = flavors_str.endswith("." + flavor_variant.suffix)

            if is_in_middle or is_on_end:

                enabled_flavors.append(flavor_variant.type)

    return tuple(enabled_flavors)


def export(root_object, filepath, name_suffix, used_parts, used_materials):
    """Export PIT EF.

    :param root_object: SCS root object
    :type root_object: bpy.types.Object
    :param filepath: PIT file path
    :type filepath: str
    :param name_suffix: file name suffix
    :type name_suffix: str
    :param used_parts: parts transitional structure for accessing stored parts from PIM, PIC and PIP
    :type used_parts: io_scs_tools.exp.transition_structs.parts.PartsTrans
    :param used_materials: materials transitional structure for accessing stored materials from PIM
    :type used_materials: io_scs_tools.exp.transition_structs.materials.MaterialsTrans
    :return: True if successful; False otherwise;
    :rtype: bool
    """

    scs_globals = _get_scs_globals()

    file_name = root_object.name

    print("\n************************************")
    print("**      SCS PIT.EF Exporter       **")
    print("**      (c)2017 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    look_list = []
    variant_list = []

    saved_active_look = root_object.scs_props.active_scs_look
    looks_inventory = root_object.scs_object_look_inventory
    looks_count = len(looks_inventory)
    if looks_count <= 0:
        looks_count = 1

    used_materials_pairs = used_materials.get_as_pairs()
    for i in range(0, looks_count):

        # apply each look from inventory first
        if len(looks_inventory) > 0:
            root_object.scs_props.active_scs_look = i

            # actually write values to material because Blender might not refresh data yet
            _looks.apply_active_look(root_object)

            curr_look_name = looks_inventory[i].name
        else:  # if no looks create default
            curr_look_name = "default"

        material_dict = {}
        material_list = []
        # get materials data
        for material_name, material in used_materials_pairs:
            if material is None:
                material_name = str("_default_material_-_default_settings_")

                # DEFAULT MATERIAL
                material_export_data = default_material(material_name)
                material_list.append(material_name)

            else:
                # print('material name: %r' % material.name)
                material_list.append(material)

                # MATERIAL EFFECT
                effect_name = material.scs_props.mat_effect_name

                # PRESET SHADERS
                flags = 0
                attribute_cnt = texture_cnt = 0
                attribute_sections = []
                texture_sections = []
                active_shader_preset_name = material.scs_props.active_shader_preset_name

                # SUBSTANCE
                substance_value = material.scs_props.substance
                # only write substance to material if it's assigned
                if substance_value != "None" and substance_value != "":

                    substance_data = _SectionData("Attribute")
                    substance_data.props.append(("Format", "STRING"))
                    substance_data.props.append(("Tag", "substance"))
                    substance_data.props.append(("Value", ["i", (substance_value,)]))
                    attribute_sections.append(substance_data)
                    attribute_cnt += 1

                if _shader_presets.has_preset(active_shader_preset_name) and active_shader_preset_name != "<none>":

                    preset = _shader_presets.get_preset(active_shader_preset_name)
                    flavors_str = effect_name[len(preset.effect):]
                    flavors_types = _get_flavor_types(preset, flavors_str)
                    section = _shader_presets.get_section(active_shader_preset_name, flavors_str)

                    # FLAGS
                    for prop in section.props:

                        if prop[0] == "Flags":
                            flags = int(not material.scs_props.enable_aliasing)
                            break

                    # COLLECT ATTRIBUTES AND TEXTURES
                    for item in section.sections:

                        # if attribute is hidden in shader preset ignore it on export
                        # this is useful for flavor hiding some attributes from original material
                        # eg: airbrush on "truckpaint" hides R G B aux attributes which are not present
                        # when using airbrush flavor
                        hidden = item.get_prop_value("Hide")
                        if hidden and hidden == "True":
                            continue

                        preview_only = item.get_prop_value("PreviewOnly")
                        if preview_only and preview_only == "True":
                            continue

                        # ATTRIBUTES
                        if item.type == "Attribute":
                            # print('     Attribute:')

                            attribute_data = _SectionData("Attribute")
                            for rec in item.props:
                                # print('       rec: %r' % str(rec))
                                if rec[0] == "Format":
                                    attribute_data.props.append((rec[0], rec[1]))
                                elif rec[0] == "Tag":
                                    # tag_prop = rec[1].replace("[", "").replace("]", "")
                                    # attribute_data.props.append((rec[0], tag_prop))
                                    attribute_data.props.append((rec[0], rec[1]))
                                elif rec[0] == "Value":
                                    format_prop = item.get_prop("Format")[1]
                                    tag_prop = item.get_prop("Tag")[1]
                                    tag_prop = tag_prop.replace("[", "").replace("]", "")
                                    # print('         format_prop: %r' % str(format_prop))
                                    # print('         tag_prop: %r' % str(tag_prop))
                                    if "aux" in tag_prop:
                                        aux_props = getattr(material.scs_props, "shader_attribute_" + tag_prop)
                                        value = []
                                        for aux_prop in aux_props:
                                            value.append(aux_prop.value)

                                        # extract list if there is only one value inside and tagged as FLOAT
                                        # otherwise it gets saved as: "Value: ( [0.0] )" instead of: "Value: ( 0.0 )"
                                        if len(value) == 1 and format_prop == "FLOAT":
                                            value = value[0]

                                    else:
                                        value = getattr(material.scs_props, "shader_attribute_" + tag_prop, "NO TAG")
                                    # print('         value: %s' % str(value))
                                    if format_prop == 'FLOAT':
                                        attribute_data.props.append((rec[0], ["&&", (value,)]))
                                    else:
                                        attribute_data.props.append((rec[0], ["i", tuple(value)]))
                            attribute_sections.append(attribute_data)
                            attribute_cnt += 1

                        # TEXTURES
                        elif item.type == "Texture":
                            # print('     Texture:')

                            texture_data = _SectionData("Texture")
                            for rec in item.props:
                                # print('       rec: %r' % str(rec))
                                if rec[0] == "Tag":
                                    tag_prop = rec[1].split(":")[1]
                                    tag = str("texture[" + str(texture_cnt) + "]:" + tag_prop)
                                    texture_data.props.append((rec[0], tag))
                                elif rec[0] == "Value":
                                    tag_prop = item.get_prop("Tag")[1].split(":")[1]
                                    # print('         tag_prop: %r' % str(tag_prop))

                                    # create and get path to tobj
                                    tobj_rel_path = get_texture_path_from_material(material, tag_prop,
                                                                                   os.path.dirname(filepath))

                                    texture_data.props.append((rec[0], tobj_rel_path))

                            texture_sections.append(texture_data)
                            texture_cnt += 1

                    material_export_data = _SectionData("Material")
                    material_export_data.props.append(("Alias", material.name))
                    material_export_data.props.append(("Effect", effect_name))

                    # add additional info about base effect and enabled flavor types
                    material_export_data.props.append(("BaseEffect", preset.effect))
                    if len(flavors_types) > 0:
                        material_export_data.props.append(("Flavors", ["ii", flavors_types]))

                    material_export_data.props.append(("Flags", flags))
                    material_export_data.props.append(("AttributeCount", attribute_cnt))
                    material_export_data.props.append(("TextureCount", texture_cnt))
                    for attribute in attribute_sections:
                        material_export_data.sections.append(attribute)
                    for texture in texture_sections:
                        material_export_data.sections.append(texture)

                elif active_shader_preset_name == "<imported>":

                    material_attributes = material['scs_shader_attributes']['attributes'].to_dict().values()
                    material_textures = material['scs_shader_attributes']['textures'].to_dict().values()

                    material_export_data = _SectionData("Material")
                    material_export_data.props.append(("Alias", material.name))
                    material_export_data.props.append(("Effect", effect_name))
                    material_export_data.props.append(("Flags", int(not material.scs_props.enable_aliasing)))
                    material_export_data.props.append(("AttributeCount", len(material_attributes)))
                    material_export_data.props.append(("TextureCount", len(material_textures)))

                    for attribute_dict in material_attributes:
                        attribute_section = _SectionData("Attribute")

                        format_value = ""
                        for attr_prop in sorted(attribute_dict.keys()):

                            # get the format of current attribute (we assume that "Format" attribute is before "Value" attribute in this for loop)
                            if attr_prop == "Format":
                                format_value = attribute_dict[attr_prop]

                            if attr_prop == "Value" and ("FLOAT" in format_value or "STRING" in format_value):

                                tag_prop = attribute_dict["Tag"].replace("[", "").replace("]", "")
                                if "aux" in tag_prop:
                                    aux_props = getattr(material.scs_props, "shader_attribute_" + tag_prop)
                                    value = []
                                    for aux_prop in aux_props:
                                        value.append(aux_prop.value)
                                else:
                                    value = getattr(material.scs_props, "shader_attribute_" + tag_prop, None)
                                    if isinstance(value, float):
                                        value = [value]

                                if value is None:
                                    attribute_section.props.append((attr_prop, ["i", tuple(attribute_dict[attr_prop])]))
                                else:
                                    attribute_section.props.append((attr_prop, ["i", tuple(value)]))

                            elif attr_prop == "Tag" and "aux" in attribute_dict[attr_prop]:
                                attribute_section.props.append((attr_prop, "aux[" + attribute_dict[attr_prop][3:] + "]"))
                            else:
                                attribute_section.props.append((attr_prop, attribute_dict[attr_prop]))

                        material_export_data.sections.append(attribute_section)

                    for texture_dict in material_textures:
                        texture_section = _SectionData("Texture")

                        tag_id_string = ""
                        for tex_prop in sorted(texture_dict.keys()):

                            if tex_prop == "Tag":
                                tag_id_string = texture_dict[tex_prop].split(':')[1]

                            if tex_prop == "Value" and tag_id_string != "":

                                tobj_rel_path = get_texture_path_from_material(material, tag_id_string, os.path.dirname(filepath))
                                texture_section.props.append((tex_prop, tobj_rel_path))

                            else:
                                texture_section.props.append((tex_prop, texture_dict[tex_prop]))

                        material_export_data.sections.append(texture_section)

                else:  # when user made material presets were there, but there is no preset library at export for some reason

                    lprint("W Shader preset used on %r not found in Shader Presets Library (Did you set correct path?), "
                           "exporting default material instead!",
                           (material_name,))

                    material_name = str("_" + material_name + "_-_default_settings_")
                    material_export_data = default_material(material_name)

            material_dict[material_name] = material_export_data

        # create materials sections for looks
        material_sections = fill_material_sections(material_list, material_dict)
        look_data = {
            "name": curr_look_name,
            "material_sections": material_sections
        }
        look_list.append(look_data)

    # restore look applied before export
    root_object.scs_props.active_scs_look = saved_active_look

    # PARTS AND VARIANTS...
    used_parts_names = used_parts.get_as_list()
    if len(root_object.scs_object_variant_inventory) == 0:
        # If there is no Variant, add the Default one...
        part_list = fill_part_list(root_object.scs_object_part_inventory, used_parts_names, all_parts=True)
        variant_list.append((_VARIANT_consts.default_name, part_list), )
    else:
        for variant in root_object.scs_object_variant_inventory:
            part_list = fill_part_list(variant.parts, used_parts_names)
            variant_list.append((variant.name, part_list), )

    # DATA CREATION
    header_section = fill_header_section(1, file_name, scs_globals.export_write_signature)
    look_section = fill_look_sections(look_list)
    # part_sections = fill_part_section(part_list)
    variant_section = fill_variant_sections(variant_list)
    comment_header_section = fill_comment_header_section(look_list, variant_list)
    global_section = fill_global_section(len(look_list), len(variant_list), used_parts.count(), len(used_materials_pairs))

    # DATA ASSEMBLING
    pit_container = [comment_header_section, header_section, global_section]
    for section in look_section:
        pit_container.append(section)
    for section in variant_section:
        pit_container.append(section)

    # FILE EXPORT
    ind = "    "
    pit_filepath = str(filepath + ".pit" + name_suffix)
    result = _pix_container.write_data_to_file(pit_container, pit_filepath, ind)

    # print("************************************")
    return result
