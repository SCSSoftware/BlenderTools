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


from io_scs_tools.internals.shaders.eut2.dif_anim import anim_blend_factor_ng
from io_scs_tools.internals.shaders.eut2.water import water_stream_ng
from io_scs_tools.internals.shaders.eut2.truckpaint import Truckpaint
from io_scs_tools.internals.shaders.flavors import paint


def update_shaders(scene):
    """Update any time changes in shaders.

    :param scene: scene in which time for shaders is being updated
    :type scene: bpy.types.Scene
    """

    # update animation blend factor group node
    anim_blend_factor_ng.update_time(scene)

    # update water streams
    water_stream_ng.update_time(scene)


def set_base_paint_color(node_tree, color):
    """Sets base paint color from global settings to given node tree of material

    :param node_tree: node tree to which paint color should be applied
    :type node_tree: bpy.types.NodeTree
    :param color: new color value
    :type color: bpy.utils.Color
    :return:
    :rtype:
    """
    # update paint flavor based shaders
    paint.set_color(node_tree, color)

    # update eut2 truckpaint shaders
    Truckpaint.set_base_paint_color(node_tree, color)
