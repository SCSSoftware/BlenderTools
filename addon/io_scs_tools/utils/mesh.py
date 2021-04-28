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

# Copyright (C) 2013-2019: SCS Software

import bpy
import bmesh
from collections import deque
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.consts import VertexColorTools as _VCT_consts
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils import convert as _convert


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
    # print('vcol_lay: %s' % str(vcol_lay))

    for i, fac in enumerate(vcol_lay.data):
        print('fac: %s' % str(fac))
        print('rgb_layer: %s' % str(rgb_layer))
        fac_rgb = rgb_layer[i]
        print('fac_rgb: %s' % str(fac_rgb))
        print('fac.color1: %s' % str(fac.color1))
        print('fac.color2: %s' % str(fac.color2))
        print('fac.color3: %s' % str(fac.color3))
        print('fac.color4: %s' % str(fac.color4))
        # for j, rgb in enumerate(fac.color2):
        for j, fac_vert_rgb in enumerate(fac_rgb):
            # print('rgb: %s' % str(rgb))
            print('fac_rgb[j]: %s - fac_vert_rgb: %s' % (str(fac_rgb[j]), str(fac_vert_rgb)))
            # rgb[0], rgb[1], rgb[2] = fac_rgb[j]

    # for i, f in enumerate(vcol_lay.data):
    # NOTE: Colors dont come in right, needs further investigation.
    # ply_col = mesh_colors[i]
    # if len(ply_col) == 4:
    # f_col = f.color1, f.color2, f.color3, f.color4
    # else:
    # f_col = f.color1, f.color2, f.color3
    #
    # for j, col in enumerate(f_col):
    # col.r, col.g, col.b = ply_col[j]

    return {'FINISHED'}


def make_points_to_weld_list(mesh_vertices, mesh_normals, mesh_rgb, mesh_rgba, equal_decimals_count):
    """Makes a map of duplicated vertices indices into it's original counter part."""

    # take first present vertex color data
    if mesh_rgb:
        mesh_final_rgba = mesh_rgb
    elif mesh_rgba:
        mesh_final_rgba = mesh_rgba
    else:
        mesh_final_rgba = {}

    posnorm_dict_tmp = {}
    perc = 10 ** equal_decimals_count  # represent precision for duplicates
    for val_i, val in enumerate(mesh_vertices):

        key = (str(int(val[0] * perc)) + str(int(val[1] * perc)) + str(int(val[2] * perc)) +
               str(int(mesh_normals[val_i][0] * perc)) + str(int(mesh_normals[val_i][1] * perc)) + str(int(mesh_normals[val_i][2] * perc)))

        # also include vertex colors in key if present
        for vc_layer_name in mesh_final_rgba:
            for col_channel in mesh_final_rgba[vc_layer_name][val_i]:
                key += str(int(col_channel * perc))

        if key not in posnorm_dict_tmp:
            posnorm_dict_tmp[key] = [val_i]
        else:
            posnorm_dict_tmp[key].append(val_i)

    # create map for quick access to original vertex index via double vertex indices: (key: double vert index; value: original vert index)
    verts_map = {}
    for indices in posnorm_dict_tmp.values():
        # ignore entry if only one vertex was added to it (means there was no duplicates for it)
        if len(indices) <= 1:
            continue

        for idx in indices[1:]:
            verts_map[idx] = indices[0]  # fist index is original, rest are duplicates

    return verts_map


def set_sharp_edges(mesh, mesh_edges):
    """
    Takes a mesh and list of edges (2 vertex indices) and sets those edges
    as sharp in the mesh.
    :param mesh:
    :param mesh_edges:
    :return:
    """
    for edge in mesh.edges:
        edge_verts = [edge.vertices[0], edge.vertices[1]]
        if edge_verts in mesh_edges or edge_verts[::-1] in mesh_edges:
            edge.use_edge_sharp = True


def get_stream_rgb(mesh, output_type, dummy_alpha=False):
    """
    Takes a mesh and returns all vertex color layers existing in the mesh and requested
    number of empty containers for streams ("section_data" data type).
    :param mesh:
    :param output_type:
    :param dummy_alpha:
    :return:
    """
    if mesh.vertex_colors:
        rgb_all_layers = mesh.vertex_colors
        streams_vcolor = []
        for rgb_i in range(len(rgb_all_layers)):
            if output_type == 'def1':
                if dummy_alpha:
                    streams_vcolor.append(('_RGBA' + str(rgb_i), []))
                else:
                    streams_vcolor.append(('_RGB' + str(rgb_i), []))
            else:
                if dummy_alpha:
                    streams_vcolor.append(('_RGBA', []))
                else:
                    streams_vcolor.append(('_RGB', []))
                break
                # print('rgb_layer: %s' % str(rgb_all_layers))
                # for item in rgb_all_layers:
                # print('\trgb_layer: %s' % str(item))
    else:
        rgb_all_layers = None
        streams_vcolor = None
        lprint('I NO RGB layers in "%s" mesh!' % mesh.name)
    return rgb_all_layers, streams_vcolor


def get_stream_uvs(mesh, active_uv_only):
    """
    Takes a mesh and returns requested number of UV layers from the mesh and
    the same number of empty containers for streams ("section_data" data type).
    :param mesh:
    :param active_uv_only:
    :return:
    """
    if mesh.uv_layers:
        streams_uv = []
        if active_uv_only:
            requested_uv_layers = (mesh.uv_layers.active,)
            streams_uv.append(('_UV0', []))
        else:
            requested_uv_layers = mesh.uv_layers
            for uv_i in range(len(requested_uv_layers)):
                streams_uv.append(('_UV' + str(uv_i), []))
                # print('uv_layer: %s' % str(requested_uv_layers))
                # for item in requested_uv_layers:
                # print('\tuv_layer: %s' % str(item))
    else:
        requested_uv_layers = None
        streams_uv = None
        lprint('I NO UV layers in "%s" mesh!' % mesh.name)
    return requested_uv_layers, streams_uv


def get_vertex_normal(mesh, vert_index):
    """
    Takes a mesh and vertex index and returns normal of the vertex.
    :param mesh:
    :param vert_index:
    :return:
    """
    loop_vert_no = mesh.vertices[vert_index].normal
    # vrt_no = (loop_vert_no[0], loop_vert_no[1], loop_vert_no[2])
    vrt_no = (loop_vert_no[0], loop_vert_no[2], loop_vert_no[1] * -1)
    # print('\tNO   x:%f y:%f z:%f' % vrt_no)
    return vrt_no


def get_face_vertex_color(layer, loop_index, dummy_alpha=False, index=0):
    """
    Takes a vertex color layer and loop index and returns RGB values
    of the starting vertex of the loop part specified by loop index.
    :param layer:
    :param loop_index:
    :param dummy_alpha:
    :param index:
    :return:
    """
    # loop_vert_rgb = mesh.vertex_colors[0]
    loop_vert_rgb = layer[loop_index].color
    # print('\tRGB%i  %s' % (index, loop_vert_rgb))
    if dummy_alpha:
        vrt_rgb = (loop_vert_rgb[0], loop_vert_rgb[1], loop_vert_rgb[2], 1.0)
    else:
        vrt_rgb = (loop_vert_rgb[0], loop_vert_rgb[1], loop_vert_rgb[2])
    # print('\tRGB%i r:%f g:%f b:%f' % (index, vrt_rgb[0], vrt_rgb[1], vrt_rgb[2]))
    return vrt_rgb


def get_face_vertex_uv(layer, loop_index, index=0):
    """
    Takes a UV layer and loop index and returns UV values
    of the starting vertex of the loop part specified by loop index.
    :param layer:
    :param loop_index:
    :param index:
    :return:
    """
    loop_vert_uv = layer[loop_index].uv
    vrt_uv = (loop_vert_uv[0], -loop_vert_uv[1] + 1)
    # print('\tUV%i  u:%f v:%f' % (index, vrt_uv[0], vrt_uv[1]))
    return vrt_uv


def bm_make_vertices(bm, vertices):
    """
    Takes BMesh object and list of vertices as vectors
    and makes new vertices within the BMesh object.
    :param bm:
    :param vertices:
    :return:
    """
    if vertices:
        for v_co_i, v_co in enumerate(vertices):
            # print('%i v_co: %s' % (v_co_i, str(v_co)))
            vert = bm.verts.new(v_co)
            vert.index = v_co_i


def bm_make_faces(bm, faces, points_to_weld_list):
    """
    Takes BMesh object, list of faces as vertex indices, list of vertices for elimination (smoothing).
    Makes faces in provided BMesh object while separating
    back faces data and creating new faces list with fixed vertices indicies.

    :param bm: Bmesh to make faces in
    :type bm: bmesh.types.BMesh
    :param faces: faces which should be created, tuples of vertex indices
    :type faces: list[tuple[float]]
    :param points_to_weld_list:
    :return: new faces with correct indices without back faces and back faces
    :rtype: tuple[list[tuple[int]], list[tuple[int]]]
    """
    back_faces = []
    new_faces = []  # store faces in new array so indices to vertices will be fixed in the case of duplicate geometry

    # dictionaries only for quick search access
    new_faces_dict = {}
    back_faces_dict = {}

    if faces:
        for f_idx_i, f_idx in enumerate(faces):

            new_f_idx = []
            for v_idx in f_idx:
                new_v_idx = v_idx
                if v_idx in points_to_weld_list:
                    new_v_idx = points_to_weld_list[v_idx]
                new_f_idx.append(new_v_idx)

            try:

                bm.verts.ensure_lookup_table()
                bm.faces.new([bm.verts[i] for i in new_f_idx])
                new_faces.append(f_idx)
                new_faces_dict[str(f_idx)] = True

            except ValueError:
                lprint('D Face #%i vertex indices already used: %s', (f_idx_i, str(new_f_idx)))

                # with deque rotation we can determinate if current face
                # is really reverse face of already existing,
                # then we can add it as back face; otherwise we have to ignore it
                f_idx_deque = deque(reversed(f_idx))
                f_idx_deque.rotate(-1)

                for _ in range(len(f_idx)):
                    f_idx_deque.rotate()
                    f_idx_str = str(list(f_idx_deque))
                    if f_idx_str in new_faces_dict and f_idx_str not in back_faces_dict:
                        back_faces.append(f_idx)
                        back_faces_dict[f_idx_str] = True
                        lprint('D Face #%i is a reverse face, it will be added to extra back object.', (f_idx_i,))

    return new_faces, back_faces


def flip_faceverts(faces):
    """Reverse order of Face-Vertex indices (to flip the normals).

    :param faces: List of Faces (Face-Vertex indices)
    :type faces: list
    :return: List of Faces (Face-Vertex indices) in reversed order
    :rtype: list
    """
    flipped_faces = []
    for face in faces:
        flipped_face = []
        for vert in reversed(face):
            flipped_face.append(vert)
        flipped_faces.append(tuple(flipped_face))
    return flipped_faces


def bm_make_uv_layer(pim_version, bm, faces, uv_layer_name, uv_layer_data):
    """Add UV Layer to the BMesh object.

    :param pim_version: PIM version of the File from which data have been read
    :type pim_version: int
    :param bm: BMesh data to add UV Layer to
    :type bm: bmesh.types.BMesh
    :param faces: Faces as Vertex indices
    :type faces: list
    :param uv_layer_name: Name for the layer
    :type uv_layer_name: str
    :param uv_layer_data: UV Layer data
    :type uv_layer_data: list
    """
    uv_lay = bm.loops.layers.uv.new(uv_layer_name)
    for face_i, face in enumerate(bm.faces):
        # f_v = shift_values(faces[face_i])  # NOTE: Needed for Blender versions prior 2.69 (Blender bug)
        f_v = faces[face_i]  # NOTE: For Blender 2.69 and above
        # print('   face[%i]: %s / %s' % (face_i, str(face), str(f_v)))
        # print_values(" * f_verts", f_v, 10)
        for loop_i, loop in enumerate(face.loops):
            if pim_version < 6:
                loop[uv_lay].uv = _convert.change_to_scs_uv_coordinates(uv_layer_data[f_v[loop_i]])
            else:
                loop[uv_lay].uv = _convert.change_to_scs_uv_coordinates(uv_layer_data[face_i][loop_i])


def bm_make_vc_layer(pim_version, bm, vc_layer_name, vc_layer_data):
    """Add Vertex Color Layer to the BMesh object.

    :param pim_version: PIM version of the File from which data have been read
    :type pim_version: int
    :param bm: BMesh data to add Vertex Color Layer to
    :type bm: bmesh.types.BMesh
    :param vc_layer_name: Name for the layer
    :type vc_layer_name: str
    :param vc_layer_data: Vertex Color Layer data
    :type vc_layer_data: list
    """
    # only 5 and 7 versions are supported currently
    assert (pim_version == 5 or pim_version == 7)

    color_lay = bm.loops.layers.color.new(vc_layer_name)

    vc_alpha_layer_name = vc_layer_name + _MESH_consts.vcol_a_suffix
    if pim_version == 5 and len(vc_layer_data[0]) == 4:
        color_a_lay = bm.loops.layers.color.new(vc_alpha_layer_name)
    elif pim_version == 7 and len(vc_layer_data[0][0]) == 4:
        color_a_lay = bm.loops.layers.color.new(vc_alpha_layer_name)

    for face_i, face in enumerate(bm.faces):
        f_v = [x.index for x in face.verts]
        for loop_i, loop in enumerate(face.loops):
            alpha = -1.0
            if pim_version == 5:
                if len(vc_layer_data[0]) == 3:
                    vcol = vc_layer_data[f_v[loop_i]]
                else:
                    vcol = vc_layer_data[f_v[loop_i]][:3]
                    alpha = vc_layer_data[f_v[loop_i]][3]
            else:
                if len(vc_layer_data[face_i][0]) == 3:
                    vcol = vc_layer_data[face_i][loop_i]
                else:
                    vcol = vc_layer_data[face_i][loop_i][:3]
                    alpha = vc_layer_data[face_i][loop_i][3]

            vcol = (vcol[0] / 2, vcol[1] / 2, vcol[2] / 2, 1.0)
            loop[color_lay] = vcol

            if alpha != -1.0:
                assert color_a_lay
                vcol_a = (alpha / 2,) * 3 + (1.0,)
                loop[color_a_lay] = vcol_a


def bm_delete_loose(mesh):
    """Deletes loose vertices in the mesh.

    :param mesh: mesh on which loose vertices should be removed
    :type mesh: bpy.types.Mesh
    :return: cleanuped mesh
    :rtype: bpy.types.Mesh
    """

    bm = bmesh.new()
    bm.from_mesh(mesh)

    used_vertices = {}
    for f in bm.faces:
        for v in f.verts:
            if v.index not in used_vertices:
                used_vertices[v.index] = True

    for v in bm.verts:
        if v.index not in used_vertices:
            bm.verts.remove(v)

    bm.to_mesh(mesh)
    bm.free()


def bm_prepare_mesh_for_export(mesh, transformation_matrix, triangulate=False, flip=False):
    """Triangulates given mesh with bmesh module. Data are then saved back into original mesh!

    :param mesh: mesh data block to be triangulated and transformed
    :type mesh: bpy.types.Mesh
    :param transformation_matrix: transformation matrix which should be applied to mesh (usually root.matrix_world.inverted * obj.matrix_world)
    :type transformation_matrix: mathutils.Matrix
    :param triangulate: flag indicating if triangulation should be executed
    :type triangulate: bool
    :param flip: flag indicating if faces vertex order should be flipped
    :type flip: bool
    :return: Mapping of triangulated faces indices to original ones if triangulation is requested; otherwise empty dict is returned
    :rtype: dict[int|int]|None
    """

    faces_mapping = {}

    bm = bmesh.new()
    bm.from_mesh(mesh)

    if triangulate:
        res = bmesh.ops.triangulate(bm, faces=bm.faces)

        for new_face, old_face in res['face_map'].items():
            faces_mapping[new_face.index] = old_face.index

    bmesh.ops.transform(bm, matrix=transformation_matrix, verts=bm.verts)

    if flip:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    del bm

    return faces_mapping


def get_mesh_for_normals(mesh):
    """Get mesh prepared to be used for normals export.
    1. enables auto smooth and sets angle to 180 degress so that split normaals can be calculated (but no normals gets splitted because of it)
    2. calculates split normals

    :param mesh: original mesh data block of object
    :type mesh: bpy.types.Mesh
    :return: mew mesh prepared for normals export
    :rtype: bpy.types.Mesh
    """
    new_mesh = mesh.copy()

    # if user is not using auto smooth, then apply it now just for the porpuse of proper normals split calculation.
    if not new_mesh.use_auto_smooth:
        new_mesh.use_auto_smooth = True
        new_mesh.auto_smooth_angle = 3.14

    new_mesh.calc_normals_split()

    return new_mesh


def cleanup_mesh(mesh):
    """Frees normals split and removes mesh if possible.

    :param mesh: mesh to be cleaned
    :type mesh: bpy.types.Mesh
    """

    mesh.free_normals_split()
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh, do_unlink=True)


def vcoloring_rebake(mesh, vcolor_arrays, old_array_hash):
    """Rebakes vertex colors from 4 vertex layers(color, decal, ao, ao2) to the vertex color layer
    used by our shaders and exporter.

    Function supports hashing so colors do not get rebaked in case that given old hash is the same as newly
    calculated one.

    Additionally function will resize arrays if they don't have proper size.

    :param mesh: mesh on which we should rebake vertex colors
    :type mesh: bpy.types.Mesh
    :param vcolor_arrays: initialized arrays for saving loops colors when calculating. Should be 4 arrays of length: loop_count * 3.
    :type vcolor_arrays: list[numpy.ndarray]
    :param old_array_hash: hashed string of active vertex color array, used for determinating if colors have to be rebaked.
    :type old_array_hash: str | None
    :return: newly calculated hashed string of active vertex color array, that should be passed next time when rebake is called.
    :rtype: str | None
    """
    mesh_vcolors = mesh.vertex_colors

    # abort any baking if one of layers is missing or buffer arrays are not sufficitent
    if _VCT_consts.ColoringLayersTypes.Color not in mesh_vcolors:
        return None

    if _VCT_consts.ColoringLayersTypes.Decal not in mesh_vcolors:
        return None

    if _VCT_consts.ColoringLayersTypes.AO not in mesh_vcolors:
        return None

    if _VCT_consts.ColoringLayersTypes.AO2 not in mesh_vcolors:
        return None

    if len(vcolor_arrays) != 4:
        return None

    # correct buffers size if needed
    for i in range(0, 4):
        if len(vcolor_arrays[i]) != len(mesh.loops) * 4:
            vcolor_arrays[i].resize((len(mesh.loops) * 4,))

    color_loops = mesh_vcolors[_VCT_consts.ColoringLayersTypes.Color].data
    decal_loops = mesh_vcolors[_VCT_consts.ColoringLayersTypes.Decal].data
    ao_loops = mesh_vcolors[_VCT_consts.ColoringLayersTypes.AO].data
    ao2_loops = mesh_vcolors[_VCT_consts.ColoringLayersTypes.AO2].data

    # ensure the layers used to bake to
    if "Col" not in mesh_vcolors:
        mesh_vcolors.new(name="Col")

    if "Col_alpha" not in mesh_vcolors:
        mesh_vcolors.new(name="Col_alpha")

    # get vertex color data for hash calculation
    if mesh_vcolors.active.name == _VCT_consts.ColoringLayersTypes.Color:
        color_loops.foreach_get("color", vcolor_arrays[0])
    elif mesh_vcolors.active.name == _VCT_consts.ColoringLayersTypes.Decal:
        decal_loops.foreach_get("color", vcolor_arrays[0])
    elif mesh_vcolors.active.name == _VCT_consts.ColoringLayersTypes.AO:
        ao_loops.foreach_get("color", vcolor_arrays[0])
    elif mesh_vcolors.active.name == _VCT_consts.ColoringLayersTypes.AO2:
        ao2_loops.foreach_get("color", vcolor_arrays[0])

    new_array_hash = hash(vcolor_arrays[0].tobytes())

    # in case old and new hash are the same, do not rebake! This ensures smooth UI responsitivity in blender
    if old_array_hash == new_array_hash:
        return old_array_hash

    color_loops.foreach_get("color", vcolor_arrays[0])
    decal_loops.foreach_get("color", vcolor_arrays[1])
    ao_loops.foreach_get("color", vcolor_arrays[2])
    ao2_loops.foreach_get("color", vcolor_arrays[3])

    vcolor_arrays[0] = vcolor_arrays[0] * vcolor_arrays[2] * vcolor_arrays[3] * 4.0
    # alpha is donated only by decal layer color, thus we just comment it out
    # vcolor_arrays[1] = vcolor_arrays[1]

    mesh_vcolors["Col"].data.foreach_set("color", vcolor_arrays[0])
    mesh_vcolors["Col_alpha"].data.foreach_set("color", vcolor_arrays[1])

    return new_array_hash
