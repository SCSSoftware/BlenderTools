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

import os
import collections
from mathutils import Matrix, Vector
from io_scs_tools.exp.pim.header import Header
from io_scs_tools.exp.pim.globall import Globall
from io_scs_tools.exp.pim.material import Material
from io_scs_tools.exp.pim.piece import Piece
from io_scs_tools.exp.pim.part import Part
from io_scs_tools.exp.pim.locator import Locator
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.convert import change_to_scs_uv_coordinates as _change_to_scs_uv_coordinates
from io_scs_tools.utils.convert import get_scs_transformation_components as _get_scs_transformation_components
from io_scs_tools.utils.convert import scs_to_blend_matrix as _scs_to_blend_matrix
from io_scs_tools.utils.printout import lprint


def execute(dirpath, root_object, mesh_objects, model_locators, used_parts, used_materials):
    """Executes export of PIM file for given data.
    :param dirpath: directory path for PIM file
    :type dirpath: str
    :param root_object: Blender SCS Root empty object
    :type root_object: bpy.types.Object
    :param mesh_objects: all the meshes which should be exported for current game object
    :type mesh_objects: list of bpy.types.Object
    :param model_locators: all Blender empty objecs which represents model locators and should be exported for current game object
    :type model_locators: list of bpy.types.Object
    :return: True if export was successfull; False otherwise
    :rtype: bool
    """

    print("\n************************************")
    print("**      SCS PIM Exporter          **")
    print("**      (c)2015 SCS Software      **")
    print("************************************\n")

    scs_globals = _get_scs_globals()

    if scs_globals.output_type == "5":
        format_version = 5
        format_type = ""
    else:
        format_version = 1
        format_type = "def"

    pim_header = Header(format_type, format_version, root_object.name)
    pim_global = Globall(root_object.name + ".pis")

    pim_materials = collections.OrderedDict()  # dict of Material class instances representing used materials
    """:type: dict of Material"""
    pim_pieces = []  # list of Piece class instances representing mesh pieces
    """:type: list of Piece"""
    pim_parts = collections.OrderedDict()  # list of Part class instances representing used parts
    """:type: dict of Part"""
    pim_locators = []  # list of Locator class instances representing model locators
    """:type: list of Locator"""

    objects_with_default_material = {}  # stores object names which has no material set
    missing_mappings_data = {}  # indicates if material doesn't have set any uv layer for export

    # create mesh object data sections
    for mesh_obj in mesh_objects:

        mesh_pieces = collections.OrderedDict()

        # get initial mesh
        mesh = _object_utils.get_mesh(mesh_obj)
        _mesh_utils.bm_triangulate(mesh)
        mesh.calc_normals_split()

        # calculate transformation matrices for this object
        pos_transf_mat = (Matrix.Scale(scs_globals.export_scale, 4) *
                          _scs_to_blend_matrix().inverted() *
                          root_object.matrix_world.inverted() *
                          mesh_obj.matrix_world)

        nor_transf_mat = (_scs_to_blend_matrix().inverted() *
                          root_object.matrix_world.inverted().to_quaternion().to_matrix().to_4x4() *
                          mesh_obj.matrix_world.to_quaternion().to_matrix().to_4x4())

        missing_uv_layers = {}  # stores missing uvs specified by materials of this object
        missing_vcolor = False  # indicates if object is missing vertex colors

        for poly in mesh.polygons:

            mat_index = poly.material_index

            # check material existance and decide what material name and effect has to be used
            if mat_index >= len(mesh_obj.material_slots) or mesh_obj.material_slots[mat_index].material is None:  # no material or invalid index
                material = None
                pim_mat_name = "_not_existing_material_"
                pim_mat_effect = "eut2.dif"
                objects_with_default_material[mesh_obj.name] = 1
            else:
                material = mesh_obj.material_slots[mat_index].material
                pim_mat_name = material.name
                pim_mat_effect = material.scs_props.mat_effect_name

            # create new pim material if material with that name doesn't yet exists
            if pim_mat_name not in pim_materials:
                pim_material = Material(len(pim_materials), pim_mat_name, pim_mat_effect, material)
                pim_materials[pim_mat_name] = pim_material
                used_materials.append(pim_mat_name)

            # create new piece if piece with this material doesn't exists yet -> split to pieces by material
            if pim_mat_name not in mesh_pieces:
                mesh_pieces[pim_mat_name] = Piece(len(pim_pieces) + len(mesh_pieces), pim_materials[pim_mat_name])

                nmap_uv_layer = pim_materials[pim_mat_name].get_nmap_uv_name()
                if nmap_uv_layer:  # if there is uv layer used for normal maps then calculate tangents on it
                    mesh.calc_tangents(uvmap=nmap_uv_layer)

            mesh_piece = mesh_pieces[pim_mat_name]
            """:type: Piece"""

            piece_vert_indices = []
            for loop_i in poly.loop_indices:

                loop = mesh.loops[loop_i]
                """:type: bpy.types.MeshLoop"""
                vert_i = loop.vertex_index

                # get data of current vertex
                # 1. position -> mesh.vertices[loop.vertex_index].co
                position = tuple(pos_transf_mat * mesh.vertices[vert_i].co)

                # 2. normal -> loop.normal -> calc_normals_split() has to be called before
                normal = nor_transf_mat * loop.normal
                normal = tuple(Vector(normal).normalized())

                # 3. uvs -> uv_lay = mesh.uv_layers[0].data; uv_lay[loop_i].uv
                uvs = []
                uvs_aliases = []
                tex_coord_alias_map = pim_materials[pim_mat_name].get_tex_coord_map()
                if len(tex_coord_alias_map) < 1:  # no textures for current material effect
                    uvs.append((0.0, 0.0))
                    uvs_aliases.append(["_TEXCOORD0"])

                    # report missing mappings only on actual materials with texture entries
                    if material and pim_materials[pim_mat_name].uses_textures():
                        if material.name not in missing_mappings_data:
                            missing_mappings_data[material.name] = {}

                        if mesh_obj.name not in missing_mappings_data[material.name]:
                            missing_mappings_data[material.name][mesh_obj.name] = 1

                else:
                    for uv_lay_name in tex_coord_alias_map:

                        if uv_lay_name not in mesh.uv_layers:
                            uvs.append((0.0, 0.0))

                            # properly report missing uv layers where name of uv layout is key and materials that misses it are values
                            if uv_lay_name not in missing_uv_layers:
                                missing_uv_layers[uv_lay_name] = []

                            if pim_mat_name not in missing_uv_layers[uv_lay_name]:  # add material if not already there
                                missing_uv_layers[uv_lay_name].append(pim_mat_name)
                        else:
                            uv_lay = mesh.uv_layers[uv_lay_name]
                            uvs.append(_change_to_scs_uv_coordinates(uv_lay.data[loop_i].uv))

                        aliases = []
                        for alias_index in tex_coord_alias_map[uv_lay_name]:
                            aliases.append("_TEXCOORD" + str(alias_index))

                        uvs_aliases.append(aliases)

                # 4. vcol -> vcol_lay = mesh.vertex_colors[0].data; vcol_lay[loop_i].color
                if len(mesh.vertex_colors) < 1:
                    vcol = (1.0, 1.0, 1.0, 1.0)
                    missing_vcolor = True
                else:
                    multiplier = mesh_obj.data.scs_props.vertex_color_multiplier
                    color = mesh.vertex_colors[0].data[loop_i].color
                    vcol = (color[0] * multiplier, color[1] * multiplier, color[2] * multiplier, 1.0)

                # 5. tangent -> loop.tangent; loop.bitangent_sign -> calc_tangents() has to be called before
                if pim_materials[pim_mat_name].get_nmap_uv_name():  # calculate tangents only if needed
                    tangent = tuple(nor_transf_mat * loop.tangent)
                    tangent = tuple(Vector(tangent).normalized())
                    tangent = (tangent[0], tangent[1], tangent[2], loop.bitangent_sign)
                else:
                    tangent = None

                # save internal vertex index to array to be able to construct triangle afterwards
                piece_vert_index = mesh_piece.add_vertex(vert_i, position, normal, uvs, uvs_aliases, vcol, tangent)
                piece_vert_indices.append(piece_vert_index)

            mesh_piece.add_triangle(tuple(piece_vert_indices[::-1]))  # invert indices because of normals flip

        # create part if it doesn't exists yet
        part_name = mesh_obj.scs_props.scs_part
        if part_name not in pim_parts:
            pim_parts[part_name] = Part(part_name)
            used_parts[part_name] = 1

        mesh_pieces = mesh_pieces.values()
        for piece in mesh_pieces:
            # put pieces of current mesh to global list
            pim_pieces.append(piece)

            # add pieces of current mesh to part
            pim_part = pim_parts[part_name]
            pim_part.add_piece(piece)

        # report missing data for each object
        if len(missing_uv_layers) > 0:
            for uv_lay_name in missing_uv_layers:
                lprint("W Object '%s' is missing UV layer '%s' specified by materials: %s\n",
                       (mesh_obj.name, uv_lay_name, missing_uv_layers[uv_lay_name]))
        if missing_vcolor:
            lprint("W Object '%s' is missing vertex color layer! Default color will be exported (1, 1, 1, 1)!", (mesh_obj.name,))

    # report mising data for whole model
    if len(missing_mappings_data) > 0:
        for material_name in missing_mappings_data:
            lprint("W Material '%s' is missing mapping data! Objects using it are exported with default UV:\n\t   %s",
                   (material_name, list(missing_mappings_data[material_name].keys())))
    if len(objects_with_default_material) > 0:
        lprint("W Some objects don't use any material. Default material and UV mapping is used on them:\n\t   %s",
               (list(objects_with_default_material.keys()),))

    # create locators data sections
    for loc_obj in model_locators:
        name = _name_utils.tokenize_name(loc_obj.name)
        hookup_string = loc_obj.scs_props.locator_model_hookup
        if hookup_string != "" and ":" in hookup_string:
            hookup = hookup_string.split(':', 1)[1].strip()
        else:
            if hookup_string != "":
                lprint("W The Hookup %r has no expected value!", hookup_string)
            hookup = None
        pos, qua, sca = _get_scs_transformation_components(loc_obj.matrix_world)

        # create locator object for export
        locator = Locator(len(pim_locators), name, hookup)
        locator.set_position(pos)
        locator.set_rotation(qua)
        locator.set_scale(sca)

        # create part if it doesn't exists yet
        part_name = loc_obj.scs_props.scs_part
        if part_name not in pim_parts:
            pim_parts[part_name] = Part(part_name)
            used_parts[part_name] = 1

        # add locator to part
        pim_part = pim_parts[part_name]
        pim_part.add_locator(locator)

        # add locator to locator list
        pim_locators.append(locator)

    # create container
    pim_container = [pim_header.get_as_section(), pim_global.get_as_section()]

    for mat_name in pim_materials:
        pim_container.append(pim_materials[mat_name].get_as_section())

    for pim_piece in pim_pieces:
        pim_container.append(pim_piece.get_as_section())

    for part_name in used_parts:
        pim_container.append(pim_parts[part_name].get_as_section())

    for locator in pim_locators:
        pim_container.append(locator.get_as_section())

    # write to file
    ind = "    "
    pim_filepath = dirpath + os.sep + root_object.name + ".pim"
    return _pix_container.write_data_to_file(pim_container, pim_filepath, ind)