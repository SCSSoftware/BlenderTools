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
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.exp import tobj as _tobj
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_tools_version as _get_tools_version
from io_scs_tools.utils.info import get_blender_version as _get_blender_version
from io_scs_tools.utils.printout import lprint


def _fill_comment_header_section(look_list, variant_list):
    """Fills up comment section (before Header)."""
    section = _SectionData("#comment")
    section.props.append(("#", "# Look Names:"))
    for look in look_list:
        section.props.append(("#", "#\t" + look['name']))
    section.props.append(("#", "#"))
    section.props.append(("#", "# Variant Names:"))
    for variant in variant_list:
        section.props.append(("#", "#\t" + variant[0]))
    section.props.append(("#", "#"))
    return section


def _fill_header_section(file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 1))
    blender_version, blender_build = _get_blender_version()
    section.props.append(("Source", "Blender " + blender_version + blender_build + ", SCS Blender Tools: " + str(_get_tools_version())))
    section.props.append(("Type", "Trait"))
    section.props.append(("Name", file_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(looks, variants, parts, materials):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("LookCount", looks))
    section.props.append(("VariantCount", variants))
    section.props.append(("PartCount", parts))
    section.props.append(("MaterialCount", materials))
    return section


def _fill_material_sections(materials, material_dict):
    """Fills up "Material" sections."""
    sections = []
    for material in materials:
        if isinstance(material, str):
            sections.append(material_dict[material])
        else:
            if material.name in material_dict:
                material_section = material_dict[material.name]
            else:
                material_section = material_dict[str("_" + material.name + "_-_default_settings_")]
            sections.append(material_section)
    return sections


def _default_material(alias):
    """Return 'default material' data section."""

    # DEFAULT PROPERTIES
    material_export_data = _SectionData("Material")
    material_export_data.props.append(("Alias", alias))
    # material_export_data.props.append(("Effect", "eut2.none"))
    material_export_data.props.append(("Effect", "eut2.dif"))
    material_export_data.props.append(("Flags", 0))
    attribute_data = [
        ('FLOAT3', "diffuse", (1.0, 1.0, 1.0)),
        ('FLOAT3', "specular", (0.0, 0.0, 0.0)),
        ('FLOAT', "shininess", (5.0, )),
        ('FLOAT', "add_ambient", (0.0, )),
        ('FLOAT', "reflection", (0.0, )),
    ]
    texture_data = [
        ('texture[0]:texture_base', ""),
    ]
    material_export_data.props.append(("AttributeCount", len(attribute_data)))
    material_export_data.props.append(("TextureCount", len(texture_data)))

    # DEFAULT ATTRIBUTES AND TEXTURE
    for attribute in attribute_data:
        attribute_section = _SectionData("Attribute")
        attribute_section.props.append(("Format", attribute[0]))
        attribute_section.props.append(("Tag", attribute[1]))
        attribute_section.props.append(("Value", ["i", attribute[2]]))
        material_export_data.sections.append(attribute_section)
    for texture in texture_data:
        texture_section = _SectionData("Texture")
        texture_section.props.append(("Tag", texture[0]))
        texture_section.props.append(("Value", texture[1]))
        material_export_data.sections.append(texture_section)
    return material_export_data


def _get_texture_path_from_material(material, texture_type):
    """Get's relative path for Texture section of tobj from given texture_type.
    If tobj is not yet created it also creates tobj for it.

    :param material: Blender material
    :type material: bpy.types.Material
    :param texture_type: type of texture which should be readed from material (example "texture_base")
    :type texture_type: str
    :return: relative path for Texture section data of PIT material
    :rtype: str
    """

    # overwrite tobj value directly if specified
    if getattr(material.scs_props, "shader_" + texture_type + "_use_imported", False):
        return getattr(material.scs_props, "shader_" + texture_type + "_imported_tobj", "")

    # use tobj value from shader preset if texture is locked and has default value
    if "scs_shader_attributes" in material and "textures" in material["scs_shader_attributes"]:
        for tex_entry in material["scs_shader_attributes"]["textures"].values():
            if "Tag" in tex_entry and texture_type in tex_entry["Tag"]:
                if "Lock" in tex_entry and tex_entry["Lock"] == "True":
                    if "Value" in tex_entry and tex_entry["Value"] != "":
                        return tex_entry["Value"]

    # TEXTURE PATH
    texture_path = getattr(material.scs_props, "shader_" + texture_type, "NO PATH")
    texture_abs_filepath = _path_utils.get_abs_path(texture_path)

    # TOBJ PATH
    tobj_rel_filepath = os.path.splitext(texture_path)[0][1:]
    tobj_abs_filepath = str(os.path.splitext(texture_abs_filepath)[0] + ".tobj")

    # CREATE TOBJ FILE
    if not os.path.isfile(tobj_abs_filepath) or getattr(material.scs_props, "shader_" + texture_type + "_export_tobj", False):

        # export tobj only if file of texture exists
        if os.path.isfile(texture_abs_filepath):
            settings = getattr(material.scs_props, "shader_" + texture_type + "_settings", set())
            _tobj.export(tobj_abs_filepath, os.path.split(texture_path)[1], settings)
        else:
            lprint("W Texture file '%s' specified in material '%s' doesn't exists, TOBJ can not be exported!", (texture_path, material.name))

    # make sure that Windows users will export proper paths
    tobj_rel_filepath = tobj_rel_filepath.replace("\\", "/")

    return tobj_rel_filepath


def _fill_look_sections(data_list, material_sections):
    """Fills up "Look" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("Look")
        section.props.append(("Name", item['name']))
        for material_section in material_sections:
            section.sections.append(material_section)
        sections.append(section)
    return sections


def _fill_atr_section(atr):
    """Creates "Attribute" section."""
    section = _SectionData("Attribute")
    section.props.append(("Format", atr[0]))
    section.props.append(("Tag", atr[1]))
    section.props.append(("Value", ["&&", (atr[2], )]))
    return section


def _fill_part_section(part):
    """Creates "Part" section."""
    section = _SectionData("Part")
    section.props.append(("Name", part[0]))
    section.props.append(("AttributeCount", len(part[1])))
    for atr in part[1]:
        atr_section = _fill_atr_section(atr)
        section.sections.append(atr_section)
    return section


def _fill_variant_sections(data_list):
    """Fills up "Variant" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("Variant")
        section.props.append(("Name", item[0]))
        for part in item[1]:
            part_section = _fill_part_section(part)
            section.sections.append(part_section)
        sections.append(section)
    return sections


def _fill_part_list(parts, used_parts, all_parts=False):
    """Fills up "Part" sections in "Varian" section

    :param parts: SCS Root part inventory or parts collection property from variant inventory
    :type parts: ObjectPartInventory | list of ObjectVariantPartInclusion
    :param used_parts: dictionary of part names that are actually used in game object (if some part is not yet in it will be added)
    :type used_parts: dict
    :param all_parts: flag for all parts are visible (handy for creating default visibilities)
    :type all_parts: bool
    :return: Part records (name, attributes)
    :rtype: list
    """
    part_list = []
    for part_name in used_parts:
        for part in parts:

            if part.name == part_name:

                part_atr = []
                if all_parts:
                    part_atr.append(('INT', 'visible', 1))
                else:
                    if part.include:
                        include = 1
                    else:
                        include = 0
                    part_atr.append(('INT', 'visible', include))

                part_list.append((part.name, part_atr), )

    return part_list


def _get_properties(section):
    """Returns all the properties from given section.

    :param section: PIX section data
    :type section: SectionData
    :return: properties of the section
    :rtype: dict
    """
    properties = {}
    for prop in section.props:
        properties[prop[0]] = prop[1]
    return properties


def export(root_object, used_parts, used_materials, scene, filepath):
    scs_globals = _get_scs_globals()
    output_type = scs_globals.output_type

    file_name = root_object.name

    print("\n************************************")
    print("**      SCS PIT Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA GATHERING
    look_list = []
    variant_list = []
    material_list = []
    material_dict = {}

    # MATERIALS AND LOOKS...
    for material in used_materials:
        if material is not None:
            # if material in ("_empty_slot_", "_empty_material_"):
            # NOTE: only workaround until module doesn't gets rewritten
            if material in bpy.data.materials:
                material = bpy.data.materials[material]

            if isinstance(material, str):
                material_name = str(material + "-_default_settings_")

                # DEFAULT MATERIAL
                material_export_data = _default_material(material_name)
                material_list.append(material_name)

            else:
                # print('material name: %r' % material.name)
                material_name = material.name
                material_list.append(material)

                # SUBSTANCE
                if material.scs_props.substance != 'None':
                    print('material.name: %r\tmat.scs_props.substance: "%s"' % (material.name, str(material.scs_props.substance)))
                    # TODO: Substance Export...

                # MATERIAL EFFECT
                # shader_data = material.get("scs_shader_attributes", {})
                # effect_name = shader_data.get('effect', "NO EFFECT")
                effect_name = material.scs_props.mat_effect_name

                # CgFX SHADERS
                # print("\n=== GET SHADER EXPORT DATA =======================") ## NOTE: The following code is OBSOLETE!!!
                # cgfx_export_data = None
                # print("  cgfx_export_data:\n%s" % str(cgfx_export_data))
                # if cgfx_export_data:
                # print("\nAttributes:")
                # for attribute in cgfx_export_data['attributes']:
                # if cgfx_export_data['attributes'][attribute]:
                # print("  %s:" % str(attribute))
                # for rec in cgfx_export_data['attributes'][attribute]:
                # print("    %s: %s" % (str(rec), str(cgfx_export_data['attributes'][attribute][rec])))
                # else:
                # print("%s:\n  %s" % (str(attribute), cgfx_export_data['attributes'][attribute]))
                # print("\nTextures:")
                # for attribute in cgfx_export_data['textures']:
                # if cgfx_export_data['textures'][attribute]:
                # print("  %s:" % str(attribute))
                # for rec in cgfx_export_data['textures'][attribute]:
                # print("    %s: %s" % (str(rec), str(cgfx_export_data['textures'][attribute][rec])))
                # else:
                # print("%s:\n  %s" % (str(attribute), cgfx_export_data['textures'][attribute]))
                # else:
                # Print(1, 'E No CgFX data for material %r!' % material.name)
                # print("==================================================")

                # PRESET SHADERS
                preset_found = False
                alias = "NO SHADER"
                def_cnt = attribute_cnt = texture_cnt = 0
                def_sections = []
                attribute_sections = []
                texture_sections = []
                active_shader_preset_name = material.scs_props.active_shader_preset_name
                # print(' active_shader_preset_name: %r' % active_shader_preset_name)
                for preset_i, preset in enumerate(scene.scs_shader_presets_inventory):
                    # print(' preset[%i]: %r' % (preset_i, preset.name))
                    if preset.name == active_shader_preset_name:
                        # print('   - material %r - %r' % (material.name, preset.name))

                        # LOAD PRESET
                        shader_presets_abs_path = _path_utils.get_abs_path(scs_globals.shader_presets_filepath)
                        # shader_presets_filepath = _get_scs_globals().shader_presets_filepath
                        # print('shader_presets_filepath: %r' % shader_presets_filepath)
                        # if shader_presets_filepath.startswith(str(os.sep + os.sep)): ## RELATIVE PATH
                        # shader_presets_abs_path = get_abs_path(shader_presets_filepath)
                        # else:
                        # shader_presets_abs_path = shader_presets_filepath

                        if os.path.isfile(shader_presets_abs_path):
                            presets_container = _pix_container.get_data_from_file(shader_presets_abs_path, '    ')

                            # FIND THE PRESET IN FILE
                            if presets_container:
                                for section in presets_container:
                                    if section.type == "Shader":
                                        section_properties = _get_properties(section)
                                        if 'PresetName' in section_properties:
                                            preset_name = section_properties['PresetName']
                                            if preset_name == active_shader_preset_name:
                                                alias = material.name
                                                # print('   + preset name: %r' % preset_name)

                                                # COLLECT ATTRIBUTES AND TEXTURES
                                                for item in section.sections:

                                                    # DATA EXCHANGE FORMAT ATRIBUTE
                                                    if item.type == "DataExchangeFormat":
                                                        def_data = _SectionData("DataExchangeFormat")
                                                        for rec in item.props:
                                                            def_data.props.append((rec[0], rec[1]))
                                                        def_sections.append(def_data)
                                                        def_cnt += 1

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
                                                                else:
                                                                    value = material.scs_props.get(str("shader_attribute_" + tag_prop), "NO TAG")
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
                                                                tobj_rel_path = _get_texture_path_from_material(material, tag_prop)

                                                                texture_data.props.append((rec[0], tobj_rel_path))

                                                        texture_sections.append(texture_data)
                                                        texture_cnt += 1

                                                preset_found = True
                                                break

                        else:
                            lprint('\nW The file path "%s" is not valid!', (shader_presets_abs_path,))
                    if preset_found:
                        break

                if preset_found:

                    material_export_data = _SectionData("Material")
                    material_export_data.props.append(("Alias", alias))
                    material_export_data.props.append(("Effect", effect_name))
                    material_export_data.props.append(("Flags", 0))
                    if output_type.startswith('def'):
                        material_export_data.props.append(("DataExchangeFormatCount", def_cnt))
                    material_export_data.props.append(("AttributeCount", attribute_cnt))
                    material_export_data.props.append(("TextureCount", texture_cnt))
                    if output_type.startswith('def'):
                        for def_section in def_sections:
                            material_export_data.sections.append(def_section)
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
                    material_export_data.props.append(("Flags", 0))
                    material_export_data.props.append(("AttributeCount", len(material_attributes)))
                    material_export_data.props.append(("TextureCount", len(material_textures)))

                    for attribute_dict in material_attributes:
                        attribute_section = _SectionData("Attribute")

                        format_value = ""
                        for attr_prop in sorted(attribute_dict.keys()):

                            # get the format of current attribute (we assume that "Format" attribute is before "Value" attribute in this for loop)
                            if attr_prop == "Format":
                                format_value = attribute_dict[attr_prop]

                            if attr_prop == "Value" and "FLOAT" in format_value:
                                attribute_section.props.append((attr_prop, ["i", tuple(attribute_dict[attr_prop])]))
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

                                tobj_rel_path = _get_texture_path_from_material(material, tag_id_string)
                                texture_section.props.append((tex_prop, tobj_rel_path))

                            else:
                                texture_section.props.append((tex_prop, texture_dict[tex_prop]))

                        material_export_data.sections.append(texture_section)

                else:
                    # DEFAULT MATERIAL
                    material_name = str("_" + material_name + "_-_default_settings_")
                    material_export_data = _default_material(material_name)

            material_dict[material_name] = material_export_data

    # PARTS AND VARIANTS...
    part_list_cnt = len(used_parts.keys())
    if len(root_object.scs_object_variant_inventory) == 0:
        # If there is no Variant, add the Default one...
        part_list = _fill_part_list(root_object.scs_object_part_inventory, used_parts, all_parts=True)
        variant_list.append((_VARIANT_consts.default_name, part_list), )
    else:
        for variant in root_object.scs_object_variant_inventory:
            part_list = _fill_part_list(variant.parts, used_parts)
            variant_list.append((variant.name, part_list), )

    # DATA CREATION
    header_section = _fill_header_section(file_name, scs_globals.sign_export)
    material_sections = _fill_material_sections(material_list, material_dict)
    if len(look_list) == 0:
        look_data = {'name': "Default"}
        look_list.append(look_data)
    look_section = _fill_look_sections(look_list, material_sections)
    # part_sections = fill_part_section(part_list)
    variant_section = _fill_variant_sections(variant_list)
    comment_header_section = _fill_comment_header_section(look_list, variant_list)
    global_section = _fill_global_section(len(look_list), len(variant_list), part_list_cnt, len(material_list))

    # DATA ASSEMBLING
    pit_container = [comment_header_section, header_section, global_section]
    for section in look_section:
        pit_container.append(section)
    for section in variant_section:
        pit_container.append(section)

    # FILE EXPORT
    ind = "    "
    pit_filepath = str(filepath + ".pit")
    result = _pix_container.write_data_to_file(pit_container, pit_filepath, ind)

    # print("************************************")
    return result