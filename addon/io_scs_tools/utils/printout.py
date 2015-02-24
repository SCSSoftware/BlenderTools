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

error_messages = []
warning_messages = []


def lprint(string, values=(), report_errors=0, report_warnings=0):
    """Handy printout function with alert levels and more fancy stuff.

    :param string: Message string which will be printed.
    :type string: str
    :param values: Tuple of values, which complements the message string
    :type values: tuple
    :param report_errors: 0 - don't print anything, but store the errors; 1 - print error summary; -1 - clear stored errors
    :type report_errors: int
    :param report_warnings: 0 - don't print anything, but store the warnings; 1 - print warning summary; -1 - clear stored warnings
    :type report_warnings: int
    """
    from io_scs_tools.utils import get_scs_globals as _get_scs_globals

    dump_level = int(_get_scs_globals().dump_level)

    global error_messages, warning_messages
    prech = ''
    if string is not "":
        while string[0] in '\n\t':
            prech += string[0]
            string = string[1:]
        if string[0] == 'E':
            message = str(prech + 'ERROR\t-  ' + string[2:] % values)
            print(message)
            error_messages.append(message.strip('\n'))
            # raise Exception('ERROR - ' + string[2:])
        if string[0] == 'W':
            message = str(prech + 'WARNING\t-  ' + string[2:] % values)
            warning_messages.append(message.strip('\n'))
            if dump_level >= 1:
                print(message)
        if dump_level >= 2:
            if string[0] == 'I':
                print(prech + 'INFO\t-  ' + string[2:] % values)
        if dump_level >= 3:
            if string[0] == 'D':
                print(prech + 'DEBUG\t-  ' + string[2:] % values)
        if dump_level >= 4:
            if string[0] == 'S':
                print(prech + string[2:] % values)
        if string[0] not in 'EWIDS':
            print(prech + '!!! UNKNOWN MESSAGE SIGN !!! - "' + string + '"' % values)

    # ERROR REPORTS
    if report_errors == 1 and error_messages:
        print('\n\nERROR SUMMARY:\n==============')
        for message_i, message in enumerate(error_messages):
            print(message)
    elif report_errors == -1:
        error_messages = []

    # WARNING REPORTS
    if report_warnings == 1 and warning_messages:
        print('\n\nWARNING SUMMARY:\n================')
        for message_i, message in enumerate(warning_messages):
            print(message)
    elif report_warnings == -1:
        warning_messages = []

    # ERROR AND WARNING REPORTS
    title = ""
    text = "\n"
    if report_errors == 1 and error_messages:
        title = "ERRORS"

        if len(error_messages) == 1:
            text += "An ERROR occurred during process!\n"
        else:
            text += "%i ERRORS occurred during process!\n" % len(error_messages)
        error_messages = []

    if report_warnings == 1 and warning_messages:
        if title != "":
            title += " AND "
        title += "WARNINGS DURING PROCESS"

        if len(warning_messages) == 1:
            text += "A WARNING is printed to the console!\n"
        else:
            text += "%i WARNINGS were printed to the console!\n" % len(warning_messages)
        warning_messages = []

    if title != "":
        text += "Please checkout the printings."
        bpy.ops.wm.show_warning_message('INVOKE_DEFAULT', title=title, message=text, is_modal=True)


def print_section(section, ind):
    print('%sSEC.: "%s"' % (ind, section.type))
    ind = ind + ind
    for prop in section.props:
        print('%sProp: %s' % (ind, prop))
    for data in section.data:
        print('%sdata: %s' % (ind, data))
    for sec in section.sections:
        print_section(sec, ind)
    return


def print_group(group_name, data_name, data_string="data"):
    data_groups_scs_data = bpy.data.groups.get(group_name)
    data_length = len(data_groups_scs_data[data_name])
    data_list = [x for x in data_groups_scs_data[data_name]]
    print('%s (%i): %s' % (data_string, data_length, str(data_list)))


def print_group_values(group_name, data_name):
    data_groups_scs_data = bpy.data.groups.get(group_name)
    for item_i, item in enumerate(data_groups_scs_data[data_name]):
        print('  value[%i]: "%s" --> "%s"' % (item_i, str(data_groups_scs_data[data_name][item][0]), str(data_groups_scs_data[data_name][item][1])))


def handle_unused_arg(filename, func_name, unused_name, value):
    """Function for reporting arguments which are not used currently but we should preserve them
    if there will be a need to incorporate them in Blender Tools

    :param filename: file where function is
    :type filename: str
    :param func_name: function name where argument is used
    :type func_name: str
    :param unused_name: name of unused argument or variable
    :type unused_name: str
    :param value: value which is presenting unused argument or variable
    :type value: object
    """
    message = "S Unused argument reported: %s:%s -> %s(%s)..."
    lprint(message, (filename, func_name, unused_name, str(value)))


'''
def print_dict(data_dict):
    """Helper function for printing of dictionaries."""
    print('')
    for key in data_dict:
        value = data_dict[key]
        print('%r = %s' % (str(key), str(value)))
    print('')


def print_used_slots(start_node, end_node):
    if start_node.scs_props.locator_prefab_np_curve1_out:
        print('start_node slot 1: "%s"' % str(start_node.scs_props.locator_prefab_np_curve1_out))
    if start_node.scs_props.locator_prefab_np_curve2_out:
        print('start_node slot 2: "%s"' % str(start_node.scs_props.locator_prefab_np_curve2_out))
    if start_node.scs_props.locator_prefab_np_curve3_out:
        print('start_node slot 3: "%s"' % str(start_node.scs_props.locator_prefab_np_curve3_out))
    if start_node.scs_props.locator_prefab_np_curve4_out:
        print('start_node slot 4: "%s"' % str(start_node.scs_props.locator_prefab_np_curve4_out))

    if end_node.scs_props.locator_prefab_np_curve1_in:
        print('end_node slot 1: "%s"' % str(end_node.scs_props.locator_prefab_np_curve1_in))
    if end_node.scs_props.locator_prefab_np_curve2_in:
        print('end_node slot 2: "%s"' % str(end_node.scs_props.locator_prefab_np_curve2_in))
    if end_node.scs_props.locator_prefab_np_curve3_in:
        print('end_node slot 3: "%s"' % str(end_node.scs_props.locator_prefab_np_curve3_in))
    if end_node.scs_props.locator_prefab_np_curve4_in:
        print('end_node slot 4: "%s"' % str(end_node.scs_props.locator_prefab_np_curve4_in))


def print_container(container):
    """Test data container printout into console."""
    ind = '  '
    if container:
        for section in container:
            print('SEC.: "%s"' % section.type)
            for prop in section.props:
                print('%sProp: %s' % (ind, prop))
            for data in section.data:
                print('%sdata: %s' % (ind, data))
            for sec in section.sections:
                print_section(sec, ind)
        print('')
    else:
        print('WARNING - print_container(): No data to print!')


def print_sii_container(container):
    """Test data container printout into console."""
    print('')
    if container:
        for section in container:
            print('"%s" : %r' % (section.type, section.id))
            for prop in section.props:
                print('  %s: %r' % (prop, section.props[prop]))
        print('')
    else:
        print('WARNING - print_sii_container(): No data to print!')


def print_matlook_info(material, actual_look, output, identification_text):

    class MatLookTable(object):
        def __init__(self, key, data_type, index, re="/", co="/", ui="/"):  # NOTE: "os.sep" instead of "/" ???
            self.key = key
            self.type = data_type
            self.index = index
            self.re = re
            self.co = co
            self.ui = ui

# -------------------------------------------- ##

    matlook_table_data = {}

# -------------------------------------------- ##
    # get info from material look record...
    # print('\nget info from material look record...')

    re_present = 1
    if len(material.scs_cgfx_looks[actual_look].cgfx_data) != 0:
        for i in material.scs_cgfx_looks[actual_look].cgfx_data:
            # print('re: "%s"' % str(i.name))
            if i.type == "bool":
                index = 999
                for item in material.scs_cgfx_looks[actual_look].cgfx_sorter:
                    # if item.name.endswith(i.name[9:]):
                    if item.name.endswith(i.name):
                        index = int(item.name[:3])
                # matlook_table_rec = MatLookTable(i.name[9:], i.type, int(i.name[5:8]))
                # matlook_table_rec = MatLookTable(i.name[9:], i.type, index)
                matlook_table_rec = MatLookTable(i.name, i.type, index)
                if i.hide:
                    matlook_table_rec.re = "H"
                else:
                    # if i.bool:
                    if i.value == "true":
                        matlook_table_rec.re = "I"
                    elif i.value == "false":
                        matlook_table_rec.re = "O"
                    else:
                        matlook_table_rec.re = "?"
                # matlook_table_data[i.name[9:]] = matlook_table_rec
                matlook_table_data[i.name] = matlook_table_rec
    else:
        re_present = 0

# -------------------------------------------- ##
    # get info from compiled...
    # print('get info from compiled...')

    if output:
        for i in output['entries']:
            # print('co: "%s"' % i)
            # print('co type: "%s"' % output['entries'][i]['type'])
            if output['entries'][i]['type'] == "bool":
                # print('co: "%s"' % i)
                if 'UIWidget' in output['entries'][i]['t_list'] and output['entries'][i]['t_list']['UIWidget']['value'] == 'None':
                    if i[9:] in matlook_table_data:
                        matlook_table_data[i[9:]].co = "H"
                    else:
                        matlook_table_data[i[9:]] = MatLookTable(i[9:], output['entries'][i]['type'], int(i[5:8]), co="H")
                        # matlook_table_data[i[9:]].co = "H"
                else:
                    if i[9:] in matlook_table_data:
                        if output['entries'][i]['value']['value'] == "true":
                            matlook_table_data[i[9:]].co = "I"
                        elif output['entries'][i]['value']['value'] == "false":
                            matlook_table_data[i[9:]].co = "O"
                        else:
                            pass
                    else:
                        matlook_table_rec = MatLookTable(i[9:], output['entries'][i]['type'], int(i[5:8]))
                        if output['entries'][i]['value']['value'] == "true":
                            matlook_table_rec.co = "I"
                        elif output['entries'][i]['value']['value'] == "false":
                            matlook_table_rec.co = "O"
                        else:
                            pass
                        matlook_table_data[i[9:]] = matlook_table_rec
    else:
        for item in matlook_table_data:
            matlook_table_data[item].co = "-"

# -------------------------------------------- ##
    # get info from UI...
    # print('get info from UI...')

    try:
        for i in bpy.context.screen.scs_cgfx_ui.__locals__:
            if i.startswith("cgfx_"):
                index = 999
                for item in material.scs_cgfx_looks[actual_look].cgfx_sorter:
                    # if item.name.endswith(i.name[9:]):
                    if str(item.name).endswith(i[5:]):
                        index = int(item.name[:3])
                value = getattr(bpy.context.screen.scs_cgfx_ui, i)
                # print('ui: "%s" = %s (%s)' % (str(i), str(value), str(type(value))[8:-2]))
                if type(value) == bool:
                    if i[5:] in matlook_table_data:
                        if value is True:
                            matlook_table_data[i[5:]].ui = "I"
                        elif value is False:
                            matlook_table_data[i[5:]].ui = "O"
                    else:
                        # matlook_table_rec = MatLookTable(i[9:], str(type(value))[8:-2], int(i[5:8]))
                        matlook_table_rec = MatLookTable(i[5:], str(type(value))[8:-2], index)
                        if value is True:
                            matlook_table_rec.ui = "I"
                        elif value is False:
                            matlook_table_rec.ui = "O"
                        else:
                            pass
                        # matlook_table_data[i[9:]] = matlook_table_rec
                        matlook_table_data[i[5:]] = matlook_table_rec
                else:
                    pass
                    # print('ui: "%s" (NON BOOL)' % str(i)[9:])
    except AttributeError:
        for item in matlook_table_data:
            matlook_table_data[item].ui = "-"

# -------------------------------------------- ##

    if not re_present:
        for item in matlook_table_data:
            matlook_table_data[item].re = "-"

# -------------------------------------------- ##
    # PRINT MAT-LOOK TABLE...
    print('|= %s' % identification_text)
    # print('...PRINT MAT-LOOK TABLE...')
    # print('  num ind   C R G   name')

    matlook_table_data_sort = []
    for item in matlook_table_data:
        matlook_table_data_sort.append(str(str(matlook_table_data[item].index).rjust(4, '0') + matlook_table_data[item].key))

    # for item_i, item in enumerate(matlook_table_data):
    for item_i, index_key in enumerate(sorted(matlook_table_data_sort)):
        rec = matlook_table_data[index_key[4:]]
        print('  %s %s   %s %s %s   "%s"' % (str(item_i).rjust(3, ' '), str(rec.index).rjust(3, ' '), rec.co, rec.re, rec.ui, rec.key))

    # print('...END OF MAT-LOOK TABLE')
'''