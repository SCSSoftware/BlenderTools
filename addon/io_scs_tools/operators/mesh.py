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

# Copyright (C) 2015: SCS Software

import bmesh
import bpy

from bpy.props import StringProperty, FloatProperty
from io_scs_tools.consts import LampTools as _LT_consts
from io_scs_tools.consts import VertexColorTools as _VCT_consts


class LampTool:
    """
    Wrapper class for better navigation in file
    """

    class SetLampMaskUV(bpy.types.Operator):
        bl_label = "Set UV to lamp mask"
        bl_idname = "mesh.scs_set_lampmask_uv"
        bl_description = "Sets offset for lamp mask UV according to given vehicle side or auxiliary color."

        vehicle_side = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        aux_color = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        traffic_light_color = StringProperty(
            description="",
            default="",
            options={'HIDDEN'},
        )

        @classmethod
        def poll(cls, context):
            return context.object is not None and context.object.mode == "EDIT"

        def execute(self, context):
            mesh = context.object.data
            bm = bmesh.from_edit_mesh(mesh)  # use bmesh module because we are working in edit mode

            # decide which offset to use depending on vehicle side, auxiliary color and traffic light type
            offset_y = 0
            if _LT_consts.VehicleSides.FrontLeft.name == self.vehicle_side:  # vehicle lights checking
                offset_x = 0
            elif _LT_consts.VehicleSides.FrontRight.name == self.vehicle_side:
                offset_x = 1
            elif _LT_consts.VehicleSides.RearLeft.name == self.vehicle_side:
                offset_x = 2
            elif _LT_consts.VehicleSides.RearRight.name == self.vehicle_side:
                offset_x = 3
            elif _LT_consts.VehicleSides.Middle.name == self.vehicle_side:
                offset_x = 4
            elif _LT_consts.AuxiliaryLampColors.White.name == self.aux_color:  # auxiliary lights checking
                offset_x = 0
            elif _LT_consts.AuxiliaryLampColors.Orange.name == self.aux_color:
                offset_x = 1
            elif _LT_consts.TrafficLightTypes.Red.name == self.traffic_light_color:  # traffic lights checking
                offset_x = 1
                offset_y = 1
            elif _LT_consts.TrafficLightTypes.Yellow.name == self.traffic_light_color:
                offset_x = 2
                offset_y = 2
            elif _LT_consts.TrafficLightTypes.Green.name == self.traffic_light_color:
                offset_x = 3
                offset_y = 3
            else:
                self.report({"ERROR"}, "Unsupported vehicle side or auxiliary color or traffic light color!")
                return {"FINISHED"}

            polys_changed = 0
            for face in bm.faces:

                if face.select and len(context.object.material_slots) > 0:
                    material = context.object.material_slots[face.material_index].material
                    if material and len(material.scs_props.shader_texture_mask_uv) > 0:

                        # use first mapping from mask texture
                        uv_lay_name = material.scs_props.shader_texture_mask_uv[0].value

                        # if mask uv layer specified by current material doesn't exists
                        # move to next face
                        if uv_lay_name not in mesh.uv_layers:
                            self.report({"ERROR"}, "UV layer: '%s' not found in this object!" % uv_lay_name)
                            break

                        uv_lay = bm.loops.layers.uv[uv_lay_name]
                        for loop in face.loops:

                            uv = loop[uv_lay].uv
                            uv = (offset_x + (uv[0] - int(uv[0])), offset_y + (uv[1] - int(uv[1])))
                            loop[uv_lay].uv = uv

                        polys_changed += 1

            # write data back if modified
            if polys_changed > 0:
                bmesh.update_edit_mesh(mesh)

            if self.vehicle_side != "":
                changed_type = self.vehicle_side
            elif self.aux_color != "":
                changed_type = self.aux_color
            else:
                changed_type = "INVALID"

            self.report({"INFO"}, "Lamp mask UV tool set %i faces to '%s'" % (polys_changed, changed_type))
            return {'FINISHED'}


class VertexColorWrapTool:
    """
    Wrapper class for better navigation in file
    """

    class WrapVertexColors(bpy.types.Operator):
        bl_label = "Wrap"
        bl_idname = "mesh.scs_wrap_vcol"
        bl_description = "Wraps vertex colors to given interval."
        bl_options = {'REGISTER', 'UNDO'}

        wrap_type = StringProperty(
            options={'HIDDEN'},
        )
        min = FloatProperty(
            name="Min Value",
            description="New minimal possible value for vertex colors.",
            default=0.4,
            max=0.5,
            min=0.0,
        )
        max = FloatProperty(
            name="Max Value",
            description="New maximal possible value for vertex colors.",
            default=0.6,
            max=1.0,
            min=0.5
        )

        original_col = {}
        """Dictionary of original vertex colors which are used for calculation
        if operator interval is changed"""

        @classmethod
        def poll(cls, context):
            return context.object is not None and context.object.mode == "VERTEX_PAINT" and len(context.object.data.vertex_colors) > 0

        def __init__(self):
            self.original_col = {}

        def __del__(self):
            self.original_col.clear()

        def execute(self, context):

            mesh = context.object.data
            interval = self.max - self.min
            vcolor_layer = mesh.vertex_colors[mesh.vertex_colors.active_index]

            for poly in mesh.polygons:

                # calculate wrapped value for face it wrap type is all or face is selected
                if self.wrap_type == _VCT_consts.WrapType.All or (self.wrap_type == _VCT_consts.WrapType.Selected and poly.select):

                    for loop_i in poly.loop_indices:

                        # cache original vertex colors because of update on interval change
                        if loop_i not in self.original_col:
                            color = vcolor_layer.data[loop_i].color
                            self.original_col[loop_i] = (color[0], color[1], color[2])

                        vcolor_layer.data[loop_i].color = (
                            self.original_col[loop_i][0] * interval + self.min,
                            self.original_col[loop_i][1] * interval + self.min,
                            self.original_col[loop_i][2] * interval + self.min
                        )

            self.report({"INFO"}, "Vertex colors wrapped!")
            return {'FINISHED'}


class NormalMap:
    """
    Wrapper class for better navigation in file
    """

    class EnsureActiveUV(bpy.types.Operator):
        bl_label = "Ensure Active UV"
        bl_idname = "mesh.scs_ensure_active_uv"
        bl_description = "Sets Nmap texture mapping as active on all meshes using this material." \
                         "(Needed because Blender calculates tangents upon active UV)"

        mat_name = StringProperty(
            default="",
            options={'HIDDEN'},
        )

        uv_layer = StringProperty(
            default="",
            options={'HIDDEN'},
        )

        def execute(self, context):

            if self.mat_name != "" and self.uv_layer != "":

                changed_count = 0
                unchanged_count = 0
                recognized_count = 0
                for obj in bpy.data.objects:

                    if obj.type == "MESH" and obj.data:

                        for mat_slot in obj.material_slots:
                            if mat_slot.material and mat_slot.material.name == self.mat_name:

                                # find uv layer which is used for normal map and mark it as active
                                for i, uv_tex in enumerate(obj.data.uv_textures):
                                    if uv_tex.name == self.uv_layer:

                                        if obj.data.uv_textures.active_index != i:
                                            obj.data.uv_textures.active_index = i
                                            changed_count += 1
                                        else:
                                            unchanged_count += 1

                                        break

                                recognized_count += 1
                                break

                if recognized_count > 0:
                    if recognized_count == unchanged_count:
                        self.report({"INFO"}, "All meshes already have proper active UV.")
                    elif recognized_count == unchanged_count + changed_count:
                        self.report({"INFO"}, "Active UV changed on %i objects." % changed_count)
                    else:
                        self.report({"ERROR"}, "UV layers out of sync on some objects. Active UVs changed on %i from %i objects!" %
                                    (changed_count, recognized_count))
                else:
                    self.report({"INFO"}, "None object is using this material. No changes made.")

            return {'FINISHED'}
