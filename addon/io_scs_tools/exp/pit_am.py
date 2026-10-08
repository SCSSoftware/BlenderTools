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

# Copyright (C) 2013-2021: SCS Software

import bpy
import os
import shutil
from . import tobj as _tobj
from ..consts import Variant as _VARIANT_consts
from ..utils import path as _path_utils
from ..utils import get_scs_globals as _get_scs_globals
from ..utils.info import get_combined_ver_str
from ..utils.printout import lprint
from ..internals import looks as _looks
from ..internals import shader_presets as _shader_presets
from ..internals.structure import UnitData as _UnitData
from ..internals.structure import SectionData as _SectionData
from ..internals.containers import pix as _pix_container
from ..internals.containers.writers import sii as _sii_writer
from ..internals.containers.parsers.mat_convert import AttributeConverter

# OK
def fill_comment_header_section(look_list, variant_list):
    """Fills up comment section (before Header)."""
    section = _SectionData("#comment")
    section.props.append(("#", "# Look Names:"))
    for look in look_list:
        section.props.append(("#", "#    " + look['name']))
    section.props.append(("#", "#"))
    section.props.append(("#", "# Variant Names:"))
    for variant in variant_list:
        section.props.append(("#", "#    " + variant[0]))
    section.props.append(("#", "#"))
    return section

# OK
def fill_header_section(format_version, file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", format_version))
    section.props.append(("Source", get_combined_ver_str()))
    section.props.append(("Type", "Trait"))
    section.props.append(("Name", file_name))
    return section

# OK
def fill_global_section(looks, variants, parts, materials):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("LookCount", looks))
    section.props.append(("VariantCount", variants))
    section.props.append(("PartCount", parts))
    section.props.append(("MaterialCount", materials))
    return section

# OK
def _fill_content_sections(input_data, sampler_data, effect_name):
    """Builds SII content for "AutoMat" sections.

    :param input_data: list of tuples (type, name, value, [is_locked], [palette_only], [palette_ufs_paths]) for input properties
    :type input_data: list[tuple[str, str, str, bool]]
    :param sampler_data: list of tuples (name, value, [is_locked]) for sampler properties
    :type sampler_data: list[tuple[str, str, bool]]
    :param effect_name: name of material effect
    :type effect_name: str
    :return: SII content
    :rtype: str
    """

    lprint("D Building SII AutoMat content (effect: %r)", (effect_name))

    units = []

    # Create HEADER
    header = _UnitData("xmat_auto_header", ".header")
    header.props["effect"] = effect_name
    header.props["ref_umat_ufs_path"] = ""
    header.props["ref_umat_ufs_path_secondary"] = ""
    units.append(header)
    # lprint("D ---- Added xmat_auto_header unit")


    # Create INPUTS
    for idx, entry in enumerate(input_data):
        typ, name, value = entry[:3]
        is_locked = entry[3] if len(entry) > 3 else False
        palette_only = entry[4] if len(entry) > 4 else False
        palette_ufs_paths = entry[5] if len(entry) > 5 else 0

        type_map = {
            "FLOAT":    "xmat_input_f",
            "FLOAT2":   "xmat_input_f2",
            "FLOAT3":   "xmat_input_f3",
            "FLOAT4":   "xmat_input_f4",
            "INT":      "xmat_input_int",
            "STRING":   "xmat_input_str"
        }

        unit_type = type_map.get(typ, "xmat_input_str")
        unit = _UnitData(unit_type, f".record{idx}")

        unit.props["name"] = name
        unit.props["value"] = value

        # Additional attributes
        if typ in ("FLOAT3", "FLOAT4"):
            unit.props["palette_only"] = palette_only
            unit.props["palette_ufs_paths"] = palette_ufs_paths

        unit.props["is_locked"] = is_locked

        units.append(unit)
        # lprint("D ---- Added input unit: %r (type: %r, val: %r, locked: %r)", (name, typ, value, is_locked))


    # Create SAMPLERS
    for idx, entry in enumerate(sampler_data):
        name, value = entry[:2]
        is_locked = entry[2] if len(entry) > 2 else False

        # Ensure that sampler path ends with .tobj
        if isinstance(value, str) and value.strip():
            if not value.endswith(".tobj"):
                value = value + ".tobj"

        unit = _UnitData("xmat_sampler", f".record{len(input_data) + idx}")
        unit.props["name"] = name
        unit.props["value"] = value
        unit.props["is_locked"] = is_locked
        units.append(unit)
        # lprint("D ---- Added sampler unit: %r (locked: %r)", (name, is_locked))

    # Finalize content
    content = _sii_writer.write_data_to_string(units, '    ')

    # Visual formatting for better readability by adding 2x tab
    lines = content.splitlines()
    if len(lines) > 1:
        lines = [lines[0]] + ['            ' + line if line.strip() else line for line in lines[1:]]
    content = '\n'.join(lines)

    # Add multi-line quotes around content (only 2x " because by default content is already in single quotes)
    content = f'""{content}""'

    return content

# OK
def fill_automat_sections(automats, automat_dict):
    """Fills up "AutoMat" sections."""
    sections = []
    for automat in automats:
        if isinstance(automat, str):
            sections.append(automat_dict[automat])
        else:
            if automat.name in automat_dict:
                automat_section = automat_dict[automat.name]
            else:
                automat_section = automat_dict[str("_" + automat.name + "_-_default_settings_")]
            sections.append(automat_section)
    return sections

# OK
def default_automat(alias):
    """Return 'default automat' data section."""

    input_data = [
        ('FLOAT3',  "diffuse",      (1.0, 1.0, 1.0)),
        ('FLOAT3',  "specular",     (0.0, 0.0, 0.0)),
        ('FLOAT',   "shininess",    (5.0,)),
        ('FLOAT',   "add_ambient",  (0.0,)),
        ('FLOAT',   "reflection",   (0.0,)),
    ]

    sampler_data = [
        ('texture_base', "", False),
    ]

    effect_name = "eut2.dif"
    content = _fill_content_sections(input_data, sampler_data, effect_name)

    # DEFAULT PROPERTIES
    automat_export_data = _SectionData("AutoMat")
    automat_export_data.props.append(("Alias", alias))
    automat_export_data.props.append(("Index", 0))
    automat_export_data.props.append(("Content", content))

    return automat_export_data

# OK
def get_texture_path_from_material(material, texture_type, export_path):
    """Get's relative path for Texture section of tobj from given texture_type.
    If tobj is not yet created it also creates tobj for it.

    :param material: Blender material
    :type material: bpy.types.Material
    :param texture_type: type of texture which should be readed from material (example "texture_base")
    :type texture_type: str
    :param export_path: path where PIT of this material and texture is gonna be exported
    :type export_path: str
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
            for infix in _path_utils.get_possible_project_infixes(include_zero_infix=True, append_sep=True):

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

                tex_dir, tex_filename = os.path.split(texture_raw_path)
                tobj_filename = tex_filename + ".tobj"

                texture_copied_path_with_ext = os.path.join(export_path, tex_filename) + ext

                # copy texture beside exported files
                try:
                    shutil.copy2(texture_raw_path_with_ext, texture_copied_path_with_ext)
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

                lprint("W Material %r texture of type %r uses absolute path!\n\t    " +
                       "Texture copied into the Project Base Path beside exported PIT file:\n\t    " +
                       "Original path: %r\n\t    " +
                       "Copied path: %r",
                       (material.name, texture_type, texture_abs_filepath, texture_copied_path_with_ext))

                break

            else:
                lprint("E Can not properly export texture %r from material %r!\n\t   " +
                       "Make sure you are exporting somewhere into Project Base Path and texture is properly set!",
                       (texture_raw_path, material.name))
                return ""

    else:
        if texture_raw_path:
            lprint("E Texture file %r from material %r doesn't exists inside current Project Base Path.\n\t   " +
               "TOBJ won't be exported and reference will remain empty, expect problems!",
               (texture_raw_path, material.name))
        else:
            lprint("E Texture type %r on material %r is missing texture.\n\t   " +
               "TOBJ won't be exported and reference will remain empty, expect problems!",
               (texture_type[8:], material.name))
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

# OK
def fill_look_sections(data_list):
    """Fills up "Look" sections."""
    sections = []
    for item_i, item in enumerate(data_list):
        section = _SectionData("Look")
        section.props.append(("Name", item['name']))
        for automat_section in item['automat_sections']:
            section.sections.append(automat_section)
        sections.append(section)
    return sections

# OK (still used in "Part")
def _fill_atr_section(atr):
    """Creates "Attribute" section."""
    section = _SectionData("Attribute")
    section.props.append(("Format", atr[0]))
    section.props.append(("Tag", atr[1]))
    section.props.append(("Value", ["&&", (atr[2],)]))
    return section

# OK
def _fill_part_section(part):
    """Creates "Part" section."""
    section = _SectionData("Part")
    section.props.append(("Name", part[0]))
    section.props.append(("AttributeCount", len(part[1])))
    for atr in part[1]:
        atr_section = _fill_atr_section(atr)
        section.sections.append(atr_section)
    return section

# OK
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

# OK
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

        automat_idx = 0
        material_dict = {}
        material_list = []
        # get materials data
        for material_name, material in used_materials_pairs:
            if material is None:
                material_name = str("_default_material_-_default_settings_")

                # DEFAULT MATERIAL
                automat_export_data = default_automat(material_name)
                material_list.append(material_name)

            else:
                # print('material name: %r' % material.name)
                material_list.append(material)

                # MATERIAL EFFECT
                effect_name = material.scs_props.mat_effect_name

                # PRESET SHADERS
                input_sections = []     # (FORMAT, tag, value)
                sampler_sections = []
                active_shader_preset_name = material.scs_props.active_shader_preset_name

                # SUBSTANCE
                substance_value = material.scs_props.substance
                # only write substance to material if it's assigned
                if substance_value != "None" and substance_value != "":
                    input_sections.append(("STRING", "substance", substance_value))

                if _shader_presets.has_preset(active_shader_preset_name) and active_shader_preset_name != "<none>":

                    preset = _shader_presets.get_preset(active_shader_preset_name)
                    flavors_str = effect_name[len(preset.effect):]
                    section = _shader_presets.get_section(active_shader_preset_name, flavors_str)

                    # COLLECT ATTRIBUTES AND TEXTURES
                    for item in section.sections:

                        preview_only = item.get_prop_value("PreviewOnly")
                        if preview_only and preview_only == "True":
                            continue

                        # ATTRIBUTES
                        if item.type == "Attribute":
                            # print('     Attribute:')

                            format_prop = item.get_prop("Format")[1]
                            tag_prop = item.get_prop("Tag")[1]
                            tag_prop_aux = tag_prop.replace("[", "").replace("]", "")

                            # print('         format_prop: %r' % str(format_prop))
                            # print('         tag_prop: %r' % str(tag_prop))

                            # NOTE: There is no "aux" attributes in new format so technically we should not check it, but for safety we do it anyway.
                            if "aux" in tag_prop:
                                aux_props = getattr(material.scs_props, "shader_attribute_" + tag_prop_aux)
                                value = []
                                for aux_prop in aux_props:
                                    value.append(aux_prop.value)

                                # extract list if there is only one value inside and tagged as FLOAT
                                # otherwise it gets saved as: "Value: ( [0.0] )" instead of: "Value: ( 0.0 )"
                                if len(value) == 1 and format_prop == "FLOAT":
                                    value = value[0]

                            else:
                                value = getattr(material.scs_props, "shader_attribute_" + tag_prop, "NO TAG")

                            if format_prop not in ("FLOAT", "INT", "INT2", "STRING"):
                                value = tuple(value)

                            # print('         > FINAL: %r - %r - %r' % (format_prop, tag_prop, value))

                            input_sections.append((format_prop, tag_prop, value))

                        # TEXTURES
                        elif item.type == "Texture":
                            # print('     Texture:')

                            tag_prop = item.get_prop("Tag")[1].split(":")[1]
                            tobj_rel_path = get_texture_path_from_material(material, tag_prop, os.path.dirname(filepath))
                            # print('         tag_prop: %r' % str(tag_prop))
                            # print('         tobj_rel_path: %r' % str(tobj_rel_path))

                            sampler_sections.append((tag_prop, tobj_rel_path))

                    #######################################
                    ##### TEMPORARY CONVERSION STARTS #####
                    #######################################
                    # NOTE: Temporary conversion from old format (Material) to new one (effect/AutoMat).
                    # In future, new format will be defalut, and converter will be used in #pit.py (not here) instead, to convert from new to old.

                    # Building material_data (for converting attributes and values) and attribute_format (to assign correct formats for not converted data) dicts from input_sections
                    material_data = {attr: val for fmt, attr, val in input_sections}
                    attribute_format = {attr: fmt for fmt, attr, val in input_sections}

                    # Convert attributes and values from material_data to new effect format
                    converter = AttributeConverter()
                    effect_data = converter.material_to_effect(effect_name, material_data)

                    # Building new_input_sections with converted data and correct format of attributes.
                    new_input_sections = []
                    if isinstance(effect_data, dict):
                        for attr, val in effect_data.items():
                            # Checking if attribute was copied 1:1 from old format (not converted - fmt should be preserved)
                            if attr in attribute_format:
                                fmt = attribute_format[attr]
                                val_out = val

                            # If attribute was converted, we need to "guess" correct one from value (there is no 100% certainty)
                            else:
                                if isinstance(val, (tuple, list)):
                                    l = len(val)
                                    if l == 1:
                                        fmt = "FLOAT"
                                        val_out = val[0]
                                    else:
                                        fmt = f"FLOAT{l}"
                                        val_out = tuple(val)

                                elif isinstance(val, int):
                                    fmt = "INT"
                                    val_out = val

                                elif isinstance(val, str):
                                    fmt = "STRING"
                                    val_out = val

                                else:
                                    fmt = "FLOAT"
                                    val_out = val

                            new_input_sections.append((fmt, attr, val_out))
                    elif isinstance(effect_data, tuple) and len(effect_data) == 2:
                        attr, val = effect_data
                         # Checking if attribute was copied 1:1 from old format (not converted - fmt should be preserved)
                        if attr in attribute_format:
                            fmt = attribute_format[attr]
                            val_out = val

                        # If attribute was converted, we need to "guess" correct one from value (there is no 100% certainty)
                        else:
                            if isinstance(val, (tuple, list)):
                                l = len(val)
                                if l == 1:
                                    fmt = "FLOAT"
                                    val_out = val[0]
                                else:
                                    fmt = f"FLOAT{l}"
                                    val_out = tuple(val)

                            elif isinstance(val, int):
                                fmt = "INT"
                                val_out = val

                            elif isinstance(val, str):
                                fmt = "STRING"
                                val_out = val

                            else:
                                fmt = "FLOAT"
                                val_out = val

                        new_input_sections.append((fmt, attr, val_out))

                    # Replace old input_sections with new one (converted to effect)
                    input_sections = new_input_sections

                    #######################################
                    #####  TEMPORARY CONVERSION ENDS  #####
                    #######################################

                    automat_export_data = _SectionData("AutoMat")
                    automat_export_data.props.append(("Alias", material.name))
                    automat_export_data.props.append(("Index", automat_idx))
                    content = _fill_content_sections(input_sections, sampler_sections, effect_name)
                    automat_export_data.props.append(("Content", content))


                elif active_shader_preset_name == "<imported>":

                    # Change it in newer format to imputs and samplers?
                    material_inputs = material['scs_shader_attributes']['attributes'].to_dict().values()
                    material_samplers = material['scs_shader_attributes']['textures'].to_dict().values()

                    # Same as 'for item in section.sections' + 'if item.type == "Attribute"' from above IF.
                    # (because <imported> not use data from preset, we get if from 'scs_shader_attributes' directly)
                    for attribute_dict in material_inputs:
                        # print('     Attribute:')

                        format_prop = ""
                        for attr_prop in sorted(attribute_dict.keys()):

                            # get the format of current attribute (we assume that "Format" attribute is before "Value" attribute in this for loop)
                            if attr_prop == "Format":
                                format_prop = attribute_dict[attr_prop]
                                # print('         format_prop: %r' % str(format_prop))

                            if attr_prop == "Value" and ("FLOAT" in format_prop or "STRING" in format_prop or "INT" in format_prop):
                                tag_prop = attribute_dict["Tag"]
                                # print('         tag_prop: %r' % str(tag_prop))

                                # Aux is not used in new format, but for safety we must do it anyway
                                if "aux" in tag_prop:
                                    aux_props = getattr(material.scs_props, "shader_attribute_" + tag_prop)
                                    value = []
                                    tag_prop = "aux[" + tag_prop[3:] + "]"
                                    for aux_prop in aux_props:
                                        value.append(aux_prop.value)
                                else:
                                    value = getattr(material.scs_props, "shader_attribute_" + tag_prop, None)

                                # print('         value: %r' % str(value))

                            elif attr_prop in ("FriendlyTag", "RequiredFlavors", "ForbiddenFlavors"):
                                continue

                        if format_prop not in ("FLOAT", "INT", "INT2", "STRING"):
                            value = tuple(value)

                        # print('         > FINAL: %r - %r - %r' % (format_prop, tag_prop, value))
                        input_sections.append((format_prop, tag_prop, value))

                    for texture_dict in material_samplers:
                        # print('     Texture:')

                        tag_prop = ""
                        for tex_prop in sorted(texture_dict.keys()):

                            if tex_prop == "Tag":
                                tag_prop = texture_dict[tex_prop].split(':')[1]
                                # print('         tag_prop: %r' % str(tag_prop))

                            elif tex_prop == "Value":
                                tobj_rel_path = get_texture_path_from_material(material, tag_prop, os.path.dirname(filepath))
                                # print('         tobj_rel_path: %r' % str(tobj_rel_path))

                                if tag_prop[8:] not in material.scs_props.get_texture_types():
                                    # Did we need to check this and replace like in pit.py? Idea of <imported> is to export whatever is set for possible backward/upward compatibility.
                                    # For now we will just print warning.
                                    if looks_count > 1:
                                        lprint("W Texture of type %r on material %r with imported shader is not supported in Blender!",
                                               (tag_prop, material_name))

                        # print('         > FINAL: %r - %r' % (tag_prop, tobj_rel_path))
                        sampler_sections.append((tag_prop, tobj_rel_path))


                    automat_export_data = _SectionData("AutoMat")
                    automat_export_data.props.append(("Alias", material.name))
                    automat_export_data.props.append(("Index", automat_idx))
                    content = _fill_content_sections(input_sections, sampler_sections, effect_name)
                    automat_export_data.props.append(("Content", content))

                else:  # when user made material presets were there, but there is no preset library at export for some reason

                    lprint("W Shader preset used on %r not found in Shader Presets Library (Did you set correct path?), "
                           "exporting default material instead!",
                           (material_name,))

                    material_name = str("_" + material_name + "_-_default_settings_")
                    automat_export_data = default_automat(material_name)

            material_dict[material_name] = automat_export_data
            automat_idx += 1

        # create automat sections for looks
        automat_sections = fill_automat_sections(material_list, material_dict)
        look_data = {
            "name": curr_look_name,
            "automat_sections": automat_sections
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
