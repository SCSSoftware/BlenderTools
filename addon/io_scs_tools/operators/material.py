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

from importlib.machinery import SourceFileLoader
import bpy
import os
from bpy.props import StringProperty, BoolProperty
from io_scs_tools.exp import tobj as _tobj_exp
from io_scs_tools.internals import looks as _looks
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.property import get_filebrowser_display_type


class Common:
    """
    Wrapper class for better navigation in file
    """

    class ReloadMaterials(bpy.types.Operator):
        bl_label = "Reload SCS Materials"
        bl_idname = "material.scs_reload_nodes"
        bl_description = "Reload node trees & any shader interface changes for all SCS materials in blend file."

        def execute(self, context):

            # find group names created by Blender Tools with
            # dynamic importing of all modules from "internals/shaders" folder
            # and checking if module has "get_node_group" functions which indicates that
            # module creates node group
            groups_to_remove = [
                "AddEnvGroup",  # from v0.6
                "FresnelGroup",  # from v0.6
                "LampmaskMixerGroup",  # from v0.6
                "ReflectionNormalGroup",  # from v0.6
            ]
            for root, dirs, files in os.walk(_path_utils.get_addon_installation_paths()[0] + os.sep + "internals/shaders"):

                for file in files:

                    if not file.endswith(".py"):
                        continue

                    module = SourceFileLoader(root + os.sep + file, root + os.sep + file).load_module()
                    if "get_node_group" in dir(module):

                        ng = module.get_node_group()
                        groups_to_remove.append(ng.name)

            # 1. clear nodes on materials
            for mat in bpy.data.materials:

                if not mat.node_tree:
                    continue

                if mat.scs_props.active_shader_preset_name == "<none>":

                    nodes_to_remove = []

                    # check for possible leftover usage of our node groups
                    for node in mat.node_tree.nodes:

                        # filter out nodes which are not node group and node groups without node tree
                        if node.type != "GROUP" or not node.node_tree:
                            continue

                        if node.node_tree.name in groups_to_remove:
                            nodes_to_remove.append(node.node_tree.name)

                    # remove possible leftover used node group nodes
                    for node_name in nodes_to_remove:
                        mat.node_tree.nodes.remove(mat.node_tree.nodes[node_name])

                    continue

                mat.node_tree.nodes.clear()

            # 2. clear nodes on node groups
            for ng_name in groups_to_remove:

                if ng_name not in bpy.data.node_groups:
                    continue

                ng = bpy.data.node_groups[ng_name]
                ng.nodes.clear()

            # 3. remove node groups from blender data blocks
            for ng_name in groups_to_remove:

                if ng_name not in bpy.data.node_groups:
                    continue

                bpy.data.node_groups.remove(bpy.data.node_groups[ng_name])

            # 4. finally set preset to material again, which will update nodes and possible input interface changes
            for mat in bpy.data.materials:

                if mat.scs_props.active_shader_preset_name == "<none>":
                    continue

                material_textures = {}
                if "scs_shader_attributes" in mat and "textures" in mat["scs_shader_attributes"]:
                    for texture in mat["scs_shader_attributes"]["textures"].values():
                        tex_id = texture["Tag"].split(":")[1]
                        tex_value = texture["Value"]
                        material_textures[tex_id] = tex_value

                (preset_name, preset_section) = _material_utils.find_preset(mat.scs_props.mat_effect_name, material_textures)

                if preset_section:
                    _material_utils.set_shader_data_to_material(mat, preset_section)

            return {'FINISHED'}


class CustomMapping:
    """
    Wrapper class for better navigation in file
    """

    class AddCustomMapping(bpy.types.Operator):
        bl_label = "Add Custom TexCoord Mapping"
        bl_idname = "material.add_custom_tex_coord_map"
        bl_description = "Add custom TexCoord mapping to list"
        bl_options = {'INTERNAL'}

        def execute(self, context):
            material = context.active_object.active_material

            if material:
                item = material.scs_props.custom_tex_coord_maps.add()
                item.name = "text_coord_x"

            return {'FINISHED'}

    class RemoveCustomMapping(bpy.types.Operator):
        bl_label = "Remove Custom TexCoord Mapping"
        bl_idname = "material.remove_custom_tex_coord_map"
        bl_description = "Remove selected custom TexCoord mapping from list"
        bl_options = {'INTERNAL'}

        def execute(self, context):
            material = context.active_object.active_material

            if material:

                material.scs_props.custom_tex_coord_maps.remove(material.scs_props.active_custom_tex_coord)

            return {'FINISHED'}


class Looks:
    """
    Wrapper class for better navigation in file
    """

    class WriteThrough(bpy.types.Operator):
        bl_label = "Write Through"
        bl_idname = "material.scs_looks_wt"
        bl_description = ("Write current material value through all currently defined looks within SCS Game Object "
                          "( Ctrl + Click to WT on other SCS Root Objects on same look, "
                          "Ctrl + Shift + Click to WT all looks of all SCS Root Objects )"
                          )
        property_str = StringProperty(
            description="String representing which property should be written through.",
            default="",
            options={'HIDDEN'},
        )

        is_ctrl = False  # WT to same look of this material in other SCS Roots
        is_shift = False  # is_shift + is_ctrl ->  WT to all looks of this material in all SCS Roots

        def execute(self, context):
            material = context.active_object.active_material

            if not material or not hasattr(material.scs_props, self.property_str):
                return {'CANCELLED'}

            scs_roots = []
            active_scs_root = _object_utils.get_scs_root(context.active_object)
            if active_scs_root:
                scs_roots.append(active_scs_root)

            if self.is_ctrl:
                scs_roots = _object_utils.gather_scs_roots(bpy.data.objects)

            if self.is_shift or not self.is_ctrl:  # WT either on active only or all SCS roots; (Shift + Ctrl) or none

                altered_looks = 0
                for scs_root in scs_roots:
                    altered_looks += _looks.write_through(scs_root, material, self.property_str)

                if altered_looks > 0:
                    message = "Write through successfully altered %s looks on %s SCS Root Objects!" % (altered_looks, len(scs_roots))
                else:
                    message = "Nothing to write through."

                self.report({'INFO'}, message)

            elif self.is_ctrl:  # special WT only into the same look of other SCS Roots

                # get current look id
                look_i = active_scs_root.scs_props.active_scs_look
                look_name = active_scs_root.scs_object_look_inventory[look_i].name if look_i >= 0 else None

                if look_name is None:
                    self.report({'WARNING'}, "Aborting as current object is not in any SCS Game Object, parent it to SCS Root first!")
                    return {'CANCELLED'}

                altered_looks = 0
                for scs_root in scs_roots:

                    # ignore active root
                    if scs_root == active_scs_root:
                        continue

                    look_id = -1

                    # search for same look by name on other scs root
                    for look in scs_root.scs_object_look_inventory:
                        if look.name == look_name:
                            look_id = look.id
                            break

                    if _looks.write_prop_to_look(scs_root, look_id, material, self.property_str):
                        altered_looks += 1

                if len(scs_roots) - 1 != altered_looks:
                    self.report({'WARNING'}, "WT partially done, same look was found on %s/%s other SCS Root Objects!" %
                                (altered_looks, len(scs_roots) - 1))
                else:
                    self.report({'INFO'}, "Write through altered property on %s other SCS Root Objects!" % altered_looks)

            return {'FINISHED'}

        def invoke(self, context, event):

            self.is_shift = event.shift
            self.is_ctrl = event.ctrl

            return self.execute(context)


class Tobj:
    """
    Wrapper class for better navigation in file
    """

    class ReloadTOBJ(bpy.types.Operator):
        bl_label = "Reload TOBJ settings"
        bl_idname = "material.scs_reload_tobj"
        bl_description = "Reload TOBJ file for this texture (if marked red TOBJ file is out of sync)"

        texture_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            material = context.active_object.active_material

            if material:

                _material_utils.reload_tobj_settings(material, self.texture_type)

            return {'FINISHED'}

    class CreateTOBJ(bpy.types.Operator):
        bl_label = "Create TOBJ"
        bl_idname = "material.scs_create_tobj"
        bl_description = "Create TOBJ file for this texture with default settings"

        texture_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            material = context.active_object.active_material

            if material:
                shader_texture_filepath = getattr(material.scs_props, "shader_texture_" + self.texture_type)

                if _path_utils.is_valid_shader_texture_path(shader_texture_filepath):

                    tex_filepath = _path_utils.get_abs_path(shader_texture_filepath)

                    if tex_filepath and (tex_filepath.endswith(".tga") or tex_filepath.endswith(".png")):

                        if _tobj_exp.export(tex_filepath[:-4] + ".tobj", os.path.basename(tex_filepath), set()):

                            _material_utils.reload_tobj_settings(material, self.texture_type)

                else:
                    self.report({'ERROR'}, "Please load texture properly first!")

            return {'FINISHED'}


class LampSwitcher:
    """
    Wrapper class for better navigation in file
    """

    class SwitchLampMask(bpy.types.Operator):
        bl_label = "Switch Lamp Mask"
        bl_idname = "material.scs_switch_lampmask"
        bl_description = "Show/Hide specific areas of lamp mask texture in lamp materials."

        lamp_type = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            from io_scs_tools.internals.shaders.eut2.std_node_groups.lampmask_mixer import LAMPMASK_MIX_G

            if LAMPMASK_MIX_G in bpy.data.node_groups:

                lampmask_nodes = bpy.data.node_groups[LAMPMASK_MIX_G].nodes
                if self.lamp_type in lampmask_nodes:

                    input_switch = lampmask_nodes[self.lamp_type].inputs[0]
                    if input_switch.default_value == 0:
                        input_switch.default_value = 1
                        self.report({"INFO"}, "'" + self.lamp_type + "' is turned ON.")
                    else:
                        input_switch.default_value = 0
                        self.report({"INFO"}, "'" + self.lamp_type + "' is turned OFF.")

            else:

                self.report({"ERROR"}, "No lamp materials yet on scene to change!")

            return {'FINISHED'}


class Aliasing:
    class LoadAliasedMaterial(bpy.types.Operator):
        bl_label = "Load Aliased Mat"
        bl_idname = "material.load_aliased_material"
        bl_description = "Load values from aliased material."

        @classmethod
        def poll(cls, context):
            return context.material is not None

        def execute(self, context):

            material = context.material

            tex_raw_path = getattr(material.scs_props, "shader_texture_base", "")
            tex_raw_path = tex_raw_path.replace("\\", "/")

            is_aliased_directory = ("/material/road" in tex_raw_path or
                                    "/material/terrain" in tex_raw_path or
                                    "/material/custom" in tex_raw_path)

            # abort if empty texture or not aliased directory
            if not (tex_raw_path != "" and is_aliased_directory):

                self.report({'ERROR'}, "Base texture is not from aliased directories, aliasing aborted!")
                return {'CANCELLED'}

            tex_abs_path = _path_utils.get_abs_path(tex_raw_path)
            mat_abs_path = tex_abs_path[:tex_abs_path.rfind(".")] + ".mat"

            # abort if aliasing material doesn't exists
            if not os.path.isfile(mat_abs_path):

                self.report({'ERROR'}, "Aliasing material not found, aliasing aborted!")
                return {'CANCELLED'}

            # finally try to do aliasing
            from io_scs_tools.internals.containers import mat as mat_container

            mat_cont = mat_container.get_data_from_file(mat_abs_path)

            # set attributes
            for attr_tuple in mat_cont.get_attributes().items():

                attr_key = attr_tuple[0]
                attr_val = attr_tuple[1]

                if attr_key == "substance":

                    if "substance" not in material.scs_props.keys():
                        continue

                    setattr(material.scs_props, "substance", attr_val)

                elif attr_key.startswith("aux"):

                    attr_key = attr_key.replace("[", "").replace("]", "")
                    auxiliary_prop = getattr(material.scs_props, "shader_attribute_" + attr_key, None)

                    if "shader_attribute_" + attr_key not in material.scs_props.keys():
                        continue

                    for i, val in enumerate(attr_val):
                        auxiliary_prop[i].value = val

                else:

                    if "shader_attribute_" + attr_key not in material.scs_props.keys():
                        continue

                    setattr(material.scs_props, "shader_attribute_" + attr_key, attr_val)

            # set textures
            for tex_tuple in mat_cont.get_textures().items():

                if "shader_texture_" + tex_tuple[0] not in material.scs_props.keys():
                    continue

                setattr(material.scs_props, "shader_texture_" + tex_tuple[0], tex_tuple[1])

            # report success of aliasing
            if mat_cont.get_effect() == material.scs_props.mat_effect_name:

                self.report({'INFO'}, "Material fully aliased!")

            else:

                msg = ("Aliased shader type doesn't match with current one, aliasing was not complete!\n" +
                       "Current shader type: %r\n" % material.scs_props.mat_effect_name +
                       "Aliased shader type: %r\n\n" % mat_cont.get_effect() +
                       "If you want to alias values from aliased material completely,\n"
                       "select correct shader preset and flavor combination and execute aliasing again!")

                bpy.ops.wm.show_warning_message("INVOKE_DEFAULT", icon="INFO", title="Aliasing partially successful!", message=msg)

                self.report({'WARNING'}, "Aliased partially succeded!")

            return {'FINISHED'}


class Flavors:
    class SwitchFlavor(bpy.types.Operator):
        bl_label = "Switch Given Flavor"
        bl_idname = "material.scs_switch_flavor"
        bl_description = "Enable/disable this flavor for selected shader."

        flavor_name = StringProperty(
            options={'HIDDEN'},
        )
        flavor_enabled = BoolProperty(
            options={"HIDDEN"}
        )

        @classmethod
        def poll(cls, context):
            return context.material

        def execute(self, context):
            lprint("I " + self.bl_label + "...")

            from io_scs_tools.internals.shader_presets import cache as _shader_presets_cache
            from io_scs_tools.utils import get_shader_presets_inventory as _get_shader_presets_inventory

            mat = context.material
            mat_scs_props = mat.scs_props
            """:type: io_scs_tools.properties.material.MaterialSCSTools"""
            preset = _get_shader_presets_inventory()[mat_scs_props.active_shader_preset_name]
            """:type: io_scs_tools.properties.world.ShaderPresetsInventoryItem"""

            # extract only flavor effect part of string
            flavor_effect_part = mat_scs_props.mat_effect_name[len(preset.effect):]

            new_flavor_state = not self.flavor_enabled
            flavors_suffix = ""
            for flavor in preset.flavors:
                flavor_variant_found = False
                for flavor_variant in flavor.variants:

                    if flavor_variant.name == self.flavor_name:
                        # add founded flavor to flavors suffix only if enabled
                        if new_flavor_state:
                            flavors_suffix += "." + flavor_variant.name

                        flavor_variant_found = True
                        break

                # if one variant of flavor is found skip all other variants
                if flavor_variant_found:
                    continue

                # make sure to add all other enabled flavors to flavors suffix
                for flavor_variant in flavor.variants:

                    is_in_middle = "." + flavor_variant.name + "." in flavor_effect_part
                    is_on_end = flavor_effect_part.endswith("." + flavor_variant.name)

                    if is_in_middle or is_on_end:
                        flavors_suffix += "." + flavor_variant.name

            # finally set new shader data to material
            section = _shader_presets_cache.get_section(preset, flavors_suffix)
            context.material.scs_props.mat_effect_name = preset.effect + flavors_suffix
            _material_utils.set_shader_data_to_material(context.material, section)

            # sync shader types on all scs roots by updating looks on them
            # to avoid different shader types on different scs roots for same material
            for scs_root in _object_utils.gather_scs_roots(bpy.data.objects):
                _looks.update_look_from_material(scs_root, mat, True)

            return {'FINISHED'}


class Texture:
    class SelectShaderTextureFilePath(bpy.types.Operator):
        """Universal operator for setting relative or absolute paths to shader texture files."""
        bl_label = "Select Shader Texture File"
        bl_idname = "material.scs_select_shader_texture_filepath"
        bl_description = "Open a Texture file browser"

        shader_texture = bpy.props.StringProperty(options={'HIDDEN'})
        filepath = StringProperty(
            name="Shader Texture File",
            description="Shader texture relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )

        # NOTE: force blender to use thumbnails preview by default with display_type
        display_type = get_filebrowser_display_type(is_image=True)

        filter_glob = StringProperty(
            default="*.tobj;*.tga;*.png;",
            options={'HIDDEN'}
        )

        def execute(self, context):
            """Set shader texture file path."""
            material = context.active_object.active_material

            # NOTE: because filter_glob property was removed in the exchange to get thumbnails preview,
            # we have to ensure correct image on execute by checking extension
            if not (self.filepath[-4:] in (".tga", ".png") or self.filepath[-5:] == ".tobj"):
                self.report({"ERROR"}, "Selected file is not TOBJ, TGA or PNG! Texture won't be loaded.")
                lprint("E Selected file is not TOBJ, TGA or PNG! Texture won't be loaded.")
                return {'CANCELLED'}

            setattr(material.scs_props, self.shader_texture, str(self.filepath))

            return {'FINISHED'}

        def invoke(self, context, event):
            """Invoke a file path selector."""

            curr_texture_path = getattr(bpy.context.active_object.active_material.scs_props, self.shader_texture)

            extensions, curr_texture_path = _path_utils.get_texture_extens_and_strip_path(curr_texture_path)
            for ext in extensions:
                filepath = _path_utils.get_abs_path(curr_texture_path + ext)

                if os.path.isfile(filepath):
                    self.filepath = filepath
                    break
            else:
                self.filepath = _get_scs_globals().scs_project_path

            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
