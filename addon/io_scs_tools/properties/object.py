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
from bpy.props import (StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       EnumProperty,
                       FloatProperty)
from collections import OrderedDict
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.consts import Look as _LOOK_consts
from io_scs_tools.consts import Part as _PART_consts
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.utils import animation as _animation_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.internals.icons import get_icon
from io_scs_tools.utils.printout import lprint

_ICON_TYPES = _ICONS_consts.Types


class ObjectLooksInventoryItem(bpy.types.PropertyGroup):
    def name_update(self, context):

        lprint("D SCS Look inventory name update: %s", (self.name,))

        # convert name to game engine like name
        tokenized_name = _name_utils.tokenize_name(self.name)
        if self.name != tokenized_name:
            self.name = tokenized_name

        # always get scs root to have access to look inventory
        scs_root_obj = _object_utils.get_scs_root(context.active_object)

        # if there is more of variants with same name, make postfixed name (this will cause another name update)
        if len(_inventory.get_indices(scs_root_obj.scs_object_look_inventory, self.name)) == 2:  # duplicate

            i = 1
            new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
            while _inventory.get_index(scs_root_obj.scs_object_look_inventory, new_name) != -1:
                new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
                i += 1

            if new_name != self.name:
                self.name = new_name

    name = StringProperty(name="Look Name", default=_LOOK_consts.default_name, update=name_update)
    id = IntProperty(name="Unique ID of this look")


class ObjectPartInventoryItem(bpy.types.PropertyGroup):
    """
    Part property inventory, which gets saved into *.blend file.
    """

    def name_update(self, context):

        lprint("D SCS Part inventory name update: %s", (self.name,))

        # convert name to game engine like name
        tokenized_name = _name_utils.tokenize_name(self.name, default_name=_PART_consts.default_name)
        if self.name != tokenized_name:
            self.name = tokenized_name

        # always get scs root because we allow editing of parts in any child
        scs_root_obj = _object_utils.get_scs_root(context.active_object)

        # if there is more of parts with same name, make postfixed name (this will cause another name update)
        if len(_inventory.get_indices(scs_root_obj.scs_object_part_inventory, self.name)) == 2:  # duplicate

            i = 1
            new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
            while _inventory.get_index(scs_root_obj.scs_object_part_inventory, new_name) != -1:
                new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
                i += 1

            if new_name != self.name:
                self.name = new_name

        if "scs_part_old_name" in self:

            if scs_root_obj:

                # fix part name in all children of current root
                children = _object_utils.get_children(scs_root_obj)
                for child in children:

                    # fix part name in child with existing old name
                    if child.scs_props.scs_part == self["scs_part_old_name"]:

                        child.scs_props.scs_part = self.name

                # rename parts in all variants also
                variant_inventory = scs_root_obj.scs_object_variant_inventory
                for variant in variant_inventory:
                    for part in variant.parts:

                        if part.name == self["scs_part_old_name"]:
                            part.name = self.name
                            break

        # backup current name for checking children on next renaming
        self["scs_part_old_name"] = self.name

    name = StringProperty(name="Part Name", default=_PART_consts.default_name, update=name_update)


class ObjectVariantPartInclusion(bpy.types.PropertyGroup):
    """
    Variant to Part references, which gets saved within "SceneVariantInventory" into *.blend file.
    """
    include = BoolProperty(name="Part is included in the Variant", default=False)


class ObjectVariantInventoryItem(bpy.types.PropertyGroup):
    """
    Variant property inventory, which gets saved into *.blend file.
    """

    def name_update(self, context):

        lprint("D SCS Variant inventory name update: %s", (self.name,))

        # convert name to game engine like name
        tokenized_name = _name_utils.tokenize_name(self.name)
        if self.name != tokenized_name:
            self.name = tokenized_name

        # always get scs root because we might allow variants editing in any child someday
        scs_root_obj = _object_utils.get_scs_root(context.active_object)

        # if there is more of variants with same name, make postfixed name (this will cause another name update)
        if len(_inventory.get_indices(scs_root_obj.scs_object_variant_inventory, self.name)) == 2:  # duplicate

            i = 1
            new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
            while _inventory.get_index(scs_root_obj.scs_object_variant_inventory, new_name) != -1:
                new_name = _name_utils.tokenize_name(self.name + "_" + str(i).zfill(2))
                i += 1

            if new_name != self.name:
                self.name = new_name

    name = StringProperty(name="Variant Name", default=_VARIANT_consts.default_name, update=name_update)
    parts = CollectionProperty(type=ObjectVariantPartInclusion)


class ObjectAnimationInventoryItem(bpy.types.PropertyGroup):
    """
    Animation property inventory, which gets saved into *.blend file.
    """

    def length_update(self, context):
        """If the total time for animation is tweaked, FPS value is recalculated to keep the
        playback speed as close as possible to the resulting playback speed in the game engine.

        :param context: Blender Context
        :type context: bpy.types.Context
        """
        active_object = context.active_object
        if active_object and active_object.type == "ARMATURE" and active_object.animation_data:
            action = active_object.animation_data.action
            if action:
                _animation_utils.set_fps_for_preview(
                    context.scene,
                    self.length,
                    self.anim_start,
                    self.anim_end,
                )

    def anim_range_update(self, context):
        """If start or end frame are changed frame range in scene should be adopted to new values
        together with FPS reset.

        """

        active_object = context.active_object
        if active_object and active_object.type == "ARMATURE" and active_object.animation_data:
            action = active_object.animation_data.action
            if action:
                _animation_utils.set_frame_range(context.scene, self.anim_start, self.anim_end)
                _animation_utils.set_fps_for_preview(
                    context.scene,
                    self.length,
                    self.anim_start,
                    self.anim_end,
                )

    def anim_action_update(self, context):
        """Set action on armature if changed.
        """

        active_object = context.active_object
        if active_object and active_object.type == "ARMATURE":

            # ensure animation data block to be able to set action
            if active_object.animation_data is None:
                active_object.animation_data_create()

            if self.action in bpy.data.actions:
                active_object.animation_data.action = bpy.data.actions[self.action]
            else:
                active_object.animation_data.action = None

    name = StringProperty(name="Animation Name", default=_VARIANT_consts.default_name)
    export = BoolProperty(
        name="Export Inclusion",
        description="Include this SCS animation on Export and write it as SCS Animation file (PIA)",
        default=True,
    )
    action = StringProperty(
        name="Animation Action",
        description="Action used for this SCS animation",
        default="",
        options={'HIDDEN'},
        update=anim_action_update
    )
    anim_start = IntProperty(
        name="Animation Start",
        description="Action start frame for this SCS animation",
        default=1,
        options={'HIDDEN'},
        update=anim_range_update
    )
    anim_end = IntProperty(
        name="Animation End",
        description="Action end frame for this SCS animation",
        default=250,
        options={'HIDDEN'},
        update=anim_range_update
    )
    length = FloatProperty(
        name="Animation Length",
        description="Total length of this SCS Animation (in seconds)",
        default=10.0,
        min=0.1,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
        precision=6,
        update=length_update,
    )


class ObjectSCSTools(bpy.types.PropertyGroup):
    """
    SCS Tools Object Variables - ...Object.scs_props...
    """

    # HELPER VARIABLES
    locators_orig_draw_size = FloatProperty(name="Locator Original Draw Size")
    locators_orig_draw_type = StringProperty(name="Locator Original Draw Type")

    def empty_object_type_items(self, context):
        """Returns object type items in real time, because of accessing to custom icons.
        """
        return [
            ('None', "None", "Normal Blender Empty object", 'X', 0),
            ('SCS_Root', "Root Object", "Empty object will become a 'SCS Root Object'", get_icon(_ICON_TYPES.scs_root), 1),
            ('Locator', "Locator", "Empty object will become a 'Locator'", get_icon(_ICON_TYPES.loc), 2),
        ]

    def update_empty_object_type(self, context):

        if context.object:

            if self.empty_object_type == "SCS_Root":
                context.object.empty_draw_size = 5.0
                context.object.empty_draw_type = "ARROWS"
                context.object.show_name = True
            else:
                context.object.empty_draw_size = 1.0
                context.object.empty_draw_type = "PLAIN_AXES"
                context.object.show_name = False

    # EMPTY OBJECT TYPE
    empty_object_type = EnumProperty(
        name="SCS Object Type",
        description="Settings for Special SCS Objects",
        items=empty_object_type_items,
        update=update_empty_object_type
    )

    # SCS SKELETON OBJECTS
    scs_skeleton_custom_export_dirpath = StringProperty(
        name="Skeleton Custom Export Path",
        description="Custom export file path for skeleton PIS file (if empty skeleton is exported beside PIM file).",
        default="",
    )
    scs_skeleton_custom_name = StringProperty(
        name="Skeleton Custom Name",
        description="Custom name for SCS Skeleton PIS file (if empty name of skeleton file is the same as PIM file).",
        default="",
    )

    # SCS GAME OBJECTS
    scs_root_object_export_enabled = BoolProperty(
        name="Export",
        description="Enable / disable export of all object's children as single 'SCS Game Object'",
        default=True,
    )
    scs_root_animated = EnumProperty(
        name="Animation Output",
        description="Animation Output",
        items=(
            ('anim', "Animated Model", ""),
            ('rigid', "Rigid Model", ""),
        ),
        default='rigid',
    )
    scs_root_object_allow_custom_path = BoolProperty(
        name="Allow Custom Export File Path",
        description="Allow use of custom export file path for this 'SCS Game Object'",
        default=False,
    )
    scs_root_object_export_filepath = StringProperty(
        name="Custom Export File Path",
        description="Custom export file path for this 'SCS Game Object'",
        default="//",
        # subtype="FILE_PATH",
        subtype='NONE',
    )
    scs_root_object_allow_anim_custom_path = BoolProperty(
        name="Allow Custom Animations Export File Path",
        description="Allow use of custom export file path for animations of this 'SCS Game Object'",
        default=False,
    )
    scs_root_object_anim_export_filepath = StringProperty(
        name="Custom Animations Export File Path",
        description="Custom export file path for animations of this 'SCS Game Object'",
        default="//",
    )

    def active_scs_part_get_direct(self):
        """Accessing active part index directly if needed trough script. Not used by active_scs_part property itself
        """

        # make sure to set active sca part before accessing it
        # NOTE: case where this happens is if user imports SCS model,
        # duplicates prefab locator without part and then changes locator
        # type to model locator.
        if "active_scs_part_value" not in self:
            self["active_scs_part_value"] = 0

        return self["active_scs_part_value"]

    def active_scs_part_get(self):
        """Getting active index in SCS Parts list. On active object change active index of the list is altered
        with the index of part belonging to new active object.

        """

        if "active_scs_part_old_active" not in self:
            self["active_scs_part_old_active"] = ""

        if "active_scs_part_value" not in self:
            self["active_scs_part_value"] = 0

        scs_root_object = _object_utils.get_scs_root(bpy.context.active_object)
        if scs_root_object and bpy.context.active_object != scs_root_object:

            # if old active object is different than current
            # set the value for active part index from it
            if self["active_scs_part_old_active"] != bpy.context.active_object.name:
                self["active_scs_part_value"] = _inventory.get_index(scs_root_object.scs_object_part_inventory,
                                                                     bpy.context.active_object.scs_props.scs_part)

        self["active_scs_part_old_active"] = bpy.context.active_object.name
        return self["active_scs_part_value"]

    def active_scs_part_set(self, value):
        self["active_scs_part_value"] = value

    active_scs_part = IntProperty(
        name="Active SCS Part",
        description="Active SCS Part for current SCS Root Object",
        default=0,
        min=0,  # max=256,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
        get=active_scs_part_get,
        set=active_scs_part_set
    )

    def get_active_scs_look(self):

        if "active_scs_look" not in self:
            return -1

        return self["active_scs_look"]

    def set_active_scs_look(self, value):

        if value != self.get_active_scs_look():

            self["active_scs_look"] = value

            if bpy.context.active_object:

                scs_root = _object_utils.get_scs_root(bpy.context.active_object)
                if scs_root:
                    _looks.apply_active_look(scs_root)

    active_scs_look = IntProperty(
        name="Active SCS Look",
        description="Active SCS Look for current SCS Game Object",
        options={'HIDDEN'},
        get=get_active_scs_look,
        set=set_active_scs_look
    )
    active_scs_variant = IntProperty(
        name="Active SCS Variant",
        description="Active SCS Variant for current SCS Game Object",
        default=0,
        min=0,  # max=256,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
    )

    def active_scs_animation_update(self, context):
        """Update function for Active SCS Animation record on Objects.

        :param context: Blender Context
        :type context: bpy.types.Context
        :rtype: None
        """
        active_object = context.active_object
        scs_root_object = _object_utils.get_scs_root(active_object)
        scene = context.scene

        # GET ARMATURE OBJECT
        armature = None
        if active_object.type == 'ARMATURE':
            armature = active_object
        else:
            children = _object_utils.get_children(scs_root_object)
            for child in children:
                if child.type == 'ARMATURE':
                    armature = child
                    break

        scs_object_anim_inventory = scs_root_object.scs_object_animation_inventory
        active_scs_anim_i = self.active_scs_animation
        if len(scs_object_anim_inventory) > active_scs_anim_i:
            active_scs_anim = scs_object_anim_inventory[active_scs_anim_i]
            start_frame = active_scs_anim.anim_start
            end_frame = active_scs_anim.anim_end
            length = active_scs_anim.length

            # set frame range properly
            _animation_utils.set_frame_range(scene, start_frame, end_frame)

            # set action to armature end properly set preview fps
            action = None
            if active_scs_anim.action in bpy.data.actions:
                action = bpy.data.actions[active_scs_anim.action]

                _animation_utils.set_fps_for_preview(scene, length, start_frame, end_frame)

            # ensure animation data block to be able to set action
            if armature.animation_data is None:
                armature.animation_data_create()

            armature.animation_data.action = action  # set/reset action of current animation

        else:
            print('Wrong Animation index %i/%i!' % (active_scs_anim_i, len(scs_object_anim_inventory)))
        return None

    active_scs_animation = IntProperty(
        name="Active SCS Animation",
        description="Active SCS Animation for current SCS Game Object",
        default=0,
        min=0,  # max=256,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
        update=active_scs_animation_update,
    )

    scs_part = StringProperty(
        name="SCS Part",
        description="SCS Part for active object (type a new name to create new SCS Part)",
        default=_PART_consts.default_name,
        options={'HIDDEN'},
        subtype='NONE',
    )

    object_identity = StringProperty(
        name="Object Identity",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
    )
    parent_identity = StringProperty(
        name="Parent Identity",
        default="",
        options={'HIDDEN'},
        subtype='NONE',
    )

    # PREVIEW MODELS
    def locator_preview_model_path_update(self, context):
        """Update function for Locator Preview Model record on Objects.

        :param context: Blender Context
        :type context: bpy.types.Context
        :return: None
        """
        obj = context.object

        if _preview_models.load(obj, deep_reload=True):

            # fix selection because in case of actual loading model from file selection will be messed up
            obj.select = True
            bpy.context.scene.objects.active = obj

        else:

            _preview_models.unload(obj)

        return None

    def locator_show_preview_model_update(self, context):
        """Update function for Locator Show Preview Model record on Objects.

        :param context: Blender Context
        :type context: bpy.types.Context
        :return: None
        """
        obj = context.object

        if not _preview_models.load(obj):
            _preview_models.unload(obj)
        return None

    locator_preview_model_path = StringProperty(
        name="Preview Model",
        description="Preview model filepath",
        default="",
        # subtype="FILE_PATH",
        subtype='NONE',
        update=locator_preview_model_path_update,
    )
    locator_show_preview_model = BoolProperty(
        name="Show Preview Model",
        description="Show preview model",
        default=True,
        update=locator_show_preview_model_update,
    )
    locator_preview_model_present = BoolProperty(
        name="Preview Model Exists",
        default=False,
    )

    def locator_preview_model_type_update(self, context):

        obj = context.object

        for child in obj.children:

            if "scs_props" in child.data and child.data.scs_props.locator_preview_model_path != "":

                child.draw_type = obj.scs_props.locator_preview_model_type

    locator_preview_model_type = EnumProperty(
        name="Draw Type",
        description="Maximum draw type to display preview model with in viewport",
        items=(
            # ('TEXTURED', "Textured", "Draw the preview model with textures (if textures are enabled in the viewport)", 'TEXTURE_SHADED', 0),
            ('SOLID', "Solid", "Draw the preview model as a solid (if solid drawing is enabled in the viewport)", 'SOLID', 1),
            ('WIRE', "Wire", "Draw the bounds of the preview model", 'WIRE', 2),
            ('BOUNDS', "Bounds", "Draw the preview model with textures (if textures are enabled in the viewport)", 'BBOX', 3),
        ),
        default='WIRE',
        update=locator_preview_model_type_update
    )

    def locator_type_items(self, context):
        return [
            ('None', "None", "Object is not locator", 'X', 0),
            ('Prefab', "Prefab", "Prefab locator", get_icon(_ICON_TYPES.loc_prefab), 1),
            ('Model', "Model", "Model locator", get_icon(_ICON_TYPES.loc_model), 2),
            ('Collision', "Collision", "Collision locator", get_icon(_ICON_TYPES.loc_collider), 3),
        ]

    def locator_type_update(self, context):

        obj = context.object

        # safety check to ensure we are dealing with proper object
        # NOTE: if this gets triggered during import, it's very likely that another object
        # was already set as active. In that case error might occur while accessing scs properties.
        if not hasattr(obj, "scs_props"):
            return

        # PREVIEW MODELS LOADING
        if obj.scs_props.locator_type in ("Collision", "None"):
            _preview_models.unload(obj)
        elif not obj.scs_props.locator_preview_model_present:
            _preview_models.load(obj)

        # SCS_PART RESET
        if not _object_utils.has_part_property(obj):
            obj.scs_props.scs_part = ""
        else:

            scs_root_object = _object_utils.get_scs_root(obj)

            if scs_root_object:

                part_inventory = scs_root_object.scs_object_part_inventory

                # set part index to active or first
                # NOTE: direct access needed otherwise get function sets invalid index because
                # active object has still old part value
                part_index = scs_root_object.scs_props.active_scs_part_get_direct()
                if part_index >= len(part_inventory) or part_index < 0:
                    part_index = 0

                obj.scs_props.scs_part = part_inventory[part_index].name

            else:  # if no root assign default

                obj.scs_props.scs_part = _PART_consts.default_name

    # SCS LOCATORS
    locator_type = EnumProperty(
        name="Type",
        description="Locator type",
        items=locator_type_items,
        update=locator_type_update,
    )
    # LOCATORS - MODELS
    locator_model_hookup = StringProperty(
        name="Hookup",
        description="Hookup",
        default="",
        subtype='NONE',
    )

    def locator_collider_type_items(self, context):
        return [
            ('Box', "Box", "Box collider type", get_icon(_ICON_TYPES.loc_collider_box), 0),
            ('Sphere', "Sphere", "Sphere collider type", get_icon(_ICON_TYPES.loc_collider_sphere), 1),
            ('Capsule', "Capsule", "Capsule collider type", get_icon(_ICON_TYPES.loc_collider_capsule), 2),
            ('Cylinder', "Cylinder", "Cylinder collider type", get_icon(_ICON_TYPES.loc_collider_cylinder), 3),
            ('Convex', "Convex", "Convex collider type", get_icon(_ICON_TYPES.loc_collider_convex), 4),
        ]

    # LOCATORS - COLLIDERS
    locator_collider_type = EnumProperty(
        name="Collider Type",
        description="Collider locator type",
        items=locator_collider_type_items,
    )
    locator_collider_wires = BoolProperty(
        name="Collider Wireframes",
        description="Display wireframes for this collider",
        default=True,
    )
    locator_collider_faces = BoolProperty(
        name="Collider Faces",
        description="Display faces for this collider",
        default=True,
    )
    locator_collider_centered = BoolProperty(
        name="Locator Centered",
        description="Make locator centered",
        default=False,
    )
    locator_collider_mass = FloatProperty(
        name="Mass Weight",
        description="Mass of the element",
        default=1.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
    )
    # TODO: MATERIAL could be probably loaded from file ".../root/maya/shared/AEModelLocatorTemplate.mel"
    locator_collider_material = EnumProperty(
        name="Material",
        description="Collider's physical material",
        items=(
            ('und', "Undefined", ""),
        ),
        default='und',
    )
    # LOCATORS - COLLIDER - BOX
    locator_collider_box_x = FloatProperty(
        name="Box X Dimension",
        description="Box X dimension",
        default=1.0,
        min=0.01,
        options={'ANIMATABLE'},
        subtype='NONE',
        unit='NONE',
    )
    locator_collider_box_y = FloatProperty(
        name="Box Y Dimension",
        description="Box Y dimension",
        default=1.0,
        min=0.01,
        options={'ANIMATABLE'},
        subtype='NONE',
        unit='NONE',
    )
    locator_collider_box_z = FloatProperty(
        name="Box Z Dimension",
        description="Box Z dimension",
        default=1.0,
        min=0.01,
        options={'ANIMATABLE'},
        subtype='NONE',
        unit='NONE',
    )
    # LOCATORS - COLLIDER - SPHERE, CAPSULE, CYLINDER
    locator_collider_dia = FloatProperty(
        name="Diameter",
        description="Collider diameter",
        default=2.0,
        min=0.01,
        options={'ANIMATABLE'},
        subtype='NONE',
        unit='NONE',
    )
    locator_collider_len = FloatProperty(
        name="Length",
        description="Collider length",
        default=2.0,
        min=0.0, max=500,
        options={'ANIMATABLE'},
        subtype='NONE',
        unit='NONE',
    )

    # LOCATORS - COLLIDER - CONVEX
    def locator_collider_margin_update(self, context):
        """Update function for Locator Collider Margin record on Objects.

        :param context: Blender Context
        :type context: bpy.types.Context
        :return: None
        """

        if context.active_object:
            _object_utils.update_convex_hull_margins(context.active_object)

    locator_collider_margin = FloatProperty(
        name="Collision Margin",
        description="Collision margin of the element",
        default=0.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
        update=locator_collider_margin_update
    )
    locator_collider_vertices = IntProperty(
        name="Number of Convex Hull Vertices",
        description="Number of convex hull vertices",
        default=0,
        min=0,  # max=512,
        step=1,
        options={'HIDDEN'},
        subtype='NONE',
    )

    def locator_prefab_type_items(self, context):
        return [
            ('Control Node', "Control Node", "Control node locator type", get_icon(_ICON_TYPES.loc_prefab_node), 0),
            ('Sign', "Sign", "Sign locator type", get_icon(_ICON_TYPES.loc_prefab_sign), 1),
            ('Spawn Point', "Spawn Point", "Spawn point locator type", get_icon(_ICON_TYPES.loc_prefab_spawn), 2),
            ('Traffic Semaphore', "Traffic Semaphore", "Traffic light locator type", get_icon(_ICON_TYPES.loc_prefab_semaphore), 3),
            ('Navigation Point', "Navigation Point", "Navigation point locator type", get_icon(_ICON_TYPES.loc_prefab_navigation), 5),
            ('Map Point', "Map Point", "Map point locator type", get_icon(_ICON_TYPES.loc_prefab_map), 7),
            ('Trigger Point', "Trigger Point", "Trigger point locator type", get_icon(_ICON_TYPES.loc_prefab_trigger), 8),
        ]

    def locator_prefab_type_update(self, context):
        self.locator_type_update(context)

    # LOCATORS - PREFABS
    locator_prefab_type = EnumProperty(
        name="Prefab Type",
        description="Prefab locator type",
        items=locator_prefab_type_items,
        update=locator_prefab_type_update,
    )
    # LOCATORS - PREFAB - CONTROL NODES
    enum_con_node_index_items = OrderedDict()
    for i in range(_PL_consts.PREFAB_NODE_COUNT_MAX):
        enum_con_node_index_items[i] = (str(i), str(i), "")
    locator_prefab_con_node_index = EnumProperty(
        name="Node Index",
        description="Node index",
        items=enum_con_node_index_items.values(),
        default='0',
    )
    # LOCATORS - PREFAB - SIGNS
    # Following String property is fed from SIGN MODEL data list, which is usually loaded from
    # "//base/def/world/sign.sii" file and stored at "scs_globals.scs_sign_model_inventory".
    locator_prefab_sign_model = StringProperty(
        name="Sign Model",
        description="Sign model",
        default="",
        subtype='NONE',
        # update=locator_prefab_sign_model_update,
    )
    enum_spawn_type_items = OrderedDict([
        (_PL_consts.PSP.NONE, (str(_PL_consts.PSP.NONE), "None", "")),
        (_PL_consts.PSP.BUY_POS, (str(_PL_consts.PSP.BUY_POS), "Buy Point", "")),
        (_PL_consts.PSP.BUS_STATION, (str(_PL_consts.PSP.BUS_STATION), "Bus Station", "")),
        (_PL_consts.PSP.CAMERA_POINT, (str(_PL_consts.PSP.CAMERA_POINT), "Camera Point", "")),
        (_PL_consts.PSP.COMPANY_POS, (str(_PL_consts.PSP.COMPANY_POS), "Company Point", "")),
        (_PL_consts.PSP.COMPANY_UNLOAD_POS, (str(_PL_consts.PSP.COMPANY_UNLOAD_POS), "Company Unload Point", "")),
        # (_PL_consts.PSP.CUSTOM, (str(_PL_consts.PSP.CUSTOM), "Custom", "")),
        (_PL_consts.PSP.GARAGE_POS, (str(_PL_consts.PSP.GARAGE_POS), "Garage Point", "")),
        (_PL_consts.PSP.GAS_POS, (str(_PL_consts.PSP.GAS_POS), "Gas Station", "")),
        # (_PL_consts.PSP.HOTEL, (str(_PL_consts.PSP.HOTEL), "Hotel", "")),
        (_PL_consts.PSP.LONG_TRAILER_POS, (str(_PL_consts.PSP.LONG_TRAILER_POS), "Long Trailer", "")),
        # (_PL_consts.PSP.MEET_POS, (str(_PL_consts.PSP.MEET_POS), "Meet", "")),
        (_PL_consts.PSP.TRAILER_SPAWN, (str(_PL_consts.PSP.TRAILER_SPAWN), "Owned Trailer", "")),
        (_PL_consts.PSP.PARKING, (str(_PL_consts.PSP.PARKING), "Parking", "")),
        (_PL_consts.PSP.RECRUITMENT_POS, (str(_PL_consts.PSP.RECRUITMENT_POS), "Recruitment", "")),
        (_PL_consts.PSP.SERVICE_POS, (str(_PL_consts.PSP.SERVICE_POS), "Service Station", "")),
        # (_PL_consts.PSP.TASK, (str(_PL_consts.PSP.TASK), "Task", "")),
        (_PL_consts.PSP.TRAILER_POS, (str(_PL_consts.PSP.TRAILER_POS), "Trailer", "")),
        (_PL_consts.PSP.TRUCKDEALER_POS, (str(_PL_consts.PSP.TRUCKDEALER_POS), "Truck Dealer", "")),
        # (_PL_consts.PSP.TRUCKSTOP_POS, (str(_PL_consts.PSP.TRUCKSTOP_POS), "Truck Stop", "")),
        (_PL_consts.PSP.UNLOAD_EASY_POS, (str(_PL_consts.PSP.UNLOAD_EASY_POS), "Unload (Easy)", "")),
        (_PL_consts.PSP.UNLOAD_MEDIUM_POS, (str(_PL_consts.PSP.UNLOAD_MEDIUM_POS), "Unload (Medium)", "")),
        (_PL_consts.PSP.UNLOAD_HARD_POS, (str(_PL_consts.PSP.UNLOAD_HARD_POS), "Unload (Hard)", "")),
        (_PL_consts.PSP.UNLOAD_RIGID_POS, (str(_PL_consts.PSP.UNLOAD_RIGID_POS), "Unload (Rigid)", "")),
        (_PL_consts.PSP.WEIGHT_POS, (str(_PL_consts.PSP.WEIGHT_POS), "Weight Station", "")),
        (_PL_consts.PSP.WEIGHT_CAT_POS, (str(_PL_consts.PSP.WEIGHT_CAT_POS), "Weight Station CAT", "")),
    ])
    # LOCATORS - PREFAB - SPAWN POINTS
    locator_prefab_spawn_type = EnumProperty(
        name="Spawn Type",
        description="Spawn type",
        items=enum_spawn_type_items.values(),
        default=str(_PL_consts.PSP.NONE),
    )
    # LOCATORS - PREFAB - TRAFFIC LIGHTS (SEMAPHORES)
    enum_tsem_id_items = OrderedDict([(-1, ('-1', "None", ""))])
    for i in range(_PL_consts.TSEM_COUNT_MAX):
        enum_tsem_id_items[i] = (str(i), str(i), "")
    locator_prefab_tsem_id = EnumProperty(
        name="ID",
        description="ID",
        items=enum_tsem_id_items.values(),
        default='-1',
    )
    # Following String property is fed from TRAFFIC SEMAPHORE PROFILES data list, which is usually loaded from
    # "//base/def/world/semaphore_profile.sii" file and stored at "scs_globals.scs_tsem_profile_inventory".
    locator_prefab_tsem_profile = StringProperty(
        name="Profile",
        description="Traffic Semaphore Profile",
        default="",
        subtype='NONE',
    )
    enum_tsem_type_items = OrderedDict([
        (_PL_consts.TST.PROFILE, (str(_PL_consts.TST.PROFILE), "(use profile)", "")),
        (_PL_consts.TST.MODEL_ONLY, (str(_PL_consts.TST.MODEL_ONLY), "Model Only", "")),
        # (_PL_consts.TST.TRAFFIC_LIGHT, (str(_PL_consts.TST.TRAFFIC_LIGHT), "Traffic Light", "")),
        (_PL_consts.TST.TRAFFIC_LIGHT_MINOR, (str(_PL_consts.TST.TRAFFIC_LIGHT_MINOR), "Traffic Light (minor road)", "")),
        (_PL_consts.TST.TRAFFIC_LIGHT_MAJOR, (str(_PL_consts.TST.TRAFFIC_LIGHT_MAJOR), "Traffic Light (major road)", "")),
        (_PL_consts.TST.TRAFFIC_LIGHT_VIRTUAL, (str(_PL_consts.TST.TRAFFIC_LIGHT_VIRTUAL), "Traffic Light (virtual)", "")),
        (_PL_consts.TST.TRAFFIC_LIGHT_BLOCKABLE, (str(_PL_consts.TST.TRAFFIC_LIGHT_BLOCKABLE), "Blockable Traffic Light", "")),
        (_PL_consts.TST.BARRIER_MANUAL_TIMED, (str(_PL_consts.TST.BARRIER_MANUAL_TIMED), "Barrier - Manual", "")),
        (_PL_consts.TST.BARRIER_GAS, (str(_PL_consts.TST.BARRIER_GAS), "Barrier - Gas", "")),
        (_PL_consts.TST.BARRIER_DISTANCE, (str(_PL_consts.TST.BARRIER_DISTANCE), "Barrier - Distance Activated", "")),
        (_PL_consts.TST.BARRIER_AUTOMATIC, (str(_PL_consts.TST.BARRIER_AUTOMATIC), "Barrier - Automatic", "")),
    ])
    locator_prefab_tsem_type = EnumProperty(
        name="Type",
        description="Type",
        items=enum_tsem_type_items.values(),
        default=str(_PL_consts.TST.PROFILE),
    )
    locator_prefab_tsem_gs = FloatProperty(
        name="G",
        description="Time interval/Distance for Green light",
        default=15.0,
        min=-1.0,
        options={'HIDDEN'},
    )
    locator_prefab_tsem_os1 = FloatProperty(
        name="O",
        description="Time interval/Distance for after-green Orange light",
        default=2.0,
        min=-1.0,
        options={'HIDDEN'},
    )
    locator_prefab_tsem_rs = FloatProperty(
        name="R",
        description="Time interval/Distance for Red light",
        default=23.0,
        min=-1.0,
        options={'HIDDEN'},
    )
    locator_prefab_tsem_os2 = FloatProperty(
        name="O",
        description="Time interval/Distance for after-red Orange light",
        default=2.0,
        min=-1.0,
        options={'HIDDEN'},
    )
    locator_prefab_tsem_cyc_delay = FloatProperty(
        name="Cycle Delay",
        description="Number of seconds by which the whole traffic semaphore cycle is shifted.",
        default=0.0,
        min=0.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
    )
    # LOCATORS - PREFAB - NAVIGATION POINTS
    locator_prefab_np_low_probab = BoolProperty(
        name="Low Probability",
        description="Low probability",
        default=False,
    )
    locator_prefab_np_add_priority = BoolProperty(
        name="Additive Priority",
        description="Additive priority",
        default=False,
    )
    locator_prefab_np_limit_displace = BoolProperty(
        name="Limit Displacement",
        description="Limit displacement",
        default=False,
    )
    locator_prefab_np_allowed_veh = EnumProperty(
        name="Allowed Vehicles",
        description="Allowed vehicles",
        items=(
            (str(_PL_consts.PNCF.ALLOWED_VEHICLES_MASK), "All Vehicles", "", 'ANIM', 0),
            (str(_PL_consts.PNCF.SMALL_VEHICLES), "Small Vehicles", "", 'X', 1),
            (str(_PL_consts.PNCF.LARGE_VEHICLES), "Large Vehicles", "", 'AUTO', 2),
            ('0', "Player Only", "", 'POSE_DATA', 3),
        ),
        default=str(_PL_consts.PNCF.ALLOWED_VEHICLES_MASK),
    )
    locator_prefab_np_blinker = EnumProperty(
        name="Blinker",
        description="Blinker",
        items=(
            (str(_PL_consts.PNCF.LEFT_BLINKER), "Left Blinker", "", 'BACK', 0),
            ('0', "No Blinker", "", 'X', 1),
            (str(_PL_consts.PNCF.FORCE_NO_BLINKER), "No Blinker (forced)", "", 'X', 2),
            (str(_PL_consts.PNCF.RIGHT_BLINKER), "Right Blinker", "", 'FORWARD', 3),
        ),
        default='0',
    )
    enum_np_boundary_items = OrderedDict([(0, ('0', "No Boundary", ""))])
    for i in range(_PL_consts.PREFAB_LANE_COUNT_MAX):
        ii = 1 + i
        enum_np_boundary_items[ii] = (str(ii), "Input - Lane " + str(i), "")
    for i in range(_PL_consts.PREFAB_LANE_COUNT_MAX):
        ii = _PL_consts.PREFAB_LANE_COUNT_MAX + 1 + i
        enum_np_boundary_items[ii] = (str(ii), "Output - Lane " + str(i), "")
    locator_prefab_np_boundary = EnumProperty(
        name="Boundary",
        description="Boundary",
        items=enum_np_boundary_items.values(),
        default='0',
    )
    enum_np_boundary_node_items = OrderedDict()
    for i in range(_PL_consts.PREFAB_NODE_COUNT_MAX):
        enum_np_boundary_node_items[i] = (str(i), str(i), "")
    locator_prefab_np_boundary_node = EnumProperty(
        name="Boundary Node",
        description="Boundary node index",
        items=enum_np_boundary_node_items.values(),
        default='0',
    )
    enum_np_traffic_semaphore_items = OrderedDict([(-1, ('-1', "None", ""))])
    for i in range(_PL_consts.TSEM_COUNT_MAX):
        enum_np_traffic_semaphore_items[i] = (str(i), str(i), "")
    locator_prefab_np_traffic_semaphore = EnumProperty(
        name="Traffic Semaphore",
        description="Traffic semaphore ID",
        items=enum_np_traffic_semaphore_items.values(),
        default='-1',
    )
    # Following String property is fed from TRAFFIC SEMAPHORE PROFILES data list, which is usually loaded from
    # "//base/def/world/traffic_rules.sii" file and stored at "scs_globals.scs_traffic_rules_inventory".
    locator_prefab_np_traffic_rule = StringProperty(
        name="Traffic Rule",
        description="Traffic rule",
        default="",
        subtype='NONE',
    )
    enum_np_priority_modifier_items = OrderedDict([(0, ('0', "None", ""))])
    for i in range(1, (_PL_consts.PNCF.PRIORITY_MASK >> _PL_consts.PNCF.PRIORITY_SHIFT) + 1):

        name = str(i)

        # add additional name info for known priorities
        if i == 12:
            name += " - major road straight"
        elif i == 11:
            name += " - major road right"
        elif i == 10:
            name += " - major road left"
        elif i == 6:
            name += " - minor road straight"
        elif i == 5:
            name += " - minor road right"
        elif i == 4:
            name += " - minor road left"

        enum_np_priority_modifier_items[i] = (str(i), name, "")

    locator_prefab_np_priority_modifier = EnumProperty(
        name="Priority Modifier",
        description="Priority modifier",
        items=enum_np_priority_modifier_items.values(),
        default='0',
    )

    # LOCATORS - PREFAB - MAP POINTS
    locator_prefab_mp_road_over = BoolProperty(
        name="Road Over",
        description="The game tries to draw map point with this flag on top of all other map points",
        default=False,
    )
    locator_prefab_mp_no_outline = BoolProperty(
        name="No Outline",
        description="Don't draw the black outline (useful for 'drawing' buildings etc.)",
        default=False,
    )
    locator_prefab_mp_no_arrow = BoolProperty(
        name="No Arrow",
        description="Prevents drawing of a green navigation arrow "
                    "(useful for prefabs with more than 2 nodes, where path is clear also without an arrow)",
        default=False,
    )
    locator_prefab_mp_prefab_exit = BoolProperty(
        name="Prefab Exit",
        description="Mark the approximate location of the prefab exit "
                    "(useful for company prefabs where navigation will navigate from/to this point",
        default=False,
    )
    enum_mp_road_size_items = OrderedDict([
        (_PL_consts.MPVF.ROAD_SIZE_AUTO, (
            str(_PL_consts.MPVF.ROAD_SIZE_AUTO),
            "Auto", "The road size is automatically determmined based on connected roads."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_ONE_WAY, (
            str(_PL_consts.MPVF.ROAD_SIZE_ONE_WAY),
            "One Way", "Narrow road (one direction with one lane)."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_1_LANE, (
            str(_PL_consts.MPVF.ROAD_SIZE_1_LANE),
            "1 + 1 (2 + 0) Lane", "One lane in both directions. Or one way road with 2 lanes."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_3_LANE_ONE_WAY, (
            str(_PL_consts.MPVF.ROAD_SIZE_3_LANE_ONE_WAY),
            "2 + 1 (3 + 0) Lane", "Two lanes in one direction and one lane in second direction. Or one way with 3 lanes."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_2_LANE, (
            str(_PL_consts.MPVF.ROAD_SIZE_2_LANE),
            "2 + 2 (4 + 0) Lane", "Two lanes in both directions. Or one way road with 4 lanes."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_2_LANE_SPLIT, (
            str(_PL_consts.MPVF.ROAD_SIZE_2_LANE_SPLIT),
            "2 + 1 + 2 Lane", "Two lanes in both directions + one turning lane."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_3_LANE, (
            str(_PL_consts.MPVF.ROAD_SIZE_3_LANE),
            "3 + 3 Lane", "Three lanes in both directions."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_3_LANE_SPLIT, (
            str(_PL_consts.MPVF.ROAD_SIZE_3_LANE_SPLIT),
            "3 + 1 + 3 Lane", "Three lanes in both directions + one turning lane."
        )),
        (_PL_consts.MPVF.ROAD_SIZE_4_LANE, (
            str(_PL_consts.MPVF.ROAD_SIZE_4_LANE),
            "4 + 4 Lane", "Four lanes in both directions."
        )),
        # (_PL_consts.MPVF.ROAD_SIZE_4_LANE_SPLIT, (
        #     str(_PL_consts.MPVF.ROAD_SIZE_4_LANE_SPLIT),
        #     "4 + 1 + 4 Lane", ""
        # )),
        (_PL_consts.MPVF.ROAD_SIZE_MANUAL, (
            str(_PL_consts.MPVF.ROAD_SIZE_MANUAL),
            "Polygon", "The map point is used to draw a polygon instead of a road."
        )),
    ])
    locator_prefab_mp_road_size = EnumProperty(
        name="Road Size",
        description="Size and type of the road for this map point",
        items=enum_mp_road_size_items.values(),
        default=str(_PL_consts.MPVF.ROAD_SIZE_1_LANE),
    )
    enum_mp_road_offset_items = OrderedDict([
        (_PL_consts.MPVF.ROAD_OFFSET_0, (str(_PL_consts.MPVF.ROAD_OFFSET_0), "0 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_1, (str(_PL_consts.MPVF.ROAD_OFFSET_1), "1 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_2, (str(_PL_consts.MPVF.ROAD_OFFSET_2), "2 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_5, (str(_PL_consts.MPVF.ROAD_OFFSET_5), "5 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_10, (str(_PL_consts.MPVF.ROAD_OFFSET_10), "10 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_15, (str(_PL_consts.MPVF.ROAD_OFFSET_15), "15 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_20, (str(_PL_consts.MPVF.ROAD_OFFSET_20), "20 m", "")),
        (_PL_consts.MPVF.ROAD_OFFSET_25, (str(_PL_consts.MPVF.ROAD_OFFSET_25), "25 m", "")),
        # (_PL_consts.MPVF.ROAD_OFFSET_LANE, (str(_PL_consts.MPVF.ROAD_OFFSET_LANE), "", "")),
    ])
    locator_prefab_mp_road_offset = EnumProperty(
        name="Road Offset",
        description="The center offset between the road lanes",
        items=enum_mp_road_offset_items.values(),
        default=str(_PL_consts.MPVF.ROAD_OFFSET_0),
    )
    enum_mp_custom_color_items = OrderedDict([
        (0, ('0', "None", "Used for roads")),
        (_PL_consts.MPVF.CUSTOM_COLOR1, (str(_PL_consts.MPVF.CUSTOM_COLOR1), "Light", "Used for accessible prefab areas")),
        (_PL_consts.MPVF.CUSTOM_COLOR2, (str(_PL_consts.MPVF.CUSTOM_COLOR2), "Dark", "Used for buildings")),
        (_PL_consts.MPVF.CUSTOM_COLOR3, (str(_PL_consts.MPVF.CUSTOM_COLOR3), "Green", "Used for grass and inaccessible areas")),
    ])
    locator_prefab_mp_custom_color = EnumProperty(
        name="Custom Color",
        description="Colorizes map points when drawing them as polygons",
        items=enum_mp_custom_color_items.values(),
        default='0',
    )
    enum_mp_assigned_node_items = OrderedDict([(0, ('0', "None", ""))])
    for i in range(_PL_consts.PREFAB_NODE_COUNT_MAX):
        enum_mp_assigned_node_items[1 << i] = (str(1 << i), str(i), "")
    enum_mp_assigned_node_items[_PL_consts.MPNF.NAV_NODE_ALL] = (str(_PL_consts.MPNF.NAV_NODE_ALL), "All", "")
    locator_prefab_mp_assigned_node = EnumProperty(
        name="Assigned Node",
        description="Must be set to corresponding prefab Control Node for start/end map points "
                    "(for no navigation at all use 'All' option on all map points)",
        items=enum_mp_assigned_node_items.values(),
        default='0',
    )
    enum_mp_dest_nodes_items = OrderedDict()
    for i in range(_PL_consts.PREFAB_NODE_COUNT_MAX):
        enum_mp_dest_nodes_items[i] = (str(i), str(i), "Leads to Control Node with index %s" % i)
    locator_prefab_mp_dest_nodes = EnumProperty(
        name="Destination Nodes",
        description="Describes Control Nodes to which this map point can lead "
                    "(only set if one of neighbour map points has more than 2 connected map points)",
        items=enum_mp_dest_nodes_items.values(),
        default=set(),
        options={'ENUM_FLAG'},
    )

    # LOCATORS - PREFAB - TRIGGER POINTS
    locator_prefab_tp_action = StringProperty(
        name="Action",
        description="Action",
        default="",
        subtype='NONE',
    )
    locator_prefab_tp_range = FloatProperty(
        name="Range",
        description="Range of the trigger point. In case trigger point is Sphere Trigger "
                    "this is used as it's range otherwise it's used for up/down range.",
        default=3.0,
        min=0.1, max=50.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
    )
    locator_prefab_tp_reset_delay = FloatProperty(
        name="Reset Delay",
        description="Reset delay",
        default=0.0,
        min=0.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
    )
    locator_prefab_tp_sphere_trigger = BoolProperty(
        name="Sphere Trigger",
        description="Sphere trigger",
        default=False,
    )
    locator_prefab_tp_partial_activ = BoolProperty(
        name="Partial Activation",
        description="Partial activation",
        default=False,
    )
    locator_prefab_tp_onetime_activ = BoolProperty(
        name="One-Time Activation",
        description="One-time activation",
        default=False,
    )
    locator_prefab_tp_manual_activ = BoolProperty(
        name="Manual Activation",
        description="Manual activation",
        default=False,
    )
