__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nlr.gov"

from pathlib import Path

import pandas as pd

DIR = Path(__file__).resolve().parent
_fp = DIR / "test_weather.csv"
test_weather = (
    pd.read_csv(_fp, parse_dates=["datetime"])
    .set_index("datetime")
    .to_records()
)
