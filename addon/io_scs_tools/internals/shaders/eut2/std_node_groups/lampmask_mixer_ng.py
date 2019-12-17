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
from io_scs_tools.consts import LampTools as _LT_consts
from io_scs_tools.consts import Material as _MAT_consts

VEHICLE_SIDES = _LT_consts.VehicleSides
VEHICLE_LAMP_TYPES = _LT_consts.VehicleLampTypes
AUX_LAMP_TYPES = _LT_consts.AuxiliaryLampTypes
TRAFFIC_LIGHT_TYPES = _LT_consts.TrafficLightTypes

UV_X_TILES = ["UV_X_0_", "UV_X_1_", "UV_X_2_", "UV_X_3_", "UV_X_4_"]
UV_Y_TILES = ["UV_Y_0_", "UV_Y_1_", "UV_Y_2_", "UV_Y_3_"]

LAMPMASK_MIX_G = _MAT_consts.node_group_prefix + "LampmaskMixerGroup"

_UV_DOT_X_NODE = "UV_X_Separator"
_UV_DOT_Y_NODE = "UV_Y_Separator"
_TEX_COL_SEP_NODE = "TexColorSeparator"
_MIN_UV_SUFFIX = "MinUV"
_MAX_UV_SUFFIX = "MaxUV"
_IN_BOUNDS_SUFFIX = "InBounds"
_ADD_NODE_PREFIX = "Addition"


def get_node_group():
    """Gets node group for calculation of lamp mask addition color.

    :return: node group which calculates reflection normal
    :rtype: bpy.types.NodeGroup
    """

    if LAMPMASK_MIX_G not in bpy.data.node_groups:
        __create_node_group__()

    return bpy.data.node_groups[LAMPMASK_MIX_G]


def __create_node_group__():
    """Create lamp mask mixer group.

    Inputs: View Vector, Normal Vector
    Outputs: Reflection Normal Vector
    """
    pos_x_shift = 185

    lampmask_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=LAMPMASK_MIX_G)

    # inputs defining
    lampmask_g.inputs.new("NodeSocketFloat", "Lampmask Tex Alpha")
    lampmask_g.inputs.new("NodeSocketColor", "Lampmask Tex Color")
    lampmask_g.inputs.new("NodeSocketVector", "UV Vector")
    input_n = lampmask_g.nodes.new("NodeGroupInput")
    input_n.location = (0, 0)

    # outputs defining
    lampmask_g.outputs.new("NodeSocketColor", "Lampmask Addition Color")
    output_n = lampmask_g.nodes.new("NodeGroupOutput")
    output_n.location = (pos_x_shift * 9, 0)

    # nodes creation
    tex_col_sep_n = lampmask_g.nodes.new("ShaderNodeSeparateRGB")
    tex_col_sep_n.name = _TEX_COL_SEP_NODE
    tex_col_sep_n.label = _TEX_COL_SEP_NODE
    tex_col_sep_n.location = (pos_x_shift, 400)

    uv_x_dot_n = lampmask_g.nodes.new("ShaderNodeVectorMath")
    uv_x_dot_n.name = _UV_DOT_X_NODE
    uv_x_dot_n.label = _UV_DOT_X_NODE
    uv_x_dot_n.location = (pos_x_shift, -200)
    uv_x_dot_n.operation = "DOT_PRODUCT"
    uv_x_dot_n.inputs[1].default_value = (1.0, 0, 0)

    uv_y_dot_n = lampmask_g.nodes.new("ShaderNodeVectorMath")
    uv_y_dot_n.name = _UV_DOT_Y_NODE
    uv_y_dot_n.label = _UV_DOT_Y_NODE
    uv_y_dot_n.location = (pos_x_shift, -450)
    uv_y_dot_n.operation = "DOT_PRODUCT"
    uv_y_dot_n.inputs[1].default_value = (0, 1.0, 0)

    # links creation
    lampmask_g.links.new(tex_col_sep_n.inputs["Image"], input_n.outputs["Lampmask Tex Color"])
    lampmask_g.links.new(uv_x_dot_n.inputs[0], input_n.outputs["UV Vector"])
    lampmask_g.links.new(uv_y_dot_n.inputs[0], input_n.outputs["UV Vector"])

    nodes_for_addition = []

    # init uv tilling mechanism
    pos_y = -100
    max_x_uv = 1
    for uv_x_tile in UV_X_TILES:

        __init_uv_tile_bounding_nodes__(lampmask_g, uv_x_dot_n, uv_x_tile, pos_x_shift * 2, pos_y, max_x_uv)

        pos_y -= 50
        max_x_uv += 1

    max_y_uv = 1
    pos_y = -400
    for uv_y_tile in UV_Y_TILES:

        __init_uv_tile_bounding_nodes__(lampmask_g, uv_y_dot_n, uv_y_tile, pos_x_shift * 2, pos_y, max_y_uv)

        pos_y -= 50
        max_y_uv += 1

    # init vehicle sides uv bounding mechanism
    pos_y = -50
    for vehicle_side in VEHICLE_SIDES:
        __init_vehicle_uv_bounding_nodes__(lampmask_g, vehicle_side, pos_x_shift * 2, pos_y)

        pos_y -= 50

    # init traffic light uv bounding mechanism
    pos_y = -350
    for traffic_light_type in TRAFFIC_LIGHT_TYPES:
        __init_traffic_light_uv_bounding_nodes__(lampmask_g, traffic_light_type, pos_x_shift * 2, pos_y)

        pos_y -= 100

    # init vehicle sides switches mechanism
    pos_y = 1000
    for vehicle_lamp_type in VEHICLE_LAMP_TYPES:

        if vehicle_lamp_type == VEHICLE_LAMP_TYPES.Positional:  # make extra space for positional
            pos_y -= 100

        __init_vehicle_switch_nodes__(lampmask_g,
                                      input_n.outputs["Lampmask Tex Alpha"],
                                      tex_col_sep_n.outputs["R"],
                                      tex_col_sep_n.outputs["G"],
                                      tex_col_sep_n.outputs["B"],
                                      vehicle_lamp_type,
                                      pos_x_shift * 5, pos_y,
                                      nodes_for_addition)
        pos_y -= 75

    # init auxiliary lamp switches mechanism
    pos_y -= 60
    for aux_lamp_type in AUX_LAMP_TYPES:

        __init_aux_switch_nodes__(lampmask_g,
                                  input_n.outputs["Lampmask Tex Alpha"],
                                  tex_col_sep_n.outputs["R"],
                                  tex_col_sep_n.outputs["G"],
                                  aux_lamp_type,
                                  pos_x_shift * 5, pos_y,
                                  nodes_for_addition)

        pos_y -= 75

    # init traffic lights switches mechanism
    pos_y -= 60
    for traffic_light_type in TRAFFIC_LIGHT_TYPES:

        __init_traffic_light_switch_nodes__(lampmask_g,
                                            input_n.outputs["Lampmask Tex Alpha"],
                                            traffic_light_type,
                                            pos_x_shift * 5, pos_y,
                                            nodes_for_addition)

        pos_y -= 40

    # init all addition nodes which mixes values from all vehicle sides and all vehicle types together
    i = 1
    last_addition_n = None
    while i < len(nodes_for_addition):

        curr_node = nodes_for_addition[i]

        add_n = lampmask_g.nodes.new("ShaderNodeMath")
        add_n.name = _ADD_NODE_PREFIX + str(i)
        add_n.label = _ADD_NODE_PREFIX + str(i)
        add_n.location = (curr_node.location.x + 120, curr_node.location.y)
        add_n.hide = True
        add_n.operation = "ADD"

        if last_addition_n:
            lampmask_g.links.new(add_n.inputs[0], last_addition_n.outputs[0])
        else:
            lampmask_g.links.new(add_n.inputs[0], nodes_for_addition[0].outputs[0])

        lampmask_g.links.new(add_n.inputs[1], curr_node.outputs[0])

        last_addition_n = add_n
        i += 1

    lampmask_g.links.new(output_n.inputs["Lampmask Addition Color"], last_addition_n.outputs[0])


def __init_uv_tile_bounding_nodes__(node_tree, uv_dot_n, name, pos_x, pos_y, max_x_uv):
    """Creates and links nodes to bind u or v coordinate to bound of given tile.
    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param uv_dot_n: node which calculates dot product for returning only U coordinate of uv map
    :type uv_dot_n: bpy.types.ShaderNodeVectorMath
    :param name: name of the node for min/max tile
    :type name: str
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    :param max_x_uv: maximum U coordinate offset for given tile
    :type max_x_uv: int
    """

    max_uv_n = node_tree.nodes.new("ShaderNodeMath")
    max_uv_n.name = name + _MAX_UV_SUFFIX
    max_uv_n.label = name + _MAX_UV_SUFFIX
    max_uv_n.location = (pos_x, pos_y - 50)
    max_uv_n.hide = True
    max_uv_n.operation = "LESS_THAN"
    max_uv_n.inputs[1].default_value = max_x_uv

    if max_x_uv == 1:

        min_uv_n = node_tree.nodes.new("ShaderNodeMath")
        min_uv_n.name = name + _MIN_UV_SUFFIX
        min_uv_n.label = name + _MIN_UV_SUFFIX
        min_uv_n.location = (pos_x, pos_y)
        min_uv_n.hide = True
        min_uv_n.operation = "LESS_THAN"
        min_uv_n.inputs[1].default_value = max_x_uv - 2

        node_tree.links.new(min_uv_n.inputs[0], uv_dot_n.outputs['Value'])

    node_tree.links.new(max_uv_n.inputs[0], uv_dot_n.outputs['Value'])


def __init_vehicle_uv_bounding_nodes__(node_tree, vehicle_side, pos_x, pos_y):
    """Creates and links nodes to bind UV coordinates to uv offset prescripted for sides of vehicle.
    These nodes are returning 1 if given vehicle side should be shown on lamp mask; otherwise 0

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param vehicle_side: for which vehicle side nodes should be created
    :type vehicle_side: VehicleSides
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    """
    if vehicle_side == VEHICLE_SIDES.FrontLeft:
        min_uv_n = node_tree.nodes[UV_X_TILES[0] + _MIN_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[0] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.FrontRight:
        min_uv_n = node_tree.nodes[UV_X_TILES[0] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[1] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.RearLeft:
        min_uv_n = node_tree.nodes[UV_X_TILES[1] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[2] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.RearRight:
        min_uv_n = node_tree.nodes[UV_X_TILES[2] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[3] + _MAX_UV_SUFFIX]
    else:  # fallback to middle
        min_uv_n = node_tree.nodes[UV_X_TILES[3] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[4] + _MAX_UV_SUFFIX]

    uv_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_in_bounds_n.name = vehicle_side.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.label = vehicle_side.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.location = (pos_x + 185, pos_y - 50)
    uv_in_bounds_n.width_hidden = 100
    uv_in_bounds_n.hide = True
    uv_in_bounds_n.operation = "LESS_THAN"

    # links creation
    node_tree.links.new(uv_in_bounds_n.inputs[0], min_uv_n.outputs[0])
    node_tree.links.new(uv_in_bounds_n.inputs[1], max_uv_n.outputs[0])


def __init_traffic_light_uv_bounding_nodes__(node_tree, traffic_light_type, pos_x, pos_y):
    """Creates and links nodes to bind UV coordinates to uv offset prescripted for traffic light type.
    These nodes are returning 1 if given traffic light should be shown on lamp mask; otherwise 0

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param traffic_light_type: for which traffic light nodes should be created
    :type traffic_light_type: TrafficLightTypes
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    """

    min_tile_i = max_tile_i = 0
    if traffic_light_type == TRAFFIC_LIGHT_TYPES.Red:
        min_tile_i = 0
        max_tile_i = 1
    elif traffic_light_type == TRAFFIC_LIGHT_TYPES.Yellow:
        min_tile_i = 1
        max_tile_i = 2
    elif traffic_light_type == TRAFFIC_LIGHT_TYPES.Green:
        min_tile_i = 2
        max_tile_i = 3

    uv_x_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_x_in_bounds_n.name = traffic_light_type.name + "X" + _IN_BOUNDS_SUFFIX
    uv_x_in_bounds_n.label = traffic_light_type.name + "X" + _IN_BOUNDS_SUFFIX
    uv_x_in_bounds_n.location = (pos_x + 185, pos_y)
    uv_x_in_bounds_n.width_hidden = 100
    uv_x_in_bounds_n.hide = True
    uv_x_in_bounds_n.operation = "LESS_THAN"

    uv_y_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_y_in_bounds_n.name = traffic_light_type.name + "Y" + _IN_BOUNDS_SUFFIX
    uv_y_in_bounds_n.label = traffic_light_type.name + "Y" + _IN_BOUNDS_SUFFIX
    uv_y_in_bounds_n.location = (pos_x + 185, pos_y - 50)
    uv_y_in_bounds_n.width_hidden = 100
    uv_y_in_bounds_n.hide = True
    uv_y_in_bounds_n.operation = "LESS_THAN"

    uv_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_in_bounds_n.name = traffic_light_type.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.label = traffic_light_type.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.location = (pos_x + 185 * 2, pos_y)
    uv_in_bounds_n.width_hidden = 100
    uv_in_bounds_n.hide = True
    uv_in_bounds_n.operation = "MULTIPLY"

    # links creation
    min_uv_x_n = node_tree.nodes[UV_X_TILES[min_tile_i] + _MAX_UV_SUFFIX]
    max_uv_x_n = node_tree.nodes[UV_X_TILES[max_tile_i] + _MAX_UV_SUFFIX]
    node_tree.links.new(uv_x_in_bounds_n.inputs[0], min_uv_x_n.outputs[0])
    node_tree.links.new(uv_x_in_bounds_n.inputs[1], max_uv_x_n.outputs[0])

    min_uv_y_n = node_tree.nodes[UV_Y_TILES[min_tile_i] + _MAX_UV_SUFFIX]
    max_uv_y_n = node_tree.nodes[UV_Y_TILES[max_tile_i] + _MAX_UV_SUFFIX]
    node_tree.links.new(uv_y_in_bounds_n.inputs[0], min_uv_y_n.outputs[0])
    node_tree.links.new(uv_y_in_bounds_n.inputs[1], max_uv_y_n.outputs[0])

    node_tree.links.new(uv_in_bounds_n.inputs[0], uv_x_in_bounds_n.outputs[0])
    node_tree.links.new(uv_in_bounds_n.inputs[1], uv_y_in_bounds_n.outputs[0])


def __init_vehicle_switch_nodes__(node_tree, a_output, r_output, g_output, b_output, lamp_type, pos_x, pos_y, nodes_for_addition):
    """Creation and linking of switching nodes, covering all combinations for vehicle lamp mask.
    Combinations are created between switching nodes and uv bounding nodes which gives end float factor of mask for each of them,
    representing how much color should be added for given lamp_type per vehicle side from prescribed RGBA channel.

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param a_output: alpha value of lampmask texture
    :type a_output: bpy.types.NodeSocketFloat
    :param r_output: red value of lampmask texture
    :type r_output: bpy.types.NodeSocketFloat
    :param g_output: green value of lampmask texture
    :type g_output: bpy.types.NodeSocketFloat
    :param b_output: blue value of lampmask texture
    :type b_output: bpy.types.NodeSocketFloat
    :param lamp_type: lamp type for which switching nodes should be created
    :type lamp_type: VehicleLampTypes
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    :param nodes_for_addition: list for nodes which should be summed and returned as result of vehicle addition color
    :type nodes_for_addition: list of bpy.types.Node
    """

    # nodes creation
    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name
    switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y)
    switch_n.width_hidden = 100
    switch_n.hide = True
    switch_n.operation = "MULTIPLY"
    switch_n.inputs[0].default_value = 0.0

    # nodes and links depending on type
    if lamp_type == VEHICLE_LAMP_TYPES.Positional:
        node_tree.links.new(switch_n.inputs[1], a_output)

        # merge all options
        mult_pos_y = pos_y + 80
        for vehicle_side in VEHICLE_SIDES:

            node_name = lamp_type.name + vehicle_side.name
            position = (pos_x + 185 * 2, mult_pos_y)
            in_bounds_n = node_tree.nodes[vehicle_side.name + _IN_BOUNDS_SUFFIX]
            mult_n = __create_merging_node__(node_tree, node_name, position, in_bounds_n.outputs[0], switch_n.outputs[0])
            nodes_for_addition.append(mult_n)

            mult_pos_y -= 36

    elif lamp_type == VEHICLE_LAMP_TYPES.DRL:
        node_tree.links.new(switch_n.inputs[1], b_output)

        node_name = lamp_type.name + VEHICLE_SIDES.Middle.name
        position = (pos_x + 185 * 2, pos_y)
        in_bounds_n = node_tree.nodes[VEHICLE_SIDES.Middle.name + _IN_BOUNDS_SUFFIX]
        mult_n = __create_merging_node__(node_tree, node_name, position, in_bounds_n.outputs[0], switch_n.outputs[0])
        nodes_for_addition.append(mult_n)

    else:
        color_output = veh_side_name1 = veh_side_name2 = None
        if lamp_type == VEHICLE_LAMP_TYPES.LeftTurn:

            color_output = r_output
            veh_side_name1 = VEHICLE_SIDES.FrontLeft.name
            veh_side_name2 = VEHICLE_SIDES.RearLeft.name

        elif lamp_type == VEHICLE_LAMP_TYPES.RightTurn:

            color_output = r_output
            veh_side_name1 = VEHICLE_SIDES.FrontRight.name
            veh_side_name2 = VEHICLE_SIDES.RearRight.name

        elif lamp_type == VEHICLE_LAMP_TYPES.Brake:

            color_output = g_output
            veh_side_name1 = VEHICLE_SIDES.RearLeft.name
            veh_side_name2 = VEHICLE_SIDES.RearRight.name

        elif lamp_type == VEHICLE_LAMP_TYPES.HighBeam:

            color_output = g_output
            veh_side_name1 = VEHICLE_SIDES.FrontLeft.name
            veh_side_name2 = VEHICLE_SIDES.FrontRight.name

        elif lamp_type == VEHICLE_LAMP_TYPES.LowBeam:

            color_output = b_output
            veh_side_name1 = VEHICLE_SIDES.FrontLeft.name
            veh_side_name2 = VEHICLE_SIDES.FrontRight.name

        elif lamp_type == VEHICLE_LAMP_TYPES.Reverse:

            color_output = b_output
            veh_side_name1 = VEHICLE_SIDES.RearLeft.name
            veh_side_name2 = VEHICLE_SIDES.RearRight.name

        if color_output:
            node_tree.links.new(switch_n.inputs[1], color_output)

            in_bounds_n = node_tree.nodes[veh_side_name1 + _IN_BOUNDS_SUFFIX]
            node_name = lamp_type.name + veh_side_name1
            node_pos = (pos_x + 185 * 2, pos_y + 18)
            mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
            nodes_for_addition.append(mult_n)

            in_bounds_n = node_tree.nodes[veh_side_name2 + _IN_BOUNDS_SUFFIX]
            node_name = lamp_type.name + veh_side_name2
            node_pos = (pos_x + 185 * 2, pos_y - 18)
            mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
            nodes_for_addition.append(mult_n)


def __init_aux_switch_nodes__(node_tree, a_output, r_output, g_output, lamp_type, pos_x, pos_y, nodes_for_addition):
    """Creation and linking of switching nodes, covering all combinations for vehicle auxiliary lamp mask.
    Combinations are created between switching nodes and uv bounding nodes which gives end float factor of mask for each of them,
    representing how much color should be added for given lamp_type per auxiliary dim type from prescribed RGBA channel.

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param a_output: alpha value of lampmask texture
    :type a_output: bpy.types.NodeSocketFloat
    :param r_output: red value of lampmask texture
    :type r_output: bpy.types.NodeSocketFloat
    :param g_output: green value of lampmask texture
    :type g_output: bpy.types.NodeSocketFloat
    :param lamp_type: lamp type for which switching nodes should be created
    :type lamp_type: AuxilliaryLampTypes
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    :param nodes_for_addition: list for nodes which should be summed and returned as result of vehicle addition color
    :type nodes_for_addition: list of bpy.types.Node
    """

    # nodes creation
    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name
    switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y)
    switch_n.width_hidden = 100
    switch_n.hide = True
    switch_n.operation = "MULTIPLY"
    switch_n.inputs[0].default_value = 0.0

    # nodes and links depending on type
    color_output = None
    if lamp_type == AUX_LAMP_TYPES.Dim:
        color_output = r_output
    elif lamp_type == AUX_LAMP_TYPES.Bright:
        color_output = g_output

    if color_output:
        node_tree.links.new(switch_n.inputs[1], color_output)

        veh_side_name1 = VEHICLE_SIDES.FrontLeft.name
        veh_side_name2 = VEHICLE_SIDES.FrontRight.name

        in_bounds_n = node_tree.nodes[veh_side_name1 + _IN_BOUNDS_SUFFIX]
        node_name = lamp_type.name + veh_side_name1
        node_pos = (pos_x + 185 * 2, pos_y + 18)
        mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
        nodes_for_addition.append(mult_n)

        in_bounds_n = node_tree.nodes[veh_side_name2 + _IN_BOUNDS_SUFFIX]
        node_name = lamp_type.name + veh_side_name2
        node_pos = (pos_x + 185 * 2, pos_y - 18)
        mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
        nodes_for_addition.append(mult_n)


def __init_traffic_light_switch_nodes__(node_tree, a_output, lamp_type, pos_x, pos_y, nodes_for_addition):
    """Creation and linking of switching nodes, covering all combinations for traffic light lamp mask.
    Combinations are created between switching nodes and uv bounding nodes which gives end float factor of mask for each of them,
    representing how much color should be added for given lamp_type per traffic light type from prescribed alpha channel.

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param a_output: alpha value of lampmask texture
    :type a_output: bpy.types.NodeSocketFloat
    :param lamp_type: lamp type for which switching nodes should be created
    :type lamp_type: TrafficLightTypes
    :param pos_x: x coordinate position
    :type pos_x: int
    :param pos_y: y coordinate position
    :type pos_y: int
    :param nodes_for_addition: list for nodes which should be summed and returned as result of vehicle addition color
    :type nodes_for_addition: list of bpy.types.Node
    """

    # nodes creation
    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name
    switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y)
    switch_n.width_hidden = 100
    switch_n.hide = True
    switch_n.operation = "MULTIPLY"
    switch_n.inputs[0].default_value = 0.0

    # nodes and links depending on type
    node_tree.links.new(switch_n.inputs[1], a_output)

    in_bounds_n = node_tree.nodes[lamp_type.name + _IN_BOUNDS_SUFFIX]
    node_name = lamp_type.name
    node_pos = (pos_x + 185 * 2, pos_y)
    mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
    nodes_for_addition.append(mult_n)


def __create_merging_node__(node_tree, node_name, position, output_0, output_1):
    """Creates and links merging node.

    :param node_tree: node tree of the mixer group
    :type node_tree: bpy.types.NodeTree
    :param node_name: name of the merging node (veh_side + lamp_type)
    :type node_name: str
    :param position: tuple of position: (pos_x, pos_y)
    :type position: (int, int)
    :param output_0: first output that should be merged
    :type output_0: bpy.types.NodeSocketFloat
    :param output_1: second output that should be merged
    :type output_1: bpy.types.NodeSocketFloat
    :return: created node
    :rtype: bpy.types.Node
    """
    mult_n = node_tree.nodes.new("ShaderNodeMath")
    mult_n.name = node_name
    mult_n.label = node_name
    mult_n.location = position
    mult_n.hide = True
    mult_n.operation = "MULTIPLY"

    node_tree.links.new(mult_n.inputs[0], output_0)
    node_tree.links.new(mult_n.inputs[1], output_1)

    return mult_n
