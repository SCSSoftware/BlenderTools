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

# Copyright (C) 2013-2019: SCS Software

import bpy
import os
from bpy.app.handlers import persistent
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback
from io_scs_tools.internals.callbacks import lighting_east_lock as _lighting_east_lock_callback
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.internals.connections.wrappers import collection as _connections_wrapper
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import info as _info_utils
from io_scs_tools.utils.printout import lprint


@persistent
def post_load(scene):
    """Initialize blender tools from handlers hooks.

    NOTE: Should be used only as load_post handler hook.
    :param scene: Blender scene
    :type scene: bpy.types.Scene
    """
    init_scs_tools()


def on_enable():
    """Initialize blender tools on addon enabling.

    NOTE: Should be used only as timer function on addon enabling.
    """

    # run until properly initialized
    if init_scs_tools():
        return None

    return 1.0


def init_scs_tools():
    """Parts and Variants data initialisation (persistent).

    Things which this function does:
    1. copies all the settings to current world
    2. checks object identities
    3. updates shaders presets path and reloads them

    Cases when it should be run:
    1. Blender startup -> SCS tools needs to configured
    2. Opening .blend file -> because all the configs needs to be moved to current world
    3. addon reloading and enable/disable -> for SCS tools this is the same as opening Blender
    """

    # SCREEN CHECK...
    if not hasattr(bpy.data, "worlds"):
        lprint("I Initialization abort, context incorrect ...")
        return False

    lprint("I Initialization of SCS scene, BT version: " + _info_utils.get_tools_version())

    # NOTE: covers: start-up, reload, enable/disable and it should be immediately removed
    # from handlers as soon as it's executed for the first time
    # if initialise_scs_dict in bpy.app.handlers.scene_update_post:
    #     bpy.app.handlers.scene_update_post.remove(initialise_scs_dict)

    # INITIALIZE CUSTOM CONNECTIONS DRAWING SYSTEM
    _connections_wrapper.init()

    # TODO: this should not be needed anymore, as we don't config locks shouldn't be saved in blend file anymore see: scs_globals.get_writtable_keys
    # release lock as user might saved blender file during engaged lock.
    # If that happens config lock property gets saved to blend file and if user opens that file again,
    # lock will be still engaged and no settings could be applied without releasing lock here.
    _config_container.release_config_lock()

    # USE SETTINGS FROM CONFIG...
    # NOTE: Reapplying the settings from config file to the currently opened Blender file datablock.
    # The thing is, that every Blend file holds its own copy of SCS Global Settings from the machine on which it got saved.
    # The SCS Global Settings needs to be overwritten upon each file load to reflect the settings from local config file,
    # but also upon every SCS Project Base Path change.
    _config_container.apply_settings(preload_from_blend=True)

    # GLOBAL PATH CHECK...
    if _get_scs_globals().scs_project_path != "":
        if not os.path.isdir(_get_scs_globals().scs_project_path):
            lprint("\nW The Project Path %r is NOT VALID!\n\tPLEASE SELECT A VALID PATH TO THE PROJECT BASE FOLDER.\n",
                   (_get_scs_globals().scs_project_path,))

    # CREATE PREVIEW MODEL LIBRARY
    _preview_models.init()

    # ADD DRAW HANDLERS
    _open_gl_callback.enable(mode=_get_scs_globals().drawing_mode)

    # ENABLE LIGHTING EAST LOCK HANDLER
    # Blender doesn't call update on properties when file is opened,
    # so in case lighting east was locked in saved blend file, we have to manually enable callback for it
    # On the other hand if user previously had east locked and now loaded the file without it,
    # again we have to manually disable callback.
    if _get_scs_globals().lighting_east_lock:
        _lighting_east_lock_callback.enable()
    else:
        _lighting_east_lock_callback.disable()

    # as last notify user if his Blender version is outdated
    if not _info_utils.is_blender_able_to_run_tools():

        message = "Your Blender version %s is outdated, all SCS Blender Tools functionalities were internally disabled.\n\t   " \
                  "Please update Blender before continue, minimal required version for SCS Blender Tools is: %s!"
        message = message % (_info_utils.get_blender_version()[0], _info_utils.get_required_blender_version())

        # first report error with blender tools printing system
        lprint("E " + message)

        # then disable add-on as it's not usable in the case Blender is out-dated
        bpy.ops.preferences.addon_disable(module="io_scs_tools")

        # and as last show warning message in the form of popup menu for user to see info about outdated Blender
        # As we don't have access to our 3D view report operator anymore,
        # we have to register our SCS_TOOLS_OT_ShowMessageInPopup class back and invoke it.
        from io_scs_tools.operators.wm import SCS_TOOLS_OT_ShowMessageInPopup
        bpy.utils.register_class(SCS_TOOLS_OT_ShowMessageInPopup)

        bpy.ops.wm.scs_tools_show_message_in_popup(context, 'INVOKE_DEFAULT',
                                                   is_modal=True,
                                                   title="SCS Blender Tools Initialization Problem",
                                                   message="\n\n" + message.replace("\t   ", "") + "\n\n",  # formatting for better visibility
                                                   width=580,  # this is minimal width to properly fit in given message
                                                   height=bpy.context.window.height if bpy.context and bpy.context.window else 200)

    return True
