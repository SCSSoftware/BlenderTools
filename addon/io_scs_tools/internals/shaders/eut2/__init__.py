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


def get_shader(effect):
    """Gets class which represents shader for given effect inside "eut2" modules.

    :param effect: full shader name without "eut2." prefix
    :type effect: str
    :return: corresponding class for given shader effect
    :rtype: class
    """

    if effect == "fakeshadow":

        from io_scs_tools.internals.shaders.eut2.fakeshadow import Fakeshadow as Shader

    elif effect == "shadowonly":

        from io_scs_tools.internals.shaders.eut2.shadowonly import Shadowonly as Shader

    elif effect == "glass":

        from io_scs_tools.internals.shaders.eut2.glass import Glass as Shader

    elif effect.startswith("lamp"):

        if ".add.env" in effect:

            from io_scs_tools.internals.shaders.eut2.lamp.add_env import LampAddEnv as Shader

        else:

            from io_scs_tools.internals.shaders.eut2.lamp import Lamp as Shader

    elif effect.startswith("dif.spec.over.dif.opac"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_over_dif_opac import DifSpecOverDifOpac as Shader

    elif effect.startswith("dif.spec.mult.dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_mult_dif_spec import DifSpecMultDifSpec as Shader

    elif effect.startswith("dif.spec.add.env.nofresnel"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_add_env.nofresnel import DifSpecAddEnvNoFresnel as Shader

    elif effect.startswith("building.add.env."):

        from io_scs_tools.internals.shaders.eut2.building.add_env_day import BuildingAddEnvDay as Shader

    elif effect.startswith("dif.spec.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv as Shader

    elif effect.startswith("dif.spec.weight"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight import DifSpecWeight as Shader

    elif effect.startswith("dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec as Shader

    elif effect.startswith("dif"):

        from io_scs_tools.internals.shaders.eut2.dif import Dif as Shader

    else:

        return None

    return Shader