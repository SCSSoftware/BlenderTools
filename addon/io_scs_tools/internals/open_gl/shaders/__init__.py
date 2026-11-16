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


MAX_CLIP_PLANES = 6
"""Maximum number of clip planes supported by our shaders."""


__GLSL_TYPES = {'VEC4': "vec4"}


def __create_shader__(varyings, vert_filename, frag_filename):
    """Creates shader with common inputs, uniforms and outputs.

    :param varyings: list of (interpolation, type, name) passed from vertex to fragment shader, interpolation: 'smooth' | 'flat'
    :type varyings: list[tuple[str, str, str]]
    :param vert_filename: filename of vertex shader source (only main function)
    :type vert_filename: str
    :param frag_filename: filename of fragment shader source (only main function)
    :type frag_filename: str
    :return: shader
    :rtype: gpu.types.GPUShader
    """
    vert_src = __get_shader_data__(vert_filename)
    frag_src = __get_shader_data__(frag_filename)

    if hasattr(gpu.types, "GPUShaderCreateInfo"):  # Blender 3.4+ (required for Vulkan/Metal backends)

        vert_out = gpu.types.GPUStageInterfaceInfo("scs_" + vert_filename.replace(".", "_") + "_iface")
        for interp, var_type, var_name in varyings:
            getattr(vert_out, interp)(var_type, var_name)

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        shader_info.push_constant('VEC4', "clip_planes", MAX_CLIP_PLANES)
        shader_info.push_constant('INT', "num_clip_planes")
        shader_info.vertex_in(0, 'VEC3', "pos")
        shader_info.vertex_in(1, 'VEC4', "color")
        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, 'VEC4', "fragColor")
        shader_info.vertex_source(vert_src)
        shader_info.fragment_source(frag_src)

        return gpu.shader.create_from_info(shader_info)

    # legacy OpenGL shader creation: add declarations to the sources ourselves
    uniforms = "uniform vec4 clip_planes[%i];\nuniform int num_clip_planes;\n" % MAX_CLIP_PLANES
    vert_decl = "uniform mat4 ModelViewProjectionMatrix;\nin vec3 pos;\nin vec4 color;\n"
    frag_decl = uniforms + "out vec4 fragColor;\n"
    for interp, var_type, var_name in varyings:
        qualifier = "flat " if interp == "flat" else ""
        vert_decl += "%sout %s %s;\n" % (qualifier, __GLSL_TYPES[var_type], var_name)
        frag_decl += "%sin %s %s;\n" % (qualifier, __GLSL_TYPES[var_type], var_name)

    return gpu.types.GPUShader(vert_decl + vert_src, frag_decl + frag_src)


def get_shader(shader_type):
    """Get GPU shader for given type.

    :param shader_type: shader type from ShaderTypes
    :type shader_type: int
    :return:
    :rtype: gpu.types.GPUShader
    """
    if shader_type in __cache:
        return __cache[shader_type]

    if shader_type == ShaderTypes.SMOOTH_COLOR_CLIPPED_3D:

        __cache[shader_type] = __create_shader__(
            (('smooth', 'VEC4', "finalColor"),
             ('smooth', 'VEC4', "vertexPos")),
            "smooth_color_clipped_3d_vert.glsl",
            "smooth_color_clipped_3d_frag.glsl"
        )

    elif shader_type == ShaderTypes.SMOOTH_COLOR_STIPPLE_CLIPPED_3D:

        __cache[shader_type] = __create_shader__(
            (('smooth', 'VEC4', "vertexColor"),
             ('flat', 'VEC4', "startVertexPos"),  # uninterpolated provoking vertex, to be able to calculate position on line
             ('smooth', 'VEC4', "vertexPos")),
            "smooth_color_stipple_clipped_3d_vert.glsl",
            "smooth_color_stipple_clipped_3d_frag.glsl"
        )

    else:

        raise TypeError("Failed generating shader, unexepected shader type: %r!" % shader_type)

    return __cache[shader_type]
