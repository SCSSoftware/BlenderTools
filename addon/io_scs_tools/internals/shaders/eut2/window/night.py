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


from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv
from io_scs_tools.internals.shaders.eut2.std_node_groups import window_uv_offset


class WindowNight(DifSpecAddEnv):
    SEC_GEOM_NODE = "SecGeometry"
    LIGHTMAP_TEX_NODE = "LightmapTex"
    BASE_LIGHTMAP_MULT_NODE = "BaseLightmapMultiplier"
    BASE_ALPHA_MULT_NODE = "BaseAlphaMultiplier"
    OUT_ADD_SPEC_NODE = "OutAddSpecular"

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

        pos_x_shift = 185

        start_pos_x = 0
        start_pos_y = 0

        # init parent
        DifSpecAddEnv.init(node_tree)

        geom_n = node_tree.nodes[DifSpecAddEnv.GEOM_NODE]
        spec_col_n = node_tree.nodes[DifSpecAddEnv.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpecAddEnv.BASE_TEX_NODE]
        diff_mult_n = node_tree.nodes[DifSpecAddEnv.DIFF_MULT_NODE]
        out_mat_n = node_tree.nodes[DifSpecAddEnv.OUT_MAT_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecAddEnv.COMPOSE_LIGHTING_NODE]
        output_n = node_tree.nodes[DifSpecAddEnv.OUTPUT_NODE]

        # move existing
        output_n.location.x += pos_x_shift
        out_mat_n.location.y -= 150

        # remove existing
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.SPEC_MULT_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOL_GROUP_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOLOR_SCALE_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.VCOLOR_MULT_NODE])
        node_tree.nodes.remove(node_tree.nodes[DifSpecAddEnv.OPACITY_NODE])

        for link in node_tree.links:
            if link.from_node == diff_mult_n and link.to_node == out_mat_n:
                node_tree.links.remove(link)
                break

        # create nodes
        uv_recalc_gn = node_tree.nodes.new("ShaderNodeGroup")
        uv_recalc_gn.name = window_uv_offset.WINDOW_UV_OFFSET_G
        uv_recalc_gn.label = window_uv_offset.WINDOW_UV_OFFSET_G
        uv_recalc_gn.location = (start_pos_x, start_pos_y + 1500)
        uv_recalc_gn.node_tree = window_uv_offset.get_node_group()

        sec_geom_n = node_tree.nodes.new("ShaderNodeGeometry")
        sec_geom_n.name = sec_geom_n.label = WindowNight.SEC_GEOM_NODE
        sec_geom_n.location = (start_pos_x - pos_x_shift, start_pos_y + 1200)
        sec_geom_n.uv_layer = _MESH_consts.none_uv

        lightmap_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        lightmap_tex_n.name = lightmap_tex_n.label = WindowNight.LIGHTMAP_TEX_NODE
        lightmap_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 1200)

        base_lightmap_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_lightmap_mult_n.name = base_lightmap_mult_n.label = WindowNight.BASE_LIGHTMAP_MULT_NODE
        base_lightmap_mult_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 1300)
        base_lightmap_mult_n.blend_type = "MULTIPLY"
        base_lightmap_mult_n.inputs["Fac"].default_value = 1.0

        base_alpha_mult_n = node_tree.nodes.new("ShaderNodeMixRGB")
        base_alpha_mult_n.name = base_alpha_mult_n.label = WindowNight.BASE_ALPHA_MULT_NODE
        base_alpha_mult_n.location = (start_pos_x + pos_x_shift * 4, start_pos_y + 1500)
        base_alpha_mult_n.blend_type = "MULTIPLY"
        base_alpha_mult_n.inputs["Fac"].default_value = 1.0

        out_add_spec_n = node_tree.nodes.new("ShaderNodeMixRGB")
        out_add_spec_n.name = out_add_spec_n.label = WindowNight.BASE_ALPHA_MULT_NODE
        out_add_spec_n.location = (start_pos_x + pos_x_shift * 9, start_pos_y + 1900)
        out_add_spec_n.blend_type = "ADD"
        out_add_spec_n.inputs["Fac"].default_value = 1.0

        # create links
        node_tree.links.new(uv_recalc_gn.inputs["UV"], geom_n.outputs["UV"])
        node_tree.links.new(uv_recalc_gn.inputs["Normal"], geom_n.outputs["Normal"])

        node_tree.links.new(base_tex_n.inputs["Vector"], uv_recalc_gn.outputs["UV Final"])
        node_tree.links.new(lightmap_tex_n.inputs["Vector"], sec_geom_n.outputs["UV"])

        # pass 1
        node_tree.links.new(base_lightmap_mult_n.inputs["Color1"], base_tex_n.outputs["Color"])
        node_tree.links.new(base_lightmap_mult_n.inputs["Color2"], lightmap_tex_n.outputs["Color"])

        # pass 2
        node_tree.links.new(base_alpha_mult_n.inputs["Color1"], base_tex_n.outputs["Value"])
        node_tree.links.new(base_alpha_mult_n.inputs["Color2"], base_lightmap_mult_n.outputs["Color"])

        # pass 3
        node_tree.links.new(diff_mult_n.inputs["Color2"], base_alpha_mult_n.outputs["Color"])

        # output material
        node_tree.links.new(out_mat_n.inputs["Spec"], spec_col_n.outputs["Color"])

        # post pass 1
        node_tree.links.new(compose_lighting_n.inputs["Diffuse Color"], diff_mult_n.outputs["Color"])
        node_tree.links.new(compose_lighting_n.inputs["Material Color"], diff_mult_n.outputs["Color"])

        # post pass 2
        node_tree.links.new(out_add_spec_n.inputs["Color1"], compose_lighting_n.outputs["Composed Color"])
        node_tree.links.new(out_add_spec_n.inputs["Color2"], out_mat_n.outputs["Spec"])

        # output pass
        node_tree.links.new(output_n.inputs["Color"], out_add_spec_n.outputs["Color"])

    @staticmethod
    def set_lightmap_texture(node_tree, texture):
        """Set lightmap texture to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture which should be assignet to lightmap texture node
        :type texture: bpy.types.Texture
        """
        node_tree.nodes[WindowNight.LIGHTMAP_TEX_NODE].texture = texture

    @staticmethod
    def set_lightmap_uv(node_tree, uv_layer):
        """Set UV layer to lightmap texture in shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param uv_layer: uv layer string used for lightmap texture
        :type uv_layer: str
        """

        if uv_layer is None or uv_layer == "":
            uv_layer = _MESH_consts.none_uv

        node_tree.nodes[WindowNight.SEC_GEOM_NODE].uv_layer = uv_layer
