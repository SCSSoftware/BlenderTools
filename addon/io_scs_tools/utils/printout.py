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
import atexit
from tempfile import NamedTemporaryFile


class _FileLogger:
    """File logging class wrapper.

    Class wrapping is needed manly for safety of log file removal
    after Blender is shut down.

    Registering fuction for atexit module makes sure than,
    file is deleted if Blender is closed normally.

    However file is not deleted if process is killed in Linux.
    On Windows, on the other hand, file gets deleted even if Blender
    is closed from Task Manager -> End Task/Process
    """
    __log_file = None

    def __init__(self):

        self.__log_file = NamedTemporaryFile(mode="w+", suffix=".log.txt", delete=True)

        # instead of destructor we are using delete method,
        # to close and consequentially delete log file
        atexit.register(self.delete)

    def delete(self):
        """Closes file and consiquentally deletes it as log file was created in that fashion.
        """

        # close file only if it's still exists in class variable
        if self.__log_file is not None:
            self.__log_file.close()
            self.__log_file = None

    def write(self, msg_object):
        """Writes message to the log file.

        :param msg_object: message to be written to file
        :type msg_object: object
        """

        self.__log_file.write(msg_object)

    def flush(self):
        """Flushes written content to file on disk."""

        self.__log_file.flush()

    def get_log(self):
        """Gets current content of temporary SCS BT log file,
        which was created at startup and is having log of BT session.

        :return: current content of log file as string
        :rtype: str
        """

        # firstly move to start of the file
        self.__log_file.seek(0)

        log = ""
        for line in self.__log_file.readlines():
            log += line.replace("\t   ", "\t\t   ")  # replace for Blender text editor to be aligned the same as in console

        return log


file_logger = _FileLogger()

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

    prech = ''
    if string is not "":
        while string[0] in '\n\t':
            prech += string[0]
            string = string[1:]

        message = None
        if string[0] == 'E':
            message = str(prech + 'ERROR\t-  ' + string[2:] % values)
            error_messages.append(message.strip('\n'))
            # raise Exception('ERROR - ' + string[2:])
        if string[0] == 'W':
            message = str(prech + 'WARNING\t-  ' + string[2:] % values)
            warning_messages.append(message.strip('\n'))
            if not dump_level >= 1:
                message = None
        if dump_level >= 2:
            if string[0] == 'I':
                message = str(prech + 'INFO\t-  ' + string[2:] % values)
        if dump_level >= 3:
            if string[0] == 'D':
                message = prech + 'DEBUG\t-  ' + string[2:] % values
        if dump_level >= 4:
            if string[0] == 'S':
                message = prech + string[2:] % values

        if message is not None:
            print(message)
            file_logger.write(message + "\n")

        if string[0] not in 'EWIDS':
            print(prech + '!!! UNKNOWN MESSAGE SIGN !!! - "' + string + '"' % values)

    # CLEAR ERROR AND WARNING STACK IF REQUESTED
    if report_errors == -1:
        error_messages.clear()
    if report_warnings == -1:
        warning_messages.clear()

    # ERROR AND WARNING REPORTS
    text = ""
    if report_errors == 1 and error_messages:

        # print error summary
        text += '\n\t   ERROR SUMMARY:\n\t   ================\n\t   '
        printed_messages = []
        for message_i, message in enumerate(error_messages):

            message = message.replace("ERROR\t-  ", "> ")
            message = message.replace("\n\t   ", "\n\t     ")

            # print out only unique error messages
            if message not in printed_messages:
                printed_messages.append(message)
                text += message + "\n\t   "

        text += "================\n"

        if dump_level == 5:
            dev_error_messages.extend(error_messages)

        error_messages.clear()

    if report_warnings == 1 and warning_messages:

        if dump_level > 0:

            # print warning summary
            text += '\n\t   WARNING SUMMARY:\n\t   ================\n\t   '
            printed_messages = []
            for message_i, message in enumerate(warning_messages):

                message = message.replace("WARNING\t-  ", "> ")
                message = message.replace("\n\t   ", "\n\t     ")

                # print only unique messages
                if message not in printed_messages:
                    printed_messages.append(message)
                    text += message + "\n\t   "

            text += "================\n"

        if dump_level == 5:
            dev_warning_messages.extend(warning_messages)

        warning_messages.clear()

    file_logger.flush()

    if text != "":
        print(text)
        file_logger.write(text + "\n")
        file_logger.flush()
        bpy.ops.wm.scs_tools_show_3dview_report('INVOKE_DEFAULT', message=text)

        # make sure to tag any 3D view for redraw so errors OpenGL drawing is triggered
        from io_scs_tools.utils.view3d import tag_redraw_all_view3d
        tag_redraw_all_view3d()

        return True
    else:
        return False


def get_log():
    """Gets current content of temporary SCS BT log file,
    which was created at startup and is having log of BT session.

    :return: current content of log file as string
    :rtype: str
    """
    return file_logger.get_log()


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
