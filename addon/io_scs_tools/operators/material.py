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

import bpy
import os
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.exp import tobj as _tobj_exp
from io_scs_tools.internals import looks as _looks
from io_scs_tools.utils import convert as _convert_utils
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

    class SCS_TOOLS_OT_ReloadMaterials(bpy.types.Operator):
        bl_label = "Reload SCS Materials"
        bl_idname = "material.scs_tools_reload_materials"
        bl_description = "Reload node trees & any shader interface changes for all SCS materials in blend file."

        def execute(self, context):

            # find group names created by Blender Tools with traversing all node groups and matching them by scs prefix
            groups_to_remove = [
                "AddEnvGroup",  # from v0.6
                "FresnelGroup",  # from v0.6
                "LampmaskMixerGroup",  # from v0.6
                "ReflectionNormalGroup",  # from v0.6
            ]
            for group in bpy.data.node_groups:
                if group.name.startswith(_MAT_consts.node_group_prefix):
                    groups_to_remove.append(group.name)

            # 1. clear nodes on materials
            for mat in bpy.data.materials:

                if not mat.node_tree:
                    continue

                # also check none blender tools materials just to remove possible nodes usage of our groups
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

                bpy.data.node_groups.remove(bpy.data.node_groups[ng_name], do_unlink=True)

            # 4. finally set preset to material again, which will update nodes and possible input interface changes
            scs_roots = _object_utils.gather_scs_roots(bpy.data.objects)
            for mat in bpy.data.materials:

                # ignore none blender tools materials
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

                    # sync shader types on all scs roots by updating looks on them
                    # without this call we might end up with outdated looks raising errors once user will switch to them
                    for scs_root in scs_roots:
                        _looks.update_look_from_material(scs_root, mat, True)
                else:
                    # reset usage of nodes, to prevent crashing in no preset is found
                    mat.use_nodes = False

            return {'FINISHED'}

    class SCS_TOOLS_OT_SearchShaderPreset(bpy.types.Operator):
        bl_label = "Search Shader Preset"
        bl_idname = "material.scs_tools_search_shader_preset"
        bl_description = "Quickly search trough shader presets with typing and assign selected shader preset to material."
        bl_property = "shader_presets"

        # NOTE: As shader preset list is "dynamic" property we can use that fact,
        # to replicate same property inside this operator, but use functions from global scs props module.
        # Second variable however is there because functions from global scs props requires it.
        from io_scs_tools.properties.addon_preferences import SCSInventories

        shader_presets: EnumProperty(
            name="Shader Presets",
            description="Shader presets",
            items=SCSInventories.retrieve_shader_presets_items,
            get=SCSInventories.get_shader_presets_item,
            set=SCSInventories.set_shader_presets_item,
        )
        shader_presets_sorted: BoolProperty(
            name="Shader Preset List Sorted Alphabetically",
            description="Sort Shader preset list alphabetically",
            default=True,
        )

        def execute(self, context):
            lprint("D You searched & selected preset with name: %s", (self.shader_presets,))
            return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager
            wm.invoke_search_popup(self)
            return {'FINISHED'}

    class SCS_TOOLS_OT_AdaptColorManagement(bpy.types.Operator):
        bl_label = "Adapt Color Management"
        bl_idname = "material.scs_tools_adapt_color_management"
        bl_description = "Adapt current scene color management for proper colors in SCS Materials"
        bl_options = {'INTERNAL'}

        adapt: IntProperty(name="Adapt Color Management?", default=-1)

        @classmethod
        def poll(cls, context):
            return not _material_utils.has_valid_color_management(context.scene)

        @staticmethod
        def draw_popup_menu(self, context):
            layout = self.layout

            display_settings = context.scene.display_settings
            view_settings = context.scene.view_settings

            settings_texts = []
            if display_settings.display_device != 'sRGB':
                settings_texts.append("%i. Display Device: %r  (desired 'sRGB')" % (len(settings_texts) + 1, display_settings.display_device))
            if view_settings.view_transform != 'Standard':
                settings_texts.append("%i. View Transform: %r  (desired 'Standard')" % (len(settings_texts) + 1, view_settings.view_transform))
            if view_settings.look != 'None':
                settings_texts.append("%i. Look: %r (desired 'None')" % (len(settings_texts) + 1, view_settings.look))
            if view_settings.exposure != 0.0:
                settings_texts.append("%i. Exposure: '%.1f' (desired '0.0')" % (len(settings_texts) + 1, view_settings.exposure))
            if view_settings.gamma != 1.0:
                settings_texts.append("%i. Gamma: '%.1f' (desired '1.0')" % (len(settings_texts) + 1, view_settings.gamma))

            body = layout.column(align=True)
            body.label(text="Some of scene color management settings are preventing proper visualization of SCS Materials:")
            for settings_info in settings_texts:
                body.label(text=settings_info)
            body.label()

            footer = body.column(align=True)
            footer.label(text="Do you want to automatically set desired values?")
            props = footer.operator("material.scs_tools_adapt_color_management", text="Yes")
            props.adapt = 1
            props = footer.operator("material.scs_tools_adapt_color_management", text="No")
            props.adapt = 0

        def execute(self, context):
            lprint("D Executed color management adoption!")

            if self.adapt != 1:  # no adaption requested
                return {'CANCELLED'}

            if not context.scene:
                self.report({'ERROR'}, "Can't adapt color management, no scene!")
                return {'CANCELLED'}

            display_settings = context.scene.display_settings
            display_settings.display_device = "sRGB"

            view_settings = context.scene.view_settings
            view_settings.view_transform = "Standard"
            view_settings.look = "None"
            view_settings.exposure = 0.0
            view_settings.gamma = 1.0

            # reset adapt property, so next invocation will bring up popup again!
            self.adapt = -1

            return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager

            # adapt state was set, do execution
            if self.adapt != -1:
                return self.execute(context)

            wm.popup_menu(self.draw_popup_menu, title="Color Management for SCS Materials!", icon='COLOR')
            return {'FINISHED'}

    class SCS_TOOLS_OT_MergeMaterials(bpy.types.Operator):
        bl_label = "Merge SCS Materials"
        bl_idname = "material.scs_tools_merge_materials"
        bl_description = "Collect same SCS materials and assign only unique instance to all objects in blend file."

        OBJ_SCOPE_SEL = "selected"
        OBJ_SCOPE_ALL = "all"

        BY_N = "name"
        BY_NE = "name_effect"
        BY_NEA = "name_effect_attributes"

        scope_type: EnumProperty(
            name="Objects Scope",
            description="Which objects should take part in materials merging: selected or all",
            items=[
                (OBJ_SCOPE_SEL, "Selected", "Materials will be merged on selected objects only", "", 1),
                (OBJ_SCOPE_ALL, "All", "Materails will be merged on all objects in blend file", "", 2)
            ],
            default=OBJ_SCOPE_ALL
        )

        merge_type: EnumProperty(
            name="Merge Type",
            description="What should be taken in consideration while merging",
            items=[
                (BY_N, "Name", "Merge by material name only", "", 1),
                (BY_NE, "Name & Effect", "Merge by material name & effect", "", 2),
                (BY_NEA, "Name & Effect & Attributes", "Merge by material name & effect & attributes in looks", "", 3),
            ],
            default=BY_NEA
        )

        def draw(self, context):
            layout = self.layout

            body = layout.column(align=True)
            body.label(text="Objects Scope:")
            body.row().prop(self, "scope_type", expand=True)
            body.label(text="Merge by:")
            body.prop(self, "merge_type", expand=True)

        def merge_materials(self, mats_to_merge, base_mat_look_entries=None):
            """Merge givem materials across all objects in blender scene.
            If additional base material look entries is provided looks entries of material on current object
            have to match to the base one, otherwise merging on particular object won't be done.

            :param mats_to_merge: materials to merge, dictonary with list of material duplicates per base material name
            :type mats_to_merge: dict[str, list[bpy.types.Material]]
            :param base_mat_look_entries: look entries from base material for in depth attributes check (finding perfect material copy)
            :type base_mat_look_entries: dict[bpy.types.Material, dict]
            """

            reassigned_objs = set()
            reassigned_mats = set()
            mats_for_look_reassign = {}

            if self.scope_type == self.OBJ_SCOPE_SEL:
                objs_to_check = bpy.context.selected_objects
            elif self.scope_type == self.OBJ_SCOPE_ALL:
                objs_to_check = bpy.data.objects
            else:
                self.report({'ERROR'}, "Invalid object scope selected!")
                return {'CANCELLED'}

            for obj in objs_to_check:
                root_obj = _object_utils.get_scs_root(obj)

                # make entry for looks reassignment map
                if root_obj not in mats_for_look_reassign:
                    mats_for_look_reassign[root_obj] = set()

                for mat_slot in obj.material_slots:
                    mat = mat_slot.material

                    # ignore empty slots
                    if not mat:
                        continue

                    # iterate whole materials to merge dictionary,
                    # search for duplicate material and re-assign
                    for base_mat_name in mats_to_merge:
                        mats_list = mats_to_merge[base_mat_name]

                        # only one material exists, means no duplicates thus continue
                        if len(mats_list) <= 1:
                            continue

                        # first in the list is always base material
                        base_mat = mats_list[0]

                        # base material already used, continue
                        if base_mat == mat:
                            continue

                        # not found in materials duplicate list, continue
                        if mat not in mats_list:
                            continue

                        # if base material look entries provided, skip the materials that don't have same looks setup as base material
                        if base_mat_look_entries:
                            mat_look_entries = _looks.get_material_entries(root_obj, mat)
                            if base_mat_look_entries[base_mat] != mat_look_entries:
                                lprint("W Looks of %r on object %r don't match with base material, material merge skipped!" % (mat.name, obj.name))
                                continue

                        # ressign material
                        mat_slot.material = base_mat

                        # mark this material for reassignment in looks, instead of immidiate reassignment
                        # which would invalidate getter for material entries for other objects using current material on this root.
                        mats_for_look_reassign[root_obj].add((mat, base_mat))

                        reassigned_mats.add(mat)
                        reassigned_objs.add(obj)
                        break

            # reassign materials entries on looks of all roots
            for root_obj in mats_for_look_reassign:
                for mat, base_mat in mats_for_look_reassign[root_obj]:
                    _looks.reassign_material(root_obj, base_mat, mat)

            reassigned_mats_count = len(reassigned_mats)
            reassigned_objs_count = len(reassigned_objs)
            if reassigned_mats_count + reassigned_objs_count > 0:
                self.report({'INFO'}, "Successfully merged %i materials on %i objects." % (reassigned_mats_count, reassigned_objs_count))
            else:
                self.report({'WARNING'}, "No materials could be merged!. No duplicates found.")

        def execute(self, context):

            # flush any possible warnings not to interfer with the ones we might report here
            lprint("", report_warnings=-1)

            # collect scs materials
            scs_materials = []
            for mat in bpy.data.materials:
                if mat.scs_props.mat_effect_name != "" and mat.scs_props.active_shader_preset_name != "<none>":
                    scs_materials.append(mat)

            mats_to_merge = {}

            # 1. group materials by name
            for mat in scs_materials:
                name = mat.name

                if re.match(r".+((\.|_)\d{3})$", name):
                    base_name = name[:-4]
                else:
                    base_name = name

                if base_name not in mats_to_merge:
                    mats_to_merge[base_name] = []

                # order materials in the list, where first one is our original to merge to
                if base_name == name:
                    mats_to_merge[base_name].insert(0, mat)
                else:
                    mats_to_merge[base_name].append(mat)

            # filter out single instance materials as they can't be really merged
            for mat_name in list(mats_to_merge.keys()):
                if len(mats_to_merge[mat_name]) <= 1:
                    del mats_to_merge[mat_name]

            # report and filter out the ones without base material
            for mat_name in list(mats_to_merge.keys()):
                if mat_name not in bpy.data.materials:
                    # report
                    msg = "W Missing base material for (to merge them, rename one to %r):\n\t   " % mat_name
                    for mat in mats_to_merge[mat_name]:
                        msg += "'" + mat.name + "', "
                    lprint(msg.strip(", "))

                    # remove
                    del mats_to_merge[mat_name]

            # now merge by name and finish
            if self.merge_type == self.BY_N:
                self.merge_materials(mats_to_merge)
                lprint("", report_warnings=1)
                return {'FINISHED'}

            # 2. group by effect name
            for base_name, mat_list in mats_to_merge.copy().items():
                base_mat_effect = mat_list[0].scs_props.mat_effect_name
                filtered_mat_list = []
                for mat in mat_list[1:]:
                    if mat.scs_props.mat_effect_name == base_mat_effect:
                        filtered_mat_list.append(mat)

                if filtered_mat_list:
                    # prepend base
                    filtered_mat_list.insert(0, mat_list[0])
                    # update materials to merge dictonary
                    mats_to_merge[base_name] = filtered_mat_list
                else:
                    del mats_to_merge[base_name]

            # now merge by name & effect and finish
            if self.merge_type == self.BY_NE:
                self.merge_materials(mats_to_merge)
                lprint("", report_warnings=1)
                return {'FINISHED'}

            # 3. complete copy
            # go trough objects and collect all mergable base materials, material is mergable if one of the following:
            # 1. is not used in any roots (no looks)
            # 2. used only on one root (only one look series is available)
            # 3. used in more roots where look entries are same for all of the roots (more looks series and all are the same)
            mergable_base_mats = {}
            unmergable_base_mats = set()
            for obj in bpy.data.objects:
                for mat_slot in obj.material_slots:
                    mat = mat_slot.material

                    if not mat:
                        continue

                    # ignore non-base materials
                    if mat.name not in mats_to_merge:
                        continue

                    root_obj = _object_utils.get_scs_root(obj)
                    mat_look_entries = _looks.get_material_entries(root_obj, mat)

                    # if no entry for current material in mergable and unmergable, save look setup from this root object
                    # otherwise move to unmergable if current root look entries doesn't match with saved one,
                    # this means we have multiple roots with different looks setup
                    if mat not in mergable_base_mats and mat not in unmergable_base_mats:
                        mergable_base_mats[mat] = mat_look_entries
                    elif mat in mergable_base_mats and mergable_base_mats[mat] != mat_look_entries:
                        del mergable_base_mats[mat]
                        unmergable_base_mats.add(mat)

            # remove unmergable base materials entries
            for mat in unmergable_base_mats:
                del mats_to_merge[mat.name]

            # take care of materials without linkage to objects,
            # should be treated as mergable as no look entries for it exists.
            for mat_name in mats_to_merge:
                mat = bpy.data.materials[mat_name]
                if mat not in mergable_base_mats:
                    mergable_base_mats[mat] = _looks.get_material_entries(None, mat)

            # report unmergable
            if len(mats_to_merge) == 0 and len(unmergable_base_mats) > 0:
                msg = ("No materials merging can be done. Found %i base material candidates, "
                       "however they are used on multiple SCS Root objects with different looks setup!") % len(unmergable_base_mats)
                self.report({'WARNING'}, msg)
                lprint("W " + msg, report_warnings=1)
                return {'CANCELLED'}
            elif len(unmergable_base_mats) > 0:
                msg = "W Due to different looks settings on multiple SCS Root objects, following base materials are unmergable:\n\t   "
                for i, mat in enumerate(unmergable_base_mats):
                    msg += str(i + 1) + ". '" + mat.name + "'\n\t   "
                lprint(msg.strip("\n\t   "))

            # now merge by name & effect & attributes and finish
            if self.merge_type == self.BY_NEA:
                self.merge_materials(mats_to_merge, base_mat_look_entries=mergable_base_mats)
                lprint("", report_warnings=1)
                return {'FINISHED'}

            # invalid type, just cancel
            return {'CANCELLED'}

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=200)

    class SCS_TOOLS_OT_MaterialItemExtrasMenu(bpy.types.Operator):
        bl_label = "More Options"
        bl_idname = "material.scs_tools_material_item_extras"
        bl_description = "Show more options for this material item (WT, Copy Linear Color etc.)"
        bl_options = set()

        property_str: StringProperty(
            description="String representing which property should be worked on.",
            default="",
            options={'HIDDEN'},
        )

        __property_str = ""
        """Static variable holding property name, for which context menu should be created."""

        @staticmethod
        def draw_context_menu(self, context):
            layout = self.layout
            property_str = Common.SCS_TOOLS_OT_MaterialItemExtrasMenu.__property_str

            body = layout.column(align=True)
            props = body.operator("material.scs_tools_write_trough_looks", text="WT")
            props.property_str = property_str
            props.wt_type = Looks.SCS_TOOLS_OT_WriteThroughLooks.WT_TYPE_NORMAL
            props = body.operator("material.scs_tools_write_trough_looks", text="WT - Same Look on All SCS Roots")
            props.property_str = property_str
            props.wt_type = Looks.SCS_TOOLS_OT_WriteThroughLooks.WT_TYPE_SAME_LOOK
            props = body.operator("material.scs_tools_write_trough_looks", text="WT - All Looks on All SCS Roots")
            props.property_str = property_str
            props.wt_type = Looks.SCS_TOOLS_OT_WriteThroughLooks.WT_TYPE_ALL

            # show copy/paste only on color type of properties, as any other properties in our games (even aux ones)
            # are not in any color space and can be copy/pasted normally as any other value in blender
            material = context.active_object.active_material
            if material.scs_props.bl_rna.properties[property_str].subtype == "COLOR":
                body.separator(factor=0.25)

                props = body.operator("material.scs_tools_cpy_color_as_linear", icon="COPYDOWN")
                props.property_str = property_str
                props = body.operator("material.scs_tools_paste_color_from_linear", icon="PASTEDOWN")
                props.property_str = property_str

        def execute(self, context):
            # copy property name to static variable for usage in context menu
            Common.SCS_TOOLS_OT_MaterialItemExtrasMenu.__property_str = self.property_str

            context.window_manager.popup_menu(self.draw_context_menu, title="Material Item Extras Menu", icon="LAYER_USED")
            return {'FINISHED'}


class CustomMapping:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_AddCustomTexCoordMapping(bpy.types.Operator):
        bl_label = "Add Custom TexCoord Mapping"
        bl_idname = "material.scs_tools_add_custom_tex_coord_mapping"
        bl_description = "Add custom TexCoord mapping to list"
        bl_options = {'INTERNAL'}

        def execute(self, context):
            material = context.active_object.active_material

            if material:
                item = material.scs_props.custom_tex_coord_maps.add()
                item.name = "text_coord_x"

            return {'FINISHED'}

    class SCS_TOOLS_OT_RemoveCustomTexCoordMapping(bpy.types.Operator):
        bl_label = "Remove Custom TexCoord Mapping"
        bl_idname = "material.scs_tools_remove_custom_tex_coord_mapping"
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

    class SCS_TOOLS_OT_WriteThroughLooks(bpy.types.Operator):
        bl_label = "Write Through"
        bl_idname = "material.scs_tools_write_trough_looks"
        bl_description = ("Write current material value through looks depending on given write trough type:\n"
                          "0 - All looks within same SCS Root object\n"
                          "1 - To same look on all SCS Root objects\n"
                          "2 - To all looks on all SCS Root objects")
        bl_options = {'REGISTER', 'UNDO'}

        WT_TYPE_NONE = -1
        WT_TYPE_NORMAL = 0
        WT_TYPE_SAME_LOOK = 1
        WT_TYPE_ALL = 2

        wt_type: IntProperty(
            name="Type of WT",
            default=WT_TYPE_NONE
        )

        property_str: StringProperty(
            description="String representing which property should be written through.",
            default="",
            options={'HIDDEN'},
        )

        is_ctrl = False  # WT to same look of this material in other SCS Roots
        is_shift = False  # is_shift + is_ctrl ->  WT to all looks of this material in all SCS Roots

        def init_control_states(self):

            # decide which type of WT is it, prefer manually set type over ctrl and shift modifiers
            if self.wt_type == self.WT_TYPE_NORMAL:
                self.is_ctrl = False
                self.is_shift = False
            elif self.wt_type == self.WT_TYPE_SAME_LOOK:
                self.is_ctrl = True
                self.is_shift = False
            elif self.wt_type == self.WT_TYPE_ALL:
                self.is_ctrl = True
                self.is_shift = True
            else:
                self.is_ctrl = False
                self.is_shift = False

            # always reset type for next invoke
            self.wt_type = -1

        def execute(self, context):
            material = context.active_object.active_material

            if not material or not hasattr(material.scs_props, self.property_str):
                return {'CANCELLED'}

            self.init_control_states()

            scs_roots = []
            active_scs_root = _object_utils.get_scs_root(context.active_object)
            if active_scs_root:
                scs_roots.append(active_scs_root)

            if self.is_ctrl:
                scs_roots = _object_utils.gather_scs_roots(bpy.data.objects)

            if self.is_shift or not self.is_ctrl:  # WT either on active only or all SCS roots; (Shift + Ctrl) or none

                altered_looks = 0
                altered_scs_roots = 0
                for scs_root in scs_roots:
                    res = _looks.write_through(scs_root, material, self.property_str)

                    # only log altered looks if write trought succeded
                    if res > 0:
                        altered_looks += res
                        altered_scs_roots += 1

                if altered_looks > 0:
                    message = "Write through successfully altered %s looks on %s SCS Root Objects!" % (altered_looks, altered_scs_roots)
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


class Tobj:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_ReloadTOBJ(bpy.types.Operator):
        bl_label = "Reload TOBJ settings"
        bl_idname = "material.scs_tools_reload_tobj"
        bl_description = "Reload TOBJ file for this texture (if marked red TOBJ file is out of sync)"

        texture_type: StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            material = context.active_object.active_material

            if material:

                _material_utils.reload_tobj_settings(material, self.texture_type)

            return {'FINISHED'}

    class SCS_TOOLS_OT_CreateTOBJ(bpy.types.Operator):
        bl_label = "Create TOBJ"
        bl_idname = "mmaterial.scs_tools_create_tobj"
        bl_description = "Create TOBJ file for this texture with default settings"

        texture_type: StringProperty(
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

    class SCS_TOOLS_OT_SwitchLampmask(bpy.types.Operator):
        bl_label = "Switch Lamp Mask"
        bl_idname = "material.scs_tools_switch_lampmask"
        bl_description = "Show/Hide specific areas of lamp mask texture in lamp materials."

        lamp_type: StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            from io_scs_tools.internals.shaders.eut2.std_node_groups.lampmask_mixer_ng import LAMPMASK_MIX_G

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
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_LoadAliasedMaterial(bpy.types.Operator):
        bl_label = "Load Aliased Mat"
        bl_idname = "material.scs_tools_load_aliased_material"
        bl_description = "Load values from aliased material."
        bl_options = {'REGISTER', 'UNDO'}

        @classmethod
        def poll(cls, context):
            return context.active_object and context.active_object.active_material

        def execute(self, context):

            material = context.active_object.active_material

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

                bpy.ops.wm.scs_tools_show_message_in_popup("INVOKE_DEFAULT", icon='INFO', title="Aliasing partially successful!", message=msg)

                self.report({'WARNING'}, "Aliased partially succeded!")

            return {'FINISHED'}


class Flavors:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_SwitchFlavor(bpy.types.Operator):
        bl_label = "Switch Given Flavor"
        bl_idname = "material.scs_tools_switch_flavor"
        bl_description = "Enable/disable this flavor for selected shader."

        flavor_name: StringProperty(
            options={'HIDDEN'},
        )
        flavor_enabled: BoolProperty(
            options={"HIDDEN"}
        )

        @classmethod
        def poll(cls, context):
            return context.active_object and context.active_object.active_material

        def execute(self, context):
            lprint("I " + self.bl_label + "...")

            from io_scs_tools.internals import shader_presets as _shader_presets

            mat = context.active_object.active_material
            mat_scs_props = mat.scs_props
            """:type: io_scs_tools.properties.material.MaterialSCSTools"""
            preset = _shader_presets.get_preset(mat_scs_props.active_shader_preset_name)

            # extract only flavor effect part of string
            flavor_effect_part = mat_scs_props.mat_effect_name[len(preset.effect):]

            new_flavor_state = not self.flavor_enabled
            flavors_suffix = ""
            for flavor in preset.flavors:
                flavor_variant_found = False
                for flavor_variant in flavor.variants:

                    if flavor_variant.suffix == self.flavor_name:
                        # add founded flavor to flavors suffix only if enabled
                        if new_flavor_state:
                            flavors_suffix += "." + flavor_variant.suffix

                        flavor_variant_found = True
                        break

                # if one variant of flavor is found skip all other variants
                if flavor_variant_found:
                    continue

                # make sure to add all other enabled flavors to flavors suffix
                for flavor_variant in flavor.variants:

                    is_in_middle = "." + flavor_variant.suffix + "." in flavor_effect_part
                    is_on_end = flavor_effect_part.endswith("." + flavor_variant.suffix)

                    if is_in_middle or is_on_end:
                        flavors_suffix += "." + flavor_variant.suffix

            # if desired combination doesn't exists, abort switching and notify user
            if not _shader_presets.has_section(preset.name, flavors_suffix):
                message = "Enabling %r flavor aborted! Wanted shader combination: %r is not supported!" % (self.flavor_name,
                                                                                                           preset.effect + flavors_suffix)
                lprint("E " + message)
                self.report({'WARNING'}, message)
                return {'FINISHED'}

            # finally set new shader data to material
            section = _shader_presets.get_section(preset.name, flavors_suffix)
            mat.scs_props.mat_effect_name = preset.effect + flavors_suffix
            _material_utils.set_shader_data_to_material(mat, section)

            # sync shader types on all scs roots by updating looks on them
            # to avoid different shader types on different scs roots for same material
            for scs_root in _object_utils.gather_scs_roots(bpy.data.objects):
                _looks.update_look_from_material(scs_root, mat, True)

            return {'FINISHED'}


class Texture:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_SelectTexturePath(bpy.types.Operator):
        """Universal operator for setting relative or absolute paths to material texture files."""
        bl_label = "Select Material Texture File"
        bl_idname = "material.scs_tools_select_texture_path"
        bl_description = "Open a Texture file browser"
        bl_options = {'REGISTER', 'UNDO'}

        shader_texture: StringProperty(
            options={'HIDDEN'}
        )
        filepath: StringProperty(
            name="Shader Texture File",
            description="Shader texture relative or absolute file path",
            # maxlen=1024,
            subtype='FILE_PATH',
        )

        # NOTE: force blender to use thumbnails preview by default with display_type
        display_type: get_filebrowser_display_type(is_image=True)

        filter_glob: StringProperty(
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


class Attribute:
    """
    Wrapper class for better navigation in file
    """

    class SCS_TOOLS_OT_CopyColorAsLinear(bpy.types.Operator):
        bl_label = "Copy Color as Linear"
        bl_idname = "material.scs_tools_cpy_color_as_linear"
        bl_description = "Copy this color to clipboard in linear colorspace (can be used for colors in SII and MAT files)"

        property_str: StringProperty(
            description="String representing which property should be copied.",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):
            material = context.active_object.active_material

            if material.scs_props.bl_rna.properties[self.property_str].subtype != "COLOR":
                self.report({'ERROR'}, "Can not copy given attribute, it's not a COLOR property!")
                return {'CANCELLED'}

            color = getattr(material.scs_props, self.property_str)
            lin_color = list(_convert_utils.srgb_to_linear(color))

            lin_color_str = ""
            for col in lin_color:
                lin_color_str += "%.6f, " % col
            lin_color_str = lin_color_str[:-2]

            context.window_manager.clipboard = lin_color_str

            self.report({'INFO'}, "Color successfully copied as: (%.6f, %.6f, %.6f)" % (color[0], color[1], color[2]))
            return {'FINISHED'}

    class SCS_TOOLS_OT_PasteColorFromLinear(bpy.types.Operator):
        bl_label = "Paste Color from Linear"
        bl_idname = "material.scs_tools_paste_color_from_linear"
        bl_description = "Paste cliboard to this color from linear colorspace (can be used for colors in SII and MAT files)"

        property_str: StringProperty(
            description="String representing which property should be copied.",
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):
            material = context.active_object.active_material

            if material.scs_props.bl_rna.properties[self.property_str].subtype != "COLOR":
                self.report({'ERROR'}, "Can not paste to given attribute, it's not a COLOR property!")
                return {'CANCELLED'}

            # paste from clipboard:
            pasted_color_str = context.window_manager.clipboard
            # 1. strip any whitespace ends and any brackets with spaces,
            pasted_color_str = pasted_color_str.strip(" ").strip("(){}[]").strip(" ")
            # 2. replace mid spaces with commas,
            pasted_color_str = pasted_color_str.replace(" ", ",")
            # 3. replace double commas with single,
            pasted_color_str = pasted_color_str.replace(",,", ",")

            # validate string: 'X,X,X'
            if not re.match(r"^\d+(\.\d*)?,\d+(\.\d*)?,\d+(\.\d*)?$", pasted_color_str):
                self.report({'ERROR'}, ("Can not parse clipboard string,"
                                        "make sure format is 'X X X' or 'X, X, X' or variants enclosed with brackets."))
                return {'CANCELLED'}

            # convert into list of floats
            pasted_color = []
            for num_str in pasted_color_str.split(","):
                pasted_color.append(float(num_str))

            # convert to srgb
            color = _convert_utils.linear_to_srgb(pasted_color)

            # finally assign
            setattr(material.scs_props, self.property_str, color)

            self.report({'INFO'}, "Color successfully pasted as: (%.6f, %.6f, %.6f)" % (color[0], color[1], color[2]))
            return {'FINISHED'}


classes = (
    Aliasing.SCS_TOOLS_OT_LoadAliasedMaterial,

    Attribute.SCS_TOOLS_OT_CopyColorAsLinear,
    Attribute.SCS_TOOLS_OT_PasteColorFromLinear,

    Common.SCS_TOOLS_OT_ReloadMaterials,
    Common.SCS_TOOLS_OT_SearchShaderPreset,
    Common.SCS_TOOLS_OT_AdaptColorManagement,
    Common.SCS_TOOLS_OT_MergeMaterials,
    Common.SCS_TOOLS_OT_MaterialItemExtrasMenu,

    CustomMapping.SCS_TOOLS_OT_AddCustomTexCoordMapping,
    CustomMapping.SCS_TOOLS_OT_RemoveCustomTexCoordMapping,

    Flavors.SCS_TOOLS_OT_SwitchFlavor,

    LampSwitcher.SCS_TOOLS_OT_SwitchLampmask,

    Looks.SCS_TOOLS_OT_WriteThroughLooks,

    Texture.SCS_TOOLS_OT_SelectTexturePath,

    Tobj.SCS_TOOLS_OT_CreateTOBJ,
    Tobj.SCS_TOOLS_ReloadTOBJ,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
