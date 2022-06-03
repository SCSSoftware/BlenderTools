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

# Copyright (C) 2013-2021: SCS Software

import bpy
import blf
import bgl
from mathutils import Vector
from gpu_extras.presets import draw_texture_2d
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.internals.open_gl import locators as _locators
from io_scs_tools.internals.open_gl import primitive as _primitive
from io_scs_tools.internals.open_gl.cache import LocatorsCache
from io_scs_tools.internals.open_gl.storage import terrain_points as _terrain_points_storage
from io_scs_tools.internals.connections.wrappers import collection as _connections_wrapper
from io_scs_tools.utils import info as _info_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import view3d as _view3d_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import get_immediate_msg as _get_immediate_msg

_2d_elements_cache = LocatorsCache()


def _cache_custom_2d_elements(region, region_3d, space):
    """Caches custom 2D visual elements, that require custom OpenGL drawing in given 2D region of given 3D view.

    :param region:
    :type region: bpy.types.Region
    :param region_3d:
    :type region_3d: bpy.types.RegionView3D
    :return: list of valid cached custom elements for given region
    :rtype: list[bpy.types.Object]
    """
    scs_globals = _get_scs_globals()

    # locators display is switched off, don't even bother with caching and return empty list
    if not scs_globals.display_locators:
        return []

    # current viewport has disabled empties drawing, don't even bother with caching and return empty list
    if not bpy.context.space_data.show_object_viewport_empty:
        return []

    # no display info is currently enabled in scs globals, don't bother with caching and return empty list
    if scs_globals.display_info not in {'locnames', 'locinfo', 'locnodes', 'loclanes'}:
        return []

    # gather visible locators
    locators = []
    for visib_obj in bpy.context.visible_objects:
        # filter out any none locator objects
        if visib_obj.type != 'EMPTY' or visib_obj.scs_props.empty_object_type != 'Locator':
            continue

        # filter out none prefav/model/collision locators
        if visib_obj.scs_props.locator_type not in {'Prefab', 'Model', 'Collision'}:
            continue

        # filter out clipped locator objects
        is_clipped = False
        if region_3d.use_clip_planes:
            for clip_plane in region_3d.clip_planes:
                clip_plane_vec = Vector(clip_plane)
                obj_loc_vec = Vector((visib_obj.matrix_world[0][3], visib_obj.matrix_world[1][3], visib_obj.matrix_world[2][3], 1.0))
                if clip_plane_vec.dot(obj_loc_vec) < 0.0:
                    is_clipped = True
                    break

        if is_clipped:
            continue

        # filter out locator objects not present in local view
        if space.local_view and not visib_obj.local_view_get(space):
            continue

        locators.append(visib_obj)

    # cache infos only if proper display option is used
    if scs_globals.display_info == 'locinfo':
        _2d_elements_cache.cache_infos(locators)

    # cache location for current 3D view
    _2d_elements_cache.cache_locations_2d(locators, region, region_3d)

    return _2d_elements_cache.get_valid_locators(str(region_3d.perspective_matrix))


def _draw_3dview_report(window, area, region):
    """Draws reports in 3d views.

    :param window: window of 3D viewport
    :type window: bpy.types.Window
    :param area: area of 3D viewport
    :type area: bpy.types.Area
    :param region: region of 3D viewport
    :type region: bpy.types.Region
    """
    from io_scs_tools.operators.wm import SCS_TOOLS_OT_Show3DViewReport as _Show3DViewReport

    # no reported lines, we don't draw anything
    if not _Show3DViewReport.has_lines():
        return

    # calculate dynamic left and top margins
    if bpy.context.preferences.system.use_region_overlap:
        pos_x = 75
        # try to find tools region and properly adopt position X
        for reg in area.regions:
            if reg.type == 'TOOLS':
                pos_x = reg.width + 20
                break
        pos_y = region.height - 105
    else:
        pos_x = 20
        pos_y = region.height - 80

    # draw BT banner
    (bindcode, width, height) = _Show3DViewReport.get_scs_banner_img_data(window)

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    draw_texture_2d(bindcode, (pos_x - 5, pos_y), width, height)
    bgl.glDisable(bgl.GL_BLEND)

    # draw control buttons, if controls are enabled
    if _Show3DViewReport.has_controls(window):

        blf.size(0, 20, 72)
        blf.color(0, .8, .8, .8, 1)

        # set x and y offsets to report operator, so that area calculations for buttons can be calculated properly
        # considering dynamic left and top margins.
        _Show3DViewReport.set_btns_xy_offset(pos_x, region.height - pos_y)

        # draw close button
        _primitive.draw_rect_2d(
            (
                (pos_x + _OP_consts.View3DReport.CLOSE_BTN_AREA[0], pos_y - _OP_consts.View3DReport.CLOSE_BTN_AREA[2]),
                (pos_x + _OP_consts.View3DReport.CLOSE_BTN_AREA[1], pos_y - _OP_consts.View3DReport.CLOSE_BTN_AREA[2]),
                (pos_x + _OP_consts.View3DReport.CLOSE_BTN_AREA[1], pos_y - _OP_consts.View3DReport.CLOSE_BTN_AREA[3]),
                (pos_x + _OP_consts.View3DReport.CLOSE_BTN_AREA[0], pos_y - _OP_consts.View3DReport.CLOSE_BTN_AREA[3])
            ),
            (.25, .25, .25, 1)
        )

        # draw close button text
        blf.position(0, pos_x + _OP_consts.View3DReport.CLOSE_BTN_TEXT_POS[0], pos_y - _OP_consts.View3DReport.CLOSE_BTN_TEXT_POS[1], 0)
        blf.draw(0, _OP_consts.View3DReport.CLOSE_BTN_TEXT)

        # draw hide button
        _primitive.draw_rect_2d(
            (
                (pos_x + _OP_consts.View3DReport.HIDE_BTN_AREA[0], pos_y - _OP_consts.View3DReport.HIDE_BTN_AREA[2]),
                (pos_x + _OP_consts.View3DReport.HIDE_BTN_AREA[1], pos_y - _OP_consts.View3DReport.HIDE_BTN_AREA[2]),
                (pos_x + _OP_consts.View3DReport.HIDE_BTN_AREA[1], pos_y - _OP_consts.View3DReport.HIDE_BTN_AREA[3]),
                (pos_x + _OP_consts.View3DReport.HIDE_BTN_AREA[0], pos_y - _OP_consts.View3DReport.HIDE_BTN_AREA[3])
            ),
            (.25, .25, .25, 1)
        )

        # draw hide button text
        blf.position(0, pos_x + _OP_consts.View3DReport.HIDE_BTN_TEXT_POS[0], pos_y - _OP_consts.View3DReport.HIDE_BTN_TEXT_POS[1], 0)
        blf.draw(0, _OP_consts.View3DReport.HIDE_BTN_TEXT)

        # draw scroll controls
        if _Show3DViewReport.is_scrolled() and _Show3DViewReport.is_shown():

            blf.size(0, 16, 72)

            # draw scroll up button
            _primitive.draw_rect_2d(
                (
                    (pos_x + _OP_consts.View3DReport.SCROLLUP_BTN_AREA[0], pos_y - _OP_consts.View3DReport.SCROLLUP_BTN_AREA[2]),
                    (pos_x + _OP_consts.View3DReport.SCROLLUP_BTN_AREA[1], pos_y - _OP_consts.View3DReport.SCROLLUP_BTN_AREA[2]),
                    (pos_x + _OP_consts.View3DReport.SCROLLUP_BTN_AREA[1], pos_y - _OP_consts.View3DReport.SCROLLUP_BTN_AREA[3]),
                    (pos_x + _OP_consts.View3DReport.SCROLLUP_BTN_AREA[0], pos_y - _OP_consts.View3DReport.SCROLLUP_BTN_AREA[3])
                ),
                (.25, .25, .25, 1)
            )

            # draw scroll up button text
            blf.position(0, pos_x + _OP_consts.View3DReport.SCROLLUP_BTN_TEXT_POS[0], pos_y - _OP_consts.View3DReport.SCROLLUP_BTN_TEXT_POS[1], 0)
            blf.draw(0, _OP_consts.View3DReport.SCROLLUP_BTN_TEXT)

            # draw scroll down button
            _primitive.draw_rect_2d(
                (
                    (pos_x + _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[0], pos_y - _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[2]),
                    (pos_x + _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[1], pos_y - _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[2]),
                    (pos_x + _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[1], pos_y - _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[3]),
                    (pos_x + _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[0], pos_y - _OP_consts.View3DReport.SCROLLDOWN_BTN_AREA[3])
                ),
                (.25, .25, .25, 1)
            )

            # draw scroll down button text
            blf.position(0, pos_x + _OP_consts.View3DReport.SCROLLDOWN_BTN_TEXT_POS[0], pos_y - _OP_consts.View3DReport.SCROLLDOWN_BTN_TEXT_POS[1], 0)
            blf.draw(0, _OP_consts.View3DReport.SCROLLDOWN_BTN_TEXT)

    # draw version string
    pos_y -= 12
    blf.size(0, 10, 72)
    blf.color(0, .952, .635, .062, 1)
    blf.position(0, pos_x, pos_y, 0)
    blf.draw(0, _info_utils.get_combined_ver_str(only_version_numbers=True))
    pos_y -= 20

    # draw actual operator title and message if shown
    if _Show3DViewReport.is_shown():

        blf.enable(0, blf.SHADOW)

        blf.size(0, 12, 72)
        blf.color(0, 1, 1, 1, 1)
        blf.shadow(0, 0, 0, 0, 0, 1)

        if _Show3DViewReport.get_title() != "":
            blf.position(0, pos_x, pos_y, 0)
            blf.draw(0, _Show3DViewReport.get_title())
            pos_y -= 15

        _Show3DViewReport.set_out_of_bounds(False)
        for line in _Show3DViewReport.get_lines():

            # finish printing if running out of space
            if pos_y - 60 < 0:
                blf.position(0, pos_x, pos_y, 0)
                blf.draw(0, "...")
                pos_y -= 15
                _Show3DViewReport.set_out_of_bounds(True)
                break

            blf.position(0, pos_x, pos_y, 0)
            if "ERROR" in line:
                blf.shadow(0, 0, 0.5, 0., 0, 1)
            elif "WARNING" in line:
                blf.shadow(0, 0, 0.3, 0.15, 0, 1)

            blf.draw(0, line)
            pos_y -= 15

        blf.disable(0, blf.SHADOW)


def _draw_3dview_immediate_report(region):
    """Draws immediate report in the middle of the region if message exists.

    :param region: region of 3D viewport
    :type region: bpy.types.Region
    """
    immediate_msg = _get_immediate_msg()

    # if there is no message don't draw anything
    if not immediate_msg:
        return

    blf.enable(0, blf.SHADOW)
    blf.shadow(0, 0, 0, 0, 0, 1)

    # draw bacground areas
    _primitive.draw_rect_2d(
        (
            (0, region.height / 2 + 31),
            (region.width, region.height / 2 + 31),
            (region.width, region.height / 2 - 31),
            (0, region.height / 2 - 31)
        ),
        (0, 0, 0, .9)
    )

    _primitive.draw_rect_2d(
        (
            (0, region.height / 2 + 30),
            (region.width, region.height / 2 + 30),
            (region.width, region.height / 2 - 30),
            (0, region.height / 2 - 30)
        ),
        (.25, .25, .25, .9)
    )

    # set size of the immidete text
    blf.size(0, 18, 72)
    blf.color(0, .952, .635, .062, 1)

    # draw on center of the region
    width, height = blf.dimensions(0, immediate_msg)
    blf.position(0, region.width / 2 - width / 2, region.height / 2 - height / 4, 0)
    blf.draw(0, immediate_msg)

    blf.disable(0, blf.SHADOW)


def fill_buffers(object_list):
    """Fill drawing buffers with custom 3D visual elements for given objects.

    :param object_list: visible objects that should be checked and filled as custom visual elements; empty list when buffers should be emptied
    :type object_list: collections.Iterable
    """

    # assemble locators dictionaries and properly set empties display sizes
    prefab_locators = {}
    model_locators = {}
    collision_locators = {}

    for visib_obj in object_list:

        # passed object reference got removed
        try:
            # do simple name access, to trigger possible reference error.
            _ = visib_obj.name
        except ReferenceError:
            continue

        if visib_obj.type != 'EMPTY':
            continue

        if visib_obj.scs_props.empty_object_type != 'Locator':
            continue

        if not visib_obj.visible_get():
            continue

        if visib_obj.scs_props.locator_type == 'Prefab':
            prefab_locators[visib_obj.name] = visib_obj
            _object_utils.store_locators_original_display_size_and_type(visib_obj)
            _object_utils.set_locators_prefab_display_size_and_type(visib_obj)
        elif visib_obj.scs_props.locator_type == 'Model':
            model_locators[visib_obj.name] = visib_obj
            _object_utils.store_locators_original_display_size_and_type(visib_obj)
            _object_utils.set_locators_model_display_size_and_type(visib_obj)
        elif visib_obj.scs_props.locator_type == 'Collision':
            collision_locators[visib_obj.name] = visib_obj
            _object_utils.store_locators_original_display_size_and_type(visib_obj)
            _object_utils.set_locators_coll_display_size_and_type(visib_obj)
        elif visib_obj.scs_props.locators_orig_display_size != 0.0:
            _object_utils.set_locators_original_size_and_type(visib_obj)

    # clear buffers
    _primitive.clear_buffers()

    # reset any set active buffer, switch back to main ones
    _primitive.set_active_buffers(None)

    # fill buffers for main view
    _fill_active_buffers(prefab_locators, model_locators, collision_locators)

    # extra buffers filling for each local view
    for space in _view3d_utils.get_spaces_with_local_view():

        local_prefab_locators = {}
        local_model_locators = {}
        local_collision_locators = {}

        for obj_name in prefab_locators:
            if prefab_locators[obj_name].local_view_get(space):
                local_prefab_locators[obj_name] = prefab_locators[obj_name]

        for obj_name in model_locators:
            if model_locators[obj_name].local_view_get(space):
                local_model_locators[obj_name] = model_locators[obj_name]

        for obj_name in collision_locators:
            if collision_locators[obj_name].local_view_get(space):
                local_collision_locators[obj_name] = collision_locators[obj_name]

        # set active buffers depending on given 3d space
        _primitive.set_active_buffers(space)

        # now fill in locators visible in this space
        _fill_active_buffers(local_prefab_locators, local_model_locators, local_collision_locators)


def _fill_active_buffers(prefab_locators, model_locators, collision_locators):
    """Fill active buffers with given locator dictionaries.

    :param prefab_locators: prefab locators that should be filled into active buffers
    :type prefab_locators: dict[bpy.types.Object]
    :param model_locators: model locators that should be filled into active buffers
    :type model_locators: dict[bpy.types.Object]
    :param collision_locators: collision locators that should be filled into active buffers
    :type collision_locators: dict[bpy.types.Object]
    """
    scs_globals = _get_scs_globals()

    # fill terrain points always
    for tp_position, tp_color in _terrain_points_storage.get_positions_and_colors():
        _primitive.draw_point(tp_position, tp_color, 5.0)

    # fill curves and lines
    if scs_globals.display_connections:
        _connections_wrapper.draw(prefab_locators)

    # fill locators
    if scs_globals.display_locators:

        for obj in prefab_locators.values():
            _locators.prefab.draw_prefab_locator(obj, scs_globals)

        for obj in model_locators.values():
            _locators.model.draw_model_locator(obj, scs_globals)

        for obj in collision_locators.values():
            _locators.collider.draw_collision_locator(obj, scs_globals)


def draw_custom_3d_elements(mode):
    """Draws custom 3D elements filled in buffers (if local view is active, then buffers are refilled also).

    :param mode: drawing mode for custom 3D elements (can be: 'Normal' or 'X-ray')
    :type mode: str
    """
    # if empties are disabled in this viewport ... our locators and connections should be too
    if not bpy.context.space_data.show_object_viewport_empty:
        return

    if mode == "Normal":
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    # draw buffers
    _primitive.draw_buffers(bpy.context.space_data)

    if mode == "Normal":
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_BLEND)


def draw_custom_2d_elements():
    """Draws custom 2D elements from cache.
    """
    context = bpy.context
    scs_globals = _get_scs_globals()

    region = context.region
    region_3d = context.region_data
    space = context.space_data
    area = context.area
    window = context.window

    # draw 3d view import/export reports
    _draw_3dview_report(window, area, region)

    # draw 3d view immediate reports
    _draw_3dview_immediate_report(region)

    # cache & get valid locators for current region boundaries
    locators = _cache_custom_2d_elements(region, region_3d, space)

    # no locators, we can safely finish here
    if not locators:
        return

    font_id = 0  # default font
    blf.size(font_id, 12, 72)
    blf.color(font_id, scs_globals.info_text_color[0], scs_globals.info_text_color[1], scs_globals.info_text_color[2], 1.0)
    blf.word_wrap(font_id, 999)
    blf.enable(font_id, blf.WORD_WRAP)

    persp_matrix_str = str(region_3d.perspective_matrix)

    # LOCATOR NAMES
    if scs_globals.display_info == 'locnames':
        for obj in locators:
            loc_2d = _2d_elements_cache.get_locator_location_2d(obj, persp_matrix_str)
            _primitive.draw_text(obj.name, font_id, loc_2d.x, loc_2d.y)

    # LOCATOR COMPREHENSIVE INFO
    elif scs_globals.display_info == 'locinfo':
        for obj in locators:
            loc_2d = _2d_elements_cache.get_locator_location_2d(obj, persp_matrix_str)
            loc_info = _2d_elements_cache.get_locator_info(obj)
            _primitive.draw_text(loc_info, font_id, loc_2d.x, loc_2d.y)

    # LOCATOR BOUNDARY NODES
    elif scs_globals.display_info == 'locnodes':
        for obj in locators:
            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                loc_2d = _2d_elements_cache.get_locator_location_2d(obj, persp_matrix_str)
                _primitive.draw_text(str(obj.scs_props.locator_prefab_np_boundary_node), font_id, loc_2d.x, loc_2d.y)

    # LOCATOR BOUNDARY LANES
    elif scs_globals.display_info == 'loclanes':
        for obj in locators:
            if obj.scs_props.locator_prefab_type == 'Navigation Point':
                if obj.scs_props.locator_prefab_np_boundary != 'no':
                    np_boundary_i = int(obj.scs_props.locator_prefab_np_boundary)
                    if np_boundary_i == 0:
                        continue

                    loc_2d = _2d_elements_cache.get_locator_location_2d(obj, persp_matrix_str)
                    _primitive.draw_text(str(obj.scs_props.enum_np_boundary_items[np_boundary_i][1]), font_id, loc_2d.x, loc_2d.y)

    blf.disable(font_id, blf.WORD_WRAP)
