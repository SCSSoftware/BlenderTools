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

# Copyright (C) 2013-2015: SCS Software

import bpy
import os
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.imp import tobj as _tobj_imp
from io_scs_tools.internals import inventory as _invetory
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.shaders import shader as _shader
from io_scs_tools.internals.shader_presets import cache as _shader_presets_cache
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint


def get_texture(texture_path, texture_type, report_invalid=False):
    """Creates and setup Texture and Image data on active Material.

    :param texture_path: Texture path
    :type texture_path: str
    :param texture_type: Texture type keyword
    :type texture_type: str
    :param report_invalid: flag indicating if invalid texture should be reported in 3d view
    :type report_invalid: bool
    """

    # CREATE TEXTURE/IMAGE ID NAME
    teximag_id_name = _path.get_filename(texture_path, with_ext=False)

    # CREATE ABSOLUTE FILEPATH
    abs_texture_filepath = _path.get_abs_path(texture_path)

    if abs_texture_filepath and abs_texture_filepath.endswith(".tobj"):
        abs_texture_filepath = _path.get_texture_path_from_tobj(abs_texture_filepath)

        # if not existing or none supported file
        if abs_texture_filepath is None or abs_texture_filepath[-4:] not in (".tga", ".png", ".dds"):

            if report_invalid:
                lprint("", report_warnings=-1, report_errors=-1)

            # take care of none existing paths referenced in tobj texture names
            if abs_texture_filepath:

                lprint("W Texture can't be displayed as TOBJ file: %r is referencing non texture file:\n\t   %r",
                       (texture_path, _path.normalize(abs_texture_filepath).replace("\\", "/")))

            else:

                lprint("W Texture can't be displayed as TOBJ file: %r is referencing non existing texture file.",
                       (texture_path,))

            if report_invalid:
                lprint("", report_warnings=1, report_errors=1)

            return None

    texture = None
    if abs_texture_filepath and os.path.isfile(abs_texture_filepath):

        # find existing texture with this image
        if teximag_id_name in bpy.data.textures:

            # reuse existing image texture if possible
            postfix = 0
            postfixed_tex = teximag_id_name
            while postfixed_tex in bpy.data.textures:

                img_exists = bpy.data.textures[postfixed_tex].image is not None
                if img_exists and _path.repair_path(bpy.data.textures[postfixed_tex].image.filepath) == _path.repair_path(abs_texture_filepath):
                    texture = bpy.data.textures[postfixed_tex]
                    break

                postfix += 1
                postfixed_tex = teximag_id_name + "." + str(postfix).zfill(3)

        # if texture wasn't found create new one
        if not texture:

            texture = bpy.data.textures.new(teximag_id_name, 'IMAGE')
            image = None

            # reuse existing image if possible
            postfix = 0
            postfixed_img = teximag_id_name
            while postfixed_img in bpy.data.images:

                if _path.repair_path(bpy.data.images[postfixed_img].filepath) == _path.repair_path(abs_texture_filepath):
                    image = bpy.data.images[postfixed_img]
                    break

                postfix += 1
                postfixed_img = teximag_id_name + "." + str(postfix).zfill(3)

            # if image wasn't found load it
            if not image:
                image = bpy.data.images.load(abs_texture_filepath)
                image.name = teximag_id_name

                # try to get relative path to the Blender file and set it to the image
                if bpy.data.filepath != '':  # empty file path means blender file is not saved
                    try:
                        rel_path = _path.relative_path(os.path.dirname(bpy.data.filepath), abs_texture_filepath)
                    except ValueError:  # catch different mount paths: "path is on mount 'C:', start on mount 'E:'"
                        rel_path = None

                    if rel_path:
                        image.filepath = rel_path

            # finally link image to texture
            texture.image = image
            image.use_alpha = True

        # set proper color space depending on texture type
        if texture_type == "nmap":
            # For TGA normal maps texture use Non-Color color space as it should be,
            # but for 16-bits PNG normal maps texture sRGB has to be used
            # otherwise Blender completely messes up normals calculation
            if texture.image.filepath.endswith(".tga"):
                texture.image.colorspace_settings.name = "Non-Color"
            else:
                texture.image.colorspace_settings.name = "sRGB"
        else:
            texture.image.colorspace_settings.name = "sRGB"

        # set usage of normal map if texture type is correct
        texture.use_normal_map = (texture_type == "nmap")

    if texture is None and texture_path.endswith(".tobj"):
        if report_invalid:
            lprint("", report_warnings=-1, report_errors=-1)

        lprint("W Texture can't be displayed as TOBJ file: %r is referencing non existing texture file:\n\t   %r",
               (texture_path, _path.normalize(abs_texture_filepath).replace("\\", "/")))

        if report_invalid:
            lprint("", report_warnings=1, report_errors=1)

    return texture


def get_shader_presets_container(shader_presets_filepath):
    """Returns shader presets data continaer from given path.

    :param shader_presets_filepath: relative or absolute shader presets filepath
    :type shader_presets_filepath: str
    :return: data container if file is found; None otherwise
    :rtype: io_scs_tools.internals.structure.SectionData
    """

    presets_container = None

    if shader_presets_filepath.startswith("//"):  # IF RELATIVE PATH, MAKE IT ABSOLUTE
        shader_presets_filepath = _path.get_abs_path(shader_presets_filepath)

    if os.path.isfile(shader_presets_filepath):

        presets_container = _pix_container.get_data_from_file(shader_presets_filepath, '    ')

    else:
        lprint('\nW The file path "%s" is not valid!', (shader_presets_filepath,))

    return presets_container


def get_shader_preset(shader_presets_filepath, template_name, presets_container=None):
    """Returns requested Shader Preset data from preset file.

    :param shader_presets_filepath: A file path to SCS shader preset file, can be absolute or relative
    :type shader_presets_filepath: str
    :param template_name: Preset name
    :type template_name: str
    :param presets_container: if provided this container is used to search shader in instead of opening the file again
    :type presets_container: io_scs_tools.internals.structure.SectionData
    :return: Preset data section
    :rtype: SectionData
    """

    # get container as it's not present in argument
    if not presets_container:

        presets_container = get_shader_presets_container(shader_presets_filepath)

    preset_section = None
    if presets_container:
        for section in presets_container:
            if section.type == "Shader":
                for prop in section.props:
                    if prop[0] == "PresetName":
                        if prop[1] == template_name:
                            # print(' + template name: "%s"' % template_name)
                            preset_section = section
                            break

    return preset_section


def get_material_from_context(context):
    if isinstance(context, bpy.types.Material):
        return context
    elif context and context.active_object and context.active_object.active_material:
        return context.active_object.active_material
    else:
        return None


def get_material_info(obj):
    """Returns information whether the object has "shadow" or "glass" material and if it hasn't either of it.

    :param obj: Blender Object
    :type obj: Object
    :return: has_shadow, has_glass, has_static_collision and is_other
    :rtype: tuple of bool
    """
    has_shadow = has_glass = has_static_collision = is_other = False
    if obj.type == 'MESH':
        for slot in obj.material_slots:

            if slot.material:

                if obj.scs_props.scs_part.startswith("coll"):
                    has_static_collision = True

                effect_name = slot.material.scs_props.mat_effect_name.lower()

                if "shadowonly" in effect_name or "fakeshadow" in effect_name or "shadowmap" in effect_name:
                    has_shadow = True
                elif ".shadow" in effect_name and not ("shadowmap" in effect_name):
                    has_shadow = True
                    is_other = True

                if "glass" in effect_name:
                    has_glass = True

        if not has_shadow and not has_glass and not has_static_collision:
            is_other = True
    return has_shadow, has_glass, has_static_collision, is_other


def set_shader_data_to_material(material, section, is_import=False, override_back_data=True):
    """Used to set up material properties from given shader data even via UI or on import.

    :param material: blender material to which section data should be set
    :type material: bpy.types.Material
    :param section: new material data presented with Material section of PIX files
    :type section: io_scs_tools.internals.structure.SectionData
    :param is_import: flag indication if shader data are set from import process
    :type is_import: bool
    :param override_back_data: flag indication if back data for UI shall be overwritten
    :type override_back_data: bool
    """

    preset_effect = section.get_prop_value("Effect")

    # check shader flags
    for attr in section.props:

        if attr[0] == "Flags":
            material.scs_props.enable_aliasing = not attr[1] == 1  # Flags: 1 #DISABLE ALIASING
            break

    attributes = {}
    textures = {}
    attribute_i = 0
    texture_i = 0
    used_attribute_types = {}  # attribute types used by current shader
    used_texture_types = {}  # texture types used by current shader and should be overlooked during clearing of texture slots
    for item in section.sections:

        if item.type == "Attribute":
            attribute_data = {}
            for prop in item.props:
                key, value = prop

                # # GETTING RID OF "[" AND "]" CHARS...
                if type(value) is str:
                    value = value.replace("[", "").replace("]", "")

                attribute_data[key] = value

            attribute_type = attribute_data['Tag']

            attributes[str(attribute_i)] = attribute_data
            attribute_i += 1

            used_attribute_types[attribute_type] = attribute_data

        elif item.type == "Texture":
            texture_data = {}
            for prop in item.props:
                # print('      prop: "%s"' % str(prop))
                texture_data[prop[0]] = prop[1]

            # APPLY SECTION TEXTURE VALUES
            texture_type = texture_data['Tag'].split(':')[1]
            tex_type = texture_type[8:]

            used_texture_types[tex_type] = texture_data

            textures[str(texture_i)] = texture_data
            texture_i += 1

    scs_props_keys = material.scs_props.keys()
    # if overriding back data also make sure to clear attribute values for current shader
    # to prevent storing of unused values from blend data block
    # NOTE: looks also takes into account that all the unused properties are omitted from scs_props dict
    if override_back_data:
        for key in scs_props_keys:
            is_key_used = False
            if key.startswith("shader_attribute"):
                for used_attribute in used_attribute_types:
                    if used_attribute in key[16:]:
                        is_key_used = True

            if key.startswith("shader_texture"):
                for used_tex_type in used_texture_types:
                    if used_tex_type in key[14:]:
                        is_key_used = True

            # delete only unused shader keys everything else should stay in the place
            # as those keys might be used in some other way
            if not is_key_used and key.startswith("shader_"):
                lprint("D Unsetting property from material in set_shader_data %s:", (key,))
                material.scs_props.property_unset(key)

    # apply used attributes
    created_attributes = {}
    for attribute_type in used_attribute_types.keys():
        attribute_data = used_attribute_types[attribute_type]

        # acquire old attribute value if exists and not importing
        old_value = None
        if "shader_attribute_" + attribute_type in scs_props_keys and not is_import:
            old_value = getattr(material.scs_props, "shader_attribute_" + attribute_type)

        if attribute_type in ("diffuse", "specular", "env_factor", "fresnel", "tint"):

            if not old_value:
                material.scs_props["shader_attribute_" + attribute_type] = attribute_data['Value']

            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type in ("shininess", "add_ambient", "reflection", "reflection2", "shadow_bias", "tint_opacity"):

            if not old_value:
                material.scs_props["shader_attribute_" + attribute_type] = attribute_data['Value'][0]

            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type.startswith("aux") and hasattr(material.scs_props, "shader_attribute_" + attribute_type):

            auxiliary_prop = getattr(material.scs_props, "shader_attribute_" + attribute_type, None)

            # NOTE : invalidate old value if size of existing auxiliary property is different
            # then size of new one overwrite it anyway, because otherwise we will might access
            # values that doesn't exists but they should, for example:
            # switching from "eut2.dif.spec.weight.mult2" to "eut2.dif.spec.weight.mult2.weight2"
            if len(auxiliary_prop) != len(attribute_data['Value']):
                old_value = None

            if not old_value:

                # clean old values possible left from previous shader
                while len(auxiliary_prop) > 0:
                    auxiliary_prop.remove(0)

                for val in attribute_data['Value']:
                    item = auxiliary_prop.add()
                    item['value'] = val
                    item['aux_type'] = attribute_type

            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type == "substance":

            if not old_value:
                material.scs_props.substance = attribute_data['Value'][0]

    # if shader attribute properties are still unset reset it to default
    if material.scs_props.substance == _MAT_consts.unset_substance and "substance" not in material.scs_props.keys():
        material.scs_props.substance = "None"

    # collect old uv mappings per tex_coord values and delete them from material (they will be set back later)
    # NOTE: we have to create extra iteration for uv mappings collecting
    # as multiple texture types can use same tex coord and we have to make sure
    # to collect them before we apply any texture data back to material.
    old_texture_mappings = {}
    for tex_type in used_texture_types:

        texture_mappings = getattr(material.scs_props, "shader_texture_" + tex_type + "_uv")
        if override_back_data:
            while len(texture_mappings) > 0:

                # save only set uv mapping tex_cord:value pairs
                if texture_mappings[0].value != "":
                    old_texture_mappings[texture_mappings[0].tex_coord] = texture_mappings[0].value

                texture_mappings.remove(0)

    # apply used textures
    created_textures = {}
    created_tex_uvs = {}
    for tex_type in used_texture_types:

        # skip unknown texture type
        if tex_type not in material.scs_props.get_texture_types().keys():
            lprint("D Trying to apply unknown texture type to SCS material: %r", (tex_type,))
            continue

        texture_data = used_texture_types[tex_type]

        # always set texture lock attribute
        # important to set it always as some texture might get unlocked in preset and
        # selecting same present again has to unlock that texture
        texture_locked = False
        if "Lock" in texture_data:
            texture_locked = bool(texture_data["Lock"])
        setattr(material.scs_props, "shader_texture_" + tex_type + "_locked", texture_locked)

        texture_mappings = getattr(material.scs_props, "shader_texture_" + tex_type + "_uv")

        # if shader is imported try to create custom tex coord mappings on material
        if material.scs_props.active_shader_preset_name == "<imported>" and "scs_tex_aliases" in material:
            custom_maps = material.scs_props.custom_tex_coord_maps

            for tex_coord_key in sorted(material["scs_tex_aliases"].keys()):

                if _invetory.get_index(custom_maps, "tex_coord_" + tex_coord_key) == -1:
                    new_map = custom_maps.add()
                    new_map.name = "tex_coord_" + tex_coord_key
                    new_map.value = material["scs_tex_aliases"][tex_coord_key]

            # add one mapping field for using it as a preview uv layer in case of imported shader
            mapping = texture_mappings.add()
            mapping.texture_type = tex_type
            mapping.tex_coord = -1

        # if there is an info about mapping in shader use it (in case of imported material this condition will fall!)
        elif "TexCoord" in texture_data:

            for tex_coord_i, tex_coord in enumerate(texture_data['TexCoord']):
                tex_coord = int(tex_coord)

                if tex_coord != -1:
                    mapping = texture_mappings.add()
                    mapping['texture_type'] = tex_type
                    mapping['tex_coord'] = tex_coord

                    # apply uv mappings either from imported data or from old mappings of previous shader
                    if "scs_tex_aliases" in material:  # scs_tex_aliases are present only on import
                        mapping['value'] = material["scs_tex_aliases"][str(tex_coord)]

                        # for now make sure to use only first coord mapping info for shader
                        # NOTE: this may give wrong shader results upon import of "truckpaint" shader
                        if len(texture_mappings) == 1:
                            created_tex_uvs[tex_type] = mapping.value

                    elif tex_coord in old_texture_mappings:

                        mapping['value'] = old_texture_mappings[tex_coord]
                        created_tex_uvs[tex_type] = old_texture_mappings[tex_coord]

        # set texture file to current texture
        scs_texture_str = _path.get_scs_texture_str(texture_data['Value'])

        # apply texture path if not empty and not yet set, except if import is going on
        # NOTE: during import bitmap has to be applied even if empty
        # because otherwise texture from previous look might be applied
        if (scs_texture_str != "" and getattr(material.scs_props, "shader_texture_" + tex_type, "") == "") or is_import:
            material.scs_props["shader_texture_" + tex_type] = scs_texture_str
            created_textures[tex_type] = get_texture(scs_texture_str, tex_type)

            if is_import:

                # only if shader is imported then make sure that by default imported values will be used
                if material.scs_props.active_shader_preset_name == "<imported>":
                    setattr(material.scs_props, "shader_texture_" + tex_type + "_use_imported", True)
                    setattr(material.scs_props, "shader_texture_" + tex_type + "_imported_tobj", texture_data['Value'])

        # if property is still unset reset it to empty
        if getattr(material.scs_props, "shader_texture_" + tex_type, "") == _MAT_consts.unset_bitmap_filepath:
            material.scs_props["shader_texture_" + tex_type] = ""
        else:

            final_tex_str = getattr(material.scs_props, "shader_texture_" + tex_type, "")
            created_textures[tex_type] = get_texture(final_tex_str, tex_type)

            if is_import and not override_back_data:

                if created_textures[tex_type] is None:
                    lprint("E Can't find texture nor TOBJ inside SCS Project Base Path: %r", (final_tex_str,))

    # override shader data for identifying used attributes and textures in UI
    if override_back_data:

        shader_data = {'effect': preset_effect,
                       'attributes': attributes,
                       'textures': textures}
        material["scs_shader_attributes"] = shader_data

    # setup nodes for 3D view visualization
    _shader.setup_nodes(material, preset_effect, created_attributes, created_textures, created_tex_uvs, override_back_data)


def reload_tobj_settings(material, tex_type):
    """Relaods TOBJ settings on given texture type of material.
    If tobj doesn't exists it does nothing.

    :param material: material
    :type material: bpy.types.Material
    :param tex_type: texture type
    :type tex_type: str
    """

    shader_texture_str = "shader_texture_" + tex_type
    shader_texture_filepath = getattr(material.scs_props, shader_texture_str)

    tobj_file = _path.get_tobj_path_from_shader_texture(shader_texture_filepath)
    if tobj_file:

        settings, map_type = _tobj_imp.get_settings_and_type(tobj_file)

        # intentionally set ID property directly to avoid update function invoke
        material.scs_props[shader_texture_str + "_settings"] = int(settings, 2)

        setattr(material.scs_props, shader_texture_str + "_map_type", map_type)
        setattr(material.scs_props, shader_texture_str + "_tobj_load_time", str(os.path.getmtime(tobj_file)))


def find_preset(material_effect, material_textures):
    """Tries to find suitable Shader Preset (as defined in shader_presets.txt file) for imported shader. If it cannot be found, it will return None.

    :param material_effect: Name of the requested Look
    :type material_effect: str
    :param material_textures: material textures dictionary (key: tex_id, value: tex_path)
    :type material_textures: dict
    :return: Preset name and section or tuple of Nones
    :rtype: (str, io_scs_tools.internals.structure.SectionData) | (None, None)
    """

    # find longest matching shader effect name
    longest_match = ""
    search_i = 0
    while search_i != -1:

        search_i = material_effect.find(".", search_i)
        curr_substr = material_effect[:search_i]

        if search_i == -1:
            curr_substr = material_effect
        else:
            search_i += 1

        if _shader_presets_cache.effect_exists(curr_substr) and len(curr_substr) > len(longest_match):
            longest_match = curr_substr

    # nothing matched
    if len(longest_match) == 0:
        return None, None

    # use longest base effect match and search for a match inside flavors
    preset_sections = _shader_presets_cache.find_sections(longest_match, material_effect[len(longest_match):])
    for preset_section in preset_sections:

        # also check for matching among locked textures
        # NOTE: this check is needed because of possible multiple
        # presets with the same effect name and different locked texture
        matched_textures = 0
        matched_textures_avaliable = 0
        for tex_sec in preset_section.get_sections("Texture"):

            tex_id = tex_sec.get_prop_value("Tag").split(":")[1]
            tex_path = tex_sec.get_prop_value("Value")
            tex_lock = tex_sec.get_prop_value("Lock")

            if tex_lock == "True":
                matched_textures_avaliable += 1

                if tex_id in material_textures and (tex_path == material_textures[tex_id] or tex_path == ""):
                    matched_textures += 1

        if matched_textures == matched_textures_avaliable or matched_textures_avaliable == 0:
            return preset_section.get_prop_value("PresetName"), preset_section

    return None, None
