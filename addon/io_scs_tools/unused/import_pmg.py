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
This script imports SCS PMG (Model) files into Blender.
"""

import bpy
import os
#import bmesh
from bpy_extras import object_utils
from bpy_extras.io_utils import unpack_face_list
from .deprecated_utils import Print
# from . import io_utils
# from . import pix_parse
# from . import deprecated_utils as utils

if "bpy" in locals():
    import imp
    if "io_utils" in locals():
        imp.reload(io_utils)
    else:
        from . import io_utils
    if "pix_parse" in locals():
        imp.reload(pix_parse)
    else:
        from . import pix_parse
    if "utils" in locals():
        imp.reload(utils)
    else:
        from . import deprecated_utils as utils

def version():
    """Here is where to alter version number of the script."""
    return 0.2

def create_material(
        materials_alias,
        materials_effect,
        ):
    if materials_alias not in bpy.data.materials:
        material = bpy.data.materials.new(materials_alias)
        material.scs_props.cgfx_filename = materials_effect ## TODO: Temporal solution!!! The effect is not always the same with CgFX shader file name!
        material.scs_props.mat_cgfx_effect_name = materials_effect
        #material.diffuse_shader = 'MINNAERT'
        #material.diffuse_color = (0.0, 0.288, 0.0)
        #material.darkness = 0.8
    else:
        material = None
        # print('WARNING: Skipping material with already existing name "%s"...' % materials_alias)
    return material

def make_per_vertex_uv_layer(mesh, mesh_uv, uv_layer_name):
    """Creates UV layer in mesh per-vertex..."""
    uvlay = mesh.tessface_uv_textures.new(name=uv_layer_name)

    for i, uv_l in enumerate(uvlay.data):
        fac = mesh.tessfaces[i]
        for j, uv in enumerate(uv_l.uv):
            vert = fac.vertices[j]
            vert_uv = mesh_uv[uv_layer_name][vert]
            # print('vert_uv: %s - uv: %s' % (str(vert_uv), str(uv)))
            uv[0], uv[1] = (vert_uv[0], -vert_uv[1] + 1)

    return {'FINISHED'}

def make_per_face_uv_layer(mesh, uv_layer, layer_name):
    """Creates UV layer in mesh per-face..."""
    uvlay = mesh.tessface_uv_textures.new(name=layer_name)

    for i, fac in enumerate(uvlay.data):
        # print('uv_layer: %s' % str(uv_layer))
        fac_uv = uv_layer[i]
        # print('fac_uv: %s' % str(fac_uv))
        for j, uv in enumerate(fac.uv):
            # print('fac_uv[j]: %s - uv: %s' % (str(fac_uv[j]), str(uv)))
            uv[0], uv[1] = (fac_uv[j][0], -fac_uv[j][1] + 1)

    return {'FINISHED'}

def make_vcolor_layer(mesh, mesh_rgb, mesh_rgba):
    """Creates UV layers in mesh..."""
    vcol_lay = mesh.tessface_vertex_colors.new()

    for i, col_l in enumerate(vcol_lay.data):
        fac = mesh.tessfaces[i]
        if len(fac.vertices) == 4:
            f_col = col_l.color1, col_l.color2, col_l.color3, col_l.color4
        else:
            f_col = col_l.color1, col_l.color2, col_l.color3
        for j, col in enumerate(f_col):
            vert = fac.vertices[j]
            if mesh_rgba:
                col.r = mesh_rgba[vert][0]
                col.g = mesh_rgba[vert][1]
                col.b = mesh_rgba[vert][2]
            elif mesh_rgb:
                col.r, col.g, col.b = mesh_rgb[vert]
    return {'FINISHED'}

def make_per_face_rgb_layer(mesh, rgb_layer, layer_name):
    """Creates color (RGB) layer in mesh per-face..."""
    vcol_lay = mesh.tessface_vertex_colors.new(name=layer_name)
    #print('vcol_lay: %s' % str(vcol_lay))

    for i, fac in enumerate(vcol_lay.data):
        print('fac: %s' % str(fac))
        print('rgb_layer: %s' % str(rgb_layer))
        fac_rgb = rgb_layer[i]
        print('fac_rgb: %s' % str(fac_rgb))
        print('fac.color1: %s' % str(fac.color1))
        print('fac.color2: %s' % str(fac.color2))
        print('fac.color3: %s' % str(fac.color3))
        print('fac.color4: %s' % str(fac.color4))
        #for j, rgb in enumerate(fac.color2):
        for j, fac_vert_rgb in enumerate(fac_rgb):
            #print('rgb: %s' % str(rgb))
            print('fac_rgb[j]: %s - fac_vert_rgb: %s' % (str(fac_rgb[j]), str(fac_vert_rgb)))
            #rgb[0], rgb[1], rgb[2] = fac_rgb[j]

    #for i, f in enumerate(vcol_lay.data):
        ## NOTE: Colors dont come in right, needs further investigation.
        #ply_col = mesh_colors[i]
        #if len(ply_col) == 4:
            #f_col = f.color1, f.color2, f.color3, f.color4
        #else:
            #f_col = f.color1, f.color2, f.color3

        #for j, col in enumerate(f_col):
            #col.r, col.g, col.b = ply_col[j]

    return {'FINISHED'}

# def visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale):
#     """
#     This function will create an additional object with edges
#     representing vertex normals to visualise imported normals.
#     :param name:
#     :param transformed_mesh_vertices:
#     :param mesh_normals:
#     :param import_scale:
#     :return:
#     """
#     if mesh_normals:
#         transformed_mesh_normals = [io_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_normals]
#         mesh_norm_vizu = bpy.data.meshes.new(str(name + "_norm_vizu"))
#         object_norm_vizu = bpy.data.objects.new(str(name + "_norm_vizu"), mesh_norm_vizu)
#         bpy.context.scene.objects.link(object_norm_vizu)
#         mesh_norm_vizu.vertices.add(len(transformed_mesh_vertices) * 2)
#         mesh_norm_vizu.edges.add(len(transformed_mesh_vertices))
#         vert_i = edge_i = 0
#
#         # print(' ** transformed_mesh_vertices: %s' % str(transformed_mesh_vertices))
#         # print(' ** mesh_normals: %s' % str(mesh_normals))
#         # print(' ** transformed_mesh_normals: %s' % str(transformed_mesh_normals))
#
#         for vert in range(len(transformed_mesh_vertices)):
#             vert_co = transformed_mesh_vertices[vert]
#             vert_no = transformed_mesh_normals[vert]
#             mesh_norm_vizu.vertices[vert_i].co = vert_co
#             vert_i += 1
#             mesh_norm_vizu.vertices[vert_i].co = Vector(vert_co) + (Vector(vert_no) / 16)
#             vert_i += 1
#             mesh_norm_vizu.edges[edge_i].vertices = (vert_i - 1, vert_i - 2)
#             edge_i += 1
#
#         # mesh_norm_vizu.validate()
#         mesh_norm_vizu.update()
#         # object_norm_vizu.select = True
#         # bpy.context.scene.objects.active = object_norm_vizu
#     else:
#         print('WARNING! "visualise_normals" - NO MESH NORMALS PROVIDED!')

def create_5_piece(
        context,
        preview_model,
        name,
        ob_material,
        mesh_vertices,
        mesh_normals,
        mesh_tangents,
        mesh_rgb,
        mesh_rgba,
        mesh_scalars,
        object_skinning,
        mesh_uv,
        mesh_tuv,
        mesh_triangles,
        materials_data,
        points_to_weld_list,
        ):

    context.window_manager.progress_begin(0.0, 1.0)
    context.window_manager.progress_update(0)

    mesh_creation_type = bpy.data.worlds[0].scs_globals.mesh_creation_type
    import_scale = bpy.data.worlds[0].scs_globals.import_scale

    mesh = bpy.data.meshes.new(name)

## COORDINATES TRANSFORMATION
    transformed_mesh_vertices = [io_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_vertices]

    context.window_manager.progress_update(0.1)

## VISUALISE IMPORTED NORMALS (DEBUG)
    # visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale)

## MESH CREATION
    duplicate_geometry = ((), (), (), ())

## -- BMesh --
    if mesh_creation_type == 'mct_bm':
        import bmesh
        bm = bmesh.new()

        ## VERTICES
        io_utils.bm_make_vertices(bm, transformed_mesh_vertices)
        context.window_manager.progress_update(0.2)

        ## FACES
        duplicate_geometry = io_utils.bm_make_faces(bm, transformed_mesh_vertices, mesh_triangles, points_to_weld_list, mesh_uv)
        context.window_manager.progress_update(0.3)

        ## UV LAYERS
        if mesh_uv:
            for uv_layer_name in mesh_uv:
                io_utils.bm_make_uv_layer(5, bm, mesh_triangles, uv_layer_name, mesh_uv[uv_layer_name])
        context.window_manager.progress_update(0.4)

        ## VERTEX COLOR
        if mesh_rgba:
            # print('mesh_rgba: %s' % str(mesh_rgba))
            for uv_layer_name in mesh_rgba:
                # io_utils.bm_make_vc_layer(5, bm, mesh_triangles, uv_layer_name, mesh_rgba[uv_layer_name])
                io_utils.bm_make_vc_layer(5, bm, uv_layer_name, mesh_rgba[uv_layer_name])
        if mesh_rgb:
            # print('mesh_rgb: %s' % str(mesh_rgb))
            for uv_layer_name in mesh_rgb:
                # io_utils.bm_make_vc_layer(5, bm, mesh_triangles, uv_layer_name, mesh_rgb[uv_layer_name])
                io_utils.bm_make_vc_layer(5, bm, uv_layer_name, mesh_rgb[uv_layer_name])
        context.window_manager.progress_update(0.5)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        context.window_manager.progress_update(0.6)

        ## Add the mesh as an object into the scene with this utility module.
        obj = object_utils.object_data_add(context, mesh).object
        obj.location = (0.0, 0.0, 0.0)

        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.shade_smooth()
        context.window_manager.progress_update(0.7)

## -- TessFaces --
    elif mesh_creation_type == 'mct_tf':
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.objects.link(obj)
        mesh.vertices.add(len(transformed_mesh_vertices))
        mesh.vertices.foreach_set("co", [a for v in transformed_mesh_vertices for a in v])

        mesh.tessfaces.add(len(mesh_triangles))

        mesh_faces = mesh.tessfaces
        mesh_faces.foreach_set("vertices_raw", unpack_face_list(mesh_triangles))

        # for i in range(len(unpack_face_list(mesh_triangles))):
            # setattr(mesh_faces[i], "vertices_raw", unpack_face_list(mesh_triangles)[i])

        # face_list = unpack_face_list(mesh_triangles)
        # print('face_list: %s' % str(face_list))
        # for i in range(len(face_list)):
            # face = face_list[i]
            # print(' face: %s' % str(face))
            # setattr(mesh_faces[i], "vertices_raw", face)

        if mesh_uv:
            for uv_layer_name in mesh_uv:
                result = make_per_vertex_uv_layer(mesh, mesh_uv, uv_layer_name)

        if mesh_rgb or mesh_rgba:
            result = make_vcolor_layer(mesh, mesh_rgb, mesh_rgba)

        # mesh.validate()
        mesh.update()
        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.shade_smooth()

## -- MeshPolygons --
    elif mesh_creation_type == 'mct_mp':
        obj = bpy.data.objects.new(name, mesh)
        # object.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.link(obj)

        edges = []
        mesh.from_pydata(transformed_mesh_vertices, edges, mesh_triangles)
        mesh.update()
        print("***00*** %s" % name)

        # object = context.active_object
        # mesh = object.data

        is_editmode = (obj.mode == 'EDIT')
        print("***01*** %s" % name)
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        print("***02*** %s" % name)
        uv_layer = bpy.ops.mesh.uv_texture_add()
        print("uv_layer %s" % uv_layer)
        # adjust UVs
        for i, uv in enumerate(uv_layer.data):
            uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
            for j, v_idx in enumerate(mesh.faces[i].vertices):
                if uv.select_uv[j]:
                    # apply the location of the vertex as a UV
                    uvs[j][:] = mesh.vertices[v_idx].co.xy
        print("***03*** %s" % name)

        if is_editmode:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # vc_layer = mesh.vertex_colors.new(name)
        # print("vc_layer %s" % vc_layer)
        mesh.update()
        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.shade_smooth()

    context.window_manager.progress_update(0.8)

## SKINNING (VERTEX GROUPS)
    if object_skinning:
        for vertex_group_name in object_skinning[name]:
            vertex_group = obj.vertex_groups.new(vertex_group_name)
            for vertex_i, vertex in enumerate(object_skinning[name][vertex_group_name]):
                weight = object_skinning[name][vertex_group_name][vertex]
                if weight != 0.0:
                    for rec in points_to_weld_list:
                        for vert in rec:
                            if vert == vertex:
                                vertex = rec[0]
                                break
                    vertex_group.add([vertex], weight, "ADD")

    context.window_manager.progress_update(0.9)

## DELETE ORPHAN VERTICES (LEFT IN THE GEOMETRY FROM SMOOTHING RECONSTRUCTION)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)
    for rec in points_to_weld_list:
        for vert_i, vert in enumerate(rec):
            if vert_i != 0: bm.verts[vert].select = True

    verts = [v for v in bm.verts if v.select]
    if verts: bmesh.ops.delete(bm, geom=verts, context=1)

## APPLYING BMESH TO MESH
    # bm.to_mesh(mesh)
    bm = bmesh.update_edit_mesh(mesh, tessface=True, destructive=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh.update()
    # bm.free()

    context.window_manager.progress_update(1.0)

## MATERIAL
    if len(materials_data) > 0 and not preview_model:
        bpy.ops.object.material_slot_add() # Add a material slot
        obj.material_slots[obj.material_slots.__len__() - 1].material = bpy.data.materials[materials_data[ob_material][0]] # Assign a material to the last slot
        #bpy.ops.object.mode_set(mode='EDIT') # Go to Edit mode
        #bpy.ops.mesh.select_all(action='SELECT') # Select all the vertices
        #bpy.ops.object.material_slot_assign() # Assign the material on all the vertices
        #bpy.ops.object.mode_set(mode='OBJECT') # Return to Object Mode

    context.window_manager.progress_end()

    return obj, duplicate_geometry

def create_7_piece(
        context,
        name,
        mesh_vertices,
        mesh_normals,
        mesh_tangents,
        mesh_rgb,
        mesh_rgba,
        mesh_scalars,
        object_skinning,
        mesh_uv,
        mesh_tuv,
        mesh_faces,
        mesh_face_materials,
        mesh_edges,
        materials_data,
        ):

    context.window_manager.progress_begin(0.0, 1.0)
    context.window_manager.progress_update(0)

    mesh_creation_type = bpy.data.worlds[0].scs_globals.mesh_creation_type
    import_scale = bpy.data.worlds[0].scs_globals.import_scale
    mesh = bpy.data.meshes.new(name)

## COORDINATES TRANSFORMATION
    transformed_mesh_vertices = [io_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_vertices]

    context.window_manager.progress_update(0.1)

## VISUALISE IMPORTED NORMALS (DEBUG)
    ## NOTE: NOT functional for PIM version 7 since mesh normals are not provided in per vertex fashion!
    # visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale)

## MESH CREATION
    duplicate_geometry = ((), (), (), ())

## -- BMesh --
    if mesh_creation_type == 'mct_bm':
        import bmesh
        bm = bmesh.new()

        ## VERTICES
        io_utils.bm_make_vertices(bm, transformed_mesh_vertices)
        context.window_manager.progress_update(0.2)

        ## FACES
        # for fac_i, fac in enumerate(mesh_faces): print('     face[%i]: %s' % (fac_i, str(fac)))
        duplicate_geometry = io_utils.bm_make_faces(bm, transformed_mesh_vertices, mesh_faces, [], mesh_uv)
        context.window_manager.progress_update(0.3)

        ## SHARP EDGES
        # print('mesh_edges: %s' % str(mesh_edges))
        for edge in bm.edges:
            edge_verts = [edge.verts[0].index, edge.verts[1].index]
            edge_verts_inv = [edge.verts[1].index, edge.verts[0].index]
            if edge_verts in mesh_edges or edge_verts_inv in mesh_edges:
                # print('edge: %s' % str(edge_verts))
                edge.smooth = False
        context.window_manager.progress_update(0.4)

        ## UV LAYERS
        if mesh_uv:
            for uv_layer_name in mesh_uv:
                io_utils.bm_make_uv_layer(7, bm, mesh_faces, uv_layer_name, mesh_uv[uv_layer_name])
        context.window_manager.progress_update(0.5)

        ## VERTEX COLOR
        if mesh_rgba:
            for rgba_layer_name in mesh_rgba:
                io_utils.bm_make_vc_layer(7, bm, rgba_layer_name, mesh_rgba[rgba_layer_name])
        if mesh_rgb:
            for rgb_layer_name in mesh_rgb:
                io_utils.bm_make_vc_layer(7, bm, rgb_layer_name, mesh_rgb[rgb_layer_name])
        context.window_manager.progress_update(0.6)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

## -- TessFaces --
    elif mesh_creation_type == 'mct_tf':
        mesh.vertices.add(len(transformed_mesh_vertices))
        mesh.vertices.foreach_set("co", [a for v in transformed_mesh_vertices for a in v])

        # print('\n  mesh_faces:\n%s' % str(mesh_faces))
        mesh.tessfaces.add(len(mesh_faces))
        mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(mesh_faces))

        if mesh_rgb or mesh_rgba:
            for rgb_layer_name in mesh_rgb:
                #print('rgb_layer_name: "%s"\n  %s' % (rgb_layer_name, str(mesh_rgb[rgb_layer_name])))
                result = make_per_face_rgb_layer(mesh, mesh_rgb[rgb_layer_name], rgb_layer_name)

        # print('\n  mesh_uv 2:\n%s' % str(mesh_uv))
        if mesh_uv:
            for uv_layer_name in mesh_uv:
                # print('uv_layer_name: "%s"\n  %s' % (uv_layer_name, str(mesh_uv[uv_layer_name])))
                result = make_per_face_uv_layer(mesh, mesh_uv[uv_layer_name], uv_layer_name)

        mesh.update()
        io_utils.set_sharp_edges(mesh, mesh_edges)

        #print('')
        #for face in mesh.polygons:
            #print('%s face - material: %s' % (str(face.index).rjust(5, ' '), str(face.material_index)))

## -- MeshPolygons --
    elif mesh_creation_type == 'mct_mp':
        pass

    ## Add the mesh as an object into the scene with this utility module.
    obj = object_utils.object_data_add(context, mesh).object

    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.shade_smooth()

## SCALAR LAYERS
    if mesh_scalars:
        for sca_layer_name in mesh_scalars:
            vertex_group = obj.vertex_groups.new(sca_layer_name)
            for val_i, val in enumerate(mesh_scalars[sca_layer_name]):
                val = float(val[0])
                if val != 0.0:
                    vertex_group.add([val_i], val, "ADD")
    context.window_manager.progress_update(0.7)

## ADD EDGESPLIT MODIFIER
    io_utils.set_edgesplit("ES_" + name)

## MATERIALS
    used_mats = []
    # print('\n  mesh_face_materials:\n%s' % str(mesh_face_materials))
    for mat_index in mesh_face_materials:
        if mat_index not in used_mats:
            used_mats.append(mat_index)
    # print('  used_mats:\n%s' % str(used_mats))
    context.window_manager.progress_update(0.8)

## ADD MATERIALS TO SLOTS
    # print('  materials_data:\n%s' % str(materials_data))
    if len(materials_data) > 0:
        for mat_i, used_mat in enumerate(used_mats):
            material = materials_data[mat_i][0]
            bpy.ops.object.material_slot_add() # Add a material slot
            last_slot = obj.material_slots.__len__() - 1
            # print('    used_mat: %s (%i) => %s : %s' % (str(used_mat), mat_i, str(last_slot), str(material)))
            obj.material_slots[last_slot].material = bpy.data.materials[material] # Assign a material to the slot
    mesh = obj.data
    context.window_manager.progress_update(0.9)

## APPLY MATERIAL INDICIES
    for face_i, face in enumerate(mesh.polygons):
        face.material_index = mesh_face_materials[face_i]
    context.window_manager.progress_update(1.0)

    return obj, duplicate_geometry

def create_locator( ## NOTE: UNUSED NOW!! Using 'io_utils.create_locator_empty()' instesd.
        loc_name,
        loc_hookup,
        loc_position,
        loc_rotation,
        loc_scale,
        # loc_type,
        ):

    import_scale = bpy.data.worlds[0].scs_globals.import_scale

## ALTER LOCATOR'S NAME IF NECESARY...
    # loc_name = utils.alter_number_in_blender_name(loc_name, bpy.data.objects)
    loc_name = io_utils.make_unique_name(bpy.data.objects[0], loc_name, sep=".")

## CREATE EMPTY...
    bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            location=io_utils.change_to_scs_xyz_coordinates(loc_position, import_scale),
            )#, layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    empty_object = bpy.context.active_object

## SET ROTATION...
    empty_object.rotation_mode = 'QUATERNION'
    empty_object.rotation_quaternion = io_utils.change_to_blender_quaternion_coordinates(loc_rotation)

## SET OTHER SETTINGS...
    empty_object.name = loc_name
    locator = bpy.data.objects.get(loc_name)
    # print('locator: "%s"' % str(locator))
    locator.empty_draw_size = 0.1
    locator.scale = loc_scale
    locator.scs_props.empty_object_type = 'Locator'
    locator.scs_props.locator_type = 'Model'
    if loc_hookup: locator.scs_props.locator_model_hookup = loc_hookup
    return locator

def make_posnorm_list(mesh_vertices, mesh_normals):
    """Makes a list of vertices records in a form (position_X, position_Y, position_Z, normal_X, normal_Y, normal_Z)."""
    posnorm_list = []
    for val_i, val in enumerate(mesh_vertices):
        posnorm_list.append((val[0], val[1], val[2], mesh_normals[val_i][0], mesh_normals[val_i][1], mesh_normals[val_i][2]))
    return posnorm_list

def make_points_to_weld_list(posnorm_list):
    """Search for identical records (the same "posnorms") and make a list..."""
    points_to_weld_list = []
    for a_i, a_pnt in enumerate(posnorm_list):
        pnt_group = []
        pnt_group_tmp = []
        for b_i, b_pnt in enumerate(posnorm_list):
            if a_i != b_i:
                if a_pnt == b_pnt:
                    pnt_group_tmp.append(b_i)
        if len(pnt_group_tmp) > 0:
            pnt_group.append(a_i)
            for item in pnt_group_tmp:
                pnt_group.append(item)
        if len(pnt_group) > 0:
            add_rec = True
            for rec in points_to_weld_list:
                if pnt_group[0] in rec:
                    add_rec = False
                    break
            if add_rec:
                points_to_weld_list.append(pnt_group)
    # for item in points_to_weld_list:
        # print('item = %s' % str(item))
    return points_to_weld_list

def getHeader(pmg_container, dump_level):
    """Receives PMG container and returns its format version as an integer.
    If the format version fail to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pmg_container:
        if section.type == "Header":
            for prop in section.props:
                if prop[0] in ("", "#"): pass
                elif prop[0] == "FormatVersion": format_version = prop[1]
                elif prop[0] == "Source": source = prop[1]
                elif prop[0] == "Type": f_type = prop[1]
                elif prop[0] == "Name": f_name = prop[1]
                elif prop[0] == "SourceFilename": source_filename = prop[1]
                elif prop[0] == "Author": author = prop[1]
                else: Print(dump_level, '\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, f_name, source_filename, author

def getGlobal(pmg_container, dump_level):
    """Receives PMG container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    vertex_count = face_count = edge_count = material_count = piece_count = part_count = bone_count = locator_count = 0
    skeleton = None
    for section in pmg_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"): pass
                elif prop[0] == "VertexCount": vertex_count = prop[1]
                elif prop[0] in ("TriangleCount", "FaceCount"): face_count = prop[1]
                elif prop[0] == "EdgeCount": edge_count = prop[1]
                elif prop[0] == "MaterialCount": material_count = prop[1]
                elif prop[0] == "PieceCount": piece_count = prop[1]
                elif prop[0] == "PartCount": part_count = prop[1]
                elif prop[0] == "BoneCount": bone_count = prop[1]
                elif prop[0] == "LocatorCount": locator_count = prop[1]
                elif prop[0] == "Skeleton": skeleton = prop[1]
                else: Print(dump_level, '\nW Unknown property in "Global" data: "%s"!', prop[0])
    return vertex_count, face_count, edge_count, material_count, piece_count, part_count, bone_count, locator_count, skeleton

def getMaterialProperties(section, dump_level):
    """Receives a Material section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    materials_alias = materials_effect = None
    for prop in section.props:
        if prop[0] in ("", "#"): pass
        elif prop[0] == "Alias": materials_alias = prop[1]
        elif prop[0] == "Effect": materials_effect = prop[1]
        else: Print(dump_level, '\nW Unknown property in "Material" data: "%s"!', prop[0])
    return materials_alias, materials_effect

def getPieceProperties(section, dump_level):
    """Receives a Piece section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    ob_index = ob_material = ob_vertex_cnt = ob_edge_cnt = ob_face_cnt = ob_stream_cnt = 0
    for prop in section.props:
        if prop[0] in ("", "#"): pass
        elif prop[0] == "Index": ob_index = prop[1]
        elif prop[0] == "Material": ob_material = prop[1]
        elif prop[0] == "VertexCount": ob_vertex_cnt = prop[1]
        elif prop[0] == "EdgeCount": ob_edge_cnt = prop[1]
        elif prop[0] in ("TriangleCount", "FaceCount"): ob_face_cnt = prop[1]
        elif prop[0] == "StreamCount": ob_stream_cnt = prop[1]
        else: Print(dump_level, '\nW Unknown property in "Piece" data: "%s"!', prop[0])
    return ob_index, ob_material, ob_vertex_cnt, ob_edge_cnt, ob_face_cnt, ob_stream_cnt

def get_piece_5_streams(section, dump_level):
    """Receives a Piece (version 5) section and returns all its data in its own variables.
    For any item that fails to be found, it returns None."""
    mesh_vertices = []
    mesh_normals = []
    mesh_tangents = []
    mesh_rgb = {}
    mesh_rgba = {}
    mesh_uv = {}
    mesh_scalars = []
    mesh_tuv = []
    mesh_triangles = []
    for sec in section.sections:
        if sec.type == "Stream":
            stream_format = stream_tag = stream_alias_count = stream_aliases = None
            for prop in sec.props:
                # print('prop: %s' % prop)
                if prop[0] in ("", "#"): pass
                elif prop[0] == "Format": stream_format = prop[1]
                elif prop[0] == "Tag": stream_tag = prop[1]
                elif prop[0] == "AliasCount": stream_alias_count = prop[1]  ## TODO: UNUSED!
                elif prop[0] == "Aliases": stream_aliases = prop[1]         ## TODO: UNUSED!
                else: Print(dump_level, '\nW Unknown property in "Stream" data: "%s"!', prop[0])
            data_block = []
            for data_line in sec.data:
                data_block.append(data_line)
            # print('data_line: %s' % data_line)
            # print('stream_format: %s' % stream_format)
            # print('stream_tag: %s' % stream_tag)

            try:
                name_num = str("_" + str(int(stream_tag[-1])))
            except:
                name_num = ""

            if stream_tag == '_POSITION' and stream_format == 'FLOAT3': mesh_vertices = data_block
            elif stream_tag == '_NORMAL' and stream_format == 'FLOAT3': mesh_normals = data_block
            elif stream_tag == '_TANGENT' and stream_format == 'FLOAT3': mesh_tangents = data_block
            # elif stream_tag == '_RGB' and stream_format == 'FLOAT3': mesh_rgb = data_block
            # elif stream_tag == '_RGBA' and stream_format == 'FLOAT4': mesh_rgba = data_block
            elif stream_tag.startswith("_SCALAR") and stream_format == 'FLOAT':
                mesh_scalars = data_block                                       # only the last layer get created (!!!)
            elif stream_tag.startswith("_RGB") and stream_format == 'FLOAT3':
                mesh_rgb[str('Col' + name_num)] = data_block
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_RGBA") and stream_format == 'FLOAT4':
                mesh_rgba[str('Col' + name_num)] = data_block
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_UV") and stream_format == 'FLOAT2':
                mesh_uv[str('UVMap' + name_num)] = data_block
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_TUV") and stream_format == 'FLOAT2':
                mesh_tuv = data_block                                           # only the last layer get created (!!!)
        elif sec.type == "Triangles":
            mesh_triangles = []
            for data_line in sec.data:
                data_line.reverse() # flip triangle normals
                mesh_triangles.append(data_line)
    return mesh_vertices, mesh_normals, mesh_tangents, mesh_rgb, mesh_rgba, mesh_scalars, mesh_uv, mesh_tuv, mesh_triangles

def get_piece_7_streams(section, dump_level):
    """Receives a Piece (version 7) section and returns all its data in its own variables.
    For any item that fails to be found, it returns None."""
    mesh_vertices = []
    mesh_normals = []
    mesh_tangents = []
    mesh_tuv = []
    mesh_faces = []
    mesh_face_materials = []
    mesh_edges = []
    mesh_uv = {} # Mesh UV layers
    mesh_rgb = {}
    mesh_rgba = {}
    mesh_scalars = {}
    for sec in section.sections:
        if sec.type == "Stream":
            stream_format = stream_tag = stream_name = stream_alias_count = stream_aliases = None
            for prop in sec.props:
                # print('prop: %s' % prop)
                if prop[0] in ("", "#"): pass
                elif prop[0] == "Format": stream_format = prop[1]
                elif prop[0] == "Tag": stream_tag = prop[1]
                elif prop[0] == "Name": stream_name = prop[1]
                elif prop[0] == "AliasCount": stream_alias_count = prop[1]  ## TODO: UNUSED!
                elif prop[0] == "Aliases": stream_aliases = prop[1]         ## TODO: UNUSED!
                else: Print(dump_level, '\nW Unknown property in "Stream" data: "%s"!', prop[0])
            data_block = []
            for data_line in sec.data:
                data_block.append(data_line)
                # print('data_line: %s' % data_line)
            # print('stream_format: %s' % stream_format)
            # print('stream_tag: %s' % stream_tag)
            if stream_tag == "_POSITION" and stream_format == "FLOAT3":
                mesh_vertices = data_block
            elif stream_tag.startswith("_SCALAR") and stream_format == "FLOAT":
                # key = "VGroup_" + stream_tag[-1]
                if stream_name not in mesh_scalars:
                    mesh_scalars[stream_name] = data_block
                else:
                    print('''\n(!!!) The same Vertex Group (scalar)? Shouldn't happen! (!!!)\n''')
                    # mesh_scalars[key].append(data_block)
        elif sec.type == "Faces":
            # print('  sec.data:\n%s' % str(sec.data))
            for data_section in sec.sections:
                if data_section.type == "Face":
                    for data_prop in data_section.props:
                        if data_prop[0] == "Index":
                            pass
                            #print('%s' % str(data_prop[1]))
                        elif data_prop[0] == "Material":
                            face_material = data_prop[1]
                            mesh_face_materials.append(face_material)
                        elif data_prop[0] == "Indices":
                            face_vertex_data = data_prop[1]
                            face_vertex_data.reverse() # flip triangle normals
                            mesh_faces.append(face_vertex_data)
                    face_stream_type = face_stream_name = face_stream_tag = None

                    for face_sec in data_section.sections:
                        for rec in face_sec.props:
                            if rec[0] == "Format": face_stream_type = rec[1]
                            elif rec[0] == "Name": face_stream_name = rec[1]
                            elif rec[0] == "Tag": face_stream_tag = rec[1]
                            else: print('     ...: %s' % str(rec[1]))
                        # print('   %s "%s" (%s) len: %s mat: %s' % (face_stream_tag, face_stream_name, face_stream_type, len(face_sec.data), face_material))

                        face_data_block = []
                        for data_line in face_sec.data:
                            face_data_block.append(data_line)

                        if face_stream_tag.startswith("_RGBA") and face_stream_type == "FLOAT4":
                            if face_stream_name not in mesh_rgba:
                                mesh_rgba[face_stream_name] = []
                            #print('      face_data_block:\n%s' % str(face_data_block))
                            mesh_rgba[face_stream_name].append(face_data_block)

                        elif face_stream_tag.startswith("_RGB") and face_stream_type == "FLOAT3":
                            if face_stream_name not in mesh_rgb:
                                mesh_rgb[face_stream_name] = []
                            #print('      face_data_block:\n%s' % str(face_data_block))
                            mesh_rgb[face_stream_name].append(face_data_block)

                        elif face_stream_tag.startswith("_UV") and face_stream_type == "FLOAT2":
                            if face_stream_name not in mesh_uv:
                                mesh_uv[face_stream_name] = []
                            mesh_uv[face_stream_name].append(face_data_block)
            #print('    mesh_rgb:\n%s' % str(mesh_rgb))

        elif sec.type == "Edges":
            for data_line in sec.data:
                mesh_edges.append(data_line)
    return mesh_vertices, mesh_normals, mesh_tangents, mesh_rgb, mesh_rgba, mesh_scalars, mesh_uv, mesh_tuv, mesh_faces, mesh_face_materials, mesh_edges

def getPartProperties(section, dump_level):
    """Receives a Part section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    part_piece_count = part_locator_count = 0
    part_name = part_pieces = part_locators = None
    for prop in section.props:
        if prop[0] in ("", "#"): pass
        elif prop[0] == "Name": part_name = prop[1]
        elif prop[0] == "PieceCount": part_piece_count = prop[1]
        elif prop[0] == "LocatorCount": part_locator_count = prop[1]
        elif prop[0] == "Pieces": part_pieces = prop[1]
        elif prop[0] == "Locators": part_locators = prop[1]
        else: Print(dump_level, '\nW Unknown property in "Part" data: "%s"!', prop[0])
    return part_name, part_piece_count, part_locator_count, part_pieces, part_locators

def getLocatorProperties(section, dump_level):
    """Receives a Locator section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    loc_index = 0
    loc_name = loc_hookup = loc_position = loc_rotation = loc_scale = None
    for prop in section.props:
        if prop[0] in ("", "#"): pass
        elif prop[0] == "Index": loc_index = prop[1]
        elif prop[0] == "Name": loc_name = prop[1]
        elif prop[0] == "Hookup": loc_hookup = prop[1]
        elif prop[0] == "Position": loc_position = prop[1]
        elif prop[0] == "Rotation": loc_rotation = prop[1]
        elif prop[0] == "Scale": loc_scale = prop[1]
        else: Print(dump_level, '\nW Unknown property in "Locator" data: "%s"!', prop[0])
    return loc_index, loc_name, loc_hookup, loc_position, loc_rotation, loc_scale

def getBonesProperties(section, dump_level):
    """Receives a Bones section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    bones = []
    if bpy.data.worlds[0].scs_globals.import_pis_file:
        for data in section.data:
            # print(' -data: %s' % str(data))
            bones.append(data)
    return bones

def getSkinStream(section, dump_level):
    """."""
    skin_stream = []
    stream_format = stream_tag = stream_item_count = stream_total_weight_count = stream_total_clone_count = None
    for prop in section.props:
        # print('prop: %s' % prop)
        if prop[0] in ("", "#"): pass
        elif prop[0] == "Format": stream_format = prop[1]
        elif prop[0] == "Tag": stream_tag = prop[1]
        elif prop[0] == "ItemCount": stream_item_count = prop[1]
        elif prop[0] == "TotalWeightCount": stream_total_weight_count = prop[1]
        elif prop[0] == "TotalCloneCount": stream_total_clone_count = prop[1]
    data_block = []
    for data_rec in section.data:
        data_block.append(data_rec)
        # print('data_rec: %s' % data_rec)
    # print('stream_format: %s' % stream_format)
    skin_stream.append((stream_format, stream_tag, stream_item_count, stream_total_weight_count, stream_total_clone_count, data_block))
    # if stream_tag == '_POSITION' and stream_format == 'FLOAT3': mesh_vertices = data_block
    return skin_stream

def getSkinProperties(section, dump_level):
    """Receives a Bones section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    skin_stream_cnt = None
    skin_streams = []
    for prop in section.props:
        if prop[0] in ("", "#"): pass
        elif prop[0] == "StreamCount": skin_stream_cnt = prop[1]
        else: Print(dump_level, '\nW Unknown property in "Bones" data: "%s"!', prop[0])
        for sec in section.sections:
            if sec.type == "SkinStream":
                skin_stream = getSkinStream(sec, dump_level)
                skin_streams.append(skin_stream)
    return skin_stream_cnt, skin_streams

###### START: Based on Blender2SCS GPL code by Simon Lusenc ######

class PMGHeader:
    """."""
    def __init__(self):
        """Header variables as they are named in game engine code. Blender2SCS names are in comments."""
        self.magic = 0                  ## version
        self.piece_count = 0            ## no_models
        self.part_count = 0             ## no_sections
        self.bone_count = 0             ## no_anims
        self.locator_count = 0          ## no_dummies

        self.center = 0                 ## part of mainBB = BoundingBox()
        self.radius = 0                 ## part of mainBB = BoundingBox()
        self.aabox_c1 = 0               ## part of mainBB = BoundingBox()
        self.aabox_c2 = 0               ## part of mainBB = BoundingBox()

        self.skeleton_offset = 0        ## anim_blocks_offset
        self.parts_offset = 0           ## sections_offset
        self.locators_offset = 0        ## dummies_offset
        self.pieces_offset = 0          ## models_offset

        self.string_pool_offset = 0     ## dummies_names_offset
        self.string_pool_size = 0       ## dummies_names_size

        self.skin_pool_offset = 0       ## anim_field_offset
        self.skin_pool_size = 0         ## anim_field_size

        self.dynamic_pool_offset = 0    ## geometry_offset
        self.dynamic_pool_size = 0      ## geometry_size

        self.static_pool_offset = 0     ## uv_map_offset
        self.static_pool_size = 0       ## uv_map_size

        self.index_pool_offset = 0      ## faces_offset
        self.index_pool_size = 0        ## faces_size

    def read_header(self, f):
        self.magic = io_utils.ReadUInt32(f)
        self.piece_count = io_utils.ReadUInt32(f)
        self.part_count = io_utils.ReadUInt32(f)
        self.bone_count = io_utils.ReadUInt32(f)
        self.locator_count = io_utils.ReadUInt32(f)

        self.center = io_utils.ReadFloatVector(f)           ## mainBB.center
        self.radius = io_utils.ReadFloat(f)                 ## mainBB.unknown4
        self.aabox_c1 = io_utils.ReadFloatVector(f)         ## mainBB.corner1
        self.aabox_c2 = io_utils.ReadFloatVector(f)         ## mainBB.corner2

        self.skeleton_offset = io_utils.ReadUInt32(f)
        self.parts_offset = io_utils.ReadUInt32(f)
        self.locators_offset = io_utils.ReadUInt32(f)
        self.pieces_offset = io_utils.ReadUInt32(f)

        self.string_pool_offset = io_utils.ReadUInt32(f)
        self.string_pool_size = io_utils.ReadUInt32(f)

        self.skin_pool_offset = io_utils.ReadUInt32(f)
        self.skin_pool_size = io_utils.ReadUInt32(f)

        self.dynamic_pool_offset = io_utils.ReadUInt32(f)
        self.dynamic_pool_size = io_utils.ReadUInt32(f)

        self.static_pool_offset = io_utils.ReadUInt32(f)
        self.static_pool_size = io_utils.ReadUInt32(f)

        self.index_pool_offset = io_utils.ReadUInt32(f)
        self.index_pool_size = io_utils.ReadUInt32(f)

class PMG:
    """Class for storing all PMG data."""
    def __init__(self, f):
        self.header = PMGHeader()
        self.header.read_header(f)
        # self.models = self.__read_models(f)
        # self.sections = self.__read_sections(f)
        # self.dummies = self.__read_dummies(f)

    def __read_models(self, f):
        f.seek(self.header.models_offset)
        i=0
        ret = []
        help_funcs.PrintDeb("Loading model headers...")
        while i < self.header.no_models:
            curr_m = PMGModel()
            curr_m.read_header(f)
            ret.append(curr_m)
            i+=1
        i=0
        help_funcs.PrintDeb("Reading model vertices...")
        while i < self.header.no_models:
            ret[i].read_verts(f)
            i+=1
        i=0
        help_funcs.PrintDeb("Reading model faces...")
        while i < self.header.no_models:
            ret[i].read_faces(f)
            i+=1
        
        help_funcs.PrintDeb("Done!")
        return ret     
    
    def __read_dummies(self, f):
        f.seek(self.header.dummies_offset)
        i=0
        ret = []
        help_funcs.PrintDeb("Loading dummies...")
        while i < self.header.no_dummies:
            curr_d = PMGDummy()
            curr_d.read_header(f)
            ret.append(curr_d)
            i+=1
        i=0
        help_funcs.PrintDeb("Getting dummies names data...")
        while i < self.header.no_dummies:
            f.seek(ret[i].name_blck_offset+self.header.dummies_names_offset)
            val=help_funcs.ReadChar(f)
            name = ""
            while val!=0:
                name += chr(val)
                val=help_funcs.ReadChar(f)
            ret[i].set_name_data(name)
            i+=1
            
        help_funcs.PrintDeb("Done!")
        return ret
    
    def __read_sections(self, f):
        f.seek(self.header.sections_offset)
        i=0
        ret = []
        model_i=0
        dummy_i=0
        help_funcs.PrintDeb("Loading sections...")
        while i < self.header.no_sections:
            curr_s = PMGSection()
            curr_s.read_header(f, model_i, dummy_i)
            model_i=curr_s.last_m
            dummy_i=curr_s.last_d
            ret.append(curr_s)
            i+=1
        help_funcs.PrintDeb("Done!")
        return ret
    
    def draw_model(self, name):
        help_funcs.PrintDeb("Creating and drawing model in blender...")
        bpy.ops.object.empty_add(type='CUBE',location=Vector())
        pmg_ob = bpy.context.active_object
        pmg_ob.empty_draw_size = 0.1
        pmg_ob.name = name
        #TODO be aware of this rotation
        pmg_ob.rotation_euler.x = 90.0*math.pi/180
        i=0
        while i<self.header.no_sections:
            self.sections[i].draw_section(i, self.models, self.dummies, pmg_ob)
            i+=1
        help_funcs.PrintDeb("Done!")
        return pmg_ob

###### END: Based on Blender2SCS GPL code by Simon Lusenc ######

def load(
        operator,
        context,
        filepath,
        ):

        ## DUMP LEVEL TABLE
        #  0 - Errors only
        #  1 - Errors and Warnings
        #  2 - Errors, Warnings and Info
        #  3 - Errors, Warnings, Info and Debugs
        #  4 - Errors, Warnings, Info, Debugs and Specials

    print("\n************************************")
    print("**      SCS PMG Importer %s      **" % version())
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # from bpy_extras.image_utils import load_image  # UNUSED

    result, objects, locators, armature, skeleton = process_pmg_data(
        filepath,
        preview_model=False,
        looks_and_materials=True,
        textures=True,
        uv=True,
        vc=True,
        vg=True,
        weld_smoothed=True,
        bones=True,
        shadow_casters=True,
        create_locators=True,
        parts_and_variants=True,
        )

    print("************************************")
    return result, objects, locators, armature, skeleton

def read_pmg_data(pmg_file, filename, filesize_perc, file_integrity):
    """."""
    import struct
    try:
        magic, piece_count, part_count, bone_count, locator_count = struct.unpack("5I", pmg_file.read(20))
        print(' > magic: %s' % magic)
        print(' > piece_count: %s' % piece_count)
        print(' > part_count: %s' % part_count)
        print(' > bone_count: %s' % bone_count)
        print(' > locator_count: %s\n' % locator_count)

        center_x, center_y, center_z, radius = struct.unpack("4f", pmg_file.read(16))
        print(' > center: <%s, %s, %s>' % (center_x, center_y, center_z))
        print(' > radius: %s\n' % radius)

        aabox_1, aabox_2, aabox_3, aabox_4, aabox_5, aabox_6 = struct.unpack("6f", pmg_file.read(24)) ## NOTE: Should be a "packed_aabox_t" - ???
        print(' > aabox: %s %s %s : %s %s %s\n' % (aabox_1, aabox_2, aabox_3, aabox_4, aabox_5, aabox_6))

        skeleton_offset, parts_offset, locators_offset, pieces_offset = struct.unpack("4I", pmg_file.read(16))
        print(' > skeleton_offset: %s' % skeleton_offset)
        print(' > parts_offset: %s' % parts_offset)
        print(' > locators_offset: %s' % locators_offset)
        print(' > pieces_offset: %s\n' % pieces_offset)

        string_pool_offset, string_pool_size = struct.unpack("2I", pmg_file.read(8))
        print(' > string_pool_offset: %s' % string_pool_offset)
        print(' > string_pool_size: %s\n' % string_pool_size)

        skin_pool_offset, skin_pool_size = struct.unpack("2I", pmg_file.read(8))
        print(' > skin_pool_offset: %s' % skin_pool_offset)
        print(' > skin_pool_size: %s\n' % skin_pool_size)

        dynamic_pool_offset, dynamic_pool_size = struct.unpack("2I", pmg_file.read(8))
        print(' > dynamic_pool_offset: %s' % dynamic_pool_offset)
        print(' > dynamic_pool_size: %s\n' % dynamic_pool_size)

        static_pool_offset, static_pool_size = struct.unpack("2I", pmg_file.read(8))
        print(' > static_pool_offset: %s' % static_pool_offset)
        print(' > static_pool_size: %s\n' % static_pool_size)

        index_pool_offset, index_pool_size = struct.unpack("2I", pmg_file.read(8))
        print(' > index_pool_offset: %s' % index_pool_offset)
        print(' > index_pool_size: %s\n' % index_pool_size)
    except:
        print("Can't read the unknown file!")
        return 0
    return file_integrity

def load_pmg_file(filepath):
    file_integrity = 0
    filename = os.path.basename(filepath)
    pmg_container = []

    bpy.context.window.cursor_modal_set('WAIT')
    # start = time.clock()                                                # zapnuti "stopek"
    bpy.context.window_manager.progress_begin(0.0, 1.0)

    try:
        pmg_file = open(filepath, "rb")
        filesize_perc = (os.stat(filepath)[6] / 100)                    # vypocet jednoho procenta velikosti souboru
        # bpy.context.window_manager.progress_update(0.0)
        file_integrity = read_pmg_data(pmg_file, filename, filesize_perc, file_integrity)
        pmg_file.close()
        # print('deBug - filesize: %s' % os.stat(filepath)[6])
    except IOError:
        bpy.context.window_manager.progress_end()
        bpy.context.window.cursor_modal_set('DEFAULT')
        print("!! ERROR: The file '%s' couldn't be loaded due to invalid filepath!" % filepath)
        # Draw.PupMenu("ERROR:%t|File couldn't be loaded! Please check the console.%x0")
        return [], ""

    bpy.context.window_manager.progress_end()
    # end = time.clock()                                                  # zastaveni "stopek"
    bpy.context.window.cursor_modal_set('DEFAULT')
    if file_integrity != 0:
        # print("'%s' imported successfully in %.2f seconds" % (filename, end-start))
        return pmg_container, ""
    else:
        # print("'%s' proceed with some errors in %.2f seconds" % (filename, end-start))
        # Draw.PupMenu("ERROR:%t|Some errors occured during '" + filename + "' file loading! Please check the console for details.%x0")
        return [], ""

def process_pmg_data(
        filepath,
        preview_model=False,
        looks_and_materials=True,
        textures=True,
        uv=True,
        vc=True,
        vg=True,
        weld_smoothed=True,
        bones=True,
        shadow_casters=True,
        create_locators=True,
        parts_and_variants=True,
        ):
    """."""
    context = bpy.context
    scs_globals = bpy.data.worlds[0].scs_globals
    dump_level = int(scs_globals.dump_level)
    ind = '    '

    # pmg_container, state = pix_parse.read_data(filepath, ind)
    pmg_container, state = load_pmg_file(filepath)
    pmg_container = []
    state = None

    if not pmg_container:
        Print(dump_level, '\nE File "%s" is empty!', str(filepath).replace("\\", "/"))
        return {'CANCELLED'}, None, None, None, None

## TEST PRINTOUTS
    # ind = '  '
    # for section in pmg_container:
        # print('SEC.: "%s"' % section.type)
        # for prop in section.props:
            # print('%sProp: %s' % (ind, prop))
        # for data in section.data:
            # print('%sdata: %s' % (ind, data))
        # for sec in section.sections:
            # print_section(sec, ind)
    # print('\nTEST - Source: "%s"' % pmg_container[0].props[1][1])
    # print('')

## TEST REEXPORT
    # from . import pix_write
    # ind = '    '
    # path, file = os.path.splitext(filepath)
    # export_filepath = str(path + '_reex' + file)
    # result = pix_write.write_data(pmg_container, export_filepath, ind)
    # if result == {'FINISHED'}:
        # Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
    # else:
        # Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)

## LOAD HEADER
    format_version, source, f_type, f_name, source_filename, author = getHeader(pmg_container, dump_level)

## LOAD GLOBALS
    vertex_count, face_count, edge_count, material_count, piece_count, part_count, bone_count, locator_count, skeleton = getGlobal(pmg_container, dump_level)
    if dump_level > 1: print('')

## DATA LOADING
    materials_data = {}
    objects_data = {}
    parts_data = {}
    locators_data = {}
    bones = None
    skin_data = []

    material_i = 0

    for section in pmg_container:
        if section.type == 'Material':
            if bpy.data.worlds[0].scs_globals.import_pmg_file:
                materials_alias, materials_effect = getMaterialProperties(section, dump_level)
                #print('\nmaterials_alias: %r' % materials_alias)
                #print('  materials_effect: %s' % materials_effect)
                materials_data[material_i] = (
                        materials_alias,
                        materials_effect,
                        )
                material_i += 1
        elif section.type == 'Piece':
            if bpy.data.worlds[0].scs_globals.import_pmg_file:
                ob_index, ob_material, ob_vertex_cnt, ob_edge_cnt, ob_face_cnt, ob_stream_cnt = getPieceProperties(section, dump_level)
                if format_version in (5, 6):
                    # print('Piece %i going to "get_piece_5_streams"...' % ob_index)
                    mesh_vertices, mesh_normals, mesh_tangents, mesh_rgb, mesh_rgba, mesh_scalars, mesh_uv, mesh_tuv, mesh_triangles = get_piece_5_streams(section, dump_level)
                    points_to_weld_list = []
                    if mesh_normals:
                        # print('Piece %i going to "make_posnorm_list"...' % ob_index)
                        if scs_globals.auto_welding:
                            posnorm_list = make_posnorm_list(mesh_vertices, mesh_normals)
                            # print('Piece %i going to "make_points_to_weld_list"...' % ob_index)
                            points_to_weld_list = make_points_to_weld_list(posnorm_list)
                    # print('Piece %i ...done' % ob_index)
                elif format_version in (7, ):
                    mesh_vertices, mesh_normals, mesh_tangents, mesh_rgb, mesh_rgba, mesh_scalars, mesh_uv, mesh_tuv, mesh_faces, mesh_face_materials, mesh_edges = get_piece_7_streams(section, dump_level)
                else:
                    Print(dump_level, '\nE Unknown PMG file version! Version %s is not currently supported by PMG importer.', format_version)
                    return {'CANCELLED'}, None, None, None, None

                piece_name = 'piece_' + str(ob_index)
                # print('piece_name: %s' % piece_name)
                # print('ob_material: %s' % ob_material)
                # print('mesh_vertices: %s' % mesh_vertices)
                # print('mesh_rgba 1: %s' % str(mesh_rgba))
                # print('mesh_uv count: %s' % len(mesh_uv))
                # print('mesh_triangles: %s' % mesh_triangles)
                # print('mesh_faces: %s' % mesh_faces)
                # print('mesh_face_materials: %s' % mesh_face_materials)
                # print('mesh_edges: %s' % mesh_edges)
                if format_version in (5, 6):
                    objects_data[ob_index] = (
                            context,
                            piece_name,
                            ob_material,
                            mesh_vertices,
                            mesh_normals,
                            mesh_tangents,
                            mesh_rgb,
                            mesh_rgba,
                            mesh_scalars,
                            mesh_uv,
                            mesh_tuv,
                            mesh_triangles,
                            points_to_weld_list,
                            )
                elif format_version in (7, ):
                    objects_data[ob_index] = (
                            context,
                            piece_name,
                            mesh_vertices,
                            mesh_normals,
                            mesh_tangents,
                            mesh_rgb,
                            mesh_rgba,
                            mesh_scalars,
                            mesh_uv,
                            mesh_tuv,
                            mesh_faces,
                            mesh_face_materials,
                            mesh_edges,
                            )
                # print('piece_count: %s' % str(piece_count))
                piece_count -= 1
        elif section.type == 'Part':
            if bpy.data.worlds[0].scs_globals.import_pmg_file:
                part_name, part_piece_count, part_locator_count, part_pieces, part_locators = getPartProperties(section, dump_level)
                # print('\npart_name: %r' % part_name)
                ##print('  part_piece_count: %i' % part_piece_count)
                ##print('  part_locator_count: %i' % part_locator_count)
                # print('  part_pieces: %s' % str(part_pieces))
                #print('  part_locators: %s' % str(part_locators))
                if part_pieces is not None and isinstance(part_pieces, int):
                    part_pieces = [part_pieces]
                if part_locators is not None and isinstance(part_locators, int):
                    part_locators = [part_locators]
                parts_data[part_name] = (
                        part_pieces,
                        part_locators,
                        )

                ## ADD PART TO INVENTORY
                utils.add_part_to_inventory(part_name)
        elif section.type == 'Locator':
            if bpy.data.worlds[0].scs_globals.import_pmg_file:
                loc_index, loc_name, loc_hookup, loc_position, loc_rotation, loc_scale = getLocatorProperties(section, dump_level)
                #print('\nloc_index: %r' % loc_index)
                #print('  loc_name: %s' % loc_name)
                #if loc_hookup:
                    #print('  loc_hookup: %s' % loc_hookup)
                #print('  loc_position: %s' % loc_position)
                #print('  loc_rotation: %s' % loc_rotation)
                #print('  loc_scale: %s' % loc_scale)
                locators_data[loc_index] = (
                        loc_name,
                        loc_hookup,
                        loc_position,
                        loc_rotation,
                        loc_scale,
                        )

## BONES
        elif section.type == 'Bones':
            if bpy.data.worlds[0].scs_globals.import_pis_file:
                bones = getBonesProperties(section, dump_level)
                # print('\nbones: %r' % str(bones))

## SKINNING
        elif section.type == 'Skin': ## Always only one skin in current SCS game implementation.
            if bpy.data.worlds[0].scs_globals.import_pmg_file and bpy.data.worlds[0].scs_globals.import_pis_file:
                skin_stream_cnt, skin_data = getSkinProperties(section, dump_level)
                # print('\nskin_stream_cnt: %r' % skin_stream_cnt)
                # print('skin_data: %r\n' % str(skin_data))

## CREATE MATERIALS
    if bpy.data.worlds[0].scs_globals.import_pmg_file and looks_and_materials:
        Print(dump_level, '\nI MATERIALS:')
        for mat_i in materials_data:
            #print('materials_data[mat_i]: %s' % str(materials_data[mat_i]))
            mat = create_material(
                    materials_data[mat_i][0],
                    materials_data[mat_i][1],
                    )
            if mat:
                Print(dump_level, 'I Created Material "%s"...', mat.name)
            else:
                Print(dump_level, 'I Existing Material "%s" reused...', materials_data[mat_i][0])

## PREPARE VERTEX GROUPS FOR SKINNING
    object_skinning = {}
    if bpy.data.worlds[0].scs_globals.import_pmg_file and bpy.data.worlds[0].scs_globals.import_pis_file and bones and skin_data:
        for skin in skin_data:
            for stream_i, stream in enumerate(skin):
                for data in stream[5]:
                    # print(' ORIGIN - data: %s' % str(data))
                    for rec in data['clones']:
                        obj = objects_data[rec[0]][1]
                        if obj not in object_skinning:
                            object_skinning[obj] = {}
                        vertex = rec[1]
                        for weight in data['weights']:
                            vg = bones[weight[0]]
                            if vg not in object_skinning[obj]:
                                object_skinning[obj][vg] = {}
                            vw = weight[1]
                            object_skinning[obj][vg][vertex] = vw

## CREATE OBJECTS
    Print(dump_level, '\nI OBJECTS:')
    objects = []
    skinned_objects = []
    for obj_i in objects_data:
        #print('objects_data[obj_i]: %s' % str(objects_data[obj_i]))
        if format_version in (5, 6):
            obj, duplicate_geometry = create_5_piece(
                    objects_data[obj_i][0], ## context
                    preview_model,
                    objects_data[obj_i][1], ## piece_name
                    objects_data[obj_i][2], ## ob_material
                    objects_data[obj_i][3], ## mesh_vertices
                    objects_data[obj_i][4], ## mesh_normals
                    objects_data[obj_i][5], ## mesh_tangents
                    objects_data[obj_i][6], ## mesh_rgb
                    objects_data[obj_i][7], ## mesh_rgba
                    objects_data[obj_i][8], ## mesh_scalars
                    object_skinning,
                    objects_data[obj_i][9], ## mesh_uv
                    objects_data[obj_i][10], ## mesh_tuv
                    objects_data[obj_i][11], ## mesh_triangles
                    materials_data,
                    objects_data[obj_i][12], ## points_to_weld_list
                    )
        elif format_version in (7, ):
            obj, duplicate_geometry = create_7_piece(
                    objects_data[obj_i][0], ## context
                    objects_data[obj_i][1], ## piece_name
                    objects_data[obj_i][2], ## mesh_vertices
                    objects_data[obj_i][3], ## mesh_normals
                    objects_data[obj_i][4], ## mesh_tangents
                    objects_data[obj_i][5], ## mesh_rgb
                    objects_data[obj_i][6], ## mesh_rgba
                    objects_data[obj_i][7], ## mesh_scalars
                    object_skinning,
                    objects_data[obj_i][8], ## mesh_uv
                    objects_data[obj_i][9], ## mesh_tuv
                    objects_data[obj_i][10], ## mesh_faces
                    objects_data[obj_i][11], ## mesh_face_materials
                    objects_data[obj_i][12], ## mesh_edges
                    materials_data,
                    )

        if len(duplicate_geometry[1]) != 0:
            print('WARNING - An object with duplicate geometry will be created...!')
            # for vertex_i, vertex in enumerate(duplicate_geometry[0]):
                # print('duplicate_geometry - vert: %s - %s (%i)' % (str(vertex), str(duplicate_geometry[0][vertex]), vertex_i))
            # for face_i, face in enumerate(duplicate_geometry[1]):
                # print('duplicate_geometry - face: %s - %s (%i)' % (str(face), str(duplicate_geometry[1][face]), face_i))
            # for uv_layer in duplicate_geometry[2]:
                # print('duplicate_geometry - uv_layer: %s' % str(uv_layer))
                # for vertex_i, vertex in enumerate(duplicate_geometry[2][uv_layer]):
                    # print('duplicate_geometry - uv_layer vert: %s - %s (%i)' % (str(vertex), str(duplicate_geometry[2][uv_layer][vertex]), vertex_i))

            import bmesh
            dup_name = "dup_" + objects_data[obj_i][1]
            mesh = bpy.data.meshes.new(dup_name)
            bm = bmesh.new()
            vertices = [duplicate_geometry[0][x] for x in duplicate_geometry[0]]
            io_utils.bm_make_vertices(bm, vertices)
            # duplicate_geometry = io_utils.bm_make_faces(bm, vertices, mesh_triangles, points_to_weld_list, mesh_uv)
            # if len(duplicate_geometry) != 0:
                # print('Ooouuuccchhh!!!')
            bm.to_mesh(mesh)
            mesh.update()
            obj = object_utils.object_data_add(context, mesh).object
            obj.name = dup_name
            # object.select = True
            # bpy.context.scene.objects.active = object
            # bpy.ops.object.shade_smooth()
            Print(dump_level, 'I Created Object "%s"...', obj.name)

        piece_name = objects_data[obj_i][1]
        if obj:
            # print('piece_name: %r - obj.name: %r' % (piece_name, obj.name))
            if piece_name in object_skinning:
                skinned_objects.append(obj)
            objects.append(obj)
            Print(dump_level, 'I Created Object "%s"...', obj.name)
## PARTS
            for part in parts_data:
                # print('parts_data["%s"]: %s' % (str(part), str(parts_data[part])))
                if parts_data[part][0] is not None:
                    if obj_i in parts_data[part][0]:
                        #print('  obj_i: %s - part: %s - parts_data[part][0]: %s' % (obj_i, part, parts_data[part][0]))
                        obj.scs_props.scs_part = part
        else:
            Print(dump_level, 'E "%s" - Object creation FAILED!', piece_name)

    if preview_model:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects: obj.select = True
        bpy.context.scene.objects.active = objects[0]
        bpy.ops.object.join()
        return objects[0], None, None, None, None

    # if uv:
    # if vc:
    # if vg:
    # if weld_smoothed:
    # if shadow_casters:
    # if parts_and_variants:

## CREATE MODEL LOCATORS
    locators = []
    if bpy.data.worlds[0].scs_globals.import_pmg_file and create_locators:
        Print(dump_level, '\nI MODEL LOCATORS:')
        for loc_i in locators_data:
            #print('locators_data[loc_i]: %s' % str(locators_data[loc_i]))
            loc = io_utils.create_locator_empty(
                    locators_data[loc_i][0], ## loc_name
                    locators_data[loc_i][2], ## loc_position
                    locators_data[loc_i][3], ## loc_rotation
                    locators_data[loc_i][4], ## loc_scale
                    1.0, ## loc_size
                    'Model', ## loc_type
                    locators_data[loc_i][1] ## loc_hookup
                    )
            # loc = create_locator(
                    # locators_data[loc_i][0], ## loc_name
                    # locators_data[loc_i][1], ## loc_hookup
                    # locators_data[loc_i][2], ## loc_position
                    # locators_data[loc_i][3], ## loc_rotation
                    # locators_data[loc_i][4], ## loc_scale
                    # # 'Model',  ## loc_type
                    # )
            locator_name = locators_data[loc_i][0]
            if loc:
                Print(dump_level, 'I Created Locator "%s"...', locator_name)
                locators.append(loc)
                for part in parts_data:
                    # print('parts_data[part]: %s' % str(parts_data[part]))
                    if parts_data[part][1] is not None:
                        if loc_i in parts_data[part][1]:
                            #print('  loc_i: %s - part: %s - parts_data[part][1]: %s' % (loc_i, part, parts_data[part][1]))
                            loc.scs_props.scs_part = part
            else:
                Print(dump_level, 'E "%s" - Locator creation FAILED!', locator_name)

## CREATE SKELETON (ARMATURE)
    armature = None
    if bpy.data.worlds[0].scs_globals.import_pis_file and bones:
        bpy.ops.object.add(type='ARMATURE', view_align=False, enter_editmode=False, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        # bpy.ops.object.armature_add(view_align=False, enter_editmode=False)
        bpy.ops.object.editmode_toggle()
        for bone in bones:
            bpy.ops.armature.bone_primitive_add(name=bone)
        bpy.ops.object.editmode_toggle()
        bpy.context.object.show_x_ray = True
        # bpy.context.object.data.show_names = True
        armature = bpy.context.object

## ADD ARMATURE MODIFIERS TO SKINNED OBJECTS
        if skin_data:
            for obj in objects:
                if obj in skinned_objects:
                    # print('...adding Armature modifier to %r...' % str(obj.name))
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_add(type='ARMATURE')
                    arm_modifier = None
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            arm_modifier = modifier
                            break
                    if arm_modifier:
                        arm_modifier.object = armature
                    obj.parent = armature

## WARNING PRINTOUTS
    if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
    if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
    if dump_level > 1: print('')
    return {'FINISHED'}, objects, locators, armature, skeleton
