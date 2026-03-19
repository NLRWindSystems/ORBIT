(cable-helpers-methods)=
# Cabling Design Helpers

For details of the code implementation, please see the
[Cabling Helpers API documentation](#cable-helpers-api).

## Overview

This overview provides the {class}`Cable` class, {class}`Plant` class, and
{class}`CableSystem` parent class.

## Cable

The cable class calculates a provided cable's power rating for determining the
maximum number of turbines that can be supported by a string of cable.

### Character Impedance ($\Omega$)

$$
Z_0 = \sqrt{\frac{R + 2 \pi f L}{G + j 2 \pi f C}}
$$

$R=$ {py:attr}`ac_resistance` \
$j=$ the imaginary unit \
$f=$ {py:attr}`line_frequency` \
$L=$ {py:attr}`inductance` \
$G=$ \frac{1}{R} =${py:attr}`conductance` \
$C=$ {py:attr}`capacitance`

### Power Factor

$$
|P| &= \cos(\theta) \\
    &= \cos(\arctan(\frac{j Z_0}{Z_0}))
$$

$\theta=$ the phase angle \
$jZ_0=$ the imaginary portion of {py:attr}`character_impedance` \
$Z_0=$ the real portion of {py:attr}`character_impedance`

### Cable Power ($MW$)

$P = \sqrt{3} * V * I * |P|$ \
$V=$ {py:attr}`rated_voltage` \
$I=$ {py:attr}`current_capacity` \
$|P|=$ {py:attr}`power_factor`

## Plant

Calculates the wind farm specifications to be used for
[array cable design phase](#array-design-methods). The "data class"
accepts either set distances between turbines and rows or calculates them
based off of the number of rotor diameters specified, for example:

```python
# First see if there is a distance defined
self.turbine_distance = config["plant"].get("turbine_distance", None)

# If not, then multiply the rotor diameter by the turbine spacing,
# an integer representation of the number of rotor diameters and covert
# to kilometers
if self.turbine_distance is None:
    self.turbine_distance = (
        rotor_diameter * config["plant"]["turbine_spacing"] / 1000.0
        )

# Repeat the same process for row distance.
self.row_distance = config["plant"].get("row_distance", None)
    if self.row_distance is None:
        self.row_distance = (
            rotor_diameter * config["plant"]["row_spacing"] / 1000.0
        )
```

where {py:attr}`config` is the configuration dictionary passed to the
[array cable design phase](#array-design-api)

The cable section length for the first turbine in each string is calculated as
the distance to the substation, `substation_distance`.

## CableSystem

{py:class}`CableSystem` acts as the parent class for both
{py:class}`ArrayDesignSystem` and {py:class}`ExportDesignSystem`. As such, it
is not intended to be invoked on its own, however it provides the shared
frameworks for both cabling system.

In particular, the {py:class}`CableSystem` offers the cabling initialization and most of
the output properties such as {py:attr}`cable_lengths_by_type`,
{py:attr}`total_cable_lengths_by_type`, {py:attr}`cost_by_type`,
{py:attr}`total_phase_cost`, {py:attr}`total_phase_time`,
{py:attr}`detailed_output`, and most importantly {py:attr}`design_result` to avoid
redefinition of multiple core calculations.
