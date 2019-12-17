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

import os
import gpu


class ShaderTypes:
    SMOOTH_COLOR_CLIPPED_3D = 1
    SMOOTH_COLOR_STIPPLE_CLIPPED_3D = 2


__cache = {}
"""Simple dictonary holding shader instances by shader type. To prevent loading shader each time one requests it."""


def __get_shader_data__(shader_filename):
    """Loads and gets shader data from given filename.

    :param shader_filename: filename of shader file inside io_scs_tools/internals/open_gl/shaders
    :type shader_filename: str
    :return: shader data string from given glsl shader
    :rtype: str
    """
    shader_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), shader_filename)

    with open(shader_filepath, "r") as file:
        shader_data_str = file.read()

    return shader_data_str


def get_shader(shader_type):
    """Get GPU shader for given type.

    :param shader_type: shader type from ShaderTypes
    :type shader_type: int
    :return:
    :rtype: gpu.types.GPUShader
    """
    if shader_type == ShaderTypes.SMOOTH_COLOR_CLIPPED_3D:

        if shader_type not in __cache:
            __cache[shader_type] = gpu.types.GPUShader(
                __get_shader_data__("smooth_color_clipped_3d_vert.glsl"),
                __get_shader_data__("smooth_color_clipped_3d_frag.glsl")
            )

    elif shader_type == ShaderTypes.SMOOTH_COLOR_STIPPLE_CLIPPED_3D:

        if shader_type not in __cache:
            __cache[shader_type] = gpu.types.GPUShader(
                __get_shader_data__("smooth_color_stipple_clipped_3d_vert.glsl"),
                __get_shader_data__("smooth_color_stipple_clipped_3d_frag.glsl"),
            )

    else:

        raise TypeError("Failed generating shader, unexepected shader type: %r!" % shader_type)

    return __cache[shader_type]
