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

# Copyright (C) 2019: SCS Software

from io_scs_tools.internals.shaders.eut2.unlit_tex import UnlitTex


class UnlitTexA8(UnlitTex):

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        Color result in this shader is always (0,0,0) and transparency is donate by grayscale texture and not alpha channel.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        # init parent
        UnlitTex.init(node_tree)

        # remove texture multiplier, which will break link for resulting color
        node_tree.nodes.remove(node_tree.nodes[UnlitTex.TEX_MULT_NODE])

        # then set output color to (0,0,0)
        node_tree.nodes[UnlitTex.OUT_SHADER_NODE].inputs['Emissive Color'].default_value = (0,) * 4

        # and instead alpha use color channel (as this shader requests grayscale)
        node_tree.links.new(node_tree.nodes[UnlitTex.ALPHA_INV_NODE].inputs[1], node_tree.nodes[UnlitTex.BASE_TEX_NODE].outputs['Color'])

    @staticmethod
    def set_paint_flavor(node_tree, switch_on):
        """Set paint flavor to this shader.

        :param node_tree: node tree of current shader
        :type node_tree: bpy.types.NodeTree
        :param switch_on: flag indication if flavor should be switched on or off
        :type switch_on: bool
        """
        pass  # no matter the color, we always output (0,0,0) opaque color in this shader, thus useless to do anything
