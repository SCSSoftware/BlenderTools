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

import gpu


class ShaderTypes:
    SMOOTH_COLOR_CLIPPED_3D = 1
    SMOOTH_COLOR_STIPPLE_CLIPPED_3D = 2


__cache = {}
"""Simple dictonary holding shader instances by shader type. To prevent loading shader each time one requests it."""


def get_shader(shader_type):
    """Get GPU shader for given type.

    :param shader_type: shader type from ShaderTypes
    :type shader_type: int
    :return:
    :rtype: gpu.types.GPUShader
    """
    if shader_type == ShaderTypes.SMOOTH_COLOR_CLIPPED_3D:

        if shader_type not in __cache:
            vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
            vert_out.smooth("VEC4", "finalColor")
            vert_out.smooth("VEC4", "vertexPos")

            shader_info = gpu.types.GPUShaderCreateInfo()
            shader_info.push_constant("MAT4", "ModelViewProjectionMatrix")
            shader_info.push_constant("MAT4", "ModelMatrix")

            shader_info.typedef_source(
                """
                struct ClipData {
                    vec4 clip_planes[6];
                    int num_clip_planes;
                    int _pad1;
                    int _pad2;
                    int _pad3;
                };
                """
            )
            shader_info.uniform_buf(0, "ClipData", "clip_data")

            shader_info.vertex_in(0, "VEC3", "pos")
            shader_info.vertex_in(1, "VEC4", "color")

            shader_info.vertex_out(vert_out)
            shader_info.fragment_out(0, "VEC4", "fragColor")

            shader_info.vertex_source(
                """
                void main()
                {
                    vertexPos = vec4(pos, 1.0);
                    gl_Position = ModelViewProjectionMatrix * vertexPos;
                    gl_PointSize = 12.0;
                    finalColor = color;

                #ifdef USE_WORLD_CLIP_PLANES
                    world_clip_planes_calc_clip_distance((ModelMatrix * vec4(pos, 1.0)).xyz);
                #endif
                }
                """
            )
            shader_info.fragment_source(
                """
                void main()
                {
                    for (int i=0; i<clip_data.num_clip_planes; ++i) {
                        float d = dot(clip_data.clip_planes[i], vertexPos);
                        if (d < 0.0) discard;
                    }
                    fragColor = finalColor;
                }
                """
            )

            __cache[shader_type] = gpu.shader.create_from_info(shader_info)

            del vert_out
            del shader_info

    elif shader_type == ShaderTypes.SMOOTH_COLOR_STIPPLE_CLIPPED_3D:

        if shader_type not in __cache:
            vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
            vert_out.smooth("VEC4", "vertexColor")
            vert_out.flat("VEC4", "startVertexPos")    # use uninterpolated provoking vertex, to be able to calculate position on line
            vert_out.smooth("VEC4", "vertexPos")

            shader_info = gpu.types.GPUShaderCreateInfo()

            shader_info.push_constant("MAT4", "ModelViewProjectionMatrix")

            shader_info.typedef_source(
                """
                struct ClipData {
                    vec4 clip_planes[6];
                    int num_clip_planes;
                    int _pad1;
                    int _pad2;
                    int _pad3;
                };
                """
            )
            shader_info.uniform_buf(0, "ClipData", "clip_data")

            shader_info.vertex_in(0, "VEC3", "pos")
            shader_info.vertex_in(1, "VEC4", "color")
            shader_info.vertex_out(vert_out)
            shader_info.fragment_out(0, "VEC4", "fragColor")

            shader_info.vertex_source(
                """
                void main()
                {
                    startVertexPos = vec4(pos, 1.0);
                    vertexPos = startVertexPos;
                    vertexColor = color;

                    gl_Position = ModelViewProjectionMatrix * vertexPos;
                    gl_PointSize = 12.0;
                }
                """
            )
            shader_info.fragment_source(
                """
                void main()
                {
                    for (int i=0; i<clip_data.num_clip_planes; ++i) {
                        float d = dot(clip_data.clip_planes[i], vertexPos);
                        if (d < 0.0) discard;
                    }

                    if (step(sin(length(vertexPos - startVertexPos) * 100), 0.4) == 1) discard;

                    fragColor = vertexColor;
                }
                """
            )

            __cache[shader_type] = gpu.shader.create_from_info(shader_info)

            del vert_out
            del shader_info
    else:

        raise TypeError("Failed generating shader, unexepected shader type: %r!" % shader_type)

    return __cache[shader_type]
