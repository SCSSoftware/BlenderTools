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
from math import pi
from bpy.props import IntProperty
from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env_ng as _add_env_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import compose_lighting_ng as _compose_lighting_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import lighting_evaluator_ng as _lighting_evaluator_ng
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories
from io_scs_tools.utils.printout import lprint


class SCS_TOOLS_OT_SetupLighting(bpy.types.Operator):
    bl_label = "Setup Lighting"
    bl_idname = "world.scs_tools_setup_lighting"
    bl_description = "Setups lighting according to given sun profile."

    __static_last_profile_i = -1
    """Static variable saving index of sun profile currently used in lighting scene.
    Variable is used when operator is called with sun profile index -1,
    to determinate from which sun profile light data should be taken while seting up lighting scene."""

    sun_profile_index: IntProperty(default=-1)

    def execute(self, context):
        lprint('D ' + self.bl_label + "...")

        scs_globals = _get_scs_globals()
        scs_inventories = _get_scs_inventories()

        # get sun profile index depending on input
        if self.sun_profile_index == -1:

            # if sun profile index is not given (equal to -1) then try to retrieve last used profile index
            # from static variable; otherwise use currently selected from list in UI
            if SCS_TOOLS_OT_SetupLighting.__static_last_profile_i != -1:
                sun_profile_i = SCS_TOOLS_OT_SetupLighting.__static_last_profile_i
            else:
                sun_profile_i = scs_globals.sun_profiles_active

        else:
            sun_profile_i = self.sun_profile_index

        # validate sun profile index
        if sun_profile_i < 0 or sun_profile_i > len(scs_inventories.sun_profiles):
            lprint("E Using active sun profile failed!")
            return {'FINISHED'}

        # update static variable for sun profile index
        SCS_TOOLS_OT_SetupLighting.__static_last_profile_i = sun_profile_i

        sun_profile_item = scs_inventories.sun_profiles[sun_profile_i]
        """:type: io_scs_tools.properties.world.GlobalSCSProps.SunProfileInventoryItem"""

        # convert elevation into rotation direction vector for diffuse and specular lamps
        # NOTE: this is not exact as in game but should be sufficient for representation
        elevation_avg = (sun_profile_item.low_elevation + sun_profile_item.high_elevation) / 2
        elevation_direction = 1 if sun_profile_item.sun_direction == 1 else -1
        directed_lamps_rotation = (
            elevation_direction * (pi / 2 - (pi * elevation_avg / 180)),  # elevation
            0,
            pi * scs_globals.lighting_scene_east_direction / 180  # current BT user defined east direction
        )

        # 1. create lighting scene
        if _LIGHTING_consts.scene_name not in bpy.data.scenes:
            lighting_scene = bpy.data.scenes.new(_LIGHTING_consts.scene_name)
        else:
            lighting_scene = bpy.data.scenes[_LIGHTING_consts.scene_name]

        # 2. create sun lamp empty and setup it's direction according elevation average

        if _LIGHTING_consts.sun_lamp_name in bpy.data.objects:
            lamp_obj = bpy.data.objects[_LIGHTING_consts.sun_lamp_name]
        else:
            lamp_obj = bpy.data.objects.new(_LIGHTING_consts.sun_lamp_name, None)

        if lamp_obj.name not in lighting_scene.collection.objects:
            lighting_scene.collection.objects.link(lamp_obj)

        # lamp_obj.hide_viewport = True
        lamp_obj.rotation_euler = directed_lamps_rotation

        # 3. set ambient, diffuse and specular environment values
        _lighting_evaluator_ng.set_ambient_light(sun_profile_item.ambient)
        _lighting_evaluator_ng.set_diffuse_light(sun_profile_item.diffuse)
        _lighting_evaluator_ng.set_specular_light(sun_profile_item.specular)
        _lighting_evaluator_ng.set_light_direction(lamp_obj)

        _compose_lighting_ng.set_additional_ambient_col(sun_profile_item.ambient)

        # 5. search for AddEnv node group and setup coefficient for environment accordingly
        _add_env_ng.set_global_env_factor(sun_profile_item.env * sun_profile_item.env_static_mod)

        return {'FINISHED'}


class SCS_TOOLS_OT_DisableLighting(bpy.types.Operator):
    bl_label = "Disable Lighting"
    bl_idname = "world.scs_tools_disable_lighting"
    bl_description = "Disables SCS lighting, reseting lighting to generic one in camera space."

    def execute(self, context):
        lprint('D ' + self.bl_label + "...")

        old_scene = None
        if context.scene and context.scene != _LIGHTING_consts.scene_name:
            old_scene = context.scene

        # if scs lighting scene is not present in blend file anymore, we are done
        if _LIGHTING_consts.scene_name not in bpy.data.scenes:
            return {'FINISHED'}

        # firstly remove the lighting scene
        override = context.copy()
        override['window'] = context.window_manager.windows[-1]
        override['scene'] = bpy.data.scenes[_LIGHTING_consts.scene_name]
        bpy.ops.scene.delete(override, 'INVOKE_DEFAULT')

        if _LIGHTING_consts.sun_lamp_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[_LIGHTING_consts.sun_lamp_name], do_unlink=True)

        # reset light direction & ambient, diffuse and specular environment values
        _lighting_evaluator_ng.reset_lighting_params()
        _compose_lighting_ng.reset_lighting_params()
        _add_env_ng.reset_lighting_params()

        # while we delete one scene blender might/will select first available as current,
        # so we have to force our screen to be using old scene again
        if old_scene and context.window:
            context.window.scene = old_scene

        return {'FINISHED'}


classes = (
    SCS_TOOLS_OT_DisableLighting,
    SCS_TOOLS_OT_SetupLighting,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
