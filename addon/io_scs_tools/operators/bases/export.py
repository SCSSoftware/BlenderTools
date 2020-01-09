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

# Copyright (C) 2019: SCS Software

import bpy
from io_scs_tools import exp as _export
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


class SCSExportHelper:
    """Class for implementation of SCS export routines, to take care of objects/collections visibilites and
    implemenet convinient methods for usage as parent class in export operators.
    """

    def __init__(self):
        self.cached_objects = None
        """:type list[bpy.types.Object]: Used in selection mode to cache selected objects, to avoid multiple collecting."""
        self.objects_states = dict()
        """:type dict[bpy.types.Object, boo]]: Hide & selection states for objects gathered on selection export. Used to restore 
        their states after export."""
        self.collection_visibilites = dict()
        """:type dict[bpy.types.Object, bool]: Original collection visibilities used to restore their state after export."""
        self.scene = None
        """:type bpy.types.Scene: Scene to which we will temporarly link objects that needs to be exported."""
        self.active_scene = None
        """:type bpy.types.Scene: Scene which was active before export and should be recovered as active once export is done."""

    def get_objects_for_export(self):
        """Get objects for export, list filtered and extended depending on export scope.

        :return: list of objects to export calculated from selection
        :rtype: list[bpy.types.Object]
        """

        # if cached, just return
        if self.cached_objects:
            return self.cached_objects

        objs_to_export = []

        export_scope = _get_scs_globals().export_scope
        if export_scope == "selection":
            for root in _object_utils.gather_scs_roots(bpy.context.selected_objects):
                objs_to_export.append(root)

                children = _object_utils.get_children(root)
                children_unselected = []
                children_selected = []

                for child_obj in children:
                    if child_obj.select_get():
                        children_selected.append(child_obj)
                    else:
                        children_unselected.append(child_obj)

                # if any children was selected make sure, to export only them
                if len(children_selected) > 0:
                    objs_to_export.extend(children_selected)
                else:
                    objs_to_export.extend(children_unselected)
        elif export_scope == "scene":
            objs_to_export = tuple(bpy.context.scene.objects)
        elif export_scope == "scenes":
            objs_to_export = tuple(bpy.data.objects)

        # cache filtered list, to be able to retrive it quickly on second call
        self.cached_objects = objs_to_export

        return self.cached_objects

    def init(self):
        """Init routine to create export scene, link all exprt objects to it and unhide objects so they can be seen in preview and exported properly.
        The problem is that depsgraph doesn't apply modifiers if object is hidden (directly or via collections).

        NOTE: Should be called before get_objects_for_export.
        """

        # we have to get object to export now, because creating new scene
        # will invalidate context and selected objects within context are lost.
        objs_to_export = self.get_objects_for_export()

        # create export scene
        self.scene = bpy.data.scenes.new("SCS Export")
        self.active_scene = bpy.context.window.scene
        bpy.context.window.scene = self.scene

        # link objects to export scene and unhide all of them
        for obj in objs_to_export:
            self.scene.collection.objects.link(obj)
            self.objects_states[obj] = obj.hide_viewport
            obj.hide_viewport = False

        scs_globals = _get_scs_globals()
        if scs_globals.export_scope == "selection" and scs_globals.preview_export_selection:
            scs_globals.preview_export_selection_active = True

    def finish(self):
        """Finish routine to restore objects & scene state after export.

        NOTE: Should be called after export has completed.
        """
        _get_scs_globals().preview_export_selection_active = False

        for obj, state in self.objects_states.items():
            obj.hide_viewport = state

        # recover old active scene and remove temporary one
        bpy.context.window.scene = self.active_scene
        bpy.data.scenes.remove(self.scene)
        self.scene = None

    def execute_export(self, context, without_preview, menu_filepath=None):
        """Executes export.

        :param context: operator context
        :type context: bpy_struct
        :param without_preview: is export run without preview?
        :type without_preview: bool
        :param menu_filepath: filepath used from menu export, if not provided export is done to none menu set path
        :type menu_filepath: str
        :return: success of batch export
        :rtype: {'FINISHED'} | {'CANCELLED'}
        """

        # show all collections, if normal export, so all modifiers will be applied correctly
        if without_preview:
            self.init()

        init_obj_list = self.get_objects_for_export()

        # check extension for EF format and properly assign it to name suffix
        ef_name_suffix = ""
        if _get_scs_globals().export_output_type == "EF":
            ef_name_suffix = ".ef"

        try:
            result = _export.batch_export(self, init_obj_list, name_suffix=ef_name_suffix, menu_filepath=menu_filepath)
        except Exception as e:

            result = {"CANCELLED"}
            context.window.cursor_modal_restore()

            import traceback

            trace_str = traceback.format_exc().replace("\n", "\n\t   ")
            lprint("E Unexpected %r accured during batch export:\n\t   %s",
                   (type(e).__name__, trace_str),
                   report_errors=1,
                   report_warnings=1)

        # restore collections visiblities if normal export
        if without_preview:
            self.finish()

        return result
