"""Default inputs used throughout ORBIT."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nlr.gov"

from pathlib import Path

import yaml

from ORBIT.core.library import loader

DIR = Path(__file__).parent

with (DIR / "process_times.yaml").open() as f:
    process_times = yaml.load(f, Loader=loader)


with (DIR / "common_costs.yaml").open() as f:
    common_costs = yaml.load(f, Loader=loader)
