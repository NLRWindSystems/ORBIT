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

# Apply thousands separators and no decimals to floats
pd.options.display.float_format = '{:,.0f}'.format

# Ensure the correct examples directory is used when running this in docs or in examples
here = Path(".").resolve()
example_dir = here.parents[1] / "examples" if here.stem == "tutorials" else here / "examples"

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

### Event Timing

The `installation_time` provides the sum total installation time of all phases, in hours, without
accounting for timing overlaps, whereas the `project_days` provides the total number of days between
the start and completion of the project. Similar to `project_days`, `project_time` provides the total
elapsed simulation time, accounting for overlapping installation phases.

```{code-cell} ipython3
print(f"Total Installation Time: {project.installation_time / 24:.0f} days")
print(f"Total Elapsed Time: {project.project_days} days")
print(f"Total Elapsed Time: {project.project_time:,.0f} hours")
```

## All Outputs At Once

The `outputs`  method provides a dictionary mapping all the major project costs and timing details
in a single view. There are two parameters that can be passed to provide further details that will
not be demonstrated. For further details on any of these metrics, please refer to that metric's
section.

- `include_logs`: include the full project installation action logs if `True`.
- `npv_details`: include the `cash_flow`, `monthly_revenue`, and `monthly_expenses`, if `True`.

```{code-cell} ipython3
pprint(project.outputs())
```

## CapEx

This section will start from the total CapEx, and work backwards demonstrating how to access
the various CapEx breakouts and breakdowns.

### Total CapEx

The `total_capex` is the sum of the BOS, soft, and project CapEx numbers (details in following
sections). This represents the complete project costs including all upfront costs, financing,
procurement and installation of BOS subsystems and the procurement costs of the turbines.

:::{note}
ORBIT doesn't explicity model the procurement of turbines, however the Turbine CapEx is included
within `project.total_capex`. To configure the cost of the turbines, `turbine_capex` can be passed
into the `project_parameters` section of an ORBIT configuration.
:::

```{code-cell} ipython3
print(f"Total CapEx (millions, USD): {project.total_capex / 1e6:,.2f}")
print(f"Total CapEx (USD) per kW: {project.total_capex_per_kw:,.2f}")
```

### Categorical CapEx Breakdowns

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

### BOS CapEx

The balance-of-system (BOS) CapEx (`bos_capex`) is the sum of the system and installation CapEx,
and is one of the core outputs of the ORBIT module.

```{code-cell} ipython3
print(f"BOS CapEx (millions, USD): {project.bos_capex / 1e6:,.2f}")
print(f"BOS CapEx (USD) per kW: {project.bos_capex_per_kw:,.2f}")
```

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

### Turbine CapEx

The `turbine_capex` is directly derived from the user inputs, and if none are provided, it is
assumed to be $1,300 USD/kW.

```{code-cell} ipython3
print(f"Turbine CapEx (millions, USD): {project.turbine_capex / 1e6:,.2f}")
print(f"Turbine CapEx (USD) per kW: {project.turbine_capex_per_kw:,.2f}")
```

### Project CapEx

Project CapEx (`project.project_capex`) includes the costs associated with
the lease area, the development of the construction operations plan and any
environmental review and other upfront project costs. There are default values
for all of these subcategories, however the values can also be overridden in the
`project_parameters` subdict.

```{code-cell} ipython3
print(f"Turbine CapEx (millions, USD): {project.project_capex / 1e6:,.2f}")
print(f"Turbine CapEx (USD) per kW: {project.project_capex_per_kw:,.2f}")
```

### Soft CapEx

Soft CapEx (`project.soft_capex`) represents additional project level costs
associated with commissioning, decommissioning and financing of the project.
The cost factors can be input in the `project_parameters` subdict of an ORBIT
configuration. The default cost factors for these categories are derived from the
[2018 Cost of Wind Energy Review](https://www.nlr.gov/docs/fy20osti/74598.pdf).

```{code-cell} ipython3
print(f"Soft CapEx (millions, USD): {project.soft_capex / 1e6:,.2f}")
print(f"Soft CapEx (USD) per kW: {project.soft_capex_per_kw:,.2f}")
```

The soft CapEx can also be broken down using both the `soft_capex_breakdown` and the `capex_detailed_soft_capex_breakdown`, which also provide a capacity-noramlized variation by adding
`_per_kw` to the end of either (not shown in this demonstration). The primary difference (as shown
below) is that the `capex_detailed_soft_capex_breakdown` metric provides the capex breakdown with
the additional soft capex breakdown.

```{code-cell} ipython3
for name, capex in project.soft_capex_breakdown.items():
    print(f"{name:>35}: ${capex / 1e6:8,.2f} (millions,USD)")
```

```{code-cell} ipython3
for name, capex in project.capex_detailed_soft_capex_breakdown.items():
    print(f"{name:>35}: ${capex / 1e6:8,.2f} (millions,USD)")
```

The soft CapEx values are also available as independent values:

- `construction_insurance_capex`
- `commissioning_capex`
- `decommissioning_capex`
- `procurement_contingency_capex`
- `installation_contingency_capex`
- `construction_financing_capex`

```{code-cell} ipython3
print(f"Construction Insurance CapEx (millions, USD): {project.construction_insurance_capex() / 1e6:,.2f}")
print(f"Commissioning CapEx (millions, USD): {project.commissioning_capex() / 1e6:,.2f}")
print(f"Decommissioning CapEx (millions, USD): {project.decommissioning_capex() / 1e6:,.2f}")
print(f"Procurement Contingency CapEx (millions, USD): {project.procurement_contingency_capex() / 1e6:,.2f}")
print(f"Installation Contingency CapEx (millions, USD): {project.installation_contingency_capex() / 1e6:,.2f}")
print(f"Construction Financing CapEx (millions, USD): {project.construction_financing_capex() / 1e6:,.2f}")
```
### All Other CapEx Categories

#### Supply Chain CapEx

The supply chain CapEx (`supply_chain_capex`) directly captures the user-provided
`supply_chain_capex` from the `project_parameters` section of the project configuration. This
value should encompass any project-level investements in supply chain development, port upgrade,
community benefit agreements, fisheries mitigation funds, community or research initiatives, and
US-built vessels.

```{code-cell} ipython3
print(f"Supply Chain CapEx (millions, USD): {project.supply_chain_capex / 1e6:,.2f}")
print(f"Supply Chain CapEx (USD) per kW: {project.supply_chain_capex_per_kw:,.2f}")
```

#### Onshore Substation CapEx

The CapEx associated with onshore substation as prescribed by the `ElectricalDesign`

```{code-cell} ipython3
print(f"Turbine CapEx (millions, USD): {project.turbine_capex / 1e6:,.2f}")
print(f"Turbine CapEx (USD) per kW: {project.turbine_capex_per_kw:,.2f}")
```

#### Overnight CapEx

The `overnight_capex` provides the overnight capital cost (system and turbine CapEx) of the project.

```{code-cell} ipython3
print(f"Overnight CapEx (millions, USD): {project.overnight_capex / 1e6:,.2f}")
```

## Logging

The installation logs can produced in varying details from high-level phase start and end dates, and
all the way down to the detailed installation logics. This section will go through the methods
provided to access these data and demonstrate some simple ways of displaying it conveniently.

### Installation Progress

The `progress_summary` provides an aggregated view of the `progress_logs` to show the number
of completed component installations for each month in the simulation.

```{code-cell} ipython3
pprint(project.progress_summary)
```

The `project_logs` provides a list of the when a component installation was completed using the
total number of hours since the start of the simulation.

As an example, this looks like the following:

```python
[
    ('Offshore Substation', 88.0925357142857),
    ('Turbine', 97.7933333333333),
    ('Substructure', 130.14586018219498),
    ('Substructure', 147.89172036438998),
    ('Turbine', 150.18666666666658),
    ...
]
```

### Phase timing

The `phase_dates` provides access to the starting and ending time of each installation phase as
a dictionary. In the following example, we will convert this data into a Pandas DataFrame with
datetime formatting, and produce a Gantt chart to highlight where the phases occur relative to
each other.

```{code-cell} ipython3
df = pd.DataFrame.from_dict(project.phase_dates).T
df.start = pd.to_datetime(df.start)
df.end = pd.to_datetime(df.end)
df = df.sort_values("start", ascending=False)
df
```

Below, we can see the installation timing is not quite realistic given the WTIV is used for the
monopile, turbine, and OSS installations and the cabling vessel is used for both the array and
export cabling installations. For both vessels, there should not be overlapping installations
unless multiple vessels are made available for these actions.

```{code-cell} ipython3
fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot(111)

ax.barh(y=df.index, width=df.end - df.start, left=df.start);

annotation = (
    f"Total Installation Time: {project.installation_time / 24:.0f} days\n"
    f"Total Elapsed Time: {project.project_days} days"
)
ax.text(
    pd.to_datetime("2010-05-06"), 3, annotation,
    bbox={"boxstyle": "square", "fc": (0.9, 0.9, 0.9, 0.9), "linewidth": 0.5},
    ha="left", va="center", size=12,
)

ax.grid(axis="x")
ax.set_axisbelow(True)
ax.set_xlim(pd.to_datetime("2009-12"), pd.to_datetime("2010-10"))
fig.tight_layout()
```

### Detailed Event Timing

The `actions` property provides access to a JSON-style list of every step taken during the
installation simulation. It is highly recommended to convert this to a Pandas DataFrame or similar
for inspection. Below, we will walk through some basic filtering of these data.

```{code-cell} ipython3
df = pd.DataFrame(project.actions)
df.head()
```

Using the data frame we can filter produce vessel timing summaries for a single phase or a single
vessel, or any combination of vessels and phases. Below is a demonstration of filtering the time
spent in various activities during the monopile installation. From an operational standpoint, this
provides insight into what actions take the longest or cost the most, and can provide a means to
identify room for innovation or process efficiencies. Please see the
[project manager phase timing tutorial](#phase-dependent-timing) for more information about
customizing timing dependencies.

```{code-cell} ipython3
mp_install = df.loc[df.phase.eq("MonopileInstallation")]
mp_vessel_summary = (
    mp_install[["agent", "action", "duration", "cost"]]
    .groupby(["agent", "action"])
    .sum()
)
mp_vessel_summary
```

## Cash Flow and Net Present Value

The `ProjectManager` includes a basic cash flow and net present value (NPV) model. The project must
have the array, export, and substation installation models configured for this model to be
applicable. The model will find the point in the project logs where the substation and export
cable installations were completed and where each completed string of array cables was installed.
When all three of these conditions are met, the project can begin to generate energy and produce
revenue. The revenue generation is then superimposed on the monthly spend of the installation
models for the `project.cash_flow`. Please note this assumes a fixed operational expenditure (OpEx).

The NPV of the project can then be calculated and is available through `npv`. The underlying
financial assumptions for this model are also contained within the `project_parameters` section of
the ORBIT configuration.

```{code-cell} ipython3
print(f"NPV: ${project.npv / 1e6:,.2f} (millions, USD)")
```

Below, we highlight the first 12 months of the project cash flow. In the 10th month we can see that
there are no more installation costs, and the project produces the same values for each field
until the end of the project.

```{code-cell} ipython3
pd.concat(
    [
        pd.DataFrame(project.monthly_opex.values(), columns=["monthly_opex"]),
        pd.DataFrame(project.monthly_expenses.values(), columns=["monthly_expenses"]),
        pd.DataFrame(project.monthly_revenue.values(), columns=["monthly_revenue"]),
        pd.DataFrame(project.cash_flow.values(), columns=["cash_flow"]),
    ],
    axis=1
).head(12)
```
