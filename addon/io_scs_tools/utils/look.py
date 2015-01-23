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

'''
def get_actual_look():
    """Returns actual Look name as a string."""
    # print('  > get_actual_look...')
    for look in bpy.context.scene.scs_look_inventory:
        if look.active:
            return look.name
    return None


def set_actual_look(look_name):
    """Sets provided Look name as active."""
    # print('  > set_actual_look...')
    print('look_name: "%s"' % str(look_name))
    for look in bpy.context.scene.scs_look_inventory:
        print('look: "%s"' % str(look))
        print('look.name: "%s"' % str(look.name))
        if look.name == look_name:
            look.active = True
        else:
            look.active = False


def add_look_to_inventory(new_look_name):
    """Given a name, it appends a new Look name to Inventory."""
    new_look_name = remove_diacritic(new_look_name)
    if new_look_name != "":
        inventory, success = inventory_add_item(bpy.context.scene.scs_look_inventory, new_look_name)
        if not success:
            print("WARNING - The Look "%s" already exists in the inventory!" % new_look_name)
'''