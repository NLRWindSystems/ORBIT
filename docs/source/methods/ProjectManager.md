(project-manager-methods)=
# Project Manager

The following pages cover the methodology behind the project manager.

## Overview

The `ProjectManager` is the primary system for interacting with ORBIT to simulate
a wind project. Users can customize their project by specifying a a wide variety of
parameters as a dictionary (see the [`ProjectManager` tutorial](#project-manager-tutorial) for
further details). For more details of the code implementation, please see the
[`ProjectManager` API](#project-manager-api).

It instantiates a class aggregates project parameters, specifies a start date, and interprets a weather
profile, and it employs a collection of decorators, `methods`, and `classmethods` to run the simulation.
Among these methods are `design_phases` and `install_phases` that serve as components to the simulation.
Additionally, some methods search and catch key errors to avoid simulation issues, export progress logs,
and save the outputs.

## Run

This method checks to see if a design or install phase is instatiated prior to running them. Depending on
which design phases are specified, each phase is run in no particular order and the results are added to
`design_results` dictionary. Conversely, the install phases can be run sequentially or as overlapped
processes (see example: {doc}`Overlapping install <../examples>`). It is worth noting, that ORBIT
has built in logic to determine any dependency between install phases.

## Properties

The `@property` decorators allow the `ProjectManager` to access and manipulate the attributes of certain classes. Of the
several properties some important ones are:

.. toctree::
    :maxdepth: 2
    :caption: Contents:

- `capex_categories`: CapEx Categories
- `npv`: Net Present Value
- `turbine_capex`: CapEx of the Wind Turbine.
- `bos_capex`: BOS CapEx includes the System CapEx and Installation CapEx.
- `system_capex`: Total system procurement cost.
- `installation_capex`: Total installation cost.
- `project_capex`: Project Capex includes, site auction, site assessment, construction plan, and installation plan costs.
- `soft_capex_breakdown`: Soft CapEx Categories

Finally, these attributes are collected in an `output` dictionary.

## Class Methods

The `@classmethod` decorator allows the `ProjectManager` to access and modify class-level attributes.

- `register_design_phase`: Add a custom design phase to the `ProjectManager` class.
- `register_install_phase`: Add a custom install phase to the `ProjectManager` class.

## Soft CapEx Methodology

The methodology outlined in {cite:t}`beiter2016spatial` applies multipliers
(or assumed factors) to the magnitude of capital expenditure (CapEx)
components in order to derive the Soft CapEx components. The factors used are
consistent with those used in {cite:t}`cower2024`, enabling the soft costs to
scale in proportion to the other costs calculated within ORBIT. Soft Capex is
calculated using the default multipliers and parameters from {cite:t}`cower2024`.
Users can specify any of the :py:attr:`soft_capex_factors` below if they prefer to
override the default values. Additionally, users can assign $/kW values for
any calculated Soft CapEx component, ending with :math:`\_capex`, for
simplicity. The soft CapEx component's definitions and their calculations
are provided below.

### Construction Insurance

All risk property, delays in start-up, third party liability, and broker's fees. Unless otherwise
specified, a `construction_insurance_factor` of 0.0207 is applied to following calculation. See the
[{py:meth}`ProjectManager.construction_insurance_capex` documentation](#project-manager-api) for
further details.

`construction_insurance_capex` = `construction_insurance_factor` $\times$ (`turbine_capex` + `bos_capex` + `project_capex`)

### Commissioning

Cost to integrate and commission the project where the `commissioning_factor` is assumed to be
0.0115 unless otherwise specified. Please see the
[{py:meth}`ProjectManager.commissioning_capex` documentation](#project-manager-api) for further
details.

`commissioning_capex` = `commissioning_factor` $\times$ (`turbine_capex` + `bos_capex` + `project_capex`)

### Decommissioning

Surety bond lease to ensure that the burden for removing offshore structures
at the end of their useful life does not fall on taxpayers where the `decommissioning_factor`
is assumed to be 0.2 unless specified otherwise. Please see the
[{py:meth}`ProjectManager.decommissioning_capex` documentation](#project-manager-api) for further
details.

`decommissioning_capex` = `decommissioning_factor` $\times$ `installation_capex`

### Procurement Contingency

Provision for an unforeseen event or circumstance during the procurement process where the
`procurement_contingency_factor` is assumed to be 0.0575 unless specified otherwise. Please see the
[{py:meth}`ProjectManager.procurement_contingency` documentation](#project-manager-api) for further
details.

`procurement_contingency_capex` = `procurement_contingency_factor` $\times$ (`turbine\_capex` + `bos_capex` + `project_capex` - `installation_capex`)

### Installation Contingency

Provision for an unforeseen event or circumstance during the installation process where the
`installation_contingency_factor` is assumed to be 0.345 unless specified otherwise. Please see the
[{py:meth}`ProjectManager.installation_contingency` documentation](#project-manager-api) for further
details.

`installation_contingency_capex` = `installation_contingency_factor` $\times$ `installation_capex`

### Construction Financing

Additional expenses incurred from interest on loans used to fund a construction
project, calculated based on the borrowing period and the project's spending schedule.

The `spend_schedule` is based on industry data from a U.S. project with the following default
payment schedule unless specified otherwise. Please see the
[{py:meth}`ProjectManager.construction_financing_factor` documentation](#project-manager-api) for
further details.

| Year  | Amount  | Cumulative  |
| ----: | ------: | ----------: |
|    0  |    0.25 |        0.25 |
|    1  |    0.25 |        0.5  |
|    2  |    0.30 |        0.8  |
|    3  |    0.10 |        0.9  |
|    4  |    0.10 |        1.0  |
|    5  |    0.00 |        1.0  |

The following default values also apply unless configured otherwise:

- `interest_during_construction` = 0.044
- `tax_rate` = 0.26

`construction_financing_factor` =

$\sum_{k=0}^{n-1} spend\_schedule_k \times (1 + (1 - tax\_rate) \times ((1+ interest\_during\_construction)^{k+0.5} - 1)$

where *k* is the current year and *n* is the total number of years in `spend_schedule`.

`construction_financing_capex` = (`construction_financing_factor` - 1) $\times$
(`construction_insurance_capex` + `commissioning_capex` + `decommissioning_capex`+
`procurement_contingency_capex` + `installation_contingency_capex` + `turbine_capex` + `bos_capex`)

```{bibliography}
:style: unsrtalpha
:filter: docname in docnames
```
