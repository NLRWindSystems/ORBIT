---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(project-manager-tutorial)=
# `ProjectManager` Deep Dive

`ProjectManager` is the primary system for interacting with ORBIT. It provides the ability to
configure and run one or multiple models at a time, allowing the user to customize ORBIT to fit the
needs of a specific project.

```{code-cell} ipython3
from pprint import pprint

import pandas as pd

from ORBIT import ProjectManager
```

## Compiling Input Requirements Dynamically

To better understand the input requirements for designing and installing multiple turbine subsystems,
`ProjectManager` provides the `compile_input_dict()` method that will generate the expected
configuration of each provided phase in a single configuration dictionary. The example below shows
how to configure a simple project with a design and multiple installation phases, and return the required configuration parameters.

```{code-cell} ipython3
phases = [
    "MonopileDesign",
    "MonopileInstallation",
    "TurbineInstallation",
]

expected_config = ProjectManager.compile_input_dict(phases)
pprint(expected_config)
```

Using the results of the `expected_config`, the following configuration is now created to minimally
define a project running only the scouring protection and monopile phases for design and
installation.

```{code-cell} ipython3
config = {
    "site": {
        "depth": 20,
        "distance": 50,
        "mean_windspeed": 9.5,
    },
    "plant": {
        "num_turbines": 50,
    },
    "turbine": {
        "rotor_diameter": 205,
        "hub_height": 125,
        "rated_windspeed": 11,
    },
    "wtiv": "example_wtiv",
    "design_phases": ["MonopileDesign"],
    "install_phases": ["MonopileInstallation", "TurbineInstallation"],
}

project = ProjectManager(config)
project.run()
```

## Weather Profiles

To include wind and wave conditions in the simulation for vessel and port constraints, pass an
hourly pandas DataFrame to `ProjectManager` using the `weather` keyword argument. All installation
phases will now use this time series to account for weather delays.

```python
weather = pd.read_csv(
    "path/to/library/weather/example_weather.csv",
    parse_dates=["datetime"]
).set_index("datetime")

project = ProjectManager(config, weather=weather_df)
```

## Accessing Individual Models

The `ProjectManager` provides a dictionary-based attribute `phases` that allows users to access the
design or installation class for custom results gathering or model inspection. Using the previously
run project, we now directly access the monopile design costs.

```{code-cell} ipython3
monopile_design_cost = project.phases["MonopileDesign"].total_cost
print(f"Total Monopile Cost: ${monopile_design_cost / 1e6:,.2f} M")
```

## Phase-Specific Configurations

As was seen in [inputs compilation demonstration](#compiling-input-requirements-dynamically),
`ProjectManager` compiles the minimum required configuration, combining the same parameter that is
needed for multiple phases into one input. This isn't always a desired outcome as there are cases
when inputs need to be different for each phase. For example, the `distance_to_shore` parameter may
be different for each installation phase if different ports are used to stage monopiles and turbines
or the installations may use different installation vessels.

In these cases, it is necessary to define phase specific input parameters using the phase's name as
the dictionary key. Below, we can see how we model a differing staging port where a separate WTIV
will be used with its much further port distance.

Please note that phase-specific configurations will always override their general counterparts.

```python
config = {
    "site": {
        "depth": 20,
        "distance": 50,
        "mean_windspeed": 9.5,
    },
    "plant": {
        "num_turbines": 50,
    },
    "turbine": {
        "rotor_diameter": 205,
        "hub_height": 125,
        "rated_windspeed": 11,
    },
    "TurbineInstallation": {
        "wtiv": "other_wtiv",
        "site": {
            "distance": 100,
        },
    },
    "wtiv": "example_wtiv",
    "design_phases": ["MonopileDesign"],
    "install_phases": ["MonopileInstallation", "TurbineInstallation"],
}
```
