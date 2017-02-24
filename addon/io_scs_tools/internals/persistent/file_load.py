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

# Copyright (C) 2015: SCS Software

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.operators.world import SCSPathsInitialization as _SCSPathsInitialization
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import info as _info_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


@persistent
def post_load(scene):
    # get Blender Tools version from last blend file load
    last_load_bt_ver = _get_scs_globals().last_load_bt_version

    if _info_utils.cmp_ver_str(last_load_bt_ver, "0.6") <= 0:

        # try to add apply fixed function as callback, if failed execute fixes right now
        if not _SCSPathsInitialization.append_callback(apply_fixes_for_0_6):
            apply_fixes_for_0_6()

    if _info_utils.cmp_ver_str(last_load_bt_ver, "1.4") <= 0:

        # try to add apply fixed function as callback, if failed execute fixes right now
        if not _SCSPathsInitialization.append_callback(apply_fixes_for_1_4):
            apply_fixes_for_1_4()

    # as last update "last load" Blender Tools version to current
    _get_scs_globals().last_load_bt_version = _info_utils.get_tools_version()


def apply_fixes_for_0_6():
    """
    Applies fixes for v0.6 or less:
    1. fixes reflection textures tga's for tobjs as TOBJ load is now supported and unlock that textures
    2. calls update on all set textures to correct paths for them
    3. tries to fix active shader preset name for materials, because of new flavor system
    """

    print("INFO\t-  Applying fixes for version <= 0.6")

    scs_roots = None

    for material in bpy.data.materials:

        # ignore materials not related to blender tools
        if material.scs_props.mat_effect_name == "":
            continue

        for tex_type in material.scs_props.get_texture_types().keys():

            texture_attr_str = "shader_texture_" + tex_type
            if texture_attr_str in material.scs_props.keys():

                # 1. fix reflection textures
                if tex_type == "reflection":

                    is_building_ref = material.scs_props[texture_attr_str].endswith("/bulding_ref.tga")
                    is_generic_s = material.scs_props[texture_attr_str].endswith("material/environment/generic_s.tga")
                    is_glass_interior = material.scs_props.active_shader_preset_name == "glass - interior"
                    is_dif_spec_weight_add_env = material.scs_props.active_shader_preset_name == "dif.spec.weight.add.env"
                    is_truckpaint = material.scs_props.active_shader_preset_name.startswith("truckpaint")

                    # fix paths
                    if is_building_ref:
                        material.scs_props[texture_attr_str] = material.scs_props[texture_attr_str][:-4]
                        material.scs_props[texture_attr_str + "_locked"] = False
                    elif is_generic_s:
                        if is_glass_interior:
                            material.scs_props[texture_attr_str] = "//material/environment/interior_reflection"
                        elif is_dif_spec_weight_add_env:
                            material.scs_props[texture_attr_str] = "//material/environment/generic_reflection"
                        else:
                            material.scs_props[texture_attr_str] = "//material/environment/vehicle_reflection"

                        # unlock reflection textures everywhere except on truckpaint shader
                        if not is_truckpaint:
                            material.scs_props[texture_attr_str + "_locked"] = False

                    # acquire roots on demand only once
                    scs_roots = _object_utils.gather_scs_roots(bpy.data.objects) if not scs_roots else scs_roots

                    # propagate reflection texture change on all of the looks.
                    # NOTE: We can afford write through because old BT had all reflection textures locked
                    # meaning user had to use same texture on all looks
                    # NOTE#2: Printouts like:
                    # "Look with ID: X doesn't have entry for material 'X' in SCS Root 'X',
                    #  property 'shader_texture_reflection' won't be updated!"
                    # are expected here, because we don't use any safety check,
                    # if material is used on the mesh objects inside scs root
                    for scs_root in scs_roots:
                        _looks.write_through(scs_root, material, texture_attr_str)

                # 2. trigger update function for path reload and reload of possible missing textures
                update_func = getattr(material.scs_props, "update_" + texture_attr_str, None)
                if update_func:
                    update_func(material)

        # ignore already properly set materials
        if _shader_presets.has_preset(material.scs_props.active_shader_preset_name):
            continue

        # 3. try to recover "active_shader_preset_name" from none flavor times Blender Tools
        material_textures = {}
        if "scs_shader_attributes" in material and "textures" in material["scs_shader_attributes"]:
            for texture in material["scs_shader_attributes"]["textures"].values():
                tex_id = texture["Tag"].split(":")[1]
                tex_value = texture["Value"]
                material_textures[tex_id] = tex_value

        (preset_name, preset_section) = _material_utils.find_preset(material.scs_props.mat_effect_name, material_textures)
        if preset_name:
            material.scs_props.active_shader_preset_name = preset_name

            # acquire roots on demand only once
            scs_roots = _object_utils.gather_scs_roots(bpy.data.objects) if not scs_roots else scs_roots

            # make sure to fix active preset shader name in all looks
            # NOTE: Printouts like:
            # "Look with ID: X doesn't have entry for material 'X' in SCS Root 'X',
            #  property 'active_shader_preset_name' won't be updated!"
            # are expected here, because we don't use any safety check,
            # if material is used on the mesh objects inside scs root
            for scs_root in scs_roots:
                _looks.write_through(scs_root, material, "active_shader_preset_name")


def apply_fixes_for_1_4():
    """
    Applies fixes for v1.4 or less:
    1. reload all materials to fixup any new materials nodes eg. normal map node
    2. remove any obosolete hidden normal map materials: ".scs_nmap_X"
    """

    print("INFO\t-  Applying fixes for version <= 1.4")

    # 1. reload all materials
    bpy.ops.material.scs_reload_nodes('INVOKE_DEFAULT')

    # 2. remove all obsolete ".scs_nmap_" + str(i) materials, as of 2.78 we are using new normal maps node
    i = 1
    while ".scs_nmap_" + str(i) in bpy.data.materials:

        material = bpy.data.materials[".scs_nmap_" + str(i)]

        # remove and clear if possible
        if material.users == 0:

            textures = {}
            # gather all used textures in this material
            for j, tex_slot in enumerate(material.texture_slots):
                if tex_slot and tex_slot.texture:
                    textures[j] = tex_slot.texture

            # remove textures from texture slots first and check if texture can be cleared
            for slot_i in textures.keys():
                material.texture_slots.clear(slot_i)

                if textures[slot_i].users == 0:
                    bpy.data.textures.remove(textures[slot_i], do_unlink=True)

            # as last delete actually nmap material
            bpy.data.materials.remove(material, do_unlink=True)

        i += 1
