# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2014: SCS Software

"""
CgFX Shader system support for SCS Tools.
"""

import bpy
import os
# import re
# import pprint
# import collections
# from bpy.props import *
# from . import io_utils
# from . import deprecated_utils as utils
from .deprecated_utils import Print

if "bpy" in locals():
    import imp
    if "io_utils" in locals():
        imp.reload(io_utils)
    else:
        from . import io_utils
    if "utils" in locals():
        imp.reload(utils)
    else:
        from . import deprecated_utils as utils

# def version():
#     '''Here is where to alter version number of the script.'''
#     return 0.2


def get_attribute(output, cgfx_props, key, value):
    """
    :param output:
    :param cgfx_props:
    :param key:
    :param value:
    :return:
    """

    attribute_dict = {}

# SEARCH DATA IN OUTPUT
    if output:
        for rec in output['entries']:
            if rec.endswith(key):
                rec_type = output['entries'][rec]['type']
                rec_default = output['entries'][rec]['value']['value']  # NOTE: UNUSED!
                if rec_type == 'bool':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                elif rec_type == 'int':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                    ui_enum = output['entries'][rec]['t_list']['UIEnum']['value']  # NOTE: UNUSED!
                elif rec_type == 'float':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                    metadata_dict = find_metadata(output, key)
                    # print('  %s' % str(metadata_dict))
                    # print_metadata(metadata_dict)
                    value_params = parse_valueparams(output, metadata_dict['ValueParams'])
                    # print('value_params: %s' % str(value_params))

                    for item in cgfx_props:
                        if item.endswith(key):
                            values = cgfx_props[item]
                            # print('values: %s' % str(values))

                    parameters = format_value_param(values, metadata_dict['ValueFormat'])
                    attribute_dict['Format'] = metadata_dict['Type']
                    attribute_dict['Tag'] = metadata_dict['Name']
                    attribute_dict['Value'] = parameters
                    # print('Attribute {')
                    # print('    Format: %s' % metadata_dict['Type'])
                    # print('    Tag: "%s"' % metadata_dict['Name'])
                    # print('    Value: %s' % str(parameters))
                    # print('}')
                elif rec_type == 'float2':
                    pass
                elif rec_type == 'float3':
                    ui_type = output['entries'][rec]['t_list']['Type']['value']  # NOTE: UNUSED!
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                    # ui_widget = output['entries'][rec]['t_list']['UIWidget']['value']
                    metadata_dict = find_metadata(output, key)
                    # print('  %s' % str(metadata_dict))
                    # print_metadata(metadata_dict)
                    value_params = parse_valueparams(output, metadata_dict['ValueParams'])  # NOTE: UNUSED!
                    # print('value_params: %s' % str(value_params))

                    for item in cgfx_props:
                        if item.endswith(key):
                            values = cgfx_props[item]
                            # print('values: %s' % str(values))

                    parameters = format_value_param(values, metadata_dict['ValueFormat'])
                    attribute_dict['Format'] = metadata_dict['Type']
                    attribute_dict['Tag'] = metadata_dict['Name']
                    attribute_dict['Value'] = parameters
                    # print('Attribute {')
                    # print('    Format: %s' % metadata_dict['Type'])
                    # print('    Tag: "%s"' % metadata_dict['Name'])
                    # print('    Value: %s' % str(parameters))
                    # print('}')
                elif rec_type == 'float4':
                    pass
                elif rec_type == 'sampler2D':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                    metadata_dict = find_metadata(output, key)
                    # print('  %s' % str(metadata_dict))
                    print_metadata(metadata_dict)
                elif rec_type == 'samplerCUBE':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']  # NOTE: UNUSED!
                    metadata_dict = find_metadata(output, key)
                    # print('  %s' % str(metadata_dict))
                    print_metadata(metadata_dict)
                else:
                    print('!!! Udefined type "%s" !!!' % rec_type)
                # print('    - "%s" <%s> - default: %s - "%s"' % (key, rec_type, rec_default, ui_name))


    # MAKE A VALUE STRING (FOR EXPORT)
    #     val_type = type(value)
    #     if val_type is tuple:
    #         if len(value) == 1:
    #             val_string = ('( %s )' % value[0])
    #         elif len(value) == 2:
    #             val_string = ('( %s %s )' % (value[0], value[1]))
    #         elif len(value) == 3:
    #             val_string = ('( %s %s %s )' % (value[0], value[1], value[2]))
    #         elif len(value) == 4:
    #             val_string = ('( %s %s %s %s )' % (value[0], value[1], value[2], value[3]))
    #         else:
    #             Print(1, 'E Unsupported tuple length (%s)' % str(value))
    #             val_string = "<error-unsupported tuple length>"
    #     else:
    #         val_string = str(value)

    # return val_string
    return attribute_dict


def get_texture(output, cgfx_props, key, texture_id):
    """
    :param output:
    :param cgfx_props:
    :param key:
    :param texture_id:
    :return:
    """
    texture_dict = {}

# SEARCH DATA IN OUTPUT
    if output:
        for rec in output['entries']:
            if rec.endswith(key):
                rec_type = output['entries'][rec]['type']
                rec_default = output['entries'][rec]['value']['value']  # NOTE: UNUSED!
                if rec_type == 'bool':
                    pass
                elif rec_type == 'int':
                    pass
                elif rec_type == 'float':
                    pass
                elif rec_type == 'float2':
                    pass
                elif rec_type == 'float3':
                    pass
                elif rec_type == 'float4':
                    pass
                elif rec_type == 'sampler2D':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']
                    ui_texture = output['entries'][rec]['s_list']['Texture']['value']
                    tag = str("texture[" + str(texture_id) + "]:" + key)
                    # print('Texture {')
                    # print('    Tag: "%s"' % tag)
                    # print('    Value: %s' % ui_texture)
                    # print('}')
                    texture_dict['Tag'] = tag
                    texture_dict['Value'] = ui_texture
                elif rec_type == 'samplerCUBE':
                    ui_name = output['entries'][rec]['t_list']['UIName']['value']  # NOTE: UNUSED!
                    ui_texture = output['entries'][rec]['s_list']['Texture']['value']
                    tag = str("texture[" + str(texture_id) + "]:" + key)
                    # print('Texture {')
                    # print('    Tag: "%s"' % tag)
                    # print('    Value: %s' % ui_texture)
                    # print('}')
                    texture_dict['Tag'] = tag
                    texture_dict['Value'] = ui_texture
                else:
                    print('!!! Udefined type "%s" !!!' % rec_type)
                # print('    - "%s" <%s> - default: %s - "%s"' % (key, rec_type, rec_default, ui_name))

    return texture_dict


def find_metadata(output, key):
    """
    :param output:
    :param key:
    :return:
    """
    metadata_dict = {}
    for rec in output['entries']:
        # print('   rec: %s' % str(rec))
        if output['entries'][rec]['type'] == 'string':
            if output['entries'][rec]['value']['value'] == key:
                if output['entries'][rec]['t_list']:
                    if output['entries'][rec]['t_list']['Name']:
                        metadata_dict['Name'] = output['entries'][rec]['t_list']['Name']['value']
                    if output['entries'][rec]['t_list']['Type']:
                        metadata_dict['Type'] = output['entries'][rec]['t_list']['Type']['value']
                    if output['entries'][rec]['t_list']['ValueFormat']:
                        metadata_dict['ValueFormat'] = output['entries'][rec]['t_list']['ValueFormat']['value']
                    if output['entries'][rec]['t_list']['ValueParams']:
                        metadata_dict['ValueParams'] = output['entries'][rec]['t_list']['ValueParams']['value']
    return metadata_dict


def print_metadata(metadata_dict):
    """
    :param metadata_dict:
    :return:
    """
    for item in metadata_dict:
        print('            %s:\t%s' % (item, metadata_dict[item]))


def format_value_param(value_params, value_format):
    """
    :param value_params:
    :param value_format:
    :return:
    """
    import collections
    parameters = []
    # print(' value_params: %s' % str(value_params))
    # print(' value_format: %s' % str(value_format))
    value_format_strip = value_format.strip('( )')
    value_formats = value_format_strip.split()
    # print(' value_formats: %s' % str(value_formats))
    indexed_values = {}
    for i, index_spec in enumerate(value_formats):
        index_spec = index_spec.strip('^s ')
        try:
            index_spec_int = int(index_spec)
        except:
            index_spec_int = None
        # print('   index_spec_int: %s' % str(index_spec_int))
        if type(value_params) == float:
            indexed_values[index_spec_int] = value_params
        else:
            indexed_values[index_spec_int] = value_params[i]
    # print('indexed_values: %s' % str(indexed_values))
    ordered_indexed_values = collections.OrderedDict(sorted(indexed_values.items()))
    # print('ordered_indexed_values: %s' % str(ordered_indexed_values))
    for key in ordered_indexed_values:
        val = ordered_indexed_values[key]
        # parameters.append(str(float(val)))
        parameters.append(str(val))
    pars = " ".join(parameters)
    result = str("( " + str(pars) + " )")
    return result


def find_entry(output, key, index=None):
    """
    Takes CgFX Shader output, key and optional index and returns
    parameter found in output or None.
    :param output:
    :param key:
    :param index:
    :return:
    """
    parameter = None
    for rec in output['entries']:
        # print("rec: %s" % str(rec))
        if rec.endswith(key):
            # print("___: %s" % str(output['entries'][rec]['value']['value']))
            parameter = output['entries'][rec]['value']['value']
            if index is not None:
                parameter = parameter[index]
    return parameter


def parse_valueparams(output, value_params_string):
    """
    :param output:
    :param value_params_string:
    :return:
    """
    value_params = []
    value_params_split = value_params_string.split(',')
    for value_param in value_params_split:
        # print('  - value_param: "%s"' % value_param)
        value_param_split = value_param.split('[', 1)
        # print('  - value_param_split: "%s"' % str(value_param_split))
        if len(value_param_split) == 1:
            parameter = find_entry(output, value_param)
        else:
            value_param_name = value_param_split[0]
            value_param_index_str = value_param_split[1].strip(']')
            try:
                value_param_index = int(value_param_index_str)
            except:
                Print(1, 'E Bad index specification! Value "%s" cannot be converted to integer!' % value_param_index)
                value_param_index = None
            parameter = find_entry(output, value_param_name, value_param_index)
        value_params.append(parameter)
    return value_params


def get_cgfx_filepath(cgfx_name):
    """Returns a valid filepath to CgFX Shader file or None.

    :param cgfx_name: CgFX Name
    :type cgfx_name: str
    :return: CgFX File Path or None
    :rtype: str
    """
    # print('  > get_cgfx_filepath... (%s)' % cgfx_name)
    if cgfx_name:
        cgfx_path = bpy.data.worlds[0].scs_globals.cgfx_library_rel_path
        if cgfx_path.startswith(str(os.sep + os.sep)):
            root_path = bpy.data.worlds[0].scs_globals.scs_project_path
            cgfx_filepath = str(root_path + cgfx_path[1:] + os.sep + cgfx_name + ".cgfx")
        else:
            cgfx_filepath = str(cgfx_path + os.sep + cgfx_name + ".cgfx")
        # print('  cgfx_filepath: "%s"' % cgfx_filepath)
        if os.path.isfile(cgfx_filepath):
            return cgfx_filepath
        else:
            Print(1, '\nE Invalid filepath %r!' % str(cgfx_filepath).replace("\\", "/"))
            return None
    else:
        return None


def get_actual_part():
    """Returns active Part name as a string."""
    # print('  > get_actual_part...')
    scs_root_object = utils.get_scs_root_object(bpy.context.active_object)
    # for part in bpy.context.scene.scs_part_inventory:
    for part in scs_root_object.scs_object_part_inventory:
        if part.active:
            return part.name
    return None


def set_actual_part(part_name):
    """Sets provided Part name as active."""
    # print('  > set_actual_part...')
    scs_root_object = utils.get_scs_root_object(bpy.context.active_object)
    # for part in bpy.context.scene.scs_part_inventory:
    for part in scs_root_object.scs_object_part_inventory:
        if part.name == part_name:
            part.active = True
        else:
            part.active = False


def get_actual_variant():
    """Returns active Variant name as a string."""
    # print('  > get_actual_variant...')
    for variant in bpy.context.scene.scs_variant_inventory:
        if variant.active:
            return variant.name
    return None


def get_actual_look():
    """Returns actual Look name as a string."""
    # print('  > get_actual_look...')
    for look in bpy.context.scene.scs_look_inventory:
        if look.active:
            return look.name
    return None


def set_actual_look(look_name): ## NOTE: Probably not needed!
    """Sets provided Look name as active."""
    # print('  > set_actual_look...')
    print('look_name: "%s"' % str(look_name))
    for look in bpy.context.scene.scs_look_inventory:
        print('look: "%s"' % str(look))
        print('look.name: "%s"' % str(look.name))
        if look.name == look_name:
            look.active = True
        else:
            look.active = False


def make_arg(key, val):
    """Takes a key and its value and return a formated argument."""
    # print('  > make_arg...')
    # "-DAIRBRUSH_ENABLE"    # Bool
    # "-DNMAP_ENABLE=0"      # Enum Index
    if val == 'true':
        arg_string = "-D" + key
    elif val == 'false':
        arg_string = None
    else:
        arg_string = "-D" + key + "=" + val
    return arg_string


def get_arg_strings(cgfx_setting_dict):
    """Receives the actual CgFX Shader settings (as set in UI) in a dictionary
    and returns it as a list of argument strings."""
    print('  > get_arg_strings...')
    add_args = []
    for item in cgfx_setting_dict:
        if item.startswith("d_"):
            arg_string = make_arg(item[2:], cgfx_setting_dict[item])
            if arg_string: add_args.append(arg_string)
    return add_args


def get_args(material, look):
    """Receives Material and Look name and returns a list of argument strings for compilation."""
    print('  > get_args... (%s)' % str(look))
    args = []
    if len(material.scs_cgfx_looks[look].cgfx_data) > 0:
        for item in material.scs_cgfx_looks[look].cgfx_data:
            # print(' ..item.name: "%s"' % item.name)
            if item.name.startswith("d_"):
                if item.type == "bool":
                    arg_string = make_arg(item.name[2:], item.value)
                elif item.type == "enum":
                    arg_string = make_arg(item.name[2:], item.value)
                else:
                    arg_string = None
                if arg_string: args.append(arg_string)
    print('  > get_args... %s' % str(args))
    return args


def get_custom_props_from_material(material, look):
    """Takes Material and Look and returns its CgFX custom properties in a dictionary or None."""
    print('  > get_custom_props_from_material...')
    props = {}
    try:
        for item in material.items():
            if item[0].startswith("cgfx_"):
                item_split = item[0].split("_", 3)
                if item_split[1] == look:
                    # print('"%s":\t%s' % (str(item[0]), str(item[1])))
                    # print('    %s' % str(item))
                    props[item[0]] = item[1]
    except:
        return None
    if len(props) == 0:
        return None
    # print('+props: %s' % str(props))
    return props


def get_cgfx_props_from_material(material, look):
    """Takes Material and Look and returns its CgFX properties in a dictionary or None."""
    print('  > get_cgfx_props_from_material...')
    props = get_custom_props_from_material(material, look)
    # print('-props: %s' % str(props))
    cgfx_props = {}

    if props:
        for prop in props:
            if prop.startswith("cgfx_"):
                # props[prop[0]] = props[prop]
                if isinstance(props[prop], int):
                    # print('"%s":\t%i' % (str(prop), props[prop]))
                    cgfx_props[prop[5:]] = str(props[prop])
                elif isinstance(props[prop], float):
                    # print('"%s":\t\t%s' % (str(prop), props[prop]))
                    cgfx_props[prop[5:]] = str(props[prop])
                elif len(props[prop]) == 2:
                    # print('"%s":\t\t(%s, %s)' % (str(prop), str(props[prop][0]), str(props[prop][1])))
                    cgfx_props[prop[5:]] = (props[prop][0], props[prop][1])
                elif len(props[prop]) == 3:
                    # print('"%s":\t\t(%s, %s, %s)' % (str(prop), str(props[prop][0]), str(props[prop][1]), str(props[prop][2])))
                    cgfx_props[prop[5:]] = (props[prop][0], props[prop][1], props[prop][2])
                else:
                    cgfx_props[prop[5:]] = props[prop]
            # else:
            #     print('prop: %s' % str(prop))
    # if len(cgfx_props) == 0:
    #     return None
    return cgfx_props


def store_cgfx_settings_in_material_look():
    """Stores all CgFX settings from actual UI into active material look."""
    material = bpy.context.active_object.active_material
    actual_look = utils.get_actual_look()
    # print('\t\t\tactual_look: %r' % actual_look)

## FOR EVERY CgFX UI ITEM...
    try:
        for ui_item in bpy.context.screen.scs_cgfx_ui.__locals__:
            if ui_item.startswith("cgfx_"):
                if not ui_item.endswith("_mtplr"):
                    value = getattr(bpy.context.screen.scs_cgfx_ui, ui_item)
                    # print('ui_item: "%s"\t--> %s' % (ui_item, value))

## ...COPY ITS VALUE INTO MATERIAL'S ACTUAL LOOK...
                    for item in material.scs_cgfx_looks[actual_look].cgfx_data:
                        if ui_item.endswith(item.name):
                            if item.type == "bool":
                                item.value = str(value).lower()
                            elif item.type in ("enum", "string"):
                                item.value = value
                            elif item.type == "float2":
                                item.value = str("(" + str(value[0]) + ", " + str(value[1]) + ")")
                            elif item.type == "float3":
                                item.value = str("(" + str(value[0]) + ", " + str(value[1]) + ", " + str(value[2]) + ")")
                            elif item.type == "color":
                                mtplr = getattr(bpy.context.screen.scs_cgfx_ui, str(ui_item + "_mtplr"))
                                item.value = str("(" + str(value[0]) + ", " + str(value[1]) + ", " + str(value[2]) + ", " + str(mtplr) + ")")
                            else:
                                item.value = str(value)
    except AttributeError:
        print('Need to recompile CgFX data...')


def update_looks_in_materials():
    """This function updates all Material Look records according to Look Inventory."""
    # print('  > update_looks_in_materials...')
    look_names = []

    ## Create list of existing Look names...
    for look in bpy.context.scene.scs_look_inventory:
        # print('  -1- Look name %r is in inventory...' % look.name)
        look_names.append(look.name)

    ## In every material...
    for material in bpy.data.materials:
        # print('  -*- Material %r...' % material.name)

        ## ...delete Look records, that doesn't exists any more...
        for look_i, look in enumerate(material.scs_cgfx_looks):
            if look not in look_names:
                material.scs_cgfx_looks.remove(look_i)

        ## ...add existing Look to Material record, if they're not already there...
        for look in bpy.context.scene.scs_look_inventory:
            # print('  -*- Look %r...' % look.name)
            if look.name not in material.scs_cgfx_looks:
                # print('  -2- Look name %r added to %r Material...' % (look.name, material.name))
                look_record = material.scs_cgfx_looks.add()
                look_record.name = look.name
            # else:
            #     print('  -2- Look name %r NOT added to %r Material...' % (look.name, material.name))


def update_ui_props_from_matlook_record(all_values):
    """Updates UI to saved values in CgFX Material Look record."""
    print('  > update_ui_props_from_matlook_record...')

    ## LOCK UI UPDATES...
    bpy.data.worlds[0].scs_globals.config_update_lock = True
    for name in bpy.context.screen.scs_cgfx_ui.__locals__:
        # item = bpy.context.screen.scs_cgfx_ui.__locals__[name]
        if name.startswith("cgfx_"):
            if name in all_values:
                item_value = all_values[name]
                if 'subtype' in bpy.context.screen.scs_cgfx_ui.__locals__[name][1]:
                    # print('name: "%s"' % name)
                    # print('class: "%s"' % item.__class__)
                    # print('item_value: %s' % str(item_value))
                    # print('  bpy.context.screen.scs_cgfx_ui.__locals__[name][1]:\n%s' % str(bpy.context.screen.scs_cgfx_ui.__locals__[name][1]))
                    if bpy.context.screen.scs_cgfx_ui.__locals__[name][1]['subtype'] == 'COLOR':
                        item_value_split = str(item_value)[1:-1].split(", ")
                        item_value_color = str("(" + item_value_split[0] + ", " + item_value_split[1] + ", " + item_value_split[2] + ")")
                        if len(item_value_split) == 4:
                            item_value_mtplr = str(item_value_split[3])
                        else:
                            item_value_mtplr = "1.0"
                        # print('item_value_color: %s' % str(item_value_color))
                        # print('item_value_mtplr: %s' % str(item_value_mtplr))
                        exec('''bpy.context.screen.scs_cgfx_ui.%s = %s''' % (name, item_value_color))
                        exec('''bpy.context.screen.scs_cgfx_ui.%s = %s''' % (str(name + "_mtplr"), item_value_mtplr))
                    else:
                        exec('''bpy.context.screen.scs_cgfx_ui.%s = %s''' % (name, str(item_value)))
                else:
                    exec('''bpy.context.screen.scs_cgfx_ui.%s = %s''' % (name, str(item_value)))

    ## UNLOCK UI UPDATES...
    bpy.data.worlds[0].scs_globals.config_update_lock = False


class Token():
    def __init__(self, data_type, value):
        self.type = data_type       # Type (number, id, string, char, eof)
        self.value = value          # Value (1.5, some_name, "ab cd", ;)


class Tokenizer():
    def __init__(self, data_input):
        self.input = data_input     # Array of data_input lines
        self.current_line = 0       # The currently processed line. If equal to length of data_input array, we are at end of the data_input
        self.current_pos = 0        # Character position in the line
        self.active_token = None    # Currently active token

    def peek_token(self):
        """Returns the active token parsing it if necessary.
        Multiple calls to this function without interleaving consume_token() returns the same token."""
        if self.active_token is None: self.active_token = self.parse_token()
        return self.active_token

    def consume_token(self):
        """Consumes active token, peeking for it if necessary. Returns the consumed token."""
        result = self.peek_token()
        self.active_token = None
        return result

    def consume_token_if_of_type(self, data_type):
        """Consumes active token if it has specified data_type."""
        if self.peek_token().type != data_type: return None
        return self.consume_token()

    def consume_token_if_match(self, data_type, value):
        """Consumes active token if it has specified type and value."""
        if self.peek_token().type != data_type or self.peek_token().value != value: return None
        return self.consume_token()

    def parse_token(self):
        """Parses next token from the input."""
        while self.current_line < len(self.input):

            # If we processed entire line, advance to next one
            line_length = len(self.input[self.current_line])
            if self.current_pos >= line_length:
                self.current_line += 1
                self.current_pos = 0
                continue

            # Unprocessed remainder of the line
            # line_remainder = str(self.input[self.current_line][self.current_pos:])[2:-1]
            line_remainder = self.input[self.current_line][self.current_pos:]

            # Skip all leading whitespace
            # print('line_remainder: %s' % str(line_remainder))
            match = re.match('[ \t]+', line_remainder)
            if match:
                self.current_pos += match.end(0)
                continue

            # Is this a number?
            match = re.match('-?\d+(\.\d+)?', line_remainder)
            if match:
                self.current_pos += match.end(0)
                return Token('number', line_remainder[0:match.end(0)])

            # Is this a identifier?
            match = re.match('\w+', line_remainder)
            if match:
                self.current_pos += match.end(0)
                return Token('id', line_remainder[0:match.end(0)])

            # Is this a string? Currently does not support escape sequences
            match = re.match('"([^"]*)"', line_remainder)
            if match:
                self.current_pos += match.end(0)
                return Token('string', line_remainder[1:match.end(0)-1])

            # Return the value as character.
            self.current_pos += 1
            return Token('char', line_remainder[0])

        # Once we get to the end of the stream, always return the eof token
        # even if we are called more than once for some reason
        return Token('eof', '')


def parse_string_value(tokenizer, output):
    """Parses sequence of strings "aaa" "bbb ccc" "dddd" until non-string
    token is encountered. There must be at least one string."""

    output["value"] = ""

    value = tokenizer.consume_token_if_of_type('string')
    if value is None: return False

    while 1:
        output["value"] = output["value"] + value.value
        value = tokenizer.consume_token_if_of_type('string')
        if value is None: break
    return True


def parse_value(tokenizer, output):
    """Parses value of one from several possible types."""

    # {num, num, num}. Variable number of numbers with at least one
    value = tokenizer.consume_token_if_match('char', '{')
    if value is not None:
        output["value"] = []
        while 1:
            value = tokenizer.consume_token_if_of_type('number')                    # Must be a number
            if value is None: return False
            output["value"].append(value.value)
            if tokenizer.consume_token_if_match('char', '}') is not None: break     # End when closing bracket is encountered
            if tokenizer.consume_token_if_match('char', ',') is None: return False  # Otherwise there must be a separator
        return True

    # Sequence of strings. Eg. "aaa" "bbb ccc" "dddd"
    if tokenizer.peek_token().type == 'string':
        return parse_string_value(tokenizer, output)

    # Simple number
    value = tokenizer.consume_token_if_of_type('number')
    if value is not None:
        output["value"] = value.value
        return True

    # Simple id
    value = tokenizer.consume_token_if_of_type('id')
    if value is not None:
        output["value"] = value.value
        return True

    # Id wrapped by brackets. E.g. <default_texture_2d>
    if tokenizer.consume_token_if_match('char', '<') is not None:
        value = tokenizer.consume_token_if_of_type('id')
        if value is None: return False
        output["value"] = "<" + value.value + ">"
        return tokenizer.consume_token_if_match('char', '>') # not None

    # Unknown value type
    return False


def parse_param(tokenizer, output):
    """Parses single parameter like 'string Name = "foo" "bar";'."""

    # Type of the parameter
    data_type = tokenizer.consume_token_if_of_type('id')
    if data_type is None: return False

    # Name of the parameter
    name = tokenizer.consume_token_if_of_type('id')
    if name is None: return False

    # Assignment operator
    if tokenizer.consume_token_if_match('char', '=') is None: return False

    # Value to assign
    param_value = {"type": data_type.value}
    output[name.value] = param_value

    if not parse_value(tokenizer, param_value): return False

    # The final separator must be present
    return tokenizer.consume_token_if_match('char', ';') is not None


def parse_struct(tokenizer, output):
    """Takes Tokenizer object (compiled data lines) and dictionary to hold the results.
    It parses compiled data and load it to the dictionary."""
    output_item_index = 0
    while 1:

        # Type of the parameter
        data_type = tokenizer.consume_token_if_of_type('id')
        if data_type is None:
            # print('  >> type is None')
            return False

        # Name of the parameter
        name = tokenizer.consume_token_if_of_type('id')
        if name is None:
            # print('  >> name is None')
            return False

        # If this is the special variable, we are done with the parsing. (Note that no type check is implemented)
        if name.value == "sgfx_effectName":
            if tokenizer.consume_token_if_match('char', '=') is None:
                # print("  >> if tokenizer.consume_token_if_match('char', '=') is None")
                return False
            return parse_string_value(tokenizer, output["effect_name"])

        struct_result = {}
        if name.value.startswith("define_"):
            name_value = name.value.replace("define_", "d_")
        else:
            name_value = name.value
        # print(' * name_value: %s' % name_value)
        output_item_name = str("cgfx_" + str(output_item_index).rjust(3, "0") + "_" + name_value)
        output["entries"][output_item_name] = struct_result
        struct_result["t_list"] = {}
        struct_result["s_list"] = {}
        struct_result["value"] = {}
        struct_result["type"] = data_type.value
        # struct_result["index"] = output_item_index
        output_item_index += 1
        # print(' >>> name_value: %s' % name_value)

        # If there is the sgfxtag, remember that in the output
        if tokenizer.consume_token_if_match('char', ':') is not None:
            if tokenizer.consume_token_if_match('id', 'SgfxDefine') is None:
                # print("  >> tokenizer.consume_token_if_match('id', 'SgfxDefine') is None")
                return False
            struct_result['is_define'] = True

        # Optional body
        if tokenizer.consume_token_if_match('char', '<') is not None:
            while tokenizer.consume_token_if_match('char', '>') is None:
                if not parse_param(tokenizer, struct_result["t_list"]):
                    # print('  >> not parse_param(tokenizer, struct_result["t_list"])')
                    return False

        # Parse the 'default' value and write it as 'value' (as it will represent actual value of an item from now on)
        if tokenizer.consume_token_if_match('char', '=') is not None:
            if not parse_value(tokenizer, struct_result["value"]):
                # print('  >> not parse_value(tokenizer, struct_result["value"])')
                return False

        # Parse the additional list.
        if tokenizer.consume_token_if_match('char', '{') is not None:
            while tokenizer.consume_token_if_match('char', '}') is None:

                # Id of the entry
                data_id = tokenizer.consume_token_if_of_type('id')
                if data_id is None:
                    # print('  >> data_id is None')
                    return False

                # Assignment operator
                if tokenizer.consume_token_if_match('char', '=') is None:
                    # print("  >> tokenizer.consume_token_if_match('char', '=') is None")
                    return False

                # The value itself
                entry_output = {}
                struct_result["s_list"][data_id.value] = entry_output

                if not parse_value(tokenizer, entry_output):
                    # print('  >> not parse_value(tokenizer, entry_output)')
                    return False

                # Final terminator of the entry
                if tokenizer.consume_token_if_match('char', ';') is None:
                    # print("  >> tokenizer.consume_token_if_match('char', ';') is None")
                    return False

        # There now must be a terminator
        if tokenizer.consume_token_if_match('char', ';') is None:
            # print("  >> tokenizer.consume_token_if_match('char', ';') is None")
            return False


def get_vertex_program(filepath):
    """Takes a filepath of CgFX file and returns the name of vertex program,
    that should be used for compilation of vertex shader.
    If no such specification is found, None is returned."""
    # print('  > get_vertex_program...')
    vertex_program = None
    with open(filepath) as file_open:
        for i, line in enumerate(file_open):
            line = line.strip()
            if line.startswith('VertexProgram'):
                line_split = line.split()
                for word in line_split:
                    if '()' in word:
                        vertex_program = word.split('(')[0]
                        # print('vertex_program: "%s"' % vertex_program)
                break
    file_open.close()
    return vertex_program


def preprocess_cgfx(effect_base_path, cgfx_filepath, add_args=[]):
    """Preprocess CgFX Shader file."""
    print('  > preprocess_cgfx...')
    # print('\teffect_base_path: %s\n\tcgfx_filepath: %s' % (effect_base_path, cgfx_filepath))
    import subprocess
    return_code = 1
    preprocessed_stdout = ""
    preprocessed_stderr = None
    args = ["cgc", "-E", "-P", "-DS_MAYA", "-I.",\
            "-I" + effect_base_path + os.sep + "eut",\
            "-I" + effect_base_path + os.sep + "eut2",\
            "-I" + effect_base_path + os.sep + "eut2" + os.sep + "cgfx",\
            "-I" + effect_base_path + os.sep + "eut2" + os.sep + "std_passes",\
            "-I" + effect_base_path + os.sep + "deferred",\
            "-I" + effect_base_path + os.sep + "deferred" + os.sep + "std_passes",\
            "-I" + effect_base_path + os.sep + "generic",\
            cgfx_filepath]
    for item in add_args:
        args.append(item)
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
    except:
        Print(1, "\n\nE 'nVidia CG Toolkit' doesn't appear to be installed on your machine! Please install it in order to be able to setup materials using CgFX shaders.\n\n")
        process = None
    if process:
        preprocessed_stdout, preprocessed_stderr = process.communicate()
        return_code = process.wait()
    # print('  preprocessed_stdout: %s\n  preprocessed_stderr: %s' % (preprocessed_stdout, preprocessed_stderr))
    return return_code, preprocessed_stdout, preprocessed_stderr


def recompile_cgfx_data(effect_base_path, cgfx_filepath, add_args=[]):
    """Recompile CgFX data..."""
    print('  > recompile_cgfx_data...')
    return_code, preprocessed_stdout, preprocessed_stderr = preprocess_cgfx(effect_base_path, cgfx_filepath, add_args)
    preprocessed_stdout_list = []
    if return_code == 0:
        print('...shader preprocess successful (%s)' % os.path.basename(cgfx_filepath))
        preprocessed_stdout_split = re.split(br'[\r\n]+', preprocessed_stdout)
        for line in preprocessed_stdout_split:
            if line not in (b' ', b'  '):
                preprocessed_stdout_list.append(str(line)[2:-1].replace('\\t', '\t'))
                # print('line: %s' % str(line)[2:-1])
                if b'sgfx_effectName' in line: break
        # print('preprocessed_stdout_list:\n  "%s"' % str(preprocessed_stdout_list))
    return return_code, preprocessed_stdout, preprocessed_stderr, preprocessed_stdout_list


def preprocess_vertex_cgfx(preprocessed_stdout, args):
    """Preprocess CgFX Vertex Shader data."""
    print('  > preprocess_vertex_cgfx...')
    import subprocess
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    vs_stdout, vs_stderr = process.communicate(preprocessed_stdout)
    return_code = process.wait()
    # print('  vs_stdout: %s\n  vs_stderr: %s' % (vs_stdout, vs_stderr))
    return return_code, vs_stdout, vs_stderr


def recompile_cgfx_vertex_data(preprocessed_stdout, cgfx_filepath, cgfx_path, vertex_program, filewrite=0):
    """Recompile CgFX vertex data..."""
    print('  > recompile_cgfx_vertex_data...')
    vertex_data = []
    args = ["cgc", "-O3", "-profile", "arbvp1", "-entry", vertex_program]
    return_code, vs_stdout, vs_stderr = preprocess_vertex_cgfx(preprocessed_stdout, args)

    if return_code == 0:
        print('...vertex shader preprocess successful...')# - (%s)' % os.path.basename(cgfx_filepath))
        # print('vs_stdout:\n%s' % repr(vs_stdout))
        vs_stdout_split = re.split(br'[\r\n]+', vs_stdout)
        if filewrite:
            cgfx_2_base_name = str(os.path.basename(cgfx_filepath)) + "_tmp2.ini"
            tmp_2_stdout = os.path.join(cgfx_path, cgfx_2_base_name)
            stdout_open = open(tmp_2_stdout, 'w')
        # line_prints = 50
        for item in vs_stdout_split:
            line = str(item)[2:-1]
            if line not in ("", " "):
                line = line.replace('\\t', '\t')
                if filewrite:
                    stdout_open.write(line + '\n')
                if 'v_maya.' in line:
                    split_1 = re.split('v_maya.', line)
                    split_2 = re.split('[ ]+', split_1[1])
                    vertex_data.append(split_2[0])
                # if line_prints > 0:
                #     print('=--"%s"' % item)
                #     print('=>   "%s"' % line)
                # line_prints -= 1
        if filewrite:
            stdout_open.close()
        # print('vertex_data:\n%s' % repr(vertex_data))
    else:
        if vs_stderr is None:
            Print(1, 'E ...no CgFX vertex data found!')
        else:
            Print(1, 'E Preprocess of CgFX vertex data failed: "%s"' % str(vs_stderr))
    return vertex_data


def recompile_cgfx_shader(material, look="", clear_records=False, filewrite=0):
    """Recompile CgFX Shader data..."""
    print('  > recompile_cgfx_shader...')

## MAKE FILEPATHS...
    # effect_base_path = utils.repair_path(bpy.data.worlds[0].scs_globals.scs_project_path + '/base/effect') ## TODO: A better solution?
    effect_base_path = utils.repair_path(bpy.data.worlds[0].scs_globals.scs_project_path + os.sep + 'base' + os.sep + 'effect')
    print('effect_base_path:\n  "%s"' % effect_base_path)
    cgfx_filepath = get_cgfx_filepath(material.scs_props.cgfx_filename)
    print('cgfx_filepath:\n  "%s"' % cgfx_filepath)

    if cgfx_filepath:
        cgfx_path = os.path.dirname(cgfx_filepath)
        # print('cgfx_path:\n  "%s"' % cgfx_path)

## UPDATE "scs_cgfx_looks"...
        if len(material.scs_cgfx_looks) == 0:
            update_looks_in_materials()

## IF NO LOOK IS PROVIDED, GET ACTUAL LOOK...
        if look == "": look = utils.get_actual_look()

## TRY TO RETRIEVE MATERIAL SETTINGS AND MAKE ARGUMENTS FOR RECOMPILING...
        args = get_args(material, look)
        #print('  * args: %s' % str(args))

## RECOMPILE CGFX SHADER...
        return_code, preprocessed_stdout, preprocessed_stderr, preprocessed_stdout_list = recompile_cgfx_data(effect_base_path, cgfx_filepath, args)
        ## NOTE: "return_code" - success state
        ## NOTE: "preprocessed_stdout" - original and complete compiled shader data
        ## NOTE: "preprocessed_stderr" - other shader data (?) (unused)
        ## NOTE: "preprocessed_stdout_list" - only UI part of compiled shader data (every non-empty line as an item of the list)

        if return_code == 0:

## PARSE CGFX SHADER DATA...
            tokenizer = Tokenizer(preprocessed_stdout_list)
            output = {'effect_name': {}, 'entries': {}}
            # output["effect_name"] = {}
            # output["entries"] = {}
            result = parse_struct(tokenizer, output)

            if result:

## DEBUG PRINT TO CONSOLE...
                if 0:
                    pp = pprint.PrettyPrinter(indent=1)
                    print("==================================================")
                    pp.pprint(output)
                    print("==================================================")

## DEBUG PRINT TO A FILE...
                if filewrite:
                    cgfx_tmp1_name = str(os.path.basename(cgfx_filepath)) + "_tmp1.ini"
                    cgfx_tmp1_filepath = os.path.join(cgfx_path, cgfx_tmp1_name)
                    # print('cgfx_tmp1_name:\n  "%s"' % cgfx_tmp1_name)
                    # print('cgfx_tmp1_filepath:\n  "%s"\n' % cgfx_tmp1_filepath)
                    file_open = open(cgfx_tmp1_filepath, 'w')
                    pprint.pprint(output, stream=file_open)
                    file_open.close()

## RECOMPILE VERTEX SHADER...
                vertex_program = get_vertex_program(cgfx_filepath)
                vertex_data = recompile_cgfx_vertex_data(preprocessed_stdout, cgfx_filepath, cgfx_path, vertex_program, filewrite)
                # vertex_data = None

## WRITE CGFX DATA TO MATERIAL LOOK...
                cgfx_rec_from_compiled(material, look, output, vertex_data, clear_records)
                # cgfx_rec_from_ui(material, look, output, vertex_data, clear_records)

                # register_cgfx_ui(material, look)

## PRINT DEBUG TABLE PRINT...
                # utils.print_matlook_info(material, look, output, "recompile_cgfx_shader (end)")

            else:
                Print(1, 'E ...while material shader parsing!')
                return None, None
        else:
            if preprocessed_stderr is None:
                print('...no CgFX data found')
            else:
                print('ERROR - Preprocess of CgFX file failed: "%s"' % str(preprocessed_stderr))
            return None, None
    else:
        Print(1, 'E Invalid CgFX filepath %r!' % str(cgfx_filepath).replace("\\", "/"))
        return None, None
    return output, vertex_data


def strip_preinfo(string):
    """Takes a string and returns it without leading info text in brackets if present.
    Otherwise it returns the same string."""
    # print('  > strip_preinfo...')
    while string.startswith("("):
        string = string.split(")", 1)[1].strip()
    return string


def cgfx_rec_from_compiled(material, look, cgfx_data, cgfx_vertex_data, clear_records=False):
    """Takes recompiled and parsed CgFX data and write them to Material Look record."""


    ## NOTE: To clear records (clear_records) is probably never needed!
    if clear_records: cr_msg = "clear records"
    else: cr_msg = "DON'T clear records"
    print('  > cgfx_rec_from_compiled... (%s)' % cr_msg)


    ## PRINT DEBUG TABLE PRINT...
    # utils.print_matlook_info(material, look, cgfx_data, "cgfx_rec_from_compiled (1)")

    ## SAVE PREVIOUS CgFX RECORD NAMES AND THEIR VALUES OR CLEAR ALL CgFX DATA OF ACTUAL MATERIAL LOOK...
    older_cgfx_record = {}
    # if clear_records:
    #     material.scs_cgfx_looks[look].cgfx_data.clear()
    for rec in material.scs_cgfx_looks[look].cgfx_data:
        older_cgfx_record[rec.name] = material.scs_cgfx_looks[look].cgfx_data[rec.name].value
    # print('  older_cgfx_record (S):\n%s' % str(older_cgfx_record))

    ## CLEAR CGFX DATA SORTER...
    material.scs_cgfx_looks[look].cgfx_sorter.clear()

    ## STORE CGFX EFFECT NAME IN ACTUAL MATERIAL LOOK...
    material.scs_props.mat_cgfx_effect_name = cgfx_data['effect_name']['value']

    ## GET UI NAME FROM CGFX DATA...
    def get_ui_name(item):
        if cgfx_data['entries'][item]['t_list']['UIName']['type'] == 'string':
            ui_name = cgfx_data['entries'][item]['t_list']['UIName']['value']
        else:
            ui_name = str(cgfx_data['entries'][item]['t_list']['UIName']['value'])
        return ui_name

    ## GO OVER ALL COMPILED CgFX DATA ITEMS...
    for index, item in enumerate(cgfx_data['entries']):

        ## CHECK IF THE ITEM IS ENABLED IN UI...
        ui_item_hide = False
        if 'UIWidget' in cgfx_data['entries'][item]['t_list']:
            if cgfx_data['entries'][item]['t_list']['UIWidget']['value'] == 'None':
                if cgfx_data['entries'][item]['t_list']['UIWidget']['value'] == 'None':
                    ui_item_hide = True

        item_var_name = item
        # print('  item_var_name: "%s"' % item_var_name)

        ## MAKE CGFX DATA SORTER RECORD...
        cgfx_sorter = material.scs_cgfx_looks[look].cgfx_sorter.add()
        cgfx_sorter.name = item_var_name[5:]
        cgfx_sorter.index = int(item_var_name[5:8])

        ## CHECK IF THE ITEM IS DEFINE...
        is_define = 0
        update_function = "store_cgfx_data"
        if 'is_define' in cgfx_data['entries'][item]:
            if cgfx_data['entries'][item]['is_define']:
                update_function = "update_cgfx_data"
                is_define = 1

        # print(' %i - %s' % (int(item_var_name[5:8]), item_var_name[9:]))

        if is_define:
            ui_name = ""

            ## BOOLEANS...
            if cgfx_data['entries'][item]['type'] == "bool":
                ui_name = get_ui_name(item)
                ui_description = strip_preinfo(ui_name + " (Boolean)")
                prop_type = "bool"

            ## ENUMS 1...
            if cgfx_data['entries'][item]['type'] == "int": ## NOTE: "int" means "enum" here...
                ui_name = get_ui_name(item)
                ui_description = strip_preinfo(ui_name + " (Enumeration)")
                prop_type = "enum"

            ## CREATE CGFX DATA ITEMS ("DEFINES")...
            if item_var_name[9:] in material.scs_cgfx_looks[look].cgfx_data:
                cgfx_item = material.scs_cgfx_looks[look].cgfx_data[item_var_name[9:]]
                if item_var_name[9:] in older_cgfx_record:
                    cgfx_item.value = older_cgfx_record.pop(item_var_name[9:], None)
            else:
                cgfx_item = material.scs_cgfx_looks[look].cgfx_data.add()
                cgfx_item.value = cgfx_data['entries'][item]['value']['value']
                cgfx_item.name = item_var_name[9:]
                cgfx_item.type = prop_type
                cgfx_item.hide = ui_item_hide
                cgfx_item.ui_name = ui_name
                cgfx_item.ui_description = ui_description
                cgfx_item.update_function = update_function

            ## ENUMS 2...
            if cgfx_data['entries'][item]['type'] == "int":   ## NOTE: "int" means "enum" here...
                cgfx_item.enum_items = cgfx_data['entries'][item]['t_list']['UIEnum']['value']

                # if cgfx_data['entries'][item]['t_list']['UIEnum']['type'] == 'string':
                #     enum_items = []
                #     for it in re.split(':', cgfx_data['entries'][item]['t_list']['UIEnum']['value']):
                #         if it:
                #             re_key = re.split('=', it)[1]
                #             re_value = re.split('=', it)[0]
                #             enum_items.append((re_key, re_value, ""))
                # else:
                #     print('ERROR!!! - Enum of non-string type!')
        else:

            ## FLOATS...
            if cgfx_data['entries'][item]['type'] == "float":
                ui_name = get_ui_name(item)
                value = cgfx_data['entries'][item]['value']['value']
                ui_description = strip_preinfo(ui_name + " (Float number)")
                prop_type = "float"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))

            ## FLOATS 2...
            elif cgfx_data['entries'][item]['type'] == "float2":
                ui_name = get_ui_name(item)
                numbers = cgfx_data['entries'][item]['value']['value']

                value = str('(' + numbers[0] + ', ' + numbers[1] + ')')
                ui_description = strip_preinfo(ui_name + " (Two float numbers)")
                prop_type = "float2"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))

            ## FLOATS 3...
            elif cgfx_data['entries'][item]['type'] == "float3":
                ui_name = get_ui_name(item)

                numbers = cgfx_data['entries'][item]['value']['value']

                if 'Type' in cgfx_data['entries'][item]['t_list']:
                    # print('numbers: %s' % str(numbers))
                    multiply = 1.0
                    for val in numbers:
                        if float(val) > multiply:
                            multiply = val
                    if multiply > 1.0:
                        norm_numbers = []
                        for val in numbers:
                            norm_numbers.append(val / multiply)
                        value = str('(' + norm_numbers[0] + ', ' + norm_numbers[1] + ', ' + norm_numbers[2] + ', ' + multiply + ')')
                    else:
                        value = str('(' + numbers[0] + ', ' + numbers[1] + ', ' + numbers[2] + ', 1.0)')
                    if cgfx_data['entries'][item]['t_list']['Type']['value'] == 'Color':
                        ui_description = strip_preinfo(ui_name + " (Color)")
                        prop_type = "color"
                else:
                    value = str('(' + numbers[0] + ', ' + numbers[1] + ', ' + numbers[2] + ')')
                    ui_description = strip_preinfo(ui_name + " (Three float numbers)")
                    prop_type = "float3"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))

            ## SAMPLERS 2D...
            elif cgfx_data['entries'][item]['type'] == "sampler2D":
                ui_name = get_ui_name(item)
                value = cgfx_data['entries'][item]['value']['value']
                ui_description = strip_preinfo(ui_name + " (Sampler2D)")
                prop_type = "sampler2D"
                if value == "sampler_state":
                    value = bpy.data.worlds[0].scs_globals.scs_project_path + os.sep + "*.*"
                else:
                    print(' UNHANDLED CASE - "NON-sampler_state" sampler2D - %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))
                    value = bpy.data.worlds[0].scs_globals.scs_project_path + os.sep + "*.*"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))

            ## SAMPLER CUBES...
            elif cgfx_data['entries'][item]['type'] == "samplerCUBE":
                ui_name = get_ui_name(item)
                value = cgfx_data['entries'][item]['value']['value']
                if value == "sampler_state":
                    value = bpy.data.worlds[0].scs_globals.scs_project_path + os.sep + "*.*"
                ui_description = strip_preinfo(ui_name + " (SamplerCUBE)")
                prop_type = "samplerCUBE"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))

            ## TEXTURES...
            elif cgfx_data['entries'][item]['type'] == "texture":
                #ui_description = strip_preinfo(ui_name + " (texture)")
                prop_type = "texture"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))
                continue

            ## STRINGS...
            elif cgfx_data['entries'][item]['type'] == "string":
                # ui_description = strip_preinfo(ui_name + " (String)")
                prop_type = "string"
                # print(' %i %s:\t%s = %s' % (int(item_var_name[5:8]), item_var_name[9:], ui_name, value))
                if cgfx_data['entries'][item]['t_list']:
                    export_link = cgfx_data['entries'][item]['value']['value']
                    export_tag = cgfx_data['entries'][item]['t_list']['Name']['value']
                    export_format = cgfx_data['entries'][item]['t_list']['Type']['value']
                    print('  %s <-- "%s" (%s)' % (export_link, export_tag, export_format))
                    # export_links[export_link] = (export_tag, export_format)
                continue
            else:
                print(' UNHANDLED DATA TYPE "%s" (%i) %s' % (cgfx_data['entries'][item]['type'], int(item_var_name[5:8]), item_var_name[9:]))
                continue

            ## CREATE ITEMS ("NON-DEFINES")...
            if item_var_name[9:] in material.scs_cgfx_looks[look].cgfx_data:
                cgfx_item = material.scs_cgfx_looks[look].cgfx_data[item_var_name[9:]]
                if item_var_name[9:] in older_cgfx_record:
                    cgfx_item.value = older_cgfx_record.pop(item_var_name[9:], None)
            else:
                cgfx_item = material.scs_cgfx_looks[look].cgfx_data.add()
                cgfx_item.value = value
                cgfx_item.name = item_var_name[9:]
                cgfx_item.type = prop_type
                cgfx_item.hide = ui_item_hide
                cgfx_item.ui_name = ui_name
                cgfx_item.ui_description = ui_description
                cgfx_item.update_function = update_function

            continue

    ## DELETE UNUSED CgFX SHADER RECORDS FROM MATERIAL LOOK
    # print('  older_cgfx_record (E):\n%s' % str(older_cgfx_record))
    # if clear_records:
    if 0:
        for rec in older_cgfx_record:
            for item_i, item in enumerate(material.scs_cgfx_looks[look].cgfx_data):
                # if item.name.endswith(rec):
                if item.name == rec:
                    material.scs_cgfx_looks[look].cgfx_data.remove(older_cgfx_record[item_i])

    ## PRINT DEBUG TABLE PRINT...
    # utils.print_matlook_info(material, look, cgfx_data, "cgfx_rec_from_compiled (2)")

    ## CgFX VERTEX DATA

    ## SAVE PREVIOUS CgFX VERTEX RECORD NAMES AND THEIR VALUES OR CLEAR ALL CgFX VERTEX DATA OF ACTUAL MATERIAL LOOK...
    older_cgfx_vertex_record = {}
    if clear_records:
        material.scs_cgfx_looks[look].cgfx_vertex_data.clear()
    for rec in material.scs_cgfx_looks[look].cgfx_vertex_data:
        older_cgfx_vertex_record[rec.name] = material.scs_cgfx_looks[look].cgfx_vertex_data[rec.name].value
    # print('  older_cgfx_vertex_record (S):\n%s' % str(older_cgfx_vertex_record))

    ## CLEAR CGFX VERTEX DATA SORTER...
    material.scs_cgfx_looks[look].cgfx_vertex_sorter.clear()

    ## GO OVER ALL COMPILED CgFX VERTEX DATA ITEMS...
    for index, item in enumerate(cgfx_vertex_data):
        prop_item_name = str("cgfx_" + item)
        # print(' ** prop_item_name: %s' % prop_item_name)

        ## MAKE CGFX VERTEX DATA SORTER RECORD...
        cgfx_vertex_sorter = material.scs_cgfx_looks[look].cgfx_vertex_sorter.add()
        cgfx_vertex_sorter.name = str(str(index).rjust(3, "0") + "_" + item)
        cgfx_vertex_sorter.index = index

        ## CREATE CGFX VERTEX DATA ITEMS...
        if prop_item_name in material.scs_cgfx_looks[look].cgfx_vertex_data:
            cgfx_vertex_item = material.scs_cgfx_looks[look].cgfx_vertex_data[prop_item_name]
            if prop_item_name in older_cgfx_vertex_record:
                cgfx_vertex_item.value = older_cgfx_vertex_record.pop(prop_item_name, None)
        else:
            cgfx_vertex_item = material.scs_cgfx_looks[look].cgfx_vertex_data.add()
            cgfx_vertex_item.value = item
            cgfx_vertex_item.name = prop_item_name
            cgfx_vertex_item.type = "vertex_shader_map"
            cgfx_vertex_item.hide = False
            ui_name = item.replace("_", " ").title()
            cgfx_vertex_item.ui_name = ui_name
            cgfx_vertex_item.ui_description = str(ui_name + " (Vertex shader map)")
            cgfx_vertex_item.update_function = "store_cgfx_data"


def cgfx_rec_copy(material, source_look, target_look):
    """Make a copy of all records from one Material Look to another.
    If target Look doesn't exists, it is created."""
    if target_look not in material.scs_cgfx_looks:
        new_look = material.scs_cgfx_looks.add()
        new_look.name = target_look
    else:
        material.scs_cgfx_looks[target_look].cgfx_data.clear()
        material.scs_cgfx_looks[target_look].cgfx_sorter.clear()
        material.scs_cgfx_looks[target_look].cgfx_vertex_data.clear()
        material.scs_cgfx_looks[target_look].cgfx_vertex_sorter.clear()

    ## COPY ALL CGFX DATA RECORDS...
    for rec in material.scs_cgfx_looks[source_look].cgfx_data:
        new_rec = material.scs_cgfx_looks[target_look].cgfx_data.add()
        new_rec.name = rec.name
        new_rec.ui_name = rec.ui_name
        new_rec.ui_description = rec.ui_description
        new_rec.type = rec.type
        new_rec.value = rec.value
        new_rec.update_function = rec.update_function
        new_rec.hide = rec.hide
        new_rec.enabled = rec.enabled
        new_rec.enum_items = rec.enum_items
        new_rec.define = rec.define

    ## COPY ALL CGFX DATA SORTER RECORDS...
    for rec in material.scs_cgfx_looks[source_look].cgfx_sorter:
        new_rec = material.scs_cgfx_looks[target_look].cgfx_sorter.add()
        new_rec.name = rec.name

    ## COPY ALL CGFX VERTEX DATA RECORDS...
    for rec in material.scs_cgfx_looks[source_look].cgfx_vertex_data:
        new_rec = material.scs_cgfx_looks[target_look].cgfx_vertex_data.add()
        new_rec.name = rec.name
        new_rec.ui_name = rec.ui_name
        new_rec.ui_description = rec.ui_description
        new_rec.type = rec.type
        new_rec.value = rec.value
        new_rec.update_function = rec.update_function
        new_rec.hide = rec.hide
        new_rec.enabled = rec.enabled

    ## COPY ALL CGFX VERTEX DATA SORTER RECORDS...
    for rec in material.scs_cgfx_looks[source_look].cgfx_vertex_sorter:
        new_rec = material.scs_cgfx_looks[target_look].cgfx_vertex_sorter.add()
        new_rec.name = rec.name


def register_cgfx_ui(material, look):
    """Reads CgFX data from Material Look and generate UI elements."""
    print('  > register_cgfx_ui...')
    print('  actual look: %r (register_cgfx_ui())' % look)

# ## FIXME: All created UI items remain in the memory until Blender quits.
# ## FIXME: If already created item is recreated, it has the original value, not the value from new data.
# ## FIXME: Following code tries to change it, but I still don't know how to use "RemoveProperty"!
# ## DELETE PREVIOUS UI ITEMS...
#     try:
#         for item in bpy.context.screen.scs_cgfx_ui.__locals__:
#             if item.startswith("cgfx_"):
#                 print('item to delete: %s' % item)
#                 ## <bpy_struct, MaterialCgFXUI("")>
#                 RemoveProperty(MaterialCgFXUI(""), item.name)
#     except AttributeError:
#         print('   > NO "scs_cgfx_ui" in delete items (AttributeError)')

## UNREGISTER CgFX UI...
    try:
        # print('   > try to unregister_cgfx_ui...')
        unregister_cgfx_ui()
        # print('   > ...done')
    except AttributeError:
        print('   > NO "scs_cgfx_ui" (AttributeError)')

    all_values = {}

    class MaterialCgFXUI(bpy.types.PropertyGroup):
        """Dynamically created CgFX UI."""

        @staticmethod ## ?
        def update_cgfx_data(context):
            """Update function called by "defines" (flavors)."""
            print('  > update_cgfx_data...')
            if not bpy.data.worlds[0].scs_globals.config_update_lock:
                store_cgfx_settings_in_material_look()
                material = bpy.context.active_object.active_material
                look = utils.get_actual_look()
                output, vertex_data = recompile_cgfx_shader(material, look)
                register_cgfx_ui(material, look)
            else:
                print('  > ...locked')
            return None

        @staticmethod ## ?
        def store_cgfx_data(context):
            """Update function called by "non-defines" (no flavors)."""
            # print('  > store_cgfx_data...')
            if not bpy.data.worlds[0].scs_globals.config_update_lock:
                store_cgfx_settings_in_material_look()
            # else:
            #     print('  > ...locked')
            return None

## CREATE UI ITEMS...
        wt_enum_values = []
        wt_enum_index = 0
        for item in material.scs_cgfx_looks[look].cgfx_data:
            # print(' -- ITEM %r: %s' % (item.name, item.value))
            prop_item_name = str("cgfx_" + item.name)

            if item.hide is False:
## BOOL
                if item.type == "bool":
                    # print(' -- bool ITEM:   "%s" - %s' % (item.name, item.value))
                    if item.value == "true":
                        value = True
                    else:
                        value = False
                    exec('''%s = BoolProperty(name="%s", description="%s", default=%s, update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = value
## ENUM
                elif item.type == "enum":
                    # print(' -- enum ITEM:   "%s" - %s' % (item.name, item.value))
                    enum_items = []
                    for it in re.split(':', item.enum_items):
                        if it:
                            re_key = re.split('=', it)[1]
                            re_value = re.split('=', it)[0]
                            enum_items.append((re_key, re_value, ""))
                    exec('''%s = EnumProperty(name="%s", description="%s", items=(%s), default='%s', update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, enum_items, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = str("'" + item.value + "'")
## FLOAT
                elif item.type == "float":
                    # print(' -- float ITEM:  "%s" - %s' % (item.name, item.value))
                    exec('''%s = FloatProperty(name="%s", description="%s", options={'HIDDEN'}, subtype='UNSIGNED', default=%s, update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = float(item.value)
## FLOAT2
                elif item.type == "float2":
                    # print(' -- float2 ITEM: "%s" - %s' % (item.name, item.value))
                    exec('''%s = FloatVectorProperty(name="%s", description="%s", options={'HIDDEN'}, subtype='NONE', min=0, max=1, size=2, default=%s, update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    value_split = re.split(', ', item.value[1:-1])
                    all_values[prop_item_name] = (float(value_split[0]), float(value_split[1]))
## FLOAT3
                elif item.type == "float3":
                    # print(' -- float3 ITEM: "%s" - %s' % (item.name, item.value))
                    exec('''%s = FloatVectorProperty(name="%s", description="%s", options={'HIDDEN'}, subtype='NONE', min=0, max=1, default=%s, update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    value_split = re.split(', ', item.value[1:-1])
                    all_values[prop_item_name] = (float(value_split[0]), float(value_split[1]), float(value_split[2]))
## COLOR
                elif item.type == "color":
                    # print(' -- float3 ITEM: "%s" - %s' % (item.name, item.value))
                    value_split = re.split(', ', item.value[1:-1])
                    color_values = (float(value_split[0]), float(value_split[1]), float(value_split[2]))
                    exec('''%s = FloatVectorProperty(name="%s", description="%s", options={'HIDDEN'}, subtype='COLOR', min=0, max=1, default=%s, update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, str(color_values), item.update_function))
                    exec('''%s = FloatProperty(name="%s", description="%s", options={'HIDDEN'}, subtype='UNSIGNED', default=%s, update=%s)''' % (str(prop_item_name + "_mtplr"), str(item.ui_name + " (multiplier)"), str(item.ui_description[:-1] + " multiplier)"), value_split[3], item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = color_values
                    all_values[str(prop_item_name + "_mtplr")] = float(value_split[3])
## SAMPLER2D
                elif item.type == "sampler2D":
                    # print(' -- sampler2D ITEM: "%s" - %s' % (item.name, item.value))
                    exec('''%s = StringProperty(name="%s", description="%s", maxlen=0, options={'HIDDEN'}, subtype='FILE_PATH', default='%s', update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = str('"' + item.value + '"')
## SAMPLERCUBE
                elif item.type == "samplerCUBE":
                    # print(' -- samplerCUBE ITEM: "%s" - %s' % (item.name, item.value))
                    exec('''%s = StringProperty(name="%s", description="%s", maxlen=0, options={'HIDDEN'}, subtype='FILE_PATH', default='%s', update=%s)''' % (prop_item_name, item.ui_name, item.ui_description, item.value, item.update_function))
                    wt_enum_values.append((str(wt_enum_index), prop_item_name, str(str(wt_enum_index) + " " + prop_item_name), 'LIBRARY_DATA_DIRECT', wt_enum_index), )
                    wt_enum_index += 1
                    all_values[prop_item_name] = str('"' + item.value + '"')

## PRINTOUTS...
        # print(str(wt_enum_values))
        # for val in wt_enum_values:
        #     print('\t\tval: %s' % str(val))

        # def set_wt_default(self, context):
        #     return wt_enum_values[0]

        # print('wt_enum_values: %s' % str(wt_enum_values))
        if len(wt_enum_values) > 0:
            wt_enum = EnumProperty(
                    name="Write Through",
                    description="Write the value through all the Looks",
                    items=wt_enum_values,
                    default='0',
                    options={'HIDDEN'}
                    # update=display_info_update,
                    )
        else:
            wt_enum = EnumProperty(
                    name="Write Through",
                    description="Write the value through all the Looks",
                    items=(('0', "0", "0", '0', 0),),
                    default='0',
                    options={'HIDDEN'}
                    )

    # for item in all_values:
    #     print('      val.: %s  %s' % (str(item), type(item)))

    class MaterialCgFXVertexUI(bpy.types.PropertyGroup):
        for item in material.scs_cgfx_looks[look].cgfx_vertex_data:
            # print(' -- ITEM %r: %s' % (item.name, item.value))
            exec('''%s = StringProperty(name="%s", description="%s", maxlen=0, options={'HIDDEN'}, subtype='NONE', default='%s')''' % (item.name, item.ui_name, item.ui_description, item.value))

    # print('Going to register "MaterialCgFXUI"...')
    bpy.utils.register_class(MaterialCgFXUI)
    # print('..."MaterialCgFXUI" registered')
    # print('Going to register "MaterialCgFXVertexUI"...')
    bpy.utils.register_class(MaterialCgFXVertexUI)
    # print('..."MaterialCgFXVertexUI" registered')

    # bpy.types.Scene.scs_cgfx_ui = PointerProperty(
    bpy.types.Screen.scs_cgfx_ui = PointerProperty(
        name="Material CgFX UI",
        type=MaterialCgFXUI,
        description="Generated UI elements for CgFX shader settings",
    )

    # bpy.types.Scene.scs_cgfx_vertex_ui = PointerProperty(
    bpy.types.Screen.scs_cgfx_vertex_ui = PointerProperty(
        name="Material CgFX Vertex UI",
        type=MaterialCgFXVertexUI,
        description="Generated UI elements for CgFX vertex shader settings",
    )

## POPULATE UI WITH SAVED VALUES (FROM CgFX MATERIAL-LOOK RECORD)...
    # print('all_values: %s' % str(all_values))
    if len(all_values) > 0: update_ui_props_from_matlook_record(all_values)


def unregister_cgfx_ui():
    # del bpy.types.Scene.scs_cgfx_ui
    del bpy.types.Screen.scs_cgfx_ui
    # del bpy.types.Scene.scs_cgfx_vertex_ui
    del bpy.types.Screen.scs_cgfx_vertex_ui
