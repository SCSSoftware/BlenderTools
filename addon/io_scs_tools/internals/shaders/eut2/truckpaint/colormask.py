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

from io_scs_tools.internals.shaders.eut2.truckpaint import Truckpaint


class TruckpaintColormask(Truckpaint):
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

        # init parent
        Truckpaint.init(node_tree)
        Truckpaint.init_colormask_or_airbrush(node_tree)

        blend_mix_n = node_tree.nodes[Truckpaint.BLEND_MIX_NODE]
        blend_mix_n.inputs['Fac'].default_value = 1.0

        paint_diff_mult_n = node_tree.nodes[Truckpaint.PAINT_DIFFUSE_MULT_NODE]
        paint_diff_mult_n.inputs['Fac'].default_value = 1.0

        paint_spec_mult_n = node_tree.nodes[Truckpaint.PAINT_SPECULAR_MULT_NODE]
        paint_spec_mult_n.inputs['Fac'].default_value = 1.0
