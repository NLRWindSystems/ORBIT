---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(design-phase-tutorial)=
# Design Modules

There are two types of modules within ORBIT, design and installation.
Installation modules require a number of inputs, setup a simulation and
model the installation of offshore wind components. Alternatively, design
modules model the design of an offshore wind components and can produce inputs.
Within the context of `ProjectManager`, a design module can remove inputs from
the required configuration for a project. The following example will illustrate
this feature and how it is used within `ProjectManager`.

:::{warning}
Design phase modules in ORBIT are intended to capture broad scaling trends
for offshore wind components and do not represent the required fidelity of a
full engineering design.
:::

## Example

Consider a simple project with one monopile installation phase:

```{code-cell} ipython3
from pprint import pprint

from ORBIT import ProjectManager

phases = [
    "MonopileInstallation",  # Monopile installation with one vessel
]

required_config = ProjectManager.compile_input_dict(phases)
pprint(required_config)
```

Above, there are many optional. inputs for the project parameterization, however, we have a
`monopile`, `transition_piece`, `turbine`, `plant`, and `site` that have required inputs, as highlighted
below.

```{code-cell} ipython3
keys = ("monopile", "turbine", "transition_piece", "site", "plant")
callouts = {k: v for k, v in required_config.items() if k in keys}
pprint(callouts)
```

In the required configuration for the above project, the user must fill in a
`'monopile'` sub dictionary. Alternatively, a `MonopileDesign` phase could
be included in the phase list. This additional phase would effectively fill in
the `'monopile'` sub dictionary for the user:

Note the additional inputs from `MonopileDesign` in the `turbine` dictionary. Similarly,
the `monopile` dictionary is no longer required as the design phase will create those outputs
from the provided design parameters.

```{code-cell} ipython3
phases = [
    "MonopileDesign",  # Basic monopile sizing based on turbine size and site
    "MonopileInstallation",  # Monopile installation with one vessel
]

required_config = ProjectManager.compile_input_dict(phases)
pprint(required_config)
```

Note the additional `monopile_design` parameters (all are optional) that can be configured, if
choosing to deviate from the models' defaults. Please see the
[monopile design methodology](#monopile-design-methods) for further details. Below we can see
these design parameters and changes to our other requirements highlighted in the configuration
subset.

```{code-cell} ipython3
keys = ("monopile_design", "turbine", "transition_piece", "site", "plant")
callouts = {k: v for k, v in required_config.items() if k in keys}
pprint(callouts)
```

## Overriding Values from a Design Phase

In the example above, the `MonopileDesign` phase will produce the input
parameters `'monopile'` and `'transition_piece'`. It is also possible to
supply some of the values for these designs if known and let `MonopileDesign`
fill in the rest. For example, if the user knows the dimensions of the monopile
but not the transition piece, the `'monopile'` dictionary can be added to the
project config above:

```{code-cell} ipython3
config = {
    'site': {
        'depth': 50,
        'mean_windspeed': 9,
        'distance': 30,
    },
    'plant': {
        'num_turbines': 100,
    },
    'wtiv': 'example_wtiv',     # model provided jackup vessel
    'turbine': {
        'hub_height': 130,
        'rotor_diameter': 154,  # <-- Additional input from MonopileDesign
        'rated_windspeed': 11
    },
    'monopile': {               # <-- 'monopile' isn't required but can be
        'type': 'Monopile',     #     added to include known project parameters.
        'mass': 800,            #     Other inputs produced by MonopileDesign will
        'length': 100           #     be added to the config.
    },
    'monopile_design': {},
    'design_phases': ['MonopileDesign'],
    'install_phases': ['MonopileInstallation'],
}

project = ProjectManager(config)
project.run()

print(project.config.dump())
```
