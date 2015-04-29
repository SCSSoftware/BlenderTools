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

from io_scs_tools.utils.printout import lprint
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import convert as _convert_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def _get_header(pic_container):
    """Receives PIC container and returns all its Header properties in its own variables.
    For any item that fails to be found, it returns None."""
    format_version = source = f_type = f_name = source_filename = author = None
    for section in pic_container:
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


def _get_global(pic_container):
    """Receives PIC container and returns all its Global properties in its own variables.
    For any item that fails to be found, it returns None."""
    vertex_count = triangle_count = material_count = piece_count = part_count = locator_count = None
    for section in pic_container:
        if section.type == "Global":
            for prop in section.props:
                if prop[0] in ("", "#"):
                    pass
                elif prop[0] == "VertexCount":
                    vertex_count = prop[1]
                elif prop[0] == "TriangleCount":
                    triangle_count = prop[1]
                elif prop[0] == "MaterialCount":
                    material_count = prop[1]
                elif prop[0] == "PieceCount":
                    piece_count = prop[1]
                elif prop[0] == "PartCount":
                    part_count = prop[1]
                elif prop[0] == "LocatorCount":
                    locator_count = prop[1]
                else:
                    lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    return vertex_count, triangle_count, material_count, piece_count, part_count, locator_count


def _get_material(section):
    """Receives a Collider Material section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    material_alias = material_effect = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Alias":
            material_alias = prop[1]
        elif prop[0] == "Effect":
            material_effect = prop[1]
        else:
            lprint('\nW Unknown property in "Material" data: "%s"!', prop[0])
    return material_alias, material_effect


def _get_piece(section):
    """Receives a Convex Collider Piece section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    piece_index = piece_material = piece_vertex_count = piece_triangle_count = piece_stream_count = None
    verts = []
    faces = []
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Index":
            piece_index = prop[1]
        elif prop[0] == "Material":
            piece_material = prop[1]
        elif prop[0] == "VertexCount":
            piece_vertex_count = prop[1]
        elif prop[0] == "TriangleCount":
            piece_triangle_count = prop[1]
        elif prop[0] == "StreamCount":
            piece_stream_count = prop[1]
        else:
            lprint('\nW Unknown property in "Piece" data: "%s"!', prop[0])
    stream_cnt = 0
    for sec in section.sections:
        if sec.type == "Stream":
            stream_cnt += 1
            for sec_prop in sec.props:
                if sec_prop[0] == "":
                    pass
                elif sec_prop[0] == "Format":
                    '''
                    NOTE: skipped for now as no data needs to be readed
                    stream_format = sec_prop[1]
                    '''
                    pass
                elif sec_prop[0] == "Tag":
                    '''
                    NOTE: skipped for now as no data needs to be readed
                    stream_tag = sec_prop[1]
                    '''
                    pass
                else:
                    lprint('\nW Unknown property in "%s" data: "%s"!', (sec.name, sec_prop[0]))
            for sec_data in sec.data:
                verts.append(tuple(sec_data))
        elif sec.type == "Triangles":
            for sec_data in sec.data:
                faces.append(tuple(sec_data))

    # WARNINGS
    if piece_vertex_count != len(verts):
        lprint('\nW Formentioned number of vertices was %i, but real number is %i!', (piece_vertex_count, len(verts)))
    if piece_triangle_count != len(faces):
        lprint('\nW Formentioned number of faces was %i, but real number is %i!', (piece_triangle_count, len(faces)))
    if piece_stream_count != stream_cnt:
        lprint('\nW Formentioned number of Piece Streams was %i, but real number is %i!', (piece_stream_count, stream_cnt))

    return piece_index, piece_material, verts, faces


def _get_locator(section):
    """Receives a Collision Locator section and returns its properties in its own variables.
    For any item that fails to be found, it returns None."""
    locator_name = locator_index = locator_position = locator_rotation = locator_alias = \
        locator_weight = locator_type = locator_parameters = locator_convex_piece = None
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            locator_name = prop[1]
        elif prop[0] == "Index":
            locator_index = prop[1]
        elif prop[0] == "Position":
            locator_position = prop[1]
        elif prop[0] == "Rotation":
            locator_rotation = prop[1]
        elif prop[0] == "Alias":
            locator_alias = prop[1]
        elif prop[0] == "Weight":
            locator_weight = prop[1]
        elif prop[0] == "Type":
            locator_type = prop[1]
        elif prop[0] == "Parameters":
            locator_parameters = prop[1]
        elif prop[0] == "ConvexPiece":
            locator_convex_piece = prop[1]
        else:
            lprint('\nW Unknown property in "Locator" data: "%s"!', prop[0])
    return (locator_name,
            locator_index,
            locator_position,
            locator_rotation,
            locator_alias,
            locator_weight,
            locator_type,
            locator_parameters,
            locator_convex_piece)


def _get_part(section):
    name = None
    pieces = []
    locators = []
    for prop in section.props:
        if prop[0] in ("", "#"):
            pass
        elif prop[0] == "Name":
            name = prop[1]
        elif prop[0] == "PieceCount":
            pass
        elif prop[0] == "LocatorCount":
            pass
        elif prop[0] == "Pieces":
            pieces = prop[1]
        elif prop[0] == "Locators":
            locators = prop[1]
        else:
            lprint('\nW Unknown property in "Global" data: "%s"!', prop[0])
    if not isinstance(pieces, list):
        if isinstance(pieces, int):
            pieces = [pieces]
    if not isinstance(locators, list):
        if isinstance(locators, int):
            locators = [locators]

    return name, pieces, locators


def _get_locator_part(parts, index):
    for part in parts:
        if part["locators"]:
            for loc_i in part["locators"]:
                if loc_i == index:
                    return part["name"].lower()

    return "defaultpart"


def load(filepath):
    scs_globals = _get_scs_globals()

    print("\n************************************")
    print("**      SCS PIC Importer          **")
    print("**      (c)2014 SCS Software      **")
    print("************************************\n")

    ind = '    '
    pic_container = _pix_container.get_data_from_file(filepath, ind)

    # TEST PRINTOUTS
    # ind = '  '
    # for section in pic_container:
    # print('SEC.: "%s"' % section.type)
    # for prop in section.props:
    # print('%sProp: %s' % (ind, prop))
    # for data in section.data:
    # print('%sdata: %s' % (ind, data))
    # for sec in section.sections:
    # print_section(sec, ind)
    # print('\nTEST - Source: "%s"' % pic_container[0].props[1][1])
    # print('')

    # TEST EXPORT
    # path, file = os.path.splitext(filepath)
    # export_filepath = str(path + '_reex' + file)
    # result = pix_write.write_data(pic_container, export_filepath, ind)
    # if result == {'FINISHED'}:
    # Print(dump_level, '\nI Test export succesful! The new file:\n  "%s"', export_filepath)
    # else:
    # Print(dump_level, '\nE Test export failed! File:\n  "%s"', export_filepath)

    # LOAD HEADER
    '''
    NOTE: skipped for now as no data needs to be readed
    format_version, source, f_type, f_name, source_filename, author = _get_header(pic_container)
    '''

    # LOAD GLOBALS
    '''
    NOTE: skipped for now as no data needs to be readed
    vertex_count, triangle_count, material_count, piece_count, part_count, locator_count = _get_global(pic_container)
    '''

    # LOAD MATERIALS
    if 0:  # NOTE: NO MATERIALS USED FOR COLLIDERS AT A MOMENT!
        loaded_materials = []
        for section in pic_container:
            if section.type == 'Material':
                material_alias, material_effect = _get_material(section)
                lprint('I Adding a Material Alias: "%s"', material_alias)
                loaded_materials.append(material_alias)

                # PRINT "MATERIAL SETTINGS" TO CONSOLE...
                if 0:
                    import pprint

                    pp = pprint.PrettyPrinter(indent=1)
                    print("===  MATERIAL SETTINGS  ==========================")
                    pp.pprint(material_effect)
                    print("==================================================")

    # LOAD PARTS
    parts = []
    for section in pic_container:
        if section.type == "Part":
            (name, pieces, locators) = _get_part(section)
            parts.append({"name": name, "pieces": pieces, "locators": locators})

    # LOAD (CONVEX) PIECES
    pieces = []
    for section in pic_container:
        if section.type == 'Piece':
            pieces.append(_get_piece(section))

    # LOAD AND CREATE LOCATORS
    import_scale = scs_globals.import_scale
    locators = []
    for section in pic_container:
        if section.type == 'Locator':
            (locator_name,
             locator_index,
             locator_position,
             locator_rotation,
             locator_alias,
             locator_weight,
             locator_type,
             locator_parameters,
             locator_convex_piece) = _get_locator(section)
            lprint('I Adding a Locator: "%s"', locator_name)
            locator = _object_utils.create_locator_empty(locator_name, locator_position, locator_rotation, (1, 1, 1), 1.0, 'Collision')
            locator.scs_props.scs_part = _get_locator_part(parts, locator_index)
            locator.scs_props.locator_collider_centered = True
            locator.scs_props.locator_collider_mass = locator_weight
            locator.scs_props.locator_collider_type = locator_type
            if locator_type == 'Box':
                locator.scs_props.locator_collider_box_x = locator_parameters[0] * import_scale
                locator.scs_props.locator_collider_box_y = locator_parameters[2] * import_scale
                locator.scs_props.locator_collider_box_z = locator_parameters[1] * import_scale
            elif locator_type in ('Sphere', 'Capsule', 'Cylinder'):
                locator.scs_props.locator_collider_dia = locator_parameters[0] * 2 * import_scale
                locator.scs_props.locator_collider_len = locator_parameters[1] * import_scale
            elif locator_type == 'Convex':
                piece_index, piece_material, verts, faces = pieces[locator_convex_piece]
                if verts and faces:

                    # BOUNDING BOX DATA CREATION AND SPACE CONVERSION
                    min_val = [None, None, None]
                    max_val = [None, None, None]
                    scs_verts = []
                    for vert in verts:
                        scs_vert = _convert_utils.change_to_scs_xyz_coordinates(vert, import_scale)
                        scs_verts.append(scs_vert)
                        min_val, max_val = _math_utils.evaluate_minmax(scs_vert, min_val, max_val)
                    bbox, bbcenter = _math_utils.get_bb(min_val, max_val)

                    # FACE FLIPPING
                    flipped_faces = _mesh_utils.flip_faceverts(faces)

                    # COLLIDER CREATION
                    geom_data = (scs_verts, flipped_faces, bbox, bbcenter)
                    _object_utils.add_collider_convex_locator(geom_data, {}, locator)

            locators.append(locator)

            # DATA BUILDING

            # WARNING PRINTOUTS
    # if piece_count < 0: Print(dump_level, '\nW More Pieces found than were declared!')
    # if piece_count > 0: Print(dump_level, '\nW Some Pieces not found, but were declared!')
    # if dump_level > 1: print('')

    print("************************************")
    return {'FINISHED'}, locators