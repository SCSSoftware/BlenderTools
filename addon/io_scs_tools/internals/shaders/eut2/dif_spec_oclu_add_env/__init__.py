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

# Copyright (C) 2015: SCS Software


from io_scs_tools.internals.shaders.eut2.dif_spec_oclu import DifSpecOclu
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv


class DifSpecOcluAddEnv(DifSpecOclu, StdAddEnv):
    REFL_TEX_NODE = "ReflectionTex"
    ENV_COLOR_NODE = "EnvFactorColor"
    ADD_ENV_GROUP_NODE = "AddEnvGroup"
    OUT_ADD_REFL_NODE = "OutputAddRefl"

    @staticmethod
    def get_name():
        """Get name of this shader file with full modules path."""
        return __name__

    @staticmethod
    def init(node_tree):
        """Initialize node tree with links for this shader.

        :param node_tree: node tree on which this shader should be created
        :type node_tree: bpy.types.NodeTree
        """

        # init parent
        DifSpecOclu.init(node_tree)

        StdAddEnv.add(node_tree,
                      DifSpecOclu.GEOM_NODE,
                      DifSpecOclu.SPEC_COL_NODE,
                      DifSpecOclu.BASE_TEX_NODE,
                      DifSpecOclu.OUT_MAT_NODE,
                      DifSpecOclu.OUTPUT_NODE)
