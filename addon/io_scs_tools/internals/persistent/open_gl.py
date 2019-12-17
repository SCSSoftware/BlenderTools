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

# Copyright (C) 2019: SCS Software

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.internals.connections.wrappers import collection as _connections_wrapper
from io_scs_tools.internals.open_gl import core as _open_gl_core
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

_LAST_SCENE = "last_scene"
"""Key for caching last scene, so we are able to detect scene change."""

_cache = {
    _LAST_SCENE: None
}


class _DelayedUpdate:
    """Class for employing delayed update of coonections recalculation and buffers refill, implemented with new timers API."""

    __objects_to_refill = []
    """Storing objects on which buffers refill should be executed, when delayed update is engaged.
    NOTE: We don't use functools as propsed in API examples, as then we can not unregister our function anymore.
    """

    @staticmethod
    def __update_internal__():
        """Execute delayed update by updating connections and re-filling the drawing buffers.

        NOTE: should be used as timer function.

        :return: float if function should be called again, or None to unregister this function from timers
        :rtype: float | None
        """
        _connections_wrapper.update_for_redraw()

        _open_gl_core.fill_buffers(_DelayedUpdate.__objects_to_refill)

        # trigger redraw as in some cases draw may not be called,
        # due the fact we just executed delayed update from timer
        _view3d_utils.tag_redraw_all_view3d()

        return None

    @staticmethod
    def schedule(delay, object_list):
        """Schedules delayed update of connections and buffers refill.

        :param delay: when update should be executed in seconds
        :type delay: float
        :param object_list: list of object to use on scheduled update delay
        :type object_list: list
        """
        assert delay > 0.0

        # check if already registered, then remove it first
        if bpy.app.timers.is_registered(_DelayedUpdate.__update_internal__):
            bpy.app.timers.unregister(_DelayedUpdate.__update_internal__)

        # now reschedule
        _DelayedUpdate.__objects_to_refill = object_list
        bpy.app.timers.register(_DelayedUpdate.__update_internal__, first_interval=delay)


@persistent
def post_undo(scene):
    """OpenGL drawing on post undo. We need it as post depsgraph handler is not called after executing undo.

    :param scene: current scene
    :type scene: bpy.type.Scene
    """
    post_depsgraph(scene)


@persistent
def post_redo(scene):
    """OpenGL drawing on post redo. We need it as post depsgraph handler is not called after executing undo.

    :param scene: current scene
    :type scene: bpy.type.Scene
    """
    post_depsgraph(scene)


@persistent
def post_frame_change(scene):
    """OpenGL drawing on post frame change. We need it for:
     1. Scene switch detection
     2. During animation playback as post depsgraph handler is not called as last.

    :param scene: current scene
    :type scene: bpy.type.Scene
    """

    do_update = False

    # on scene change we need to refill our buffers, as different objects will be displayed
    if scene != _cache[_LAST_SCENE]:
        _cache[_LAST_SCENE] = scene
        do_update = True
    # take over during animation playback, where late update should be initiated each time objects are updated
    elif bpy.context.screen and bpy.context.screen.is_animation_playing and bpy.context.view_layer.depsgraph.id_type_updated('OBJECT'):
        do_update = True

    if do_update and not _get_scs_globals().import_in_progress:
        _connections_wrapper.invalidate()

        # in case of playback we don't want to slow down FPS, empty buffers and wait for delayed update to do it's job
        _open_gl_core.fill_buffers([])

        # NOTE: while animation is playing context.visible_objects for some reason
        # returns only visible objects of current 3d view if user mouse is over 3d view.
        # To prevent wrong object selection in that case we are rather sendin all view layer objects.
        _DelayedUpdate.schedule(0.1, bpy.context.view_layer.objects.values())


@persistent
def post_depsgraph(scene):
    """OpenGL drawing on post depsgraph. Main hookup to update connections and re-fill positions and colors of custom 3d elements.

    :param scene: current scene
    :type scene: bpy.type.Scene
    """
    scs_globals = _get_scs_globals()

    # during animation playback, leave everything up to post frame change
    screen = bpy.context.screen
    if screen and screen.is_animation_playing:
        return

    # nothing we are interested in was updated, means we don't have to refill our buffers
    depsgraph = bpy.context.view_layer.depsgraph
    if depsgraph and not depsgraph.id_type_updated('OBJECT') and not depsgraph.id_type_updated('SCENE'):
        # OBJECT not updated, none of the objects was transformed or hidden
        # SCENE not updated, collections did not get hidden or shown in outliner
        return

    _connections_wrapper.invalidate()

    # if post graph get's called with global context only (e.g. blend data changes in timers),
    # then screen is not availabe nor is visible_objects variable, in that case use all view layer objects
    if bpy.context.screen:
        objects_list = bpy.context.visible_objects
    else:
        objects_list = bpy.context.view_layer.objects.values()

    # during import always re-schedule delayed update, so once import ends refill will be triggered
    if scs_globals.import_in_progress:
        _DelayedUpdate.schedule(0.1, objects_list)
        return

    # if optimized do late connections update and refill, otherwise prepare connections for filling into buffers
    if scs_globals.optimized_connections_drawing:
        _DelayedUpdate.schedule(0.1, objects_list)
    else:
        _connections_wrapper.update_for_redraw()

    # fill buffers in any case, when connections are optimized, only locators will be filled to buffers,
    # otherwise everything will be filled.
    _open_gl_core.fill_buffers(objects_list)
