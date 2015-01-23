# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2014: SCS Software

"""
This script manages import of various SCS binary data files into Blender.
"""

import bpy
import os
# from bpy_extras import io_utils
# from . import import_pmg
# from . import import_pit
# from . import import_pic
# from . import import_pip
# from . import import_pis
# from . import import_pia
# from . import io_utils
from .deprecated_utils import Print

if "bpy" in locals():
    import imp
    # if "import_pmg" in locals():
    #     imp.reload(import_pmg)
    # else:
    #     from . import import_pmg
    # if "import_pit" in locals():
    #     imp.reload(import_pit)
    # else:
    #     from . import import_pit
    # #if "import_pic" in locals():
    #     #imp.reload(import_pic)
    # #else:
    #     #from . import import_pic
    # if "import_pip" in locals():
    #     imp.reload(import_pip)
    # else:
    #     from . import import_pip
    # if "import_pis" in locals():
    #     imp.reload(import_pis)
    # else:
    #     from . import import_pis
    # if "import_pia" in locals():
    #     imp.reload(import_pia)
    # else:
    #     from . import import_pia
    if "io_utils" in locals():
        imp.reload(io_utils)
    else:
        from . import io_utils

def version():
    """Here is where to alter version number of the script."""
    return 0.2

def create_lod_empty(name, objects, locators, armature, skeleton):
    """Creates an 'SCS Root Object' (Empty Object) for currently imported 'SCS Game Object' and parent all import content to it."""
    if name in bpy.data.objects:
        name = io_utils.make_unique_name(bpy.data.objects[0], name)

## CREATE EMPTY OBJECT
    bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            # location=scs_loc,
            # rotation=rot,
            )#, layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

## MAKE A PROPER SETTINGS TO THE 'SCS ROOT OBJECT'
    lod_object = bpy.context.active_object
    lod_object.name = name
    lod_object.show_name = True
    lod_object.scs_props.scs_root_object_export_enabled = True
    lod_object.scs_props.empty_object_type = 'SCS_Root'

## MAKE ALL CHILDREN SELECTED
    if armature:
        bpy.ops.object.select_all(action='DESELECT')
        armature.select = True
    else:
        for obj in objects:
            obj.select = True
        for obj in locators:
            obj.select = True

## SET PARENT
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

## MAKE ONLY 'SCS GAME OBJECT' SELECTED
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        obj.select = False
    lod_object.select = True
    bpy.context.scene.objects.active = lod_object

    return bpy.data.objects.get(name)

def load(
        operator,
        context,
        filepath,
        ):
    import time

    t = time.time()
    bpy.context.window.cursor_modal_set('WAIT')
    # import_scale = bpy.data.worlds[0].scs_globals.import_scale
    # load_textures = bpy.data.worlds[0].scs_globals.load_textures
    # mesh_creation_type = bpy.data.worlds[0].scs_globals.mesh_creation_type
    dump_level = int(bpy.data.worlds[0].scs_globals.dump_level)

    prefab_locators = []
    objects = []
    locators = []
    armature = skeleton = None

    # ## NEW SCENE CREATION
    # if bpy.data.worlds[0].scs_globals.scs_lod_definition_type == 'scenes':
    #     if context.scene.name != 'Scene':
    #         bpy.ops.scene.new(type='NEW')

## IMPORT PMG (PIM)
    if bpy.data.worlds[0].scs_globals.import_pmg_file or bpy.data.worlds[0].scs_globals.import_pis_file:
        if filepath:
            if os.path.isfile(filepath):
                Print(dump_level, '\nD PMG filepath:\n  %s', str(filepath).replace("\\", "/"))
                # result, objects, locators, armature, skeleton = import_pmg.load(operator, context, filepath)
            else:
                Print(dump_level, '\nI No file found at %r!' % str(filepath).replace("\\", "/"))
        else:
            Print(dump_level, '\nI No filepath provided!')

# ## IMPORT PIT
#     if bpy.data.worlds[0].scs_globals.import_pit_file:
#         pit_filepath = str(filepath[:-1] + 't')
#         if os.path.isfile(pit_filepath):
#             Print(dump_level, '\nD PIT filepath:\n  %s', pit_filepath)
#             # print('PIT filepath:\n  %s' % pit_filepath)
#             result = import_pit.load(operator, context, pit_filepath)
#         else:
#             Print(dump_level, '\nI No PIT file.')
#             # print('INFO - No PIT file.')

# ## IMPORT PIC
#     if bpy.data.worlds[0].scs_globals.import_pic_file:
#         pic_filepath = str(filepath[:-1] + 'c')
#         if os.path.isfile(pic_filepath):
#             Print(dump_level, '\nD PIC filepath:\n  %s', pic_filepath)
#             # print('PIC filepath:\n  %s' % pic_filepath)
#         else:
#             Print(dump_level, '\nI No PIC file.')
#             # print('INFO - No PIC file.')

# ## IMPORT PIP
#     if bpy.data.worlds[0].scs_globals.import_pip_file:
#         pip_filepath = str(filepath[:-1] + 'p')
#         if os.path.isfile(pip_filepath):
#             Print(dump_level, '\nD PIP filepath:\n  %s', pip_filepath)
#             # print('PIP filepath:\n  %s' % pip_filepath)
#             result, prefab_locators = import_pip.load(operator, context, pip_filepath)
#         else:
#             Print(dump_level, '\nI No PIP file.')
#             # print('INFO - No PIP file.')

# ## IMPORT PIS
#     if bpy.data.worlds[0].scs_globals.import_pis_file:
#         pis_filepath = str(filepath[:-1] + 's')
#         if os.path.isfile(pis_filepath):
#             Print(dump_level, '\nD PIS filepath:\n  %s', pis_filepath)
#             # print('PIS filepath:\n  %s' % pis_filepath)
#             result, bones = import_pis.load(operator, context, pis_filepath, armature)
#         else:
#             bones = None
#             Print(dump_level, '\nI No PIS file.')
#             # print('INFO - No PIS file.')

# ## IMPORT PIA
#     if bpy.data.worlds[0].scs_globals.import_pis_file and bpy.data.worlds[0].scs_globals.import_pia_file:
#         basepath = os.path.dirname(filepath)
#         ## Search for PIA files in model's directory and its subdirectiories...
#         Print(dump_level, '\nI Searching the directory for PIA files:\n   %s', str(basepath))
#         # print('\nSearching the directory for PIA files:\n   %s' % str(basepath))
#         pia_files = []
#         index = 0
#         for root, dirs, files in os.walk(basepath):
#             if not bpy.data.worlds[0].scs_globals.include_subdirs_for_pia:
#                 if index > 0:
#                     break
#             # print('  root: %s - dirs: %s - files: %s' % (str(root), str(dirs), str(files)))
#             for file in files:
#                 if file.endswith(".pia"):
#                     pia_filepath = os.path.join(root, file)
#                     pia_files.append(pia_filepath)
#             index += 1
#
#         if len(pia_files) > 0:
#             if dump_level > 1:
#                 Print(dump_level, 'I PIA files found:')
#                 for pia_filepath in pia_files: Print(dump_level, 'I %r', pia_filepath)
#             # print('armature: %s\nskeleton: %r\nbones: %s\n' % (str(armature), str(skeleton), str(bones)))
#             result = import_pia.load(operator, context, pia_files, armature, skeleton, bones)
#             # print('  result: %s' % str(result))
#         else:
#             Print(dump_level, '\nI No PIA files.')

## SETUP LODS
    for item in prefab_locators:
        locators.append(item)
    path, file = os.path.split(filepath)
    # print('  path: %r\n  file: %r' % (path, file))
    lod_name, ext = os.path.splitext(file)
    # print('  root: %r\n  ext: %r' % (root, ext))
    # if bpy.data.worlds[0].scs_globals.scs_lod_definition_type == 'scenes':
    #     print('LODs as Scenes...')
    #     context.scene.name = lod_name
    #     context.scene.scs_props.scene_lod = True
    # else:
    print('LODs as Objects...')
    if objects:
        create_lod_empty(lod_name, objects, locators, armature, skeleton)

## SET DRAW MODES
    ## Turn on Textured Solid in 3D view...
    for bl_screen in bpy.data.screens:
        for bl_area in bl_screen.areas:
            for bl_space in bl_area.spaces:
                if bl_space.type == 'VIEW_3D':
                    bl_space.show_textured_solid = True

                    # bl_space.viewport_shade = 'WIREFRAME'
                    # bl_space.show_manipulator = True
                    bl_space.transform_orientation = 'NORMAL'
                    bl_space.transform_manipulators = {'ROTATE'}

    ## Turn on GLSL in 3D view...
    bpy.context.scene.game_settings.material_mode = 'GLSL'

## TURN ON SCS TOOLS
    # bpy.context.scene.scs_props.locator_size = 10.0 # TMP: increase locators' size

    bpy.context.window.cursor_modal_restore()
    Print(dump_level, '\nI files imported (in %.3f sec)', time.time() - t)
