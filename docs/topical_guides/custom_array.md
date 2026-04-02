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
## Case 3: Distance-based "coordinate" system

In this case, we will consider each turbine and substation on a distance-based "coordinate" system where the longitude and latitude are the longitudinal (x direction) and latitudinal (y direction) **distances**, in kilometers, from a common reference point. We are still using the Dudgeon data, but the distances were computed outside of this example and the details are not be included.

Below, we can see that the input file is still encoded in the exact same manner as [Case 2](#case_2), but latitude and longitude are relative distances and not proper coordinates.

```{code-cell} ipython3
df = pd.read_csv("../library/cables/dudgeon_distance_based.csv", index_col=False).fillna("")
df
```

#### For this case we also add the `distance` argument to the `array_system_design` and set it to `True` to indicate we are dealing with distances.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_simple_distance_based")
pprint(config)
```

#### OR we can create the flag in the function call.

**Note:** the configuration dictionary will always override this setting.

```{code-cell} ipython3
array_distance = CustomArraySystemDesign(config, distance=True)
array_distance.run()
```

#### Let's take a look at the data to see what it output

While some of the cable lengths may be slightly different, the spacing is still maintained, and we can see that this is the Dudgeon windfarm.

```{code-cell} ipython3
array_distance.plot_array_system(show=True)
```

#### Now let's look at the cost for this cabling setup by each type of cable as well as the total cost and compare it to the previous case

While there is a minor difference, this difference is small in comparison to the total project cost and errs in a more conservative direction.

```{code-cell} ipython3
print(f"{'Cable Type':<16} | {'Cost in USD (lat,lon)':>20} | {'Cost in USD (dist_lat,dist_lon)':>15}")
for (cable1, cost1), (cable2, cost2) in zip(array.cost_by_type.items(), array_distance.cost_by_type.items()):
    print(f"{cable1:<16} | ${cost1:>20,.2f} | ${cost2:>15,.2f}")

print(f"{'Total':<16} | ${array.total_cable_cost:>20,.2f} | ${array_distance.total_cable_cost:>15,.2f}")
```

```{code-cell} ipython3

```

(case_4)=
## Case 4: We want to account for some additions to the cable lengths due to exclusion zones

This can be done with the `"average_exclusion_percent"` keyword in the configuration that can be seen below.

**Note:**
 1. There is an average  exclusion and is applied to each of the cable sections
 2. The plot won't change because it will not have details on the new paths so we'll only demonstrate the cost changes (a 4.8% increase, which is in line with the exclusion and the accounting for the site depth.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_exclusions")
config
```

```{code-cell} ipython3
array_exclusion = CustomArraySystemDesign(config)
array_exclusion.run()
```

```{code-cell} ipython3
print(f"{'Cable Type':<16}|  {'Cost in USD':>15}")
for cable, cost in array_exclusion.cost_by_type.items():
    print(f"{cable:<16}| ${cost:>15,.2f}")

print(f"{'Total':<16}| ${array_exclusion.total_cable_cost:>15,.2f}")
```

```{code-cell} ipython3

```

(case_5)=
## Case 5: Customize the distances

If we look at the map in the [Call to Mariners](http://dudgeonoffshorewind.co.uk/news/notices/Dudgeon%20-%20Notice%20to%20Mariners%20wk25.pdf) there are different sized exclusions in the cables, so for this example we'll change the distances from [Case 4](#case_4) where we used an average exclusion to be a bit different in each case by using the `cable_length` column. In addition, we will utilize the `bury_speed` column to demonstrate how these columns will be used.

**Note:** this work was done outside the notebook, but can be uploaded as show in the example below.

For this example, half of the windfarm will have different soil condition, so we will use our proxy: `bury_speed` by modifying the burial speed to be fast (0.5 km/h) and slow (0.05 km/hr), respectively, to account for sandy soil and rocky soil. The purpose of this is for passing through customized parameters in the design phase to be utilized in the installation phase as will be seen in the final two examples.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_custom")

# Note location_data the same one that was saved because I updated it!
config
```

```{code-cell} ipython3
array_custom = CustomArraySystemDesign(config)
array_custom.run()
```

#### Note that there are now cable lengths defined as well as burial speeds for installation

```{code-cell} ipython3
array_custom.location_data
```

#### See also that the costs have increased again!

```{code-cell} ipython3
print(f"{'Cable Type':<16}|  {'Cost in USD':>15}")
for cable, cost in array_custom.cost_by_type.items():
    print(f"{cable:<16}| ${cost:>15,.2f}")

print(f"{'Total':<16}| ${array_custom.total_cable_cost:>15,.2f}")
```

```{code-cell} ipython3

```

(running)=
# Let's run some simulations!
We can now compare cases 2-4 to see how the installation cost will vary.

+++

#### First, we have to create a configuration dictionary for each of the 3 main cases we'll be simulating for installations, corresponding to the configuration file from the tests library. Then, we'll update eeach with the `design_result` of each of the 3 cases that we defined above.

```{code-cell} ipython3
base_config = library.extract_library_specs("config", "example_array_cable_install")

#Case 2
array_case2 = deepcopy(base_config)
array_case2["array_system"] = array.design_result["array_system"]

# Case 3
array_case3 = deepcopy(base_config)
array_case3["array_system"] = array_distance.design_result["array_system"]

# Case 4
array_case4 = deepcopy(base_config)
array_case4["array_system"] = array_exclusion.design_result["array_system"]

# Case 5
array_case5 = deepcopy(base_config)
array_case5["array_system"] = array_custom.design_result["array_system"]
```

#### Instantiate the simulations

```{code-cell} ipython3
sim2 = ArrayCableInstallation(array_case2)
sim3 = ArrayCableInstallation(array_case3)
sim4 = ArrayCableInstallation(array_case4)
sim5 = ArrayCableInstallation(array_case5)
```

#### Run the simulations

We can see that both the installation cost and the time required to complete the simulation have all increased here, which corresponds to the increased cable lengths and changes to the burial speeds defined above.

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

```{code-cell} ipython3

```

(project_manager)=
## Let's put this all together and load with a data frame

### Using `ProjectManager` we will run Case 4 from design to installation.

We'll see here at the end that we end up with the same results running a custom array cabling project piecemeal and as a whole.

```{code-cell} ipython3
config = library.extract_library_specs("config", "example_custom_array_project_manager")
config["array_system_design"]["location_data"] = library.extract_library_specs(
    "cables", config["array_system_design"]["location_data"], file_type="csv"
)
config
```

```{code-cell} ipython3
project = ProjectManager(config)
project.run()
```

```{code-cell} ipython3
total = array_custom.total_cable_cost + sim5.installation_capex

print(f"Custom Design        | ${array_custom.total_cable_cost:>13,.2f}")
print(f"Custom Installation  | ${sim5.installation_capex:>13,.2f}")
print(f"Total Cost.          | ${total:>13,.2f}")
print(f"Project Manager Cost | ${project.bos_capex:>13,.2f}")
```
