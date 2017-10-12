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


from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec
from io_scs_tools.internals.shaders.eut2.dif_spec_fade_dif_spec import detail_nmap
from io_scs_tools.internals.shaders.eut2.dif_spec_fade_dif_spec import detail_setup_ng


class DifSpecFadeDifSpec(DifSpec):
    UV_SCALE_NODE = "UVScale"
    DETAIL_UV_SCALING_NODE = "DetailUVScaling"
    DETAIL_TEX_NODE = "DetailTex"
    BASE_DETAIL_MIX_NODE = "BaseDetailMix"
    BASE_DETAIL_MIX_A_NODE = "BaseDetailMixAlpha"
    DETAIL_SETUP_GNODE = "DetailSetupGroup"

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

        # init parent
        DifSpec.init(node_tree, disable_remap_alpha=True)

        geom_n = node_tree.nodes[DifSpec.GEOM_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        opacity_n = node_tree.nodes[DifSpec.OPACITY_NODE]
        spec_mult_n = node_tree.nodes[DifSpec.SPEC_MULT_NODE]
        vcol_mult_n = node_tree.nodes[DifSpec.VCOLOR_MULT_NODE]

        # move existing
        for node in node_tree.nodes:
            if node.location.x > start_pos_x + pos_x_shift:
                node.location.x += pos_x_shift

        # node creation
        uv_scale_n = node_tree.nodes.new("ShaderNodeValue")
        uv_scale_n.name = uv_scale_n.label = DifSpecFadeDifSpec.UV_SCALE_NODE
        uv_scale_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)

        detail_uv_scaling_n = node_tree.nodes.new("ShaderNodeMixRGB")
        detail_uv_scaling_n.name = detail_uv_scaling_n.label = DifSpecFadeDifSpec.DETAIL_UV_SCALING_NODE
        detail_uv_scaling_n.location = (start_pos_x, start_pos_y + 1200)
        detail_uv_scaling_n.blend_type = "MULTIPLY"
        detail_uv_scaling_n.inputs['Fac'].default_value = 1.0

        detail_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        detail_tex_n.name = detail_tex_n.label = DifSpecFadeDifSpec.DETAIL_TEX_NODE
        detail_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        detail_setup_group_n = node_tree.nodes.new("ShaderNodeGroup")
        detail_setup_group_n.name = detail_setup_group_n.label = DifSpecFadeDifSpec.DETAIL_SETUP_GNODE
        detail_setup_group_n.location = (start_pos_x + pos_x_shift, start_pos_y + 900)
        detail_setup_group_n.node_tree = detail_setup_ng.get_node_group()

        base_detail_mix_a_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_detail_mix_a_n.name = base_detail_mix_a_n.label = DifSpecFadeDifSpec.BASE_DETAIL_MIX_A_NODE
        base_detail_mix_a_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1700)
        base_detail_mix_a_n.blend_type = "MIX"

        base_detail_mix_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_detail_mix_n.name = base_detail_mix_n.label = DifSpecFadeDifSpec.BASE_DETAIL_MIX_NODE
        base_detail_mix_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1400)
        base_detail_mix_n.blend_type = "MIX"

        # links creation
        node_tree.links.new(detail_uv_scaling_n.inputs['Color1'], geom_n.outputs['UV'])
        node_tree.links.new(detail_uv_scaling_n.inputs['Color2'], uv_scale_n.outputs[0])

        # geom pass
        node_tree.links.new(detail_tex_n.inputs['Vector'], detail_uv_scaling_n.outputs['Color'])

        # pass 1
        node_tree.links.new(base_detail_mix_a_n.inputs['Fac'], detail_setup_group_n.outputs['Blend Factor'])
        node_tree.links.new(base_detail_mix_a_n.inputs['Color1'], base_tex_n.outputs['Value'])
        node_tree.links.new(base_detail_mix_a_n.inputs['Color2'], detail_tex_n.outputs['Value'])

        node_tree.links.new(base_detail_mix_n.inputs['Fac'], detail_setup_group_n.outputs['Blend Factor'])
        node_tree.links.new(base_detail_mix_n.inputs['Color1'], base_tex_n.outputs['Color'])
        node_tree.links.new(base_detail_mix_n.inputs['Color2'], detail_tex_n.outputs['Color'])

        # pass 2
        node_tree.links.new(spec_mult_n.inputs['Color2'], base_detail_mix_a_n.outputs['Color'])

        # pass 3
        node_tree.links.new(vcol_mult_n.inputs['Color2'], base_detail_mix_n.outputs['Color'])

    @staticmethod
    def set_detail_texture(node_tree, texture):
        """Set detail texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to detail texture node
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecFadeDifSpec.DETAIL_TEX_NODE].texture = texture

    @staticmethod
    def set_detail_uv(node_tree, uv_layer):
        """Set UV layer to detail texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for detail texture
        :type uv_layer: str
        """

        DifSpec.set_base_uv(node_tree, uv_layer)

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

            out_mat_n = node_tree.nodes[DifSpec.OUT_MAT_NODE]
            uv_scale_n = node_tree.nodes[DifSpecFadeDifSpec.UV_SCALE_NODE]
            detail_setup_group_n = node_tree.nodes[DifSpecFadeDifSpec.DETAIL_SETUP_GNODE]

            location = (out_mat_n.location.x - 185, min_y - 400)

            detail_nmap.init(node_tree, location,
                             uv_scale_n.outputs[0],
                             detail_setup_group_n.outputs['Detail Strength'],
                             out_mat_n.inputs['Normal'])
        else:
            detail_nmap.delete(node_tree)

    @staticmethod
    def set_nmap_texture(node_tree, texture):
        """Set normal map texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to nmap texture node
        :type texture: bpy.types.Texture
        """

        detail_nmap.set_texture(node_tree, texture)

    @staticmethod
    def set_nmap_uv(node_tree, uv_layer):
        """Set UV layer to normal map texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for nmap texture
        :type uv_layer: str
        """

        detail_nmap.set_uv(node_tree, uv_layer)

    @staticmethod
    def set_nmap_detail_texture(node_tree, texture):
        """Set detail normal map texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assigned to detail nmap texture node
        :type texture: bpy.types.Texture
        """

        detail_nmap.set_detail_texture(node_tree, texture)

    @staticmethod
    def set_nmap_detail_uv(node_tree, uv_layer):
        """Set UV layer to detail normal map texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for detail nmap texture
        :type uv_layer: str
        """

        detail_nmap.set_detail_uv(node_tree, uv_layer)

    @staticmethod
    def set_aux5(node_tree, aux_property):
        """Set zero texture generation scale.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param aux_property: secondary specular color represented with property group
        :type aux_property: bpy.types.IDPropertyGroup
        """

        detail_setup_group_n = node_tree.nodes[DifSpecFadeDifSpec.DETAIL_SETUP_GNODE]
        uv_scale_n = node_tree.nodes[DifSpecFadeDifSpec.UV_SCALE_NODE]

        detail_setup_group_n.inputs["Fade From"].default_value = aux_property[0]['value']
        detail_setup_group_n.inputs["Fade Range"].default_value = aux_property[1]['value']
        detail_setup_group_n.inputs["Blend Bias"].default_value = aux_property[2]['value']
        uv_scale_n.outputs[0].default_value = aux_property[3]['value']
