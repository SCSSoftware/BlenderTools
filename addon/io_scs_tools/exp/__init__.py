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

from io_scs_tools.exp import pia
from io_scs_tools.exp import pic
from io_scs_tools.exp import pip
from io_scs_tools.exp import pis
from io_scs_tools.exp import pix

from io_scs_tools.utils import object as _object
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def batch_export(operator_instance, init_obj_list, exclude_switched_off=True, menu_filepath=None):
    """This function calls other sorting functions and depending on the resulting output
    dictionary it exports all available 'SCS Game Objects' into specified locations.

    :param operator_instance: operator from within this function is called (used for report)
    :type operator_instance: bpy.types.Operator
    :param init_obj_list: initial object list which should be exported
    :type init_obj_list: tuple of Blender objects
    :param exclude_switched_off: exlude game object wich root is excplicity exluded by property
    :type exclude_switched_off: bool
    :param menu_filepath: filepath used from menu export
    :type menu_filepath: str
    """

    lprint("", report_errors=-1, report_warnings=-1)  # Clear the 'error_messages' and 'warning_messages'
    game_objects_dict = _object.sort_out_game_objects_for_export(init_obj_list)
    if exclude_switched_off:
        game_objects_dict = _object.exclude_switched_off(game_objects_dict)

    if game_objects_dict:
        scs_game_objects_exported = []

        # GET GLOBAL FILE PATH
        scs_project_path = _get_scs_globals().scs_project_path
        is_blend_file_within_base = bpy.data.filepath != "" and bpy.data.filepath.startswith(scs_project_path)
        default_export_path = bpy.context.scene.scs_props.default_export_filepath
        # if not set try to use Blender filepath
        if default_export_path == "" and is_blend_file_within_base:
            global_filepath = os.path.dirname(bpy.data.filepath)
        else:
            global_filepath = os.path.join(scs_project_path, default_export_path.strip(os.sep * 2))

        for root_object in game_objects_dict:
            game_object_list = game_objects_dict[root_object]

            # GET CUSTOM FILE PATH
            custom_filepath = None
            if root_object.scs_props.scs_root_object_allow_custom_path:
                scs_root_export_path = root_object.scs_props.scs_root_object_export_filepath
                # if not set try to use Blender filepath
                if scs_root_export_path == "" and is_blend_file_within_base:
                    custom_filepath = os.path.dirname(bpy.data.filepath)
                    print("Custom filepath for Blend file!")
                else:
                    custom_filepath = os.path.join(scs_project_path, scs_root_export_path.strip(os.sep * 2))
                    print("Custom filepath:", custom_filepath)

            # MAKE FINAL FILEPATH
            if menu_filepath:
                filepath = menu_filepath
                filepath_message = "Export path selected in file browser:\n\t   \"" + filepath + "\""
            elif custom_filepath:
                filepath = custom_filepath
                filepath_message = "Custom export path used for \"" + root_object.name + "\" is:\n\t   \"" + filepath + "\""
            else:
                filepath = global_filepath
                filepath_message = "Default export path used for \"" + root_object.name + "\":\n\t   \"" + filepath + "\""

            # print(' filepath (%r):\n%r' % (root_object.name, str(filepath)))
            scs_project_path = _get_scs_globals().scs_project_path
            if os.path.isdir(filepath) and filepath.startswith(scs_project_path) and scs_project_path != "":
                pix.export(filepath, root_object, game_object_list)
                scs_game_objects_exported.append("> \"" + root_object.name + "\" exported to: '" + filepath + "'")
                # if result != {'FINISHED'}: return {'CANCELLED'}
            else:
                if filepath:
                    message = (
                        "No valid export path found!\n\t   " +
                        "Export path does not exists or it's not inside SCS Project Base Path.\n\t   " +
                        "SCS Project Base Path:\n\t   \"" + scs_project_path + "\"\n\t   " +
                        filepath_message
                    )
                else:
                    message = "No valid export path found! Please check \"SCS Project Base Path\" first."
                lprint('E ' + message)
                operator_instance.report({'ERROR'}, message.replace("\t", "").replace("   ", ""))
                return {'CANCELLED'}

        lprint("\nI Export procces completed, summaries are printed below!", report_errors=True, report_warnings=True)
        if len(scs_game_objects_exported) > 0:
            print("\n\nEXPORTED GAME OBJECTS:\n" + "=" * 22)
            for scs_game_object_export_message in scs_game_objects_exported:
                print(scs_game_object_export_message)
        else:
            message = "Nothing to export! Please set at least one 'SCS Root Object'."
            lprint('E ' + message)
            operator_instance.report({'ERROR'}, message)
            return {'CANCELLED'}
    else:
        message = "Please create at least one 'SCS Root Object' and parent your objects to it in order to export a 'SCS Game Object'!\n" \
                  "(For more information, please refer to 'SCS Blender Tools' documentation.)"
        lprint('E ' + message)
        operator_instance.report({'ERROR'}, message)
        return {'CANCELLED'}

    return {'FINISHED'}