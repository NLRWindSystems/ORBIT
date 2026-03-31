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

(outputs-tutorial)=
# Available Outputs

Using `ProjectManager` to run a collection of ORBIT design and installation models representing a
partial or complete offshore wind project installation enables a variety of project-level metrics
to be calculated that are not available in individual models. The outputs of each model are also
made directly available by access to the model itself or in aggregate form for all project-level
outputs available via the `ProjectManager` API.

## Model Setup

Before diving in, we will import all the packages and functionality we'll need, and run a project
that can highlight the project's metrics.

```{code-cell} ipython3
from pathlib import Path
from pprint import pprint

import pandas as pd
import matplotlib.pyplot as plt

from ORBIT import ProjectManager, load_config

# Ensure the correct examples directory is used when running this in docs or in examples
here = Path(".").resolve()
example_dir = here.parents[1] / "examples" if here.stem == "tutorial" else here

config = load_config(example_dir / "configs/example_fixed_project.yaml")
project = ProjectManager(config)
project.run()
```

## Project Details

### Model Design Results

The `design_results` object is dictionary mapping between phase names and the dictionary of outputs
used by `ProjectManger` to pass into other phases or calculate further metrics.

```{code-cell} ipython3
pprint(project.design_results)
```

### Project Parameterizaions

Below is brief example showing the basic project parameterizations that are availabe.

- `num_turbines`: the number of turbines.
- `turbine_rating`: the rating of an individual turbine, in MW.
- `capacity`: The total project capacity, in MW.
- `project_time`: The total project installation time, including all delays, in hours.

```{code-cell} ipython3
print(f"Number of turbines: {project.num_turbines}")
print(f"Turbine Rating: {project.turbine_rating:.2f}")
print(f"Project Capacity (MW): {project.capacity:,.2f}")
print(f"Project Installation Time (days): {project.project_time / 24:,.1f}")
```

## All Outputs At Once

The `outputs`  method provides a dictionary mapping all the major project costs and timing details
in a single view. There are two parameters that can be passed to provide further details that will
not be demonstrated. For further details on any of these metrics, please refer to that metric's
section.

- `include_logs`: include the full project installation action logs if `True`.
- `npv_details`: include the `cash_flow`, `monthly_revenue`, and `monthly_expenses`, if `True`.

```{code-cell} ipython3
pprint(project.outputs)
```

## CapEx

The two main outputs of ORBIT are the system CapEx (the total cost of procuring the configured
subsystems) and the installation CapEx (the total cost of installing the subsystems). The following
sections will demonstrate these metrics and their breakdowns.

### System CapEx

The `system_capex` property provides the total procurement costs for all modeled systems, whether
the costs were user inputs, or the results of design models. This value will not change unless
the design or plant's properties (e.g., distance to shore, depth, or number of turbines) change.

In addition, `system_capex_per_kw` provies the capacity-normalized CapEx for the project.

```{code-cell} ipython3
print(f"System (procurement) CapEx (millions, USD): {project.system_capex / 1e6:,.2f}")
print(f"System (procurement) CapEx (USD) per kW: {project.system_capex_per_kw:,.2f}")
```

To view the individual component system costs, users can inspect the `system_costs` dictionary where
costs are summarized by each modeled or input system.

```{code-cell} ipython3
for name, capex in project.system_costs.items():
    print(f"{name:>35}: ${capex / 1e6:6,.2f} (millions, USD)")
```

### Installation Capex

Installation CapEx is a dynamic result based on the installation simulation and the timing
associated with each subsystem installation, day rates of any vessels/ports and any accrued weather
delays.

In addition, `installation_capex_per_kw` provies the capacity-normalized CapEx for the project.
Below we will print out the dictionary keys and the values in millions USD.

```{code-cell} ipython3
print(f"Installation CapEx (millions, USD): {project.installation_capex / 1e6:,.2f}")
print(f"Installation CapEx (USD) per kW: {project.installation_capex_per_kw:,.2f}")
```

To view the individual component installation costs, users can inspect the `installation_costs`
dictionary where costs are summarized by each modeled system. Below we will print out the dictionary
keys and the values in millions USD.

```{code-cell} ipython3
for name, capex in project.installation_costs.items():
    print(f"{name:>35}: ${capex / 1e6:6,.2f} (millions, USD)")
```

### Categorical CapEx

The `capex_breakdown` property provides a dictionary of all the procurement, installation, soft,
and project costs associated with a project. Below we will print out the dictionary keys and
the values in millions USD.

```{code-cell} ipython3
for name, capex in project.capex_breakdown.items():
    print(f"{name:>35}: ${capex / 1e6:6,.2f} (millions, USD)")
```

Like in the previous examples, the `capex_breakdown_per_kw` will provide each category's associated
costs as a capacity normalized value.

```{code-cell} ipython3
for name, capex in project.capex_breakdown_per_kw.items():
    print(f"{name:>35}: ${capex:8,.2f} (USD/kW)")
```

## BOS CapEx

The balance-of-system CapEx (available as `project.bos_capex`) is the sum of
the system and installation capex numbers and is one of the core outputs of the
ORBIT module.

## Soft CapEx

Soft CapEx (`project.soft_capex`) represents additional project level costs
associated with commissioning, decommissioning and financing of the project.
The cost factors can be input in the `project_parameters` subdict of an ORBIT
configuration. The default cost factors for these categories are derived from the
[2018 Cost of Wind Energy Review](https://www.nlr.gov/docs/fy20osti/74598.pdf).

## Project CapEx

Project CapEx (`project.project_capex`) includes the costs associated with
the lease area, the development of the construction operations plan and any
environmental review and other upfront project costs. There are default values
for all of these subcategories, however the values can also be overridden in the
`project_parameters` subdict.

## Total CapEx

Total CapEx (`project.total_capex`) is the sum of the BOS, Soft and Project
CapEx numbers. This represents complete project costs including all upfront
costs, financing, procurement and installation of BOS subsystems and the
procurement costs of the turbines.

:::{note}
ORBIT doesn't explicity model the procurement of turbines, however the
Turbine CapEx is included within `project.total_capex`. To configure the
cost of the turbines, `turbine_capex` can be passed into the
`project_parameters` subdict of an ORBIT config. The default is \$1300/kW.
:::

## Actions

A list of every step taken during the installation modules is available at
`project.actions`. The best way to view, sort and save these results is as
a pandas DataFrame. A few example use cases are presented below.

```python
import pandas as pd
df = pd.DataFrame(project.actions)

# Sort by a specific phase
df.loc[df["phase"]=="MonopileInstallation"]

# Group by vessel and action to see where each vessel spent the most time
df.groupby(["vessel", "action"]).sum()["duration"]

# Save results to 'csv'
df.to_csv("filename.csv")
```

## Logging

`progress_logs`
`progress_summary`
`actions`

`phase_dates`
`installation_time`
`project_days`


## Detailed Outputs

More detailed results from individual phases are available at
`project.detailed_outputs`.

## Cash Flow and Net Present Value

`ProjectManager` also includes a basic cash flow and net present value model.
The project must have the array system, export system and the substation
installation modules configured for this model to be applicable. The model will
find the point in the project logs where the substation and export system
installations were completed and where each array system string was installed.
When all three of these conditions are met, the project can begin to generate
energy and produce revenue. The revenue generation is then superimposed on the
monthly spend of the installation modules for the `project.cash_flow`.

The net present value of the project can then be calculated and is available at
`project.npv`. The underlying financial assumptions for this model are also
contained within the `project_parameters` subdict of the ORBIT configuration.

### Estimated Operational Costs

`monthly_opex`
`monthly_expenses`
`monthly_revenue`
`cash_flow`
`npv`
