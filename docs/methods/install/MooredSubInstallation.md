(moored-sub-install-methods)=
# Moored Substructure Installation Methodology

For details of the code implementation, please see the
[Moored Substructure Installation API documentation](#moored-sub-install-api)

## Overview

The `MooredSubInstallation` module simulates the manufacture and installation
of moored substructures for a floating offshore wind project. The installation
procedures include the time required to manufacture a substructure at quayside,
assemble a turbine on the substructure, ballast the completed assembly, tow
the completed assembly to site and hook up the pre-installed mooring lines.

## Configuration

The primary configuration parameters available for this module are related to
the quayside assembly process and the vessels used to tow the completed
assemblies to site and complete the installation. The code block highlights
the key parameters available.

```python
config = {

    ...

    "ahts_vessel": "example_ahts_vessel",    # Anchor handling tug supply vessel associated with each tow group.
    "towing_vessel": "example_towing_vessel",    # Towing groups will contain multiple of this vessel.
    "towing_groups": {
        "towing_vessel": 1,  # Vessels used to tow the substructure to site.
        "ahts_vessels": 3,  # Number of anchor handling/station keeping vessels
        "num_groups": 1  # Number of independent groups. Optional, default: 1.
    },

    "port": {
        "sub_assembly_lines": 2,  # Independent substructure assembly lines.
        "sub_storage": 8,         # Available storage berths at port for completed substructures.
        "turbine_assembly_cranes": 2,  # Independent turbine assembly cranes.
        "assembly_storage": 8,    # Available storage berths at port for completed turbine/substructure assemblies.
    },

    "substructure": {
        "takt_time": 168,   # h, time to manufacture one substructure.
        "towing_speed": 6,  # km/h.
    },

    ...
}
```

## Processes

### Quayside Assembly

| Process                                               | Default |
| ----------------------------------------------------- | ------- |
| Substructure Assembly                                 | 168h    |
| Prepare Substructure for Turbine Assembly             | 12h     |
| Lift and Fasten Tower Section (repeated if necessary) | 12h     |
| Lift and Fasten Nacelle                               | 7h      |
| Lift and Fasten Blade (repeated)                      | 3.5h    |
| Mechanical Completion and Verification                | 24h     |

### Substructure Tow-out and Assembly

| Process                             | Default    |
| ----------------------------------- | ---------- |
| Ballast to Towing Draft             | 6h         |
| Tow-out                             | calculated |
| Ballast to Operational Draft        | 6h         |
| Connect Mooring Lines               | 22h        |
| Check Mooring Lines and Connections | 12h        |
