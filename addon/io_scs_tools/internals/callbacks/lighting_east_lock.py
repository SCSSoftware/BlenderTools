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

# Copyright (C) 2017: SCS Software

import bpy
from math import pi
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals

_callback = {
    "handle": None,
    "initial_view_rotation": -1,
    "initial_lamp_rotation": 0
}


def _get_diffuse_and_specular_lamps_from_scs_lighting():
    if _LIGHTING_consts.scene_name not in bpy.data.scenes:
        return None, None

    lighting_scene = bpy.data.scenes[_LIGHTING_consts.scene_name]

    if _LIGHTING_consts.diffuse_lamp_name not in lighting_scene.objects:
        return None, None

    diffuse_lamp_obj = lighting_scene.objects[_LIGHTING_consts.diffuse_lamp_name]

    if _LIGHTING_consts.specular_lamp_name not in lighting_scene.objects:
        return None, None

    specular_lamp_obj = lighting_scene.objects[_LIGHTING_consts.specular_lamp_name]

    return diffuse_lamp_obj, specular_lamp_obj


def _lightning_east_lock_draw_callback(reset):
    # implicitly kill east lock draw callback if Blender has more 3d view spaces,
    # because in that case lights can not be properly rotated as no one knows which view should be used as active
    if not reset and _view3d_utils.has_multiple_view3d_spaces():
        disable()
        _get_scs_globals().lighting_east_lock = False
        _view3d_utils.tag_redraw_all_regions()
        return

    # 1. check lighting scene integrity and region data integrity and
    # finish callback if everything is not up and ready
    diffuse_lamp_obj, specular_lamp_obj = _get_diffuse_and_specular_lamps_from_scs_lighting()
    if diffuse_lamp_obj is None or specular_lamp_obj is None:
        return

    if reset:

        east_rotation = _get_scs_globals().lighting_scene_east_direction * pi / 180.0

    else:

        if not hasattr(bpy.context.region_data, "view_rotation"):
            return

        current_view_rot = bpy.context.region_data.view_rotation.to_euler('XYZ')
        current_view_z_rot = current_view_rot.y + current_view_rot.z  # because of axis flipping always combine y and z

        # 2. on first run just remember initial rotation and end callback
        if _callback["initial_view_rotation"] == -1:
            _callback["initial_lamp_rotation"] = diffuse_lamp_obj.rotation_euler[2]
            _callback["initial_view_rotation"] = current_view_z_rot
            return

        # 3. recalculate current east direction
        east_rotation = current_view_z_rot - _callback["initial_view_rotation"] + _callback["initial_lamp_rotation"]

    # as last apply rotations to lamps
    if abs(east_rotation - diffuse_lamp_obj.rotation_euler[2]) > 0.001:
        diffuse_lamp_obj.rotation_euler[2] = east_rotation

    if abs(east_rotation - specular_lamp_obj.rotation_euler[2]) > 0.001:
        specular_lamp_obj.rotation_euler[2] = east_rotation


def correct_lighting_east():
    """Corrects lighting east depending on current rotation of directed lamps in SCS Lighting scene

    """
    diffuse_lamp_obj, specular_lamp_obj = _get_diffuse_and_specular_lamps_from_scs_lighting()
    if diffuse_lamp_obj is None:
        return

    _get_scs_globals().lighting_scene_east_direction = (diffuse_lamp_obj.rotation_euler[2] * 180 / pi + 360) % 360


def set_lighting_east():
    """Sets lighting east according to current value set in SCS Globals.
    
    """
    _lightning_east_lock_draw_callback(True)


def enable():
    """Append SCS Lighting east lock callback.

    """
    if _callback["handle"]:
        disable()

    handle_pre_view = bpy.types.SpaceView3D.draw_handler_add(_lightning_east_lock_draw_callback, (False,), 'WINDOW', 'PRE_VIEW')
    _callback["handle"] = handle_pre_view
    _callback["initial_view_rotation"] = -1
    _callback["initial_lamp_rotation"] = 0


def disable():
    """Remove SCS Lighting east lock callback.

    """
    if not _callback["handle"]:
        return

    handle_pre_view = _callback["handle"]
    bpy.types.SpaceView3D.draw_handler_remove(handle_pre_view, 'WINDOW')
    _callback["handle"] = None
    _callback["initial_view_rotation"] = -1
    _callback["initial_lamp_rotation"] = 0
