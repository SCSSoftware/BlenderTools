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

# Copyright (C) 2015-2019: SCS Software

from io_scs_tools.internals.shaders.eut2.std_node_groups import add_env_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import refl_normal_ng
from io_scs_tools.utils import convert as _convert_utils


class StdAddEnv:
    REFL_NORMAL_NODE = "ReflectionNormal"
    REFL_TEX_NODE = "ReflectionTex"
    ENV_COLOR_NODE = "EnvFactorColor"
    ADD_ENV_GROUP_NODE = "AddEnvGroup"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def add(node_tree, geom_n_name, spec_col_socket, alpha_socket, final_normal_socket, output_socket):
        """Add add env pass to node tree with links.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        :param geom_n_name: name of geometry node from which normal and view vectors will be taken
        :type geom_n_name: str
        :param spec_col_socket: specular color node socket from which specular color will be taken
        :type spec_col_socket: bpy.type.NodeSocket
        :param alpha_socket: socket from which alpha will be taken (if None it won't be used)
        :type alpha_socket: bpy.type.NodeSocket | None
        :param final_normal_socket: socket of final normal, if not provided geometry normal is used
        :type final_normal_socket: bpy.type.NodeSocket | None
        :param output_socket: output socket to which result will be given
        :type output_socket: bpy.type.NodeSocket
        """

        start_pos_x = 0
        start_pos_y = 0

        pos_x_shift = 185

        geometry_n = node_tree.nodes[geom_n_name]

        # node creation
        refl_normal_n = node_tree.nodes.new("ShaderNodeGroup")
        refl_normal_n.name = refl_normal_n.label = StdAddEnv.REFL_NORMAL_NODE
        refl_normal_n.location = (start_pos_x, start_pos_y + 2500)
        refl_normal_n.node_tree = refl_normal_ng.get_node_group()

        refl_tex_n = node_tree.nodes.new("ShaderNodeTexEnvironment")
        refl_tex_n.name = refl_tex_n.label = StdAddEnv.REFL_TEX_NODE
        refl_tex_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2500)
        refl_tex_n.width = 140

        env_col_n = node_tree.nodes.new("ShaderNodeRGB")
        env_col_n.name = env_col_n.label = StdAddEnv.ENV_COLOR_NODE
        env_col_n.location = (start_pos_x + pos_x_shift, start_pos_y + 2200)

        add_env_n = node_tree.nodes.new("ShaderNodeGroup")
        add_env_n.name = add_env_n.label = StdAddEnv.ADD_ENV_GROUP_NODE
        add_env_n.location = (start_pos_x + pos_x_shift * 3, start_pos_y + 2300)
        add_env_n.node_tree = add_env_ng.get_node_group()
        add_env_n.inputs['Apply Fresnel'].default_value = 1.0
        add_env_n.inputs['Fresnel Scale'].default_value = 0.9
        add_env_n.inputs['Fresnel Bias'].default_value = 0.2
        add_env_n.inputs['Base Texture Alpha'].default_value = 0.5
        add_env_n.inputs['Weighted Color'].default_value = (1.0,) * 4
        add_env_n.inputs['Strength Multiplier'].default_value = 1.0

        # geometry links
        node_tree.links.new(refl_normal_n.inputs['Incoming'], geometry_n.outputs['Incoming'])
        node_tree.links.new(refl_normal_n.inputs['Normal'], geometry_n.outputs['Normal'])

        node_tree.links.new(refl_tex_n.inputs['Vector'], refl_normal_n.outputs['Reflection Normal'])

        node_tree.links.new(add_env_n.inputs['Normal Vector'], geometry_n.outputs['Normal'])
        node_tree.links.new(add_env_n.inputs['Reflection Normal Vector'], refl_normal_n.outputs['Reflection Normal'])

        # if out material node is really material node and has normal output,
        # use it as this normal might include normal maps
        if final_normal_socket is not None:
            node_tree.links.new(refl_normal_n.inputs['Normal'], final_normal_socket)
            node_tree.links.new(add_env_n.inputs['Normal Vector'], final_normal_socket)

        node_tree.links.new(add_env_n.inputs['Env Factor Color'], env_col_n.outputs['Color'])
        node_tree.links.new(add_env_n.inputs['Reflection Texture Color'], refl_tex_n.outputs['Color'])

        node_tree.links.new(add_env_n.inputs['Specular Color'], spec_col_socket)
        if add_env_n and alpha_socket:
            node_tree.links.new(add_env_n.inputs['Base Texture Alpha'], alpha_socket)

        node_tree.links.new(output_socket, add_env_n.outputs['Environment Addition Color'])

    @staticmethod
    def set_reflection_texture(node_tree, image):
        """Set reflection texture on shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param image: texture image object which should be used for reflection
        :type image: bpy.types.Image
        """

        node_tree.nodes[StdAddEnv.REFL_TEX_NODE].image = image

    @staticmethod
    def set_reflection_texture_settings(node_tree, settings):
        """Set reflection texture settings to shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param settings: binary string of TOBJ settings gotten from tobj import
        :type settings: str
        """
        pass  # reflection texture shouldn't use any custom settings

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
