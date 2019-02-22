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
from re import match
from mathutils import Matrix, Vector
from io_scs_tools.consts import Mesh as _MESH_consts
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.exp.pim.header import Header
from io_scs_tools.exp.pim.globall import Globall
from io_scs_tools.exp.pim.material import Material
from io_scs_tools.exp.pim.piece import Piece
from io_scs_tools.exp.pim.part import Part
from io_scs_tools.exp.pim.locator import Locator
from io_scs_tools.exp.pim.bones import Bones
from io_scs_tools.exp.pim.skin import Skin
from io_scs_tools.exp.pim.skin import SkinStream
from io_scs_tools.internals.containers import pix as _pix_container
from io_scs_tools.utils import mesh as _mesh_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.convert import change_to_scs_uv_coordinates as _change_to_scs_uv_coordinates
from io_scs_tools.utils.convert import get_scs_transformation_components as _get_scs_transformation_components
from io_scs_tools.utils.convert import scs_to_blend_matrix as _scs_to_blend_matrix
from io_scs_tools.utils.convert import hookup_name_to_hookup_id as _hookup_name_to_hookup_id
from io_scs_tools.utils.printout import lprint


def execute(dirpath, name_suffix, root_object, armature_object, skeleton_filepath, mesh_objects, model_locators,
            used_parts, used_materials, used_bones, used_terrain_points):
    """Executes export of PIM file for given data.
    :param dirpath: directory path for PIM file
    :type dirpath: str
    :param name_suffix: file name suffix
    :type name_suffix: str
    :param root_object: Blender SCS Root empty object
    :type root_object: bpy.types.Object
    :param armature_object: Blender Aramture object belonging to this SCS game object
    :type armature_object: bpy.types.Object
    :param skeleton_filepath: relative file path of PIS file
    :type skeleton_filepath: str
    :param mesh_objects: all the meshes which should be exported for current game object
    :type mesh_objects: list of bpy.types.Object
    :param model_locators: all Blender empty objecs which represents model locators and should be exported for current game object
    :type model_locators: list of bpy.types.Object
    :param used_parts: parts transitional structure for storing used parts inside this PIM export
    :type used_parts: io_scs_tools.exp.transition_structs.parts.PartsTrans
    :param used_materials: materials transitional structure for storing used materials inside this PIM export
    :type used_materials: io_scs_tools.exp.transition_structs.materials.MaterialsTrans
    :param used_bones: bones transitional structure for storing used bones inside this PIM export
    :type used_bones: io_scs_tools.exp.transition_structs.bones.BonesTrans
    :param used_terrain_points: terrain points transitional structure for storing used terrain points
    :type used_terrain_points: io_scs_tools.exp.transition_structs.terrain_points.TerrainPntsTrans
    :return: True if export was successfull; False otherwise
    :rtype: bool
    """

    print("\n************************************")
    print("**      SCS PIM Exporter          **")
    print("**      (c)2017 SCS Software      **")
    print("************************************\n")

    scs_globals = _get_scs_globals()

    format_version = 5

    is_skin_used = (armature_object and root_object.scs_props.scs_root_animated == "anim")

    pim_header = Header("", format_version, root_object.name)
    pim_global = Globall(used_parts.count(), skeleton_filepath)

    pim_materials = collections.OrderedDict()  # dict of Material class instances representing used materials
    """:type: dict[str, Material]"""
    pim_pieces = []  # list of Piece class instances representing mesh pieces
    """:type: list[Piece]"""
    pim_parts = {}  # list of Part class instances representing used parts
    """:type: dict[str, Part]"""
    pim_locators = []  # list of Locator class instances representing model locators
    """:type: list[Locator]"""

    objects_with_default_material = {}  # stores object names which has no material set
    missing_mappings_data = {}  # indicates if material doesn't have set any uv layer for export
    invalid_objects_for_tangents = set()  # stores object names which tangents calculation failed because of N-gons existence

    bones = skin = skin_stream = None
    if is_skin_used:

        invalid_bone_names = set()  # set for saving bones with invalid names, they are used for reporting to user

        # create bones data section
        bones = Bones()
        for bone in armature_object.data.bones:
            bones.add_bone(bone.name)
            used_bones.add(bone.name)

            # do bones name checks
            if _name_utils.tokenize_name(bone.name) != bone.name:
                invalid_bone_names.add(bone.name)

        # create skin data section
        skin_stream = SkinStream(SkinStream.Types.POSITION)
        skin = Skin(skin_stream)

        # report invalid bone names
        if len(invalid_bone_names) > 0:
            lprint("W Invalid bone names detected, max. length of valid bone name is 12 and must consists from [a-z, 0-9 and _ ] characters.\n\t   "
                   "Conversion will generalize names, however expect problems by re-import! List of invalid bone names for %r:\n\t   "
                   "%r",
                   (armature_object.name, list(invalid_bone_names)))

    mesh_pieces = collections.OrderedDict()
    """:type: dict[str, Piece]"""

    # create mesh object data sections
    for mesh_i, mesh_obj in enumerate(mesh_objects):

        lprint("I Preparing mesh object: %r ...", (mesh_obj.name,))

        # create part if it doesn't exists yet
        part_name = used_parts.ensure_part(mesh_obj)
        if part_name not in pim_parts:
            pim_parts[part_name] = Part(part_name)

        vert_groups = mesh_obj.vertex_groups

        # calculate faces flip state from all ancestors of current object
        scale_sign = 1
        parent = mesh_obj
        while parent and parent.scs_props.empty_object_type != "SCS_Root":

            for scale_axis in parent.scale:
                scale_sign *= scale_axis

            for scale_axis in parent.delta_scale:
                scale_sign *= scale_axis

            parent = parent.parent

        face_flip = scale_sign < 0

        # calculate transformation matrix for current object (root object transforms are always subtracted!)
        mesh_transf_mat = root_object.matrix_world.inverted() * mesh_obj.matrix_world
        """:type: mathutils.Matrix"""

        # calculate vertex position transformation matrix for this object
        pos_transf_mat = (Matrix.Scale(scs_globals.export_scale, 4) *
                          _scs_to_blend_matrix().inverted())
        """:type: mathutils.Matrix"""

        # calculate vertex normals transformation matrix for this object
        # NOTE: as normals will be read from none export prepared mesh we have to add rotation and scale from mesh transformation matrix
        _, rot, scale = mesh_transf_mat.decompose()
        scale_matrix_x = Matrix.Scale(scale.x, 3, Vector((1, 0, 0))).to_4x4()
        scale_matrix_y = Matrix.Scale(scale.y, 3, Vector((0, 1, 0))).to_4x4()
        scale_matrix_z = Matrix.Scale(scale.z, 3, Vector((0, 0, 1))).to_4x4()
        nor_transf_mat = (_scs_to_blend_matrix().inverted() *
                          rot.to_matrix().to_4x4() *
                          scale_matrix_x * scale_matrix_y * scale_matrix_z)
        """:type: mathutils.Matrix"""

        tangent_transf_mat = _scs_to_blend_matrix().inverted()
        """:type: mathutils.Matrix"""

        # get initial mesh & extra copy of the mesh for normals
        mesh = _object_utils.get_mesh(mesh_obj)
        mesh_for_normals = mesh.copy()

        # prepare meshes
        faces_mapping = _mesh_utils.bm_prepare_mesh_for_export(mesh, mesh_transf_mat, triangulate=True)
        mesh_for_normals.calc_normals_split()

        missing_uv_layers = {}  # stores missing uvs specified by materials of this object
        missing_vcolor = False  # indicates if object is missing vertex color layer
        missing_vcolor_a = False  # indicates if object is missing vertex color alpha layer
        missing_skinned_verts = set()  # indicates if object is having only partial skin, which is not allowed in our models
        has_unnormalized_skin = False  # indicates if object has vertices which bones weight sum is smaller then one
        last_tangents_uv_layer = None  # stores uv layer for which tangents were calculated, so tangents won't be calculated all over again

        for poly in mesh.polygons:

            mat_index = poly.material_index

            # check material existence and decide what material name and effect has to be used
            if mat_index >= len(mesh_obj.material_slots) or mesh_obj.material_slots[mat_index].material is None:  # no material or invalid index
                material = None
                pim_mat_name = "_default_material_-_default_settings_"
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
                used_materials.add(pim_mat_name, material)

            # if there is uv layer used for normal maps and that uv layer exists on mesh then calculate tangents on it otherwise report warning
            nmap_uv_layer = pim_materials[pim_mat_name].get_nmap_uv_name()
            if nmap_uv_layer and nmap_uv_layer != last_tangents_uv_layer:

                # save last uv layer that tangents were calculated on, so it won't be recalculated for each polygon
                last_tangents_uv_layer = nmap_uv_layer

                if nmap_uv_layer in mesh.uv_layers:
                    try:
                        mesh.calc_tangents(uvmap=nmap_uv_layer)
                    except RuntimeError:
                        invalid_objects_for_tangents.add(mesh_obj.name)
                else:
                    lprint("W Unable to calculate normal map tangents for object %r,\n\t   "
                           "as it's missing UV layer with name: %r, expect problems!",
                           (mesh_obj.name, nmap_uv_layer))

            # construct piece dictonary key (can divide even one mesh to more if they have multiple materials)
            if is_skin_used:  # if animated we try to merge as many pieces as possible
                piece_key = pim_mat_name + "|" + part_name
            else:  # if rigid just expot each mesh as own piece (conversion tools should take care about merging)
                piece_key = pim_mat_name + "|" + part_name + "|" + str(mesh_i)

            # create mesh piece object if max number of vertices is reached or no p piece for current piece dictonary key exists
            if piece_key in mesh_pieces and mesh_pieces[piece_key].get_vertex_count() > 65536 - 3:

                piece = mesh_pieces[piece_key]

                # put current piece of current mesh to global list
                pim_pieces.append(piece)

                # add pieces of current mesh to part
                pim_part = pim_parts[part_name]
                pim_part.add_piece(piece)

                del mesh_pieces[piece_key]
                mesh_pieces[piece_key] = Piece(len(pim_pieces) + len(mesh_pieces), pim_materials[pim_mat_name])

            elif piece_key not in mesh_pieces:

                mesh_pieces[piece_key] = Piece(len(pim_pieces) + len(mesh_pieces), pim_materials[pim_mat_name])

            mesh_piece = mesh_pieces[piece_key]
            """:type: Piece"""

            # get polygon loop indices for normals depending on mapped triangulated face
            if poly.index in faces_mapping:
                normals_poly_loop_indices = list(mesh_for_normals.polygons[faces_mapping[poly.index]].loop_indices)
            else:
                normals_poly_loop_indices = list(mesh_for_normals.polygons[poly.index].loop_indices)

            # vertex data
            triangle_pvert_indices = []  # storing vertex indices for this polygon triangle
            for loop_i in poly.loop_indices:

                loop = mesh.loops[loop_i]
                """:type: bpy.types.MeshLoop"""
                vert_i = loop.vertex_index

                # get data of current vertex
                # 1. position -> mesh.vertices[loop.vertex_index].co
                position = tuple(pos_transf_mat * mesh.vertices[vert_i].co)

                # 2. normal -> mesh_for_normals.loops[loop_i].normal -> calc_normals_split() has to be called before
                normal = (0, 0, 0)
                for i, normals_poly_loop_i in enumerate(normals_poly_loop_indices):
                    normal_loop = mesh_for_normals.loops[normals_poly_loop_i]

                    # match by vertex index as triangle will for sure have three unique vertices
                    if vert_i == normal_loop.vertex_index:
                        normal = nor_transf_mat * normal_loop.normal
                        normal = tuple(Vector(normal).normalized())
                        del normals_poly_loop_indices[i]
                        break
                else:
                    lprint("E Normals data gathering went wrong, expect corrupted mesh! Shouldn't happen...")

                # 3. uvs -> uv_lay = mesh.uv_layers[0].data; uv_lay[loop_i].uv
                uvs = []
                uvs_aliases = []
                tex_coord_alias_map = pim_materials[pim_mat_name].get_tex_coord_map()
                if len(tex_coord_alias_map) < 1:  # no textures or none uses uv mapping in current material effect
                    uvs.append((0.0, 0.0))
                    uvs_aliases.append(["_TEXCOORD0"])

                    # report missing mappings only on actual materials with textures using uv mappings
                    if material and pim_materials[pim_mat_name].uses_textures_with_uv():
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
                vcol_multi = mesh_obj.data.scs_props.vertex_color_multiplier
                if _MESH_consts.default_vcol not in mesh.vertex_colors:  # get RGB component of RGBA
                    vcol = (1.0,) * 3
                    missing_vcolor = True
                else:
                    color = mesh.vertex_colors[_MESH_consts.default_vcol].data[loop_i].color
                    vcol = (color[0] * 2 * vcol_multi, color[1] * 2 * vcol_multi, color[2] * 2 * vcol_multi)

                if _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix not in mesh.vertex_colors:  # get A component of RGBA
                    vcol += (1.0,)
                    missing_vcolor_a = True
                else:
                    alpha = mesh.vertex_colors[_MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix].data[loop_i].color
                    vcol += ((alpha[0] + alpha[1] + alpha[2]) / 3.0 * 2 * vcol_multi,)  # take avg of colors for alpha

                # 5. tangent -> loop.tangent; loop.bitangent_sign -> calc_tangents() has to be called before
                if pim_materials[pim_mat_name].get_nmap_uv_name():  # calculate tangents only if needed
                    tangent = tuple(tangent_transf_mat * loop.tangent)
                    tangent = tuple(Vector(tangent).normalized())
                    tangent = (tangent[0], tangent[1], tangent[2], loop.bitangent_sign)
                else:
                    tangent = None

                # 6. There we go, vertex data collected! Now create internal vertex index, for triangle and skin stream construction
                # Construct unique vertex index - donated by mesh and vertex index, as we may export more mesh objects into same piece,
                # thus only vertex index wouldn't be unique representation.
                unique_vert_i = str(mesh_i) + "|" + str(vert_i)
                piece_vert_index = mesh_piece.add_vertex(unique_vert_i, position, normal, uvs, uvs_aliases, vcol, tangent)

                # 7. Add vertex to triangle creation list
                triangle_pvert_indices.append(piece_vert_index)

                # 8. Get skinning data for vertex and save it to skin stream
                if is_skin_used:
                    bone_weights = {}
                    bone_weights_sum = 0
                    for v_group_entry in mesh.vertices[vert_i].groups:
                        bone_indx = bones.get_bone_index(vert_groups[v_group_entry.group].name)
                        bone_weight = v_group_entry.weight

                        # proceed only if bone exists in our armature
                        if bone_indx != -1:
                            bone_weights[bone_indx] = bone_weight
                            bone_weights_sum += bone_weight

                    skin_entry = SkinStream.Entry(mesh_piece.get_index(), piece_vert_index, position, bone_weights, bone_weights_sum)
                    skin_stream.add_entry(skin_entry)

                    # report un-skinned vertices (no bones or zero sum weight) or badly skinned model
                    if bone_weights_sum <= 0:
                        missing_skinned_verts.add(vert_i)
                    elif bone_weights_sum < 1:
                        has_unnormalized_skin = True

                # 9. Terrain Points: save vertex to terrain points storage, if present in correct vertex group
                for group in mesh.vertices[vert_i].groups:

                    # if current object doesn't have vertex group found in mesh data, then ignore that group
                    # This can happen if multiple objects are using same mesh and
                    # some of them have vertex groups, but others not.
                    if group.group >= len(mesh_obj.vertex_groups):
                        continue

                    curr_vg_name = mesh_obj.vertex_groups[group.group].name

                    # if vertex group name doesn't match prescribed one ignore this vertex group
                    if not match(_OP_consts.TerrainPoints.vg_name_regex, curr_vg_name):
                        continue

                    # if node index is not in bounds ignore this vertex group
                    node_index = int(curr_vg_name[-1])
                    if node_index >= _PL_consts.PREFAB_NODE_COUNT_MAX:
                        continue

                    # if no variants defined add globally (without variant block)
                    if len(root_object.scs_object_variant_inventory) == 0:
                        used_terrain_points.add(-1, node_index, position, normal)
                        continue

                    # finally iterate variant parts entries to find where this part is included
                    # and add terrain points to transitional structure
                    #
                    # NOTE: variant index is donated by direct order of variants in inventory
                    # so export in PIT has to use the same order otherwise variant
                    # indices will be misplaced
                    for variant_i, variant in enumerate(root_object.scs_object_variant_inventory):

                        used_terrain_points.ensure_entry(variant_i, node_index)

                        for variant_part in variant.parts:
                            if variant_part.name == mesh_obj.scs_props.scs_part and variant_part.include:

                                used_terrain_points.add(variant_i, node_index, position, normal)
                                break

            # triangles
            if face_flip:
                mesh_piece.add_triangle(tuple(triangle_pvert_indices))
            else:
                mesh_piece.add_triangle(tuple(triangle_pvert_indices[::-1]))  # yep it's weird but it simply works vice versa

        # free normals calculations
        _mesh_utils.cleanup_mesh(mesh)
        _mesh_utils.cleanup_mesh(mesh_for_normals)

        # report missing data for each object
        if len(missing_uv_layers) > 0:
            for uv_lay_name in missing_uv_layers:
                lprint("W Object %r is missing UV layer %r specified by materials: %r",
                       (mesh_obj.name, uv_lay_name, missing_uv_layers[uv_lay_name]))
        if missing_vcolor:
            lprint("W Object %r is missing vertex color layer with name %r! Default RGB color will be exported (0.5, 0.5, 0.5)!",
                   (mesh_obj.name, _MESH_consts.default_vcol))
        if missing_vcolor_a:
            lprint("W Object %r is missing vertex color alpha layer with name %r! Default alpha will be exported (0.5)",
                   (mesh_obj.name, _MESH_consts.default_vcol + _MESH_consts.vcol_a_suffix))
        if len(missing_skinned_verts) > 0:
            lprint("E Object %r from SCS Root %r has %s vertices which are not skinned to any bone, expect errors during conversion!",
                   (mesh_obj.name, root_object.name, len(missing_skinned_verts)))
        if has_unnormalized_skin:
            lprint("W Object %r from SCS Root %r has unormalized skinning, exporting normalized weights!\n\t   "
                   "You can normalize weights by selecting object & executing 'Normalize All Vertex Groups'.",
                   (mesh_obj.name, root_object.name))

    # add rest of the pieces to global list
    for piece_key in mesh_pieces:

        part_name = piece_key.split("|")[1]  # get part from piece key (<material name>|<part name>|(optional)<mesh index>)
        piece = mesh_pieces[piece_key]

        # put pieces of current mesh to global list
        pim_pieces.append(piece)

        # add pieces of current mesh to part
        pim_part = pim_parts[part_name]
        pim_part.add_piece(piece)

    # report missing data for whole model
    if len(missing_mappings_data) > 0:
        for material_name in missing_mappings_data:
            lprint("W Material '%s' is missing mapping data! Objects using it are exported with default UV:\n\t   %s",
                   (material_name, list(missing_mappings_data[material_name].keys())))
    if len(objects_with_default_material) > 0:
        lprint("W Some objects don't use any material. Default material and UV mapping is used on them:\n\t   %s",
               (list(objects_with_default_material.keys()),))

    if len(invalid_objects_for_tangents) > 0:
        lprint("E N-gons present in some objects, thus normal map tangent calculation failed.\n\t   "
               "Visualization in game will be distorted for this objects:\n\t   %s",
               (list(invalid_objects_for_tangents),))

    # create locators data sections
    for loc_obj in model_locators:

        pos, qua, sca = _get_scs_transformation_components(root_object.matrix_world.inverted() * loc_obj.matrix_world)

        if sca[0] * sca[1] * sca[2] < 0:
            lprint("W Model locator %r inside SCS Root Object %r not exported because of invalid scale.\n\t   " +
                   "Model locators must have positive scale!", (loc_obj.name, root_object.name))
            continue

        name = _name_utils.tokenize_name(loc_obj.name)
        hookup_string = loc_obj.scs_props.locator_model_hookup
        hookup_id = None
        if hookup_string != "":
            hookup_id = _hookup_name_to_hookup_id(hookup_string)
            if hookup_id is None:
                lprint("W Model locator %r has unexpected hookup value %r.", (loc_obj.name, loc_obj.scs_props.locator_model_hookup))

        # create locator object for export
        locator = Locator(len(pim_locators), name, hookup_id)
        locator.set_position(pos)
        locator.set_rotation(qua)
        locator.set_scale(sca)

        # create part if it doesn't exists yet
        part_name = used_parts.ensure_part(loc_obj)
        if part_name not in pim_parts:
            pim_parts[part_name] = Part(part_name)

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

    for part_name in used_parts.get_as_list():

        # export all parts even empty ones used only in PIC and/or PIP
        if part_name in pim_parts:
            pim_container.append(pim_parts[part_name].get_as_section())
        else:
            pim_container.append(Part(part_name).get_as_section())

    for locator in pim_locators:
        pim_container.append(locator.get_as_section())

    if is_skin_used:
        pim_container.append(bones.get_as_section())
        pim_container.append(skin.get_as_section())

    # write to file
    ind = "    "
    pim_filepath = os.path.join(dirpath, root_object.name + ".pim" + name_suffix)
    return _pix_container.write_data_to_file(pim_container, pim_filepath, ind)
