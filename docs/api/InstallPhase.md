(install-phases)=
# Install Phases

ORBIT includes the following installation modules that can be used within
ProjectManager. These modules utilize SimPy to model individual processes and
their constraints due to weather and vessel interactions. For a more detailed
description of vessel scheduling within ORBIT, please see `add link`.

## Substructures

### Fixed-Bottom

- [Monopile](#monopile-install-api)
- [Jacket](#jacket-install-api)
- [Scouring Protection](#scour-protection-install-api)

### Floating

- [Moored Substructure](#moored-sub-install-api)
- [Gravity-Based Substructure](#gravity-install-api)
- [Mooring System](#mooring-install-api)

## Cabling

- [Array System](#array-install-api)
- [Export System](#export-install-api)

## Substation & Turbine

- [Turbine](#turbine-install-api)
- [Offshore Substation](#oss-install-api)
