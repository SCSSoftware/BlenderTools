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
from bpy.app.handlers import persistent
from io_scs_tools.internals.containers import config as _config_container
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


@persistent
def pre_save(scene):
    # clear all not needed inventories
    scs_globals = _get_scs_globals()
    scs_globals.scs_hookup_inventory.clear()
    scs_globals.scs_matsubs_inventory.clear()
    scs_globals.scs_sign_model_inventory.clear()
    scs_globals.scs_traffic_rules_inventory.clear()
    scs_globals.scs_tsem_profile_inventory.clear()
    scs_globals.scs_trigger_actions_inventory.clear()

    # clear unused materials, this has to be done because of usage of same material inside nodes
    for material in bpy.data.materials:
        if material.node_tree and material.users == 1:
            for node in material.node_tree.nodes:
                if node.type in ("MATERIAL_EXT", "MATERIAL"):
                    if node.material == material:
                        material.user_clear()

    # make sure to save actions used in at least one scs game object
    for obj in bpy.data.objects:
        if obj.type == "EMPTY" and obj.scs_props.empty_object_type == "SCS_Root":
            for scs_anim in obj.scs_object_animation_inventory:
                if scs_anim.action in bpy.data.actions:
                    bpy.data.actions[scs_anim.action].use_fake_user = True


@persistent
def post_save(scene):
    # reload inventories
    readonly = True
    scs_globals = _get_scs_globals()
    _config_container.update_hookup_library_rel_path(
        scs_globals.scs_hookup_inventory,
        scs_globals.hookup_library_rel_path,
        readonly
    )
    _config_container.update_matsubs_inventory(
        scs_globals.scs_matsubs_inventory,
        scs_globals.matsubs_library_rel_path,
        readonly
    )
    _config_container.update_traffic_rules_library_rel_path(
        scs_globals.scs_traffic_rules_inventory,
        scs_globals.traffic_rules_library_rel_path,
        readonly
    )
    _config_container.update_tsem_library_rel_path(
        scs_globals.scs_tsem_profile_inventory,
        scs_globals.tsem_library_rel_path,
        readonly
    )
    _config_container.update_sign_library_rel_path(
        scs_globals.scs_sign_model_inventory,
        scs_globals.sign_library_rel_path,
        readonly
    )
    _config_container.update_trigger_actions_rel_path(
        scs_globals.scs_trigger_actions_inventory,
        scs_globals.trigger_actions_rel_path,
        readonly
    )
