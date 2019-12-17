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

from io_scs_tools.properties.dynamic import scene
from io_scs_tools.properties.dynamic import object


class DynamicProps:
    class Scopes:
        """Scopes to distingish variable names to avoid registration of dynamic properties with same names."""
        __prefix = "dynamic_"

        SCS_GLOBALS = __prefix + "scs_globals"

    __registered_props = {}

    @staticmethod
    def __register_property__(scope, property_name):
        """Registered given property name for given class type.

        :param scope: scope in which this porperty will be registered
        :type scope: str
        :param property_name: name of the property
        :type property_name: str
        :return: True if property can be registered; False if property is already registered for given class type
        :rtype: bool
        """

        if scope not in DynamicProps.__registered_props:
            DynamicProps.__registered_props[scope] = set()

        if property_name in DynamicProps.__registered_props:
            return False

        DynamicProps.__registered_props[scope].add(property_name)
        return True

    @staticmethod
    def register(scope, property_name, property_type, default):
        """Registers runtime property that won't be saved in blend file.

        :param scope: scope in which this porperty will be registered
        :type scope: str
        :param property_name: name of the property under which it will be saved
        :type property_name: str
        :param property_type: type of the property: str | float | bool | int | tuple | list
        :type property_type: type
        :param default: default value to be returned
        :type default: any
        :return: property implementation
        :rtype: property
        """

        def getter(self):
            """Returns property value.

            :param self: instance of object on which property will be registered
            :type self: object
            :return: default or saved value
            :rtype: any
            """
            assert self

            prefs = bpy.context.preferences.addons["io_scs_tools"].preferences

            if scope not in prefs:
                return default

            scoped_prefs = prefs[scope]

            if property_name not in scoped_prefs:
                return default

            return scoped_prefs[property_name]

        def setter(self, value):
            """Sets value to the property.

            :param self: instance of object on which property will be registered
            :type self: obj
            :param value: value to save into this property
            :type value: str | float | int | bool
            """
            assert self
            assert isinstance(value, property_type)

            prefs = bpy.context.preferences.addons["io_scs_tools"].preferences

            if scope not in prefs:
                prefs[scope] = {}

            prefs[scope][property_name] = value

        # check for default value type
        assert isinstance(default, property_type)

        # make sure registration is unique
        assert DynamicProps.__register_property__(scope, property_name)

        return property(getter, setter)

    @staticmethod
    def get_registered_members(scope):
        """Gets property names as a tuple.

        :return: tuple of dynamic property names
        :rtype: set[str]
        """
        assert scope in DynamicProps.__registered_props

        return DynamicProps.__registered_props[scope]


def register():
    scene.register()
    object.register()


def unregister():
    scene.register()
    object.register()
