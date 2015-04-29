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
from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env


class DifSpecAddEnv(DifSpec):
    REFL_TEX_NODE = "ReflectionTex"
    ENV_COLOR_NODE = "EnvFactorColor"
    ADD_ENV_GROUP_NODE = "AddEnvGroup"
    OUT_ADD_REFL_NODE = "OutputAddRefl"

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
        DifSpec.init(node_tree)

        geometry_n = node_tree.nodes[DifSpec.GEOM_NODE]
        spec_col_n = node_tree.nodes[DifSpec.SPEC_COL_NODE]
        base_tex_n = node_tree.nodes[DifSpec.BASE_TEX_NODE]
        out_mat_n = node_tree.nodes[DifSpec.OUT_MAT_NODE]
        output_n = node_tree.nodes[DifSpec.OUTPUT_NODE]

        # move existing
        output_n.location.x += pos_x_shift

        # node creation
        refl_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        refl_tex_n.name = DifSpecAddEnv.REFL_TEX_NODE
        refl_tex_n.label = DifSpecAddEnv.REFL_TEX_NODE
        refl_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2500)

        env_col_n = node_tree.nodes.new("ShaderNodeRGB")
        env_col_n.name = DifSpecAddEnv.ENV_COLOR_NODE
        env_col_n.label = DifSpecAddEnv.ENV_COLOR_NODE
        env_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)

        add_env_gn = node_tree.nodes.new("ShaderNodeGroup")
        add_env_gn.name = DifSpecAddEnv.ADD_ENV_GROUP_NODE
        add_env_gn.label = DifSpecAddEnv.ADD_ENV_GROUP_NODE
        add_env_gn.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        add_env_gn.node_tree = add_env.get_node_group()
        add_env_gn.inputs['Apply Fresnel'].default_value = 1.0
        add_env_gn.inputs['Fresnel Scale'].default_value = 0.9
        add_env_gn.inputs['Fresnel Bias'].default_value = 0.2

        out_add_refl_n = node_tree.nodes.new("ShaderNodeMixRGB")
        out_add_refl_n.name = DifSpecAddEnv.OUT_ADD_REFL_NODE
        out_add_refl_n.label = DifSpecAddEnv.OUT_ADD_REFL_NODE
        out_add_refl_n.location = (output_n.location.x - pos_x_shift, start_pos_y + 1950)
        out_add_refl_n.blend_type = "ADD"
        out_add_refl_n.inputs['Fac'].default_value = 1

        # geometry links
        node_tree.links.new(add_env_gn.inputs['Normal Vector'], geometry_n.outputs['Normal'])
        node_tree.links.new(add_env_gn.inputs['View Vector'], geometry_n.outputs['View'])
        node_tree.links.new(refl_tex_n.inputs['Vector'], geometry_n.outputs['Normal'])

        node_tree.links.new(add_env_gn.inputs['Env Factor Color'], env_col_n.outputs['Color'])
        node_tree.links.new(add_env_gn.inputs['Reflection Texture Color'], refl_tex_n.outputs['Color'])

        node_tree.links.new(add_env_gn.inputs['Specular Color'], spec_col_n.outputs['Color'])
        node_tree.links.new(add_env_gn.inputs['Base Texture Alpha'], base_tex_n.outputs['Value'])

        # output pass
        node_tree.links.new(out_add_refl_n.inputs['Color1'], add_env_gn.outputs['Environment Addition Color'])
        node_tree.links.new(out_add_refl_n.inputs['Color2'], out_mat_n.outputs['Color'])

        node_tree.links.new(output_n.inputs['Color'], out_add_refl_n.outputs['Color'])

    @staticmethod
    def set_reflection_texture(node_tree, texture):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture object which should be used for reflection
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[DifSpecAddEnv.REFL_TEX_NODE].texture = texture

    @staticmethod
    def set_env_factor(node_tree, color):
        """Set environment factor color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: environment color
        :type color: Color or tuple
        """

        if len(color) == 3:
            color = tuple(color) + (1,)

        node_tree.nodes[DifSpecAddEnv.ENV_COLOR_NODE].outputs[0].default_value = color

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Bias'].default_value = bias_scale[0]
        node_tree.nodes[DifSpecAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Scale'].default_value = bias_scale[1]