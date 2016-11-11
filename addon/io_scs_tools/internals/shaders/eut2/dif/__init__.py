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


from mathutils import Color
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.std_node_groups import compose_lighting
from io_scs_tools.internals.shaders.eut2.std_node_groups import vcolor_input
from io_scs_tools.internals.shaders.flavors import alpha_test
from io_scs_tools.internals.shaders.flavors import blend_over
from io_scs_tools.internals.shaders.flavors import blend_add
from io_scs_tools.internals.shaders.flavors import nmap
from io_scs_tools.internals.shaders.flavors import paint
from io_scs_tools.internals.shaders.flavors import tg0
from io_scs_tools.utils import convert as _convert_utils


class Dif:
    DIFF_COL_NODE = "DiffuseColor"
    SPEC_COL_NODE = "SpecularColor"
    GEOM_NODE = "Geometry"
    VCOL_GROUP_NODE = "VColorGroup"
    OPACITY_NODE = "OpacityMultiplier"
    BASE_TEX_NODE = "BaseTex"
    DIFF_MULT_NODE = "DiffMultiplier"
    VCOLOR_MULT_NODE = "VertexColorMultiplier"
    VCOLOR_SCALE_NODE = "VertexColorScale"
    OUT_MAT_NODE = "InputMaterial"
    COMPOSE_LIGHTING_NODE = "ComposeLighting"
    OUTPUT_NODE = "Output"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        # node creation
        vcol_group_n = node_tree.nodes.new("ShaderNodeGroup")
        vcol_group_n.name = Dif.VCOL_GROUP_NODE
        vcol_group_n.label = Dif.VCOL_GROUP_NODE
        vcol_group_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1650)
        vcol_group_n.node_tree = vcolor_input.get_node_group()

        geometry_n = node_tree.nodes.new("ShaderNodeGeometry")
        geometry_n.name = Dif.GEOM_NODE
        geometry_n.label = Dif.GEOM_NODE
        geometry_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1500)
        geometry_n.uv_layer = _MESH_consts.none_uv

        diff_col_n = node_tree.nodes.new("ShaderNodeRGB")
        diff_col_n.name = Dif.DIFF_COL_NODE
        diff_col_n.label = Dif.DIFF_COL_NODE
        diff_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1700)

        spec_col_n = node_tree.nodes.new("ShaderNodeRGB")
        spec_col_n.name = Dif.SPEC_COL_NODE
        spec_col_n.label = Dif.SPEC_COL_NODE
        spec_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1900)

        vcol_scale_n = node_tree.nodes.new("ShaderNodeMixRGB")
        vcol_scale_n.name = Dif.VCOLOR_SCALE_NODE
        vcol_scale_n.label = Dif.VCOLOR_SCALE_NODE
        vcol_scale_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1550)
        vcol_scale_n.blend_type = "MULTIPLY"
        vcol_scale_n.inputs['Fac'].default_value = 1
        vcol_scale_n.inputs['Color2'].default_value = (2,) * 4

        opacity_n = node_tree.nodes.new("ShaderNodeMath")
        opacity_n.name = Dif.OPACITY_NODE
        opacity_n.label = Dif.OPACITY_NODE
        opacity_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        opacity_n.operation = "MULTIPLY"

        base_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        base_tex_n.name = Dif.BASE_TEX_NODE
        base_tex_n.label = Dif.BASE_TEX_NODE
        base_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1500)

        vcol_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        vcol_mult_n.name = Dif.VCOLOR_MULT_NODE
        vcol_mult_n.label = Dif.VCOLOR_MULT_NODE
        vcol_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1500)
        vcol_mult_n.blend_type = "MULTIPLY"
        vcol_mult_n.inputs['Fac'].default_value = 1

        diff_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        diff_mult_n.name = Dif.DIFF_MULT_NODE
        diff_mult_n.label = Dif.DIFF_MULT_NODE
        diff_mult_n.location = (start_pos_x + pos_x_shift * 5, start_pos_y + 1650)
        diff_mult_n.blend_type = "MULTIPLY"
        diff_mult_n.inputs['Fac'].default_value = 1
        diff_mult_n.inputs['Color2'].default_value = (0, 0, 0, 1)

        out_mat_n = node_tree.nodes.new("ShaderNodeExtendedMaterial")
        out_mat_n.name = Dif.OUT_MAT_NODE
        out_mat_n.label = Dif.OUT_MAT_NODE
        if "Refl" in out_mat_n:
            out_mat_n.inputs['Refl'].default_value = 1.0
        elif "Reflectivity" in out_mat_n:
            out_mat_n.inputs['Reflectivity'].default_value = 1.0
        out_mat_n.location = (start_pos_x + pos_x_shift * 7, start_pos_y + 1800)

        compose_lighting_n = node_tree.nodes.new("ShaderNodeGroup")
        compose_lighting_n.name = Dif.COMPOSE_LIGHTING_NODE
        compose_lighting_n.label = Dif.COMPOSE_LIGHTING_NODE
        compose_lighting_n.location = (start_pos_x + pos_x_shift * 8, start_pos_y + 2000)
        compose_lighting_n.node_tree = compose_lighting.get_node_group()

        output_n = node_tree.nodes.new("ShaderNodeOutput")
        output_n.name = Dif.OUTPUT_NODE
        output_n.label = Dif.OUTPUT_NODE
        output_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 1800)

        # links creation
        node_tree.links.new(base_tex_n.inputs['Vector'], geometry_n.outputs['UV'])
        node_tree.links.new(vcol_scale_n.inputs['Color1'], vcol_group_n.outputs['Vertex Color'])

        node_tree.links.new(vcol_mult_n.inputs['Color1'], vcol_scale_n.outputs['Color'])
        node_tree.links.new(vcol_mult_n.inputs['Color2'], base_tex_n.outputs['Color'])

        node_tree.links.new(diff_mult_n.inputs['Color1'], diff_col_n.outputs['Color'])
        node_tree.links.new(diff_mult_n.inputs['Color2'], vcol_mult_n.outputs['Color'])
        node_tree.links.new(opacity_n.inputs[0], base_tex_n.outputs["Value"])
        node_tree.links.new(opacity_n.inputs[1], vcol_group_n.outputs["Vertex Color Alpha"])

        node_tree.links.new(out_mat_n.inputs['Color'], diff_mult_n.outputs['Color'])
        node_tree.links.new(out_mat_n.inputs['Spec'], spec_col_n.outputs['Color'])

        node_tree.links.new(compose_lighting_n.inputs['Diffuse Color'], diff_mult_n.outputs['Color'])
        node_tree.links.new(compose_lighting_n.inputs['Material Color'], out_mat_n.outputs['Color'])

        node_tree.links.new(output_n.inputs['Color'], compose_lighting_n.outputs['Composed Color'])
        node_tree.links.new(output_n.inputs['Alpha'], out_mat_n.outputs['Alpha'])

    @staticmethod
    def set_material(node_tree, material):
        """Set output material for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param material: blender material for used in this tree node as output
        :type material: bpy.types.Material
        """

        node_tree.nodes[Dif.OUT_MAT_NODE].material = material

        # make sure to reset to lambert always as flat flavor might use fresnel diffuse shader
        material.diffuse_shader = "LAMBERT"

    @staticmethod
    def set_add_ambient(node_tree, factor):
        """Set ambient factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: add ambient factor
        :type factor: float
        """

        node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE].inputs["AddAmbient"].default_value = factor

    @staticmethod
    def set_diffuse(node_tree, color):
        """Set diffuse color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: diffuse color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Dif.DIFF_COL_NODE].outputs['Color'].default_value = color
        # fix intensity each time if user might changed it by hand directly on material
        node_tree.nodes[Dif.OUT_MAT_NODE].material.diffuse_intensity = 0.7

    @staticmethod
    def set_specular(node_tree, color):
        """Set specular color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: specular color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[Dif.SPEC_COL_NODE].outputs['Color'].default_value = color
        # fix intensity each time if user might changed it by hand directly on material
        node_tree.nodes[Dif.OUT_MAT_NODE].material.specular_intensity = 1.0

    @staticmethod
    def set_shininess(node_tree, factor):
        """Set shininess factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param factor: shininess factor
        :type factor: float
        """

        node_tree.nodes[Dif.OUT_MAT_NODE].material.specular_hardness = factor

    @staticmethod
    def set_reflection(node_tree, value):
        """Set reflection factor to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: reflection factor
        :type value: float
        """

        pass  # NOTE: reflection attribute doesn't change anything in rendered material, so pass it

    @staticmethod
    def set_shadow_bias(node_tree, value):
        """Set shadow bias attirbute for this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param value: blender material for used in this tree node as output
        :type value: float
        """

        pass  # NOTE: shadow bias won't be visualized as game uses it's own implementation

    @staticmethod
    def set_base_texture(node_tree, texture):
        """Set base texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to base texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[Dif.BASE_TEX_NODE].texture = texture

    @staticmethod
    def set_base_uv(node_tree, uv_layer):
        """Set UV layer to base texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for base texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[Dif.GEOM_NODE].uv_layer = uv_layer

    @staticmethod
    def set_alpha_test_flavor(node_tree, switch_on):
        """Set alpha test flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if alpha test should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not blend_over.is_set(node_tree):
            out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
            in_node = node_tree.nodes[Dif.OPACITY_NODE]
            location = (out_node.location.x - 185 * 2, out_node.location.y - 500)

            alpha_test.init(node_tree, location, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            alpha_test.delete(node_tree)

    @staticmethod
    def set_blend_over_flavor(node_tree, switch_on):
        """Set blend over flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend over should be switched on or off
        :type switch_on: bool
        """

        # remove alpha test flavor if it was set already. Because these two can not coexist
        if alpha_test.is_set(node_tree):
            Dif.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
        in_node = node_tree.nodes[Dif.OPACITY_NODE]

        if switch_on:
            blend_over.init(node_tree, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            blend_over.delete(node_tree)

    @staticmethod
    def set_blend_add_flavor(node_tree, switch_on):
        """Set blend add flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if blend add should be switched on or off
        :type switch_on: bool
        """

        # remove alpha test flavor if it was set already. Because these two can not coexist
        if alpha_test.is_set(node_tree):
            Dif.set_alpha_test_flavor(node_tree, False)

        out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
        in_node = node_tree.nodes[Dif.OPACITY_NODE]

        if switch_on:
            blend_add.init(node_tree, in_node.outputs['Value'], out_node.inputs['Alpha'])
        else:
            blend_add.delete(node_tree)

    @staticmethod
    def set_nmap_flavor(node_tree, switch_on):
        """Set normal map flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if normal map should be switched on or off
        :type switch_on: bool
        """

        if switch_on:

            # find minimal y position for input nodes and position flavor beneath it
            min_y = None
            for node in node_tree.nodes:
                if node.location.x <= 185 and (min_y is None or min_y > node.location.y):
                    min_y = node.location.y

            out_node = node_tree.nodes[Dif.OUT_MAT_NODE]
            location = (out_node.location.x - 185, min_y - 400)

            nmap.init(node_tree, location, out_node.inputs['Normal'])
        else:
            nmap.delete(node_tree)

    @staticmethod
    def set_nmap_texture(node_tree, texture):
        """Set normal map texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to nmap texture node
        :type texture: bpy.types.Texture
        """

        nmap.set_texture(node_tree, texture)

    @staticmethod
    def set_nmap_uv(node_tree, uv_layer):
        """Set UV layer to normal map texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for nmap texture
        :type uv_layer: str
        """

        nmap.set_uv(node_tree, uv_layer)

    @staticmethod
    def set_tg0_flavor(node_tree, switch_on):
        """Set zero texture generation flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        if switch_on and not tg0.is_set(node_tree):

            out_node = node_tree.nodes[Dif.GEOM_NODE]
            in_node = node_tree.nodes[Dif.BASE_TEX_NODE]

            out_node.location.x -= 185
            location = (out_node.location.x + 185, out_node.location.y)

            tg0.init(node_tree, location, out_node.outputs["Global"], in_node.inputs["Vector"])

        elif not switch_on:

            tg0.delete(node_tree)

    @staticmethod
    def set_aux0(node_tree, aux_property):
        """Set zero texture generation scale.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: zero texture generation scale represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        if tg0.is_set(node_tree):

            tg0.set_scale(node_tree, aux_property[0]['value'], aux_property[1]['value'])

    @staticmethod
    def set_flat_flavor(node_tree, switch_on):
        """Set flat shading flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        _FLAT_FAC_MULT_NODE = "FlatFlavorMult"

        out_mat_n = node_tree.nodes[Dif.OUT_MAT_NODE]
        compose_lighting_n = node_tree.nodes[Dif.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[Dif.OUTPUT_NODE]
        diff_mult_n = node_tree.nodes[Dif.DIFF_MULT_NODE]

        if switch_on:

            out_mat_n.use_specular = False
            out_mat_n.material.diffuse_shader = "FRESNEL"
            out_mat_n.material.diffuse_fresnel = 0

            out_mat_n.location.x += 185
            output_n.location.x += 185

            flat_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
            flat_mult_n.name = flat_mult_n.label = _FLAT_FAC_MULT_NODE
            flat_mult_n.location = (out_mat_n.location.x - 185 * 2, diff_mult_n.location.y)
            flat_mult_n.blend_type = "MULTIPLY"
            flat_mult_n.inputs['Fac'].default_value = 1
            flat_mult_n.inputs['Color2'].default_value = (0.4,) * 3 + (1,)  # factor is 0.4

            node_tree.links.new(flat_mult_n.inputs['Color1'], diff_mult_n.outputs['Color'])
            node_tree.links.new(out_mat_n.inputs['Color'], flat_mult_n.outputs['Color'])
            node_tree.links.new(compose_lighting_n.inputs['Material Color'], flat_mult_n.outputs['Color'])

        else:

            out_mat_n.use_specular = True
            out_mat_n.material.diffuse_shader = "LAMBERT"

            out_mat_n.location.x -= 185
            output_n.location.x -= 185

            if _FLAT_FAC_MULT_NODE in node_tree.nodes:
                node_tree.nodes.remove(node_tree.nodes[_FLAT_FAC_MULT_NODE])

            node_tree.links.new(out_mat_n.inputs['Color'], diff_mult_n.outputs['Color'])
            node_tree.links.new(compose_lighting_n.inputs['Material Color'], diff_mult_n.outputs['Color'])

    @staticmethod
    def set_paint_flavor(node_tree, switch_on):
        """Set paint flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """

        diff_col_n = node_tree.nodes[Dif.DIFF_COL_NODE]
        diff_mult_n = node_tree.nodes[Dif.DIFF_MULT_NODE]

        if switch_on:

            location = (diff_mult_n.location.x - 185, diff_mult_n.location.y + 50)
            paint.init(node_tree, location, diff_col_n.outputs["Color"], diff_mult_n.inputs["Color1"])

        else:
            paint.delete(node_tree)
