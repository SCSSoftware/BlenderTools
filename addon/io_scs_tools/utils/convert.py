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

# Copyright (C) 2013-2014: SCS Software

import struct
import math
from mathutils import Matrix, Quaternion, Vector
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def make_color_mtplr(prop_value):
    """Takes color values as list or tuple of three values (RGB) and creates all values within range of 0.0-1.0 and generates multiplication value.

    :param prop_value: Color values
    :type prop_value: list of float | tuple of float
    :return: Color and multiplier values
    :rtype: tuple of tuple and float
    """
    mult = 1.0
    for val in prop_value:
        if val > 1.0:
            mult = val
    if mult > 1.0:
        rgb = ((prop_value[0] / mult), (prop_value[1] / mult), (prop_value[2] / mult))
    else:
        rgb = prop_value[:3]
    return rgb, mult


def float_to_hex_string(value):
    """Takes a float and returns it as hexadecimal number in a string format.

    :param value: Value
    :type value: float
    :return: Hexadecimal value or Error string
    :rtype: str
    """
    if type(value) is float:
        data_bytes = struct.pack(">f", value)
        # binary_float = "&" + ''.join('{:02x}'.format(ord(b)) for b in data_bytes) <-- original version from Python 2.6
        binary_float = "&" + ''.join('{:02x}'.format(b) for b in data_bytes)
        return binary_float
    lprint('E float_to_hex_string: Wrong input data type! "%s" is not a float.', str(value))
    return "Value Error"


def hex_string_to_float(string):
    """Takes a string of a hexadecimal number and returns it as float number.

    :param string: Hexadecimal value
    :type string: str
    :return: Float value or Error string
    :rtype: float or str
    """
    if type(string) is str:
        if string[0] == '&':
            if len(string) == 9:
                byte = bytearray.fromhex(string[1:])
                value = struct.unpack(">f", byte)
            else:
                value = ""
                # print('\tstring 1: %s' % string)
        else:
            value = ""
            # print('\tstring 2: %s' % string)
        return float(value[0])
    lprint('E hex_string_to_float: Wrong input data type! "%s" is not a string.', string)
    return "Value Error"


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
    return Matrix.Scale(scs_globals.export_scale, 4) * scs_to_blend_matrix().inverted() * (offset_matrix.inverted() * location)


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
    return (scs_to_blend_matrix() * quat.to_matrix().to_4x4() * scs_to_blend_matrix().inverted()).to_quaternion()


def change_to_scs_quaternion_coordinates(rot):
    """Transposes quaternion rotation from Blender to SCS game engine.

    :param rot: Blender quaternion (or four floats)
    :type rot: Quaternion | list | tuple
    :return: Transposed quaternion rotation
    :rtype: Quaternion
    """
    quat = Quaternion((rot[0], rot[1], rot[2], rot[3]))
    return (scs_to_blend_matrix().inverted() * quat.to_matrix().to_4x4() * scs_to_blend_matrix()).to_quaternion()


def change_to_scs_uv_coordinates(uvs):
    """Transposes UV coordinates from Blender to SCS game engine.

    :param uvs: UV coordinates
    :type uvs: tuple | list of float
    :return: Transposed UV coordinates
    :rtype: tuple of float
    """
    return uvs[0], -uvs[1] + 1


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
    delta_matrix = zero_angle_matrix.inverted() * mat_3x3
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
    return (roll_matrix * b_matrix).to_3x3()


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