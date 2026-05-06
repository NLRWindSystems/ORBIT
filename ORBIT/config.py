"""Provides the configuration loading and saving methods."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nlr.gov"


from pathlib import Path

import yaml
import numpy as np
from yaml import Dumper
from benedict.dicts import benedict

from ORBIT.core import loader


def load_config(filepath):
    """
    Load an ORBIT config at `filepath`.

    Parameters
    ----------
    filepath : str
        Path to yaml config file.
    """

    with Path(filepath).open() as f:
        data = yaml.load(f, Loader=loader)

    return data


def prepare_config_for_save(config: dict | benedict) -> dict:
    """Prepare the configuration file for compatbility with the YAML
    ``SafeDump`` class used for saving configurations to file.

    Parameters
    ----------
    config : dict | benedict
        ORBIT configuration dictionary.

    Returns
    -------
    dict
        ORBIT configuration dictionary where all NumPy data types are converted
        to standard Python data types, e.g. ``np.float64`` -> ``float``.
    """
    for k, v in config.items():
        match v:
            case np.ndarray():
                config[k] = v.tolist()
            case np.floating():
                config[k] = float(v)
            case np.integer():
                config[k] = int(v)
            case benedict():
                config[k] = prepare_config_for_save(v.dict())
            case dict():
                config[k] = prepare_config_for_save(v)
            case _:
                pass
    return config


def save_config(
    config: dict | benedict, filepath: str | Path, overwrite: bool = False
):
    """
    Save an ORBIT configuration to :py:attr:`filepath`.

    Parameters
    ----------
    config : dict | benedict
        ORBIT configuration.
    filepath : str | Path
        Location to save config.
    overwrite : bool (optional)
        Overwrite file if it already exists. Default: False.
    """

    filepath = Path(filepath).resolve()
    dirs = filepath.parent
    if not dirs.exists():
        dirs.mkdir(parents=True)

    if overwrite is False:
        if filepath.exists():
            raise FileExistsError(f"File already exists at '{filepath}'.")

    config = prepare_config_for_save(config)
    if isinstance(config, benedict):
        config = config.dict()

    with filepath.open("w") as f:
        yaml.dump(config, f, Dumper=Dumper, default_flow_style=False)
