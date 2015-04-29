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
from bpy.props import BoolProperty, StringProperty, IntProperty
from io_scs_tools.consts import Look as _LOOK_consts
from io_scs_tools.consts import Part as _PART_consts
from io_scs_tools.consts import Variant as _VARIANT_consts
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.internals import looks as _looks
from io_scs_tools.internals.connections.wrappers import group as _connection_group_wrapper
from io_scs_tools.operators.bases.selection import Selection as _BaseSelectionOperator
from io_scs_tools.operators.bases.view import View as _BaseViewOperator
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
                    elif not self.select_type in (self.SHIFT_SELECT, self.CTRL_SELECT):
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
                    elif not self.select_type in (self.SHIFT_SELECT, self.CTRL_SELECT):
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
                if has_shadow:

                    # set actual hide state if it's not set yet
                    if actual_hide_state is None:

                        actual_hide_state = not obj.hide

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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
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
                has_shadow, has_glass, is_other = _material_utils.get_material_info(obj)
                if has_glass:
                    obj.draw_type = 'TEXTURED'
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

                def execute(self, context):
                    # TODO: finish actually assigning of terrain points
                    lprint('D Assign Terrain Points...')
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

                    if not obj0.type == "EMPTY" or not obj0.scs_props.locator_prefab_type in ("Navigation Point", "Map Point", "Trigger Point"):
                        self.report({'ERROR'}, "Selected objects are not correct prefab locators or they are not the same type.")
                        return {'FINISHED'}

                    if _connection_group_wrapper.create_connection(obj0, obj1):
                        _view3d_utils.tag_redraw_all_view3d()
                    else:
                        self.report({'ERROR'},
                                    """Failed.
Connection already exists or
current locators types can not be connected or
one of locators doesn't have any empty slot!""")

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
        bl_label = "Add New SCS Root Object"

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
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Add SCS Animation to actual SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)

            # ADD NEW VARIANT
            _animation_utils.add_animation_to_root(scs_root_object)

            return {'FINISHED'}

    class RemoveSCSAnimationOperator(bpy.types.Operator):
        """Remove SCS Animation to actual SCS Game Object."""
        bl_label = "Remove SCS Animation"
        bl_idname = "object.remove_scs_animation"
        bl_description = "Remove SCS Animation to actual SCS Game Object"

        @classmethod
        def poll(cls, context):
            if _object_utils.get_scs_root(context.active_object):
                return True
            else:
                return False

        def execute(self, context):
            lprint('D Remove SCS Animation to actual SCS Game Object...')
            active_object = context.active_object
            scs_root_object = _object_utils.get_scs_root(active_object)
            active_scs_animation = scs_root_object.scs_props.active_scs_animation
            inventory = scs_root_object.scs_object_animation_inventory

            if active_scs_animation < len(inventory):
                active_scs_animation_name = inventory[active_scs_animation].name
                # print('len(inventory): %i - active_scs_animation: %i' % (len(inventory), active_scs_animation))
                if len(inventory) > active_scs_animation:
                    # children = _utils.get_children(scs_root_object)
                    # for child in children:
                    # if child.scs_props.scs_animation == active_scs_animation_name:
                    # child.scs_props.scs_animation = "DefaultPart"
                    lprint('I inventory[%i] - REMOVE item[%i] %r...', (len(inventory), active_scs_animation, inventory[active_scs_animation].name))
                    inventory.remove(active_scs_animation)
                else:
                    lprint("W No active 'SCS Animation' in list!")
            else:
                lprint("W No active 'SCS Animation' to remove!")
            return {'FINISHED'}

    '''
    class PerformEulerFilter(bpy.types.Operator):
        bl_label = "Discontinuity (Euler) Filter"
        bl_idname = "scene.euler_filter"
        bl_description = "Apply discontinuity (euler) filter on current object's Action"

        def execute(self, context):
            lprint('D Discontinuity (Euler) Filter...')

            def apply_euler_filter(curve):
                """."""
                XFLIPS = []  # A list of points on the RotX curve that are flipped
                ZFLIPS = []  # A list of points on the RotZ curve that are flipped

                # Get all relevant data for this curve
                cTyp = curve.name  # Name of the current curve
                keyframe_points = curve.keyframe_points  # The bezier points on the curve
                newpoints = []  # All the new points
                prev = 0  # The previous point on the curve
                pDif = 0  # The previous "difference" between keys
                fOffset = 0.0  # The current offset of the curve
                invert = 0  # Whether or not the curve needs inversion
                invertMethod = 0  # The type of inversion we need
                iOffset = 0.0  # The value of inversion offset
                cOffset = 0.0  # The offset to actually apply to a curve

                for keyframe_point in keyframe_points:
                    pnt = keyframe_point.co  # Current point
                    cDif = 0

                    # Only if we know a previous point can we do anything
                    if not prev:
                        newpoints.append([pnt[0], pnt[1]])
                    else:
                        cFr = pnt[0]  # Current place on the timeline
                        cCo = pnt[1]  # Current position
                        pCo = prev[1]  # Previous position
                        pSet = pCo + cOffset  # The previously set value
                        cDif = (-pCo) + cCo  # The difference between the previous and current position
                        iOffset = 0.0  # Inversion offset is set every time
                        cOffset = 0.0  # Offset for this frame for this point

                        # For the roty curve we need to do something special
                        # If all is well this is evaluated last and we have flips
                        # This curve isn't flipped, but inverted relative to -90 or +90 degrees
                        if cTyp == 'RotY' and cFr in XFLIPS and cFr in ZFLIPS:
                            # We need to either invert or stop inverting
                            if not invert:
                                invert = 1
                                # Depending on whether we are positive or negative we need a different inversion
                                if cCo < 0:
                                    invertMethod = 0
                                else:
                                    invertMethod = 1
                            else:
                                invert = 0
                                iOffset = 0.0
                                fOffset = 0.0

                        # lets see if RotX or RotZ flip
                        else:

                            # If the previous point is positive and we go down more than 90 degrees... it's a flip
                            if pCo > 0.0001 and (cDif < -9):
                                fOffset += 18

                                # The current value really should be bigger than the previous one
                                # So keep adding 180 degrees until it is
                                while pDif > 0.0001 and (cCo + fOffset) < pSet:
                                    fOffset += 18

                                if cTyp == 'RotX':
                                    XFLIPS.append(cFr)
                                else:
                                    ZFLIPS.append(cFr)

                            # If the previous point is negative and we go up more than 90 degrees it's a flip
                            elif pCo < -0.0001 and (cDif > 9):
                                fOffset -= 18

                                # The current value really should be smaller than the previous one
                                # So keep subtracting 180 degrees until it is
                                while pDif < -0.0001 and (cCo + fOffset) > pSet:
                                    fOffset -= 18

                                if cTyp == 'RotX':
                                    XFLIPS.append(cFr)
                                else:
                                    ZFLIPS.append(cFr)

                        # Now if we need to invert it's simple, just get the offset relative to -90 or +90 and do negative twice the distance to
                        that
                        # value
                        if invert:
                            # Lets get the offset
                            if not invertMethod:
                                cDif = 9.0 + cCo
                                iOffset = (-cDif) * 2
                            else:
                                cDif = -9.0 + cCo
                                iOffset = (-cDif) * 2

                            cOffset = iOffset

                            # If there's also an flipping offset, lets invert that as well and add it to the inversion offset
                            if fOffset:
                                cOffset += (-fOffset)

                        # if we're not inverting the current offset is just the "flipping offset"
                        else:
                            cOffset = fOffset

                        # No matter what happened, lets apply the offset to every point
                        newpoints.append([pnt[0], (pnt[1] + cOffset)])

                    # Set this point as the previous one for the next loop
                    prev = pnt
                    pDif = cDif

                # Apply the new points
                if len(newpoints):
                    for i, keyframe_point in enumerate(newpoints):
                        keyframe_points[i].pt = [p[0], p[1]]

            euler_curves = {}
            if context.active_object:
                if context.active_object.animation_data.action:
                    for fcurve in context.active_object.animation_data.action.fcurves:
                        if fcurve.data_path.endswith("rotation_euler"):
                            data_id = str(fcurve.array_index)
                            euler_curves[data_id] = fcurve
                            # print('data_path: %s' % fcurve.data_path)
                            # bpy.ops.graph.euler_filter()
                        if len(euler_curves) == 3:
                            fcurve_bone_name = fcurve.data_path.split('"', 2)[1]
                            print("Performing Euler filter on %r bone's F-Curve..." % fcurve_bone_name)
                            for euler_curve in euler_curves:
                                print('  euler_curve %r - %s' % (euler_curve, euler_curves[euler_curve]))
                                apply_euler_filter(euler_curves[euler_curve])
                            euler_curves = {}
            return {'FINISHED'}
    '''


class BlankOperator(bpy.types.Operator):
    """Blank Operator."""
    bl_label = "Blank Operator"
    bl_idname = "object.blank_operator"
    bl_description = "Blank operator"

    def execute(self, context):
        print('Blank Operator...')
        return {'FINISHED'}