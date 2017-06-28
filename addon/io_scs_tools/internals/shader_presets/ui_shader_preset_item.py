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

# Copyright (C) 2017: SCS Software


class UIShaderPresetItem:
    """Class holding shader preset data used for UI."""

    def __init__(self, the_effect, the_name):
        """Constructor creating new UI shader preset item for given base effect and preset name.

        :param the_effect: base effect without any flavor postfix
        :type the_effect: str
        :param the_name: preset name
        :type the_name: str
        """
        self.name = the_name
        """Shader Presets Name"""
        self.effect = the_effect
        """Base Effect Name"""
        self.flavors = []
        """:type: list[Flavor]"""
        """Collection of flavors for this shader ordered by the name of apperance in the effect name"""

    def append_flavor(self):
        """Creates new flavor entry for preset item.
        """
        new_flavor = Flavor()
        self.flavors.append(new_flavor)

    def append_flavor_variant(self, variant_type, variant_suffix):
        """Appends flavor variant to lastly added flavor.

        NOTE: This should be always called after "append_flavor", otherwise it will result in error.

        :param variant_type: type of the flavor variant
        :type variant_type: str
        :param variant_suffix: name of the flavor variant
        :type variant_suffix: str
        """
        new_flavor_variant = FlavorVariant(variant_type, variant_suffix)
        self.flavors[-1].append_variant(new_flavor_variant)


class Flavor:
    def __init__(self):
        """Constructor.
        """
        self.variants = []
        """:type: list[FlavorVariant]
        Represents variants of this flavor. (eg. tsnmap,  tsnmapuv)
        """

    def append_variant(self, variant):
        """Appends given flavor variant to list.

        :param variant: flavor variant to add
        :type variant: FlavorVariant
        """

        self.variants.append(variant)


class FlavorVariant:
    def __init__(self, the_type, the_suffix):
        """Constructor.

        :param the_type: type of the flavor variant
        :type the_type: str
        :param the_suffix: name of the flavor variant
        :type the_suffix: str
        """
        self.type = the_type
        """Internal type name of the flavor variant."""
        self.suffix = the_suffix
        """Suffix of flavor variant inside effect name."""
