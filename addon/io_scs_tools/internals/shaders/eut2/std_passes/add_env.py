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


from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env
from io_scs_tools.utils import convert as _convert_utils


class StdAddEnv:
    REFL_TEX_NODE = "ReflectionTex"
    ENV_COLOR_NODE = "EnvFactorColor"
    ADD_ENV_GROUP_NODE = "AddEnvGroup"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def add(node_tree, geom_n_name, spec_col_n_name, base_tex_n_name, out_mat_n_name, output_n_name, output_n_socket_name="Env Color"):
        """Add add env pass to node tree with links.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param geom_n_name: name of geometry node from which normal will be taken
        :type geom_n_name: str
        :param spec_col_n_name: name of specular color node from which specular color will be taken
        :type spec_col_n_name: str
        :param base_tex_n_name: name of base texture node from which alpha will be taken (if empty string it won't be used)
        :type base_tex_n_name: str
        :param out_mat_n_name: name of output material node from which output color will be taken
        :type out_mat_n_name: str
        :param output_n_name: name of output node with color input node to which result will be given
        :type output_n_name: str
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        geometry_n = node_tree.nodes[geom_n_name]
        spec_col_n = node_tree.nodes[spec_col_n_name]
        base_tex_n = node_tree.nodes[base_tex_n_name] if base_tex_n_name in node_tree.nodes else None
        out_mat_n = node_tree.nodes[out_mat_n_name]
        output_n = node_tree.nodes[output_n_name]

        # node creation
        refl_tex_n = node_tree.nodes.new("ShaderNodeTexture")
        refl_tex_n.name = refl_tex_n.label = StdAddEnv.REFL_TEX_NODE
        refl_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2500)

        env_col_n = node_tree.nodes.new("ShaderNodeRGB")
        env_col_n.name = env_col_n.label = StdAddEnv.ENV_COLOR_NODE
        env_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)

        add_env_gn = node_tree.nodes.new("ShaderNodeGroup")
        add_env_gn.name = add_env_gn.label = StdAddEnv.ADD_ENV_GROUP_NODE
        add_env_gn.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        add_env_gn.node_tree = add_env.get_node_group()
        add_env_gn.inputs['Apply Fresnel'].default_value = 1.0
        add_env_gn.inputs['Fresnel Scale'].default_value = 0.9
        add_env_gn.inputs['Fresnel Bias'].default_value = 0.2
        add_env_gn.inputs['Base Texture Alpha'].default_value = 0.5

        # geometry links
        node_tree.links.new(add_env_gn.inputs['Normal Vector'], geometry_n.outputs['Normal'])
        node_tree.links.new(add_env_gn.inputs['View Vector'], geometry_n.outputs['View'])
        node_tree.links.new(refl_tex_n.inputs['Vector'], geometry_n.outputs['Normal'])

        # if out material node is really material node and has normal output,
        # use it as this normal might include normal maps
        if "Normal" in out_mat_n.outputs:
            node_tree.links.new(refl_tex_n.inputs['Vector'], out_mat_n.outputs['Normal'])

        node_tree.links.new(add_env_gn.inputs['Env Factor Color'], env_col_n.outputs['Color'])
        node_tree.links.new(add_env_gn.inputs['Reflection Texture Color'], refl_tex_n.outputs['Color'])

        node_tree.links.new(add_env_gn.inputs['Specular Color'], spec_col_n.outputs['Color'])
        if add_env_gn and base_tex_n:
            node_tree.links.new(add_env_gn.inputs['Base Texture Alpha'], base_tex_n.outputs['Value'])

        node_tree.links.new(output_n.inputs[output_n_socket_name], add_env_gn.outputs['Environment Addition Color'])

    @staticmethod
    def set_reflection_texture(node_tree, texture):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param texture: texture object which should be used for reflection
        :type texture: bpy.types.Texture
        """

        node_tree.nodes[StdAddEnv.REFL_TEX_NODE].texture = texture

    @staticmethod
    def set_env_factor(node_tree, color):
        """Set environment factor color to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param color: environment color
        :type color: Color or tuple
        """

        color = _convert_utils.to_node_color(color)

        node_tree.nodes[StdAddEnv.ENV_COLOR_NODE].outputs[0].default_value = color

    @staticmethod
    def set_fresnel(node_tree, bias_scale):
        """Set fresnel bias and scale value to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param bias_scale: bias and scale factors as tuple: (bias, scale)
        :type bias_scale: (float, float)
        """

        node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Bias'].default_value = bias_scale[0]
        node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE].inputs['Fresnel Scale'].default_value = bias_scale[1]
