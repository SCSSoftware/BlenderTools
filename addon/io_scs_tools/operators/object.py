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


import bmesh
import bpy
import re
from bpy.props import BoolProperty, StringProperty, IntProperty
from io_scs_tools.consts import Look as _LOOK_consts
from io_scs_tools.consts import Part as _PART_consts
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.consts import Icons as _ICONS_consts
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals.icons import get_icon as _get_icon
from io_scs_tools.internals.connections.wrappers import group as _connection_group_wrapper
from io_scs_tools.internals.open_gl.storage import terrain_points as _terrain_points_storage
from io_scs_tools.operators.bases.selection import Selection as _BaseSelectionOperator
from io_scs_tools.operators.bases.view import View as _BaseViewOperator
from io_scs_tools.properties.object import ObjectSCSTools as _ObjectSCSTools
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import animation as _animation_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


class ConvexCollider:
    """
    Wrapper class for better navigation in file
    """

    class MakeConvex(bpy.types.Operator):
        bl_label = "Make Convex From Selection"
        bl_idname = "object.make_convex"
        bl_description = "Create convex hull from selected objects"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            lprint('D Make Convex Geometry From Selection...')
            objects, active_object = _object_utils.pick_objects_from_selection(self, needs_active_obj=True, obj_type='MESH')
            if objects:
                geoms, convex_props, resulting_convex_object = _object_utils.create_convex_data(objects, create_hull=True)
                _object_utils.make_objects_selected((resulting_convex_object,))
            return {'FINISHED'}

    class ConvertToConvexLocator(bpy.types.Operator):
        bl_label = "Convert Meshes to Convex Collider"
        bl_idname = "object.convert_meshes_to_convex_locator"
        bl_description = "Convert selection to Convex Collision Locator"
        bl_options = {'REGISTER', 'UNDO'}

        delete_mesh_objects = BoolProperty(
            name="Delete Original Geometries",
            description="Delete all original Mesh Objects",
            default=False,
        )
        individual_objects = BoolProperty(
            name="Individual Objects",
            description="Make convex Locator from every individual Mesh Object in selection",
            default=False,
        )

        def execute(self, context):
            # print('Convert Selection to Convex Collision Locator...')
            objects, active_object = _object_utils.pick_objects_from_selection(self, needs_active_obj=True, obj_type='MESH')
            if objects:
                if self.individual_objects:
                    new_objects = []
                    for obj in objects:
                        parent = obj.parent
                        geoms, convex_props, resulting_convex_object = _object_utils.create_convex_data((obj,), create_hull=False)
                        locator = _object_utils.create_collider_convex_locator(geoms, convex_props, (obj,), self.delete_mesh_objects)
                        if locator:
                            locator.parent = parent
                            new_objects.append(locator)
                    if new_objects:
                        _object_utils.make_objects_selected(new_objects)
                else:
                    geoms, convex_props, resulting_convex_object = _object_utils.create_convex_data(objects, create_hull=False)
                    parent = active_object.parent
                    locator = _object_utils.create_collider_convex_locator(geoms, convex_props, objects, self.delete_mesh_objects)
                    if locator:
                        locator.parent = parent
                        # make sure to apply parent inverse matrix so object is oriented as origin object
                        locator.matrix_parent_inverse = active_object.matrix_parent_inverse
                        _object_utils.make_objects_selected((locator,))
            return {'FINISHED'}

    class ConvertFromConvex(bpy.types.Operator):
        bl_label = "Convert Convex Collider to Mesh"
        bl_idname = "object.convert_convex_locator_to_mesh"
        bl_description = "Convert Convex Collision Locator to Mesh Object"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            # print('Convert Convex Collision Locator to Mesh Object...')
            objects, active_object = _object_utils.pick_objects_from_selection(self, needs_active_obj=False, obj_type='EMPTY')
            new_active_object = None
            new_objects = []
            if objects:
                for obj in objects:
                    if obj.scs_props.locator_type == 'Collision':
                        if obj.scs_props.locator_collider_type == 'Convex':
                            parent = obj.parent
                            new_object = _object_utils.make_mesh_convex_from_locator(obj)
                            new_object.parent = parent
                            if obj == active_object:
                                new_active_object = new_object
                            new_objects.append(new_object)
            if new_objects:
                _object_utils.make_objects_selected(new_objects)
                # else:
                # self.report({'ERROR_INVALID_CONTEXT'}, "No Collision Convex Locator in selection to operate on!")
            if new_active_object:
                bpy.context.scene.objects.active = new_active_object
            return {'FINISHED'}

    class UpdateConvex(bpy.types.Operator):
        bl_label = "Update Convex Collider"
        bl_idname = "object.update_convex"
        bl_description = "Update Convex Collision Locator"

        def execute(self, context):
            lprint('D Update Convex Collider Locator...')
            _object_utils.update_convex_hull_margins(bpy.context.active_object)
            return {'FINISHED'}


class Look:
    """
    Wrapper class for better navigation in file
    """

    class AddLookOperator(bpy.types.Operator):
        """Add SCS Look to actual SCS Game Object."""
        bl_label = "Add SCS Look"
        bl_idname = "object.add_scs_look"
        bl_description = "Add new SCS Look to SCS Game Object"

        look_name = StringProperty(
            default=_LOOK_consts.default_name,
            description="Name of the new look"
        )
        instant_apply = BoolProperty(
            default=True,
            description="Flag indicating if new look should also be applied directly"
                        "(used on import when applying of each look is useless)"
        )

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:

                look_inventory = scs_root_object.scs_object_look_inventory

                # gather existing ids
                used_ids = {}
                for look in look_inventory:
                    used_ids[look.id] = 1

                # create unique id
                look_id = 0
                while look_id in used_ids:
                    look_id += 1

                look = _inventory.add_item(look_inventory, self.look_name, conditional=False)
                look.id = look_id

                _looks.add_look(scs_root_object, look.id)

                if self.instant_apply:
                    scs_root_object.scs_props.active_scs_look = len(look_inventory) - 1

            return {'FINISHED'}

    class RemoveActiveLookOperator(bpy.types.Operator):
        """Remove SCS Look to actual SCS Game Object."""
        bl_label = "Remove Active SCS Look"
        bl_idname = "object.remove_scs_look"
        bl_description = "Remove active SCS Look from SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Remove SCS Variant from SCS Game Object...')

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            active_scs_look = scs_root_object.scs_props.active_scs_look
            look_inventory = scs_root_object.scs_object_look_inventory

            if 0 <= active_scs_look < len(look_inventory):

                _looks.remove_look(scs_root_object, look_inventory[active_scs_look].id)

                _inventory.remove_items_by_id(look_inventory, active_scs_look)

                # if active index is not in the inventory anymore select last one
                if active_scs_look >= len(look_inventory):
                    scs_root_object.scs_props.active_scs_look = len(look_inventory) - 1

                # make sure to reapply currently selected look after removal
                _looks.apply_active_look(scs_root_object, force_apply=True)

            else:
                lprint("W No active 'SCS Look' to remove!")

            return {'FINISHED'}


class Part:
    """
    Wrapper class for better navigation in file
    """

    class SelectObjectsInPart(bpy.types.Operator, _BaseSelectionOperator):
        """Switch select state for objects of given SCS Part."""
        bl_label = "Select/Deselect All Objects In Part"
        bl_idname = "object.switch_part_selection"
        bl_description = "Switch selection for all objects in SCS Part" + _BaseSelectionOperator.bl_base_description

        part_index = IntProperty()

        def select_active_parts(self, objects, active_scs_part, outside_game_objects=False):

            actual_select_state = self.get_select_state()

            for obj in objects:
                if obj.type in ('EMPTY', 'MESH'):
                    if outside_game_objects:
                        if _object_utils.get_scs_root(obj):
                            continue
                    if obj.scs_props.scs_part == active_scs_part:

                        # set actual select state if it's not set yet
                        if actual_select_state is None:

                            actual_select_state = not obj.select
                            bpy.ops.object.select_all(action='DESELECT')

                        obj.select = actual_select_state
                    elif self.select_type not in (self.SHIFT_SELECT, self.CTRL_SELECT):
                        obj.select = False
            return

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if scs_root_object:

                children = _object_utils.get_children(scs_root_object)
                inventory = scs_root_object.scs_object_part_inventory

                if 0 <= self.part_index < len(inventory):
                    part_name = inventory[self.part_index].name
                    self.select_active_parts(children, part_name)
                else:
                    lprint("W Given 'SCS Part' index is not in list: %i", (self.part_index,))

            else:

                self.select_active_parts(context.scene.objects, active_object.scs_props.scs_part, True)

            return {'FINISHED'}

    class ViewObjectsInPart(bpy.types.Operator, _BaseViewOperator):
        """Switch view state for all objects of given Part."""
        bl_label = "View/Hide Objects In Part"
        bl_idname = "object.switch_part_visibility"
        bl_description = "Switch view state for all objects in SCS Part" + _BaseViewOperator.bl_base_description

        part_index = IntProperty()

        def view_active_part(self, objects, active_scs_part, outside_game_objects=False):

            actual_hide_state = self.get_hide_state()

            for obj in objects:
                if obj.type in ('EMPTY', 'MESH'):
                    if outside_game_objects:
                        if _object_utils.get_scs_root(obj):
                            continue
                    if obj.scs_props.scs_part == active_scs_part:

                        # set actual hide state if it's not set yet
                        if actual_hide_state is None:

                            actual_hide_state = not obj.hide

                        obj.hide = actual_hide_state

                    elif self.view_type == self.VIEWONLY:

                        obj.hide = True

            return

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if scs_root_object:

                children = _object_utils.get_children(scs_root_object)
                inventory = scs_root_object.scs_object_part_inventory

                if 0 <= self.part_index < len(inventory):
                    part_name = inventory[self.part_index].name
                    self.view_active_part(children, part_name)
                else:
                    lprint("W Given 'SCS Part' index is not in list: %i", (self.part_index,))
            else:

                self.view_active_part(context.scene.objects, active_object.scs_props.scs_part, True)

            return {'FINISHED'}

    class AddPartOperator(bpy.types.Operator):
        """Add SCS Part to actual SCS Game Object."""
        bl_label = "Add SCS Part"
        bl_idname = "object.add_scs_part"
        bl_description = "Add new SCS Part to SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:

                part_inventory = scs_root_object.scs_object_part_inventory
                variant_inventory = scs_root_object.scs_object_variant_inventory

                # ADD NEW PART
                part = _inventory.add_item(part_inventory, _PART_consts.default_name, conditional=False)

                # ADD NEW PART TO ALL VARIANTS
                for variant in variant_inventory:

                    variant_part = _inventory.add_item(variant.parts, part.name)
                    if variant_part:
                        variant_part.include = True
                    else:
                        lprint("W Part %r already in variant %r.", (part.name, variant.name))

                scs_root_object.scs_props.active_scs_part = len(part_inventory) - 1

            return {'FINISHED'}

    class RemoveActivePartOperator(bpy.types.Operator):
        """Remove SCS Part to actual SCS Game Object."""
        bl_label = "Remove Active SCS Part"
        bl_idname = "object.remove_scs_part"
        bl_description = "Remove active SCS Part from SCS Game Object (will be removed if none of the object uses it)"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            active_scs_part = scs_root_object.scs_props.active_scs_part
            part_inventory = scs_root_object.scs_object_part_inventory

            # DELETE SCS PART FROM PART INVENTORY
            if 0 <= active_scs_part < len(part_inventory):
                if len(part_inventory) > 1:

                    active_scs_part_name = part_inventory[active_scs_part].name

                    children = _object_utils.get_children(scs_root_object)
                    active_part_used_name = None
                    for child in children:
                        if child.scs_props.scs_part == active_scs_part_name:
                            active_part_used_name = child.name
                            break

                    # Remove the Part name if it is not used by any Object.
                    if not active_part_used_name:

                        _inventory.remove_items_by_id(part_inventory, active_scs_part)

                        # DELETE SCS PART FROM VARIANT-PART INVENTORY
                        for variant in scs_root_object.scs_object_variant_inventory:

                            _inventory.remove_items_by_name(variant.parts, [active_scs_part_name])

                        # if active index is not in the inventory anymore select last one
                        if active_scs_part >= len(part_inventory):
                            scs_root_object.scs_props.active_scs_part = len(part_inventory) - 1

                    else:
                        self.report({"ERROR"}, "Failed! Part is still used on object '%s'" % active_part_used_name)
                        lprint("W Cannot remove item which is still used by object '%s'.", (active_part_used_name,))
                else:
                    self.report({"ERROR"}, "Failed! Can not remove last part!")
                    lprint("W Cannot remove the last item!")
            else:
                lprint("W Active SCS Part index not in parts!")

            return {'FINISHED'}

    class CleanPartsOperator(bpy.types.Operator):
        """Removes all unused SCS Parts from SCS Game Object."""
        bl_label = "Clean SCS Parts"
        bl_idname = "object.clean_scs_parts"
        bl_description = "Removes all unused SCS Parts from SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            part_inventory = scs_root_object.scs_object_part_inventory

            children = _object_utils.get_children(scs_root_object)

            remove_part_list = []
            # DELETE SCS PART FROM PART INVENTORY
            for i, part in enumerate(part_inventory):
                if len(part_inventory) - len(remove_part_list) > 1:  # remove empty parts until only one is left

                    part_name = part.name

                    curr_part_used = False
                    for child in children:
                        if child.scs_props.scs_part == part_name:
                            curr_part_used = True
                            break

                    # Remove the Part name if it is not used by any Object.
                    if not curr_part_used:
                        remove_part_list.append(part_name)
                else:
                    self.report({"INFO"}, "Last SCS Part won't be removed! SCS Game object has to have at least one SCS Part.")

            # DELETE SCS PART FROM PART AND VARIANT INVENTORY
            if len(remove_part_list) > 0:

                _inventory.remove_items_by_name(part_inventory, remove_part_list)
                for variant in scs_root_object.scs_object_variant_inventory:

                    _inventory.remove_items_by_name(variant.parts, remove_part_list)

                # if active index is not in the inventory anymore select last one
                if scs_root_object.scs_props.active_scs_part >= len(part_inventory):
                    scs_root_object.scs_props.active_scs_part = len(part_inventory) - 1

            else:

                self.report({"INFO"}, "No parts were removed! No free SCS Parts for current SCS Game Object!")

            return {'FINISHED'}

    class AssignPartOperator(bpy.types.Operator):
        """Assign active SCS Part to selected objects."""
        bl_label = "Assign SCS Part"
        bl_idname = "object.assign_scs_part"
        bl_description = "Assign active SCS Part to selected objects"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            part_inventory = scs_root_object.scs_object_part_inventory
            active_part_index = scs_root_object.scs_props.active_scs_part

            scs_roots_count = len(_object_utils.gather_scs_roots(bpy.context.selected_objects))
            if scs_roots_count == 1:

                if 0 <= active_part_index < len(part_inventory):

                    active_part_name = part_inventory[active_part_index].name

                    for obj in bpy.context.selected_objects:
                        if obj.scs_props.empty_object_type != "SCS_Root" and _object_utils.has_part_property(obj):
                            obj.scs_props.scs_part = active_part_name

                else:
                    self.report({"ERROR"}, "Failed! Invalid active SCS Part in list!")

            elif scs_roots_count > 1:
                self.report({"ERROR"}, "Failed! Can not assign SCS Part because selection consists of multiple SCS Game Objects.")
            else:  # no root found for selected objects, this means only active object can be handled

                if 0 <= active_part_index < len(part_inventory):

                    active_part_name = part_inventory[active_part_index].name
                    active_object.scs_props.scs_part = active_part_name

                else:
                    self.report({"ERROR"}, "Failed! Invalid active SCS Part in list!")

            return {"FINISHED"}

    class PrintPartsOperator(bpy.types.Operator):
        """Print SCS Parts to actual SCS Game Object."""
        bl_label = "Print SCS Part"
        bl_idname = "object.print_scs_parts"
        bl_description = "Print SCS Parts to actual SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Print SCS Parts to actual SCS Game Object...')
            active_object = context.active_object
            lprint('I Object %r has SCS Part %r', (active_object.name, active_object.scs_props.scs_part))
            return {'FINISHED'}


class Variant:
    """
    Wrapper class for better navigation in file
    """

    class SelectObjectsInVariant(bpy.types.Operator, _BaseSelectionOperator):
        """Switch selection for all objects in Variant."""
        bl_label = "Select/Deselect All Objects In Variant"
        bl_idname = "object.switch_variant_selection"
        bl_description = "Switch selection for all objects in SCS Variant" + _BaseSelectionOperator.bl_base_description

        variant_index = IntProperty()

        def execute(self, context):
            lprint("D " + self.bl_label + "...")
            scs_root_object = _object_utils.get_scs_root(context.active_object)
            variant_inventory = scs_root_object.scs_object_variant_inventory

            if 0 <= self.variant_index <= len(variant_inventory):

                parts = [part.name for part in variant_inventory[self.variant_index].parts if part.include]
                actual_select_state = self.get_select_state()

                children = _object_utils.get_children(scs_root_object)
                for obj in children:
                    if obj.scs_props.scs_part in parts:

                        # set actual select state if it's not set yet
                        if actual_select_state is None:

                            actual_select_state = not obj.select
                            bpy.ops.object.select_all(action='DESELECT')

                        obj.select = actual_select_state
                    elif self.select_type not in (self.SHIFT_SELECT, self.CTRL_SELECT):
                        obj.select = False
            else:

                lprint("W Given index for 'SCS Variant' is out of bounds: %i", (self.variant_index,))

            return {'FINISHED'}

    class ViewObjectsInVariant(bpy.types.Operator, _BaseViewOperator):
        """Switch view state for all objects of given Variant."""
        bl_label = "View/Hide Objects In Variant"
        bl_idname = "object.switch_variant_visibility"
        bl_description = "Switch view state for all objects in SCS Variant" + _BaseViewOperator.bl_base_description

        variant_index = IntProperty()

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            scs_root_object = _object_utils.get_scs_root(context.active_object)
            variant_inventory = scs_root_object.scs_object_variant_inventory

            if 0 <= self.variant_index < len(variant_inventory):

                parts = [part.name for part in variant_inventory[self.variant_index].parts if part.include]
                actual_hide_state = self.get_hide_state()

                children = _object_utils.get_children(scs_root_object)
                for obj in children:
                    if obj.scs_props.scs_part in parts:

                        if actual_hide_state is None:
                            actual_hide_state = not obj.hide

                        obj.hide = actual_hide_state
                    elif self.view_type == self.VIEWONLY:
                        obj.hide = True
            else:

                lprint("W Given index for 'SCS Variant' is out of bounds: %i", (self.variant_index,))

            return {'FINISHED'}

    class AddVariantOperator(bpy.types.Operator):
        """Add SCS Variant to actual SCS Game Object."""
        bl_label = "Add SCS Variant"
        bl_idname = "object.add_scs_variant"
        bl_description = "Add new SCS Variant to SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint("D " + self.bl_label + "...")
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:

                part_inventory = scs_root_object.scs_object_part_inventory
                variant_inventory = scs_root_object.scs_object_variant_inventory

                # ADD NEW PART
                variant = _inventory.add_item(variant_inventory, _VARIANT_consts.default_name, conditional=False)

                # ADD PART NAMES
                for part in part_inventory:

                    variant_part = _inventory.add_item(variant.parts, part.name)
                    variant_part.include = True

                scs_root_object.scs_props.active_scs_variant = len(variant_inventory) - 1

            return {'FINISHED'}

    class RemoveActiveVariantOperator(bpy.types.Operator):
        """Remove SCS Variant to actual SCS Game Object."""
        bl_label = "Remove Active SCS Variant"
        bl_idname = "object.remove_scs_variant"
        bl_description = "Remove active SCS Variant from SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Remove SCS Variant from SCS Game Object...')

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            active_scs_variant = scs_root_object.scs_props.active_scs_variant
            variant_inventory = scs_root_object.scs_object_variant_inventory

            if 0 <= active_scs_variant < len(variant_inventory):

                _inventory.remove_items_by_id(variant_inventory, active_scs_variant)

                # if active index is not in the inventory anymore select last one
                if active_scs_variant >= len(variant_inventory):
                    scs_root_object.scs_props.active_scs_variant = len(variant_inventory) - 1

            else:
                lprint("W No active 'SCS Variant' to remove!")

            return {'FINISHED'}

    class PrintVariantsOperator(bpy.types.Operator):
        """Print SCS Variants to actual SCS Game Object."""
        bl_label = "Print SCS Variant"
        bl_idname = "object.print_scs_variants"
        bl_description = "Print SCS Variants to actual SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Print SCS Variants to actual SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if scs_root_object:
                lprint('I SCS Root Object %r has SCS Variants:', (scs_root_object.name,))
                for variant in scs_root_object.scs_object_variant_inventory:
                    lprint('I   > variant %r', (variant.name,))
                    for part in variant.parts:
                        lprint('I     > part %r', (part.name,))
            else:
                lprint("W Object %r has no 'SCS Root Object'!", (active_object.name,))
            return {'FINISHED'}


class ModelObjects:
    """
    Wrapper class for better navigation in file
    """

    class SelectModelObjects(bpy.types.Operator):
        """Selects all model objects."""
        bl_label = "Select Model Objects"
        bl_idname = "object.select_model_objects"
        bl_description = "Select model objects"

        def execute(self, context):
            lprint('D Select Model Objects...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if is_other:
                    obj.select = True
                else:
                    obj.select = False
            return {'FINISHED'}

    class ViewModelObjects(bpy.types.Operator, _BaseViewOperator):
        """Switch visibility of model objects."""
        bl_label = "Switch Visibility of Model Objects"
        bl_idname = "object.switch_model_objects_visibility"
        bl_description = "View only model objects" + _BaseViewOperator.bl_base_description

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            actual_hide_state = self.get_hide_state()

            for obj in self.get_objects(context):
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if is_other:

                    # set actual hide state if it's not set yet
                    if actual_hide_state is None:

                        actual_hide_state = not obj.hide

                    obj.hide = actual_hide_state

                elif self.view_type == self.VIEWONLY:

                    obj.hide = True

            return {'FINISHED'}


class ShadowCasters:
    """
    Wrapper class for better navigation in file
    """

    class SelectShadowCasters(bpy.types.Operator):
        """Selects all shadow casters."""
        bl_label = "Select Shadow Casters"
        bl_idname = "object.select_shadow_casters"
        bl_description = "Select shadow casters"

        def execute(self, context):
            lprint('D Select Shadow Casters...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_shadow:
                    obj.select = True
                else:
                    obj.select = False
            return {'FINISHED'}

    class ViewShadowCasters(bpy.types.Operator, _BaseViewOperator):
        """Switch visibility of shadow casters only."""
        bl_label = "Switch Visibility of Shadow Casters"
        bl_idname = "object.switch_shadow_casters_visibility"
        bl_description = "View only Shadow Casters" + _BaseViewOperator.bl_base_description

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            actual_hide_state = self.get_hide_state()

            for obj in self.get_objects(context):
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_shadow:

                    # set actual hide state if it's not set yet
                    if actual_hide_state is None:

                        actual_hide_state = not obj.hide

                    # when hiding ignore flavored shadow casters
                    if actual_hide_state is True and has_shadow and is_other:
                        continue

                    obj.hide = actual_hide_state

                elif self.view_type == self.VIEWONLY:

                    obj.hide = True

            return {'FINISHED'}

    class ShadowCasterObjectsInWireframes(bpy.types.Operator):
        """Shadow Caster objects in wireframes."""
        bl_label = "Shadow Caster Objects In Wireframes"
        bl_idname = "object.shadow_caster_objects_in_wireframes"
        bl_description = "Display all shadow caster objects as wireframes"

        def execute(self, context):
            lprint('D Shadow Casters Objects In Wireframes...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_shadow:
                    obj.draw_type = 'WIRE'
                    obj.show_all_edges = True
            return {'FINISHED'}

    class ShadowCasterObjectsTextured(bpy.types.Operator):
        """Shadow Caster objects textured."""
        bl_label = "Shadow Caster Objects Textured"
        bl_idname = "object.shadow_caster_objects_textured"
        bl_description = "Display all shadow caster objects textured"

        def execute(self, context):
            lprint('D Shadow Casters Objects Textured...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_shadow:
                    obj.draw_type = 'TEXTURED'
            return {'FINISHED'}


class Glass:
    """
    Wrapper class for better navigation in file
    """

    class SelectGlassObjects(bpy.types.Operator):
        """Selects all glass objects."""
        bl_label = "Select Glass Objects"
        bl_idname = "object.select_glass_objects"
        bl_description = "Select glass objects"

        def execute(self, context):
            lprint('D Select Glass Objects...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_glass:
                    obj.select = True
                else:
                    obj.select = False
            return {'FINISHED'}

    class ViewGlassObjects(bpy.types.Operator, _BaseViewOperator):
        """Switch visibility of glass objects."""
        bl_label = "Switch Visibility of Glass Objects"
        bl_idname = "object.switch_glass_objects_visibility"
        bl_description = "View only glass objects" + _BaseViewOperator.bl_base_description

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            actual_hide_state = self.get_hide_state()

            for obj in self.get_objects(context):
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_glass:

                    # set actual hide state if it's not set yet
                    if actual_hide_state is None:

                        actual_hide_state = not obj.hide

                    obj.hide = actual_hide_state

                elif self.view_type == self.VIEWONLY:

                    obj.hide = True

            return {'FINISHED'}

    class GlassObjectsInWireframes(bpy.types.Operator):
        """Glass objects in wireframes."""
        bl_label = "Glass Objects In Wireframes"
        bl_idname = "object.glass_objects_in_wireframes"
        bl_description = "Display all glass objects as wireframes"

        def execute(self, context):
            lprint('D Glass Objects In Wireframes...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_glass:
                    obj.draw_type = 'WIRE'
                    obj.show_all_edges = True
            return {'FINISHED'}

    class GlassObjectsTextured(bpy.types.Operator):
        """Glass objects textured."""
        bl_label = "Glass Objects Textured"
        bl_idname = "object.glass_objects_textured"
        bl_description = "Display all glass objects textured"

        def execute(self, context):
            lprint('D Glass Objects Textured...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_glass:
                    obj.draw_type = 'TEXTURED'
            return {'FINISHED'}


class Collision:
    """
    Wrapper class for better navigation in file
    """

    class SelectCollisionObjects(bpy.types.Operator):
        """Selects all glass objects."""
        bl_label = "Select static collision objects"
        bl_idname = "object.select_substance_objects"
        bl_description = "Select objects with material using physics substance"

        def execute(self, context):
            lprint('D Select Glass Objects...')
            for obj in context.scene.objects:
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_static_collision:
                    obj.select = True
                else:
                    obj.select = False
            return {'FINISHED'}

    class ViewCollisionObjects(bpy.types.Operator, _BaseViewOperator):
        """Switch visibility of glass objects."""
        bl_label = "Switch Visibility of static collision objects"
        bl_idname = "object.switch_substance_objects_visibility"
        bl_description = "View only objects which SCS Part is prefixed with 'coll', marking it as static collision object" + \
                         _BaseViewOperator.bl_base_description

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            actual_hide_state = self.get_hide_state()

            for obj in self.get_objects(context):
                has_shadow, has_glass, has_static_collision, is_other = _material_utils.get_material_info(obj)
                if has_static_collision:

                    # set actual hide state if it's not set yet
                    if actual_hide_state is None:

                        actual_hide_state = not obj.hide

                    obj.hide = actual_hide_state

                elif self.view_type == self.VIEWONLY:

                    obj.hide = True

            return {'FINISHED'}


class Locators:
    """
    Wrapper class for better navigation in file
    """

    class Model:
        """
        Wrapper class for better navigation in file
        """

        class SelectModelLocators(bpy.types.Operator):
            """Selects all model locators."""
            bl_label = "Select Model Locators"
            bl_idname = "object.select_model_locators"
            bl_description = "Select model locators"

            def execute(self, context):
                lprint('D Select Model Locators...')
                for obj in context.scene.objects:
                    if obj.scs_props.locator_type == 'Model':
                        obj.select = True
                    else:
                        obj.select = False
                return {'FINISHED'}

        class ViewModelLocators(bpy.types.Operator, _BaseViewOperator):
            """Switch visibility of model locators."""
            bl_label = "Switch Visibility of Model Locators"
            bl_idname = "object.switch_model_locators_visibility"
            bl_description = "View only model locators" + _BaseViewOperator.bl_base_description

            def execute(self, context):
                lprint("D " + self.bl_label + "...")

                actual_hide_state = self.get_hide_state()

                _object_utils.show_loc_type(self.get_objects(context), 'Model',
                                            hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                return {'FINISHED'}

    class Prefab:
        """
        Wrapper class for better navigation in file
        """

        class ControlNodes:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabNodeLocators(bpy.types.Operator):
                """Selects all prefab control node locators."""
                bl_label = "Select Prefab Control Node Locators"
                bl_idname = "object.select_prefab_nodes"
                bl_description = "Select prefab control node locators"

                def execute(self, context):
                    lprint('D Select Prefab Control Node Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Control Node':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabNodeLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab control node locators."""
                bl_label = "Switch Visibility of Prefab Control Node Locators"
                bl_idname = "object.switch_prefab_nodes_visibility"
                bl_description = "View only prefab control node locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Control Node',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

            class AssignTerrainPoints(bpy.types.Operator):
                bl_label = "Assign Terrain Points"
                bl_idname = "object.assign_terrain_points"
                bl_description = str("Assigns terrain point to currently selected prefab Control Node "
                                     "(confirm requested if some vertices from this mesh are already assigned).")

                vg_name = StringProperty()
                """Name of the vertex group for terrain points. It consists of vertex group prefix and node index."""

                @classmethod
                def poll(cls, context):
                    return _object_utils.can_assign_terrain_points(context)

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    active_obj = context.active_object

                    # ensure vertex group for current node
                    if self.vg_name not in active_obj.vertex_groups:
                        active_obj.vertex_groups.new(self.vg_name)

                    vg_instance = active_obj.vertex_groups[self.vg_name]

                    # collect vertices for terrain points
                    vertices_to_assign = []
                    for v in active_obj.data.vertices:
                        if v.select:
                            vertices_to_assign.append(v.index)

                    # assign terrain points to vertex group
                    bpy.ops.object.mode_set(mode='OBJECT')
                    vg_instance.remove(list(range(len(active_obj.data.vertices))))  # first remove all indices
                    vg_instance.add(vertices_to_assign, 1.0, 'REPLACE')  # finally add currently selected back to vertex group
                    bpy.ops.object.mode_set(mode='EDIT')

                    # remove vertex group if not needed anymore
                    if len(vertices_to_assign) == 0:
                        active_obj.vertex_groups.remove(vg_instance)

                    return {'FINISHED'}

                def invoke(self, context, event):

                    active_obj = context.active_object
                    other_obj = _object_utils.get_other_object(context.selected_objects, active_obj)
                    wm = context.window_manager

                    # set vertex group name regarding selected node index
                    self.vg_name = _OP_consts.TerrainPoints.vg_name_prefix + str(other_obj.scs_props.locator_prefab_con_node_index)

                    # switch between modes to ensure updated vertices data
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.mode_set(mode='EDIT')

                    if self.vg_name not in active_obj.vertex_groups:
                        return self.execute(context)
                    else:
                        return wm.invoke_confirm(self, event)  # ask user for overwrite

            class ClearTerrainPointsOperator(bpy.types.Operator):
                bl_label = "Clear All Terrain Points"
                bl_idname = "object.clear_all_terrain_points"
                bl_description = "Clears all terrain points for currently selected prefab Control Node"

                @classmethod
                def poll(cls, context):
                    active_obj = context.active_object
                    scs_root = _object_utils.get_scs_root(active_obj)

                    is_active_obj_node = active_obj and scs_root and (active_obj.type == "EMPTY" and
                                                                      active_obj.scs_props.empty_object_type == "Locator" and
                                                                      active_obj.scs_props.locator_type == "Prefab" and
                                                                      active_obj.scs_props.locator_prefab_type == "Control Node")

                    return is_active_obj_node or _object_utils.can_assign_terrain_points(context)

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    # make sure to abort possible preview operator
                    if bpy.ops.object.abort_preview_terrain_points.poll():
                        bpy.ops.object.abort_preview_terrain_points()

                    # if user is in assigning terrain points mode then node locator is other object
                    if context.active_object.mode == "EDIT":
                        node_loc_obj = _object_utils.get_other_object(context.selected_objects, context.active_object)
                    else:
                        node_loc_obj = context.active_object

                    vg_to_delete_count = 0
                    for sibling in _object_utils.get_siblings(node_loc_obj):

                        if sibling.type != "MESH":
                            continue

                        vg_to_delete = []
                        for vertex_group in sibling.vertex_groups:

                            # if vertex group name doesn't match prescribed one ignore this vertex group
                            if not re.match(_OP_consts.TerrainPoints.vg_name_regex, vertex_group.name):
                                continue

                            # if node index is not from current node ignore vertex group
                            node_index = vertex_group.name[-1]
                            if node_index != node_loc_obj.scs_props.locator_prefab_con_node_index:
                                continue

                            vg_to_delete.append(vertex_group)

                        vg_to_delete_count += len(vg_to_delete)

                        # remove all listed vertex groups
                        while len(vg_to_delete) > 0:
                            sibling.vertex_groups.remove(vg_to_delete.pop())

                    if vg_to_delete_count == 0:
                        self.report({'INFO'}, "No terrain points to clear!")

                    return {'FINISHED'}

            class PreviewTerrainPoints(bpy.types.Operator):
                bl_label = "Preview Terrain Points"
                bl_idname = "object.preview_terrain_points"
                bl_description = "Preview terrain points for currently selected prefab Control Node "

                preview_all = BoolProperty(
                    name="PreviewAll",
                    description="If False only terrain points from visible meshes are shown. Otherwise all terrain points are shown.",
                    default=False
                )

                is_active = False  # tells if any preview is already in progress, this will prevent possible multiple previews
                abort = False  # indicating if user manually aborted preview, via abort preview operator below

                __timer = None  # saves timer instance so it can be deleted when aborting
                __active_object = None  # caches active object for possible abort of operator when selection changes
                __active_object_mode = None  # caches active object mode state for possible abort of operator
                __active_object_matrix = None  # caches active object matrix for terrain point recalculation when object is transformed

                def execute_internal(self, context):

                    # clear any possible leftovers
                    _terrain_points_storage.clear()

                    # if user is in assigning terrain points mode then node locator is other object
                    if context.active_object.mode == "EDIT":
                        node_loc_obj = _object_utils.get_other_object(context.selected_objects, context.active_object)
                    else:
                        node_loc_obj = context.active_object

                    for sibling in _object_utils.get_siblings(node_loc_obj):

                        # ignore none mesh siblings or hidden siblings if previewing only visible
                        if sibling.type != "MESH" or (not self.preview_all and sibling.hide):
                            continue

                        for vertex_group in sibling.vertex_groups:

                            # if vertex group name doesn't match prescribed one ignore this vertex group
                            if not re.match(_OP_consts.TerrainPoints.vg_name_regex, vertex_group.name):
                                continue

                            # if node index is not from current node ignore vertex group
                            node_index = vertex_group.name[-1]
                            if node_index != node_loc_obj.scs_props.locator_prefab_con_node_index:
                                continue

                            # if user is in assigning terrain points mode then
                            # take data from bmesh for the object that is in edit mode
                            if sibling.mode == "EDIT":
                                bm = bmesh.from_edit_mesh(sibling.data)
                                bm.verts.ensure_lookup_table()
                            else:
                                bm = None

                            for v in sibling.data.vertices:
                                for group in v.groups:
                                    if vertex_group.index == group.group:

                                        if sibling.mode == "EDIT":
                                            co = bm.verts[v.index].co
                                        else:
                                            co = v.co

                                        # finally add terrain point if it has correct vertex group
                                        _terrain_points_storage.add(sibling.matrix_world * co, not sibling.hide)

                    # force view refresh
                    _view3d_utils.tag_redraw_all_view3d_and_props()

                    # cache active object matrix for possible terrain points desync check
                    self.__active_object_matrix = str(context.active_object.matrix_world)

                @classmethod
                def poll(cls, context):

                    # mark preview operator as disabled if preview is in progress
                    if cls.is_active:
                        return False

                    active_obj = context.active_object
                    scs_root = _object_utils.get_scs_root(active_obj)

                    is_active_obj_node = active_obj and scs_root and (active_obj.type == "EMPTY" and
                                                                      active_obj.scs_props.empty_object_type == "Locator" and
                                                                      active_obj.scs_props.locator_type == "Prefab" and
                                                                      active_obj.scs_props.locator_prefab_type == "Control Node")

                    return is_active_obj_node or _object_utils.can_assign_terrain_points(context)

                def modal(self, context, event):

                    is_aborted = Locators.Prefab.ControlNodes.PreviewTerrainPoints.abort
                    active_object_changed = self.__active_object != context.active_object
                    is_object_mode_changed = self.__active_object_mode != context.active_object.mode
                    is_transformed = self.__active_object_matrix and self.__active_object_matrix != str(context.active_object.matrix_world)

                    # abort if:
                    # 1. user manually press abort
                    # 2. active object mode has changed
                    # 3. if user changed active object
                    if is_aborted or is_object_mode_changed or active_object_changed:
                        self.cancel(context)
                        return {'CANCELLED'}

                    # extra abort step if there is nothing more to draw
                    if _terrain_points_storage.is_emtpy():
                        visible_msg = "visible " if not self.preview_all else ""
                        self.report({'INFO'}, "No " + visible_msg + "terrain points to preview for this node")
                        self.cancel(context)
                        return {'CANCELLED'}

                    # if user is in assigning terrain points mode or user is all selected objects
                    # make sure to update possible moved terrain points
                    if event.type == "TIMER" and (context.active_object.mode == "EDIT" or is_transformed):
                        self.execute_internal(context)

                    return {'PASS_THROUGH'}

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    self.execute_internal(context)

                    # set event timer which will take care of aborting
                    wm = context.window_manager
                    self.__timer = wm.event_timer_add(0.25, context.window)
                    self.__active_object = context.active_object
                    self.__active_object_mode = context.active_object.mode
                    self.__active_object_matrix = str(context.active_object.matrix_world)

                    Locators.Prefab.ControlNodes.PreviewTerrainPoints.is_active = True
                    Locators.Prefab.ControlNodes.PreviewTerrainPoints.abort = False

                    # use modal execution to abort operator if it gets aborted somehow
                    wm.modal_handler_add(self)
                    return {'RUNNING_MODAL'}

                def cancel(self, context):

                    # clear terrain points storage and force redraw
                    _terrain_points_storage.clear()
                    _view3d_utils.tag_redraw_all_view3d_and_props()

                    wm = context.window_manager
                    wm.event_timer_remove(self.__timer)

                    self.__timer = None
                    self.__active_object = None
                    self.__active_object_matrix = None

                    Locators.Prefab.ControlNodes.PreviewTerrainPoints.is_active = False

            class AbortPreviewTerrainPointsOperator(bpy.types.Operator):
                bl_label = "Abort Preview Terrain Points"
                bl_idname = "object.abort_preview_terrain_points"
                bl_description = "Abort preview of terrain points for currently selected prefab Control Node "

                @classmethod
                def poll(cls, context):
                    return Locators.Prefab.ControlNodes.PreviewTerrainPoints.is_active

                def execute(self, context):
                    Locators.Prefab.ControlNodes.PreviewTerrainPoints.abort = True
                    return {'FINISHED'}

        class Signs:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabSignLocators(bpy.types.Operator):
                """Selects all prefab sign locators."""
                bl_label = "Select Prefab Sign Locators"
                bl_idname = "object.select_prefab_signs"
                bl_description = "Select prefab sign locators"

                def execute(self, context):
                    lprint('D Select Prefab Sign Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Sign':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabSignLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab sign locators."""
                bl_label = "Switch Visibility of Prefab Sign Locators"
                bl_idname = "object.switch_prefab_signs_visibility"
                bl_description = "View only prefab sign locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Sign',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class SpawnPoints:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabSpawnLocators(bpy.types.Operator):
                """Selects all prefab spawn locators."""
                bl_label = "Select Prefab Spawn Locators"
                bl_idname = "object.select_prefab_spawns"
                bl_description = "Select prefab spawn locators"

                def execute(self, context):
                    lprint('D Select Prefab Spawn Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Spawn Point':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabSpawnLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visiblity of prefab spawn locators."""
                bl_label = "Switch Visibility of Prefab Spawn Locators"
                bl_idname = "object.switch_prefab_spawns_visibility"
                bl_description = "View only prefab spawn locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Spawn Point',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class TrafficLights:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabTrafficLocators(bpy.types.Operator):
                """Selects all prefab traffic locators."""
                bl_label = "Select Prefab Traffic Locators"
                bl_idname = "object.select_prefab_traffics"
                bl_description = "Select prefab traffic locators"

                def execute(self, context):
                    lprint('D Select Prefab Traffic Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Traffic Semaphore':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabTrafficLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab traffic locators."""
                bl_label = "Switch Visibility of Prefab Traffic Locators"
                bl_idname = "object.switch_prefab_traffics_visibility"
                bl_description = "View only prefab traffic locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Traffic Semaphore',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class NavigationPoints:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabNavigationLocators(bpy.types.Operator):
                """Selects all prefab navigation locators."""
                bl_label = "Select Prefab Navigation Locators"
                bl_idname = "object.select_prefab_navigations"
                bl_description = "Select prefab navigation locators"

                def execute(self, context):
                    lprint('D Select Prefab Navigation Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabNavigationLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab navigation locators."""
                bl_label = "Switch Visibility of Prefab Navigation Locators"
                bl_idname = "object.switch_prefab_navigations_visibility"
                bl_description = "View only prefab navigation locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Navigation Point',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class MapPoints:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabMapLocators(bpy.types.Operator):
                """Selects all prefab map locators."""
                bl_label = "Select Prefab Map Locators"
                bl_idname = "object.select_prefab_maps"
                bl_description = "Select prefab map locators"

                def execute(self, context):
                    lprint('D Select Prefab Map Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Map Point':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabMapLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab map locators."""
                bl_label = "Switch Visibility of Prefab Map Locators"
                bl_idname = "object.switch_prefab_maps_visibility"
                bl_description = "View only prefab map locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Map Point',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class TriggerPoints:
            """
            Wrapper class for better navigation in file
            """

            class SelectPrefabTriggerLocators(bpy.types.Operator):
                """Selects all prefab trigger locators."""
                bl_label = "Select Prefab Trigger Locators"
                bl_idname = "object.select_prefab_triggers"
                bl_description = "Select prefab trigger locators"

                def execute(self, context):
                    lprint('D Select Prefab Trigger Locators...')
                    for obj in context.scene.objects:
                        if obj.scs_props.locator_type == 'Prefab':
                            if obj.scs_props.locator_prefab_type == 'Trigger Point':
                                obj.select = True
                            else:
                                obj.select = False
                        else:
                            obj.select = False
                    return {'FINISHED'}

            class ViewPrefabTriggerLocators(bpy.types.Operator, _BaseViewOperator):
                """Switch visibility of prefab trigger locators."""
                bl_label = "Switch Visibility of Prefab Trigger Locators"
                bl_idname = "object.switch_prefab_triggers_visibility"
                bl_description = "View only prefab trigger locators" + _BaseViewOperator.bl_base_description

                def execute(self, context):
                    lprint("D " + self.bl_label + "...")

                    actual_hide_state = self.get_hide_state()

                    _object_utils.show_loc_type(self.get_objects(context), 'Prefab', 'Trigger Point',
                                                hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                    return {'FINISHED'}

        class ConnectPrefabLocators(bpy.types.Operator):
            bl_label = "Connect Prefab Locators"
            bl_idname = "object.connect_prefab_locators"
            bl_description = "To connect prefab locators two of them must be selected and they have to be same type"

            def execute(self, context):

                if len(context.selected_objects) == 2:
                    obj0 = None
                    obj1 = context.active_object

                    for selected in context.selected_objects:
                        if selected != obj1:
                            obj0 = selected

                    if not obj0.type == "EMPTY" or obj0.scs_props.locator_prefab_type not in ("Navigation Point", "Map Point", "Trigger Point"):
                        self.report({'ERROR'}, "Selected objects are not correct prefab locators or they are not the same type.")
                        return {'FINISHED'}

                    if _connection_group_wrapper.create_connection(obj0, obj1):
                        _view3d_utils.tag_redraw_all_view3d()
                    else:
                        msg = str("Failed, because of one of following reasons:\n"
                                  "-> connection already exists,\n"
                                  "-> current locators types can not be connected,\n"
                                  "-> one of locators doesn't have any empty slot.")
                        self.report({'ERROR'}, msg)

                else:
                    self.report({'ERROR'}, "In order to create connection, make sure you have selected two prefab locators of type Navigation "
                                           "Point, Map Point or Trigger Point")

                return {'FINISHED'}

        class DisconnectPrefabLocators(bpy.types.Operator):
            bl_label = "Disconnect Prefab Locators"
            bl_idname = "object.disconnect_prefab_locators"
            bl_description = "To disconnect navigation points two connected prefab locators must be selected"

            def execute(self, context):

                if len(context.selected_objects) == 2:
                    obj0_name = context.selected_objects[0].name
                    obj1_name = context.selected_objects[1].name

                    if _connection_group_wrapper.delete_connection(obj0_name, obj1_name):
                        _view3d_utils.tag_redraw_all_view3d()
                    else:
                        self.report({'ERROR'}, "Connection between selected objects doesn't exists!")

                return {'FINISHED'}

        class SelectPrefabLocators(bpy.types.Operator):
            """Selects all prefab locators."""
            bl_label = "Select Prefab Locators"
            bl_idname = "object.select_prefab_locators"
            bl_description = "Select prefab locators"

            def execute(self, context):
                lprint('D Select Prefab Locators...')
                for obj in context.scene.objects:
                    if obj.scs_props.locator_type == 'Prefab':
                        obj.select = True
                    else:
                        obj.select = False
                return {'FINISHED'}

        class ViewPrefabLocators(bpy.types.Operator, _BaseViewOperator):
            """Switch visibility of prefab locators."""
            bl_label = "Switch Visibility of Prefab Locators"
            bl_idname = "object.switch_prefab_locators_visibility"
            bl_description = "View only prefab locators" + _BaseViewOperator.bl_base_description

            def execute(self, context):
                lprint("D " + self.bl_label + "...")

                actual_hide_state = self.get_hide_state()

                _object_utils.show_loc_type(self.get_objects(context), 'Prefab',
                                            hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                return {'FINISHED'}

    class Collision:
        """
        Wrapper class for better navigation in file
        """

        class SelectCollisionLocators(bpy.types.Operator):
            """Selects all collision locators."""
            bl_label = "Select Collision Locators"
            bl_idname = "object.select_collision_locators"
            bl_description = "Select collision locators"

            def execute(self, context):
                lprint('D Select Collision Locators...')
                for obj in context.scene.objects:
                    if obj.scs_props.locator_type == 'Collision':
                        obj.select = True
                    else:
                        obj.select = False
                return {'FINISHED'}

        class ViewCollisionLocators(bpy.types.Operator, _BaseViewOperator):
            """Switch visibility of collision locators."""
            bl_label = "Switch Visibility of Collision Locators"
            bl_idname = "object.switch_collision_locators_visibility"
            bl_description = "View only collision locators" + _BaseViewOperator.bl_base_description

            def execute(self, context):
                lprint("D " + self.bl_label + "...")

                actual_hide_state = self.get_hide_state()

                _object_utils.show_loc_type(self.get_objects(context), 'Collision',
                                            hide_state=actual_hide_state, view_only=self.view_type == self.VIEWONLY)
                return {'FINISHED'}

        class AllCollisionLocatorsWire(bpy.types.Operator):
            """All Collision Locators Wireframes ON."""
            bl_label = "All Collision Locators Wireframes ON"
            bl_idname = "object.all_collision_locators_wires"
            bl_description = "Turn ON wireframes draw in all collision locators"

            def execute(self, context):
                lprint('D All Collision Locators Wireframes ON...')
                for obj in context.scene.objects:
                    if obj.type == 'EMPTY':
                        if obj.scs_props.locator_type == 'Collision':
                            obj.scs_props.locator_collider_wires = True
                return {'FINISHED'}

        class NoCollisionLocatorsWire(bpy.types.Operator):
            """All Collision Locators Wireframes OFF."""
            bl_label = "All Collision Locators Wireframes OFF"
            bl_idname = "object.no_collision_locators_wires"
            bl_description = "Turn OFF wireframes draw in all collision locators"

            def execute(self, context):
                lprint('D All Collision Locators Wireframes OFF...')
                for obj in context.scene.objects:
                    if obj.type == 'EMPTY':
                        if obj.scs_props.locator_type == 'Collision':
                            obj.scs_props.locator_collider_wires = False
                return {'FINISHED'}

        class AllCollisionLocatorsFaces(bpy.types.Operator):
            """All Collision Locators Faces ON."""
            bl_label = "All Collision Locators Faces ON"
            bl_idname = "object.all_collision_locators_faces"
            bl_description = "Turn ON faces draw in all collision locators"

            def execute(self, context):
                lprint('D All Collision Locators Faces ON...')
                for obj in context.scene.objects:
                    if obj.type == 'EMPTY':
                        if obj.scs_props.locator_type == 'Collision':
                            obj.scs_props.locator_collider_faces = True
                return {'FINISHED'}

        class NoCollisionLocatorsFaces(bpy.types.Operator):
            """All Collision Locators Faces OFF."""
            bl_label = "All Collision Locators Faces OFF"
            bl_idname = "object.no_collision_locators_faces"
            bl_description = "Turn OFF faces draw in all collision locators"

            def execute(self, context):
                lprint('D All Collision Locators Faces OFF...')
                for obj in context.scene.objects:
                    if obj.type == 'EMPTY':
                        if obj.scs_props.locator_type == 'Collision':
                            obj.scs_props.locator_collider_faces = False
                return {'FINISHED'}

    class Commons:
        """
        Wrapper class for better navigation in file
        """

        class SelectAllLocators(bpy.types.Operator):
            """Selects all locators."""
            bl_label = "Select All Locators"
            bl_idname = "object.select_all_locators"
            bl_description = "Select all locators"

            def execute(self, context):
                lprint('D Select All Locators...')
                for obj in context.scene.objects:
                    if obj.scs_props.locator_type != 'None':
                        obj.select = True
                    else:
                        obj.select = False
                return {'FINISHED'}

        class ViewAllLocators(bpy.types.Operator, _BaseViewOperator):
            """Switch visibility all locators."""
            bl_label = "Switch Visibility of All Locators"
            bl_idname = "object.switch_all_locators_visibility"
            bl_description = "View only all locators" + _BaseViewOperator.bl_base_description

            def execute(self, context):
                lprint("D " + self.bl_label + "...")

                actual_hide_state = self.get_hide_state()

                for obj in self.get_objects(context):
                    if obj.scs_props.locator_type != 'None' or (obj.type == 'MESH' and obj.scs_props.locator_preview_model_path != ""):

                        # set actual hide state if it's not set yet
                        if actual_hide_state is None:

                            actual_hide_state = not obj.hide

                        obj.hide = actual_hide_state

                    elif self.view_type == self.VIEWONLY:

                        obj.hide = True

                return {'FINISHED'}

        class PreviewModelPath(bpy.types.Operator):
            """Operator for setting a relative path to Preview model file."""
            bl_label = "Select Preview Model (*.pim)"
            bl_idname = "object.select_preview_model_path"
            bl_description = "Open a file browser"

            filepath = StringProperty(
                name="Preview Model File Path",
                description="Relative path to a Preview model file",
                # maxlen=1024,
                subtype='FILE_PATH',
            )
            filter_glob = StringProperty(default="*.pim", options={'HIDDEN'})

            def execute(self, context):
                """Set Traffic Semaphore Profile directory paths."""
                rel_path = _path_utils.relative_path(_get_scs_globals().scs_project_path, self.filepath)
                context.active_object.scs_props.locator_preview_model_path = str(rel_path)
                # print('   DIR: "%s"' % str(_get_scs_globals().scs_project_path + bpy.data.worlds[
                # 0].scs_globals.tsem_library_rel_path[1:]))
                # print('Is DIR: "%s"' % os.path.isdir(str(_get_scs_globals().scs_project_path + bpy.data.worlds[
                # 0].scs_globals.tsem_library_rel_path[1:])))
                return {'FINISHED'}

            def invoke(self, context, event):
                """Invoke a path selector."""
                context.window_manager.fileselect_add(self)
                return {'RUNNING_MODAL'}


class SCSRoot:
    """
    Wrapper class for better navigation in file
    """

    class AddSCSRootObjectDialogOperator(bpy.types.Operator):
        """Makes a dialog window allowing specifying a new Part name and adds it into Part list."""
        bl_idname = "object.add_scs_root_object_dialog_operator"
        bl_label = "Add SCS Root Dialog"
        bl_description = "Create dialog for adding new scs root (shouldn't be executed by user)"
        bl_options = {"INTERNAL"}

        scs_root_object_string = StringProperty(name="Name for a new 'SCS Root Object':")

        def execute(self, context):
            context.active_object.name = _name_utils.remove_diacritic(self.scs_root_object_string)
            return {'FINISHED'}

        def invoke(self, context, event):
            self.scs_root_object_string = context.active_object.name
            return context.window_manager.invoke_props_dialog(self)

    class CreateSCSRootObject(bpy.types.Operator):
        """Create New SCS Root Object."""
        bl_label = "Add New SCS Root Object"
        bl_idname = "object.create_scs_root_object"
        bl_description = "Create a new 'SCS Root Object' with initial setup. If any objects are selected," \
                         "they automatically become a part of the new 'SCS Game Object'."

        def execute(self, context):
            lprint('D Create New SCS Root Object...')
            _object_utils.make_scs_root_object(context, dialog=False)
            return {'FINISHED'}

    class CreateSCSRootObjectDialog(bpy.types.Operator):
        """Create New SCS Root Object."""
        bl_label = "Add New SCS Root Object"
        bl_idname = "object.create_scs_root_object_dialog"
        bl_description = "Create a new 'SCS Root Object' with initial setup.\nIf any objects are selected," \
                         "they automatically become a part of the new 'SCS Game Object'."

        def execute(self, context):
            lprint('D Create New SCS Root Object with Name dialog...')
            _object_utils.make_scs_root_object(context, dialog=True)
            return {'FINISHED'}

    class HideObjects(bpy.types.Operator):
        bl_label = "Hide objects within current SCS Game Object"
        bl_idname = "object.hide_objects_within_root"
        bl_description = "Hide all the objects in active layers within current SCS Game Object"

        def execute(self, context):
            lprint('D Hide objects within current SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:
                for obj in _object_utils.get_children(scs_root_object):
                    if obj.type in ('EMPTY', 'MESH') and obj.scs_props.empty_object_type != 'SCS_Root':
                        obj.hide = True

            return {'FINISHED'}

    class ViewAllObjects(bpy.types.Operator):
        """Shows all the objects within current SCS Root object."""
        bl_label = "View All Objects Within SCS Root"
        bl_idname = "object.view_all_objects_within_root"
        bl_description = "Shows all the objects within current SCS Root object"

        @classmethod
        def poll(cls, context):
            return _object_utils.get_scs_root(context.active_object) is not None

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            if scs_root_object:
                for obj in _object_utils.get_children(scs_root_object):
                    if obj.type in ('EMPTY', 'MESH') and obj.scs_props.empty_object_type != 'SCS_Root':
                        obj.hide = False

            scs_root_object.hide = False

            return {'FINISHED'}

    class InvertVisibility(bpy.types.Operator):
        """Invert visibility of the objects within current SCS Root object."""
        bl_label = "Invert Visibility Within SCS Root"
        bl_idname = "object.invert_visibility_within_root"
        bl_description = "Invert visibility of the objects within current SCS Root object"

        @classmethod
        def poll(cls, context):
            return _object_utils.get_scs_root(context.active_object) is not None

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:
                for obj in _object_utils.get_children(scs_root_object):
                    if obj.type in ('EMPTY', 'MESH') and obj.scs_props.empty_object_type != 'SCS_Root':
                        if obj.hide:
                            obj.hide = False
                            bpy.context.scene.objects.active = obj
                        else:
                            obj.hide = True

            return {'FINISHED'}

    class Isolate(bpy.types.Operator):
        """Isolate all of the objects within current SCS Root object."""
        bl_label = "Isolate Objects Within SCS Root"
        bl_idname = "object.isolate_objects_within_root"
        bl_description = "Isolate all of the objects within current SCS Root object"

        @classmethod
        def poll(cls, context):
            return _object_utils.get_scs_root(context.active_object) is not None

        def execute(self, context):
            lprint("D " + self.bl_label + "...")

            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            if scs_root_object:
                children = _object_utils.get_children(scs_root_object)
                for obj in bpy.context.scene.objects:
                    if obj in children:
                        obj.hide = False
                        obj.select = True
                    else:
                        obj.hide = True
                        obj.select = False

                scs_root_object.hide = False
                scs_root_object.select = True
                bpy.context.scene.objects.active = scs_root_object

            return {'FINISHED'}


class Animation:
    """
    Wrapper class for better navigation in file
    """

    class AddSCSAnimationOperator(bpy.types.Operator):
        """Add SCS Animation to actual SCS Game Object."""
        bl_label = "Add SCS Animation"
        bl_idname = "object.add_scs_animation"
        bl_description = "Add SCS Animation to actual SCS Game Object"

        @classmethod
        def poll(cls, context):
            return _object_utils.get_scs_root(context.active_object) is not None

        def execute(self, context):
            lprint('D Add SCS Animation to actual SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            _animation_utils.add_animation_to_root(scs_root_object, scs_root_object.name)

            # select last one as this is new animation
            scs_root_object.scs_props.active_scs_animation = len(scs_root_object.scs_object_animation_inventory) - 1

            return {'FINISHED'}

    class RemoveSCSAnimationOperator(bpy.types.Operator):
        """Remove SCS Animation to actual SCS Game Object."""
        bl_label = "Remove SCS Animation"
        bl_idname = "object.remove_scs_animation"
        bl_description = "Remove SCS Animation to actual SCS Game Object"

        @classmethod
        def poll(cls, context):
            active_obj = context.active_object
            return active_obj and active_obj.type == "ARMATURE" and _object_utils.get_scs_root(active_obj)

        def execute(self, context):
            lprint('D Remove SCS Animation to actual SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            active_scs_anim_i = scs_root_object.scs_props.active_scs_animation
            inventory = scs_root_object.scs_object_animation_inventory

            if active_scs_anim_i < len(inventory):
                active_scs_anim = inventory[active_scs_anim_i]
                if len(inventory) > active_scs_anim_i:

                    if active_scs_anim.action in bpy.data.actions and active_object.animation_data.action:

                        active_object.animation_data.action = None

                        # remove fake user from action if it was used only by removed scs animation
                        action = bpy.data.actions[active_scs_anim.action]
                        if action.users == 1 and action.use_fake_user:
                            action.use_fake_user = False

                    lprint('S inventory[%i] - REMOVE item[%i] %r...', (len(inventory), active_scs_anim_i, active_scs_anim.name))
                    inventory.remove(active_scs_anim_i)
                else:
                    lprint("W No active 'SCS Animation' in list!")
            else:
                lprint("W No active 'SCS Animation' to remove!")
            return {'FINISHED'}


class AddObject(bpy.types.Operator):
    """Creates and links locator or SCS Root to the scenes."""
    bl_label = "Add SCS Object"
    bl_idname = "object.scs_add_object"
    bl_description = "Create SCS object of choosen type at 3D coursor position \n" \
                     "(when locator is created it will also be parented to SCS Root, if currently active)."

    # create function for retrieving items so custom icons can be used
    def new_object_type_items(self, context):
        return [
            (
                'Root Object', "Root Object", "Creates SCS Root Object add parents any selected objects to it.",
                _get_icon(_ICONS_consts.Types.scs_root), 0
            ),
            (
                'Prefab Locator', "Prefab Locator", "Creates prefab locator + creates parent to SCS Root if currently active.",
                _get_icon(_ICONS_consts.Types.loc_prefab), 1
            ),
            (
                'Model Locator', "Model Locator", "Creates model locator + creates parent to SCS Root if currently active.",
                _get_icon(_ICONS_consts.Types.loc_model), 2
            ),
            (
                'Collision Locator', "Collision Locator", "Creates collision locator + creates parent to SCS Root if currently active.",
                _get_icon(_ICONS_consts.Types.loc_collider), 3
            ),
        ]

    new_object_type = bpy.props.EnumProperty(
        items=new_object_type_items
    )

    prefab_type = bpy.props.EnumProperty(
        name="Prefab Locator Type",
        description="Defines type of new prefab locator.",
        items=_ObjectSCSTools.locator_prefab_type_items
    )

    collider_type = bpy.props.EnumProperty(
        name="Collision Locator Type",
        description="Defines type of new collision locator.",
        items=_ObjectSCSTools.locator_collider_type_items
    )

    def draw(self, context):
        col = self.layout.column()

        # draw invoke props dialog depending on which type of locator user selected
        if self.new_object_type == "Prefab Locator":

            col.label(text="Prefab Locator Type:")
            col.prop(self, "prefab_type", text="")

        elif self.new_object_type == "Collision Locator":

            col.label(text="Collision Locator Type:")
            col.prop(self, "collider_type", text="")

        return

    def execute(self, context):
        lprint("D " + self.bl_label + "...")

        # save active object for later parenting of locator
        active_obj = context.active_object

        if self.new_object_type == "Root Object":

            bpy.ops.object.create_scs_root_object()

        else:

            if self.new_object_type == "Prefab Locator":
                new_loc = _object_utils.create_locator_empty("pl", context.scene.cursor_location, data_type="Prefab", blend_coords=True)
                new_loc.scs_props.locator_prefab_type = self.prefab_type
            elif self.new_object_type == "Model Locator":
                new_loc = _object_utils.create_locator_empty("ml", context.scene.cursor_location, data_type="Model", blend_coords=True)
            else:
                new_loc = _object_utils.create_locator_empty("cl", context.scene.cursor_location, data_type="Collision", blend_coords=True)
                new_loc.scs_props.locator_collider_type = self.collider_type

            # if previous active object was SCS root then automatically parent new locator to it
            if active_obj and _object_utils.get_scs_root(active_obj) == active_obj:

                # 1. deselect all
                bpy.ops.object.select_all(action='DESELECT')

                # 2. prepare selection for parenting: select new locator, scs root and set scs root as active object
                new_loc.select = True
                active_obj.select = True
                context.scene.objects.active = active_obj

                # 3. execute parenting (selected -> active)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

                # 4. switch active to new locator so user can continue working on it
                context.scene.objects.active = new_loc

        return {'FINISHED'}

    def invoke(self, context, event):

        # get extra input from user to decide which type of prefab or collision locator should be created
        if self.new_object_type in ("Prefab Locator", "Collision Locator"):
            return context.window_manager.invoke_props_dialog(self, width=150)

        return self.execute(context)


class BlankOperator(bpy.types.Operator):
    """Blank Operator."""
    bl_label = "Blank Operator"
    bl_idname = "object.blank_operator"
    bl_description = "Blank operator"

    def execute(self, context):
        print('Blank Operator...')
        return {'FINISHED'}
