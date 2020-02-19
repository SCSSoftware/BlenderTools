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

import bmesh
import bpy
import os
import tempfile
from math import pi
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.imp import tobj as _tobj_imp
from io_scs_tools.internals import inventory as _invetory
from io_scs_tools.internals import shader_presets as _shader_presets
from io_scs_tools.internals.shaders import shader as _shader
from io_scs_tools.utils import path as _path
from io_scs_tools.utils.printout import lprint


def get_texture_image(texture_path, texture_type, report_invalid=False):
    """Creates and returns image for given texture path and type.

    :param texture_path: Texture path
    :type texture_path: str
    :param texture_type: Texture type keyword
    :type texture_type: str
    :param report_invalid: flag indicating if invalid texture should be reported in 3d view
    :type report_invalid: bool
    :return: loaded image datablock to be used in SCS material
    :rtype: bpy.types.Image
    """

    # get reflection image texture
    if texture_path.endswith(".tobj") and texture_type == "reflection":
        return get_reflection_image(texture_path, report_invalid=report_invalid)

    # CREATE TEXTURE/IMAGE ID NAME
    teximag_id_name = _path.get_filename(texture_path, with_ext=False)

    # CREATE ABSOLUTE FILEPATH
    abs_texture_filepath = _path.get_abs_path(texture_path)

    # return None on non-existing texture file path
    if not abs_texture_filepath or not os.path.isfile(abs_texture_filepath):
        return None

    if abs_texture_filepath.endswith(".tobj"):
        abs_texture_filepath = _path.get_texture_path_from_tobj(abs_texture_filepath)

        # if not existing or none supported file
        if abs_texture_filepath is None or abs_texture_filepath[-4:] not in (".tga", ".png", ".dds"):

            if report_invalid:
                lprint("", report_warnings=-1, report_errors=-1)

            # take care of none existing paths referenced in tobj texture names
            if abs_texture_filepath:

                lprint("W Texture can't be displayed as TOBJ file: %r is referencing non texture file:\n\t   %r",
                       (texture_path, _path.readable_norm(abs_texture_filepath)))

            else:

                lprint("W Texture can't be displayed as TOBJ file: %r is referencing non existing texture file.",
                       (texture_path,))

            if report_invalid:
                lprint("", report_warnings=1, report_errors=1)

            return None

    image = None
    if abs_texture_filepath and os.path.isfile(abs_texture_filepath):

        # reuse existing image texture if possible
        postfix = 0
        postfixed_tex = teximag_id_name
        while postfixed_tex in bpy.data.images:

            img_exists = postfixed_tex in bpy.data.images
            if img_exists and _path.repair_path(bpy.data.images[postfixed_tex].filepath) == _path.repair_path(abs_texture_filepath):
                image = bpy.data.images[postfixed_tex]
                break

            postfix += 1
            postfixed_tex = teximag_id_name + "." + str(postfix).zfill(3)

        # if image wasn't found create new one
        if not image:

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
                image.alpha_mode = 'CHANNEL_PACKED'

                # try to get relative path to the Blender file and set it to the image
                if bpy.data.filepath != '':  # empty file path means blender file is not saved
                    try:
                        rel_path = _path.relative_path(os.path.dirname(bpy.data.filepath), abs_texture_filepath)
                    except ValueError:  # catch different mount paths: "path is on mount 'C:', start on mount 'E:'"
                        rel_path = None

                    if rel_path:
                        image.filepath = rel_path

    if image is None and texture_path.endswith(".tobj"):
        if report_invalid:
            lprint("", report_warnings=-1, report_errors=-1)

        lprint("W Texture can't be displayed as TOBJ file: %r is referencing non existing texture file:\n\t   %r",
               (texture_path, _path.readable_norm(abs_texture_filepath)))

        if report_invalid:
            lprint("", report_warnings=1, report_errors=1)

    return image


def get_reflection_image(texture_path, report_invalid=False):
    """Gets reflection image for given texture path.

    1. gets all textures names and check existance
    2. create image objects for all planes
    3. setup scene, create planes, create camera projector and assign images
    4. render & save image
    5. cleanup & scene restoring
    6. load temp image and pack it
    7. set filepath to TOBJ

    :param texture_path: Texture path
    :type texture_path: str
    :param report_invalid: flag indicating if invalid texture should be reported in 3d view
    :type report_invalid: bool
    :return: loaded image datablock to be used in SCS material
    :rtype: bpy.types.Image
    """

    # CREATE TEXTURE/IMAGE ID NAME
    teximag_id_name = _path.get_filename(texture_path, with_ext=False) + "_cubemap"

    # CREATE ABSOLUTE FILEPATH
    abs_tobj_filepath = _path.get_abs_path(texture_path)

    # return None on non-existing TOBJ
    if not abs_tobj_filepath or not os.path.isfile(abs_tobj_filepath):
        return None

    # 1. reuse existing image texture if possible, otherwise construct first free slot

    postfix = 0
    postfixed_tex = teximag_id_name
    while postfixed_tex in bpy.data.images:

        img_exists = postfixed_tex in bpy.data.images
        if img_exists and _path.repair_path(bpy.data.images[postfixed_tex].filepath) == _path.repair_path(abs_tobj_filepath):
            return bpy.data.images[postfixed_tex]

        postfix += 1
        postfixed_tex = teximag_id_name + "." + str(postfix).zfill(3)

    teximag_id_name = postfixed_tex

    # 2. get all textures file paths and check their existance

    abs_texture_filepaths = _path.get_texture_paths_from_tobj(abs_tobj_filepath)

    # should be a cubemap with six images
    if not abs_texture_filepaths or len(abs_texture_filepaths) != 6:
        return None

    # all six images have to exist
    for abs_texture_filepath in abs_texture_filepaths:

        if abs_texture_filepath[-4:] not in (".tga", ".png", ".dds"):  # none supported file

            if report_invalid:
                lprint("", report_warnings=-1, report_errors=-1)

            lprint("W Texture can't be displayed as TOBJ file: %r is referencing non texture file:\n\t   %r",
                   (texture_path, _path.readable_norm(abs_texture_filepath)))

            if report_invalid:
                lprint("", report_warnings=1, report_errors=1)

            return None

        elif not os.path.isfile(abs_texture_filepath):  # none existing file

            if report_invalid:
                lprint("", report_warnings=-1, report_errors=-1)

            # take care of none existing paths referenced in tobj texture names
            lprint("W Texture can't be displayed as TOBJ file: %r is referencing non existing texture file:\n\t   %r",
                   (texture_path, _path.readable_norm(abs_texture_filepath)))

            if report_invalid:
                lprint("", report_warnings=1, report_errors=1)

            return None

    # 3. create image objects for all planes

    images = []
    for abs_texture_filepath in abs_texture_filepaths:
        images.append(bpy.data.images.load(abs_texture_filepath))

    # 4. setup scene, create planes, create camera projector and assign images

    old_scene = bpy.context.window.scene
    tmp_scene = bpy.data.scenes.new("cubemap")
    bpy.context.window.scene = tmp_scene

    meshes = []
    materials = []
    objects = []
    for i, plane in enumerate(("x+", "x-", "y+", "y-", "z+", "z-")):
        # mesh creation
        bm = bmesh.new(use_operators=True)

        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1, calc_uvs=True)

        mesh = bpy.data.meshes.new(plane)
        bm.to_mesh(mesh)
        bm.free()

        mesh.uv_layers.new()

        meshes.append(mesh)

        # material creation
        material = bpy.data.materials.new(plane)
        material.use_nodes = True
        material.node_tree.nodes.clear()

        out_node = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
        emission_node = material.node_tree.nodes.new("ShaderNodeEmission")
        tex_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = images[i]

        material.node_tree.links.new(emission_node.inputs['Color'], tex_node.outputs['Color'])
        material.node_tree.links.new(out_node.inputs['Surface'], emission_node.outputs['Emission'])

        mesh.materials.append(material)

        materials.append(material)

        # object creation
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.location = (0,) * 3
        obj.rotation_euler = (0,) * 3
        if plane == "x+":
            obj.rotation_euler.x = pi * 0.5
            obj.location.y = 1
        elif plane == "x-":
            obj.rotation_euler.x = pi * 0.5
            obj.rotation_euler.z = pi
            obj.location.y = -1
        elif plane == "y+":
            obj.rotation_euler.x = pi
            obj.rotation_euler.z = pi * 0.5
            obj.location.z = 1
        elif plane == "y-":
            obj.rotation_euler.z = pi * 0.5
            obj.location.z = -1
        elif plane == "z+":
            obj.rotation_euler.x = pi * 0.5
            obj.rotation_euler.z = pi * 0.5
            obj.location.x = -1
        elif plane == "z-":
            obj.rotation_euler.x = pi * 0.5
            obj.rotation_euler.z = -pi * 0.5
            obj.location.x = 1

        tmp_scene.collection.objects.link(obj)
        objects.append(obj)

    # camera creation
    camera = bpy.data.cameras.new("projector")
    camera.type = "PANO"
    camera.lens = 5
    camera.sensor_width = 32
    camera.cycles.panorama_type = "EQUIRECTANGULAR"
    camera.cycles.latitude_min = -pi * 0.5
    camera.cycles.latitude_max = pi * 0.5
    camera.cycles.longitude_min = pi
    camera.cycles.longitude_max = -pi

    cam_obj = bpy.data.objects.new(camera.name, camera)
    cam_obj.location = (0,) * 3
    cam_obj.rotation_euler = (pi * 0.5, 0, 0)

    tmp_scene.collection.objects.link(cam_obj)

    # 5. render & save image

    final_image_path = os.path.join(tempfile.gettempdir(), teximag_id_name + ".tga")

    tmp_scene.render.engine = "CYCLES"
    tmp_scene.cycles.samples = 1
    tmp_scene.camera = cam_obj
    tmp_scene.render.image_settings.file_format = "TARGA"
    tmp_scene.render.image_settings.color_mode = "RGBA"
    tmp_scene.render.resolution_percentage = 100
    tmp_scene.render.resolution_x = images[0].size[0] * 4
    tmp_scene.render.resolution_y = images[0].size[1] * 2
    tmp_scene.render.filepath = final_image_path
    bpy.ops.render.render(write_still=True, scene=tmp_scene.name)

    # 6. cleanup & scene restoring

    for obj in objects:
        bpy.data.objects.remove(obj)

    for mesh in meshes:
        bpy.data.meshes.remove(mesh)

    for material in materials:
        bpy.data.materials.remove(material)

    for image in images:
        bpy.data.images.remove(image)

    bpy.data.objects.remove(cam_obj)
    bpy.data.cameras.remove(camera)

    bpy.context.window.scene = old_scene
    bpy.data.scenes.remove(tmp_scene)

    # 7. load temp image and pack it

    final_image = bpy.data.images.load(final_image_path)
    final_image.name = teximag_id_name
    final_image.alpha_mode = 'CHANNEL_PACKED'
    final_image.pack()

    # 8. set filepath to original image
    final_image.filepath = abs_tobj_filepath

    return final_image


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

        elif attribute_type in ("shininess", "add_ambient", "reflection", "reflection2", "shadow_bias", "tint_opacity", "queue_bias"):

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
    created_tex_settings = {}
    created_tex_mappings = []
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

                        # if mesh is corrupted then tex aliases won't be filled in properly in material from PIM importer,
                        # so report error and skip creation of texture mapping for current tex_coord.
                        if str(tex_coord) not in material["scs_tex_aliases"]:
                            lprint("E Material %r is missing texture coordinate aliases, some UV mappings in Material Textures will remain empty!",
                                   (material.name,))
                            continue

                        mapping['value'] = material["scs_tex_aliases"][str(tex_coord)]
                        created_tex_mappings.append((tex_type, mapping.value, tex_coord))

                    elif tex_coord in old_texture_mappings:

                        mapping['value'] = old_texture_mappings[tex_coord]
                        created_tex_mappings.append((tex_type, mapping.value, tex_coord))

        # set texture file to current texture
        scs_texture_str = _path.get_scs_texture_str(texture_data['Value'])

        # apply texture path if not empty and not yet set, except if import is going on
        # NOTE: during import bitmap has to be applied even if empty
        # because otherwise texture from previous look might be applied
        if (scs_texture_str != "" and getattr(material.scs_props, "shader_texture_" + tex_type, "") == "") or is_import:
            material.scs_props["shader_texture_" + tex_type] = scs_texture_str
            created_textures[tex_type] = get_texture_image(scs_texture_str, tex_type)

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
            created_textures[tex_type] = get_texture_image(final_tex_str, tex_type)

            if is_import and not override_back_data:

                if created_textures[tex_type] is None:
                    lprint("E Can't find texture nor TOBJ inside SCS Project Base Path: %r", (final_tex_str,))

        # now try to retrive settings for the textures from TOBJ
        if tex_type in created_textures and created_textures[tex_type]:
            final_tex_str = getattr(material.scs_props, "shader_texture_" + tex_type, "")
            tobj_abs_path = _path.get_tobj_path_from_shader_texture(final_tex_str)
            settings, map_type = _tobj_imp.get_settings_and_type(tobj_abs_path)
            created_tex_settings[tex_type] = settings

    # override shader data for identifying used attributes and textures in UI
    if override_back_data:

        shader_data = {'effect': preset_effect,
                       'attributes': attributes,
                       'textures': textures}
        material["scs_shader_attributes"] = shader_data

    # setup nodes for 3D view visualization
    _shader.setup_nodes(material, preset_effect, created_attributes, created_textures, created_tex_settings, override_back_data)

    # setup uv mappings to nodes later trough dedicated function, so proper validation is made on tex coord bindings
    for mapping_data in created_tex_mappings:

        # data[0] = texture type;
        # data[1] = uv mapping value;
        # data[2] = tex coord value
        _shader.set_uv(material, mapping_data[0], mapping_data[1], mapping_data[2])


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

        # apply reloaded settings to shader
        _shader.set_texture_settings(material, tex_type, settings)


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

        if _shader_presets.has_effect(curr_substr) and len(curr_substr) > len(longest_match):
            longest_match = curr_substr

    # nothing matched
    if len(longest_match) == 0:
        return None, None

    # use longest base effect match and search for a match inside flavors
    preset_sections = _shader_presets.find_sections(longest_match, material_effect[len(longest_match):])
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


def set_texture_settings_to_node(tex_node, settings):
    """Sets TOBJ settings to given texture node and it's assigned image.

    :param tex_node: texture image node to which settings should be applied
    :type tex_node: bpy.types.ShaderNodeTexImage
    :param settings: binary string of TOBJ settings gotten from tobj import
    :type settings: str
    """

    # addr - repeating
    if settings[2] == "1" and settings[3] == "1":
        tex_node.extension = "REPEAT"
    else:
        tex_node.extension = "EXTEND"

    image = tex_node.image

    # image settings can't be done without image object thus end here
    if not image:
        return

    # linear colorspace
    if settings[0] == "1":
        image.colorspace_settings.name = "Linear"
    else:
        image.colorspace_settings.name = "sRGB"

    # tsnormal option
    if settings[1] == "1":
        if image.filepath[-4:] in (".tga", ".dds"):
            image.colorspace_settings.name = "Non-Color"
        elif image.filepath[-4:] == ".png" and image.is_float:
            image.colorspace_settings.name = "Linear"


def has_valid_color_management(scene):
    """Gets validity of color management for rendering SCS object.

    :param scene: scene for which we are checking validity
    :type scene: bpy.types.Scene
    :return: True if scene colormanagement is valid; False otherwise
    :rtype: bool
    """

    if not scene:
        return False

    display_settings = scene.display_settings
    view_settings = scene.view_settings

    is_proper_display_device = display_settings.display_device == "sRGB"
    is_proper_view_transform = view_settings.view_transform == "Standard"
    is_proper_look = view_settings.look == "None"
    is_proper_exposure = view_settings.exposure == 0.0
    is_proper_gamma = view_settings.gamma == 1.0

    valid_color_management = (
            is_proper_display_device and
            is_proper_view_transform and
            is_proper_look and
            is_proper_exposure and
            is_proper_gamma
    )
    return valid_color_management
