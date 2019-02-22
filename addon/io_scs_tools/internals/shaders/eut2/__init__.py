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

    if effect == "none":

        from io_scs_tools.internals.shaders.eut2.none import NNone as Shader

    elif effect == "water":

        from io_scs_tools.internals.shaders.eut2.water import Water as Shader

    elif effect == "window.day":

        from io_scs_tools.internals.shaders.eut2.window.day import WindowDay as Shader

    elif effect == "window.night":

        from io_scs_tools.internals.shaders.eut2.window.night import WindowNight as Shader

    elif effect == "reflective":

        from io_scs_tools.internals.shaders.eut2.reflective import Reflective as Shader

    elif effect == "sign":

        from io_scs_tools.internals.shaders.eut2.sign import Sign as Shader

    elif effect == "grass":

        from io_scs_tools.internals.shaders.eut2.grass import Grass as Shader

    elif effect == "glass":

        from io_scs_tools.internals.shaders.eut2.glass import Glass as Shader

    elif effect == "mlaaweight":

        from io_scs_tools.internals.shaders.eut2.mlaaweight import MlaaWeight as Shader

    elif effect.startswith("fakeshadow"):

        from io_scs_tools.internals.shaders.eut2.fakeshadow import Fakeshadow as Shader

    elif effect.startswith("shadowonly"):

        from io_scs_tools.internals.shaders.eut2.shadowonly import Shadowonly as Shader

    elif effect.startswith("lightmap.night"):

        from io_scs_tools.internals.shaders.eut2.lightmap.night import LightMapNight as Shader

    elif effect.startswith("light.tex"):

        from io_scs_tools.internals.shaders.eut2.light_tex import LightTex as Shader

    elif effect.startswith("retroreflective"):

        from io_scs_tools.internals.shaders.eut2.retroreflective import Retroreflective as Shader

    elif effect.startswith("unlit.tex"):

        from io_scs_tools.internals.shaders.eut2.unlit_tex import UnlitTex as Shader

    elif effect.startswith("unlit.vcol.tex"):

        from io_scs_tools.internals.shaders.eut2.unlit_vcol_tex import UnlitVcolTex as Shader

    elif effect.startswith("truckpaint"):

        if ".airbrush" in effect:

            from io_scs_tools.internals.shaders.eut2.truckpaint.airbrush import TruckpaintAirbrush as Shader

        elif ".colormask" in effect:

            from io_scs_tools.internals.shaders.eut2.truckpaint.colormask import TruckpaintColormask as Shader

        else:

            from io_scs_tools.internals.shaders.eut2.truckpaint import Truckpaint as Shader

    elif effect.startswith("lamp"):

        if ".add.env" in effect:

            from io_scs_tools.internals.shaders.eut2.lamp.add_env import LampAddEnv as Shader

        else:

            from io_scs_tools.internals.shaders.eut2.lamp import Lamp as Shader

    elif effect.startswith("sky"):

        from io_scs_tools.internals.shaders.eut2.sky import Sky as Shader

    elif effect.startswith("shadowmap"):

        from io_scs_tools.internals.shaders.eut2.shadowmap import Shadowmap as Shader

    elif effect.startswith("flare"):

        from io_scs_tools.internals.shaders.eut2.flare import Flare as Shader

    elif effect.startswith("decalshadow"):

        from io_scs_tools.internals.shaders.eut2.decalshadow import Decalshadow as Shader

    elif effect.startswith("dif.spec.over.dif.opac"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_over_dif_opac import DifSpecOverDifOpac as Shader

    elif effect.startswith("dif.spec.mult.dif.spec.iamod.dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_mult_dif_spec_iamod_dif_spec import DifSpecMultDifSpecIamodDifSpec as Shader

    elif effect.startswith("dif.spec.mult.dif.spec.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_mult_dif_spec.add_env import DifSpecMultDifSpecAddEnv as Shader

    elif effect.startswith("dif.spec.mult.dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_mult_dif_spec import DifSpecMultDifSpec as Shader

    elif effect.startswith("dif.spec.add.env.nofresnel"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_add_env.nofresnel import DifSpecAddEnvNoFresnel as Shader

    elif effect.startswith("building.add.env.day"):

        from io_scs_tools.internals.shaders.eut2.building.add_env_day import BuildingAddEnvDay as Shader

    elif effect.startswith("building.lvcol.day"):

        from io_scs_tools.internals.shaders.eut2.building.lvcol_day import BuildingLvcolDay as Shader

    elif effect.startswith("building.day"):

        from io_scs_tools.internals.shaders.eut2.building.day import BuildingDay as Shader

    elif effect.startswith("dif.weight.dif"):

        from io_scs_tools.internals.shaders.eut2.dif_weight_dif import DifWeightDif as Shader

    elif effect.startswith("dif.spec.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_add_env import DifSpecAddEnv as Shader

    elif effect.startswith("dif.spec.fade.dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_fade_dif_spec import DifSpecFadeDifSpec as Shader

    elif effect.startswith("dif.spec.oclu.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_oclu_add_env import DifSpecOcluAddEnv as Shader

    elif effect.startswith("dif.spec.oclu.weight.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_oclu_weight_add_env import DifSpecOcluWeightAddEnv as Shader

    elif effect.startswith("dif.spec.weight.add.env"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight_add_env import DifSpecWeightAddEnv as Shader

    elif effect.startswith("dif.spec.weight.weight.dif.spec.weight"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight_weight_dif_spec_weight import DifSpecWeightWeightDifSpecWeight as Shader

    elif effect.startswith("dif.spec.weight.mult2.weight2"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight_mult2_weight2 import DifSpecWeightMult2Weight2 as Shader

    elif effect.startswith("dif.spec.weight.mult2"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight_mult2 import DifSpecWeightMult2 as Shader

    elif effect.startswith("dif.spec.weight"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_weight import DifSpecWeight as Shader

    elif effect.startswith("dif.spec.oclu"):

        from io_scs_tools.internals.shaders.eut2.dif_spec_oclu import DifSpecOclu as Shader

    elif effect.startswith("dif.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_spec import DifSpec as Shader

    elif effect.startswith("dif.lum.spec"):

        from io_scs_tools.internals.shaders.eut2.dif_lum_spec import DifLumSpec as Shader

    elif effect.startswith("dif.lum"):

        from io_scs_tools.internals.shaders.eut2.dif_lum import DifLum as Shader

    elif effect.startswith("dif.anim"):

        from io_scs_tools.internals.shaders.eut2.dif_anim import DifAnim as Shader

    elif effect.startswith("dif"):

        from io_scs_tools.internals.shaders.eut2.dif import Dif as Shader

    else:

        return None

    return Shader
