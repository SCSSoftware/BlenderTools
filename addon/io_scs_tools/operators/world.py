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
from math import pi
from time import time
from bpy.props import BoolProperty, IntProperty, StringProperty, CollectionProperty
from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env as _add_env_node_group
from io_scs_tools.internals.shaders.eut2.std_node_groups import compose_lighting as _compose_lighting
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


class UseSunProfile(bpy.types.Operator):
    bl_label = "Use Sun Profile"
    bl_idname = "world.scs_use_sun_profile"
    bl_description = "Setups lighting according to this sun profile."

    __static_last_profile_i = -1
    """Static variable saving index of sun profile currently used in lighting scene.
    Variable is used when operator is called with sun profile index -1,
    to determinate from which sun profile light data should be taken while seting up lighting scene."""

    sun_profile_index = IntProperty(default=-1)
    skip_background_set = BoolProperty(default=False)

    def execute(self, context):
        lprint('D ' + self.bl_label + "...")

        scs_globals = _get_scs_globals()

        # get sun profile index depending on input
        if self.sun_profile_index == -1:

            # if sun profile index is not given (equal to -1) then try to retrieve last used profile index
            # from static variable; otherwise use currently selected from list in UI
            if UseSunProfile.__static_last_profile_i != -1:
                sun_profile_i = UseSunProfile.__static_last_profile_i
            else:
                sun_profile_i = scs_globals.sun_profiles_inventory_active

        else:
            sun_profile_i = self.sun_profile_index

        # validate sun profile index
        if sun_profile_i < 0 or sun_profile_i > len(scs_globals.sun_profiles_inventory):
            lprint("E Using active sun profile failed!")
            return {'FINISHED'}

        # update static variable for sun profile index
        UseSunProfile.__static_last_profile_i = sun_profile_i

        sun_profile_item = scs_globals.sun_profiles_inventory[sun_profile_i]
        """:type: io_scs_tools.properties.world.GlobalSCSProps.SunProfileInventoryItem"""

        # convert elevation into rotation direction vector for diffuse and specular lamps
        # NOTE: this is not exact as in game but should be sufficient for representation
        elevation_avg = (sun_profile_item.low_elevation + sun_profile_item.high_elevation) / 2
        elevation_direction = 1 if sun_profile_item.sun_direction == 1 else -1
        directed_lamps_rotation = (
            0,
            elevation_direction * (pi / 2 - (pi * elevation_avg / 180)),  # elevation
            pi * scs_globals.lighting_scene_east_direction / 180  # current BT user defined east direction
        )

        # 1. create lighting scene
        if _LIGHTING_consts.scene_name not in bpy.data.scenes:
            lighting_scene = bpy.data.scenes.new(_LIGHTING_consts.scene_name)
        else:
            lighting_scene = bpy.data.scenes[_LIGHTING_consts.scene_name]

        lighting_scene.layers = [True] * 20

        # 2. create ambient lights
        _compose_lighting.set_additional_ambient_col(sun_profile_item.ambient * sun_profile_item.ambient_hdr_coef)
        for ambient_lamp_name, ambient_lamp_direction, ambient_lamp_factor in _LIGHTING_consts.ambient_lamps:

            if ambient_lamp_name in bpy.data.lamps:
                lamp_data = bpy.data.lamps[ambient_lamp_name]
            else:
                lamp_data = bpy.data.lamps.new(ambient_lamp_name, "HEMI")

            lamp_data.type = "HEMI"
            lamp_data.use_specular = False
            lamp_data.use_diffuse = True
            lamp_data.energy = sun_profile_item.ambient_hdr_coef * ambient_lamp_factor
            lamp_data.color = sun_profile_item.ambient

            if ambient_lamp_name in bpy.data.objects:
                lamp_obj = bpy.data.objects[ambient_lamp_name]
                lamp_obj.data = lamp_data
            else:
                lamp_obj = bpy.data.objects.new(ambient_lamp_name, lamp_data)

            lamp_obj.hide = True
            lamp_obj.rotation_euler = ambient_lamp_direction
            lamp_obj.rotation_euler[2] = directed_lamps_rotation[2]
            lamp_obj.layers = [True] * 20  # enable it on all layers

            if lamp_obj.name not in lighting_scene.objects:
                lighting_scene.objects.link(lamp_obj)

        # 3. create sun lamp for diffuse and setup it's direction according elevation average
        if _LIGHTING_consts.diffuse_lamp_name in bpy.data.lamps:
            lamp_data = bpy.data.lamps[_LIGHTING_consts.diffuse_lamp_name]
        else:
            lamp_data = bpy.data.lamps.new(_LIGHTING_consts.diffuse_lamp_name, "SUN")

        lamp_data.type = "SUN"
        lamp_data.use_specular = False
        lamp_data.use_diffuse = True
        lamp_data.energy = sun_profile_item.diffuse_hdr_coef
        lamp_data.color = _convert_utils.linear_to_srgb(sun_profile_item.diffuse)

        if _LIGHTING_consts.diffuse_lamp_name in bpy.data.objects:
            lamp_obj = bpy.data.objects[_LIGHTING_consts.diffuse_lamp_name]
            lamp_obj.data = lamp_data
        else:
            lamp_obj = bpy.data.objects.new(_LIGHTING_consts.diffuse_lamp_name, lamp_data)

        lamp_obj.hide = True
        lamp_obj.rotation_euler = directed_lamps_rotation
        lamp_obj.layers = [True] * 20  # enable it on all layers

        if lamp_obj.name not in lighting_scene.objects:
            lighting_scene.objects.link(lamp_obj)

        # 4. create sun lamp for specular and setup it's direction according elevation average
        if _LIGHTING_consts.specular_lamp_name in bpy.data.lamps:
            lamp_data = bpy.data.lamps[_LIGHTING_consts.specular_lamp_name]
        else:
            lamp_data = bpy.data.lamps.new(_LIGHTING_consts.specular_lamp_name, "SUN")

        lamp_data.type = "SUN"
        lamp_data.use_specular = True
        lamp_data.use_diffuse = False
        lamp_data.energy = sun_profile_item.specular_hdr_coef
        lamp_data.color = _convert_utils.linear_to_srgb(sun_profile_item.specular)

        if _LIGHTING_consts.specular_lamp_name in bpy.data.objects:
            lamp_obj = bpy.data.objects[_LIGHTING_consts.specular_lamp_name]
            lamp_obj.data = lamp_data
        else:
            lamp_obj = bpy.data.objects.new(_LIGHTING_consts.specular_lamp_name, lamp_data)

        lamp_obj.hide = True
        lamp_obj.rotation_euler = directed_lamps_rotation
        lamp_obj.layers = [True] * 20  # enable it on all layers

        if lamp_obj.name not in lighting_scene.objects:
            lighting_scene.objects.link(lamp_obj)

        # 5. search for AddEnv node group and setup coefficient for environment accordingly
        _add_env_node_group.set_global_env_factor(sun_profile_item.env * sun_profile_item.env_static_mod)

        # 6. set lighting scene as background scene of current scene if skipping wasn't requested in input params
        if not self.skip_background_set:

            if context.scene and context.scene != lighting_scene:
                context.scene.background_set = lighting_scene
            else:
                lprint("E Lighting scene created but not used, as currently there is no active scene!")

        return {'FINISHED'}


class RemoveSCSLightingFromScene(bpy.types.Operator):
    bl_label = "Switch Off SCS Lighting in Current Scene"
    bl_idname = "world.scs_disable_lighting_in_scene"
    bl_description = "Disables SCS lighting in current scene, giving you ability to setup your own lighting."

    def execute(self, context):
        lprint('D ' + self.bl_label + "...")

        old_scene = None
        if context.scene and context.scene.background_set and context.scene.background_set.name == _LIGHTING_consts.scene_name:
            old_scene = context.scene
            old_scene.background_set = None

        # if scs lighting scene is not present in blend file anymore, we are done
        if _LIGHTING_consts.scene_name not in bpy.data.scenes:
            return {'FINISHED'}

        # otherwise check if current scene was the last using SCS lighting,
        # if so then make sure to cleanup lamp objects and delete the scene
        used_counter = 0
        for scene in bpy.data.scenes:

            if scene.name == _LIGHTING_consts.scene_name:
                continue

            if scene.background_set == bpy.data.scenes[_LIGHTING_consts.scene_name]:
                used_counter += 1

        if used_counter == 0:

            # firstly remove the lighting scene
            override = {
                'window': context.window,
                'screen': context.screen,
                'blend_data': context.blend_data,
                'scene': bpy.data.scenes[_LIGHTING_consts.scene_name],
                'region': None,
                'area': None,
                'edit_object': None,
                'active_object': None,
                'selected_objects': None,
            }
            bpy.ops.scene.delete(override, 'INVOKE_DEFAULT')

            # now gather all lamp objects names
            lamp_names = [_LIGHTING_consts.diffuse_lamp_name, _LIGHTING_consts.specular_lamp_name]
            for lamp_name, lamp_dir, lamp_factor in _LIGHTING_consts.ambient_lamps:
                lamp_names.append(lamp_name)

            # lastly delete blend objects and lamps
            for lamp_name in lamp_names:

                if lamp_name in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects[lamp_name], do_unlink=True)

                if lamp_name in bpy.data.lamps:
                    bpy.data.lamps.remove(bpy.data.lamps[lamp_name], do_unlink=True)

            # while we delete one scene blender might/will select first available as current,
            # so we have to force our screen to be using old scene again
            if old_scene and context.screen:
                context.screen.scene = old_scene

        return {'FINISHED'}


class SCSPathsInitialization(bpy.types.Operator):
    bl_label = ""
    bl_description = "Initializes SCS Blender Tools filepaths asynchronously with proper reporting in 3D view."
    bl_idname = "world.scs_paths_initialization"

    DUMP_LEVEL = 3
    """Constant for log level index according in SCS Globals, on which operator should printout extended report."""

    # Static running variables
    __timer = None
    """Timer instance variable. We use timer to initilize paths gradually one by one."""
    __last_time = None
    """Used for time tracking on each individual path initialization."""
    __path_in_progress = False
    """Used as flag for indicating path being processed. So another execute method call shouldn't be triggered."""
    __static_paths_count = 0
    """Static variable holding number of all paths that had to be processed. Used for reporting progress eg. 'X of Y paths done'."""
    __static_paths_done = 0
    """Static variable holding number of already processed paths. Used for reporting progress eg. 'X of Y paths done'."""
    __static_running_instances = 0
    """Used for indication of already running operator."""

    # Static data storage
    __static_message = ""
    """Static variable holding printout extended message. This message used only if dump level is high enough."""
    __static_paths_list = []
    """Static variable holding CollectionProperty with entries of Filepath class, defining paths that needs initialization.
    Processed paths are removed on the fly.
    """
    __static_callbacks = []
    """Static variable holding list of callbacks that will be executed once operator is finished or cancelled.
    """

    class Filepath(bpy.types.PropertyGroup):
        """
        Entry for file paths collection that should be set on SCS globals asynchronously inside SCSToolsInitialization operator.
        """
        name = StringProperty(description="Friendly name used for printouts.")
        attr = StringProperty(description="Name of the property in SCSGlobalsProps class.")
        path = StringProperty(description="Actual file/dir path that should be applied to the property.")

    paths_list = CollectionProperty(
        type=Filepath,
        description=
        """
        List of paths that should be initialized, used only for passing filepaths data to operator.
        During operator invoke this list extends static paths list. Accessing paths via static variable
        is needed for multiple operator invoking from different places. As this enables us having common
        up to date list for processing paths in order and none of it stays unproperly processed.
        """
    )

    @staticmethod
    def is_running():
        """Tells if paths initialization is still in progress.

        :return: True if scs paths initialization is still in progress; False if none instances are running
        :rtype: bool
        """
        return SCSPathsInitialization.__static_running_instances > 0

    @staticmethod
    def append_callback(callback):
        """Appends given callback function to callback list. Callbacks are called once paths initialization is done.
        If operator is not running then False is returned and callback is not added to the list!
        NOTE: there is no check if given callback is already in list.

        :param callback: callback function without arguments
        :type callback: object
        :return: True if operator is running and callback is added to the list properly; False if callback won't be added and executed
        :rtype: bool
        """
        if SCSPathsInitialization.is_running():
            SCSPathsInitialization.__static_callbacks.append(callback)
            return True

        return False

    def __init__(self):
        SCSPathsInitialization.__static_running_instances += 1

    def __del__(self):
        if SCSPathsInitialization.__static_running_instances > 0:

            SCSPathsInitialization.__static_running_instances -= 1

        # if user disables add-on, destructor is called again, so cleanup timer and static variables
        if SCSPathsInitialization.__static_running_instances <= 0:

            SCSPathsInitialization.__static_message = ""
            SCSPathsInitialization.__static_paths_list = []
            SCSPathsInitialization.__static_callbacks = []

            if bpy.context and bpy.context.window_manager and self.__timer:
                wm = bpy.context.window_manager
                wm.event_timer_remove(self.__timer)

    def execute(self, context):

        # do not proceed if list is already empty
        if len(SCSPathsInitialization.__static_paths_list) <= 0:
            return {'FINISHED'}

        self.__path_in_progress = True

        # update message with current path and apply it
        SCSPathsInitialization.__static_message += "Initializing " + SCSPathsInitialization.__static_paths_list[0].name + "..."
        setattr(_get_scs_globals(), SCSPathsInitialization.__static_paths_list[0].attr, SCSPathsInitialization.__static_paths_list[0].path)
        SCSPathsInitialization.__static_paths_list.remove(0)  # remove just processed item
        SCSPathsInitialization.__static_message += " Done in %.2f s!\n" % (time() - self.__last_time)
        SCSPathsInitialization.__static_paths_done += 1

        # when executing last one, also print out hiding message
        if len(SCSPathsInitialization.__static_paths_list) == 0:
            SCSPathsInitialization.__static_message += "SCS Blender Tools are ready!"
            _view3d_utils.tag_redraw_all_view3d()

        self.__last_time = time()  # reset last time for next path

        self.__path_in_progress = False

        # if debug then report whole progress message otherwise print out condensed message
        if int(_get_scs_globals().dump_level) >= self.DUMP_LEVEL:
            message = SCSPathsInitialization.__static_message
            hide_controls = False
        else:
            message = "Paths and libraries initialization %s/%s ..." % (SCSPathsInitialization.__static_paths_done,
                                                                        SCSPathsInitialization.__static_paths_count)
            hide_controls = True
        bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', message=message, hide_controls=hide_controls, is_progress_message=True)

        return {'FINISHED'}

    def cancel(self, context):

        # reset static variables
        SCSPathsInitialization.__static_message = ""
        SCSPathsInitialization.__static_paths_list.clear()

        wm = context.window_manager
        wm.event_timer_remove(self.__timer)

        # report finished progress to 3d view report operator
        if int(_get_scs_globals().dump_level) < self.DUMP_LEVEL:
            bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', abort=True, is_progress_message=True)

        # when done, tag everything for redraw in the case some UI components
        # are reporting status of this operator
        _view3d_utils.tag_redraw_all_regions()

        # as last invoke any callbacks and afterwards delete them
        while len(SCSPathsInitialization.__static_callbacks) > 0:

            callback = SCSPathsInitialization.__static_callbacks[0]

            callback()
            SCSPathsInitialization.__static_callbacks.remove(callback)

    def modal(self, context, event):

        if event.type == "TIMER":  # process timer event

            if len(SCSPathsInitialization.__static_paths_list) <= 0:  # once no more paths to process abort it

                # NOTE: canceling has to be done in timer event.
                # Otherwise finishing operator with status 'FINISHED' eats event and
                # stops event in this operator and cancels action which user wanted to do.
                self.cancel(context)
                lprint("I Paths initialization done, deleting operator!")
                return {'FINISHED'}

            if not self.__path_in_progress:  # if not in progress then trigger execute and process next

                self.execute(context)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        SCSPathsInitialization.__static_paths_done = 0  # reset done paths counter as everything starts here

        # if another instance is running update static paths list with paths passed to this instance
        if SCSPathsInitialization.__static_running_instances > 1:

            # now fill up new paths to static inventory
            for filepath_prop in self.paths_list:

                # search for identical path in not yet processed paths list
                old_item = None
                for item in SCSPathsInitialization.__static_paths_list:
                    if item.attr == filepath_prop.attr:
                        old_item = item
                        break

                # if old item is found just reuse it instead of adding new item to list
                item = old_item if old_item else SCSPathsInitialization.__static_paths_list.add()
                item.name = filepath_prop.name
                item.attr = filepath_prop.attr
                item.path = filepath_prop.path

            # update paths counter to the current paths list length
            SCSPathsInitialization.__static_paths_count = len(SCSPathsInitialization.__static_paths_list)

            # cancel this instance if another instance is still running
            # (it can happen that previous operator was done until now as each operator runs asynchronously,
            # in that case we have to continue otherwise latest paths won't be  )
            if SCSPathsInitialization.__static_running_instances > 0:

                SCSPathsInitialization.__static_message = "Restarting initialization...\n\n"
                bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', message=SCSPathsInitialization.__static_message,
                                              hide_controls=True, is_progress_message=True)

                lprint("D Restarting initialization...!")
                return {'CANCELLED'}

        SCSPathsInitialization.__static_message = "Starting initialization...\n"
        bpy.ops.wm.show_3dview_report('INVOKE_DEFAULT', message=SCSPathsInitialization.__static_message,
                                      hide_controls=True, is_progress_message=True)

        SCSPathsInitialization.__static_paths_list = self.paths_list
        SCSPathsInitialization.__static_paths_count = len(self.paths_list)

        wm = context.window_manager
        self.__timer = wm.event_timer_add(0.2, context.window)
        self.__last_time = time()

        wm.modal_handler_add(self)
        lprint("I Paths initialization started...")
        return {'RUNNING_MODAL'}
