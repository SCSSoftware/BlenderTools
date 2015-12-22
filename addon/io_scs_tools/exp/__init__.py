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
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def batch_export(operator_instance, init_obj_list, menu_filepath=None):
    """This function calls other sorting functions and depending on the resulting output
    dictionary it exports all available 'SCS Game Objects' into specified locations.

    :param operator_instance: operator from within this function is called (used for report)
    :type operator_instance: bpy.types.Operator
    :param init_obj_list: initial object list which should be exported
    :type init_obj_list: tuple of Blender objects
    :param menu_filepath: filepath used from menu export
    :type menu_filepath: str
    """

    lprint("", report_errors=-1, report_warnings=-1)  # Clear the 'error_messages' and 'warning_messages'
    game_objects_dict = _object_utils.sort_out_game_objects_for_export(init_obj_list)

    # exclude game objects that were manually omitted from export by property
    game_objects_dict = _object_utils.exclude_switched_off(game_objects_dict)

    if game_objects_dict:
        scs_game_objects_exported = []
        scs_game_objects_rejected = []

        global_filepath = _path_utils.get_global_export_path()

        for root_object in game_objects_dict:

            # update root object location to invoke update tagging on it and
            # then update scene to make sure all children objects will have all transforms up to date
            # NOTE: needed because Blender doesn't update objects on invisible layers on it's own
            root_object.location = root_object.location
            for scene in bpy.data.scenes:
                scene.update()

            game_object_list = game_objects_dict[root_object]

            # GET CUSTOM FILE PATH
            custom_filepath = _path_utils.get_custom_scs_root_export_path(root_object)

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

            scs_project_path = _get_scs_globals().scs_project_path
            if os.path.isdir(filepath) and _path_utils.startswith(filepath, scs_project_path) and scs_project_path != "":

                # EXPORT ENTRY POINT
                export_success = pix.export(filepath, root_object, game_object_list)

                if export_success:
                    scs_game_objects_exported.append("> \"" + root_object.name + "\" exported to: '" + filepath + "'")
                else:
                    scs_game_objects_rejected.append("> \"" + root_object.name + "\"")

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

        if not lprint("\nI Export procces completed, summaries are printed below!", report_errors=True, report_warnings=True):
            operator_instance.report({'INFO'}, "Export successfully completed!")
            bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', abort=True)  # abort 3d view reporting operator

        if len(scs_game_objects_exported) > 0:
            print("\n\nEXPORTED GAME OBJECTS (" + str(len(scs_game_objects_exported)) + "):\n" + "=" * 26)
            for scs_game_object_export_message in scs_game_objects_exported:
                print(scs_game_object_export_message)

        if len(scs_game_objects_rejected) > 0:
            print("\n\nREJECTED GAME OBJECTS (" + str(len(scs_game_objects_rejected)) + "):\n" + "=" * 26)
            for scs_game_object_export_message in scs_game_objects_rejected:
                print(scs_game_object_export_message)

        if len(scs_game_objects_exported) + len(scs_game_objects_rejected) == 0:
            message = "Nothing to export! Please set at least one 'SCS Root Object'."
            lprint('E ' + message)
            operator_instance.report({'ERROR'}, message)
            return {'CANCELLED'}
    else:
        message = "No 'SCS Root Object' present or all of them were manually exluded from export in their settings.\n\t   " \
                  "(For more information, please refer to 'SCS Blender Tools' documentation.)"
        lprint('E ' + message)
        operator_instance.report({'ERROR'}, message.replace("\n\t   ", "\n"))
        return {'CANCELLED'}

    return {'FINISHED'}
