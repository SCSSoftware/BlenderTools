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

import os
import bpy
from io_scs_tools.internals import inventory as _invetory
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import path as _path
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def is_valid_shader_texture_path(shader_texture):
    """It returns True if there is valid Shader Texture file, otherwise False.

    :param shader_texture: SCS texture path, can be absolute or relative
    :type shader_texture: str
    :return: True if there is valid Shader Texture file, otherwise False
    :rtype: bool
    """
    if shader_texture != "":
        if shader_texture.startswith(str(os.sep + os.sep)):  # RELATIVE PATH
            shader_texture_abs_path = _path.get_abs_path(shader_texture)
            if shader_texture_abs_path:
                if os.path.isfile(shader_texture_abs_path):
                    return True
        else:  # ABSOLUTE PATH
            if os.path.isfile(shader_texture):
                return True
    else:
        return True  # NOTE: This is because we don't want to have all empty slots marked as invalid.
    return False


def clear_texture_slots(material, texture_type):
    """Clears texture slots with given texture_type.

    :param texture_type: Type of SCS texture
    :type texture_type: str
    :return: True if any slots were deleted or False if none
    :rtype: bool
    """
    texture_slots = material.texture_slots
    for texture_slot_i, texture_slot in enumerate(texture_slots):
        # print('  texture_slot[%.2i]: %s' % (texture_slot_i, str(texture_slot)))
        if texture_slot:
            # print('   texture_slot.name: %r' % str(texture_slot.name))
            if texture_slot.name.startswith(str("scs_" + texture_type + "_")):
                tex = texture_slots[texture_slot_i].texture
                texture_slots.clear(texture_slot_i)
                if tex.users == 0:
                    bpy.data.textures.remove(tex)

                return True
    return False


def get_texture_slot(material, texture_type):
    """Takes texture type and returns texture slot from active Material or None.

    :param material: Blender material object
    :type material: Material
    :param texture_type: SCS texture type
    :type texture_type: str
    :return: Material Texture Slot or None
    :rtype: MaterialTextureSlot
    """
    texture_slots = material.texture_slots
    for texture_slot_i, texture_slot in enumerate(texture_slots):
        # print('  texture_slot[%.2i]: %s' % (texture_slot_i, str(texture_slot)))
        if texture_slot:
            # print('   texture_slot.name: %r' % str(texture_slot.name))
            if texture_slot.name.startswith(str("scs_" + texture_type + "_")):
                return texture_slot
    return None


def correct_image_filepath(texture_slot, abs_texture_filepath):
    """Takes a Texture slot and correct absolut filepath of an Image and applies it on Texture in provided slot.
    Then the function performs image reload.

    :param texture_slot: Texture Slot in active Material
    :type texture_slot: TextureSlot
    :param abs_texture_filepath: New absolute texture path
    :type abs_texture_filepath: str
    """
    # NOTE: The "use_auto_refresh" is used here on Texture to refresh
    # the image texture because "reload()", "update()", "gl_load()" nor
    # any other method on Image doesn't work due to a wrong context.
    texture_slot.texture.image_user.use_auto_refresh = True
    image = texture_slot.texture.image
    bpy.data.images[image.name].filepath = abs_texture_filepath
    texture_slot.texture.image_user.use_auto_refresh = False


def update_texture_slots(material, texture_path, texture_type):
    """Creates and setup Texture and Image data on active Material.

    :param material: Blender material
    :type material: Material
    :param texture_path: Texture path
    :type texture_path: str
    :param texture_type: Texture type keyword
    :type texture_type: str
    """
    # print(' texture_path: %s' % str(texture_path))

    # CREATE TEXTURE/IMAGE ID NAME
    teximag_id_name = str("scs_" + texture_type + "_" + os.path.splitext(os.path.basename(texture_path))[0])
    # print(' teximag_id_name: %r' % str(teximag_id_name))

    # PROVIDE A TEXTURE SLOT
    slot_found = None
    texture_slots = material.texture_slots

    # A. Check all Texture slots for existing Image Textures (OLD WAY)
    # NOTE: This method often results in arbitrary order of Image Textures
    # within Texture Slots. In such circumstances it is very hard to ensure
    # uniform way of Material appearance in 3D viewport, because of
    # different mixing order of Textures.
    # for texture_slot_i, texture_slot in enumerate(texture_slots):

    # B. Fixed slots for Textures...
    fixed_slots_dict = {'base': 5, 'reflection': 6, 'over': 7, 'oclu': 8,
                        'mask': 9, 'mult': 10, 'iamod': 11, 'lightmap': 12,
                        'paintjob': 13, 'flakenoise': 14, 'nmap': 15}
    if texture_type in fixed_slots_dict:
        texture_slot_i = fixed_slots_dict[texture_type]
        texture_slot = texture_slots[texture_slot_i]
        # print('  texture_slot[%.2i]: %s' % (texture_slot_i, str(texture_slot)))

        if texture_slot:
            # print('   texture_slot.name: %r' % str(texture_slot.name))
            if texture_slot.name.startswith(str("scs_" + texture_type + "_")):
                if texture_slot.name == teximag_id_name:
                    slot_found = texture_slot
                else:
                    texture_slots.clear(texture_slot_i)
                    # break # Needed for "A. Method" above...

    # CREATE ABSOLUT FILEPATH
    abs_texture_filepath = _path.get_abs_path(texture_path)
    # print(' Set texture base filepath: %r' % abs_texture_filepath)

    if abs_texture_filepath and os.path.isfile(abs_texture_filepath):
        # IF SLOT EXISTS, INSPECT IT FOR VALIDITY
        # NOTE: If Blend file contains Image links from another,
        # currently unexisting location, it is needed to correct these links.
        if slot_found:
            # print(' "SLOT_FOUND" - texture_path: %r' % str(texture_path))
            # print(' "SLOT_FOUND" - abs_texture_filepath:\n\t%r' % str(abs_texture_filepath))
            # print(' "SLOT_FOUND" - teximag_id_name: %r' % str(teximag_id_name))
            # print(' "SLOT_FOUND" - texture_slot:\n\t%r' % str(texture_slot))
            correct_image_filepath(texture_slot, abs_texture_filepath)

            return

        # CREATE/FIND NEW TEXTURE
        if teximag_id_name in bpy.data.textures:

            if os.path.abspath(bpy.data.textures[teximag_id_name].image.filepath) == abs_texture_filepath:
                # REUSE EXISTING IMAGE TEXTURE
                new_texture = bpy.data.textures[teximag_id_name]
            else:  # also check all the duplicates
                postfix = 1
                postfixed_tex = teximag_id_name + "." + str(postfix).zfill(3)
                while postfixed_tex in bpy.data.textures:

                    if os.path.abspath(bpy.data.textures[postfixed_tex].image.filepath) == abs_texture_filepath:
                        # REUSE EXISTING IMAGE TEXTURE
                        new_texture = bpy.data.textures[postfixed_tex]
                        break

                    postfix += 1
                    postfixed_tex = teximag_id_name + "." + str(postfix).zfill(3)
                else:
                    # CREATE NEW IMAGE TEXTURE
                    new_texture = bpy.data.textures.new(teximag_id_name, 'IMAGE')
        else:
            # CREATE NEW IMAGE TEXTURE
            new_texture = bpy.data.textures.new(teximag_id_name, 'IMAGE')
        # print('   new_texture: %s' % str(new_texture))

        # CREATE/FIND NEW IMAGE
        if teximag_id_name in bpy.data.images.keys() and os.path.abspath(bpy.data.images[teximag_id_name].filepath) == abs_texture_filepath:
            # REUSE EXISTING IMAGE
            new_image = bpy.data.images[teximag_id_name]
        else:
            # CREATE NEW IMAGE
            new_image = bpy.data.images.load(abs_texture_filepath)
            new_image.name = teximag_id_name
        # print('   new_image: %s' % str(new_image))

        # LINK IMAGE TO IMAGE TEXTURE
        new_texture.image = new_image

        # CREATE AND SETUP NEW TEXTURE SLOT
        # for texture_slot_i, texture_slot in enumerate(texture_slots):  # Needed for "A. Method" above...
        # print('  texture_slot[%.2i]: %s' % (texture_slot_i, str(texture_slot)))
        # if not texture_slot:

        new_texture_slot = texture_slots.create(texture_slot_i)

        # LINK IMAGE TEXTURE TO TEXTURE SLOT
        new_texture_slot.texture = new_texture

        # MAKE VISUAL SETTINGS
        new_texture_slot.color = (1.0, 1.0, 1.0)
        new_image.use_alpha = False

        texture_mappings = getattr(material.scs_props, "shader_texture_" + texture_type + "_uv")
        if texture_mappings and len(texture_mappings) > 0:
            new_texture_slot.uv_layer = texture_mappings[0].value

        if texture_type == 'base':
            new_texture_slot.texture_coords = 'UV'
            new_texture_slot.use_map_color_diffuse = True
        else:
            new_texture_slot.use_map_color_diffuse = False

        if texture_type == 'reflection':
            new_texture_slot.texture_coords = 'REFLECTION'
            new_texture_slot.use_map_emit = True

        if texture_type == "mult":
            new_texture_slot.use_map_color_diffuse = True
            new_texture_slot.blend_type = "MULTIPLY"

        if texture_type == 'nmap':
            new_texture_slot.texture_coords = 'UV'
            new_texture_slot.use_map_normal = True
            new_texture_slot.normal_map_space = 'TANGENT'
            new_texture.use_normal_map = True


def get_shader_preset(shader_presets_filepath, template_name):
    """Returns requested Shader Preset data from preset file.

    :param shader_presets_filepath: A file path to SCS shader preset file, can be absolute or relative
    :type shader_presets_filepath: str
    :param template_name: Preset name
    :type template_name: str
    :return: Preset data section
    :rtype: SectionData
    """
    # print('shader_presets_filepath: %r' % shader_presets_filepath)
    if shader_presets_filepath.startswith(str(os.sep + os.sep)):  # IF RELATIVE PATH, MAKE IT ABSOLUTE
        shader_presets_filepath = _path.get_abs_path(shader_presets_filepath)
    preset_section = None
    if os.path.isfile(shader_presets_filepath):
        presets_container = _pix_container.get_data_from_file(shader_presets_filepath, '    ')
        if presets_container:
            for section in presets_container:
                if section.type == "Shader":
                    for prop in section.props:
                        if prop[0] == "PresetName":
                            if prop[1] == template_name:
                                # print(' + template name: "%s"' % template_name)
                                preset_section = section
                                break
    else:
        lprint('\nW The file path "%s" is not valid!', shader_presets_filepath)
    return preset_section


def set_env_factor(texture_slot, env_factor):
    """Sets Environment factor properties on given Material Texture Slot.

    :param texture_slot: Material Texture Slot
    :type texture_slot: MaterialTextureSlot
    :param env_factor: Environment factor attribute (3x float)
    :type env_factor: FloatVectorProperty
    """
    # texture_slot.use_map_color_diffuse = False
    # texture_slot.diffuse_color_factor = env_factor.v

    texture_slot.use_map_emit = True
    texture_slot.emit_factor = env_factor.v
    # texture_slot.emit_factor = 1.0

    texture_slot.blend_type = 'ADD'
    texture_slot.use_rgb_to_intensity = True
    texture_slot.color = env_factor


def set_diffuse(texture_slot, material, diffuse_attr):
    """Sets Diffuse color on given Material.

    :param texture_slot: Material Texture Slot
    :type texture_slot: MaterialTextureSlot
    :param material: Blender material
    :type material: Material
    :param diffuse_attr: Diffuse attribute (3x float)
    :type diffuse_attr: FloatVectorProperty
    """
    material.diffuse_color = diffuse_attr
    texture_slot.blend_type = 'MULTIPLY'


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
    :return: has_shadow, has_glass and is_other
    :rtype: tuple of bool
    """
    has_shadow = has_glass = is_other = False
    if obj.type == 'MESH':
        for slot in obj.material_slots:

            effect_name = slot.material.scs_props.mat_effect_name.lower()

            if "shadowonly" in effect_name or "fakeshadow" in effect_name or "shadowmap" in effect_name:
                has_shadow = True
            elif ".shadow" in effect_name and not ("shadowmap" in effect_name):
                has_shadow = True
                is_other = True

            if "glass" in effect_name:
                has_glass = True
        if not has_shadow and not has_glass:
            is_other = True
    return has_shadow, has_glass, is_other


def correct_blender_texture_paths():
    """
    Update of Blender image textures according to SCS texture records,
    so the images are loaded always from the correct locations.
    """
    lprint('D Update Texture Paths to SCS Base...')
    scs_project_path = _get_scs_globals().scs_project_path
    for material in bpy.data.materials:
        for prop in material.scs_props.get_shader_texture_types():
            texture_path = getattr(material.scs_props, prop)
            scs_texture_path = os.path.join(scs_project_path, texture_path[2:])
            if texture_path:
                for slot in material.texture_slots:
                    if slot:
                        postfix = prop.split('_')[-1]
                        if slot.name.startswith("scs_" + postfix):
                            image_path = slot.texture.image.filepath
                            if image_path != scs_texture_path:
                                correct_image_filepath(slot, scs_texture_path)
                                lprint('I In material %r, in its slot %r the Image file path:\n"%s"\n   ...has been changed to:\n"%s"',
                                       (material.name, slot.name, image_path, scs_texture_path))


def set_shader_data_to_material(material, section, preset_effect, is_import=False, override_back_data=True):
    """
    :param material:
    :type material: bpy.types.Material
    :param section:
    :param preset_effect:
    :return:
    """

    defined_tex_types = ("base", "flakenoise", "iamod", "lightmap", "mask", "mult", "oclu", "over", "paintjob", "reflection", "nmap")

    attributes = {}
    textures = {}
    attribute_i = 0
    texture_i = 0
    # dictionary for listing of texture types which are used and should be overlooked during clearing of texture slots
    used_texture_types = {}
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
            # APPLY PRESET ATTRIBUTE VALUES FROM PRESET
            if attribute_type == 'diffuse':
                material.scs_props.shader_attribute_diffuse = attribute_data['Value']
                if is_import:
                    material.scs_props.update_diffuse(material)
            elif attribute_type == 'specular':
                material.scs_props.shader_attribute_specular = attribute_data['Value']
                if is_import:
                    material.scs_props.update_specular(material)
            elif attribute_type == 'shininess':
                material.scs_props.shader_attribute_shininess = attribute_data['Value'][0]
                if is_import:
                    material.scs_props.update_shininess(material)
            elif attribute_type == 'add_ambient':
                material.scs_props.shader_attribute_add_ambient = attribute_data['Value'][0]
                if is_import:
                    material.scs_props.update_add_ambient(material)
            elif attribute_type == 'reflection':
                material.scs_props.shader_attribute_reflection = attribute_data['Value'][0]
                if is_import:
                    material.scs_props.update_reflection(material)
            elif attribute_type == 'reflection2':
                material.scs_props.shader_attribute_reflection2 = attribute_data['Value'][0]
                if is_import:
                    material.scs_props.update_reflection(material)
            elif attribute_type == 'shadow_bias':
                material.scs_props.shader_attribute_shadow_bias = attribute_data['Value'][0]
                if is_import:
                    material.scs_props.update_shadow_bias(material)
            elif attribute_type == 'env_factor':
                material.scs_props.shader_attribute_env_factor = attribute_data['Value']
                if is_import:
                    material.scs_props.update_env_factor(material)
            elif attribute_type == 'fresnel':
                material.scs_props.shader_attribute_fresnel = attribute_data['Value']
            elif attribute_type == 'tint':
                material.scs_props.shader_attribute_tint = attribute_data['Value']
            elif attribute_type == 'tint_opacity':
                material.scs_props.shader_attribute_tint_opacity = attribute_data['Value'][0]
            elif attribute_type in ("aux3", "aux5", "aux6", "aux7", "aux8"):

                auxiliary_prop = getattr(material.scs_props, "shader_attribute_" + attribute_type, None)

                # clean old values possible left from previous shader
                while len(auxiliary_prop) > 0:
                    auxiliary_prop.remove(0)

                for val in attribute_data['Value']:
                    item = auxiliary_prop.add()
                    item.value = val

            attributes[str(attribute_i)] = attribute_data
            attribute_i += 1

        elif item.type == "Texture":
            texture_data = {}
            for prop in item.props:
                # print('      prop: "%s"' % str(prop))
                texture_data[prop[0]] = prop[1]

            # APPLY SECTION TEXTURE VALUES
            texture_type = texture_data['Tag'].split(':')[1]
            slot_id = texture_type[8:]

            # set only defined textures
            if slot_id in defined_tex_types:

                texture_mappings = getattr(material.scs_props, "shader_texture_" + slot_id + "_uv")

                # clear all texture mapping for current texture from previous shader
                if override_back_data:
                    while len(texture_mappings) > 0:
                        texture_mappings.remove(0)

                # if shader is imported try to create custom tex coord mappings on material
                if material.scs_props.active_shader_preset_name == "<imported>" and "scs_tex_aliases" in material:
                    custom_maps = material.scs_props.shader_custom_tex_coord_maps

                    for tex_coord_key in sorted(material["scs_tex_aliases"].keys()):

                        if _invetory.get_index(custom_maps, "tex_coord_" + tex_coord_key) == -1:
                            new_map = custom_maps.add()
                            new_map.name = "tex_coord_" + tex_coord_key
                            new_map.value = material["scs_tex_aliases"][tex_coord_key]

                    # add one mapping field for using it as a preview uv layer in case of imported shader
                    mapping = texture_mappings.add()
                    mapping.texture_type = slot_id
                    mapping.tex_coord = -1

                # if there is an info about mapping in shader use it (in case of imported material this condition will fall!)
                elif "TexCoord" in texture_data:

                    for tex_coord in texture_data['TexCoord']:
                        tex_coord = int(tex_coord)

                        if tex_coord != -1:
                            mapping = texture_mappings.add()
                            mapping.texture_type = slot_id
                            mapping.tex_coord = tex_coord

                            if "scs_tex_aliases" in material:
                                mapping.value = material["scs_tex_aliases"][str(tex_coord)]

                used_texture_types[slot_id] = 1

                bitmap_filepath = _path.get_bitmap_filepath(texture_data['Value'])

                if bitmap_filepath and bitmap_filepath != "":
                    setattr(material.scs_props, "shader_texture_" + slot_id, bitmap_filepath)

                    if is_import:
                        update_texture_slots(material, bitmap_filepath, slot_id)
                        setattr(material.scs_props, "shader_texture_" + slot_id + "_use_imported", True)
                        setattr(material.scs_props, "shader_texture_" + slot_id + "_imported_tobj", texture_data['Value'])

                    texture_slot = get_texture_slot(material, slot_id)
                    if slot_id == 'base' and texture_slot:
                        set_diffuse(texture_slot, material, material.scs_props.shader_attribute_diffuse)
                    elif slot_id == 'reflection' and texture_slot:
                        set_env_factor(texture_slot, material.scs_props.shader_attribute_env_factor)

            textures[str(texture_i)] = texture_data
            texture_i += 1

    if override_back_data:

        # clear texture slots for unused textures from previous preset
        for tex_type in defined_tex_types:
            if tex_type not in used_texture_types:  # delete unused texture slots
                clear_texture_slots(material, tex_type)

        shader_data = {'effect': preset_effect,
                       'attributes': attributes,
                       'textures': textures}
        material["scs_shader_attributes"] = shader_data


'''
def get_cgfx_template(cgfx_templates_filepath, template_name):
    """Returns requested CgFX template data from template file."""
    #print('cgfx_templates_filepath: %r' % cgfx_templates_filepath)
    if cgfx_templates_filepath.startswith(str(os.sep + os.sep)):  # IF RELATIVE PATH, MAKE IT ABSOLUTE
        cgfx_templates_filepath = get_abs_path(cgfx_templates_filepath)
    template_section = None
    if os.path.isfile(cgfx_templates_filepath):
        templates_container = get_data_container_from_file(cgfx_templates_filepath, '    ')
        if templates_container:
            for section in templates_container:
                if section.type == "Shader":
                    for prop in section.props:
                        if prop[0] == "TemplateName":
                            if prop[1] == template_name:
                                #print(' + template name: "%s"' % template_name)
                                template_section = section
                                break
    else:
        Print(4, '\nW The file path "%s" is not valid!', cgfx_templates_filepath)
    return template_section


def update_cgfx_template_path(cgfx_templates_filepath):
    """Takes absolute or relative path to the file with CgFX Templates.
    The function deletes and populates again a list of CgFX template
    items in inventory. It also updates corresponding record in config file."""
    #print('cgfx_templates_filepath: %r' % cgfx_templates_filepath)
    if cgfx_templates_filepath.startswith(str(os.sep + os.sep)): # RELATIVE PATH
        cgfx_templates_abs_path = get_abs_path(cgfx_templates_filepath)
    else:
        cgfx_templates_abs_path = cgfx_templates_filepath

    if os.path.isfile(cgfx_templates_abs_path):

        # CLEAR INVENTORY
        bpy.context.scene.scs_cgfx_template_inventory.clear()

        # ADD DEFAULT TEMPLATE ITEM "<custom>" INTO INVENTORY
        new_cgfx_template = bpy.context.scene.scs_cgfx_template_inventory.add()
        new_cgfx_template.name = "<custom>"
        new_cgfx_template.active = True
        templates_container = get_data_container_from_file(cgfx_templates_abs_path, '    ')

        # ADD ALL TEMPLATE ITEMS FROM FILE INTO INVENTORY
        if templates_container:
            for section in templates_container:
                if section.type == "Shader":
                    for prop in section.props:
                        if prop[0] == "TemplateName":
                            template_name = prop[1]
                            #print(' + template name: "%s"' % template_name)
                            new_cgfx_template = bpy.context.scene.scs_cgfx_template_inventory.add()
                            new_cgfx_template.name = template_name
    else:
        Print(4, '\nW The file path "%s" is not valid!', cgfx_templates_abs_path)

    update_item_in_file(get_config_filepath(), 'Paths.CgFXTemplatesFilePath', cgfx_templates_filepath)


def update_cgfx_library_rel_path(cgfx_library_rel_path):
    """Takes a relative path to the directory with CgFX files.
    The function deletes and populates again a list of CgFX names in inventory.
    It also updates corresponding record in config file."""
    abs_path = get_abs_path(cgfx_library_rel_path)
    if abs_path:

        # CLEAR INVENTORY
        bpy.context.scene.scs_cgfx_inventory.clear()

        # ADD ALL "CGFX" FILES FROM FOLDER INTO INVENTORY
        for root, dirs, files in os.walk(abs_path):
            # print('   root: "%s"\n  dirs: "%s"\n files: "%s"' % (root, dirs, files))
            for file in files:
                if file.endswith(".cgfx"):
                    cgfx_file = bpy.context.scene.scs_cgfx_inventory.add()
                    cgfx_file.name = file[:-5]
                    cgfx_file.filepath = os.path.join(root, file)
            if '.svn' in dirs:
                dirs.remove('.svn') # ignore SVN

    update_item_in_file(get_config_filepath(), 'Paths.CgFXRelDirPath', cgfx_library_rel_path)
'''