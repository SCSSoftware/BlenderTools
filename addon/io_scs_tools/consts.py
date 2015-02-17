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

"""
Constants for data group of map and navigation curves
"""


class ConnectionsStorage:
    """Constants related for storage of connections used in custom drawing
    """

    group_name = ".scs_connection_storage"
    """Name of bpy.data.group which will be used for storing Custom Property for connections dictionary"""
    custom_prop_name = "scs_locator_connections"
    """Name of the Blender Custom Property where dictionary for connections will be stored"""


class Operators:
    class SelectionType:
        """Constants related to type of selection in operators all over the tools
        """
        undecided = -1
        deselect = 0
        select = 1
        shift_select = 2
        ctrl_select = 3

    class ViewType:
        """Constants related to type of view in operators all over the tools
        """
        undecided = -1
        hide = 0
        viewonly = 1
        shift_view = 2
        ctrl_view = 3


class Icons:
    """Constants related to loading of custom icons.
    """

    class Types:
        """This class saves names of all custom icons for Blender Tools.
        """
        mesh = ".01_mesh_model_object.png"
        mesh_shadow_caster = ".02_object_with_shadow_caster_material.png"
        mesh_glass = ".03_object_with_glass_material.png"
        mesh_with_physics = ".04_object_with_physical_material.png"
        loc = ".05_locator_all_types.png"
        loc_model = ".06_locator_model.png"
        loc_prefab = ".07_locator_prefab.png"
        loc_collider = ".08_locator_collision.png"
        loc_prefab_node = ".09_locator_prefab_node.png"
        loc_prefab_sign = ".10_locator_prefab_sign.png"
        loc_prefab_spawn = ".11_locator_prefab_spawn.png"
        loc_prefab_semaphore = ".12_locator_prefab_semaphore.png"
        loc_prefab_navigation = ".13_locator_prefab_navigation.png"
        loc_prefab_map = ".14_locator_prefab_map.png"
        loc_prefab_trigger = ".15_locator_prefab_trigger.png"
        loc_collider_box = ".16_collider_box.png"
        loc_collider_sphere = ".17_collider_sphere.png"
        loc_collider_capsule = ".18_collider_capsule.png"
        loc_collider_cylinder = ".19_collider_cylinder.png"
        loc_collider_convex = ".20_collider_convex.png"
        scs_root = ".21_scs_root_object.png"
        scs_logo = ".icon_scs_bt_logo.png"

        @staticmethod
        def as_list():
            """Gets file names of all custom icons defined in Blender Tools
            :return: list of all custom icon files
            :rtype: list
            """
            return [Icons.Types.mesh, Icons.Types.mesh_shadow_caster, Icons.Types.mesh_glass, Icons.Types.mesh_with_physics,
                    Icons.Types.loc, Icons.Types.loc_model, Icons.Types.loc_prefab, Icons.Types.loc_collider,
                    Icons.Types.loc_prefab_node, Icons.Types.loc_prefab_sign, Icons.Types.loc_prefab_spawn, Icons.Types.loc_prefab_semaphore,
                    Icons.Types.loc_prefab_navigation, Icons.Types.loc_prefab_map, Icons.Types.loc_prefab_trigger,
                    Icons.Types.loc_collider_box, Icons.Types.loc_collider_sphere, Icons.Types.loc_collider_capsule,
                    Icons.Types.loc_collider_cylinder, Icons.Types.loc_collider_convex, Icons.Types.scs_root, Icons.Types.scs_logo]


class Part:
    """Constants related to 'SCS Parts'
    """
    default_name = "defaultpart"
    """Default name for part"""


class Variant:
    """Constants related to 'SCS Variants'
    """
    default_name = "default"
    """Default name for variant"""