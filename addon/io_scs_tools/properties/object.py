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
import os
from bpy.props import (StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       EnumProperty,
                       FloatProperty)
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.consts import Look as _LOOK_consts
from io_scs_tools.consts import Part as _PART_consts
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals import preview_models as _preview_models
from io_scs_tools.utils import animation as _animation_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.internals.icons.wrapper import get_icon
from io_scs_tools.utils.printout import lprint

_ICON_TYPES = _ICONS_consts.Types


class ObjectLooksInventory(bpy.types.PropertyGroup):
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


class ObjectPartInventory(bpy.types.PropertyGroup):
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


class ObjectVariantInventory(bpy.types.PropertyGroup):
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


class ObjectAnimationInventory(bpy.types.PropertyGroup):
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
        if active_object:
            if active_object.animation_data:
                action = active_object.animation_data.action
                if action:
                    scs_root_object = _object_utils.get_scs_root(active_object)
                    if scs_root_object:
                        active_scs_animation = scs_root_object.scs_props.active_scs_animation
                        scs_object_animation_inventory = scs_root_object.scs_object_animation_inventory
                        animation = scs_object_animation_inventory[active_scs_animation]
                        _animation_utils.set_fps_for_preview(
                            context.scene,
                            animation.length,
                            action.scs_props.anim_export_step,
                            animation.anim_start,
                            animation.anim_end,
                        )

    name = StringProperty(name="Animation Name", default=_VARIANT_consts.default_name)
    active = BoolProperty(name="Animation Activation Status", default=True)
    export = BoolProperty(
        name="Export Animation",
        description="Include actual Animation on Export and write it as an SCS Animation file (PIA)",
        default=False,
    )
    action = StringProperty(
        name="Animation Action",
        default="",
    )
    anim_start = IntProperty(
        name="Animation Start",
        description="Start frame for this animation",
        default=1,
        options={'HIDDEN'},
    )
    anim_end = IntProperty(
        name="Animation End",
        description="End frame for this animation",
        default=250,
        options={'HIDDEN'},
    )
    anim_export_filepath = StringProperty(
        name="Alternative Export Path",
        description="Alternative custom file path for export of animation",
        # default=utils.get_cgfx_templates_filepath(),
        default="",
        subtype="FILE_PATH",
        # update=anim_export_filepath_update,
    )
    length = FloatProperty(
        name="Animation Length",
        description="Animation total length (in seconds)",
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
        return [
            ('None', "None", "Normal Blender Empty object", 'X_VEC', 0),
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

    # SCS GAME OBJECTS

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

        scs_object_animation_inventory = scs_root_object.scs_object_animation_inventory
        active_scs_animation = self.active_scs_animation
        if len(scs_object_animation_inventory) > active_scs_animation:
            active_animation = scs_object_animation_inventory[active_scs_animation]
            animation_name = active_animation.name
            print('Animation changed to %r [%i].' % (animation_name, active_scs_animation))

            # SET ACTION STRING
            action = armature.animation_data.action
            action_names = []
            for act in bpy.data.actions:
                action_names.append(act.name)
            if animation_name in action_names:
                action = bpy.data.actions[animation_name]
                armature.animation_data.action = action
            active_object.data.scs_props.current_action = action.name

            # SET PREVIEW RANGE
            scene.use_preview_range = True
            print(
                'CAUTION! --- DELAYED START UPDATE ISSUE --- (see the code)')  # FIXME: If the start value is other than zero,
            # it gets only properly updated the second time an "SCS Animation" is hit in the list. For the first time it mysteriously
            # always gets the old 'anim_end' value. Test is on "multiple_animations_from_one_action.blend" file.
            print('scene.frame_preview_start:\t%i' % scene.frame_preview_start)
            print('active_animation.anim_start:\t\t%i' % active_animation.anim_start)
            start_frame = active_animation.anim_start
            scene.frame_preview_start = start_frame
            print('scene.frame_preview_start:\t%i' % scene.frame_preview_start)
            end_frame = active_animation.anim_end
            scene.frame_preview_end = end_frame
            # frame_range = action.frame_range
            # set_fps(scene, action, frame_range)
            # set_fps(scene, action, (active_animation.anim_start, active_animation.anim_end))
            length = active_animation.length
            anim_export_step = action.scs_props.anim_export_step
            _animation_utils.set_fps_for_preview(scene, length, anim_export_step, start_frame, end_frame)
        else:
            print('Wrong Animation index %i/%i!' % (active_scs_animation, len(scs_object_animation_inventory)))
        return None

    scs_root_object_export_enabled = BoolProperty(
        name="Export",
        description="Enable / disable export of all object's children as single 'SCS Game Object'",
        default=False,
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
        default=os.sep * 2,
        # subtype="FILE_PATH",
        subtype='NONE',
    )
    scs_root_object_animations = StringProperty(
        name="Animation Directory Name",
        description="This name is used for directory for animation files (if current 'SCS Game Object' contains any bone animated item)",
        default="anim",
        options={'HIDDEN'},
        subtype='NONE',
    )

    def active_scs_part_get_direct(self):
        """Accessing active part index directly if needed trough script. Not used by active_scs_part property itself
        """
        return self["active_scs_part_value"]

    def active_scs_part_get(self):
        """Getting active index in SCS Parts list. On active object change active index of the list is altered
        with the index of part belonging to new active object.

        """

        if not "active_scs_part_old_active" in self:
            self["active_scs_part_old_active"] = ""

        if not "active_scs_part_value" in self:
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

        if _preview_models.load(obj):

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
            ('None', "None", "Object is not locator", 'X_VEC', 0),
            ('Prefab', "Prefab", "Prefab locator", get_icon(_ICON_TYPES.loc_prefab), 1),
            ('Model', "Model", "Model locator", get_icon(_ICON_TYPES.loc_model), 2),
            ('Collision', "Collision", "Collision locator", get_icon(_ICON_TYPES.loc_collider), 3),
        ]

    def locator_type_update(self, context):

        obj = context.object

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
            # ('cob', "Colbox", "Colbox locator type", 'X_VEC', 4),
            ('Navigation Point', "Navigation Point", "Navigation point locator type", get_icon(_ICON_TYPES.loc_prefab_navigation), 5),
            # ('nac', "Navigation Curve", "Navigation curve locator type", 'X_VEC', 6),
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
    # LOCATORS - PREFABS GLOBAL CONSTANTS
    p_locator_nodes = 6
    p_locator_lanes = 8
    p_locator_tsems = 32
    p_priority_modif = 15
    # LOCATORS - PREFAB - CONTROL NODES
    it = []
    for i in range(p_locator_nodes):
        it.append((str(i), str(i), ""))
    locator_prefab_con_node_index = EnumProperty(
        name="Node Index",
        description="Node index",
        items=it,
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
    locator_prefab_sign_pref_part = StringProperty(
        name="Prefab Part",
        description="Prefab part",
        default="",
        subtype='NONE',
    )
    # LOCATORS - PREFAB - SPAWN POINTS
    locator_prefab_spawn_type = EnumProperty(
        name="Spawn Type",
        description="Spawn type",
        items=(
            ('0', "None", ""),
            ('1', "Trailer", ""),
            ('2', "Unload", ""),
            ('3', "Gas Station", ""),
            ('4', "Service Station", ""),
            # ('5', "Truck Stop", ""),
            ('6', "Weight Station", ""),
            ('7', "Truck Dealer", ""),
            # ('8', "Hotel", ""),
            # ('9', "Custom", ""),
            ('10', "Parking", ""),
            # ('11', "Task", ""),
            # ('12', "Meet", ""),
            ('13', "Company Point", ""),
            ('14', "Garage Point", ""),
            ('15', "Buy Point", ""),
            # ('16', "Recruitment", ""),
            ('17', "Camera Point", ""),
            ('18', "Bus Station", ""),
        ),
        default='0',
    )
    # LOCATORS - PREFAB - TRAFFIC LIGHTS (SEMAPHORES)
    it = [('none', "None", "")]
    for i in range(p_locator_tsems):
        it.append((str(i), str(i), ""))
    locator_prefab_tsem_id = EnumProperty(
        name="ID",
        description="ID",
        items=it,
        default='none',
    )
    # Following String property is fed from TRAFFIC SEMAPHORE PROFILES data list, which is usually loaded from
    # "//base/def/world/semaphore_profile.sii" file and stored at "scs_globals.scs_tsem_profile_inventory".
    locator_prefab_tsem_profile = StringProperty(
        name="Profile",
        description="Traffic Semaphore Profile",
        default="",
        subtype='NONE',
    )
    locator_prefab_tsem_type = EnumProperty(
        name="Type",
        description="Type",
        items=(
            ('0', "(use profile)", ""),
            ('1', "Model Only", ""),
            # ('2', "Traffic Light", ""),
            ('3', "Traffic Light (minor road)", ""),
            ('4', "Traffic Light (major road)", ""),
            ('5', "Barrier - Manual Timed", ""),
            ('6', "Barrier - Distance Activated", ""),
            ('7', "Blockable Traffic Light", ""),
        ),
        default='0',
    )
    locator_prefab_tsem_gs = FloatProperty(
        name="G",
        description="Time interval for Green light",
        default=15.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
    )
    locator_prefab_tsem_os1 = FloatProperty(
        name="O",
        description="Time interval for after-green Orange light",
        default=2.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
    )
    locator_prefab_tsem_rs = FloatProperty(
        name="R",
        description="Time interval for Red light",
        default=23.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
    )
    locator_prefab_tsem_os2 = FloatProperty(
        name="O",
        description="Time interval for after-red Orange light",
        default=2.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='TIME',
        unit='TIME',
    )
    locator_prefab_tsem_gm = FloatProperty(
        name="G",
        description="Distance where the Green light turns on",
        default=150.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='DISTANCE',
        unit='LENGTH',
    )
    locator_prefab_tsem_om1 = FloatProperty(
        name="O",
        description="Distance where the after-green Orange light turns on",
        default=300.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='DISTANCE',
        unit='LENGTH',
    )
    locator_prefab_tsem_rm = FloatProperty(
        name="R",
        description="Distance where the Red light turns on",
        default=200.0,
        min=-1.0,
        options={'HIDDEN'},
        subtype='DISTANCE',
        unit='LENGTH',
    )
    locator_prefab_tsem_cyc_delay = FloatProperty(
        name="Cycle Delay",
        description="Cycle Delay",
        default=0.0,
        min=0.0,
        options={'HIDDEN'},
        subtype='NONE',
        unit='NONE',
    )
    locator_prefab_tsem_activation = EnumProperty(
        name="Activation",
        description="Activation",
        items=(
            ('auto', "Automatic Timed", ""),
            ('man', "Manual Timed", ""),
            ('dis', "Mover Distance", ""),
        ),
        default='auto',
    )
    locator_prefab_tsem_ai_only = BoolProperty(
        name="AI Only",
        description="Artificial intelligence only",
        default=False,
    )
    # LOCATORS - PREFAB - NAVIGATION POINTS
    locator_prefab_np_tl_activ = BoolProperty(
        name="Traffic Semaphore Activator",
        description="Traffic light activator",
        default=False,
    )
    locator_prefab_np_low_prior = BoolProperty(
        name="Low Priority",
        description="Low priority",
        default=False,
    )
    locator_prefab_np_ig_blink_prior = BoolProperty(
        name="Ignore Blinker Priority",
        description="Ignore blinker priority",
        default=False,
    )
    locator_prefab_np_crossroad = BoolProperty(
        name="Crossroad",
        description="Crossroad",
        default=False,
    )
    locator_prefab_np_stopper = BoolProperty(
        name="Stopper",
        description="Stopper",
        default=False,
    )
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
    locator_prefab_np_allowed_veh = EnumProperty(
        name="Allowed Vehicles",
        description="Allowed vehicles",
        items=(
            ('all', "All Vehicles", "", 'ANIM', 0),
            ('nt', "No Trucks", "", 'X', 1),
            ('to', "Trucks Only", "", 'AUTO', 2),
            ('po', "Player Only", "", 'POSE_DATA', 3),
        ),
        default='all',
    )
    locator_prefab_np_speed_limit = FloatProperty(
        name="Speed Limit [km/h]",
        description="Speed limit in kilometers per hour",
        min=0, max=250,
        default=0.0,
        options={'HIDDEN'},
        subtype="DISTANCE",
        unit="VELOCITY",
    )
    locator_prefab_np_blinker = EnumProperty(
        name="Blinker",
        description="Blinker",
        items=(
            ('lb', "Left Blinker", "", 'BACK', 0),
            ('no', "No Blinker", "", 'X', 1),
            ('nf', "No Blinker (forced)", "", 'X_VEC', 2),
            ('rb', "Right Blinker", "", 'FORWARD', 3),
        ),
        default='no',
    )
    it = [('no', "No Boundary", "")]
    for i in range(p_locator_lanes):
        it.append(('in ' + str(i), "Input - Lane " + str(i), ""))
    for i in range(p_locator_lanes):
        it.append(('out ' + str(i), "Output - Lane " + str(i), ""))
    locator_prefab_np_boundary = EnumProperty(
        name="Boundary",
        description="Boundary",
        items=it,
        default='no',
    )
    it = []
    for i in range(p_locator_nodes):
        it.append((str(i), str(i), ""))
    locator_prefab_np_boundary_node = EnumProperty(
        name="Boundary Node",
        description="Boundary node",
        items=it,
        default='0',
    )
    it = [('-1', "None", "")]
    for i in range(p_locator_tsems):
        it.append((str(i), str(i), ""))
    locator_prefab_np_traffic_light = EnumProperty(
        name="Traffic Semaphore",
        description="Traffic light",
        items=it,
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
    it = [('-1', "None", "")]
    for i in range(p_priority_modif):
        it.append((str(i + 1), str(i + 1), ""))
    locator_prefab_np_priority_mask = EnumProperty(
        name="Priority Modifier",
        description="Priority modifier",
        items=it,
        default='-1',
    )

    # LOCATORS - PREFAB - MAP POINTS
    locator_prefab_mp_road_over = BoolProperty(
        name="Road Over",
        description="Road over",
        default=False,
    )
    locator_prefab_mp_no_outline = BoolProperty(
        name="No Outline",
        description="No outline",
        default=False,
    )
    locator_prefab_mp_no_arrow = BoolProperty(
        name="No Arrow",
        description="No arrow",
        default=False,
    )
    locator_prefab_mp_prefab_exit = BoolProperty(
        name="Prefab Exit",
        description="Prefab exit",
        default=False,
    )
    it = [('auto', "Auto", ""), ('ow', "One Way", "")]
    for i in range(4):
        it.append((str(i + 1) + ' lane', str(i + 1) + " - Lane", ""))
    it.append(('poly', "Polygon", ""))
    locator_prefab_mp_road_size = EnumProperty(
        name="Road Size",
        description="Road size",
        items=it,
        default='1 lane',
    )
    locator_prefab_mp_road_offset = EnumProperty(
        name="Road Offset",
        description="Road offset",
        items=(
            ('0m', "0m", ""),
            ('1m', "1m", ""),
            ('2m', "2m", ""),
            ('5m', "5m", ""),
            ('10m', "10m", ""),
            ('15m', "15m", ""),
            ('20m', "20m", ""),
            ('25m', "25m", ""),
        ),
        default='0m',
    )
    locator_prefab_mp_custom_color = EnumProperty(
        name="Custom Color",
        description="Custom color",
        items=(
            ('none', "None", ""),
            ('light', "Light", ""),
            ('dark', "Dark", ""),
            ('green', "Green", ""),
        ),
        default='none',
    )
    it = [('none', "None", "")]
    for i in range(p_locator_nodes):
        it.append((str(i), str(i), ""))
    it.append(('all', "All", ""))
    locator_prefab_mp_assigned_node = EnumProperty(
        name="Assigned Node",
        description="Assigned node",
        items=it,
        default='none',
    )
    locator_prefab_mp_des_nodes_0 = BoolProperty(
        name="0",
        description="0",
        default=False,
    )
    locator_prefab_mp_des_nodes_1 = BoolProperty(
        name="1",
        description="1",
        default=False,
    )
    locator_prefab_mp_des_nodes_2 = BoolProperty(
        name="2",
        description="2",
        default=False,
    )
    locator_prefab_mp_des_nodes_3 = BoolProperty(
        name="3",
        description="3",
        default=False,
    )
    locator_prefab_mp_des_nodes_ct = BoolProperty(
        name="Custom Target",
        description="Custom target",
        default=False,
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
        description="Range",
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
