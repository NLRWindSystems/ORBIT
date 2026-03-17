"""The design package contains `DesignPhase` and its subclasses."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = ["Jake Nunemaker", "Rob Hammond"]
__email__ = ["jake.nunemaker@nlr.gov" "rob.hammond@nlr.gov"]


from .design_phase import DesignPhase  # isort:skip
from .oss_design import OffshoreSubstationDesign
from .spar_design import SparDesign
from .monopile_design import MonopileDesign
from .electrical_export import ElectricalDesign
from .array_system_design import ArraySystemDesign, CustomArraySystemDesign
from .oss_design_floating import OffshoreFloatingSubstationDesign
from .export_system_design import ExportSystemDesign
from .mooring_system_design import MooringSystemDesign
from .scour_protection_design import ScourProtectionDesign
from .semi_submersible_design import SemiSubmersibleDesign
