---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

(custom-array-layou)=
# Custom Array Cabling Guide

## Dudgeon Windfarm

This guide will walk through four of the main use cases for using the custom array cable layout
functionality of `ORBIT` for when custom turbine locations, cable lengths or burial speeds are needed.

This example uses the Dudgeon Wind Farm turbine locations derived from their publicly available
[Call to Mariners](http://dudgeonoffshorewind.co.uk/news/notices/Dudgeon%20-%20Notice%20to%20Mariners%20wk25.pdf) documents.

## Setup

First, we'll import the necessary libraries and functionality, and setup our library reference.

```{code-cell} ipython3
from copy import deepcopy
from pprint import pprint
from pathlib import Path

import numpy as np
import pandas as pd

import ORBIT
from ORBIT import ProjectManager
from ORBIT.core import library
from ORBIT.phases.design import CustomArraySystemDesign
from ORBIT.phases.install import ArrayCableInstallation


# Set the library path for later use and initialize the ORBIT library
here = Path(".").resolve()
library_path = here.parents[1] / "library" if here.stem == "topical_guides" else here
library.initialize_library(library_path)
```

## Contents

- [Overview](#overview): How to use the inputs
- [Case 1](#case_1): Needing to know what to collect
- [Case 2](#case_2): Coordinates with a straight-line distance for cable length
- [Case 3](#case_3): Using distance from a reference point
- [Case 4](#case_4): Adjusting for exclusions in the cable paths
- [Case 5](#case_5): Fully customizing the cabling parameters
- [Applying the cases to `ArrayCableInstallation`](#running)
- [Using `ProjectManager` to model the entire process](#project_manager)

## Overview

### Working with the ORBIT Library

In the highest level of this repository there is a folder called `library` where all of the example
data for this notebook is going to be stored. While any folder could be used, the folder structure
must be strictly adhered to. More details on this structure can be found in the
[library section of the ORBIT introduction tutorial](#library-tutorial).

For this example of how to setup a configuration, we will be using the file
[`library/project/config/example_custom_array_simple.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/project/config/example_custom_array_simple.yaml).

Now, we will load the configuration file and display it below.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_simple")
pprint(config)
```

### Key Differences In A Custom Layout Configuration

There are 2 important differences in the custom array design that are work calling out:

1) The `array_system_design` dictionary contains the `location_data` key, which contains the base
   file name for the layout file, which is assumed to be CSV file located at
   [`library/cables/dudgeon_array.csv`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/dudgeon_array.csv)
2) The `plant` dictionary uses the "custom" for `layout` to indicate that the custom array design
   workflow will be used.

Now, let's see what is contained within the additional files from the configuration dictionary. It
should be noted that running the design class extracts the data from the files automatically to
produce the below output.

```{code-cell} ipython3
array = CustomArraySystemDesign(config)
array.run()
print(array.config.dump())
```

### Custom Array Layout CSV Explanation

When the `dudgeon_array.csv` file is loaded, it is not passed back into the configuration
dictionary, so let's dissect this file:

1. The file must have all of the columns shown below (not case-sensitive).
   - All columns must be completely filled out for turbines (note on substation(s) following).
   - `cable_length` and `bury_speed` are optional and if these are not known, simply fill with a 0.
2. A latitude and longitude must be provided for all turbines and substation(s). This can either be
   a WGS-84 decimal coordinate or a distance-based "coordinate" where latitude and longitude are the
   distances from some reference point, in kilometers; see [Case 3](#case_3) for more details.
3. Define the offshore substation(s)
   - For each substation, the values in columns `id` and `substation_id` _must_ be the same.
   - There is no need to fill in any data for the columns `String`, `Order`, `cable_length` and
     `bury_speed`.
4. Define the turbines
   - Each turbine should have a reference to its substation in the `substation_id` column.
     - In this example, there is one substaion, so all of the values are "DOW_OSS".
   - `string` and `order` should be 0-indexed for their ordering and not skip any numbers.
     - In this example, the strings are ordered in clock-wise order starting from the string with
       turbines labeled with an "A" in the
       [Call to Mariners](http://dudgeonoffshorewind.co.uk/news/notices/Dudgeon%20-%20Notice%20to%20Mariners%20wk25.pdf)
   - The ordering on a string should travel from substation to the farthest end of the cable

Below is the how the Dudgeon layout has been configured.

```{code-cell} ipython3
df = pd.read_csv(library_path / "cables/dudgeon_array.csv").fillna("")
df.sort_values(by=["String", "Order"])
```

(case_1)=
## Case 1: Needing to know what to collect

In this first case, we assume little knowledge of what data are required for the CSV, and walk
through generating a sample CSV. We will use the
[`library/cables/example_custom_array_no_data.csv`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_custom_array_no_data.csv)
configuration for this example.

First, we need to load in the configuration dictionary. Then, we will create a starter file in
the `<library_path>/project/config/plant` folder that can be filled in for a new project, which will be saved in the initialized library folder.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_no_data")
pprint(config)

array = CustomArraySystemDesign(config)
save_name = array.config["array_system_design"]["location_data"]
array.create_project_csv(save_name, folder="plant")
```

There are a few items worth noting in the layout:

1. The offshore substation (row 0) is indicated via the `id` and `substation_id` columns being equal
2. For substaions only the `id`, `substation_id`, `name`, `latitude`, and `longitude` are required
3. `cable_length` and `bury_speed` are optional columns for turbines
4. `string` and `order` are filled out to maximize the length of a string given the cable(s)
   provided, which translates to a maximum of 5 turbines in a string.
5. The string and cable numbering are 0-indexed, so the numbering system starts with 0.

```{code-cell} ipython3
dudgeon_array_no_data = pd.read_csv(library_path / f"project/plant/{save_name}.csv")
dudgeon_array_no_data

# NOTE: remove this line if you would like to keep this data
Path(library_path / "project/plant/dudgeon_array_no_data.csv").unlink()
```

(case_2)=
## Case 2: Straight-Line Distance for Cable Lengths

We have the turbine and offshore substation locations that were extracted from the Call to Mariners
referenced in the [Dudgeon Wind Farm Overview](#dudgeon-windfarm). However there is not any
information regarding the actual cable lengths or the cable burial speeds for each section. As such,
we will demonstrate using the standard straight-line distance and default cable burying rates.

This case will rely on the
[`library/cables/example_custom_array_simple.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_custom_array_simple.yaml) configuration.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_simple")
pprint(config)
```

The below figure demonstrates the meaning of the straight-line distance between two points.

```{code-cell} ipython3
array = CustomArraySystemDesign(config)
array.run()
array.plot_array_system(show=True)
```

Here the cable length and bury speed are still set to 0 to indicate that they are unknown, which
will tell the installation phase to use either ORBIT's defaults or the vessel's settings. Notice
that the latitude and longitude here are WGS-84 decimal coordinates.

```{code-cell} ipython3
array.location_data
```

For later comparison, we'll show the cabling costs for the straight-line cabling assumption.

```{code-cell} ipython3
print(f"{'Cable Type':<16}|  {'Cost in USD':>15}")
for cable, cost in array.cost_by_type.items():
    print(f"{cable:<16}| ${cost:>15,.2f}")

print(f"{'Total':<16}| ${array.total_cable_cost:>15,.2f}")
```

(case_3)=
## Case 3: Distance-based coordinate system

In this case, we will consider each turbine and substation on a distance-based coordinate system
where the longitude and latitude are the longitudinal (x direction) and latitudinal (y direction)
**distances**, in kilometers, from a common reference point. We are still using the Dudgeon data,
but the distances were computed outside of this example and the details are not be included.

:::{important}
For distance-based coordinate systems, all points should be be positive, meaning the reference point
should either be both west and south of the farm itself, or at the west-most and south-most point.
:::

Below, we can see that the input file
[`library/cables/dudgeon_distance_based.csv`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/dudgeon_distance_based.csv)
is still encoded in the exact same manner as [Case 2](#case_2), but latitude and longitude are
relative distances and not proper coordinates.

```{code-cell} ipython3
df = pd.read_csv(library_path / "cables/dudgeon_distance_based.csv", index_col=False).fillna("")
df
```

Using the distance-based location data requires us to set `distance` to True in the
`array_system_design` section of the configuration. This change is shown below in the
[`library/cables/example_custom_array_simple_distance_based.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_custom_array_simple_distance_based.yaml) configuration.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_simple_distance_based")
pprint(config)
```

Alternatively, we can set the `distance=True` when calling the `CustomArraySystemDesign`, however
the configuration dictionary's setting will override this input to allow for project-level
configurations to run as expected. Below, we can see some of the cable lengths differ slightly due
to the methodology of converting the WGS-84coordinates to relative points, however the spacing is
maintained, and we can see that this is still the Dudgeon windfarm.

```{code-cell} ipython3
array_distance = CustomArraySystemDesign(config, distance=True)
array_distance.run()
array_distance.plot_array_system(show=True)
```

Overall, the cabling cost is highly similar, with the difference being attributed to the method
to convert the WGS-84 coordiantes to relative coordinates.

```{code-cell} ipython3
print(f"{'Cable Type':<16} | {'Cost in USD (lat,lon)':>20} | {'Cost in USD (dist_lat,dist_lon)':>15}")
for (cable1, cost1), (cable2, cost2) in zip(array.cost_by_type.items(), array_distance.cost_by_type.items()):
    print(f"{cable1:<16} | ${cost1:>20,.2f} | ${cost2:>15,.2f}")

print(f"{'Total':<16} | ${array.total_cable_cost:>20,.2f} | ${array_distance.total_cable_cost:>15,.2f}")
```

(case_4)=
## Case 4: Site-Wide Cable Length Modifications

To account for exclusion zones from rocky soil or other seabed conditions, we use the
`average_exclusion_percent` input in the `array_system_design` configuration section. This exclusion
will be applied to all cable sections, so it's important to account for this when modeling
additional cable lengths.

In the
[`library/cables/example_custom_array_exclusions.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_custom_array_exclusions.yaml)
configuration, a 4.8% exclusion is applied to the entire farm. When plotting farms with exclusion
zones, they will not be shown since we are not mapping the true cable path, simply the connections
between turbines. In this case, we can also a modest increase in cabling costs resulting from the
additional cable required to account for the exclusion zones.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_exclusions")
pprint(config)

array_exclusion = CustomArraySystemDesign(config)
array_exclusion.run()
```

```{code-cell} ipython3
print(f"{'Cable Type':<16}|  {'Cost in USD':>15}")
for cable, cost in array_exclusion.cost_by_type.items():
    print(f"{cable:<16}| ${cost:>15,.2f}")

print(f"{'Total':<16}| ${array_exclusion.total_cable_cost:>15,.2f}")
```

(case_5)=
## Case 5: Custom Cable Lengths

If we look at the map in the
[Call to Mariners](http://dudgeonoffshorewind.co.uk/news/notices/Dudgeon%20-%20Notice%20to%20Mariners%20wk25.pdf)
there are different sized exclusions in the cables, so for this example we'll change the distances
from [Case 4](#case_4) to have more variation by using the `cable_length` column of the
`location_data` CSV. In addition, we will utilize the `bury_speed` column to demonstrate how these
columns will be used. Please note this work was performed outside the example, and we will only
show the resulting configurations.

For this example, half of the windfarm will have different soil condition, so we will use our proxy:
`bury_speed` by modifying the burial speed to be fast (0.5 km/h) and slow (0.05 km/hr),
respectively, to account for sandy soil and rocky soil. The purpose of this is for passing through
customized parameters in the design phase to be utilized in the installation phase as will be seen
in the final two examples.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_custom")
pprint(config)

array_custom = CustomArraySystemDesign(config)
array_custom.run()
```

Note that there are now cable lengths defined as well as burial speeds for the installation phase.

```{code-cell} ipython3
array_custom.location_data
```

Once again, the cabling costs have increased.

```{code-cell} ipython3
print(f"{'Cable Type':<16}|  {'Cost in USD':>15}")
for cable, cost in array_custom.cost_by_type.items():
    print(f"{cable:<16}| ${cost:>15,.2f}")

print(f"{'Total':<16}| ${array_custom.total_cable_cost:>15,.2f}")
```

(running)=
## Incorporating Custom Array Designs Into `ProjectManager`

Using cases 2, 3, 4, and 5 we will demonstrate the project-wide effects from differing cabling layouts.

### Setting Up The Cases

Using the
[`library/cables/example_array_cable_install.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_array_cable_install.yaml)
configuration as a base configuration, we'll create a new configuration for each of the cases
using each case's `design_result` as the `array_system` values.

```{code-cell} ipython3
base_config = library.extract_library_specs("config", "example_array_cable_install")

array_case2 = deepcopy(base_config)
array_case2["array_system"] = array.design_result["array_system"]

array_case3 = deepcopy(base_config)
array_case3["array_system"] = array_distance.design_result["array_system"]

array_case4 = deepcopy(base_config)
array_case4["array_system"] = array_exclusion.design_result["array_system"]

array_case5 = deepcopy(base_config)
array_case5["array_system"] = array_custom.design_result["array_system"]

sim2 = ArrayCableInstallation(array_case2)
sim3 = ArrayCableInstallation(array_case3)
sim4 = ArrayCableInstallation(array_case4)
sim5 = ArrayCableInstallation(array_case5)
```

### Run And Inspect The Simulation Results

We can see that both the installation cost and the time required to complete the installations have
all increased here, corresponding to the increased cable lengths and changes to the burial speeds
defined above.

```{code-cell} ipython3
names = ("straight-line distance", "distance-based coordinates", "with exclusions", "custom")
simulations = (sim2, sim3, sim4, sim5)

print(f"{'Simulation':<26} | {'Cost (in USD)':>14} | {'Time (in hours)':>16}")
for name, simulation in zip(names, simulations):
    simulation.run()
    cost = simulation.installation_capex
    time = simulation.total_phase_time
    print(f"{name:<26} | ${cost:>13,.2f} | {time:>16,.0f}")
```

(project_manager)=
### Incorporating Case 5 Into `ProjectManager`

We will now incorporate the desgin settings from [Case 5](#case_5) to demonstrate incorporation
of the custom array design tooling into `ProjectManager`. This example will use the
[`library/cables/example_custom_array_project_manager.yaml`](https://github.com/NLRWindSystems/ORBIT/tree/main/library/cables/example_custom_array_project_manager.yaml)
configuration.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_project_manager")
config["array_system_design"]["location_data"] = library.extract_library_specs(
    "cables", config["array_system_design"]["location_data"], file_type="csv"
)
config
```

Below, we can see that the results coming from the `ProjectManager` are the same as the additive
results of running each phase separately.

```{code-cell} ipython3
project = ProjectManager(config)
project.run()

total = array_custom.total_cable_cost + sim5.installation_capex
print(f"Custom Design        | ${array_custom.total_cable_cost:>13,.2f}")
print(f"Custom Installation  | ${sim5.installation_capex:>13,.2f}")
print(f"Total Custom Cost    | ${total:>13,.2f}")
print(f"Project Manager Cost | ${project.bos_capex:>13,.2f}")
```
