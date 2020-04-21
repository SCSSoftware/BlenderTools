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
import array
from re import match
from mathutils import Vector
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.imp.transition_structs.terrain_points import TerrainPntsTrans
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.printout import handle_unused_arg
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def get_header(pim_container):
    """Receives PIM container and returns its format version as an integer.
    If the format version fail to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pim_container:
        if section.type == "Header":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "FormatVersion":
                    format_version = prop[1]
                elif prop[0] == "Source":
                    source = prop[1]
                elif prop[0] == "Type":
                    f_type = prop[1]
                elif prop[0] == "Name":
                    f_name = prop[1]
                elif prop[0] == "SourceFilename":
                    source_filename = prop[1]
                elif prop[0] == "Author":
                    author = prop[1]
                else:
                    lprint('\nW Unknown property in "Header" data: "%s"!', prop[0])
    return format_version, source, f_type, f_name, source_filename, author


def get_global(pim_container):
    """Receives PIM container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    vertex_count = face_count = edge_count = material_count = piece_count = part_count = bone_count = locator_count = piece_skin_count = 0
    skeleton = None
    for section in pim_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "VertexCount":
                    vertex_count = prop[1]
                elif prop[0] in ("TriangleCount", "FaceCount"):
                    face_count = prop[1]
                elif prop[0] == "EdgeCount":
                    edge_count = prop[1]
                elif prop[0] == "MaterialCount":
                    material_count = prop[1]
                elif prop[0] == "PieceCount":
                    piece_count = prop[1]
                elif prop[0] == "PartCount":
                    part_count = prop[1]
                elif prop[0] == "BoneCount":
                    bone_count = prop[1]
                elif prop[0] == "LocatorCount":
                    locator_count = prop[1]
                elif prop[0] == "Skeleton":
                    skeleton = prop[1]
                elif prop[0] == "PieceSkinCount":
                    piece_skin_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return vertex_count, face_count, edge_count, material_count, piece_count, part_count, bone_count, locator_count, skeleton, piece_skin_count


def get_material_properties(section):
    """Receives a Material section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    material_index = materials_alias = materials_effect = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            material_index = prop[1]
        elif prop[0] == "Alias":
            materials_alias = prop[1]
        elif prop[0] == "Effect":
            materials_effect = prop[1]
        else:
            lprint('\nW Unknown property in "Material" data: "%s"!', prop[0])
    return material_index, materials_alias, materials_effect


def get_piece_properties(section):
    """Receives a Piece section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    ob_index = ob_material = ob_vertex_cnt = ob_edge_cnt = ob_face_cnt = ob_stream_cnt = 0
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            ob_index = prop[1]
        elif prop[0] == "Material":
            ob_material = prop[1]
        elif prop[0] == "VertexCount":
            ob_vertex_cnt = prop[1]
        elif prop[0] == "EdgeCount":
            ob_edge_cnt = prop[1]
        elif prop[0] in ("TriangleCount", "FaceCount"):
            ob_face_cnt = prop[1]
        elif prop[0] == "StreamCount":
            ob_stream_cnt = prop[1]
        else:
            lprint('\nW Unknown property in "Piece" data: "%s"!', prop[0])
    return ob_index, ob_material, ob_vertex_cnt, ob_edge_cnt, ob_face_cnt, ob_stream_cnt


def _get_piece_streams(section):
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
            stream_aliases_count = 0
            stream_aliases = {}
            stream_format = stream_tag = None
            for prop in sec.props:
                # print('prop: %s' % prop)
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "Format":
                    stream_format = prop[1]
                elif prop[0] == "Tag":
                    stream_tag = prop[1]
                elif prop[0] == "AliasCount":
                    stream_aliases_count = prop[1]
                elif prop[0] == "Aliases":
                    if stream_aliases_count and stream_aliases_count > 0:
                        stream_aliases = prop[1].replace("\"", "").replace("  ", " ").split(" ")
                else:
                    lprint('\nW Unknown property in "Stream" data: "%s"!', prop[0])
            data_block = []
            for data_line in sec.data:
                data_block.append(data_line)
            # print('data_line: %s' % data_line)
            # print('stream_format: %s' % stream_format)
            # print('stream_tag: %s' % stream_tag)

            num_suffix = _convert_utils.str_to_int(stream_tag[-1])
            if num_suffix is None:
                num_suffix = ""
            else:
                num_suffix = "_" + str(num_suffix)

            if stream_tag == '_POSITION' and stream_format == 'FLOAT3':
                mesh_vertices = data_block
            elif stream_tag == '_NORMAL' and stream_format == 'FLOAT3':
                mesh_normals = data_block
            elif stream_tag == '_TANGENT' and stream_format == 'FLOAT3':
                mesh_tangents = data_block
            # elif stream_tag == '_RGB' and stream_format == 'FLOAT3': mesh_rgb = data_block
            # elif stream_tag == '_RGBA' and stream_format == 'FLOAT4': mesh_rgba = data_block
            elif stream_tag.startswith("_SCALAR") and stream_format == 'FLOAT':
                mesh_scalars = data_block  # only the last layer get created (!!!)
            elif stream_tag.startswith("_RGB") and stream_format == 'FLOAT3':
                mesh_rgb[str(_MESH_consts.default_vcol)] = data_block
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_RGBA") and stream_format == 'FLOAT4':
                mesh_rgba[str(_MESH_consts.default_vcol)] = data_block
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_UV") and stream_format == 'FLOAT2':
                mesh_uv[str(_MESH_consts.default_uv + num_suffix)] = {
                    "data": data_block,
                    "aliases": stream_aliases
                }
                # print('data_block.props: %s' % str(data_block))
            elif stream_tag.startswith("_TUV") and stream_format == 'FLOAT2':
                mesh_tuv = data_block  # only the last layer get created (!!!)
        elif sec.type == "Triangles":
            mesh_triangles = []
            for data_line in sec.data:
                data_line.reverse()  # flip triangle normals
                mesh_triangles.append(data_line)
    return mesh_vertices, mesh_normals, mesh_tangents, mesh_rgb, mesh_rgba, mesh_scalars, mesh_uv, mesh_tuv, mesh_triangles


def get_part_properties(section):
    """Receives a Part section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    part_piece_count = part_locator_count = 0
    part_name = part_pieces = part_locators = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            part_name = prop[1]
        elif prop[0] == "PieceCount":
            part_piece_count = prop[1]
        elif prop[0] == "LocatorCount":
            part_locator_count = prop[1]
        elif prop[0] == "Pieces":
            part_pieces = prop[1]
        elif prop[0] == "Locators":
            part_locators = prop[1]
        else:
            lprint('\nW Unknown property in "Part" data: "%s"!', prop[0])
    return part_name, part_piece_count, part_locator_count, part_pieces, part_locators


def get_locator_properties(section):
    """Receives a Locator section and returns its properties in its own variables.
    For any item that fails to be found, it returns None.

    :param section: Data section from imported PIM file
    :type section: SectionData
    :return: Properties with its values in list
    :rtype: list
    """
    loc_index = 0
    loc_name = loc_hookup = loc_position = loc_rotation = loc_scale = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            loc_index = prop[1]
        elif prop[0] == "Name":
            loc_name = prop[1]
        elif prop[0] == "Hookup":
            loc_hookup = _convert_utils.hookup_id_to_hookup_name(prop[1])
        elif prop[0] == "Position":
            loc_position = prop[1]
        elif prop[0] == "Rotation":
            loc_rotation = prop[1]
        elif prop[0] == "Scale":
            loc_scale = prop[1]
        else:
            lprint('\nW Unknown property in "Locator" data: "%s"!', prop[0])
    return loc_index, loc_name, loc_hookup, loc_position, loc_rotation, loc_scale


def get_bones_properties(section, import_pis_file):
    """Receives a Bones section and returns its properties in its own variables.
    For any item that fails to be found, it returns None.

    :param section: Data section from imported PIM file
    :type section: SectionData
    :param import_pis_file: Global setting whether to import PIS files
    :type import_pis_file: bool
    :return: Bone names in list
    :rtype: list of str
    """
    bones = []
    if import_pis_file:
        for data in section.data:
            # print(' -data: %s' % str(data))
            bones.append(data)
    return bones


def _get_skin_stream(section):
    skin_stream = []
    stream_format = stream_tag = stream_item_count = stream_total_weight_count = stream_total_clone_count = None
    for prop in section.props:
        # print('prop: %s' % prop)
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Format":
            stream_format = prop[1]
        elif prop[0] == "Tag":
            stream_tag = prop[1]
        elif prop[0] == "ItemCount":
            stream_item_count = prop[1]
        elif prop[0] == "TotalWeightCount":
            stream_total_weight_count = prop[1]
        elif prop[0] == "TotalCloneCount":
            stream_total_clone_count = prop[1]
    data_block = []
    for data_rec in section.data:
        data_block.append(data_rec)
        # print('data_rec: %s' % data_rec)
    # print('stream_format: %s' % stream_format)
    skin_stream.append((stream_format, stream_tag, stream_item_count, stream_total_weight_count, stream_total_clone_count, data_block))
    # if stream_tag == '_POSITION' and stream_format == 'FLOAT3': mesh_vertices = data_block
    return skin_stream


def _get_piece_skin_stream(section):
    piece_skin_stream = []
    stream_format = stream_tag = stream_item_count = stream_total_weight_count = stream_total_vertex_count = None
    for prop in section.props:
        # print('prop: %s' % prop)
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Format":
            stream_format = prop[1]
        elif prop[0] == "Tag":
            stream_tag = prop[1]
        elif prop[0] == "ItemCount":
            stream_item_count = prop[1]
        elif prop[0] == "TotalWeightCount":
            stream_total_weight_count = prop[1]
        elif prop[0] == "TotalVertexIndexCount":
            stream_total_vertex_count = prop[1]
    data_block = []
    for data_rec in section.data:
        data_block.append(data_rec)

    piece_skin_stream.append((stream_format, stream_tag, stream_item_count, stream_total_weight_count, stream_total_vertex_count, data_block))
    return piece_skin_stream


def get_skin_properties(section):
    """Receives a Bones section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    skin_stream_cnt = None
    skin_streams = []

    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "StreamCount":
            skin_stream_cnt = prop[1]
        else:
            lprint('\nW Unknown property in "Bones" data: "%s"!', prop[0])
        for sec in section.sections:
            if sec.type == "SkinStream":
                skin_stream = _get_skin_stream(sec)
                skin_streams.append(skin_stream)

    return skin_stream_cnt, skin_streams


def get_piece_skin_properties(section):
    skin_piece_idx = None
    skin_stream_cnt = None
    skin_streams = []

    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Piece":
            skin_piece_idx = prop[1]
        elif prop[0] == "StreamCount":
            skin_stream_cnt = prop[1]
        else:
            lprint('\nW Unknown property in "Bones" data: "%s"!', prop[0])
        for sec in section.sections:
            if sec.type == "PieceSkinStream":
                skin_stream = _get_piece_skin_stream(sec)
                skin_streams.append(skin_stream)

    return skin_piece_idx, skin_stream_cnt, skin_streams


def _create_piece(
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
        terrain_points_trans,
        ignore_backfaces=False
):
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_tangents", mesh_tangents)
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_scalars", mesh_scalars)
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_tuv", mesh_tuv)

    context.window_manager.progress_begin(0.0, 1.0)
    context.window_manager.progress_update(0)

    import_scale = _get_scs_globals().import_scale

    mesh = bpy.data.meshes.new(name)

    # COORDINATES TRANSFORMATION
    transformed_mesh_vertices = [_convert_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_vertices]

    context.window_manager.progress_update(0.1)

    # VISUALISE IMPORTED NORMALS (DEBUG)
    # visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale)

    # MESH CREATION
    bm = bmesh.new()

    # VERTICES
    _mesh_utils.bm_make_vertices(bm, transformed_mesh_vertices)
    context.window_manager.progress_update(0.2)

    # FACES
    mesh_triangles, back_triangles = _mesh_utils.bm_make_faces(bm, mesh_triangles, points_to_weld_list)
    context.window_manager.progress_update(0.3)

    # UV LAYERS
    if mesh_uv:
        for uv_layer_name in mesh_uv:
            _mesh_utils.bm_make_uv_layer(5, bm, mesh_triangles, uv_layer_name, mesh_uv[uv_layer_name]["data"])
    context.window_manager.progress_update(0.4)

    # VERTEX COLOR
    if mesh_rgba:
        mesh_rgb_final = mesh_rgba
    elif mesh_rgb:
        mesh_rgb_final = mesh_rgb
    else:
        mesh_rgb_final = []

    for vc_layer_name in mesh_rgb_final:
        max_value = mesh_rgb_final[vc_layer_name][0][0] / 2

        for vc_entry in mesh_rgb_final[vc_layer_name]:
            for i, value in enumerate(vc_entry):
                if max_value < value / 2:
                    max_value = value / 2

        if max_value > mesh.scs_props.vertex_color_multiplier:
            mesh.scs_props.vertex_color_multiplier = max_value

        _mesh_utils.bm_make_vc_layer(5, bm, vc_layer_name, mesh_rgb_final[vc_layer_name], mesh.scs_props.vertex_color_multiplier)

    context.window_manager.progress_update(0.5)

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()

    # NORMALS - has to be applied after bmesh creation as they are set directly to mesh
    if _get_scs_globals().import_use_normals:

        mesh.create_normals_split()

        # first set normals directly to loops
        for loop in mesh.loops:
            curr_n = _convert_utils.scs_to_blend_matrix() @ Vector(mesh_normals[loop.vertex_index])
            loop.normal[:] = curr_n

        # then we have to go trough very important step they say,
        # as without validation we get wrong result for some normals
        mesh.validate(clean_customdata=False)  # *Very* important to not remove lnors here!

        # set polygons to use smooth representation
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

        # finally fill clnors from loops normals and apply them (taken from official Blenders scripts)
        clnors = array.array('f', [0.0] * (len(mesh.loops) * 3))
        mesh.loops.foreach_get("normal", clnors)
        mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
        mesh.use_auto_smooth = True

        mesh.free_normals_split()
    else:
        # set polygons to use smooth representation only
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    context.window_manager.progress_update(0.6)

    # Create object out of mesh and link it to active layer collection.
    obj = bpy.data.objects.new(mesh.name, mesh)
    obj.scs_props.object_identity = obj.name
    obj.location = (0.0, 0.0, 0.0)
    context.view_layer.active_layer_collection.collection.objects.link(obj)

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    context.window_manager.progress_update(0.7)

    context.window_manager.progress_update(0.8)

    # TERRAIN POINTS (VERTEX GROUPS)
    for vertex_i, vertex_pos in enumerate(mesh_vertices):

        tp_entries = terrain_points_trans.get(vertex_pos)

        # add current vertex to all combinations of variants/nodes
        # from found terrain points transitional structures
        for tp_entry in tp_entries:

            # first 6 chars in vertex group name will represent variant index
            # this way we will be able to identify variant during vertex groups
            # cleanup if this vertex will be set to multiple variants
            vg_name = str(tp_entry.variant_i).zfill(6) + _OP_consts.TerrainPoints.vg_name_prefix + str(tp_entry.node_i)

            if vg_name not in obj.vertex_groups:
                obj.vertex_groups.new(name=vg_name)

            vertex_group = obj.vertex_groups[vg_name]
            vertex_group.add([vertex_i], 1.0, "REPLACE")

    # SKINNING (VERTEX GROUPS)
    if object_skinning:
        if name in object_skinning:
            for vertex_group_name in object_skinning[name]:
                vertex_group = obj.vertex_groups.new(name=vertex_group_name)
                for vertex_i, vertex in enumerate(object_skinning[name][vertex_group_name]):
                    weight = object_skinning[name][vertex_group_name][vertex]
                    if weight != 0.0:
                        if vertex in points_to_weld_list:
                            vertex = points_to_weld_list[vertex]
                        vertex_group.add([vertex], weight, "ADD")
        else:
            lprint('\nE Missing skin group %r! Skipping...', name)

    context.window_manager.progress_update(0.9)

    # DELETE ORPHAN VERTICES (LEFT IN THE GEOMETRY FROM SMOOTHING RECONSTRUCTION)
    if points_to_weld_list:
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bm.verts.ensure_lookup_table()
        for vert_i in points_to_weld_list.keys():
            bm.verts[vert_i].select_set(True)

        verts = [v for v in bm.verts if v.select]
        if verts:
            bmesh.ops.delete(bm, geom=verts, context='VERTS')

        # APPLYING BMESH TO MESH
        bm.to_mesh(mesh)
        bm.free()

    context.window_manager.progress_update(1.0)

    # MATERIAL
    if len(materials_data) > 0 and not preview_model:
        # Assign a material to the last slot
        used_material = bpy.data.materials[materials_data[ob_material][0]]
        obj.data.materials.append(used_material)

        # NOTE: we are setting texture aliases only first time to avoid duplicates etc.
        # So we assume that pieces which are using same material will also have same  uv aliases alignement
        if "scs_tex_aliases" not in used_material:

            alias_mapping = {}
            for uv_lay in mesh_uv:
                if "aliases" in mesh_uv[uv_lay]:

                    import re

                    for alias in mesh_uv[uv_lay]["aliases"]:
                        numbers = re.findall("\d+", alias)
                        number = numbers[len(numbers) - 1]
                        alias_mapping[number] = uv_lay

            used_material["scs_tex_aliases"] = alias_mapping

    context.window_manager.progress_end()

    # if back triangles are present, then create new object with
    # back triangles and merge it to original
    if len(back_triangles) > 0 and not ignore_backfaces:

        back_obj = _create_piece(context, preview_model, "back_" + name,
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
                                 back_triangles,
                                 materials_data,
                                 points_to_weld_list,
                                 terrain_points_trans,
                                 ignore_backfaces=True)

        lprint("W Found %s back face(s) without it's own vertices on object %r, additional vertices were added!",
               (len(back_obj.data.polygons), obj.name))

        # creation of back face object used all original vertices
        # for proper index accessing during binding all of the data blocks to vertices.
        # Because of that we have to remove vertices which are not really used
        # in back faces mesh, so called "loose" vertices
        back_obj.data = _mesh_utils.bm_delete_loose(back_obj.data)

        # finally join back object with original
        override = context.copy()
        override["active_object"] = obj
        override["selected_editable_objects"] = (obj, back_obj)
        bpy.ops.object.join(override)

    return obj


'''
def visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale):
    """
    This function will create an additional object with edges
    representing vertex normals to visualise imported normals.
    :param name:
    :param transformed_mesh_vertices:
    :param mesh_normals:
    :param import_scale:
    :return:
    """
    if mesh_normals:
        transformed_mesh_normals = [io_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_normals]
        mesh_norm_vizu = bpy.data.meshes.new(str(name + "_norm_vizu"))
        object_norm_vizu = bpy.data.objects.new(str(name + "_norm_vizu"), mesh_norm_vizu)
        bpy.context.scene.objects.link(object_norm_vizu)
        mesh_norm_vizu.vertices.add(len(transformed_mesh_vertices) * 2)
        mesh_norm_vizu.edges.add(len(transformed_mesh_vertices))
        vert_i = edge_i = 0

        # print(' ** transformed_mesh_vertices: %s' % str(transformed_mesh_vertices))
        # print(' ** mesh_normals: %s' % str(mesh_normals))
        # print(' ** transformed_mesh_normals: %s' % str(transformed_mesh_normals))

        for vert in range(len(transformed_mesh_vertices)):
            vert_co = transformed_mesh_vertices[vert]
            vert_no = transformed_mesh_normals[vert]
            mesh_norm_vizu.vertices[vert_i].co = vert_co
            vert_i += 1
            mesh_norm_vizu.vertices[vert_i].co = Vector(vert_co) + (Vector(vert_no) / 16)
            vert_i += 1
            mesh_norm_vizu.edges[edge_i].vertices = (vert_i - 1, vert_i - 2)
            edge_i += 1

        # mesh_norm_vizu.validate()
        mesh_norm_vizu.update()
        # object_norm_vizu.select = True
        # bpy.context.scene.objects.active = object_norm_vizu
    else:
        print("WARNING! 'visualise_normals' - NO MESH NORMALS PROVIDED!")
'''


def load_pim_file(context, filepath, terrain_points_trans=None, preview_model=False):
    """Loads the actual PIM file type. This is used also for loading of 'Preview Models'.

    :param filepath: File path to be imported
    :type filepath: str
    :param preview_model: Load geomety as Preview Model
    :type preview_model: bool
    :param terrain_points_trans: transitional structure with filled terrain points from PIP; or None
    :type terrain_points_trans: io_scs_tools.imp.transition_structs.terrain_points.TerrainPntsTrans | None
    :return: ({'FINISHED'}, objects, skinned_objects, locators, armature, skeleton) or preview model object
    :rtype: tuple | bpy.types.Object
    """

    # create empty terrain points transitional structure if none is passed
    if terrain_points_trans is None:
        terrain_points_trans = TerrainPntsTrans()

    scs_globals = _get_scs_globals()

    lprint("I Reading data from PIM file...")

    ind = '    '
    pim_container = _pix_container.get_data_from_file(filepath, ind)

    lprint("I Assembling data...")

    # LOAD HEADER
    format_version, source, f_type, f_name, source_filename, author = get_header(pim_container)

    if format_version not in (5,):
        lprint('\nE Unknown PIM file version! Version %r is not currently supported by PIM importer.', format_version)
        return {'CANCELLED'}, None, None, [], None, None

    # LOAD GLOBALS
    (vertex_count,
     face_count,
     edge_count,
     material_count,
     piece_count,
     part_count,
     bone_count,
     locator_count,
     skeleton,
     piece_skin_count) = get_global(pim_container)

    # DATA LOADING
    materials_data = {}
    objects_data = {}
    parts_data = {}
    locators_data = {}
    bones = {}
    skin_streams = []
    piece_skin_data = {}

    for section in pim_container:
        if section.type == 'Material':
            if scs_globals.import_pim_file:
                material_i, materials_alias, materials_effect = get_material_properties(section)
                # print('\nmaterials_alias: %r' % materials_alias)
                # print('  materials_effect: %s' % materials_effect)

                # suport legacy format without index
                if not material_i:
                    material_i = len(materials_data.keys())

                materials_data[material_i] = [
                    materials_alias,
                    materials_effect,
                ]
        elif section.type == 'Piece':
            if scs_globals.import_pim_file:
                ob_index, ob_material, ob_vertex_cnt, ob_edge_cnt, ob_face_cnt, ob_stream_cnt = get_piece_properties(section)
                piece_name = 'piece_' + str(ob_index)

                # print('Piece %i going to "get_piece_5_streams"...' % ob_index)
                (mesh_vertices,
                 mesh_normals,
                 mesh_tangents,
                 mesh_rgb,
                 mesh_rgba,
                 mesh_scalars,
                 mesh_uv,
                 mesh_tuv,
                 mesh_triangles) = _get_piece_streams(section)
                points_to_weld_list = {}
                if mesh_normals:
                    # print('Piece %i going to "make_posnorm_list"...' % ob_index)
                    if scs_globals.import_use_welding:
                        points_to_weld_list = _mesh_utils.make_points_to_weld_list(mesh_vertices,
                                                                                   mesh_normals,
                                                                                   mesh_rgb,
                                                                                   mesh_rgba,
                                                                                   scs_globals.import_welding_precision)

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

                # print('piece_name: %s' % piece_name)
                # print('ob_material: %s' % ob_material)
                # print('mesh_vertices: %s' % mesh_vertices)
                # print('mesh_rgba 1: %s' % str(mesh_rgba))
                # print('mesh_uv count: %s' % len(mesh_uv))
                # print('mesh_triangles: %s' % mesh_triangles)
                # print('mesh_faces: %s' % mesh_faces)
                # print('mesh_face_materials: %s' % mesh_face_materials)
                # print('mesh_edges: %s' % mesh_edges)
                # print('piece_count: %s' % str(piece_count))
                piece_count -= 1
        elif section.type == 'Part':
            if scs_globals.import_pim_file:
                part_name, part_piece_count, part_locator_count, part_pieces, part_locators = get_part_properties(section)
                # print('\npart_name: %r' % part_name)
                # print('  part_piece_count: %i' % part_piece_count)
                # print('  part_locator_count: %i' % part_locator_count)
                # print('  part_pieces: %s' % str(part_pieces))
                # print('  part_locators: %s' % str(part_locators))
                if part_pieces is not None and isinstance(part_pieces, int):
                    part_pieces = [part_pieces]
                if part_locators is not None and isinstance(part_locators, int):
                    part_locators = [part_locators]
                parts_data[part_name] = (
                    part_pieces,
                    part_locators,
                )
        elif section.type == 'Locator':
            if scs_globals.import_pim_file:
                loc_index, loc_name, loc_hookup, loc_position, loc_rotation, loc_scale = get_locator_properties(section)
                # print('\nloc_index: %r' % loc_index)
                # print('  loc_name: %s' % loc_name)
                # if loc_hookup:
                # print('  loc_hookup: %s' % loc_hookup)
                # print('  loc_position: %s' % loc_position)
                # print('  loc_rotation: %s' % loc_rotation)
                # print('  loc_scale: %s' % str(loc_scale))
                locators_data[loc_index] = (
                    loc_name,
                    loc_hookup,
                    loc_position,
                    loc_rotation,
                    loc_scale,
                )

        # BONES
        elif section.type == 'Bones':
            if scs_globals.import_pis_file:
                bones = get_bones_properties(section, scs_globals.import_pis_file)
                # print('\nbones: %r' % str(bones))

        # SKINNING
        elif section.type == 'Skin':  # Always only one skin in current SCS game implementation.
            if scs_globals.import_pim_file and scs_globals.import_pis_file:
                skin_stream_cnt, skin_streams = get_skin_properties(section)
                # print('\nskin_stream_cnt: %r' % skin_stream_cnt)
                # print('skin_data: %r\n' % str(skin_data))

        elif section.type == "PieceSkin":
            if scs_globals.import_pim_file and scs_globals.import_pis_file:
                skin_piece_idx, skin_stream_cnt, skin_piece_streams = get_piece_skin_properties(section)
                piece_skin_data[skin_piece_idx] = skin_piece_streams
                piece_skin_count -= 1

    # CREATE MATERIALS
    if scs_globals.import_pim_file and not preview_model:
        lprint("\nI ------ Creating materials: ------")

        for mat_i in materials_data:
            mat = bpy.data.materials.new(materials_data[mat_i][0])
            mat.scs_props.mat_effect_name = materials_data[mat_i][1]

            materials_data[mat_i].append(materials_data[mat_i][0])
            materials_data[mat_i][0] = mat.name
            lprint("I Created material %r...", (mat.name,))

        lprint("I ---------------------------------")

    # PREPARE VERTEX GROUPS FOR SKINNING
    object_skinning = {}
    if scs_globals.import_pim_file and scs_globals.import_pis_file and bones:
        if skin_streams:  # global skinning section
            for skin_stream in skin_streams:
                for stream_i, stream in enumerate(skin_stream):
                    for data in stream[5]:  # index 5 is data block, see _get_skin_stream
                        # print(' ORIGIN - data: %s' % str(data))
                        for rec in data['clones']:
                            obj = objects_data[rec[0]][1]  # piece name
                            if obj not in object_skinning:
                                object_skinning[obj] = {}
                            vertex = rec[1]
                            for weight in data['weights']:
                                vg = bones[weight[0]]
                                if vg not in object_skinning[obj]:
                                    object_skinning[obj][vg] = {}
                                vw = weight[1]
                                object_skinning[obj][vg][vertex] = vw
        elif piece_skin_data:  # or skinning per piece
            for piece_idx, piece_skin_streams in piece_skin_data.items():
                obj = objects_data[piece_idx][1]  # piece name
                for skin_stream in piece_skin_streams:
                    for stream_i, stream in enumerate(skin_stream):
                        for data in stream[5]:  # index 5 is data block, see _get_skin_stream
                            # print(' ORIGIN - data: %s' % str(data))
                            for vertex_idx in data['vertex_indices']:
                                if obj not in object_skinning:
                                    object_skinning[obj] = {}
                                for weight in data['weights']:
                                    vg = bones[weight[0]]
                                    if vg not in object_skinning[obj]:
                                        object_skinning[obj][vg] = {}
                                    vw = weight[1]
                                    object_skinning[obj][vg][vertex_idx] = vw

    # CREATE OBJECTS
    lprint("\nI ------ Creating mesh objects: -------")
    objects = []
    skinned_objects = []
    for obj_i in objects_data:

        # PARTS - search part first so preview model can possibly ignore objects with prescribed variant
        part_name = None
        for part in parts_data:
            if parts_data[part][0] is not None and obj_i in parts_data[part][0]:
                part_name = part.lower()

        if preview_model:

            # ignore pieces with "coll" parts
            if match(r'^coll([0-9]?|_.*)$', part_name):
                lprint("I Ignoring piece with part collision part name %r for preview model!", (part_name,))
                continue

            # ignore pieces with shadow and none material effects
            used_mat_effect = materials_data[objects_data[obj_i][2]][1]
            if ".shadowonly" in used_mat_effect or ".fakeshadow" in used_mat_effect or used_mat_effect.startswith("eut2.none"):
                lprint("I Ignoring piece with material having shadow or none effect for preview model!")
                continue

        # print('objects_data[obj_i]: %s' % str(objects_data[obj_i]))
        obj = _create_piece(
            objects_data[obj_i][0],  # context
            preview_model,
            objects_data[obj_i][1],  # piece_name
            objects_data[obj_i][2],  # ob_material
            objects_data[obj_i][3],  # mesh_vertices
            objects_data[obj_i][4],  # mesh_normals
            objects_data[obj_i][5],  # mesh_tangents
            objects_data[obj_i][6],  # mesh_rgb
            objects_data[obj_i][7],  # mesh_rgba
            objects_data[obj_i][8],  # mesh_scalars
            object_skinning,
            objects_data[obj_i][9],  # mesh_uv
            objects_data[obj_i][10],  # mesh_tuv
            objects_data[obj_i][11],  # mesh_triangles
            materials_data,
            objects_data[obj_i][12],  # points_to_weld_list
            terrain_points_trans,
        )

        piece_name = objects_data[obj_i][1]
        if obj:

            # make sure that objects are using Z depth calculation
            # comes handy when we have any kind of transparent materials.
            # Moreover as this property doesn't do any change on
            # none transparent materials we can easily set this to all imported objects
            obj.show_transparent = True

            if piece_name in object_skinning:
                skinned_objects.append(obj)
            else:
                objects.append(obj)

            lprint("I Created object %r (%s/%s)...", (obj.name, obj_i, len(objects_data)))

            # PARTS
            if part_name:
                obj.scs_props.scs_part = part_name
        else:
            lprint("E %r - Object creation FAILED!", piece_name)

    lprint("I -------------------------------------")

    if preview_model:

        # abort loading if no meshes inside imported model
        if len(objects) == 0 and len(skinned_objects) == 0:
            return None

        # get active object for joining meshes into it
        active_object = objects[0] if len(objects) > 0 else skinned_objects[0]

        override = context.copy()
        override["active_object"] = active_object
        override["selected_editable_objects"] = objects + skinned_objects
        bpy.ops.object.join(override)

        return active_object

    # CREATE MODEL LOCATORS
    locators = []
    if scs_globals.import_pim_file and not preview_model:
        lprint("\nI ------ Creating model locators: ------")

        for loc_i in locators_data:
            # print('locators_data[loc_i]: %s' % str(locators_data[loc_i]))
            loc = _object_utils.create_locator_empty(
                locators_data[loc_i][0],  # loc_name
                locators_data[loc_i][2],  # loc_position
                locators_data[loc_i][3],  # loc_rotation
                locators_data[loc_i][4],  # loc_scale
                1.0,  # loc_size
                'Model',  # loc_type
                locators_data[loc_i][1],  # loc_hookup
            )
            # loc = create_locator(
            # locators_data[loc_i][0],  # loc_name
            # locators_data[loc_i][1],  # loc_hookup
            # locators_data[loc_i][2],  # loc_position
            # locators_data[loc_i][3],  # loc_rotation
            # locators_data[loc_i][4],  # loc_scale
            # 'Model',  ## loc_type
            # )
            locator_name = locators_data[loc_i][0]
            if loc:
                lprint("I Created locator %r...", (locator_name,))
                locators.append(loc)
                for part in parts_data:
                    # print('parts_data[part]: %s' % str(parts_data[part]))
                    if parts_data[part][1] is not None:
                        if loc_i in parts_data[part][1]:
                            # print('  loc_i: %s - part: %s - parts_data[part][1]: %s' % (loc_i, part, parts_data[part][1]))
                            loc.scs_props.scs_part = part.lower()
            else:
                lprint("E %r - Locator creation FAILED!", (locator_name,))

        lprint("I --------------------------------------")

    # CREATE SKELETON (ARMATURE)
    armature = None
    if scs_globals.import_pis_file and bones:
        bpy.ops.object.add(type='ARMATURE')
        if bpy.app.version < (2, 82, 0):
            bpy.ops.object.editmode_toggle()
        for bone in bones:
            bpy.ops.armature.bone_primitive_add(name=bone)
        bpy.ops.object.editmode_toggle()
        # bpy.context.object.data.show_names = True
        armature = bpy.context.object

        # ADD ARMATURE MODIFIERS TO SKINNED OBJECTS
        for obj in skinned_objects:
            # print('...adding Armature modifier to %r...' % str(obj.name))
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='ARMATURE')
            arm_modifier = None
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    arm_modifier = modifier
                    break
            if arm_modifier:
                arm_modifier.object = armature
            obj.parent = armature

    # WARNING PRINTOUTS
    if piece_count < 0:
        lprint("W More Pieces found than were declared!")
    if piece_count > 0:
        lprint("W Some Pieces not found, but were declared!")
    if piece_skin_count > 0:
        lprint("W More PieceSkins found than were declared!")
    if piece_skin_count < 0:
        lprint("W Some PieceSkins not found, but were declared!")

    return {'FINISHED'}, objects, locators, armature, skeleton, materials_data.values()


def load(context, filepath, terrain_points_trans):
    """Loads the PIM file type.

    :param context: Blender Context
    :type context: bpy.types.Context
    :param filepath: File path to be imported
    :type filepath: str
    :param terrain_points_trans: transitional structure with filled terrain points from PIP; or None
    :type terrain_points_trans: io_scs_tools.imp.transition_structs.terrain_points.TerrainPntsTrans | None
    :return: (result, objects, locators, armature, skeleton)
    :rtype: tuple
    """

    print("\n************************************")
    print("**      SCS PIM Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    result, objects, locators, armature, skeleton, mats_info = load_pim_file(
        context,
        filepath,
        terrain_points_trans,
        preview_model=False
    )

    print("************************************")
    return result, objects, locators, armature, skeleton, mats_info
