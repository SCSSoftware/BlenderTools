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

# Copyright (C) 2015-2022: SCS Software

import bpy
from bpy.app.handlers import persistent
from io_scs_tools.consts import SCSLigthing as _LIGHTING_consts
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import info as _info_utils
from io_scs_tools.utils import property as _property_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


@persistent
def post_load(scene):
    from io_scs_tools.internals.containers.config import AsyncPathsInit

    # get Blender Tools version from last blend file load
    last_load_bt_ver = _get_scs_globals().last_load_bt_version

    # no version yet, so new blend or blend without previous BT usage. Nothing to be fixed, yay!
    if last_load_bt_ver == _property_utils.get_default(_get_scs_globals(), 'last_load_bt_version'):
        _get_scs_globals().last_load_bt_version = _info_utils.get_tools_version()
        return

    # list versions and fix functions  & then execute them
    VERSIONS_LIST = (
        ("0.6", apply_fixes_for_0_6),
        ("1.4", apply_fixes_for_1_4),
        ("1.12", apply_fixes_for_1_12),
        ("2.0", apply_fixes_for_2_0),
        ("2.4", apply_fixes_for_2_4),
    )

    for version, func in VERSIONS_LIST:
        if _info_utils.cmp_ver_str(last_load_bt_ver, version) <= 0:

            # try to add apply fixed function as callback, if failed execute fixes right now
            if not AsyncPathsInit.append_callback(func):
                func()

    # as last update "last load" Blender Tools version to current
    _get_scs_globals().last_load_bt_version = _info_utils.get_tools_version()


def _reload_materials():
    """Triggers materials nodes and UI attributes reloading.
    """
    windows = bpy.data.window_managers[0].windows

    assert len(windows) > 0

    with bpy.context.temp_override(window=windows[0]):
        bpy.ops.material.scs_tools_reload_materials('INVOKE_DEFAULT')


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

        for tex_type in material.scs_props.get_texture_types():

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

        # 4. reload all materials once all corrections to materials has been done
        _reload_materials()


def apply_fixes_for_1_4():
    """
    Applies fixes for v1.4 or less:
    1. reload all materials to fixup any new materials nodes eg. normal map node
    2. remove any obosolete hidden normal map materials: ".scs_nmap_X"
    """

    print("INFO\t-  Applying fixes for version <= 1.4")

    # 1. reload all materials
    _reload_materials()

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


def apply_fixes_for_1_12():
    """
    Applies fixes for 1.12 or less:
    1. Remove legacy scs_shader_presets_inventory from world.
    2. Remove old lighting scene.
    3. Reload materials node trees.
    4. Unhide collections in viewport.
    5. Enable proper filters in outliner (for user to see why his objects are hidden)
    """

    print("INFO\t-  Applying fixes for version <= 1.12")

    from io_scs_tools.utils import __get_world__
    world = __get_world__()

    # 1. remove legacy scs_shader_presets_inventory from world
    if 'scs_shader_presets_inventory' in world:
        del world['scs_shader_presets_inventory']

    # 2. remove old lighting scene
    if _LIGHTING_consts.scene_name in bpy.data.scenes:
        lighting_scene = bpy.data.scenes[_LIGHTING_consts.scene_name]

        for obj in lighting_scene.objects:

            if obj.type == "LIGHT":
                bpy.data.lights.remove(obj.data)
            else:
                bpy.data.objects.remove(obj)

        # TODO: use scenes.remove() once bug is resolved: https://developer.blender.org/T71422
        override = {'scene': lighting_scene}
        bpy.ops.scene.delete(override, 'EXEC_DEFAULT')

        for col in bpy.data.collections:
            if col.users == 0:
                bpy.data.collections.remove(col)

    # 3. reload materials node trees
    _reload_materials()

    # 4. update preview models to get new material assigned
    _preview_models.update(force=True)

    # 5. remove unused textures and reflection images from old blender (materials now don't use texture objects anymore)
    for tex in bpy.data.textures:
        if tex.users == 0:
            bpy.data.textures.remove(tex)

    for img in bpy.data.images:
        if img.users == 0:
            bpy.data.images.remove(img)

    # 6. unhide all collections and objects in viewport
    for coll in bpy.data.collections:
        coll.hide_viewport = False

    for obj in bpy.data.objects:
        obj.hide_viewport = False

    windows = bpy.data.window_managers[0].windows
    if len(windows) > 0:
        # due to big version bump after this one, we let user know he is migrating to 2.0
        msg = (
            "\nWelcome back, your scene just migrated to SCS Blender Tools 2.0!\n",
            "To give you idea what just happened, here is a summary:",
            "1. SCS Materials were reloaded and adopted to the new renderer in Blender!",
            "2. SCS preview models were reloaded to apply new material to them!",
            "3. Old SCS Lighting was removed and replaced by new one!",
            "4. Old textures and images were purged!",
            "5. Old layers were migrated over as collections, thus everything got visible in your scene!"
        )

        with bpy.context.temp_override(window=windows[0]):
            bpy.ops.wm.scs_tools_show_3dview_report('INVOKE_DEFAULT', message="\n".join(msg))


def apply_fixes_for_2_0():
    """
    Applies fixes for 2.0 or less:
    1. Reload materials since some got removed/restructed attributes
    2. Remove .linv flavor from dif.lum.spec shaders (it's not supported anymore)
    """

    print("INFO\t-  Applying fixes for version <= 2.0")

    # dictinary of materials with "eut2.sky" effect and their former uv sets
    # to be reapplied to new texture types
    sky_uvs_mat = {}

    # 1. do pre-reload changes and collect data
    for mat in bpy.data.materials:

        effect_name = mat.scs_props.mat_effect_name

        # dif.lum.spec got removed linv flavor, thus remove it.
        if effect_name.startswith("eut2.dif.lum.spec") and ".linv" in effect_name:
            start_idx = effect_name.index(".linv")
            end_idx = start_idx + 5
            mat.scs_props.mat_effect_name = mat.scs_props.mat_effect_name[:start_idx] + mat.scs_props.mat_effect_name[end_idx:]

        # window.[day|night] got transformed into window.lit
        if effect_name in ("eut2.window.day", "eut2.window.night"):
            mat.scs_props.mat_effect_name = "eut2.window.lit"
            mat.scs_props.active_shader_preset_name = "window.lit"

        # sky got different texture types preserver uvs
        if effect_name.startswith("eut2.sky") and len(mat.scs_props.shader_texture_base_uv) == 1:
            sky_uvs_mat[mat] = mat.scs_props.shader_texture_base_uv[0].value

    # 2. reload materials node trees and possible param changes in UI as last
    _reload_materials()

    # 3. post-reload changes
    # recover uvs for sky shaders
    for mat in sky_uvs_mat:
        mat.scs_props.shader_texture_sky_weather_base_a_uv[0].value = sky_uvs_mat[mat]
        mat.scs_props.shader_texture_sky_weather_base_b_uv[0].value = sky_uvs_mat[mat]
        mat.scs_props.shader_texture_sky_weather_over_a_uv[0].value = sky_uvs_mat[mat]
        mat.scs_props.shader_texture_sky_weather_over_b_uv[0].value = sky_uvs_mat[mat]

        # we need to update looks so that new values get propagated to all of the looks
        for scs_root in _object_utils.gather_scs_roots(bpy.data.objects):
            _looks.update_look_from_material(scs_root, mat)


def apply_fixes_for_2_4():
    """
    Applies fixes for 2.4 or less:
    1. Reload materials since some got removed/restructed attributes
    """

    print("INFO\t-  Applying fixes for version <= 2.4")

    # 1. reload all materials
    _reload_materials()
