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

# Copyright (C) 2021: SCS Software

import math


def get_material_luminosity(luminance_boost):
    """Gets perceptual material luminosity from luminance boost given in nits.

    :param luminance_boost: luminance boost in nits
    :type luminance_boost: float
    :return: perceptual material lumionosity
    :rtype: float
    """

    scale = 1.0
    if luminance_boost < 0.0:
        scale = abs(luminance_boost)
    else:
        MIDGRAY_NITS = 50.0
        if luminance_boost == 0:
            desired_nits = MIDGRAY_NITS
        else:
            desired_nits = luminance_boost

        if desired_nits <= MIDGRAY_NITS:
            scale = 0.25 * (desired_nits / MIDGRAY_NITS)
        else:
            MAX_LOG2_SCALE = 10.0
            normalized = min(1.0, max(0.0, math.log2(desired_nits / MIDGRAY_NITS) / MAX_LOG2_SCALE))
            perceptual = 0.5 + 0.5 * normalized
            scale = perceptual * perceptual

    return scale


def get_fresnel_v1(bias, scale, default_bias):
    """Gets fresnel as in-game, if scale is -1 use given bias from material otherwise default bias.

    :param bias: material_fresnel[0]
    :type bias: float
    :param scale: material_fresnel[1]
    :type scale: float
    :param default_bias: default bias to use if scale is not -1
    :type default_bias: float
    :return: recalculated fresnel
    :rtype: float, float
    """

    if scale == -1.0:
        f0 = bias
    else:
        f0 = default_bias

    return f0, 1.0


def get_fresnel_glass(bias, scale):
    """Get fresnel params for the glass shader.

    :param bias: material_fresnel[0]
    :type bias: float
    :param scale: material_fresnel[1]
    :type scale: float
    :return: recalculated fresnel
    :rtype: float, float
    """

    return get_fresnel_v1(bias, scale, 0.07)


def get_fresnel_truckpaint(bias, scale):
    """Get fresnel params for the truckpaint shader.

    :param bias: material_fresnel[0]
    :type bias: float
    :param scale: material_fresnel[1]
    :type scale: float
    :return: recalculated fresnel
    :rtype: float, float
    """

    return get_fresnel_v1(bias, scale, 0.025)


def get_fresnel_window(bias, scale):
    """Get fresnel params for the window shader.

    :param bias: material_fresnel[0]
    :type bias: float
    :param scale: material_fresnel[1]
    :type scale: float
    :return: recalculated fresnel
    :rtype: float, float
    """

    return get_fresnel_v1(bias, scale, 0.14)
