"""The install package contains `InstallPhase` and its subclasses."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = ["Jake Nunemaker", "Rob Hammond"]
__email__ = ["jake.nunemaker@nlr.gov" "rob.hammond@nlr.gov"]

from .install_phase import InstallPhase  # isort:skip
from .oss_install import (
    FloatingSubstationInstallation,
    OffshoreSubstationInstallation,
)
from .cable_install import ArrayCableInstallation, ExportCableInstallation
from .jacket_install import JacketInstallation
from .mooring_install import MooringSystemInstallation
from .turbine_install import TurbineInstallation
from .monopile_install import MonopileInstallation
from .quayside_assembly_tow import (
    MooredSubInstallation,
    GravityBasedInstallation,
)
from .scour_protection_install import ScourProtectionInstallation

install_phases = [
    "MonopileInstallation",
    "JacketInstallation",
    "ScourProtectionInstallation",
    "GravityBasedInstallation",
    "MooredSubInstallation",
    "MooringSystemInstallation",
    "TurbineInstallation",
    "ArrayCableInstallation",
    "ExportCableInstallation",
    "OffshoreSubstationInstallation",
    "FloatingSubstationInstallation",
]
