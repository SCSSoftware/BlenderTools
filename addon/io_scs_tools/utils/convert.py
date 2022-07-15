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

# Copyright (C) 2013-2021: SCS Software

import struct
import math
import re
from mathutils import Matrix, Quaternion, Vector, Color
from io_scs_tools.consts import Colors as _COL_consts
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import get_scs_inventories as _get_scs_inventories

_FLOAT_STRUCT = struct.Struct(">f")
_BYTE_STRUCT = struct.Struct(">I")


def linear_to_srgb(value):
    """Converts linear color to srgb colorspace. Function can convert single float or list of floats.
    NOTE: taken from game code

    :param value: list of floats or float
    :type value: float | collections.Iterable[float]
    :return: converted color
    :rtype: float | list[float]
    """

    is_float = isinstance(value, float)
    if is_float:
        vals = [value]
    else:
        vals = list(value)

    for i, v in enumerate(vals):
        if v <= 0.0031308:
            vals[i] = 12.92 * v
        else:
            a = 0.055
            vals[i] = (v ** (1.0 / 2.4) * (1.0 + a)) - a

    if is_float:
        return vals[0]
    else:
        return vals


def srgb_to_linear(value):
    """Converts srgb color to linear colorspace. Function can convert single float or list of floats.
    NOTE: taken from game code

    :param value: list of floats or float
    :type value: float | collections.Iterable[float]
    :return: converted color
    :rtype: float | list[float]
    """

    is_float = isinstance(value, float)
    if is_float:
        vals = [value]
    else:
        vals = list(value)

    for i, v in enumerate(vals):

        if v <= 0.04045:
            vals[i] = v / 12.92
        else:
            a = 0.055
            vals[i] = ((v + a) / (1.0 + a)) ** 2.4

    if is_float:
        return vals[0]
    else:
        return vals


def pre_gamma_corrected_col(color):
    """Pre applys gamma decoding to color.
    Usefull for preparation of color for Blender color pickers/nodes,
    if we want Blender to output raw value as it was given to color picker/node

    :param color: color which should be pre applied
    :type color: mathutils.Color
    :return: pre applied gamma decoding
    :rtype: mathutils.Color
    """

    c = Color(color)

    for i in range(3):
        c[i] **= _COL_consts.gamma

    return c


def to_node_color(color, from_linear=False):
    """Gets color ready for assigning to Blender nodes.
    1. Sets minimal HSV value attribute for rendering
    2. Applies pre gamma correction
    3. Returns it as tuple of 4 floats RGBA

    :param color: color to be converted for usage in node
    :type color: mathutils.Color | collections.Iterable[float]
    :param from_linear: should color first be converted from linear space?
    :type from_linear: bool
    :return: RGBA as tuple of floats
    :rtype: tuple[float]
    """

    srgb_color = color
    if from_linear:
        srgb_color = linear_to_srgb(color)

    c = Color(srgb_color[:3])  # copy color so changes won't reflect on original passed color object

    c = pre_gamma_corrected_col(c)

    # set minimal value for Blender to use it in rendering
    if c.v == 0:
        c.v = 0.000001  # this is the smallest value Blender still uses for rendering

    return tuple(c) + (1,)


def aux_to_node_color(aux_prop, from_index=0):
    """Converts auxiliary item to color ready for assigning to Blender nodes.
    1. Converts auxiliary item to color
    2. Sets minimal HSV value attribute for rendering
    3. Applies pre gamma correction
    4. Returns it as tuple of 4 floats RGBA

    :param aux_prop:
    :type aux_prop: bpy.props.IDPropertyGroup
    :param from_index: index in aux property collection from which to start taking RGB values
    :type from_index: int
    :return: RGBA as tuple of floats
    :rtype: tuple[float]
    """

    col = []
    for i, aux_item in enumerate(aux_prop):

        if from_index <= i < from_index + 3:
            col.append(max(0, aux_item['value']))

    # just make sure to fill empty RGB channels so game won't complain
    if len(col) < 3:
        col.extend([0, ] * (3 - len(col)))
        lprint("D Filling 0.0 for missing auxiliary item values of RGB color presentation (Actual/needed count: %s/3)",
               (len(aux_prop),))

    return to_node_color(col)


def float_array_to_hex_string(value):
    """Takes a float array and returns it as hexadecimal number in a string format.
    There are direct implementations for array sizes of 3, 4, 2.

    For speed reasons we do not have any check on the value, so beware!

    :param value: Value
    :type value: iter
    :return: Hexadecimal string value
    :rtype: str
    """

    items_count = len(value)
    if items_count == 3:
        return'&%s  &%s  &%s' % (_FLOAT_STRUCT.pack(value[0]).hex(),
                                 _FLOAT_STRUCT.pack(value[1]).hex(),
                                 _FLOAT_STRUCT.pack(value[2]).hex())
    elif items_count == 4:
        return '&%s  &%s  &%s  &%s' % (_FLOAT_STRUCT.pack(value[0]).hex(),
                                       _FLOAT_STRUCT.pack(value[1]).hex(),
                                       _FLOAT_STRUCT.pack(value[2]).hex(),
                                       _FLOAT_STRUCT.pack(value[3]).hex())
    elif items_count == 2:
        return '&%s  &%s' % (_FLOAT_STRUCT.pack(value[0]).hex(),
                             _FLOAT_STRUCT.pack(value[1]).hex())
    else:
        return '  '.join([float_to_hex_string(x) for x in value])


def float_to_hex_string(value):
    """Takes a float and returns it as hexadecimal number in a string format.

    For speed reasons we do not have any check on the value, so beware!

    :param value: Value
    :type value: float
    :return: Hexadecimal string value
    :rtype: str
    """
    return '&%s' % _FLOAT_STRUCT.pack(value).hex()


def string_to_number(string):
    """Converts string to number. It accepts hex interpretation or decimal.
    NOTE: no safety checks if string is really a number string

    :param string: hex or decimal string carrying number
    :type string: str
    :return: float or int depending on passed string. It will result in int in case if input string will be decimal value without dot
    :rtype: float | int
    """

    if string[0] == '&':
        val = hex_string_to_float(string)
    elif "." in string:
        val = float(string)
    else:
        val = int(string)

    return val


def hex_string_to_float(string):
    """Takes a string of a hexadecimal number and returns it as float number.

    For speed reasons we do not have any check on the input string, so beware!

    :param string: Hexadecimal value in format &XXxxXXxx
    :type string: str
    :return: Float value
    :rtype: float
    """
    return _FLOAT_STRUCT.unpack(bytearray.fromhex(string[1:]))[0]


def scs_to_blend_matrix():
    """Transformation matrix for space conversion from SCS coordinate system to Blender's.

    :return: Transformation matrix
    :rtype: Matrix
    """
    return Matrix.Rotation(math.pi / 2, 4, 'X')


def convert_location_to_scs(location, offset_matrix=Matrix()):
    """Takes a vector or list of three floats and returns its coordinates transposed for SCS game engine.
    \rIf an "offset_matrix" is provided it is used to offset coordinates.

    :param location: Location (or three floats)
    :type location: Vector | list | tuple
    :param offset_matrix: Offset
    :type offset_matrix: Matrix
    :return: Transposed location
    :rtype: Vector
    """
    scs_globals = _get_scs_globals()
    return Matrix.Scale(scs_globals.export_scale, 4) @ scs_to_blend_matrix().inverted() @ (offset_matrix.inverted() @ location)


def change_to_scs_xyz_coordinates(vec, scale):
    """Transposes location from Blender to SCS game engine.

    :param vec: Location (or three floats)
    :type vec: Vector | list | tuple
    :param scale: Scale
    :type scale: Vector
    :return: Transposed location
    :rtype: tuple of float
    """
    return vec[0] * scale, (vec[2] * -scale), (vec[1] * scale)


def change_to_blender_quaternion_coordinates(rot):
    """Transposes quaternion rotation from SCS game engine to Blender.

    :param rot: SCS quaternion (or four floats)
    :type rot: Quaternion | list | tuple
    :return: Transposed quaternion rotation
    :rtype: Quaternion
    """
    quat = Quaternion((rot[0], rot[1], rot[2], rot[3]))
    return (scs_to_blend_matrix() @ quat.to_matrix().to_4x4() @ scs_to_blend_matrix().inverted()).to_quaternion()


def change_to_scs_quaternion_coordinates(rot):
    """Transposes quaternion rotation from Blender to SCS game engine.

    :param rot: Blender quaternion (or four floats)
    :type rot: Quaternion | list | tuple
    :return: Transposed quaternion rotation
    :rtype: Quaternion
    """
    quat = Quaternion((rot[0], rot[1], rot[2], rot[3]))
    return (scs_to_blend_matrix().inverted() @ quat.to_matrix().to_4x4() @ scs_to_blend_matrix()).to_quaternion()


def change_to_scs_uv_coordinates(uvs):
    """Transposes UV coordinates from Blender to SCS game engine.

    :param uvs: UV coordinates
    :type uvs: tuple | list of float
    :return: Transposed UV coordinates
    :rtype: tuple of float
    """
    return uvs[0], 1 - uvs[1]


def get_scs_transformation_components(matrix):
    """Takes an matrix and returns its transformations for SCS game engine.

    :param matrix: Matrix
    :type matrix: Matrix
    :return: Location (vector), rotation (quaternion), scale (vector)
    :rtype: tuple of Vector
    """
    export_scale = _get_scs_globals().export_scale
    loc = convert_location_to_scs(matrix.to_translation())
    mat_qua = change_to_scs_quaternion_coordinates(matrix.to_quaternion())
    qua = (mat_qua.w, mat_qua.x, mat_qua.y, mat_qua.z)
    sca = matrix.to_scale()
    sca = (sca.x * export_scale, sca.z * export_scale, sca.y * export_scale)
    return loc, qua, sca


def mat3_to_vec_roll(mat):
    """Computes rotation axis and its roll from a Matrix.

    :param mat: Matrix
    :type mat: Matrix
    :return: Rotation axis and roll
    :rtype: Vector and float
    """
    mat_3x3 = mat.to_3x3()
    # print('  mat_3x3:\n%s' % str(mat_3x3))
    axis = Vector(mat_3x3.col[1]).normalized()
    # print('  axis:\n%s' % str(axis))
    # print('  mat_3x3[2]:\n%s' % str(mat_3x3.col[2]))

    zero_angle_matrix = vec_roll_to_mat3(axis, 0)
    delta_matrix = zero_angle_matrix.inverted() @ mat_3x3
    angle = math.atan2(delta_matrix.col[2][0], delta_matrix.col[2][2])
    return axis, angle


def vec_roll_to_mat3(axis, roll):
    """Computes 3x3 Matrix from rotation axis and its roll.

    :param axis: Rotation
    :type axis: Vector
    :param roll: Roll
    :type roll: float
    :return: 3x3 Matrix
    :rtype: Matrix
    """
    nor = axis.normalized()
    target = Vector((0, 1, 0))
    axis = target.cross(nor)

    if axis.dot(axis) > 1.0e-9:
        axis.normalize()
        theta = _math_utils.angle_normalized_v3v3(target, nor)
        b_matrix = Matrix.Rotation(theta, 4, axis)
    else:
        if target.dot(nor) > 0:
            up_or_down = 1.0
        else:
            up_or_down = -1.0

        b_matrix = Matrix()
        b_matrix[0] = (up_or_down, 0, 0, 0)
        b_matrix[1] = (0, up_or_down, 0, 0)
        b_matrix[2] = (0, 0, 1, 0)
        b_matrix[3] = (0, 0, 0, 1)

    roll_matrix = Matrix.Rotation(roll, 4, nor)
    return (roll_matrix @ b_matrix).to_3x3()


def str_to_int(str_value):
    """Converts string to integer if string can not be converted None is returned

    :param str_value: string to convert to integer
    :type str_value: int
    :return: int value if string is parsable otherwise None
    :rtype: int | None
    """
    try:
        value = int(str_value)
    except ValueError:
        value = None

    return value


def split_hookup_id(hookup_id):
    """Takes a raw Hookup ID string and returns hookup id and if exists, parsed payload.

    :param hookup_id: hookup ID (as saved in PIM)
    :type hookup_id: str
    :return: Dictionary of payload properties (property names as keys and property values as values)
    :rtype: (str, dict[str, str])
    """

    hookup_payload = {}

    hookup_splits = re.split(r'#', hookup_id)
    if len(hookup_splits) == 2:
        for prop_object in re.split(r';', hookup_splits[1]):
            prop_split = re.split(r':', prop_object)
            if len(prop_split) == 2:
                hookup_payload[prop_split[0]] = prop_split[1]

    return hookup_splits[0], hookup_payload


def hookup_id_to_hookup_name(hookup_id):
    """Takes a Hookup ID string and returns the whole Hookup Name
    or original ID string if it doesn't exists in Hookup inventory.

    :param hookup_id: Hookup ID (as saved in PIM)
    :type hookup_id: str
    :return: Hookup Name (as used in Blender UI)
    :rtype: str
    """
    hookup_name = hookup_id
    for rec in _get_scs_inventories().hookups:
        rec_id = rec.name.split(':', 1)[1].strip()
        if rec_id == hookup_id:
            hookup_name = rec.name
            break

    return hookup_name


def hookup_name_to_hookup_id(hookup_string):
    """Takes hookup name from model locator hookup property and returns hookup id used for export.

    :param hookup_string: hookup name string from model locator hookup property "flare_vehicle : flare.vehicle.high_beam"
    :type hookup_string: str
    :return: hookup id
    :rtype: str | None
    """
    hookup = None
    if hookup_string != "" and ":" in hookup_string:
        hookup = hookup_string.split(':', 1)[1].strip()

    return hookup
