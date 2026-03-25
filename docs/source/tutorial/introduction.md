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

(intro-tutorial)=
# ORBIT Introduction

ORBIT's CapEx modeling is comprised of the both design and installation models for a variety of
offshore wind turbine subsystems. As such, the model's core functionality are split into the
`design` and `install` model classes. The design classes are intended to model the sizing and cost
of offshore wind components and the installation modules simulate the installation of these
subcomponents in a discrete event simulation framework. This tutorial will walk through the basics
of modeling the design and then installation of the monopile, leading to the introduction of the
`ProjectManger` to orchestrate the design and installation of multiple turbine subsystems.

To get started, we first import the required imports that will be used in this demonstration.

```{code-cell} ipython3
from pathlib import Path
from copy import deepcopy
from pprint import pprint

from ORBIT import ProjectManager, load_config, save_config
from ORBIT.phases.design import MonopileDesign, design_phases
from ORBIT.phases.install import MonopileInstallation, install_phases
```

While this introduction will focus on the monopile design and installation to highlight working with
ORBIT, it should be noted that there are both fixed and floating substructure models. Below is an
easy way to check what models are available in ORBIT.

```{code-cell} ipython3
pprint(design_phases)
```

```{code-cell} ipython3
pprint(install_phases)
```

## Configuration Basics

Each model has a property `expected_config` that provides basic information about the required and
optional inputs for the model. Notice that for each input there is a provided data type, an
indication if the parameter is optional, and any nested dictionary configurations are fully mapped
in the same way as individal parameters. Below, we can see the expected configurations for both
the monopile design and installation classes. It should be noted that when combining complimentary
design and installation phases for a component, that the design model will provide most of the
installation inputs as a `design_result` (more details in the `ProjectManager` introduction).

```{code-cell} ipython3
pprint(MonopileDesign.expected_config)
```

```{code-cell} ipython3
pprint(MonopileInstallation.expected_config)
```

### Design Models

Design phase modules in ORBIT are intended to capture broad scaling trends for offshore wind
components and do not represent the required fidelity of a full engineering design. Please see NLR's
[WISDEM](https://github.com/NLRWindSystems/WISDEM/) if a higher fidelity turbine design model
is required.

For the sake of illustration we will provide only the required inputs, as shown below.

```{code-cell} ipython3
# Filling out the config for a simple fixed bottom project:
design_config = {
    "site": {
        "depth": 25,
        "mean_windspeed": 9.5,
    },
    "plant": {
        "num_turbines": 50,
    },
    "turbine": {
        "rotor_diameter": 220,
        "hub_height": 120,
        "rated_windspeed": 13,
    }
}
```

Similar to `expected_config`, every design and installation model contains a `run` method that runs
the design or installation simulation logic.

```{code-cell} ipython3
monopile_design = MonopileDesign(design_config)
monopile_design.run()
print(f"Total Substructure Cost: ${monopile_design.total_cost / 1e6:,.1f} M")
pprint(monopile_design.design_result)
```

### Incomplete or Incorrect Configurations

If a required input is missing, an error message will be raised with the input and it's location
within the configuration. This error message used dot-notation to show the structure of the
dictionary. Each "." represents a lower level in the dictionary such that `site.depth` means the "site" subdictionary is missing the "depth" key, value pair.

In the example below, the `site` inputs have been removed. The following inputs will be missing:
`["site.depth", "site.mean_windspeed"]`

```{code-cell} ipython3
:tags: [raises-exception]

config_error = deepcopy(design_config)
_ = config_error.pop("site")

failed_monopile_design = MonopileDesign(config_error)
```

### Optional Inputs

Optional inputs can be provided as they are available or desired in place of ORBIT's
defaults. In general ORBIT's default values are updated on annual basis to align with
the last complete year of inflationary data and commodity price indices. These values
also align with the annual [NLR Cost of Wind Energy Review](https://github.com/NatLabRockies/AnnualReportingWind/).

```{code-cell} ipython3
design_config = {
    "site": {
        "depth": 25,
        "mean_windspeed": 9.5,
    },
    "plant": {
        "num_turbines": 50,
    },
    "turbine": {
        "rotor_diameter": 220,
        "hub_height": 120,
        "rated_windspeed": 13,
    },

    # Overriding of the design cost defaults, both in $USD/tonne
    "monopile_design": {
        "monopile_steel_cost": 3500,
         "tp_steel_cost": 4500,
    }
}

monopile_design = MonopileDesign(design_config)
monopile_design.run()
print(f"Total Substructure Cost: ${monopile_design.total_cost / 1e6:,.2f} M")
pprint(monopile_design.design_result)
```

### Overriding Values from the Design Phase

In the example above, the `MonopileDesign` phase will produce the input parameters "monopile and
"transition_piece". It is also possible to supply some of the values for these designs if they are
known, and let `MonopileDesign` fill in the rest. For example, if the user knows the dimensions of
the monopile but not the transition piece, the "monopile" dictionary can be added to the project config above:

```{code-cell} ipython3
design_config_custom = {
    "site": {
        "depth": 25,
        "mean_windspeed": 9.5,
    },
    "plant": {
        "num_turbines": 50,
    },
    "turbine": {
        "rotor_diameter": 220,
        "hub_height": 120,
        "rated_windspeed": 13,
    },
    "monopile": {
        "type": "Monopile",
        "mass": 800,
        "length": 100,
    },
}

monopile_design = MonopileDesign(design_config_custom)
monopile_design.run()
monopile_design_result = monopile_design.design_result
pprint(monopile_design_result)
```

### Installation Phases

ORBIT's installation phases tend to require more inputs and provide implicit pathways to model
installation strategies. For instance, in the monopile installation, we can provide a "wtiv" vessel
for a single WTIV installation strategy or provide a "feeder" configuration with "num_feeders"
to model barges ferrying components to and from the site while a WTIV installs the turbines.
Additionally, supply chains and ports can be configured to model component availability and port
logistics.

Using the output from the above example, we can add further configurations. Note that ORBIT provides
a series of default vessls in `library/vessels/` to support all possible installation strategies.
For more details on vessel configurations, please see the [vessels tutorial](#vessels-tutorial).

```{code-cell} ipython3
install_config = deepcopy(monopile_design_result)
install_config["wtiv"] = "example_wtiv"
install_config["feeder"] = "example_feeder"
install_config["num_feeders"] = 2
install_config["site"] = design_config["site"] | {"distance": 70}
install_config["plant"] = design_config["plant"]
install_config["turbine"] = design_config["turbine"]

monopile_install = MonopileInstallation(install_config)
monopile_install.run()
print(f"Total Installation Cost: ${monopile_install.installation_capex / 1e6:,.2f} M")
print(monopile_install.config.dump())
```

### Loading and Saving Configurations

In addition to writing dictionaries in a script or Notebook file, ORBIT also provides the
`load_config` and `save_config` functions to load and save configurations for easier scenario
management. In the following example, we demonstrate a hypothetical workflow loading, updating, and
saving a new monopile design configuration.

```python
design_config = load_config("path/to/monopile_design.yaml")

...  # calculate additional properties of the monopile and update the configuration

save_config(design_config, "path/to/new_monopile_design.yaml")
```

Other use cases could be for creating input templates for project configurations, such
as those used by `ProjectManager` in the next section.

## Syncing Design and Installation with `ProjectManager`

`ProjectManager` is the primary system for interacting with ORBIT. It provides the ability to
configure and run one or multiple design and installation at a time, allowing the user to customize
ORBIT to fit the needs of a specific project. It also provides a helper method to detail what inputs
are required to run the desired configuration.

Continuing to work with just the monopile, we can provide a barebones configuration to set the
desired phases, and output the required inputs when running the design and installation phase in
unison. Notice that the "monopile" definition is no longer required for the installation as the
`design_result` will be automatically passed from the design phase to the installation phase.
There are now additional project parameters to supply development and other non-modeled fixed costs
the project will incur. Similar to the design and installation models, anything that is marked as
optional will have a default value within the model.

For more details on the `ProjectManager`, please see the [tutorial](#project-manager-tutorial).

```{code-cell} ipython3
phases = ["MonopileDesign", "MonopileInstallation"]
config_template = ProjectManager.compile_input_dict(phases)
pprint(config_template)
```

Now, we can combine the monopile design and installation configurations that were
used in the previous examples, and run the model to get a single CapEx alongsie the
high level category breakdown.

```{code-cell} ipython3
project_config = deepcopy(design_config)
project_config["wtiv"] = "example_wtiv"
project_config["feeder"] = "example_feeder"
project_config["num_feeders"] = 2
project_config["site"] = install_config["site"]
project_config["turbine"]["turbine_rating"] = 12
project_config["design_phases"] = ["MonopileDesign"]
project_config["install_phases"] = ["MonopileInstallation"]

project = ProjectManager(project_config)
project.run()
print(f"{"Project Capex":>30}: {project.bos_capex / 1e6:6,.2f} M")

for category, cost in project.capex_breakdown.items():
    print(f"{category:>30}: {cost / 1e6:6,.2f} M")
```

To continue with the previous subsection's demonstration, we can also save the final configuration
in one combined file, so the project could be reloaded and rerun in the future.

```{code-cell} ipython3
config_fn = Path("monopile_demo.yaml").resolve()
save_config(project.config, config_fn)

config = load_config(config_fn)
project = ProjectManager(config)
project.run()

print(f"{"Project Capex":>30}: {project.bos_capex / 1e6:6,.2f} M")
for category, cost in project.capex_breakdown.items():
    print(f"{category:>30}: {cost / 1e6:6,.2f} M")

config_fn.unlink()  # delete the demo file
```
