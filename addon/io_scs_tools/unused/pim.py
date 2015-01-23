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

import bpy
from mathutils import Vector, Matrix
from io_scs_tools.utils.printout import lprint
from io_scs_tools.utils.printout import handle_unused_arg
from io_scs_tools.utils.info import get_tools_version as _get_tools_version
from io_scs_tools.utils.info import get_blender_version as _get_blender_version
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container


def _fill_header_section(file_name, output_type):
    """
    Fills up "Header" section.
    :return:
    """
    header_section = _SectionData("Header")
    if output_type.startswith('def'):
        header_section.props.append(("FormatVersion", output_type))
    else:
        header_section.props.append(("FormatVersion", int(output_type)))
    blender_version, blender_build = _get_blender_version()
    header_section.props.append(("Source", "Blender " + blender_version + blender_build + ", SCS Blender Tools: " + str(_get_tools_version())))
    header_section.props.append(("Type", "Model"))
    header_section.props.append(("Name", file_name))
    if output_type.startswith('def'):
        source_filename = str(bpy.data.filepath)
        if source_filename == "":
            source_filename = "Unsaved"
        header_section.props.append(("SourceFilename", source_filename))
        author = bpy.context.user_preferences.system.author
        if author:
            header_section.props.append(("Author", str(author)))
    return header_section


def _fill_global_section(file_name, vertex_cnt, face_cnt, edge_cnt, material_cnt, piece_cnt, part_cnt, bone_cnt, locator_cnt, output_type):
    """
    Fills up "Global" section.
    :param vertex_cnt:
    :param face_cnt:
    :param edge_cnt:
    :param material_cnt:
    :param piece_cnt:
    :param part_cnt:
    :param bone_cnt:
    :param locator_cnt:
    :return:
    """
    global_section = _SectionData("Global")
    global_section.props.append(("VertexCount", vertex_cnt))
    if output_type.startswith('def'):
        global_section.props.append(("FaceCount", face_cnt))
        global_section.props.append(("EdgeCount", edge_cnt))
    else:
        global_section.props.append(("TriangleCount", face_cnt))
    global_section.props.append(("MaterialCount", material_cnt))
    global_section.props.append(("PieceCount", piece_cnt))
    global_section.props.append(("PartCount", part_cnt))
    global_section.props.append(("BoneCount", bone_cnt))
    global_section.props.append(("LocatorCount", locator_cnt))
    global_section.props.append(("Skeleton", str(file_name + ".pis")))
    return global_section


def _fill_material_sections(used_materials):
    """
    Fills up "Material" sections.
    :param used_materials:
    :return:
    """
    material_sections = []
    for material_i, material in enumerate(used_materials):
        if material is not None:
            material_section = _SectionData("Material")
            if isinstance(material, str):
                # mat_alias = "_empty_material_"
                mat_alias = str(material + "-_default_settings_")
                lprint('I "%s" material has been used to replace all unspecified materials.', (mat_alias,))
                # effect_name = "eut2.none"
                effect_name = "eut2.dif"
            else:
                shader_data = material.get("scs_shader_attributes", {})
                mat_alias = material.name
                effect_name = shader_data.get('effect', None)
                if not effect_name:
                    mat_alias = str("_" + material.name + "_-_default_settings_")
                    # effect_name = "eut2.none"
                    effect_name = "eut2.dif"
            material_section.props.append(("Alias", mat_alias))
            material_section.props.append(("Effect", effect_name))
            # print('material %i: "%s"' % (material_i, mat_alias))
            material_sections.append(material_section)
    return material_sections


def _fill_piece_sections_5(root_object, object_list, bone_list, scene, used_materials, offset_matrix, scs_globals):
    """Fills up "Piece" sections for file version 5.

    :param root_object: SCS Root Object
    :type root_object: bpy.types.Object
    :param object_list: Object for export
    :type object_list: list of Objects
    :param bone_list: Bones for export
    :type bone_list: list
    :param scene: Blender Scene to operate on
    :type scene: bpy.types.Scene
    :param used_materials: All Materials used in 'SCS Game Object'
    :type used_materials: list
    :param offset_matrix: Matrix for specifying of pivot point
    :type offset_matrix: Matrix
    :param scs_globals: SCS Tools Globals
    :type scs_globals: GlobalSCSProps
    :return: list of parameters
    :rtype: list
    """

    handle_unused_arg(__file__, _fill_piece_sections_5.__name__, "used_materials", used_materials)

    apply_modifiers = scs_globals.apply_modifiers
    exclude_edgesplit = scs_globals.exclude_edgesplit
    include_edgesplit = scs_globals.include_edgesplit
    piece_sections = []
    piece_index_obj = {}
    piece_index = global_vertex_count = global_face_count = 0

    # ----- START: SOLVE THIS!
    skin_list = []
    skin_weights_cnt = skin_clones_cnt = 0
    # -----   END: SOLVE THIS!

    print_info = False

    if print_info:
        print('used_materials: %s\n' % str(used_materials))
        print('object_list: %s\n' % str(object_list))

    # For each object...
    for obj_i, obj in enumerate(object_list):
        piece_index_obj[obj_i] = obj
        # Get all Materials from Object as they're set in material slots...
        object_materials = _object_utils.get_object_materials(obj)
        if print_info:
            print('  object_materials: %s' % str(object_materials))

        # Make Material dictionary (needed for getting rid of Material duplicities)...
        material_dict = _make_material_dict(object_materials)
        if print_info:
            for item in material_dict:
                print('    "%s" = %s' % (str(item), str(material_dict[item])))
            print('')

        # Get Object's Mesh data and list of temporarily disabled "Edge Split" Modifiers...
        mesh = _object_utils.get_mesh(obj)

        # SORT GEOMETRY
        piece_dict, skin_list, skin_weights_cnt, skin_clones_cnt = _get_geometry_dict(root_object,
                                                                                      obj,
                                                                                      mesh,
                                                                                      offset_matrix,
                                                                                      material_dict,
                                                                                      used_materials,
                                                                                      bone_list,
                                                                                      scs_globals)

        # DUMP
        if 0:
            for piece in piece_dict:
                print('Pm: %r' % piece)
                for data in piece_dict[piece]:
                    print('  Da: %r' % str(data))
                    if data == 'hash_dict':
                        if len(piece_dict[piece][data]) > 0:
                            for val in piece_dict[piece][data]:
                                print('    HD: %s:%s' % (str(val), str(piece_dict[piece][data][val])))
                        else:
                            print('    NO "hash_dict" Data!')
                    elif data == 'verts':
                        if len(piece_dict[piece][data]) > 0:
                            for val in piece_dict[piece][data]:
                                print('    Ve: %s' % str(val))
                        else:
                            print('    NO "verts" Data!')
                    elif data == 'faces':
                        if len(piece_dict[piece][data]) > 0:
                            for val in piece_dict[piece][data]:
                                print('    Fa: %s' % str(val))
                        else:
                            print('    NO "faces" Data!')
                print('')
            print('')

        # CREATE SECTIONS
        for piece in piece_dict:
            vertex_count = len(piece_dict[piece]['verts'])
            global_vertex_count += vertex_count
            face_count = len(piece_dict[piece]['faces'])
            global_face_count += face_count
            stream_sections = []

            # VERTEX STREAMS
            verts_data = {}
            for val in piece_dict[piece]['verts']:
                facevert_common_data, facevert_unique_data = val
                for data_key in facevert_common_data:
                    # print(' data_key: %s' % str(data_key))
                    if data_key == '_VG':
                        pass
                    else:
                        if data_key not in verts_data:
                            verts_data[data_key] = []
                        verts_data[data_key].append(facevert_common_data[data_key])
                for data_key in facevert_unique_data:
                    # print(' data_key: %s' % str(data_key))
                    if data_key == '_UV':
                        for layer_i, layer in enumerate(facevert_unique_data[data_key]):
                            layer_data_key = str(data_key + str(layer_i))
                            if layer_data_key not in verts_data:
                                verts_data[layer_data_key] = []
                            verts_data[layer_data_key].append(facevert_unique_data[data_key][layer])
                    if data_key == '_RGBA':
                        for layer_i, layer in enumerate(facevert_unique_data[data_key]):
                            if len(facevert_unique_data[data_key]) > 1:
                                layer_data_key = str(data_key + str(layer_i))
                            else:
                                layer_data_key = data_key
                            if layer_data_key not in verts_data:
                                verts_data[layer_data_key] = []
                            verts_data[layer_data_key].append(facevert_unique_data[data_key][layer])
            lprint('S verts_data: %s', (str(verts_data),))

            data_types = (
                '_POSITION', '_NORMAL', '_UV', '_UV0', '_UV1', '_UV2', '_UV3', '_UV4', '_UV5', '_UV6', '_UV7', '_UV8', '_UV9', '_RGBA', '_RGBA0',
                '_RGBA1', '_RGBA2', '_RGBA3', '_RGBA4', '_RGBA5', '_RGBA6', '_RGBA7', '_RGBA8', '_RGBA9', '_VG')
            add_uv = True
            add_rgba = False
            for data_type in data_types:
                if '_RGBA' not in verts_data:
                    add_rgba = True
                if data_type in verts_data:
                    if data_type.startswith('_UV'):
                        add_uv = False
                        stream_sections.append(_pix_container.make_stream_section(verts_data[data_type], data_type, (data_type,)))
                    else:
                        stream_sections.append(_pix_container.make_stream_section(verts_data[data_type], data_type, ()))

            # ADD DEFAULT UV LAYER
            if add_uv:
                lprint('I Adding default UV layer.')
                uv_dummy_data = []
                for vert in range(len(piece_dict[piece]['verts'])):
                    uv_dummy_data.append(Vector((0.0, 0.0)))
                stream_sections.append(_pix_container.make_stream_section(uv_dummy_data, '_UV0', ('_UV0',)))

            # ADD DEFAULT RGBA LAYER
            if add_rgba:
                lprint('I Adding default RGBA (vertex color) layer.')
                rgba_dummy_data = []
                for vert in range(len(piece_dict[piece]['verts'])):
                    rgba_dummy_data.append(Vector((1.0, 1.0, 1.0, 1.0)))
                stream_sections.append(_pix_container.make_stream_section(rgba_dummy_data, '_RGBA', ()))

            # PIECE PROPERTIES
            piece_section = _SectionData("Piece")
            piece_section.props.append(("Index", piece_index))
            piece_section.props.append(("Material", piece_dict[piece]['material_index']))
            piece_section.props.append(("VertexCount", vertex_count))
            piece_section.props.append(("TriangleCount", face_count))
            piece_section.props.append(("StreamCount", len(stream_sections)))
            piece_section.props.append(("", ""))
            piece_index += 1
            for stream_section in stream_sections:
                piece_section.sections.append(stream_section)

            # FACE STREAM
            stream_section = _SectionData("Triangles")
            stream_section.data = piece_dict[piece]['faces']
            piece_section.sections.append(stream_section)

            piece_sections.append(piece_section)

    return piece_sections, global_vertex_count, global_face_count, piece_index_obj, skin_list, skin_weights_cnt, skin_clones_cnt


def _fill_piece_sections_7(root_object, object_list, bone_list, scene, vg_list, used_materials, offset_matrix, scs_globals, output_type):
    """
    Fills up "Piece" sections for file version 7 (exchange format).
    :param object_list:
    :param bone_list:
    :param scene:
    :param vg_list:
    :param used_materials:
    :param offset_matrix:
    :return:
    """
    piece_sections = []  # container for all "Pieces"
    global_vertex_count = 0
    global_face_count = 0
    global_edge_count = 0
    piece_index_obj = {}
    skin_list = []
    skin_weights_cnt = 0
    skin_clones_cnt = 0
    for piece_index, obj in enumerate(object_list):
        mat_world = obj.matrix_world
        piece_index_obj[piece_index] = obj
        object_materials = _object_utils.get_object_materials(obj)  # get object materials

        # Get Object's Mesh data and list of temporarily disabled "Edge Split" Modifiers...
        mesh = _object_utils.get_mesh(obj)

        # VERTICES
        # TEMPORAL VERTEX STREAM DATA FORMAT:
        # example: ('_POSITION', [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), ...])
        # example: ('_SCALAR', [(0.0), (0.0), ...])

        stream_pos = ('_POSITION', [])
        # stream_nor = ('_NORMAL', [])
        # if scs_globals.export_vertex_groups:
        vg_layers_for_export, streams_vg = _object_utils.get_stream_vgs(obj)  # get Vertex Group layers (SCALARs)

        vertex_stream_count = 1
        vertex_streams = []
        stream_vg_container = []
        # print('bone_list: %s' % str(bone_list.keys))
        for vert_i, vert in enumerate(mesh.vertices):
            position = offset_matrix.inverted() * mesh.vertices[vert_i].co
            # scs_position = io_utils.change_to_scs_xyz_coordinates(mat_world * position, scs_globals.export_scale) ## POSITION
            scs_position = Matrix.Scale(scs_globals.export_scale,
                                        4) * _convert_utils.scs_to_blend_matrix().inverted() * mat_world * position  # POSITION
            stream_pos[1].append(scs_position)
            # stream_nor[1].append(io_utils.get_vertex_normal(mesh, vert_i))              # NORMAL
            if scs_globals.export_vertex_groups:
                if streams_vg:
                    vg_i = 0
                    for vg in vg_layers_for_export:  # weights (even unused) all vertices become 0.0
                        if vg.name in vg_list:
                            vg_weight = (_object_utils.get_vertex_group(vg, vert_i),)  # SCALARs
                            key = str("_SCALAR" + str(vg_i))
                            if vg_i == len(stream_vg_container) and len(stream_vg_container) != len(vg_layers_for_export):
                                stream_vg_container.append((vg.name, key, [vg_weight]))
                            else:
                                stream_vg_container[vg_i][2].append(vg_weight)
                            vg_i += 1

                            # SKINNING (OLD STYLE FOR PIM VER. 7)
            # if scs_globals.export_anim_file == 'anim':
            if root_object.scs_props.scs_root_animated == 'anim':
                skin_vector = scs_position  # NOTE: Vertex position - from Maya scaled *10 (old & unused in game engine)
                skin_weights = []
                for group in vert.groups:
                    for vg in vg_layers_for_export:
                        if vg.index == group.group:
                            for bone_i, bone in enumerate(bone_list):
                                if vg.name == bone.name:
                                    skin_weights.append((bone_i, group.weight))
                                    skin_weights_cnt += 1
                                    # print('vert: %i - group: %r (%i) - %s' % (vert_i, vg.name, bone_i, str(group.weight)))
                                    break
                            break
                skin_clones = ((piece_index, vert_i), )
                skin_clones_cnt += 1
                skin_list.append((skin_vector, skin_weights, skin_clones))

                # ##
        vertex_streams.append(stream_pos)
        # print('\nstream_pos:\n  %s' % str(stream_pos))
        # vertex_streams.append(stream_nor)
        # print('\nstream_nor:\n  %s' % str(stream_nor))
        for vg_stream in stream_vg_container:
            vertex_stream_count += 1
            vertex_streams.append(vg_stream)
            # print('\nvg_stream:\n  %s' % str(vg_stream))
        # FACES
        # TEMPORAL FACE STREAM DATA FORMAT:
        # faces = [face_data, face_data, ...]
        # face_data = (material, [vertex indices], [face-vertex streams])
        # face_streams = [('_UV0', [(0.0, 0.0), (0.0, 0.0), ...]), ...]
        # example: [(0, [0, 1, 2], [('_UV0', [(0.0, 0.0), (0.0, 0.0)]), ('_UV0', [(0.0, 0.0), (0.0, 0.0)])]), (), ...]

        faces = []
        face_cnt = 0
        uv_layers_exists = 1
        rgb_layers_exists = 1
        # print('used_materials: %s' % str(used_materials))
        for face_i, face in enumerate(mesh.polygons):
            face_cnt += 1
            streams_uv = None
            streams_vcolor = None
            if uv_layers_exists:
                requested_uv_layers, streams_uv = _mesh_utils.get_stream_uvs(mesh, scs_globals.active_uv_only)  # get UV layers (UVs)
                if not streams_uv:
                    uv_layers_exists = 0
            if rgb_layers_exists and scs_globals.export_vertex_color:
                if scs_globals.export_vertex_color_type_7 == 'rgb':
                    rgb_all_layers, streams_vcolor = _mesh_utils.get_stream_rgb(mesh, output_type, False)  # get Vertex Color layers (RGB)
                elif scs_globals.export_vertex_color_type_7 == 'rgbda':
                    rgb_all_layers, streams_vcolor = _mesh_utils.get_stream_rgb(mesh, output_type, True)  # get Vertex Color layers (
                    # RGBdA)
                else:
                    streams_vcolor = None  # TODO: Alpha from another layer
                if not streams_vcolor:
                    rgb_layers_exists = 0
            mat_index = used_materials.index(object_materials[face.material_index])
            # print('face-mat_index: %s; object_materials[f-m_i]: %s; used_materials.index(o_m[f-m_i]): %s' % (face.material_index,
            # object_materials[face.material_index], used_materials.index(object_materials[face.material_index])))
            face_verts = []
            for vert in face.vertices:
                face_verts.append(vert)
            face_verts = face_verts[::-1]  # revert vertex order in face
            # print('face_verts: %s' % str(face_verts))
            face_streams = []
            stream_fv_nor = ("_NORMAL", [])
            stream_fv_uv_container = []
            stream_fv_rgb_container = []
            stream_names = {}
            for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
                # edge_index = mesh.loops[loop_index].edge_index
                vert_index = mesh.loops[loop_index].vertex_index
                # print('face i.: %s\tloop i.: %s\tedge i.: %s\tvert i.: %s' % (face_i, loop_index, edge_index, vert_index))
                # Normals
                stream_fv_nor[1].append(offset_matrix.inverted() * Vector(_mesh_utils.get_vertex_normal(mesh, vert_index)))
                # UV Layers
                if streams_uv:
                    for uv_i, uv_l in enumerate(requested_uv_layers):
                        uv_values = _mesh_utils.get_face_vertex_uv(uv_l.data, loop_index, uv_i)
                        key = str("_UV" + str(uv_i))
                        if uv_i == len(stream_fv_uv_container) and len(stream_fv_uv_container) != len(requested_uv_layers):
                            stream_fv_uv_container.append((key, [uv_values]))
                            stream_names[key] = uv_l.name
                        else:
                            stream_fv_uv_container[uv_i][1].append(uv_values)
                            # Vertex Color Layers (RGB)
                if scs_globals.export_vertex_color:
                    if streams_vcolor:
                        for rgb_i, rgb_l in enumerate(rgb_all_layers):
                            if scs_globals.export_vertex_color_type_7 == 'rgb':
                                rgb_values = _mesh_utils.get_face_vertex_color(rgb_l.data, loop_index, False, rgb_i)
                                key = str("_RGB" + str(rgb_i))
                            elif scs_globals.export_vertex_color_type_7 == 'rgbda':
                                rgb_values = _mesh_utils.get_face_vertex_color(rgb_l.data, loop_index, True, rgb_i)
                                key = str("_RGBA" + str(rgb_i))
                            else:
                                streams_vcolor = None  # TODO: Alpha from another layer
                            if rgb_i == len(stream_fv_rgb_container) and len(stream_fv_rgb_container) != len(rgb_all_layers):
                                stream_fv_rgb_container.append((key, [rgb_values]))
                                stream_names[key] = rgb_l.name
                            else:
                                stream_fv_rgb_container[rgb_i][1].append(rgb_values)
                                # Data Assembling
            face_streams.append(stream_fv_nor)
            for stream in stream_fv_uv_container:
                face_streams.append(stream)
            for stream in stream_fv_rgb_container:
                face_streams.append(stream)
            face_data = (mat_index, face_verts, face_streams)
            faces.append(face_data)

        # SHARP EDGES
        sharp_edges = []
        for edge in mesh.edges:
            if edge.use_edge_sharp:
                sharp_edges.append(edge.vertices[:])

        # BUILD FACE SECTION
        faces_container = _SectionData("Faces")
        faces_container.props.append(("StreamCount", len(faces[0][2])))
        for face_i, face_data in enumerate(faces):
            face_container = _SectionData("Face")
            face_container.props.append(("Index", face_i))
            face_container.props.append(("Material", face_data[0]))
            face_container.props.append(("Indices", face_data[1]))
            for stream in face_data[2]:
                if stream[0] in stream_names:
                    face_container.sections.append(_pix_container.make_vertex_stream(stream, stream_names[stream[0]]))
                else:
                    face_container.sections.append(_pix_container.make_vertex_stream(stream))
            faces_container.sections.append(face_container)

        # BUILD PIECE SECTION
        piece_section = _SectionData("Piece")
        piece_section.props.append(("Index", piece_index))
        global_vertex_count += len(stream_pos[1])
        piece_section.props.append(("VertexCount", len(stream_pos[1])))
        global_face_count += face_cnt
        piece_section.props.append(("FaceCount", face_cnt))
        global_edge_count += len(sharp_edges)
        piece_section.props.append(("EdgeCount", len(sharp_edges)))
        piece_section.props.append(("StreamCount", vertex_stream_count))
        piece_section.props.append(("", ""))
        # vertex streams...
        for stream in vertex_streams:
            if len(stream) == 3:
                # print('\nstream:\n  %s' % str(stream))
                piece_section.sections.append(_pix_container.make_vertex_stream(stream[1:], stream[0]))
            else:
                piece_section.sections.append(_pix_container.make_vertex_stream(stream))
                # faces...
        piece_section.sections.append(faces_container)

        # BUILD AND STORE EDGE SECTION
        if sharp_edges:
            edges_container = _SectionData("Edges")
            for edge in sharp_edges:
                edges_container.data.append(edge)
            piece_section.sections.append(edges_container)

        # STORE PIECE SECTION
        piece_sections.append(piece_section)  # add a piece
    return piece_sections, global_vertex_count, global_face_count, global_edge_count, piece_index_obj, skin_list, skin_weights_cnt, skin_clones_cnt


def _fill_locator_sections(model_locator_list):
    """
    Fills up "Locator" sections.
    :param model_locator_list:
    :return:
    """
    locator_sections = []
    locator_i = 0

    for item in model_locator_list:
        # print('locator: "%s" - "%s"' % (item.name, str(item.scs_props.locator_model_hookup)))
        part_section = _SectionData("Locator")
        loc_name = _name_utils.tokenize_name(item.name)
        part_section.props.append(("Name", loc_name))
        if item.scs_props.locator_model_hookup:
            part_section.props.append(("Hookup", item.scs_props.locator_model_hookup.split(':', 1)[1].strip()))
        part_section.props.append(("Index", locator_i))
        loc, qua, sca = _convert_utils.get_scs_transformation_components(item.matrix_world)
        part_section.props.append(("Position", ["&&", loc]))
        part_section.props.append(("Rotation", ["&&", qua]))
        part_section.props.append(("Scale", ["&&", sca]))
        locator_sections.append(part_section)
        locator_i += 1
    return locator_sections


def _fill_bones_section(bone_list):
    """
    Fills up "Bones" section.
    :param bone_list:
    :return:
    """
    section = _SectionData("Bones")
    for bone in bone_list:
        section.data.append(("__string__", bone.name))
    return section


def _fill_skin_section(skin_list, skin_weights_cnt, skin_clones_cnt):
    """
    Fills up "Bones" section.
    :param skin_list:
    :param skin_weights_cnt:
    :param skin_clones_cnt:
    :return:
    """
    section = _SectionData("Skin")
    section.props.append(("StreamCount", 1))  # NOTE: Multiple streams are currently not supported in the game engine.
    stream_section = _SectionData("SkinStream")
    stream_section.props.append(("Format", "FLOAT3"))  # NOTE: Nonsense - an old relict.
    stream_section.props.append(("Tag", "_POSITION"))  # NOTE: Nonsense - an old relict.
    stream_section.props.append(("ItemCount", len(skin_list)))
    stream_section.props.append(("TotalWeightCount", skin_weights_cnt))
    stream_section.props.append(("TotalCloneCount", skin_clones_cnt))
    for skin in skin_list:
        stream_section.data.append(("__skin__", skin))
    section.sections.append(stream_section)
    return section


def _make_material_dict(object_materials):
    """Eliminate any material duplicities in slots.

    :param object_materials: All Object's Materials (should be ordered as they exists in material slots)
    :type object_materials: list
    :return: Keys are materials and values are lists of (material slot) indices in which they're set
    :rtype: dict
    """
    material_dict = {}
    if object_materials:
        for obj_mat_i, obj_mat in enumerate(object_materials):
            if obj_mat not in material_dict:
                material_dict[obj_mat] = []
            material_dict[obj_mat].append(obj_mat_i)
    return material_dict


def _create_index_material_dict(material_dict):
    """
    Takes Material dictionary and creates another dictionary, where
    keys are Material indexes and values are Materials.
    :param material_dict:
    :return:
    """
    index_material_dict = {}
    for material in material_dict:
        for index in material_dict[material]:
            index_material_dict[index] = material
    return index_material_dict


def _get_vertex_group_index(bone_name_list, group_name):
    """
    Takes a Bone list and Group name and returns index of the Group name
    in Bone list or None if the name is not within the list.

    :param bone_name_list: Bone names
    :type bone_name_list: list of str
    :param group_name: Group name for which we need to find the Bone index
    :type group_name: str
    :return: Bone index or None
    :rtype: int
    """
    for bone_name_i, bone_name in enumerate(bone_name_list):
        if bone_name == group_name:
            return bone_name_i
    return None


def _get_geometry_dict(root_object, obj, mesh, offset_matrix, material_dict, used_materials, bone_list, scs_globals):
    """
    :param root_object: SCS Root Object
    :type root_object: bpy.types.Object
    :param obj: Actual Object data
    :type obj: bpy.types.Object
    :param mesh: Object's Mesh data
    :type mesh: bpy.types.Mesh
    :param offset_matrix: Matrix for specifying of pivot point
    :type offset_matrix: Matrix
    :param material_dict: Materials used in current Object
    :type material_dict: dict
    :param used_materials: All Materials used in 'SCS Game Object'
    :type used_materials: list
    :param bone_list: Bones for export
    :type bone_list: list
    :param scs_globals: SCS Tools Globals
    :type scs_globals: GlobalSCSProps
    :return: Piece dictionary, Skin list, Skin weight count, Skin clone count
    :rtype: list
    """
    # Create Index => Material Dictionary...
    index_material_dict = _create_index_material_dict(material_dict)

    # Create Piece (Material) Dictionary...
    piece_dict = {}
    for material in material_dict:
        material_i = loc_material_i = material_dict[material][0]  # Eliminates multiple Material assignment

        # Set correct Material index for Piece
        for used_mat_i, used_mat in enumerate(used_materials):
            if material == used_mat:
                material_i = used_mat_i

        # print(' "%s" = %s => %s' % (str(material), str(material_dict[material]), str(loc_material_i)))

        piece_dict[loc_material_i] = {}
        piece_dict[loc_material_i]['material_index'] = material_i
        piece_dict[loc_material_i]['hash_dict'] = {}
        piece_dict[loc_material_i]['verts'] = []
        piece_dict[loc_material_i]['faces'] = []

    # DATA LAYERS
    uv_layers = mesh.tessface_uv_textures
    vc_layers = mesh.tessface_vertex_colors
    vertex_groups = obj.vertex_groups

    # Make sure if everything is recalculated...
    mesh.calc_tessface()
    mesh.calc_normals()
    mesh.calc_normals_split()

    for tessface in mesh.tessfaces:
        material = index_material_dict[tessface.material_index]
        loc_material_i = material_dict[material][0]  # Eliminates multiple Material assignment
        # print('tessface [%s]: %s' % (str(tessface.index).rjust(2, "0"), str(tessface.vertices)))
        # print(' "%s" = %s => %s' % (str(material), str(material_dict[material]), str(material_i)))
        face_verts = []

        for facevert_i, facevert in enumerate(tessface.vertices):
            facevert_common_data = {}
            facevert_unique_data = {}
            # POSITION
            facevert_co = offset_matrix.inverted() * obj.matrix_world * mesh.vertices[facevert].co
            # print('  facevert [%s] - position: %s' % (str(facevert).rjust(2, "0"), str(facevert_co)))
            scs_position = (Matrix.Scale(scs_globals.export_scale, 4) *
                            _convert_utils.scs_to_blend_matrix().inverted() *
                            facevert_co)
            facevert_common_data['_POSITION'] = scs_position

            # NORMAL
            facevert_no = mesh.vertices[facevert].normal
            # print('    normal: %s' % str(facevert_no))
            scs_normal = (_convert_utils.scs_to_blend_matrix().inverted() *
                          offset_matrix.inverted() *
                          obj.matrix_world *
                          facevert_no)

            # normalize normal vector and set it
            facevert_common_data['_NORMAL'] = Vector(scs_normal).normalized()

            # VERTEX GROUPS - for every vertices we need weight for every existing vertex group
            # print('    vg : %s len(%i)' % (str(vertex_groups), len(vertex_groups)))
            vert_grp = {}
            unused_groups = vertex_groups.keys()  # store all groups that are not yet used
            for vg_elem in mesh.vertices[facevert].groups:
                vert_grp[vertex_groups[vg_elem.group].name] = vg_elem.weight
                unused_groups.remove(vertex_groups[vg_elem.group].name)  # remove it from unused
            for group_name in unused_groups:  # for all unused groups that are left write weight 0
                vert_grp[group_name] = 0.0

            # print('      vert_grp: %s' % str(vert_grp))
            facevert_common_data['_VG'] = vert_grp

            # VERTEX UV LAYERS
            # print('    uv: %s len(%i)' % (str(uv_layers), len(uv_layers)))
            uv_lyr = {}
            if scs_globals.active_uv_only:
                uv = uv_layers.active.data[tessface.index].uv[facevert_i][:]
                scs_uv = _convert_utils.change_to_scs_uv_coordinates(uv)
                uv_lyr[uv_layers.active.name] = Vector(scs_uv)
            else:
                for layer_i, layer in enumerate(uv_layers.keys()):
                    uv = uv_layers[layer_i].data[tessface.index].uv[facevert_i][:]
                    # print('      uv%i: %r %s' % (layer_i, layer, str(uv)))
                    scs_uv = _convert_utils.change_to_scs_uv_coordinates(uv)
                    uv_lyr[layer] = Vector(scs_uv)
            # print('      uv_lyr: %s' % str(uv_lyr))
            facevert_unique_data['_UV'] = uv_lyr

            # VERTEX COLOR LAYERS
            # NOTE: In current PIM version 5 there should be only one Color layer present,
            # but I'll leave the multilayer solution here just for the case it could
            # be used in the future.
            active_vc_only = True
            # print('    vc : %s len(%i)' % (str(vc_layers), len(vc_layers)))
            if vc_layers and scs_globals.export_vertex_color:
                vc_lyr = {}
                if active_vc_only:
                    if facevert_i == 0:
                        vc = vc_layers.active.data[tessface.index].color1[:]
                    elif facevert_i == 1:
                        vc = vc_layers.active.data[tessface.index].color2[:]
                    elif facevert_i == 2:
                        vc = vc_layers.active.data[tessface.index].color3[:]
                    elif facevert_i == 3:
                        vc = vc_layers.active.data[tessface.index].color4[:]
                    if scs_globals.export_vertex_color_type == 'rgbda':
                        vc = (vc[0], vc[1], vc[2], 1.0)
                    # print('      vc%i: %r %s' % (layer_i, layer, str(vc)))
                    vc_lyr[vc_layers.active.name] = Vector(vc)
                else:
                    for layer_i, layer in enumerate(vc_layers.keys()):
                        if facevert_i == 0:
                            vc = vc_layers[layer_i].data[tessface.index].color1[:]
                        elif facevert_i == 1:
                            vc = vc_layers[layer_i].data[tessface.index].color2[:]
                        elif facevert_i == 2:
                            vc = vc_layers[layer_i].data[tessface.index].color3[:]
                        elif facevert_i == 3:
                            vc = vc_layers[layer_i].data[tessface.index].color4[:]
                        if scs_globals.export_vertex_color_type == 'rgbda':
                            vc = (vc[0], vc[1], vc[2], 1.0)
                        # print('      vc%i: %r %s' % (layer_i, layer, str(vc)))
                        vc_lyr[layer] = Vector(vc)
                # print('      vc_lyr: %s' % str(vc_lyr))
                facevert_unique_data['_RGBA'] = vc_lyr

            # DATA EVALUATION
            # print(' *** (%s) *** (%s) ***' % (str(facevert).rjust(3, "0"), str(tessface.vertices[facevert_i]).rjust(3, "0")))
            if facevert in piece_dict[loc_material_i]['hash_dict']:
                for vert in piece_dict[loc_material_i]['hash_dict'][facevert]:
                    # print(' %s > UD: %s' % (str(facevert).rjust(3, "0"), str(facevert_unique_data)))
                    vert_facevert_unique_data = piece_dict[loc_material_i]['verts'][vert][1]
                    # print(' %s < UD: %s' % (str(facevert).rjust(3, "0"), str(vert_facevert_unique_data)))
                    if facevert_unique_data == vert_facevert_unique_data:
                        # print(' %s O MATCH!' % str(facevert).rjust(3, "0"))
                        face_verts.append(vert)
                        break
                else:
                    # print(' %s - NOT in existing record...' % str(facevert).rjust(3, "0"))
                    new_vert_index = len(piece_dict[loc_material_i]['verts'])
                    piece_dict[loc_material_i]['hash_dict'][facevert].append(new_vert_index)  # Add the new vertex index to "hash_dict" record
                    face_verts.append(new_vert_index)  # Add the vertex to the actual face
                    piece_dict[loc_material_i]['verts'].append((facevert_common_data, facevert_unique_data))  # Create a new vertex to 'verts'
            else:
                # print(' %s | NOT a record... %s' % (str(facevert).rjust(3, "0"), str(facevert_common_data['_POSITION'][:])))
                new_vert_index = len(piece_dict[loc_material_i]['verts'])
                piece_dict[loc_material_i]['hash_dict'][facevert] = [new_vert_index]  # Create a new "hash_dict" record
                face_verts.append(new_vert_index)  # Add vertex to the actual face
                piece_dict[loc_material_i]['verts'].append((facevert_common_data, facevert_unique_data))  # Create a new vertex to 'verts'

        # FACES
        face_verts = face_verts[::-1]  # NOTE: Vertex order is swapped here to make the face normal flipped! Needs a check if it is right.
        if len(face_verts) == 4:  # Simple triangulation...
            piece_dict[loc_material_i]['faces'].append(face_verts[:3])
            piece_dict[loc_material_i]['faces'].append((face_verts[2], face_verts[3], face_verts[0]))
        else:
            piece_dict[loc_material_i]['faces'].append(face_verts)

    # BONE NAME LIST
    skin_list = []
    skin_weights_cnt = skin_clones_cnt = 0
    if bone_list:
        # if _get_scs_globals().export_anim_file == 'anim':
        if root_object.scs_props.scs_root_animated == 'anim':
            bone_name_list = []
            for bone_i, bone in enumerate(bone_list):
                bone_name_list.append(bone.name)
                # print('%s bone: %r' % (str(bone_i).rjust(3, "0"), str(bone.name)))

            # SKINNING DATA
            for vert in mesh.vertices:

                # SKIN VECTOR
                # position = Vector(mesh.vertices[vert_i].co)
                scs_position = (Matrix.Scale(scs_globals.export_scale, 4) *
                                _convert_utils.scs_to_blend_matrix().inverted() *
                                obj.matrix_world *
                                vert.co)
                # NOTE: Vertex position - when exported from Maya the value get scaled *10, but it is old & unused in game engine anyway.
                skin_vector = scs_position
                # print('    vertex: %s: %s' % (str(vert.index), str(piece_dict[material_i]['hash_dict'][vert.index])))

                # SKIN WEIGHTS
                skin_weights = []
                for vg_elem in vert.groups:
                    group_name = vertex_groups[vg_elem.group].name
                    if group_name in bone_name_list:
                        # print('      group: %r - %s' % (group_name, str(group.weight)))
                        bone_index = _get_vertex_group_index(bone_name_list, group_name)
                        skin_weights.append((bone_index, vg_elem.weight))
                        skin_weights_cnt += 1
                    else:
                        print('WARNING - Vertex Group %r is not a bone weight...' % group_name)  # TODO: Maybe handle this case? Useful?
                skin_clones = []

                # SKIN CLONES
                if loc_material_i is not None:
                    for v in piece_dict[loc_material_i]['hash_dict'][vert.index]:
                        skin_clones.append((0, v))
                        skin_clones_cnt += 1
                else:
                    print('ERROR - Material indices incorrect! (get_geometry_dict())')

                skin_list.append((skin_vector, skin_weights, skin_clones))

    mesh.free_normals_split()

    # print(' ** piece_dict: %s' % str(piece_dict))
    # print('')

    return piece_dict, skin_list, skin_weights_cnt, skin_clones_cnt


def export(context, root_object, used_parts, used_materials, object_list, model_locator_list, bone_list, vg_list, filepath):
    """
    :param context: Blender Context
    :type context: bpy.types.Context
    :param root_object: SCS Root Object
    :type root_object: bpy.types.Object
    :param used_parts: dictionary of used parts for current game object (it will get extended if some part from pic is not yet in)
    :type: dict
    :param used_materials: All Materials used in 'SCS Game Object'
    :type used_materials: list
    :param object_list: Objects for export
    :type object_list: list
    :param model_locator_list: Locators for export
    :type model_locator_list: list
    :param bone_list: Bones for export
    :type bone_list: list
    :param vg_list: ...
    :type vg_list: list
    :param filepath: ...
    :type filepath: str
    :return: Return state statuses (Usually 'FINISHED')
    :rtype: dict
    """
    scene = context.scene
    scs_globals = _get_scs_globals()
    output_type = scs_globals.output_type

    file_name = root_object.name
    offset_matrix = root_object.matrix_world

    print("\n************************************")
    print("**      SCS PIM Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # NEW SORTING
    # for piece_key in piece_keys_sorted:
    # piece_data = piece_dict[piece_key]
    # print('\n%r' % piece_key)
    # print('  piece_data: %s' % str(piece_data))
    # print('    obj: %r' % str(piece_data[0]))
    # print('    mat: %r' % str(piece_data[1]))
    # print('    uvs: %r' % str(piece_data[2]))
    # print('    vcl: %r' % str(piece_data[3]))
    # print('    arm: %r' % str(piece_data[4]))

    # SKELETONS AND ANIMATIONS
    # if scs_globals.export_anim_file != 'anim':
    if root_object.scs_props.scs_root_animated != 'anim':
        bone_list = []

    # DATA CREATION
    header_section = _fill_header_section(file_name, output_type)
    material_sections = _fill_material_sections(used_materials)

    piece_sections = []  # container for all "Pieces"
    global_vertex_count = 0
    global_face_count = 0
    global_edge_count = 0
    piece_index_obj = {}
    skin_list2 = []
    skin_weights_cnt = 0
    skin_clones_cnt = 0
    bones_section = None
    skin_section = None

    if not output_type.startswith('def'):
        (piece_sections,
         global_vertex_count,
         global_face_count,
         piece_index_obj,
         skin_list2,
         skin_weights_cnt,
         skin_clones_cnt) = _fill_piece_sections_5(root_object,
                                                   object_list,
                                                   bone_list,
                                                   scene,
                                                   used_materials,
                                                   offset_matrix,
                                                   scs_globals)
        global_edge_count = 0
    else:
        (piece_sections,
         global_vertex_count,
         global_face_count,
         global_edge_count,
         piece_index_obj,
         skin_list2,
         skin_weights_cnt,
         skin_clones_cnt) = _fill_piece_sections_7(root_object,
                                                   object_list,
                                                   bone_list,
                                                   scene,
                                                   vg_list,
                                                   used_materials,
                                                   offset_matrix,
                                                   scs_globals,
                                                   output_type)

    locator_sections = _fill_locator_sections(model_locator_list)
    part_sections = _pix_container.fill_part_sections(piece_index_obj, model_locator_list, used_parts)

    if bone_list:
        bones_section = _fill_bones_section(bone_list)
        skin_section = _fill_skin_section(skin_list2, skin_weights_cnt, skin_clones_cnt)

    global_section = _fill_global_section(file_name,
                                          global_vertex_count,
                                          global_face_count,
                                          global_edge_count,
                                          len(material_sections),
                                          len(piece_sections),
                                          len(part_sections),
                                          len(bone_list),
                                          len(locator_sections),
                                          output_type)

    # DATA ASSEMBLING
    pim_container = [header_section, global_section]
    for section in material_sections:
        pim_container.append(section)
    for section in piece_sections:
        pim_container.append(section)
    for section in part_sections:
        pim_container.append(section)
    for section in locator_sections:
        pim_container.append(section)
    if bone_list:
        pim_container.append(bones_section)
        # for section in skin_section: pim_container.append(section)
        pim_container.append(skin_section)

    # FILE EXPORT
    ind = "    "
    pim_filepath = str(filepath + ".pim")
    result = _pix_container.write_data_to_file(pim_container, pim_filepath, ind)

    # print("************************************")
    return result, piece_index_obj
