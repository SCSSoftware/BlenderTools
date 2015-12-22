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

from io_scs_tools.exp.pip.curve import Curve
from io_scs_tools.exp.pip.intersection import Intersection
from io_scs_tools.exp.pip.map_point import MapPoint
from io_scs_tools.exp.pip.node import Node
from io_scs_tools.exp.pip.semaphore import Semaphore
from io_scs_tools.exp.pip.sign import Sign
from io_scs_tools.exp.pip.spawn_point import SpawnPoint
from io_scs_tools.exp.pip.trigger_point import TriggerPoint
from io_scs_tools.internals.structure import SectionData as _SectionData


class Globall:
    def __init__(self):
        """Constructs global for PIP.
        """
        Node.reset_counter()
        Curve.reset_counter()
        Sign.reset_counter()
        SpawnPoint.reset_counter()
        Semaphore.reset_counter()
        MapPoint.reset_counter()
        TriggerPoint.reset_counter()
        Intersection.reset_counter()

    @staticmethod
    def get_as_section():
        """Gets global prefab information represented with SectionData structure class.
        :return: packed globals as section data
        :rtype: io_scs_tools.internals.structure.SectionData
        """

        section = _SectionData("Global")
        section.props.append(("NodeCount", Node.get_global_node_count()))
        section.props.append(("TerrainPointCount", Node.get_global_tp_count()))
        section.props.append(("TerrainPointVariantCount", Node.get_global_tp_variant_count()))
        section.props.append(("NavCurveCount", Curve.get_global_curve_count()))
        section.props.append(("SignCount", Sign.get_global_sign_count()))
        section.props.append(("SpawnPointCount", SpawnPoint.get_global_spawn_point_count()))
        section.props.append(("SemaphoreCount", Semaphore.get_global_semaphore_count()))
        section.props.append(("MapPointCount", MapPoint.get_global_map_point_count()))
        section.props.append(("TriggerPointCount", TriggerPoint.get_global_trigger_point_count()))
        section.props.append(("IntersectionCount", Intersection.get_global_intersection_count()))

        return section
