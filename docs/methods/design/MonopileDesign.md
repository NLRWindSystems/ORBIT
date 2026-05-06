(monopile-design-methods)=
# Monopile Design Methodology

For details of the code implementation, please see the
[Monopile Design API documentation](#monopile-design-api).

## Overview

This module is based on initial pile dimension calculations from {cite:t}`arany2017design`.
Pile dimensions are chosen to withstand the bending moment from
the 50-year Extreme Operation Gust (EOG). This corresponds to wind scenario
U-3 in Section 2.2.1. This module is not intended to capture the complexities
of a full engineering design study for monopiles, but rather broadly capture
the scaling trends due to increased site depth, turbine size and material
parameters.

The 50-year extreme wind speed can be calculated using the following cumulative
density function.

$U_{10,50-year}=K(-\ln(1-0.98^\frac{1}{52596}))^\frac{1}{S}$

where $K$ and $S$ are the Weibull scale and shape factors
respectively.

The mudline bending moment is calculated as:

$M_{wind,EOG} = \gamma_LF_{wind,EOG}(S + z_{hub})$

where $\gamma_L$ is the load factor (defaults to 1.35),
$F_{wind,EOG}$ is the total wind load on the turbine, $S$ is the
water depth at site and $z_{hub}$ is the hub height of the turbine. The
derivation of $F_{wind,EOG}$ can be seen in detail in the
[ORBIT technical documentation](https://www.nlr.gov/docs/fy20osti/77081.pdf).

Initial pile dimensions are then calculated using {cite:t}`arany2017design`,
{cite:t}`api2000`, and {cite:t}`poulos1980pile`.

## References

```{bibliography}
:style: unsrtalpha
:filter: docname in docnames
```
