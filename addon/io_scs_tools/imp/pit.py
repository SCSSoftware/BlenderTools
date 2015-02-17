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
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def _get_header(pit_container):
    """Receives PIT container and returns all its Header properties in its own variables.
    For any item that fails to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pit_container:
        if section.type == "Header":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "FormatVersion":
                    format_version = prop[1]
                elif prop[0] == "Source":
                    source = prop[1]
                elif prop[0] == "Type":
                    f_type = prop[1]
                elif prop[0] == "Name":
                    f_name = prop[1]
                elif prop[0] == "SourceFilename":
                    source_filename = prop[1]
                elif prop[0] == "Author":
                    author = prop[1]
                else:
                    lprint('\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, f_name, source_filename, author


def _get_global(pit_container):
    """Receives PIT container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    look_count = variant_count = part_count = material_count = None
    for section in pit_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "LookCount":
                    look_count = prop[1]
                elif prop[0] == "VariantCount":
                    variant_count = prop[1]
                elif prop[0] == "PartCount":
                    part_count = prop[1]
                elif prop[0] == "MaterialCount":
                    material_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return look_count, variant_count, part_count, material_count


def _get_look(section):
    """Receives a Look section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    look_name = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            look_name = prop[1]
        else:
            lprint('\nW Unknown property in "Look" data: "%s"!', prop[0])
    look_mat_settings = {}
    for sec in section.sections:
        if sec.type == "Material":
            mat_alias = mat_effect = mat_flags = attribute_count = texture_count = None
            attributes = {}
            textures = {}
            for sec_prop in sec.props:
                if sec_prop[0] in ("", "#"):
                    pass
                elif sec_prop[0] == "Alias":
                    mat_alias = sec_prop[1]
                elif sec_prop[0] == "Effect":
                    mat_effect = sec_prop[1]
                elif sec_prop[0] == "Flags":
                    mat_flags = sec_prop[1]
                elif sec_prop[0] == "AttributeCount":
                    attribute_count = sec_prop[1]
                elif sec_prop[0] == "TextureCount":
                    texture_count = sec_prop[1]
                else:
                    lprint('\nW Unknown property in "Look/Material" data: "%s"!', sec_prop[0])
                for sec_section in sec.sections:
                    if sec_section.type == "Attribute":
                        atr_format = atr_tag = atr_value = None
                        for sec_section_prop in sec_section.props:
                            if sec_section_prop[0] in ("", "#"):
                                pass
                            elif sec_section_prop[0] == "Format":
                                atr_format = sec_section_prop[1]
                            elif sec_section_prop[0] == "Tag":
                                atr_tag = sec_section_prop[1]
                            elif sec_section_prop[0] == "Value":
                                atr_value = sec_section_prop[1]
                            else:
                                lprint('\nW Unknown property in "Look/Material/Attribute" data: "%s"!', sec_section_prop[0])
                        attributes[atr_tag] = (atr_format, atr_value)
                    elif sec_section.type == "Texture":
                        txr_tag = txr_value = None
                        for sec_section_prop in sec_section.props:
                            if sec_section_prop[0] in ("", "#"):
                                pass
                            elif sec_section_prop[0] == "Tag":
                                txr_tag = sec_section_prop[1]
                            elif sec_section_prop[0] == "Value":
                                txr_value = sec_section_prop[1]
                            else:
                                lprint('\nW Unknown property in "Look/Material/Texture" data: "%s"!', sec_section_prop[0])
                        textures[txr_tag] = txr_value
            if len(attributes) != attribute_count:
                lprint("W Attribute count in PIT file doesn't match its declaration!")
            if len(textures) != texture_count:
                lprint("W Texture count in PIT file doesn't match its declaration!")
            look_mat_settings[mat_alias] = (mat_effect, mat_flags, attributes, textures, sec)
    return look_name, look_mat_settings


def _get_variant(section):
    """Receives a Variant section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    variant_name = None
    variantparts = []
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            variant_name = prop[1]
        else:
            lprint('\nW Unknown property in "Variant" data: "%s"!', prop[0])

    for sec in section.sections:
        if sec.type == "Part":
            part_name = None
            for sec_prop in sec.props:
                if sec_prop[0] in ("", "#"):
                    pass
                elif sec_prop[0] == "Name":
                    part_name = sec_prop[1]
                elif sec_prop[0] == "AttributeCount":
                    '''
                    NOTE: skipped for now as no data needs to be readed
                    attribute_count = sec_prop[1]
                    '''
                    pass
                else:
                    lprint('\nW Unknown property in "Variant/Part" data: "%s"!', sec_prop[0])

            var_part_format = var_part_tag = var_part_value = None
            for sec_section in sec.sections:
                if sec_section.type == "Attribute":
                    for sec_section_prop in sec_section.props:
                        if sec_section_prop[0] in ("", "#"):
                            pass
                        elif sec_section_prop[0] == "Format":
                            var_part_format = sec_section_prop[1]
                        elif sec_section_prop[0] == "Tag":
                            var_part_tag = sec_section_prop[1]
                        elif sec_section_prop[0] == "Value":
                            var_part_value = sec_section_prop[1]
                        else:
                            lprint('\nW Unknown property in "Variant/Part/Attribute" data: "%s"!', sec_section_prop[0])

                if var_part_format == "INT" and var_part_tag == "visible":
                    if var_part_value[0] == 1:
                        variantparts.append(_name_utils.tokenize_name(part_name))
                else:
                    print('---var_part_value: %s' % str(var_part_value))
    return variant_name, variantparts


def _find_preset(material_effect):
    """Tries to find suitable Shader Preset (as defined in shader_presets.txt file) for imported shader. If it cannot be found, it will return None.

    :param material_effect: Name of the requested Look
    :type material_effect: str
    :return: Preset index and name or None
    :rtype: (int, str) | None
    """

    scs_shader_presets_inventory = bpy.context.scene.scs_shader_presets_inventory
    for i, shader_preset in enumerate(scs_shader_presets_inventory):

        if shader_preset.name != "<none>":
            preset_section = _material_utils.get_shader_preset(_get_scs_globals().shader_presets_filepath, shader_preset.name)
            for preset_prop in preset_section.props:
                if preset_prop[0] == "Effect":

                    if preset_prop[1] == material_effect:

                        return i, shader_preset.name

    return None, None


def _get_shader_data(material_data):
    """Returns Material's Effect, Attributes and Textures.

    :param material_data: Material data
    :type material_data: list
    :return: Material's Effect, Attributes, Textures
    :rtype: tuple
    """
    material_effect = material_data[0]
    material_attributes = material_data[2]
    material_textures = material_data[3]
    material_section = material_data[4]
    return material_effect, material_attributes, material_textures, material_section


def load(filepath, pim_mats_info):
    """Enty point for importing PIT file

    :param filepath: filepath of PIT file
    :type filepath: str
    :param pim_mats_info: list of material info, one material info consists of list: [ blend_mat_name, mat_effect, original_mat_alias ]
    :type pim_mats_info: list of list
    """
    print("\n************************************")
    print("**      SCS PIT Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    ind = '    '
    pit_container = _pix_container.get_data_from_file(filepath, ind)

    # TEST PRINTOUTS
    # ind = '  '
    # for section in pit_container:
    # print('SEC.: "%s"' % section.type)
    # for prop in section.props:
    # print('%sProp: %s' % (ind, prop))
    # for data in section.data:
    # print('%sdata: %s' % (ind, data))
    # for sec in section.sections:
    # print_section(sec, ind)
    # print('\nTEST - Source: "%s"' % pit_container[0].props[1][1])
    # print('')

    # TEST EXPORT
    # path, file = os.path.splitext(filepath)
    # export_filepath = str(path + '_reex' + file)
    # result = pix_write.write_data(pit_container, export_filepath, ind, dump_level)
    # if result == {'FINISHED'}:
    # Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
    # else:
    # Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)

    # LOAD HEADER
    '''
    NOTE: skipped for now as no data needs to be readed
    (format_version, source, f_type, f_name, source_filename, author) = _get_header(pit_container, dump_level)
    '''

    # LOAD GLOBALS
    '''
    NOTE: skipped for now as no data needs to be readed
    (look_count, variant_count, part_count, material_count) = _get_global(pit_container, dump_level)
    '''

    # LOAD LOOKS AND VARIANTS
    loaded_looks = {}
    looks = []
    loaded_variants = []
    for section in pit_container:
        if section.type == 'Look':
            look_name, look_mat_settings = _get_look(section)
            loaded_looks[look_name] = look_mat_settings
            looks.append(look_name)
        elif section.type == 'Variant':
            variant_name, variantparts = _get_variant(section)
            variant_record = (variant_name, variantparts)
            # variant_record = (getVariant(section))
            loaded_variants.append(variant_record)
            # loaded_variants.append((getVariant(section)))

    # PICK ONE LOOK DATA BLOCK, NOTE: This is temporal now as we don't have proper support for Looks.
    if "Default" in loaded_looks:
        look_name = "Default"
    else:
        look_name = looks[0]
    # print(" look_name: %r" % look_name)
    look_mat_settings = loaded_looks[look_name]

    # SETUP ALL THE MATERIALS, NOTE: They should be already created by PIM import.
    for mat_info in pim_mats_info:
        mat = bpy.data.materials[mat_info[0]]
        if mat_info[2] in look_mat_settings:

            # ASSIGN IMPORTED SHADER DATA
            material_effect, material_attributes, material_textures, material_section = _get_shader_data(look_mat_settings[mat_info[2]])

            # TRY TO FIND SUITABLE PRESET
            (preset_index, preset_name) = _find_preset(material_effect)

            if preset_index:  # preset name is found within presets shaders

                mat.scs_props.active_shader_preset_name = preset_name
                preset_section = _material_utils.get_shader_preset(_get_scs_globals().shader_presets_filepath, preset_name)

                if preset_section:

                    preset_effect = preset_section.get_prop_value("Effect")
                    mat.scs_props.mat_effect_name = preset_effect

                    # apply default shader settings
                    _material_utils.set_shader_data_to_material(mat, preset_section, preset_effect,
                                                                is_import=True)

                    # reapply settings from material
                    _material_utils.set_shader_data_to_material(mat, material_section, material_effect,
                                                                is_import=True, override_back_data=False)

                    lprint("I Using shader preset on material %r.", (mat.name,))

                else:
                    print('''NO "preset_section"! (Shouldn't happen!)''')

            else:  # import shader directly from material and mark it as imported

                mat.scs_props.active_shader_preset_name = "<imported>"
                _material_utils.set_shader_data_to_material(mat, material_section, material_effect,
                                                            is_import=True)

                lprint("I Using imported shader on material %r.", (mat.name,))

            # delete not needed data on material
            if "scs_tex_aliases" in mat:
                del mat["scs_tex_aliases"]

    print("************************************")
    return {'FINISHED'}, loaded_variants