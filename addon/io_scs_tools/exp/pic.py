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
from io_scs_tools.internals.structure import SectionData as _SectionData
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.info import get_combined_ver_str
from io_scs_tools.utils.object import get_scs_root as _get_scs_root


def _fill_header_section(file_name, sign_export):
    """Fills up "Header" section."""
    section = _SectionData("Header")
    section.props.append(("FormatVersion", 2))
    section.props.append(("Source", get_combined_ver_str()))
    section.props.append(("Type", "Collision"))
    # section.props.append(("Name", str(os.path.basename(bpy.data.filepath)[:-6])))
    section.props.append(("Name", file_name))
    if sign_export:
        section.props.append(("SourceFilename", str(bpy.data.filepath)))
        author = bpy.context.user_preferences.system.author
        if author:
            section.props.append(("Author", str(author)))
    return section


def _fill_global_section(vertices, triangles, materials, pieces, parts, locators):
    """Fills up "Global" section."""
    section = _SectionData("Global")
    section.props.append(("VertexCount", vertices))
    section.props.append(("TriangleCount", triangles))
    section.props.append(("MaterialCount", materials))
    section.props.append(("PieceCount", pieces))
    section.props.append(("PartCount", parts))
    section.props.append(("LocatorCount", locators))
    return section


def _fill_coll_material_section():
    """Fills up "Material" section for convex colliders."""
    section = _SectionData("Material")
    section.props.append(("Alias", "convex"))  # Static value
    section.props.append(("Effect", "dry.void"))  # Static value
    return section


def _fill_piece_sections(convex_coll_locators, export_scale):
    """Fills up "Piece" sections for convex colliders."""

    len_vertices = 0
    len_faces = 0
    piece_sections = []
    index = 0
    for item in convex_coll_locators:
        stream_cnt = 0
        verts = item.scs_props.get("coll_convex_verts", 0)
        faces = item.scs_props.get("coll_convex_faces", 0)
        if verts:
            stream_cnt += 1

        len_vertices += len(verts)
        len_faces += len(faces)

        section = _SectionData("Piece")
        section.props.append(("Index", index))
        section.props.append(("Material", 0))
        section.props.append(("VertexCount", len(verts)))
        section.props.append(("TriangleCount", len(faces)))
        section.props.append(("StreamCount", stream_cnt))
        section.props.append(("", ""))

        # VERTICES
        if verts:
            vector_verts = []
            for vert in verts:
                # scs_position = Matrix.Scale(scs_globals.export_scale, 4) * io_utils.scs_to_blend_matrix().inverted() * mat_world * position ##
                # POSITION
                scs_position = Matrix.Scale(export_scale, 4) * _convert_utils.scs_to_blend_matrix().inverted() * Vector(vert)  # POSITION
                vector_verts.append(Vector(scs_position))
            section.sections.append(_pix_container.make_stream_section(vector_verts, "_POSITION", ()))

        # FACES (TRIANGLES)
        if faces:
            # FACE FLIPPING
            flipped_faces = _mesh_utils.flip_faceverts(faces)
            section.sections.append(_pix_container.make_triangle_stream(flipped_faces))

        index += 1
        piece_sections.append(section)
    return len_vertices, len_faces, piece_sections


def _fill_part_sections(locator_list, used_parts):
    """Fills up "Parts" sections.

    :param locator_list: list of Blender Objects - only 'Empty' typs, set as 'SCS Model Locators'
    :type locator_list: list
    :param used_parts: parts transitional structure for storing used parts inside this PIC export
    :type used_parts: io_scs_tools.exp.transition_structs.parts.PartsTrans
    :return: list of 'part_sections'
    :rtype: list
    """

    parts = []
    locator_parts = {}
    for locator_i, locator in enumerate(locator_list):
        scs_part = locator.scs_props.scs_part

        if scs_part not in locator_parts:
            locator_parts[scs_part] = [locator_i]
        else:
            locator_parts[scs_part].append(locator_i)

        if scs_part not in parts:
            parts.append(scs_part)

    # PART SECTIONS
    ordered_part_sections = []
    for part_name in used_parts.get_as_list():

        piece_count = 0
        pieces = None
        locator_count = 0
        locators = None

        # fill up part data from PIC data
        if part_name in parts:

            # PIECE COUNT
            piece_count = 0
            # PIECES
            pieces = None

            # LOCATOR COUNT
            if part_name in locator_parts:
                locator_count = len(locator_parts[part_name])
            # LOCATORS
            locators = None
            if part_name in locator_parts:
                if locator_parts[part_name]:
                    locators = locator_parts[part_name]

        # MAKE SECTION
        part_section = _SectionData("Part")
        part_section.props.append(("Name", part_name))
        part_section.props.append(("PieceCount", piece_count))
        part_section.props.append(("LocatorCount", locator_count))
        part_section.props.append(("Pieces", pieces))
        part_section.props.append(("Locators", locators))
        ordered_part_sections.append(part_section)

    return ordered_part_sections


def _make_common_part(item, index, col_type):
    scs_root = _get_scs_root(item)

    if not item.scs_props.locator_collider_centered:
        if item.scs_props.locator_collider_type == 'Box':
            offset_matrix = (item.matrix_world *
                             Matrix.Translation((0.0, -item.scs_props.locator_collider_box_y / 2, 0.0)) *
                             (Matrix.Scale(item.scs_props.locator_collider_box_x, 4, (1.0, 0.0, 0.0)) *
                              Matrix.Scale(item.scs_props.locator_collider_box_y, 4, (0.0, 1.0, 0.0)) *
                              Matrix.Scale(item.scs_props.locator_collider_box_z, 4, (0.0, 0.0, 1.0))))
        elif item.scs_props.locator_collider_type == 'Sphere':
            offset_matrix = (item.matrix_world *
                             Matrix.Translation((0.0, -item.scs_props.locator_collider_dia / 2, 0.0)) *
                             Matrix.Scale(item.scs_props.locator_collider_dia, 4))
        elif item.scs_props.locator_collider_type in ('Capsule', 'Cylinder'):
            offset_matrix = (item.matrix_world *
                             Matrix.Translation((0.0, -item.scs_props.locator_collider_len / 2, 0.0)) *
                             Matrix.Scale(item.scs_props.locator_collider_dia, 4))
        else:
            offset_matrix = item.matrix_world

        loc, qua, sca = _convert_utils.get_scs_transformation_components(scs_root.matrix_world.inverted() * offset_matrix)
    else:
        loc, qua, sca = _convert_utils.get_scs_transformation_components(scs_root.matrix_world.inverted() * item.matrix_world)

    section = _SectionData("Locator")
    section.props.append(("Name", _name_utils.tokenize_name(item.name)))
    section.props.append(("Index", index))
    section.props.append(("Position", ["&&", loc]))
    section.props.append(("Rotation", ["&&", qua]))
    section.props.append(("Alias", ""))
    section.props.append(("Weight", ["&", (item.scs_props.locator_collider_mass,)]))
    section.props.append(("Type", col_type))
    return section


def _fill_collision_locator_sections(collision_locator_list):
    """Fills up "Locator" sections."""
    collision_locator_sections = []
    piece_index = 0

    for item_i, item in enumerate(collision_locator_list):

        loc_type = item.scs_props.locator_collider_type
        section = _make_common_part(item, item_i, loc_type)

        if loc_type == "Box":
            # dimX dimY dimZ
            section.props.append(("Parameters", ["&&", (
                item.scs_props.locator_collider_box_x, item.scs_props.locator_collider_box_z, item.scs_props.locator_collider_box_y, 0.0)]))
        elif loc_type == "Sphere":
            # radius
            section.props.append(("Parameters", ["&&", (item.scs_props.locator_collider_dia / 2, 0.0, 0.0, 0.0)]))
        elif loc_type == "Capsule":
            # radius length
            section.props.append(("Parameters", ["&&", (item.scs_props.locator_collider_dia / 2, item.scs_props.locator_collider_len, 0.0, 0.0)]))
        elif loc_type == "Cylinder":
            # radius length
            section.props.append(("Parameters", ["&&", (item.scs_props.locator_collider_dia / 2, item.scs_props.locator_collider_len, 0.0, 0.0)]))
        elif loc_type == "Convex":
            section.props.append(("ConvexPiece", piece_index))
            piece_index += 1

        collision_locator_sections.append(section)

    return collision_locator_sections


def _sort_collision_locators(collision_locator_list):
    box_coll_locators = {}
    sphere_coll_locators = {}
    capsule_coll_locators = {}
    cylinder_coll_locators = {}
    convex_coll_locators = {}
    for item_i, item in enumerate(collision_locator_list):
        if item.scs_props.locator_collider_type == 'Box':
            box_coll_locators[item_i] = item
        if item.scs_props.locator_collider_type == 'Sphere':
            sphere_coll_locators[item_i] = item
        if item.scs_props.locator_collider_type == 'Capsule':
            capsule_coll_locators[item_i] = item
        if item.scs_props.locator_collider_type == 'Cylinder':
            cylinder_coll_locators[item_i] = item
        if item.scs_props.locator_collider_type == 'Convex':
            convex_coll_locators[item_i] = item
    return box_coll_locators, sphere_coll_locators, capsule_coll_locators, cylinder_coll_locators, convex_coll_locators


def export(collision_locator_list, filepath, filename, used_parts):
    """Exports PIC colliders

    :param collision_locator_list:
    :type collision_locator_list:
    :param filepath:
    :type filepath:
    :param filename:
    :type filename:
    :param used_parts: parts transitional structure for storing used parts inside this PIC export
    :type used_parts: io_scs_tools.exp.transition_structs.parts.PartsTrans
    """
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIC Exporter          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    # DATA CREATION
    header_section = _fill_header_section(filename, scs_globals.export_write_signature)
    piece_sections = []
    materials = 0
    len_vertices = 0
    len_faces = 0
    convex_coll_locators = [loc for loc in collision_locator_list if loc.scs_props.locator_collider_type == "Convex"]
    if convex_coll_locators:
        len_vertices, len_faces, piece_sections = _fill_piece_sections(convex_coll_locators, scs_globals.export_scale)
        materials += 1
    part_sections = _fill_part_sections(collision_locator_list, used_parts)
    collision_locator_sections = _fill_collision_locator_sections(collision_locator_list)
    global_section = _fill_global_section(len_vertices, len_faces, materials,
                                          len(piece_sections), len(part_sections), len(collision_locator_sections))

    # DATA ASSEMBLING
    pic_container = [header_section, global_section]
    if convex_coll_locators:
        material_section = _fill_coll_material_section()
        pic_container.append(material_section)
    if piece_sections:
        for section in piece_sections:
            pic_container.append(section)
    for section in part_sections:
        pic_container.append(section)
    for section in collision_locator_sections:
        pic_container.append(section)
    # print('  pic_container:\n%s' % str(pic_container))

    # FILE EXPORT
    ind = "    "
    pic_filepath = str(filepath + ".pic")
    result = _pix_container.write_data_to_file(pic_container, pic_filepath, ind)

    # print("************************************")
    return result
