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

from io_scs_tools.internals.shaders.eut2.dif_spec_oclu import DifSpecOclu
from io_scs_tools.internals.shaders.eut2.std_passes.add_env import StdAddEnv


class DifSpecOcluWeightAddEnv(DifSpecOclu, StdAddEnv):
    VCOLOR_SPEC_MULT_NODE = "VertexColorSpecMultiplier"

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

        spec_mult_n = node_tree.nodes[DifSpecOclu.SPEC_MULT_NODE]
        vcol_scale_n = node_tree.nodes[DifSpecOclu.VCOLOR_SCALE_NODE]
        compose_lighting_n = node_tree.nodes[DifSpecOclu.COMPOSE_LIGHTING_NODE]

        # init nodes
        vcol_spec_mult_n = node_tree.nodes.new("ShaderNodeVectorMath")
        vcol_spec_mult_n.name = vcol_spec_mult_n.label = DifSpecOcluWeightAddEnv.VCOLOR_SPEC_MULT_NODE
        vcol_spec_mult_n.location = (spec_mult_n.location.x + 185, spec_mult_n.location.y)
        vcol_spec_mult_n.operation = "MULTIPLY"

        # make links
        node_tree.links.new(vcol_spec_mult_n.inputs[0], spec_mult_n.outputs[0])
        node_tree.links.new(vcol_spec_mult_n.inputs[1], vcol_scale_n.outputs[0])

        node_tree.links.new(compose_lighting_n.inputs['Specular Color'], vcol_spec_mult_n.outputs[0])

        # init env pass
        StdAddEnv.add(node_tree,
                      DifSpecOclu.GEOM_NODE,
                      node_tree.nodes[DifSpecOclu.SPEC_COL_NODE].outputs['Color'],
                      node_tree.nodes[DifSpecOclu.BASE_TEX_NODE].outputs['Alpha'],
                      node_tree.nodes[DifSpecOclu.LIGHTING_EVAL_NODE].outputs['Normal'],
                      node_tree.nodes[DifSpecOclu.COMPOSE_LIGHTING_NODE].inputs['Env Color'])

        oclu_sep_n = node_tree.nodes[DifSpecOclu.OCLU_SEPARATE_RGB_NODE]
        vcol_scale_n = node_tree.nodes[DifSpecOclu.VCOLOR_SCALE_NODE]
        add_env_gn = node_tree.nodes[StdAddEnv.ADD_ENV_GROUP_NODE]

        # links creation
        node_tree.links.new(add_env_gn.inputs['Weighted Color'], vcol_scale_n.outputs[0])
        node_tree.links.new(add_env_gn.inputs['Strength Multiplier'], oclu_sep_n.outputs['R'])
