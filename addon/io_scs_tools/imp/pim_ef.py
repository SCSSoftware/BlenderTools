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

# Copyright (C) 2017-2019: SCS Software

import bpy
import bmesh
import array
from mathutils import Vector
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.imp.pim import get_header
from io_scs_tools.imp.pim import get_global
from io_scs_tools.imp.pim import get_material_properties
from io_scs_tools.imp.pim import get_piece_properties
from io_scs_tools.imp.pim import get_part_properties
from io_scs_tools.imp.pim import get_locator_properties
from io_scs_tools.imp.pim import get_bones_properties
from io_scs_tools.imp.pim import get_skin_properties
from io_scs_tools.imp.pim import get_piece_skin_properties
from io_scs_tools.imp.transition_structs.terrain_points import TerrainPntsTrans
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.printout import handle_unused_arg
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def _get_piece_streams(section):
    """Receives a Piece (Exchange Format version) section and returns all its data in its own variables.
    For any item that fails to be found, it returns None."""
    mesh_vertices = []
    mesh_normals = []
    mesh_tangents = []
    mesh_tuv = []
    mesh_faces = []
    mesh_face_materials = []
    mesh_edges = []
    mesh_uv = {}  # Mesh UV layers
    mesh_uv_aliases = {}
    mesh_rgb = {}
    mesh_rgba = {}
    mesh_scalars = {}
    for sec in section.sections:
        if sec.type == "Stream":
            stream_format = stream_tag = stream_name = None
            for prop in sec.props:
                # print('prop: %s' % prop)
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "Format":
                    stream_format = prop[1]
                elif prop[0] == "Tag":
                    stream_tag = prop[1]
                elif prop[0] == "Name":
                    stream_name = prop[1]
                elif prop[0] == "AliasCount":
                    '''
                    NOTE: skipped for now as no data needs to be readed
                    stream_alias_count = prop[1]
                    '''
                    pass
                elif prop[0] == "Aliases":
                    '''
                    NOTE: skipped for now as no data needs to be readed
                    stream_aliases = prop[1]
                    '''
                    pass
                else:
                    lprint('\nW Unknown property in "Stream" data: "%s"!', prop[0])
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
                            # print('%s' % str(data_prop[1]))
                        elif data_prop[0] == "Material":
                            face_material = data_prop[1]
                            mesh_face_materials.append(face_material)
                        elif data_prop[0] == "Indices":
                            face_vertex_data = data_prop[1]
                            face_vertex_data.reverse()  # flip triangle normals
                            mesh_faces.append(face_vertex_data)
                    face_stream_type = face_stream_name = face_stream_tag = face_stream_aliases = None
                    for face_sec in data_section.sections:
                        face_stream_aliases_count = 0
                        for rec in face_sec.props:
                            if rec[0] == "Format":
                                face_stream_type = rec[1]
                            elif rec[0] == "Name":
                                face_stream_name = rec[1]
                            elif rec[0] == "Tag":
                                face_stream_tag = rec[1]
                            elif rec[0] == "AliasCount":
                                face_stream_aliases_count = rec[1]
                            elif rec[0] == "Aliases":
                                if face_stream_aliases_count and face_stream_aliases_count > 0:
                                    face_stream_aliases = rec[1].replace("\"", "").replace("  ", " ").split(" ")
                            else:
                                print('     ...: %s' % str(rec[1]))
                        # print('   %s "%s" (%s) len: %s mat: %s' % (face_stream_tag, face_stream_name,
                        # face_stream_type, len(face_sec.data), face_material))

                        face_data_block = []
                        for data_line in face_sec.data:
                            face_data_block.append(data_line)

                        if face_stream_tag.startswith("_NORMAL") and face_stream_type == "FLOAT3":
                            # print('      face_data_block:\n%s' % str(face_data_block))
                            mesh_normals.append(face_data_block)

                        elif face_stream_tag.startswith("_RGBA") and face_stream_type == "FLOAT4":
                            if face_stream_name not in mesh_rgba:
                                mesh_rgba[face_stream_name] = []
                            # print('      face_data_block:\n%s' % str(face_data_block))
                            mesh_rgba[face_stream_name].append(face_data_block)

                        elif face_stream_tag.startswith("_RGB") and face_stream_type == "FLOAT3":
                            if face_stream_name not in mesh_rgb:
                                mesh_rgb[face_stream_name] = []
                            # print('      face_data_block:\n%s' % str(face_data_block))
                            mesh_rgb[face_stream_name].append(face_data_block)

                        elif face_stream_tag.startswith("_UV") and face_stream_type == "FLOAT2":
                            if face_stream_name not in mesh_uv:
                                mesh_uv[face_stream_name] = []
                            mesh_uv[face_stream_name].append(face_data_block)

                            # save aliases per material index, because each material can have different aliases
                            # depending on the name of stream aka name of the uv layer
                            if face_material not in mesh_uv_aliases:
                                mesh_uv_aliases[face_material] = {}
                            if face_stream_name not in mesh_uv_aliases[face_material]:
                                mesh_uv_aliases[face_material][face_stream_name] = []

                            if face_stream_aliases:
                                for alias in face_stream_aliases:
                                    mesh_uv_aliases[face_material][face_stream_name].append(alias)
                                    # print('    mesh_rgb:\n%s' % str(mesh_rgb))

        elif sec.type == "Edges":
            for data_line in sec.data:
                mesh_edges.append(data_line)
    values = (
        mesh_vertices,
        mesh_normals,
        mesh_tangents,
        mesh_rgb,
        mesh_rgba,
        mesh_scalars,
        mesh_uv,
        mesh_uv_aliases,
        mesh_tuv,
        mesh_faces,
        mesh_face_materials,
        mesh_edges,
    )
    return values


def _create_piece(
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
        mesh_uv_aliases,
        mesh_tuv,
        mesh_faces,
        mesh_face_materials,
        mesh_edges,
        terrain_points_trans,
        materials_data,
):
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_normals", mesh_normals)
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_tangents", mesh_tangents)
    handle_unused_arg(__file__, _create_piece.__name__, "mesh_tuv", mesh_tuv)

    context.window_manager.progress_begin(0.0, 1.0)
    context.window_manager.progress_update(0)

    import_scale = _get_scs_globals().import_scale
    mesh = bpy.data.meshes.new(name)

    # COORDINATES TRANSFORMATION
    transformed_mesh_vertices = [_convert_utils.change_to_scs_xyz_coordinates(vec, import_scale) for vec in mesh_vertices]

    context.window_manager.progress_update(0.1)

    # VISUALISE IMPORTED NORMALS (DEBUG)
    # NOTE: NOT functional for PIM version 7 since mesh normals are not provided in per vertex fashion!
    # visualise_normals(name, transformed_mesh_vertices, mesh_normals, import_scale)

    bm = bmesh.new()

    # VERTICES
    _mesh_utils.bm_make_vertices(bm, transformed_mesh_vertices)
    context.window_manager.progress_update(0.2)

    # FACES
    # for fac_i, fac in enumerate(mesh_faces): print('     face[%i]: %s' % (fac_i, str(fac)))
    mesh_faces, back_faces = _mesh_utils.bm_make_faces(bm, mesh_faces, [])
    context.window_manager.progress_update(0.3)

    # SHARP EDGES
    # print('mesh_edges: %s' % str(mesh_edges))
    for edge in bm.edges:
        edge_verts = [edge.verts[0].index, edge.verts[1].index]
        edge_verts_inv = [edge.verts[1].index, edge.verts[0].index]
        if edge_verts in mesh_edges or edge_verts_inv in mesh_edges:
            # print('edge: %s' % str(edge_verts))
            edge.smooth = False
    context.window_manager.progress_update(0.4)

    # UV LAYERS
    if mesh_uv:
        for uv_layer_name in mesh_uv:
            _mesh_utils.bm_make_uv_layer(7, bm, mesh_faces, uv_layer_name, mesh_uv[uv_layer_name])
    context.window_manager.progress_update(0.5)

    # VERTEX COLOR
    mesh_rgb_final = {}
    if mesh_rgba:
        mesh_rgb_final.update(mesh_rgba)
    if mesh_rgb:
        mesh_rgb_final.update(mesh_rgb)

    for vc_layer_name in mesh_rgb_final:
        max_value = mesh_rgb_final[vc_layer_name][0][0][0] / 2

        for vc_entry in mesh_rgb_final[vc_layer_name]:
            for v_i in vc_entry:
                for i, value in enumerate(v_i):
                    if max_value < value / 2:
                        max_value = value / 2

        if max_value > mesh.scs_props.vertex_color_multiplier:
            mesh.scs_props.vertex_color_multiplier = max_value

        _mesh_utils.bm_make_vc_layer(7, bm, vc_layer_name, mesh_rgb_final[vc_layer_name], mesh.scs_props.vertex_color_multiplier)

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()

    # NORMALS - has to be applied after bmesh creation as they are set directly to mesh
    if _get_scs_globals().import_use_normals:

        mesh.create_normals_split()

        # first set normals directly to loops
        for poly_i, poly in enumerate(mesh.polygons):

            for poly_loop_i, loop_i in enumerate(poly.loop_indices):

                curr_n = _convert_utils.scs_to_blend_matrix() @ Vector(mesh_normals[poly_i][poly_loop_i])
                mesh.loops[loop_i].normal[:] = curr_n

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

    # SCALAR LAYERS
    if mesh_scalars:
        for sca_layer_name in mesh_scalars:
            vertex_group = obj.vertex_groups.new(name=sca_layer_name)
            for val_i, val in enumerate(mesh_scalars[sca_layer_name]):
                val = float(val[0])
                if val != 0.0:
                    vertex_group.add([val_i], val, "ADD")
    context.window_manager.progress_update(0.7)

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
                        vertex_group.add([vertex], weight, "ADD")
        else:
            lprint('\nE Missing skin group %r! Skipping...', name)

    # ADD EDGE SPLIT MODIFIER
    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add(type='EDGE_SPLIT')
    bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
    bpy.context.object.modifiers["EdgeSplit"].name = "ES_" + name

    # MATERIALS
    used_mat_indices = set()
    # print('\n  mesh_face_materials:\n%s' % str(mesh_face_materials))
    for mat_index in mesh_face_materials:
        used_mat_indices.add(mat_index)
    # print('  used_mats:\n%s' % str(used_mats))
    context.window_manager.progress_update(0.8)

    # ADD MATERIALS TO SLOTS
    # print('  materials_data:\n%s' % str(materials_data))
    mat_index_to_mat_slot_map = {}
    if len(materials_data) > 0:
        for used_mat_idx in used_mat_indices:
            material_name = materials_data[used_mat_idx][0]
            bpy.ops.object.material_slot_add()  # Add a material slot
            last_slot = obj.material_slots.__len__() - 1

            # now as we created slot and we know index of it, write down indices of material slots to dictionary
            # for later usage by assigning faces to proper slots
            mat_index_to_mat_slot_map[used_mat_idx] = last_slot

            # print('    used_mat: %s (%i) => %s : %s' % (str(used_mat), mat_i, str(last_slot), str(material)))
            obj.material_slots[last_slot].material = bpy.data.materials[material_name]  # Assign a material to the slot

            # NOTE: we are setting texture aliases only first time to avoid duplicates etc.
            # So we assume that pieces which are using same material will also have same uv aliases alignment
            used_material = bpy.data.materials[material_name]
            if "scs_tex_aliases" not in used_material:

                alias_mapping = {}
                for uv_lay in mesh_uv_aliases[used_mat_idx]:

                    import re

                    for alias in mesh_uv_aliases[used_mat_idx][uv_lay]:
                        numbers = re.findall("\d+", alias)
                        number = numbers[len(numbers) - 1]
                        alias_mapping[number] = uv_lay

                used_material["scs_tex_aliases"] = alias_mapping

    mesh = obj.data
    context.window_manager.progress_update(0.9)

    # APPLY MATERIAL SLOT INDICES TO FACES
    for face_i, face in enumerate(mesh.polygons):
        face.material_index = mat_index_to_mat_slot_map[mesh_face_materials[face_i]]
    context.window_manager.progress_update(1.0)

    return obj


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
    ind = '    '
    pim_container = _pix_container.get_data_from_file(filepath, ind)

    # LOAD HEADER
    format_version, source, f_type, f_name, source_filename, author = get_header(pim_container)

    if format_version not in (1,):
        lprint('\nE Unknown PIM.EF file version! Version %r is not currently supported by PIM.EF importer.', format_version)
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

                (mesh_vertices,
                 mesh_normals,
                 mesh_tangents,
                 mesh_rgb,
                 mesh_rgba,
                 mesh_scalars,
                 mesh_uv,
                 mesh_uv_aliases,
                 mesh_tuv,
                 mesh_faces,
                 mesh_face_materials,
                 mesh_edges) = _get_piece_streams(section)

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
                    mesh_uv_aliases,
                    mesh_tuv,
                    mesh_faces,
                    mesh_face_materials,
                    mesh_edges,
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
        lprint('\nI MATERIALS:')
        for mat_i in materials_data:
            mat = bpy.data.materials.new(materials_data[mat_i][0])
            mat.scs_props.mat_effect_name = materials_data[mat_i][1]

            materials_data[mat_i].append(materials_data[mat_i][0])
            materials_data[mat_i][0] = mat.name
            lprint('I Created Material "%s"...', mat.name)

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
    lprint('\nI OBJECTS:')
    objects = []
    skinned_objects = []
    for obj_i in objects_data:
        # print('objects_data[obj_i]: %s' % str(objects_data[obj_i]))
        obj = _create_piece(
            objects_data[obj_i][0],  # context
            objects_data[obj_i][1],  # piece_name
            objects_data[obj_i][2],  # mesh_vertices
            objects_data[obj_i][3],  # mesh_normals
            objects_data[obj_i][4],  # mesh_tangents
            objects_data[obj_i][5],  # mesh_rgb
            objects_data[obj_i][6],  # mesh_rgba
            objects_data[obj_i][7],  # mesh_scalars
            object_skinning,
            objects_data[obj_i][8],  # mesh_uv
            objects_data[obj_i][9],  # mesh_uv_aliases
            objects_data[obj_i][10],  # mesh_tuv
            objects_data[obj_i][11],  # mesh_faces
            objects_data[obj_i][12],  # mesh_face_materials
            objects_data[obj_i][13],  # mesh_edges
            terrain_points_trans,
            materials_data,
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

            lprint('I Created Object "%s"...', (obj.name,))

            # PARTS
            for part in parts_data:
                # print('parts_data["%s"]: %s' % (str(part), str(parts_data[part])))
                if parts_data[part][0] is not None:
                    if obj_i in parts_data[part][0]:
                        # print('  obj_i: %s - part: %s - parts_data[part][0]: %s' % (obj_i, part, parts_data[part][0]))
                        obj.scs_props.scs_part = part.lower()
        else:
            lprint('E "%s" - Object creation FAILED!', piece_name)

    if preview_model:

        bases = []
        # get the bases of newly created objects for override
        for base in bpy.context.scene.object_bases:
            if base.object in objects:
                bases.append(base)

        override = {
            'window': bpy.context.window,
            'screen': bpy.context.screen,
            'blend_data': bpy.context.blend_data,
            'scene': bpy.context.scene,
            'region': None,
            'area': None,
            'active_object': objects[0],
            'selected_editable_bases': bases
        }
        bpy.ops.object.join(override)

        return objects[0]

    # CREATE MODEL LOCATORS
    locators = []
    if scs_globals.import_pim_file and not preview_model:
        lprint('\nI MODEL LOCATORS:')
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
                lprint('I Created Locator "%s"...', locator_name)
                locators.append(loc)
                for part in parts_data:
                    # print('parts_data[part]: %s' % str(parts_data[part]))
                    if parts_data[part][1] is not None:
                        if loc_i in parts_data[part][1]:
                            # print('  loc_i: %s - part: %s - parts_data[part][1]: %s' % (loc_i, part, parts_data[part][1]))
                            loc.scs_props.scs_part = part.lower()
            else:
                lprint('E "%s" - Locator creation FAILED!', locator_name)

    # CREATE SKELETON (ARMATURE)
    armature = None
    if scs_globals.import_pis_file and bones:
        bpy.ops.object.add(type='ARMATURE', enter_editmode=False)
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
        lprint('W More Pieces found than were declared!')
    if piece_count > 0:
        lprint('W Some Pieces not found, but were declared!')
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
    print("**      SCS PIM.EF Importer       **")
    print("**      (c)2017 SCS Software      **")
    print("************************************\n")

    result, objects, locators, armature, skeleton, mats_info = load_pim_file(
        context,
        filepath,
        terrain_points_trans,
        preview_model=False
    )

    print("************************************")
    return result, objects, locators, armature, skeleton, mats_info
