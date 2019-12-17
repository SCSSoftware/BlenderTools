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
import shutil
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.exp import tobj as _tobj
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.utils.printout import lprint


def fill_comment_header_section(look_list, variant_list):
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


def fill_header_section(format_version, file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", format_version))
    section.props.append(("Source", get_combined_ver_str()))
    section.props.append(("Type", "Trait"))
    section.props.append(("Name", file_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def fill_global_section(looks, variants, parts, materials):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("LookCount", looks))
    section.props.append(("VariantCount", variants))
    section.props.append(("PartCount", parts))
    section.props.append(("MaterialCount", materials))
    return section


def fill_material_sections(materials, material_dict):
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


def default_material(alias):
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
        ('FLOAT', "shininess", (5.0,)),
        ('FLOAT', "add_ambient", (0.0,)),
        ('FLOAT', "reflection", (0.0,)),
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


def get_texture_path_from_material(material, texture_type, export_path):
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

    # CALCULATING TOBJ AND TEXTURE PATHS
    texture_raw_path = getattr(material.scs_props, "shader_" + texture_type, "NO PATH")
    tobj_rel_filepath = tobj_abs_filepath = texture_abs_filepath = ""
    scs_project_path = _get_scs_globals().scs_project_path.rstrip("\\").rstrip("/")

    extensions, texture_raw_path = _path_utils.get_texture_extens_and_strip_path(texture_raw_path)

    for ext in extensions:
        if texture_raw_path.startswith("//"):  # relative

            # search for relative path inside current scs project base and
            # possible dlc/mod parent folders; use first found
            for infix in ("", "../base/", "../../base/"):

                curr_path = os.path.join(scs_project_path, infix + texture_raw_path[2:] + ext)

                if os.path.isfile(curr_path):

                    tobj_rel_filepath = texture_raw_path.replace("//", "/")

                    # if tobj is used by user then get texture path from tobj
                    # otherwise get tobj path from texture path
                    if ext == ".tobj":
                        tobj_abs_filepath = curr_path
                        texture_abs_filepath = _path_utils.get_texture_path_from_tobj(curr_path)
                    else:
                        tobj_abs_filepath = _path_utils.get_tobj_path_from_shader_texture(curr_path, check_existance=False)
                        texture_abs_filepath = curr_path
                    break

            # break searching for texture if texture was found
            if tobj_rel_filepath != "":
                break

        elif ext != ".tobj" and os.path.isfile(texture_raw_path + ext):  # absolute

            texture_raw_path_with_ext = texture_raw_path + ext

            # if we are exporting somewhere into SCS Project Base Path texture still can be saved
            if scs_project_path != "" and _path_utils.startswith(export_path, scs_project_path):

                tex_dir, tex_filename = os.path.split(texture_raw_path_with_ext)
                tobj_filename = tex_filename + ".tobj"

                # copy texture beside exported files
                try:
                    shutil.copy2(texture_raw_path_with_ext, os.path.join(export_path, tex_filename))
                except OSError as e:
                    # ignore copying the same file
                    # NOTE: happens if absolute texture paths are used
                    # even if they are referring to texture inside scs project path
                    if type(e).__name__ != "SameFileError":
                        raise e

                # copy also TOBJ if exists
                texture_raw_tobj_path = str(tex_dir) + os.sep + tobj_filename
                if os.path.isfile(texture_raw_tobj_path):
                    shutil.copy2(texture_raw_tobj_path, os.path.join(export_path, tobj_filename))

                # get copied TOBJ relative path to current scs project path
                tobj_rel_filepath = ""
                if export_path != scs_project_path:
                    tobj_rel_filepath = os.sep + os.path.relpath(export_path, scs_project_path)

                tobj_rel_filepath = tobj_rel_filepath + os.sep + tobj_filename[:-5]
                tobj_abs_filepath = os.path.join(export_path, tobj_filename)
                texture_abs_filepath = texture_raw_path_with_ext
                break

            else:
                lprint("E Can not properly export texture %r from material %r!\n\t   " +
                       "Make sure you are exporting somewhere into Project Base Path and texture is properly set!",
                       (texture_raw_path, material.name))
                return ""

    else:
        lprint("E Texture file %r from material %r doesn't exists inside current Project Base Path.\n\t   " +
               "TOBJ  won't be exported and reference will remain empty, expect problems!",
               (texture_raw_path, material.name))
        return ""

    # CREATE TOBJ FILE
    if not os.path.isfile(tobj_abs_filepath):  # only if it does not exists yet

        # export tobj only if file of texture exists
        if os.path.isfile(texture_abs_filepath):
            texture_name = os.path.basename(_path_utils.strip_sep(texture_abs_filepath))
            _tobj.export(tobj_abs_filepath, texture_name, set())
        else:
            lprint("E Texture file %r from material %r doesn't exists, TOBJ can not be exported!",
                   (texture_raw_path, material.name))

    # make sure that Windows users will export proper paths
    tobj_rel_filepath = tobj_rel_filepath.replace("\\", "/")

    return tobj_rel_filepath


def fill_look_sections(data_list):
    """Fills up "Look" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("Look")
        section.props.append(("Name", item['name']))
        for material_section in item['material_sections']:
            section.sections.append(material_section)
        sections.append(section)
    return sections


def _fill_atr_section(atr):
    """Creates "Attribute" section."""
    section = _SectionData("Attribute")
    section.props.append(("Format", atr[0]))
    section.props.append(("Tag", atr[1]))
    section.props.append(("Value", ["&&", (atr[2],)]))
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


def fill_variant_sections(data_list):
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


def fill_part_list(parts, used_parts_names, all_parts=False):
    """Fills up "Part" sections in "Varian" section

    :param parts: SCS Root part inventory or parts collection property from variant inventory
    :type parts: io_scs_tools.properties.object.ObjectPartInventoryItem | list[io_scs_tools.properties.object.ObjectVariantPartInclusionItem]
    :param used_parts_names: list of part names that are actually used in game object
    :type used_parts_names: list[str]
    :param all_parts: flag for all parts are visible (handy for creating default visibilities)
    :type all_parts: bool
    :return: Part records (name, attributes)
    :rtype: list
    """
    part_list = []
    for part_name in used_parts_names:

        part_written = False
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
                part_written = True

        if not part_written:
            lprint("E Part %r from collected parts not avaliable in variant parts inventory, expect problems by conversion!", (part_name,))

    return part_list


def export(root_object, filepath, name_suffix, used_parts, used_materials):
    """Export PIT.

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
    print("**      SCS PIT Exporter          **")
    print("**      (c)2014 SCS Software      **")
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
            root_object.scs_props.active_scs_look = i  # set index for curret look
            _looks.apply_active_look(root_object)  # apply look manually, as active look setter method works only when user sets index from UI

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
                                    elif format_prop == 'INT':
                                        attribute_data.props.append((rec[0], ["ii", (value,)]))
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

                            if attr_prop == "Value" and ("FLOAT" in format_value or "STRING" in format_value or "INT" in format_value):

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
    root_object.scs_props.active_scs_look = saved_active_look  # set index for curret look
    _looks.apply_active_look(root_object)  # apply look manually, as active look setter method works only when user sets index from UI

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
