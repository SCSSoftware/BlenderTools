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

import bpy
from io_scs_tools.consts import Material as _MAT_consts
from io_scs_tools.internals.shaders.eut2.std_node_groups import scs_uvs_combine_ng
from io_scs_tools.internals.shaders.eut2.std_node_groups import scs_uvs_separate_ng
from io_scs_tools.internals.shaders.eut2.window import window_offset_factor_ng
from io_scs_tools.internals.shaders.eut2.window import window_final_uv_ng

WINDOW_UV_OFFSET_G = _MAT_consts.node_group_prefix + "WindowUVOffsetGroup"


def get_node_group():
    """Gets node group for uv offseting based on view angle.
    For more information take a look at: eut2.window.cg

    NOTE: Due to lack of data view angle is calclulated
    based on normal of the mesh face.
    :return: node group which calculates change factor
    :rtype: bpy.types.NodeGroup
    """

    if WINDOW_UV_OFFSET_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[WINDOW_UV_OFFSET_G]


def __create_node_group__():
    """Create UV factor group.

    Inputs: UV, Normal, Incoming
    Outputs: UV Final
    """

    pos_x_shift = 185

    uv_offset_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=WINDOW_UV_OFFSET_G)

    # inputs defining
    uv_offset_g.inputs.new("NodeSocketVector", "UV")
    uv_offset_g.inputs.new("NodeSocketVector", "Normal")
    uv_offset_g.inputs.new("NodeSocketVector", "Incoming")
    input_n = uv_offset_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    uv_offset_g.outputs.new("NodeSocketVector", "UV Final")
    output_n = uv_offset_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 12, 0)

    # group nodes
    # pass 1
    es_world_up_n = uv_offset_g.nodes.new("ShaderNodeVectorTransform")
    es_world_up_n.name = es_world_up_n.label = "ESWorldUp"
    es_world_up_n.location = (pos_x_shift * 1, 200)
    es_world_up_n.vector_type = "NORMAL"
    es_world_up_n.convert_from = "WORLD"
    es_world_up_n.convert_to = "CAMERA"
    es_world_up_n.inputs[0].default_value = (0, 0, 1)

    es_normal_n = uv_offset_g.nodes.new("ShaderNodeVectorTransform")
    es_normal_n.name = es_normal_n.label = "ESNormal"
    es_normal_n.location = (pos_x_shift * 1, 0)
    es_normal_n.vector_type = "NORMAL"
    es_normal_n.convert_from = "WORLD"
    es_normal_n.convert_to = "CAMERA"

    es_window_z_n = uv_offset_g.nodes.new("ShaderNodeVectorTransform")
    es_window_z_n.name = es_window_z_n.label = "ESWindowZ"
    es_window_z_n.location = (pos_x_shift * 1, -200)
    es_window_z_n.vector_type = "NORMAL"
    es_window_z_n.convert_from = "WORLD"
    es_window_z_n.convert_to = "CAMERA"

    # pass 2
    es_window_x_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    es_window_x_n.name = es_window_x_n.label = "ESWindowX"
    es_window_x_n.location = (pos_x_shift * 2, 200)
    es_window_x_n.operation = "CROSS_PRODUCT"

    # pass 3
    es_window_y_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    es_window_y_n.name = es_window_y_n.label = "ESWindowY"
    es_window_y_n.location = (pos_x_shift * 3, 100)
    es_window_y_n.operation = "CROSS_PRODUCT"

    # pass 4
    wnd_to_eye_row1_mult_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    wnd_to_eye_row1_mult_n.name = wnd_to_eye_row1_mult_n.label = "WndToEyeRow1"
    wnd_to_eye_row1_mult_n.location = (pos_x_shift * 5, 200)
    wnd_to_eye_row1_mult_n.operation = "DOT_PRODUCT"

    wnd_to_eye_row2_mult_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    wnd_to_eye_row2_mult_n.name = wnd_to_eye_row2_mult_n.label = "WndToEyeRow2"
    wnd_to_eye_row2_mult_n.location = (pos_x_shift * 5, 0)
    wnd_to_eye_row2_mult_n.operation = "DOT_PRODUCT"

    wnd_to_eye_row3_mult_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    wnd_to_eye_row3_mult_n.name = wnd_to_eye_row3_mult_n.label = "WndToEyeRow3"
    wnd_to_eye_row3_mult_n.location = (pos_x_shift * 5, -200)
    wnd_to_eye_row3_mult_n.operation = "DOT_PRODUCT"

    # pass 5
    wnd_to_eye_xz_n = uv_offset_g.nodes.new("ShaderNodeCombineXYZ")
    wnd_to_eye_xz_n.name = wnd_to_eye_xz_n.label = "WndToEyeXZ"
    wnd_to_eye_xz_n.location = (pos_x_shift * 6, 200)
    wnd_to_eye_xz_n.inputs[1].default_value = 0.0

    wnd_to_eye_n = uv_offset_g.nodes.new("ShaderNodeCombineXYZ")
    wnd_to_eye_n.name = wnd_to_eye_n.label = "WndToEye"
    wnd_to_eye_n.location = (pos_x_shift * 6, 0)

    wnd_to_eye_yz_n = uv_offset_g.nodes.new("ShaderNodeCombineXYZ")
    wnd_to_eye_yz_n.name = wnd_to_eye_yz_n.label = "WndToEyeYZ"
    wnd_to_eye_yz_n.location = (pos_x_shift * 6, -200)
    wnd_to_eye_yz_n.inputs[0].default_value = 0.0

    # pass 6
    wnd_to_eye_xz_normalize_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    wnd_to_eye_xz_normalize_n.name = wnd_to_eye_xz_normalize_n.label = "WndToEyeXZNorm"
    wnd_to_eye_xz_normalize_n.location = (pos_x_shift * 7, 200)
    wnd_to_eye_xz_normalize_n.operation = "NORMALIZE"

    wnd_to_eye_yz_normalize_n = uv_offset_g.nodes.new("ShaderNodeVectorMath")
    wnd_to_eye_yz_normalize_n.name = wnd_to_eye_yz_normalize_n.label = "WndToEyeYZNorm"
    wnd_to_eye_yz_normalize_n.location = (pos_x_shift * 7, -200)
    wnd_to_eye_yz_normalize_n.operation = "NORMALIZE"

    # pass 7
    wnd_to_eye_xz_sep_n = uv_offset_g.nodes.new("ShaderNodeSeparateXYZ")
    wnd_to_eye_xz_sep_n.name = wnd_to_eye_xz_sep_n.label = "WndToEyeXZSeparate"
    wnd_to_eye_xz_sep_n.location = (pos_x_shift * 8, 200)

    wnd_to_eye_sep_n = uv_offset_g.nodes.new("ShaderNodeSeparateXYZ")
    wnd_to_eye_sep_n.name = wnd_to_eye_sep_n.label = "WndToEyeSeparate"
    wnd_to_eye_sep_n.location = (pos_x_shift * 8, 0)

    wnd_to_eye_yz_sep_n = uv_offset_g.nodes.new("ShaderNodeSeparateXYZ")
    wnd_to_eye_yz_sep_n.name = wnd_to_eye_yz_sep_n.label = "WndToEyeYZSeparate"
    wnd_to_eye_yz_sep_n.location = (pos_x_shift * 8, -200)

    # pass 8
    u_factor_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    u_factor_n.name = u_factor_n.label = "UFactor"
    u_factor_n.location = (pos_x_shift * 9, 200)
    u_factor_n.node_tree = window_offset_factor_ng.get_node_group()

    uv_sep_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    uv_sep_n.name = uv_sep_n.label = "UVSeparate"
    uv_sep_n.location = (pos_x_shift * 9, 0)
    uv_sep_n.node_tree = scs_uvs_separate_ng.get_node_group()

    v_factor_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    v_factor_n.name = v_factor_n.label = "VFactor"
    v_factor_n.location = (pos_x_shift * 9, -200)
    v_factor_n.node_tree = window_offset_factor_ng.get_node_group()

    # pass 9
    u_final_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    u_final_n.name = u_final_n.label = "UFinal"
    u_final_n.location = (pos_x_shift * 10, 100)
    u_final_n.node_tree = window_final_uv_ng.get_node_group()

    v_final_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    v_final_n.name = v_final_n.label = "VFinal"
    v_final_n.location = (pos_x_shift * 10, -100)
    v_final_n.node_tree = window_final_uv_ng.get_node_group()

    # pass 10
    uv_combine_n = uv_offset_g.nodes.new("ShaderNodeGroup")
    uv_combine_n.name = uv_combine_n.label = "UVFinal"
    uv_combine_n.location = (pos_x_shift * 11, 0)
    uv_combine_n.node_tree = scs_uvs_combine_ng.get_node_group()

    # group links
    # pass 1
    uv_offset_g.links.new(es_normal_n.inputs[0], input_n.outputs['Normal'])

    uv_offset_g.links.new(es_window_z_n.inputs[0], input_n.outputs['Incoming'])

    # pass 2
    uv_offset_g.links.new(es_window_x_n.inputs[0], es_world_up_n.outputs[0])
    uv_offset_g.links.new(es_window_x_n.inputs[1], es_normal_n.outputs[0])

    # pass 3
    uv_offset_g.links.new(es_window_y_n.inputs[0], es_window_x_n.outputs[0])
    uv_offset_g.links.new(es_window_y_n.inputs[1], es_normal_n.outputs[0])

    # pass 4
    uv_offset_g.links.new(wnd_to_eye_row1_mult_n.inputs[0], es_window_x_n.outputs[0])
    uv_offset_g.links.new(wnd_to_eye_row1_mult_n.inputs[1], es_window_z_n.outputs[0])

    uv_offset_g.links.new(wnd_to_eye_row2_mult_n.inputs[0], es_window_y_n.outputs[0])
    uv_offset_g.links.new(wnd_to_eye_row2_mult_n.inputs[1], es_window_z_n.outputs[0])

    uv_offset_g.links.new(wnd_to_eye_row3_mult_n.inputs[0], es_normal_n.outputs[0])
    uv_offset_g.links.new(wnd_to_eye_row3_mult_n.inputs[1], es_window_z_n.outputs[0])

    # pass 5
    uv_offset_g.links.new(wnd_to_eye_xz_n.inputs['X'], wnd_to_eye_row1_mult_n.outputs['Value'])
    uv_offset_g.links.new(wnd_to_eye_xz_n.inputs['Z'], wnd_to_eye_row3_mult_n.outputs['Value'])

    uv_offset_g.links.new(wnd_to_eye_n.inputs['X'], wnd_to_eye_row1_mult_n.outputs['Value'])
    uv_offset_g.links.new(wnd_to_eye_n.inputs['Y'], wnd_to_eye_row2_mult_n.outputs['Value'])
    uv_offset_g.links.new(wnd_to_eye_n.inputs['Z'], wnd_to_eye_row3_mult_n.outputs['Value'])

    uv_offset_g.links.new(wnd_to_eye_yz_n.inputs['Y'], wnd_to_eye_row2_mult_n.outputs['Value'])
    uv_offset_g.links.new(wnd_to_eye_yz_n.inputs['Z'], wnd_to_eye_row3_mult_n.outputs['Value'])

    # pass 6
    uv_offset_g.links.new(wnd_to_eye_xz_normalize_n.inputs[0], wnd_to_eye_xz_n.outputs[0])

    uv_offset_g.links.new(wnd_to_eye_yz_normalize_n.inputs[0], wnd_to_eye_yz_n.outputs[0])

    # pass 7
    uv_offset_g.links.new(wnd_to_eye_xz_sep_n.inputs[0], wnd_to_eye_xz_normalize_n.outputs[0])

    uv_offset_g.links.new(wnd_to_eye_sep_n.inputs[0], wnd_to_eye_n.outputs[0])

    uv_offset_g.links.new(wnd_to_eye_yz_sep_n.inputs[0], wnd_to_eye_yz_normalize_n.outputs[0])

    # pass 8
    uv_offset_g.links.new(u_factor_n.inputs['WndToEye Up'], wnd_to_eye_xz_sep_n.outputs['Z'])
    uv_offset_g.links.new(u_factor_n.inputs['WndToEye Direction'], wnd_to_eye_sep_n.outputs['X'])

    uv_offset_g.links.new(uv_sep_n.inputs[0], input_n.outputs['UV'])

    uv_offset_g.links.new(v_factor_n.inputs['WndToEye Up'], wnd_to_eye_yz_sep_n.outputs['Z'])
    uv_offset_g.links.new(v_factor_n.inputs['WndToEye Direction'], wnd_to_eye_sep_n.outputs['Y'])

    # pass 10
    uv_offset_g.links.new(u_final_n.inputs['UV'], uv_sep_n.outputs['U'])
    uv_offset_g.links.new(u_final_n.inputs['Factor'], u_factor_n.outputs['Offset Factor'])

    uv_offset_g.links.new(v_final_n.inputs['UV'], uv_sep_n.outputs['V'])
    uv_offset_g.links.new(v_final_n.inputs['Factor'], v_factor_n.outputs['Offset Factor'])

    # pass 11
    uv_offset_g.links.new(uv_combine_n.inputs['U'], u_final_n.outputs['Final UV'])
    uv_offset_g.links.new(uv_combine_n.inputs['V'], v_final_n.outputs['Final UV'])

    # output
    uv_offset_g.links.new(output_n.inputs['UV Final'], uv_combine_n.outputs['Vector'])
