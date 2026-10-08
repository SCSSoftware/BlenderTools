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

# Copyright (C) 2015-2021: SCS Software
# Copyright (C) 2024-2026: Michaleczeq


def get_shader(effect):
    """Gets class which represents shader for given effect inside "eut2" modules.

    :param effect: full shader name without "eut2." prefix
    :type effect: str
    :return: corresponding class for given shader effect
    :rtype: class
    """

    if effect == "none":
        from .none import NNone as Shader

    elif effect.startswith("water"):
        from .water import Water as Shader

    elif effect == "window.lit":
        from .window.lit import WindowLit as Shader

    elif effect == "interior.lit" or effect == "interior.spatial.lit":
        from .interior import InteriorLit as Shader

    elif effect == "interior.curtain.lit":
        from .interior.curtain import InteriorCurtain as Shader

    elif effect == "reflective":
        from .reflective import Reflective as Shader

    elif effect == "sign":
        from .sign import Sign as Shader

    elif effect == "grass":
        from .grass import Grass as Shader

    elif effect.startswith("leaves"):
        from .leaves import Leaves as Shader

    elif effect.startswith("glass"):
        from .glass import Glass as Shader

    elif effect == "mlaaweight":
        from .mlaaweight import MlaaWeight as Shader

    elif effect.startswith("fakeshadow"):
        from .fakeshadow import Fakeshadow as Shader

    elif effect.startswith("shadowonly"):
        from .shadowonly import Shadowonly as Shader

    elif effect.startswith("particle"):
        from .particle import Particle as Shader

    elif effect.startswith("lightmap.night"):
        from .lightmap.night import LightMapNight as Shader

    elif effect.startswith("light.tex"):
        from .light_tex import LightTex as Shader

    elif effect.startswith("light"):
        from .light import Light as Shader

    elif effect.startswith("retroreflective"):
        from .retroreflective import Retroreflective as Shader

    elif effect.startswith("unlit.tex"):
        from .unlit_tex import UnlitTex as Shader

    elif effect.startswith("unlit.vcol.tex"):
        from .unlit_vcol_tex import UnlitVcolTex as Shader

    elif effect.startswith("truckpaint"):
        if ".airbrush" in effect:
            from .truckpaint.airbrush import TruckpaintAirbrush as Shader

        elif ".colormask" in effect:
            from .truckpaint.colormask import TruckpaintColormask as Shader

        else:
            from .truckpaint import Truckpaint as Shader

    elif effect.startswith("lamp"):
        if ".add.env" in effect:
            from .lamp.add_env import LampAddEnv as Shader

        else:
            from .lamp import Lamp as Shader

    elif effect.startswith("sky.bottom"):
        from .sky.bottom import SkyBottom as Shader

    elif effect.startswith("sky"):
        from .sky import Sky as Shader

    elif effect.startswith("shadowmap"):
        from .shadowmap import Shadowmap as Shader

    elif effect.startswith("flare"):
        from .flare import Flare as Shader

    elif effect.startswith("decalshadow"):
        from .decalshadow import Decalshadow as Shader
    
    elif effect.startswith("dif.spec.over.dif.opac.add.env"):
        from .dif_spec_over_dif_opac_add_env import DifSpecOverDifOpacAddEnv as Shader

    elif effect.startswith("dif.spec.over.dif.opac"):
        from .dif_spec_over_dif_opac import DifSpecOverDifOpac as Shader
        
    elif effect.startswith("dif.spec.amod.dif.spec.add.env"):
        from .dif_spec_amod_dif_spec_add_env import DifSpecAmodDifSpecAddEnv as Shader
        
    elif effect.startswith("dif.spec.amod.dif.spec"):
        from .dif_spec_amod_dif_spec import DifSpecAmodDifSpec as Shader

    elif effect.startswith("dif.spec.mult.dif.spec.iamod.dif.spec"):
        from .dif_spec_mult_dif_spec_iamod_dif_spec import DifSpecMultDifSpecIamodDifSpec as Shader

    elif effect.startswith("dif.spec.mult.dif.iamod.dif.add.env"):
        from .dif_spec_mult_dif_iamod_dif_add_env import DifSpecMultDifIamodDifAddEnv as Shader

    elif effect.startswith("dif.spec.mult.dif.spec.add.env"):
        from .dif_spec_mult_dif_spec.add_env import DifSpecMultDifSpecAddEnv as Shader

    elif effect.startswith("dif.spec.mult.dif.spec"):
        from .dif_spec_mult_dif_spec import DifSpecMultDifSpec as Shader

    elif effect.startswith("dif.spec.add.env.over.dif.opac"):
        from .dif_spec_add_env_over_dif_opac import DifSpecAddEnvOverDifOpac as Shader

    elif effect.startswith("dif.spec.add.env.nofresnel"):
        from .dif_spec_add_env.nofresnel import DifSpecAddEnvNoFresnel as Shader

    elif effect.startswith("building.add.env"):
        from .building.add_env_day import BuildingAddEnvDay as Shader

    elif effect.startswith("building"):
        from .building.day import BuildingDay as Shader

    elif effect.startswith("dif.weight.dif"):
        from .dif_weight_dif import DifWeightDif as Shader

    elif effect.startswith("dif.spec.add.env"):
        from .dif_spec_add_env import DifSpecAddEnv as Shader

    elif effect.startswith("dif.spec.fade.dif.spec"):
        from .dif_spec_fade_dif_spec import DifSpecFadeDifSpec as Shader

    elif effect.startswith("dif.spec.fade.mult.dif.spec"):
        from .dif_spec_fade_mult_dif_spec import DifSpecFadeMultDifSpec as Shader

    elif effect.startswith("dif.spec.oclu.add.env"):
        from .dif_spec_oclu_add_env import DifSpecOcluAddEnv as Shader

    elif effect.startswith("dif.spec.oclu.weight.add.env"):
        from .dif_spec_oclu_weight_add_env import DifSpecOcluWeightAddEnv as Shader

    elif effect.startswith("dif.spec.weight.add.env.nofresnel"):
        from .dif_spec_weight_add_env.nofresnel import DifSpecWeightAddEnvNoFresnel as Shader

    elif effect.startswith("dif.spec.weight.add.env"):
        from .dif_spec_weight_add_env import DifSpecWeightAddEnv as Shader

    elif effect.startswith("dif.spec.weight.weight.dif.spec.weight"):
        from .dif_spec_weight_weight_dif_spec_weight import DifSpecWeightWeightDifSpecWeight as Shader

    elif effect.startswith("dif.spec.weight.mask.dif.spec.weight"):
        from .dif_spec_weight_mask_dif_spec_weight import DifSpecWeightMaskDifSpecWeight as Shader

    elif effect.startswith("dif.spec.weight.mult2.weight2"):
        from .dif_spec_weight_mult2_weight2 import DifSpecWeightMult2Weight2 as Shader

    elif effect.startswith("dif.spec.weight.mult2.mask2"):
        from .dif_spec_weight_mult2_mask2 import DifSpecWeightMult2Mask2 as Shader

    elif effect.startswith("dif.spec.weight.mult2"):
        from .dif_spec_weight_mult2 import DifSpecWeightMult2 as Shader

    elif effect.startswith("dif.spec.weight"):
        from .dif_spec_weight import DifSpecWeight as Shader

    elif effect.startswith("dif.spec.oclu"):
        from .dif_spec_oclu import DifSpecOclu as Shader

    elif effect.startswith("dif.spec"):
        from .dif_spec import DifSpec as Shader

    elif effect.startswith("dif.lum.spec"):
        from .dif_lum_spec import DifLumSpec as Shader

    elif effect.startswith("dif.lum"):
        from .dif_lum import DifLum as Shader

    elif effect.startswith("dif.anim"):
        from .dif_anim import DifAnim as Shader

    elif effect.startswith("dif"):
        from .dif import Dif as Shader

    elif effect.startswith("billboard"):
        from .billboard import Billboard as Shader

    elif effect.startswith("baked"):
        if ".add.env" in effect:
            from .baked.add_env import BakedSpecAddEnv as Shader

        elif ".spec" in effect:
            from .baked.spec import BakedSpec as Shader

        else:
            from .baked import Baked as Shader

    else:
        return None

    return Shader
