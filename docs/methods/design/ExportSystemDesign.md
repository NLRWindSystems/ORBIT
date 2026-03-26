(export-design-methods)=
# Export System Design Methodology

For details of the code implementation, please see
[Export System Design API documentation](#export-design-api).

## Overview

Below is an overview of the process used to design an export cable system in
ORBIT. For more detail on the helper classes used to support this design please
see the [Cabling Helper Classes documentation](#cable-helpers-methods), specifically
{class}`Cable` and {class}`CableSystem`.

## Number of Required Cables

The number of export cables required is calculated by dividing the windfarm's
capacity by the configured export cable's power rating and adding any user
defined redundnacy as seen below.

$num\_cables = \lceil\frac{plant\_capacity}{cable\_power}\rceil + num\_redundant$

## Export Cable length

The total length of the export cables is calculated as the sum of the site
depth, distance to landfall and distance to interconnection multiplied by the
user defined :py:attr\`percent_added_length\` to account for any exclusions or
geotechnical design considerations that make a straight line cable route
impractical.

$length = (d + distance_\text{landfall} + distance_\text{interconnection} * (1 + length_\text{percent_added})$

## Design Result

The result of this design module ({py:attr}`design_result`) is a list of cable
sections and their lengths and masses that represent the export cable system.
This result can then be passed to the
[export cable installation module](#export-install-methods)
to simulate the installation of the system.

## Process Diagrams

![Export cable design process diagram](../../../images/process_diagrams/ExportSystemDesign.png)
