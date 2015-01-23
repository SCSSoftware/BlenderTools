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
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint


class IconTypes:
    MESH = ".01_mesh_model_object.png"
    MESH_SHADOW_CASTER = ".02_object_with_shadow_caster_material.png"
    MESH_GLASS = ".03_object_with_glass_material.png"
    MESH_WITH_PHYSICS = ".04_object_with_physical_material.png"
    LOC = ".05_locator_all_types.png"
    LOC_MODEL = ".06_locator_model.png"
    LOC_PREFAB = ".07_locator_prefab.png"
    LOC_COLLIDER = ".08_locator_collision.png"
    LOC_PREFAB_NODE = ".09_locator_prefab_node.png"
    LOC_PREFAB_SIGN = ".10_locator_prefab_sign.png"
    LOC_PREFAB_SPAWN = ".11_locator_prefab_spawn.png"
    LOC_PREFAB_SEMAPHORE = ".12_locator_prefab_semaphore.png"
    LOC_PREFAB_NAVIGATION = ".13_locator_prefab_navigation.png"
    LOC_PREFAB_MAP = ".14_locator_prefab_map.png"
    LOC_PREFAB_TRIGGER = ".15_locator_prefab_trigger.png"
    LOC_COLLIDER_BOX = ".16_collider_box.png"
    LOC_COLLIDER_SPHERE = ".17_collider_sphere.png"
    LOC_COLLIDER_CAPSULE = ".18_collider_capsule.png"
    LOC_COLLIDER_CYLINDER = ".19_collider_cylinder.png"
    LOC_COLLIDER_CONVEX = ".20_collider_convex.png"
    SCS_ROOT = ".21_scs_root_object.png"
    SCS_LOGO = ".icon_scs_bt_logo.png"

    @staticmethod
    def as_list():
        return [IconTypes.MESH, IconTypes.MESH_SHADOW_CASTER, IconTypes.MESH_GLASS, IconTypes.MESH_WITH_PHYSICS,
                IconTypes.LOC, IconTypes.LOC_MODEL, IconTypes.LOC_PREFAB, IconTypes.LOC_COLLIDER,
                IconTypes.LOC_PREFAB_NODE, IconTypes.LOC_PREFAB_SIGN, IconTypes.LOC_PREFAB_SPAWN, IconTypes.LOC_PREFAB_SEMAPHORE,
                IconTypes.LOC_PREFAB_NAVIGATION, IconTypes.LOC_PREFAB_MAP, IconTypes.LOC_PREFAB_TRIGGER,
                IconTypes.LOC_COLLIDER_BOX, IconTypes.LOC_COLLIDER_SPHERE, IconTypes.LOC_COLLIDER_CAPSULE,
                IconTypes.LOC_COLLIDER_CYLINDER, IconTypes.LOC_COLLIDER_CONVEX, IconTypes.SCS_ROOT, IconTypes.SCS_LOGO]


class _Handler:
    initialized = False
    _icons_dict = {}

    @staticmethod
    def load_image(icon_type):
        tools_paths = _path.get_addon_installation_paths()
        if len(tools_paths) > 0:
            # create path to current icon "ui/icons/icon_type"
            icon_path = os.path.join(tools_paths[0], 'ui' + os.sep + 'icons' + os.sep + icon_type)
            if os.path.isfile(icon_path):
                if not icon_type in bpy.data.images:
                    img = bpy.data.images.load(icon_path)
                    img.use_alpha = True
                    img.user_clear()
            else:
                lprint("W Icon %s is missing. Please try to install addon again!")

    @staticmethod
    def draw(self, context):
        self.layout.row().label("Everything should be set to go...")
        self.layout.row().label("Check the console for result and happy Blending :)")

        icons_list = IconTypes.as_list()
        for icon in icons_list:
            _Handler._icons_dict[icon] = self.layout.icon(bpy.data.images[icon])

    @staticmethod
    def init():

        icons_list = IconTypes.as_list()
        for icon in icons_list:
            _Handler.load_image(icon)

        bpy.context.window_manager.popup_menu(_Handler.draw, title="SCS Blender Tools", icon="INFO")
        _Handler.initialized = True

    @staticmethod
    def get_icon(icon_type):
        if icon_type in _Handler._icons_dict:
            return _Handler._icons_dict[icon_type]
        else:
            return 0


def init():
    """Initialize custom icons for usage in layouts!
    NOTE: This function should be called when all Blender data blocks are ready for usage!
    """
    if not _Handler.initialized:
        _Handler.init()


def invalidate():
    """Invalidate initialization startu for custom icons.
    """
    _Handler.initialized = False


def get_icon(icon_type):
    """Get the custom icon for given type.
    :param icon_type: type of the icon. IconTypes variables should be used for it.
    :type icon_type: str
    :return: integer of icon or 0 if icon is not found in dictionary
    :rtype: int
    """
    return _Handler.get_icon(icon_type)


