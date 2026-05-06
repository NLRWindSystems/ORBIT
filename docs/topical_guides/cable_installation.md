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

# Cable Laying and Burying

This guide will demonstrate the use of a combined cable laying and burying vessel compared to using
separate cable laying and burying vessels. Here we will focus on the array cabling, but the same
logic applies to the export cables.

```{code-cell} ipython3
from copy import deepcopy

import pandas as pd

from ORBIT import ProjectManager
```

Below, we set up a base configuration using an imagined cable and sections (25 each of 1km and 2km cable sections) designed for simplicity.

```{code-cell} ipython3
base_config = {
    "site": {"distance": 20, "depth": 35},
    "array_system": {
        "system_cost": 50e6,
        "cables": {
            "ExampleCable": {
                "linear_density": 40,
                "cable_sections": [(2, 25), (1, 25)]
            }
        }
    },
    "install_phases": ["ArrayCableInstallation"]
}
```

## Single Cable Laying and Burying Process

Now we can add a cable laying vessel that will simultaneously lay and bury cables by defining the
`array_cable_install_vessel`. For export cables, this is the `export_cable_install_vessel`. We will
create and run the project for later results comparison.

```{code-cell} ipython3
config_combined = deepcopy(base_config)
config_combined["array_cable_install_vessel"] = "example_cable_lay_vessel"

project_combined = ProjectManager(config_combined)
project_combined.run()
```

## Separate Cable Laying and Burying Processes

Using the same base configuration, we can now signal to the simulation to use a separate cable
laying and burying process by defining both the `array_cable_install_vessel` and
`array_cable_bury_vessel`. Note that the laying and combined vessel configuration keys are the same,
so that a separate input is only required when the cable burying vessel is utilized. Similar to the
above example, the export cable burying vessel is `export_cable_bury_vessel`.

Even though the vessel is the same, by defining both vessel keys, we indicate that the processes
should be separated.

```{code-cell} ipython3
config_separate = deepcopy(base_config)
config_separate["array_cable_install_vessel"] = "example_cable_lay_vessel"
config_separate["array_cable_bury_vessel"] = "example_cable_lay_vessel"

project_separate = ProjectManager(config_separate)
project_separate.run()
```

## Including a Trenching Vessel

A third option is to also define a cable trenching vessel that digs out the trench for the cable
to lie in prior to the cable laying. This is often required for rocky soil types. Similar to the
separate process, we simply define the trenching vessel to activate the separated process using
the `array_cable_trench_vessel` key or `export_cable_trench_vessel` for export cables.

```{code-cell} ipython3
config_separate_with_trench = deepcopy(base_config)
config_separate_with_trench["array_cable_install_vessel"] = "example_cable_lay_vessel"
config_separate_with_trench["array_cable_bury_vessel"] = "example_cable_lay_vessel"
config_separate_with_trench["array_cable_trench_vessel"] = "example_cable_lay_vessel"

# Run
project_separate_with_trench = ProjectManager(config_separate_with_trench)
project_separate_with_trench.run()
```

## Viewing the results

Below we show the combined process for laying and burying the first cable. Note the "action"
column contains the "Lay/Bury" action to indicate the combined process.

```{code-cell} ipython3
df_combined = pd.DataFrame(project_combined.actions)
df_combined.iloc[3:12]
```

Now, we demonstrate the separate process by combining the separate laying and burying steps taken
for the first cable. Note that we have to concatenate two separate sections of the actions log
to highlight this process. For each process the vessel has to "Position Onsite", then go on
with the separate logic. For the burying process, this is much simpler than the initial laying
and cable connection.

```{code-cell} ipython3
df_separate = pd.DataFrame(project_separate.actions)
pd.concat((df_separate.iloc[4:13], df_separate.iloc[455:457]))

```

Similar to the above, when we add trenching as a separate step, we have three discrete stages to
combine to demonstrate the trenching, laying, and burying for the first cable.

```{code-cell} ipython3
df_separate_with_trench = pd.DataFrame(project_separate_with_trench.actions)
pd.concat((
    df_separate_with_trench.iloc[4:6],
    df_separate_with_trench.iloc[107:116],
    df_separate_with_trench.iloc[558:560],
))
```
