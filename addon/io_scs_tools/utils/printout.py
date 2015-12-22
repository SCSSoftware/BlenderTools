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

dev_error_messages = []
error_messages = []
dev_warning_messages = []
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

    # CLEAR ERROR AND WARNING STACK IF REQUESTED
    if report_errors == -1:
        error_messages = []
    if report_warnings == -1:
        warning_messages = []

    # ERROR AND WARNING REPORTS
    title = ""
    text = ""
    if report_errors == 1 and error_messages:

        # print error summary
        print('\n\nERROR SUMMARY:\n================')
        text += '\nERROR SUMMARY:\n================\n'
        printed_messages = []
        for message_i, message in enumerate(error_messages):
            if message not in printed_messages:
                printed_messages.append(message)
                print(message)
                text += message + "\n"

        # create dialog title and message
        title = "ERRORS"

        if dump_level == 5:
            dev_error_messages.extend(error_messages)

        error_messages = []

    if report_warnings == 1 and warning_messages:

        if dump_level > 0:

            # print warning summary
            print('\n\nWARNING SUMMARY:\n================')
            text += '\nWARNING SUMMARY:\n================\n'
            printed_messages = []
            for message_i, message in enumerate(warning_messages):
                # print only unique messages
                if message not in printed_messages:
                    printed_messages.append(message)
                    print(message)
                    text += message + "\n"

            # create dialog title and message
            if title != "":
                title += " AND "
            title += "WARNINGS DURING PROCESS"

        if dump_level == 5:
            dev_warning_messages.extend(warning_messages)

        warning_messages = []

    if title != "":
        bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', title=title, message=text)
        return True
    else:
        return False


def dev_lprint():
    """Prints out whole stack of errors and warnings. Stack is cleared afterwards.
    """
    global dev_error_messages, dev_warning_messages

    print('\n\nDEV ERROR SUMMARY:\n==============')
    printed_messages = []
    for message_i, message in enumerate(dev_error_messages):
        if message not in printed_messages:
            printed_messages.append(message)
            print(message)

    if len(printed_messages) == 0:
        print("NO ERRORS :D")

    dev_error_messages = []

    print('\n\nDEV WARNING SUMMARY:\n==============')
    printed_messages = []
    for message_i, message in enumerate(dev_warning_messages):
        if message not in printed_messages:
            printed_messages.append(message)
            print(message)

    if len(printed_messages) == 0:
        print("NO WARNINGS :D")

    dev_warning_messages = []


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
