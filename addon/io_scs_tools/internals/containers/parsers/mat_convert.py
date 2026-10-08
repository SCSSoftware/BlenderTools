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

# Copyright (C) 2025: SCS Software

# Converting script based on the mwl4 script from https://github.com/mwl4/ConverterPIX/

from ....utils.printout import lprint


class AttributeConvert:
    def __init__(self, name, value_count, start_index):
        self.name = name
        self.value_count = value_count
        self.start_index = start_index

map_to_material = {
    "additional_ambient": [AttributeConvert("add_ambient", 1, 0)],
    "glass_tint_color": [AttributeConvert("tint", 3, 0)],
    "glass_tint_opacity": [AttributeConvert("tint_opacity", 1, 0)],
    "shadowmap_bias": [AttributeConvert("shadow_bias", 1, 0)],
    "paintjob_base_color": [AttributeConvert("aux[8]", 3, 0)],
    "specular_secondary": [AttributeConvert("aux[3]", 4, 0)],
    "shininess_secondary": [AttributeConvert("aux[3]", 4, 3)],
    "reflection_secondary": [AttributeConvert("reflection2", 1, 0)],
    "lod_selector": [AttributeConvert("aux[1]", 1, 0)],
    "shadow_offset": [AttributeConvert("aux[0]", 1, 0)],
    "amod_decal_blending_factors": [AttributeConvert("aux[0]", 2, 0)],
    "texgen_0_gen": [AttributeConvert("aux[0]", 4, 0)],
    "texgen_0_rot": [AttributeConvert("aux[0]", 4, 2)],
    "texgen_1_gen": [AttributeConvert("aux[1]", 4, 0)],
    "texgen_1_rot": [AttributeConvert("aux[1]", 4, 2)],
    "far_color": [AttributeConvert("aux[2]", 4, 0)],
    "far_specular_power": [AttributeConvert("aux[2]", 4, 3)],
    "depth_bias": [AttributeConvert("aux[0]", 1, 0)],
    "luminance_output": [AttributeConvert("aux[5]", 2, 0)],
    "luminance_night": [AttributeConvert("aux[5]", 2, 1)],
    "interior_atlas_dimensions": [AttributeConvert("aux[1]", 2, 0)],
    "interior_glass_color": [AttributeConvert("aux[2]", 4, 0)],
    "interior_unit_room_dimensions": [AttributeConvert("aux[0]", 2, 0)],
    "water_distances": [AttributeConvert("aux[0]", 3, 0)],
    "water_near_color": [AttributeConvert("aux[1]", 3, 0)],
    "water_horizon_color": [AttributeConvert("aux[2]", 3, 0)],
    "water_layer_0_yaw": [AttributeConvert("aux[3]", 4, 0)],
    "water_layer_0_speed": [AttributeConvert("aux[3]", 4, 1)],
    "water_layer_0_scale": [AttributeConvert("aux[3]", 4, 2)],
    "water_layer_1_yaw": [AttributeConvert("aux[4]", 4, 0)],
    "water_layer_1_speed": [AttributeConvert("aux[4]", 4, 1)],
    "water_layer_1_scale": [AttributeConvert("aux[4]", 4, 2)],
    "water_mirror": [AttributeConvert("aux[5]", 1, 0)],
    "animsheet_cfg_fps": [AttributeConvert("aux[0]", 3, 0)],
    "animsheet_cfg_frames_row": [AttributeConvert("aux[0]", 3, 1)],
    "animsheet_cfg_frames_total": [AttributeConvert("aux[0]", 3, 2)],
    "animsheet_frame_width": [AttributeConvert("aux[1]", 2, 0)],
    "animsheet_frame_height": [AttributeConvert("aux[1]", 2, 1)],
    "detail_fadeout_from": [AttributeConvert("aux[5]", 4, 0)],
    "detail_fadeout_range": [AttributeConvert("aux[5]", 4, 1)],
    "detail_blend_bias": [AttributeConvert("aux[5]", 4, 2)],
    "detail_uv_scale": [AttributeConvert("aux[5]", 4, 3)],
    "animation_speed": [AttributeConvert("aux[0]", 1, 0)],
    "showroom_r_color": [AttributeConvert("aux[0]", 1, 0)],
    "showroom_speed": [AttributeConvert("aux[4]", 3, 0)],
    "flake_uvscale": [AttributeConvert("aux[5]", 4, 0)],
    "flake_shininess": [AttributeConvert("aux[5]", 4, 1)],
    "flake_clearcoat_rolloff": [AttributeConvert("aux[5]", 4, 2)],
    "flake_vratio": [AttributeConvert("aux[5]", 4, 3)],
    "flake_color": [AttributeConvert("aux[6]", 4, 0)],
    "flake_density": [AttributeConvert("aux[6]", 4, 3)],
    "flip_color": [AttributeConvert("aux[7]", 4, 0)],
    "flip_strength": [AttributeConvert("aux[7]", 4, 3)],
    "mix00_diffuse_secondary": [AttributeConvert("aux[0]", 3, 0)],
    "mult_uvscale": [AttributeConvert("aux[5]", 4, 0)],
    "mult_uvscale_secondary": [AttributeConvert("aux[5]", 4, 2)],
    "sheet_frame_size_r": [AttributeConvert("aux[0]", 4, 0)],
    "sheet_frame_size_g": [AttributeConvert("aux[0]", 4, 2)],
    "sheet_frame_size_b": [AttributeConvert("aux[1]", 4, 0)],
    "sheet_frame_size_a": [AttributeConvert("aux[1]", 4, 2)],
    "paintjob_r_color": [AttributeConvert("aux[5]", 3, 0)],
    "paintjob_g_color": [AttributeConvert("aux[6]", 3, 0)],
    "paintjob_b_color": [AttributeConvert("aux[7]", 3, 0)],
}

map_to_effect = {
    "add_ambient": [AttributeConvert("additional_ambient", 1, 0)],
    "shadow_bias": [AttributeConvert("shadowmap_bias", 1, 0)],
    "tint": [AttributeConvert("glass_tint_color", 3, 0)],
    "tint_opacity": [AttributeConvert("glass_tint_opacity", 1, 0)],
    "reflection2": [AttributeConvert("reflection_secondary", 1, 0)],
}

map_to_effect_truckpaint = {
    "aux[5]": [AttributeConvert("paintjob_r_color", 3, 0)],
    "aux[6]": [AttributeConvert("paintjob_g_color", 3, 0)],
    "aux[7]": [AttributeConvert("paintjob_b_color", 3, 0)],
    "aux[8]": [AttributeConvert("paintjob_base_color", 3, 0)],
}

map_to_effect_flipflake = {
    "aux[5]": [
        AttributeConvert("flake_uvscale", 1, 0),
        AttributeConvert("flake_shininess", 1, 1),
        AttributeConvert("flake_clearcoat_rolloff", 1, 2),
        AttributeConvert("flake_vratio", 1, 3),
    ],
    "aux[6]": [
        AttributeConvert("flake_color", 3, 0),
        AttributeConvert("flake_density", 1, 3),
    ],
    "aux[7]": [
        AttributeConvert("flip_color", 3, 0),
        AttributeConvert("flip_strength", 1, 3),
    ],
    "aux[8]": [AttributeConvert("paintjob_base_color", 3, 0)],
}

map_to_effect_weight = {
    "aux[3]": [
        AttributeConvert("specular_secondary", 3, 0),
        AttributeConvert("shininess_secondary", 1, 3),
    ]
}

map_to_effect_leaves = {
    "aux[0]": [AttributeConvert("shadow_offset", 1, 0)],
    "aux[1]": [AttributeConvert("lod_selector", 3, 0)],
}

map_to_effect_tg0tg1 = {
    "aux[0]": [
        AttributeConvert("texgen_0_gen", 2, 0),
        AttributeConvert("texgen_0_rot", 1, 2),
        AttributeConvert("lod_switch_distance", 1, 3),
    ],
    "aux[1]": [
        AttributeConvert("texgen_1_gen", 2, 0),
        AttributeConvert("texgen_1_rot", 1, 2),
    ],
}

map_to_effect_light = {
    "aux[0]": [AttributeConvert("depth_bias", 1, 0)],
    "aux[5]": [
        AttributeConvert("luminance_output", 1, 0),
        AttributeConvert("luminance_night", 1, 1),
    ],
}

map_to_effect_water = {
    "aux[0]": [AttributeConvert("water_distances", 3, 0)],
    "aux[1]": [AttributeConvert("water_near_color", 3, 0)],
    "aux[2]": [AttributeConvert("water_horizon_color", 3, 0)],
    "aux[3]": [
        AttributeConvert("water_layer_0_yaw", 1, 0),
        AttributeConvert("water_layer_0_speed", 1, 1),
        AttributeConvert("water_layer_0_scale", 2, 2),
    ],
    "aux[4]": [
        AttributeConvert("water_layer_1_yaw", 1, 0),
        AttributeConvert("water_layer_1_speed", 1, 1),
        AttributeConvert("water_layer_1_scale", 2, 2),
    ],
    "aux[5]": [AttributeConvert("water_mirror", 1, 0)],
}

map_to_effect_animsheet = {
    "aux[0]": [
        AttributeConvert("animsheet_cfg_fps", 1, 0),
        AttributeConvert("animsheet_cfg_frames_row", 1, 1),
        AttributeConvert("animsheet_cfg_frames_total", 1, 2),
    ],
    "aux[1]": [
        AttributeConvert("animsheet_frame_width", 1, 0),
        AttributeConvert("animsheet_frame_height", 1, 1),
    ],
}

map_to_effect_detail = {
    "aux[5]": [
        AttributeConvert("detail_fadeout_from", 1, 0),
        AttributeConvert("detail_fadeout_range", 1, 1),
        AttributeConvert("detail_blend_bias", 1, 2),
        AttributeConvert("detail_uv_scale", 1, 3),
    ],
}

map_to_effect_difanim = {
    "aux[0]": [AttributeConvert("animation_speed", 1, 0)],
}

map_to_effect_showroom = {
    "aux[0]": [AttributeConvert("showroom_r_color", 3, 0)],
    "aux[4]": [AttributeConvert("showroom_speed", 3, 0)],
}

map_to_effect_mult = {
    "aux[5]": [AttributeConvert("mult_uvscale", 2, 0)],
}

map_to_effect_mult2 = {
    "aux[5]": [AttributeConvert("mult_uvscale_secondary", 2, 2)],
}

map_to_effect_lampanim = {
    "aux[0]": [
        AttributeConvert("sheet_frame_size_r", 2, 0),
        AttributeConvert("sheet_frame_size_g", 2, 2),
    ],
    "aux[1]": [
        AttributeConvert("sheet_frame_size_b", 4, 0),
        AttributeConvert("sheet_frame_size_a", 4, 2),
    ],
}


class AttributeConverter:
    def __init__(self):
        self.temp_values = {}

    def effect_to_material(self, attribute, value):
        """Converts effect attribute to material attribute if present in the mapping list.
    
        :param attribute: attribute name to convert
        :type attribute: str
        :param value: value of attribute to convert
        :type value: int, float, tuple
        :return: tuple of converted attribute name and value
        :rtype: (attr, val)
        """

        # lprint("D [CONVERTER]\t EFFECT_ATTR: %s", (attribute,))
        # lprint("D [CONVERTER]\t EFFECT_VAL: %s", (value,))

        if attribute in map_to_material:
            conversions = map_to_material[attribute]
            results = []

            if not isinstance(value, tuple):
                value = (value,)

            for conversion in conversions:
                attr = conversion.name

                # check for values in temp_values
                if attr in self.temp_values:
                    val = list(self.temp_values[attr])
                else:
                    val = [None] * conversion.value_count

                # insert values into correct positions
                for i, v in enumerate(value):
                    idx = conversion.start_index + i
                    if idx < len(val):
                        # Special case for "lod_switch_distance" attribute
                        if attribute == "lod_switch_distance":
                            val[idx] = v / 25.0
                        else:
                            val[idx] = v

                # save updated value in temp_values if not fully filled
                if None in val or 0.0 in val:
                    self.temp_values[attr] = tuple(val)
                else:
                    self.temp_values.pop(attr, None)

                # set none to 0.0
                val = tuple(v if v is not None else 0.0 for v in val)

                # return single value if only one
                if len(val) == 1:
                    val = val[0]

                results.append((attr, val))

            if len(results) == 1:
                return results[0]
            return results

        else:
            return attribute, value

    def material_to_effect(self, effect, material_data):
        """Converts material attribute to effect attribute if present in the mapping list.
        
        :param effect: effect name to check for proper mapping
        :type effect: str
        :param material_data: dictionary of material attributes and values to convert
        :type material_data: dict
        :return: tuple of converted attribute name and value
        :rtype: (attr, val)
        """
        result = {}
        maps_to_check = [map_to_effect]

        # lprint("D [CONVERTER]\t EFFECT: %s", (effect,))
        # lprint("D [CONVERTER]\t MAT_DATA: %r", (material_data,))

        # Add specific maps based on effect type
        if "dif.spec.weight" in effect:
            maps_to_check.append(map_to_effect_weight)

        # mwl4 used "dif.spec.weight.mult2" check, but I think that it's better to check only for "mult2". (Need to test)
        if "mult2" in effect:
            maps_to_check.append(map_to_effect_mult)

        # mwl4 used "dif.spec.weight.mult2.weight2" but there is several new effects using that mapping, so I check only for "mult2" + "mask2" or "weight2". (Need to test)
        if "mult2.mask2" in effect or "mult2.weight2" in effect:
            maps_to_check.append(map_to_effect_mult2)

        if "leaves" in effect:
            maps_to_check.append(map_to_effect_leaves)

        if "tg0" in effect or "tg1" in effect:
            maps_to_check.append(map_to_effect_tg0tg1)

        # I merged map for "lightmap" into "light" and added other flavors where it's used.
        # "light.tex" was simplified to "light" due to new shader without ".tex" part.
        # Added "day" and "lit" cause it's also used instead of "night" flavor.
        if "light" in effect or "day" in effect or "lit" in effect or "night" in effect or "flare" in effect or "unlit" in effect or ".lum" in effect:
            maps_to_check.append(map_to_effect_light)

        if "water" in effect:
            maps_to_check.append(map_to_effect_water)

        # mwl4 use ".bounce", but animsheet is used also in other "flare" flavors so it's better to check for ".sun".
        if ".flipsheet" in effect or ".fadesheet" in effect or ".sun" in effect:
            maps_to_check.append(map_to_effect_animsheet)

        if ".fade." in effect:
            maps_to_check.append(map_to_effect_detail)

        if "lamp.anim" in effect:
            maps_to_check.append(map_to_effect_lampanim)

        # mwl4 used only ".anim." but that attribute is specific for "dif.anim" only, andit can conflict with other shaders and flavors like "lamp.anim".
        # What's more, due to conversion tool 2.21 data in eut2_dif_anim.sui, it can't be used with flipsheet and fadesheet, so I added check for that also.
        if "dif.anim" in effect and "flipsheet" not in effect and "fadesheet" not in effect:
            maps_to_check.append(map_to_effect_difanim)

        # Is normal "showroom" even used in newer versions? Should I check also for that? (data looks very similar)
        if "showroom_v2" in effect:
            maps_to_check.append(map_to_effect_showroom)

        if "flipflake" in effect:
            maps_to_check.append(map_to_effect_flipflake)

        if "truckpaint" in effect:
            maps_to_check.append(map_to_effect_truckpaint)

        # lprint("D [CONVERTER]\t MAPS_TO_CHECK: %d", (len(maps_to_check),))

        mapped_keys = set()
        for attribute_map in maps_to_check:
            mapped_keys.update(attribute_map.keys())

        # Process material_data
        for key, value in material_data.items():
            if key in mapped_keys:
                # Map found - break down attributes
                for attribute_map in maps_to_check:
                    if key in attribute_map:
                        for conv in attribute_map[key]:
                            # Extract values based on start index and value count
                            if isinstance(value, (tuple, list)):
                                vals = value
                            else:
                                vals = (value,)
                            start = conv.start_index
                            end = start + conv.value_count
                            out_val = tuple(vals[start:end])

                            # Special case for "lod_switch_distance" attribute
                            if conv.name == "lod_switch_distance":
                                out_val = out_val * 25.0

                            # If only one value, return it as single value
                            if len(out_val) == 1:
                                out_val = out_val[0]
                            result[conv.name] = out_val
            else:
                # Map not found - pass original key and value to result
                result[key] = value

        return result
