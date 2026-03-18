# ORBIT

## Overview

The Offshore Renewables Balance of system and Installation Tool (ORBIT) is a
model developed by the National Laboratory of the Rockies (NLR) to study
the cost and times associated with Offshore Wind Balance of System (BOS)
processes.

ORBIT includes many different modules that can be used to model phases within
the BOS process, split into {ref}`design <design-phases>` and
{ref}`installation <install-phases>`. It is highly flexible and allows the user
to define which phases are needed to model their project or scenario using
{ref}`ProjectManager <project-manager-api>` for a single analysis, or the
[`ParametricManager`](#parametric-manager-api) for a parameter sweep of
analysis setttings.

ORBIT is written in Python 3.10 and utilizes
[SimPy](https://simpy.readthedocs.io/en/latest/)'s discrete event simulation
framework to model individual processes during the installation phases,
allowing for the effects of weather delays and vessel interactions to be
studied.

## License

Apache 2.0. Please see the
[repository](https://github.com/NLRWindSystems/ORBIT/blob/main/LICENSE)
for license information.
