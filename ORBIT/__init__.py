"""Initializes ORBIT and provides the top-level import objects."""

__author__ = [
    "Jake Nunemaker",
    "Matt Shields",
    "Rob Hammond",
    "Nick Riccobono",
]
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Nick Riccobono"
__email__ = ["nicholas.riccobono@nlr.gov", "rob.hammond@nlr.gov"]
__status__ = "Development"


from ORBIT.manager import ProjectManager  # isort:skip
from ORBIT.config import load_config, save_config
from ORBIT.parametric import ParametricManager
from ORBIT.supply_chain import SupplyChainManager

__version__ = "1.3"
