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


def get_layer_collections(view_layer):
    """Gets all children layer collections of given view layer (master collection is excluded)sas.

    :param view_layer: view layer to look up for layer collections
    :type view_layer: bpy.types.ViewLayer
    :return: list of layer collections in this view layer
    :rtype: list[bpy.types.LayerCollection]
    """

    layer_collections = set()

    master_layer_coll = view_layer.layer_collection
    collections_to_check = [master_layer_coll]
    while len(collections_to_check) > 0:
        coll = collections_to_check.pop(0)

        if coll.children:
            collections_to_check.extend(coll.children)

        if coll == master_layer_coll:
            continue

        layer_collections.add(coll)

    return list(layer_collections)
