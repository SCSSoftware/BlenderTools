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

import os

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals.callbacks import open_gl as _open_gl_callback
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.internals.connections.wrappers import group as _connections_group_wrapper
from io_scs_tools.utils import icon as _icons_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


@persistent
def initialise_scs_dict(scene):
    """Parts and Variants data initialisation (persistent).

    Things which this function does:
    1. copies all the settings to current world
    2. checks object identities
    3. updates shaders presets path and reloads them

    Cases when it should be run:
    1. Blender startup -> SCS tools needs to configured
    2. Opening .blend file -> because all the configs needs to be moved to current world
    3. addon reloading and enable/disable -> for SCS tools this is the same as opening Blender

    :param scene: Current Blender Scene
    :type scene: bpy.types.Scene
    """

    # SCREEN CHECK...
    if bpy.context.screen:
        lprint("I >Initialization of SCS scene")

        # NOTE: covers: start-up, reload, enable/disable and it should be immidiately removed
        # from handlers as soon as it's executed for the first time
        if initialise_scs_dict in bpy.app.handlers.scene_update_post:
            lprint("I ---> Removing 'scene_update_post' handler...")
            bpy.app.handlers.scene_update_post.remove(initialise_scs_dict)

        # INITIALIZE CUSTOM CONNECTIONS DRAWING SYSTEM
        _connections_group_wrapper.init()

        # TRIGGER RELOAD OF CUSTOM ICONS
        _icons_utils.invalidate()

        # USE SETTINGS FROM CONFIG...
        # NOTE: Reapplying the settings from config file to the currently opened Blender file datablock.
        # The thing is, that every Blend file holds its own copy of SCS Global Settings from the machine on which it got saved.
        # The SCS Global Settings needs to be overwritten upon each file load to reflect the settings from local config file,
        # but also upon every SCS Project Base Path change.
        _config_container.apply_settings()

        # GLOBAL PATH CHECK...
        if _get_scs_globals().scs_project_path != "":
            if not os.path.isdir(_get_scs_globals().scs_project_path):
                lprint("\nW The Project Path %r is NOT VALID!\n\tPLEASE SELECT A VALID PATH TO THE PROJECT BASE FOLDER.\n",
                       (_get_scs_globals().scs_project_path,))

        # CREATE PREVIEW MODEL LIBRARY
        _preview_models.init()

        # ADD DRAW HANDLERS
        _open_gl_callback.enable(mode=bpy.context.scene.scs_props.drawing_mode)