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

import os

import bpy
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.imp import tobj as _tobj_imp
from io_scs_tools.internals import inventory as _invetory
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.internals.shaders import shader as _shader
from io_scs_tools.utils import path as _path
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def is_valid_shader_texture_path(shader_texture, tobj_check=False):
    """It returns True if there is valid Shader Texture file, otherwise False.

    :param shader_texture: SCS texture path, can be absolute or relative
    :type shader_texture: str
    :return: True if there is valid Shader Texture file, otherwise False
    :rtype: bool
    """
    if shader_texture != "":

        if tobj_check and (shader_texture.endswith(".tga") or shader_texture.endswith(".png")):
            shader_texture = shader_texture[:-4] + ".tobj"

        if shader_texture.startswith("//"):  # RELATIVE PATH
            shader_texture_abs_path = _path.get_abs_path(shader_texture)
            if shader_texture_abs_path:
                if os.path.isfile(shader_texture_abs_path):
                    return True
        else:  # ABSOLUTE PATH
            if os.path.isfile(shader_texture):
                return True

    return False


def correct_image_filepath(texture_slot, abs_texture_filepath):
    """Takes a Texture slot and correct absolut filepath of an Image and applies it on Texture in provided slot.
    Then the function performs image reload.

    :param texture_slot: Texture Slot in active Material
    :type texture_slot: bpy.types.TextureSlot
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


def get_texture(texture_path, texture_type):
    """Creates and setup Texture and Image data on active Material.

    :param texture_path: Texture path
    :type texture_path: str
    :param texture_type: Texture type keyword
    :type texture_type: str
    """
    # print(' texture_path: %s' % str(texture_path))

    # CREATE TEXTURE/IMAGE ID NAME
    teximag_id_name = _path.get_filename(texture_path, with_ext=False)

    # CREATE ABSOLUTE FILEPATH
    abs_texture_filepath = _path.get_abs_path(texture_path)

    texture = None
    if abs_texture_filepath and os.path.isfile(abs_texture_filepath):

        # find existing texture with this image
        if teximag_id_name in bpy.data.textures:

            # reuse existing image texture if possible
            postfix = 0
            postfixed_tex = teximag_id_name
            while postfixed_tex in bpy.data.textures:

                if _path.repair_path(bpy.data.textures[postfixed_tex].image.filepath) == _path.repair_path(abs_texture_filepath):
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

        # normal map related settings
        if texture_type == "nmap":
            texture.image.colorspace_settings.name = "Raw"
            texture.use_normal_map = True
        else:
            texture.image.colorspace_settings.name = "sRGB"
            texture.use_normal_map = False

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
    :return: has_shadow, has_glass and is_other
    :rtype: tuple of bool
    """
    has_shadow = has_glass = is_other = False
    if obj.type == 'MESH':
        for slot in obj.material_slots:

            if slot.material:

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
        for tex_type in material.scs_props.get_texture_types().keys():
            texture_path = getattr(material.scs_props, "shader_texture_" + tex_type)
            scs_texture_path = os.path.join(scs_project_path, texture_path[2:])
            if texture_path:
                for slot in material.texture_slots:
                    if slot:
                        if slot.name.startswith("scs_" + tex_type):
                            image_path = slot.texture.image.filepath
                            if image_path != scs_texture_path:
                                correct_image_filepath(slot, scs_texture_path)
                                lprint('I In material %r, in its slot %r the Image file path:\n"%s"\n   ...has been changed to:\n"%s"',
                                       (material.name, slot.name, image_path, scs_texture_path))


def set_shader_data_to_material(material, section, preset_effect, is_import=False, override_back_data=True):
    """Used to set up material properties from given shader data even via UI or on import.
    :param material:
    :type material: bpy.types.Material
    :param section:
    :param preset_effect:
    :return:
    """

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

    # clear attribute values for current shader to be stored in blend data block
    # NOTE: looks also takes into account that all the unused properties are omitted from scs_props dict
    scs_props_keys = material.scs_props.keys()
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
        if attribute_type in ("diffuse", "specular", "env_factor", "fresnel", "tint"):

            material.scs_props["shader_attribute_" + attribute_type] = attribute_data['Value']
            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type in ("shininess", "add_ambient", "reflection", "reflection2", "shadow_bias", "tint_opacity"):

            material.scs_props["shader_attribute_" + attribute_type] = attribute_data['Value'][0]
            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type.startswith("aux") and hasattr(material.scs_props, "shader_attribute_" + attribute_type):

            auxiliary_prop = getattr(material.scs_props, "shader_attribute_" + attribute_type, None)

            # clean old values possible left from previous shader
            while len(auxiliary_prop) > 0:
                auxiliary_prop.remove(0)

            for val in attribute_data['Value']:
                item = auxiliary_prop.add()
                item['value'] = val
                item['aux_type'] = attribute_type

            created_attributes[attribute_type] = material.scs_props["shader_attribute_" + attribute_type]

        elif attribute_type == "substance":

            material.scs_props.substance = attribute_data['Value'][0]

    # if shader attribute properties are still unset reset it to default
    if material.scs_props.substance == _MAT_consts.unset_substance and "substance" not in material.scs_props.keys():
        material.scs_props.substance = "None"

    # apply used textures
    created_textures = {}
    created_tex_uvs = {}
    for tex_type in used_texture_types:
        texture_data = used_texture_types[tex_type]

        if tex_type in material.scs_props.get_texture_types().keys():

            if "Lock" in texture_data:
                setattr(material.scs_props, "shader_texture_" + tex_type + "_locked", bool(texture_data["Lock"]))

            texture_mappings = getattr(material.scs_props, "shader_texture_" + tex_type + "_uv")
            # clear all texture mapping for current texture from previous shader
            if override_back_data:
                while len(texture_mappings) > 0:
                    texture_mappings.remove(0)

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

                for tex_coord in texture_data['TexCoord']:
                    tex_coord = int(tex_coord)

                    if tex_coord != -1:
                        mapping = texture_mappings.add()
                        mapping.texture_type = tex_type
                        mapping.tex_coord = tex_coord

                        if "scs_tex_aliases" in material:
                            mapping.value = material["scs_tex_aliases"][str(tex_coord)]

                            # for now make sure to use only first coord mapping info for shader
                            if len(texture_mappings) == 1:
                                created_tex_uvs[tex_type] = mapping.value

            # set bitmap file to current texture
            bitmap_filepath = _path.get_bitmap_filepath(texture_data['Value'])

            # apply texture path if not empty, except if import is going on
            # NOTE: during import bitmap has to be applied even if empty
            # because otherwise texture from previous look might be applied
            if (bitmap_filepath and bitmap_filepath != "") or is_import:
                material.scs_props["shader_texture_" + tex_type] = bitmap_filepath
                created_textures[tex_type] = get_texture(bitmap_filepath, tex_type)

                if is_import:

                    # only if shader is imported then make sure that by default imported values will be used
                    if material.scs_props.active_shader_preset_name == "<imported>":
                        setattr(material.scs_props, "shader_texture_" + tex_type + "_use_imported", True)
                        setattr(material.scs_props, "shader_texture_" + tex_type + "_imported_tobj", texture_data['Value'])

            # if property is still unset reset it to empty
            if getattr(material.scs_props, "shader_texture_" + tex_type, "") == _MAT_consts.unset_bitmap_filepath:
                material.scs_props["shader_texture_" + tex_type] = ""
            else:
                bitmap_filepath = _path.get_abs_path(getattr(material.scs_props, "shader_texture_" + tex_type, ""))
                created_textures[tex_type] = get_texture(bitmap_filepath, tex_type)

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

    if is_valid_shader_texture_path(shader_texture_filepath, tobj_check=True):

        tobj_file = _path.get_abs_path(shader_texture_filepath[:-4] + ".tobj")
        # intentionally set ID property directly to avoid update function invoke
        material.scs_props[shader_texture_str + "_settings"] = int(_tobj_imp.get_settings(tobj_file), 2)
        setattr(material.scs_props, shader_texture_str + "_tobj_load_time", str(os.path.getmtime(tobj_file)))


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
