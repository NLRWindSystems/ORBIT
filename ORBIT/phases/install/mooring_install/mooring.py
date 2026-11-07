"""Installation strategies for mooring systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nlr.gov"


from marmot import process

from ORBIT.core import Cargo
from ORBIT.core.logic import position_onsite, get_list_of_items_from_port
from ORBIT.core.defaults import process_times as pt
from ORBIT.phases.install import InstallPhase
from ORBIT.core.exceptions import ItemNotFound


class MooringSystemInstallation(InstallPhase):
    """Module to model the installation of mooring systems at sea."""

    phase = "Mooring System Installation"
    capex_category = "Mooring System"

    #:
    expected_config = {
        "mooring_install_vessel": "dict | str",
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "mooring_system": {
            "num_lines": "int (optional, per turbine, standard design only)",
            "total_num_lines": "int (optional, custom design only)",
            "total_num_anchors": "int (optional, custom design only)",
            "line_cost": "USD (optional, per line, standard design only)",
            "anchor_cost": "USD (optional, per anchor, standard design only)",
            "total_line_cost": "USD (optional, custom design only)",
            "total_anchor_cost": "USD (optional, custom design only)",
            "system_cost": "USD (optional)",
            "design_class": "str (optional, default: 'standard')",
        },
        "mooring_installation_method": "str (optional, default: 'basic')",
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of `MooringSystemInstallation`.

        Parameters
        ----------
        config : dict
            Simulation specific configuration.
        weather : np.array
            Weather data at site.
        """

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """
        Sets up the required simulation infrastructure:
            - initializes port
            - initializes installation vessel
            - initializes mooring systems at port.
        """

        depth = self.config["site"]["depth"]
        distance = self.config["site"]["distance"]

        # ProjectManager.run_design_phase merges MooringSystem.design_result into self.config directly
        mooring_system = self.config["mooring_system"]
        self.design_class = mooring_system.get("design_class", "standard")
        self.num_systems = self.config["plant"]["num_turbines"]

        if self.design_class == "standard":
            self.num_lines = mooring_system["num_lines"]
            self.total_num_lines = self.num_systems * self.num_lines
            self.total_num_anchors = self.total_num_lines
            self.total_line_cost = self.total_num_lines * mooring_system["line_cost"]
            self.total_anchor_cost = (
                self.total_num_anchors * mooring_system["anchor_cost"]
            )

        elif self.design_class == "custom":
            self.total_num_lines = mooring_system["total_num_lines"]
            self.total_num_anchors = mooring_system["total_num_anchors"]
            self.total_line_cost = mooring_system["total_line_cost"]
            self.total_anchor_cost = mooring_system["total_anchor_cost"]

        else:
            raise ValueError(
                f"Mooring system design_class '{self.design_class}' not"
                " recognized. Valid options: 'standard', 'custom'"
            )

        # 'system_cost' is only present when a design phase runs first; fall
        # back to the cost inputs when 'mooring_system' is user-provided.
        self.system_cost = mooring_system.get(
            "system_cost", self.total_line_cost + self.total_anchor_cost
        )

        # set the installation method
        self.installation_method = self.config.get(
            "mooring_installation_method", "basic"
        )

        self.initialize_port()
        self.initialize_installation_vessel()
        self.initialize_components()

        if self.installation_method == "basic":     # install packaged mooring systems
            install_mooring_systems(
                self.vessel,
                self.port,
                distance,
                depth,
                self.num_systems,
                **kwargs,
            )

        # install all anchors first, then mooring lines
        elif self.installation_method == "anchors-first":
            install_all_anchors_then_moorings(
                self.vessel,
                self.port,
                distance,
                depth,
                self.total_num_anchors,
                self.total_num_lines,
                **kwargs,
            )

    @property
    def system_capex(self):
        """Returns total procurement cost of all mooring systems."""
        return self.system_cost

    def initialize_installation_vessel(self):
        """Initializes the mooring system installation vessel."""

        vessel_specs = self.config.get("mooring_install_vessel", None)
        name = vessel_specs.get("name", "Mooring System Installation Vessel")

        vessel = self.initialize_vessel(name, vessel_specs)
        self.env.register(vessel)

        vessel.initialize()
        vessel.at_port = True
        vessel.at_site = False
        self.vessel = vessel

    def initialize_components(self):
        """Initializes the Cargo components at port."""

        mooring_system = self.config["mooring_system"]

        if self.installation_method == "basic":
            # Standard installation: load complete mooring systems
            if mooring_system.get("has_shared_components", False):
                raise ValueError(
                    "The 'basic' installation method cannot be used with"
                    " shared anchors or shared mooring lines."
                )

            if self.design_class == "standard":
                system = MooringSystem(**mooring_system)
                for _ in range(self.num_systems):
                    self.port.put(system)

            elif self.design_class == "custom":
                self.num_systems = mooring_system["lines"]["turbine_id"].nunique()
                for i in range(self.num_systems):
                    self.port.put(MooringSystem(i, **mooring_system))

        elif self.installation_method == "anchors-first":
            if self.design_class == "standard":
                raise ValueError(
                    "The standard mooring design only supports the 'basic'"
                    " installation method."
                )

            for i in range(self.total_num_anchors):
                self.port.put(Anchor(i, **mooring_system))

            for i in range(self.total_num_lines):
                self.port.put(Mooring(i, **mooring_system))

        else:
            raise ValueError(
                f"Installation method '{self.installation_method}' not"
                " recognized. Valid options: 'basic', 'anchors-first'"
            )

    @property
    def detailed_output(self):
        """Detailed outputs of the mooring system installation."""

        outputs = {self.phase: {**self.agent_efficiencies}}

        return outputs


@process
def install_mooring_systems(vessel, port, distance, depth, systems, **kwargs):
    """
    Logic for the Mooring System Installation Vessel.

    Parameters
    ----------
    vessel : Vessel
        Mooring System Installation Vessel
    port : Port
    distance : int | float
        Distance between port and site (km).
    systems : int
        Total systems to install.
    """

    n = 0
    while n < systems:
        if vessel.at_port:
            try:
                # Get mooring systems from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["MooringSystem"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:
            if vessel.storage.items:
                system = yield vessel.get_item_from_storage(
                    "MooringSystem", **kwargs
                )
                for _ in range(system.num_lines):
                    yield position_onsite(vessel, **kwargs)
                    yield perform_mooring_site_survey(vessel, **kwargs)
                    yield install_mooring_anchor(
                        vessel,
                        depth,
                        system.anchor_type,
                        **kwargs,
                    )
                    yield install_mooring_line(vessel, depth, **kwargs)

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Mooring systems installation complete!")


@process
def install_all_anchors_then_moorings(
    vessel, port, distance, depth, nanchors, nmoorings, **kwargs
):
    """
    Logic for the Mooring System Installation Vessel when all anchors are
    installed before any mooring lines are installed.

    Parameters
    ----------
    vessel : Vessel
        Mooring System Installation Vessel
    port : Port
    distance : int | float
        Distance between port and site (km).
    depth : int | float
        Depth at site (m).
    nanchors : int
        Total number of anchors to install.
    nmoorings : int
        Total number of mooring lines to install.
    """

    n = 0
    while n < nanchors:
        if vessel.at_port:
            try:
                # Get anchors from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["Anchor"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:

                anchor = yield vessel.get_item_from_storage(
                    "Anchor", **kwargs
                )

                yield position_onsite(vessel, **kwargs)
                yield perform_mooring_site_survey(vessel, **kwargs)     # this defaults to 4 hrs unless 'process_times: mooring_site_survey_time: 1' is included in config
                yield install_mooring_anchor(
                    vessel,
                    depth,
                    anchor.anchor_type,
                    **kwargs,
                )

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Installation of all anchors complete!")


    n = 0
    while n < nmoorings:
        if vessel.at_port:
            try:
                # Get mooring lines from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["Mooring"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:

                mooring = yield vessel.get_item_from_storage(
                    "Mooring", **kwargs
                )

                yield position_onsite(vessel, **kwargs)
                yield perform_mooring_site_survey(vessel, **kwargs)     # this defaults to 4 hrs unless 'process_times: mooring_site_survey_time: 1' is included in config     
                yield install_mooring_line(vessel, depth, **kwargs)

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Installation of all mooring lines complete!")


@process
def perform_mooring_site_survey(vessel, **kwargs):
    """
    Calculates time required to perform a mooring system survey.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.

    Yields
    ------
    vessel.task representing time to "Perform Mooring Site Survey".
    """

    key = "mooring_site_survey_time"
    survey_time = kwargs.get(key, pt[key])

    yield vessel.task_wrapper(
        "Perform Mooring Site Survey",
        survey_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


@process
def install_mooring_anchor(vessel, depth, anchor_type, **kwargs):
    """
    Calculates time required to install a mooring system anchor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    depth : int | float
        Depth at site (m).
    anchor_type : str
        Anchor type. 'Suction Pile', 'Drag Embedment' or 'D&G Pile'.

    Yields
    ------
    vessel.task representing time to install mooring anchor.
    """

    if anchor_type == "Suction Pile":
        key = "suction_pile_install_time"
        task = "Install Suction Pile Anchor"
        fixed = kwargs.get(key, pt[key])

    elif anchor_type == "Drag Embedment":
        key = "drag_embed_install_time"
        task = "Install Drag Embedment Anchor"
        fixed = kwargs.get(key, pt[key])

    elif anchor_type == "D&G Pile":
        key = "dandg_pile_install_time"
        task = "Install D&G Pile Anchor"
        fixed = kwargs.get(key, pt[key])

    else:
        raise ValueError(
            f"Mooring System Anchor Type: {anchor_type} not recognized.",
        )

    install_time = fixed + 0.005 * depth
    yield vessel.task_wrapper(
        task,
        install_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


@process
def install_mooring_line(vessel, depth, **kwargs):
    """
    Calculates time required to install a mooring system line.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    depth : int | float
        Depth at site (m).

    Yields
    ------
    vessel.task representing time to install mooring line.
    """

    install_time = 0.005 * depth

    yield vessel.task_wrapper(
        "Install Mooring Line",
        install_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


class MooringSystem(Cargo):
    """Mooring System Cargo: all lines and anchors for one platform."""

    def __init__(
        self,
        i=None,
        num_lines=None,
        line_mass=None,
        anchor_mass=None,
        anchor_type="Suction Pile",
        **kwargs,
    ):
        """
        Creates an instance of MooringSystem.

        Parameters
        ----------
        i : int
            Custom design only: index of the platform (sorted turbine_id).
        num_lines : int
            Standard design only: number of lines (and anchors) per system.
        line_mass : float
            Standard design only: mass of one mooring line (t).
        anchor_mass : float
            Standard design only: mass of one anchor (t).
        anchor_type : str
            Standard design only: anchor type used for every line.
        """

        self.deck_space = 0

        if kwargs.get("design_class", "standard") == "custom":
            lines_df = kwargs["lines"]
            anchors_df = kwargs["anchors"]
            turbine_id = sorted(lines_df["turbine_id"].unique())[i]

            moorings = [
                Mooring(j, **kwargs)
                for j in lines_df.index[lines_df["turbine_id"] == turbine_id]
            ]
            anchors = [
                Anchor(k, **kwargs)
                for k in anchors_df.index[anchors_df["turbine_id"] == turbine_id]
            ]
            if len(anchors) != len(moorings):
                raise ValueError(
                    f"Turbine {turbine_id} has {len(anchors)} anchors and"
                    f" {len(moorings)} mooring lines; the 'basic' installation"
                    " method requires one anchor per line."
                )

            anchor_types = {a.anchor_type for a in anchors}
            if len(anchor_types) != 1:
                raise ValueError(
                    f"Turbine {turbine_id} has mixed anchor types"
                    f" {sorted(anchor_types)}; a MooringSystem requires one"
                    " anchor type for all of its lines."
                )

            num_lines = len(moorings)
            line_mass = sum(m.mass for m in moorings) / num_lines
            anchor_mass = sum(a.mass for a in anchors) / num_lines
            anchor_type = anchor_types.pop()
            self.deck_space = sum(c.deck_space for c in [*anchors, *moorings])

        self.num_lines = num_lines
        self.line_mass = line_mass      # average mass across all mooring lines in the package
        self.anchor_mass = anchor_mass  # average mass across all anchors in the package
        self.anchor_type = anchor_type

    @property
    def mass(self):
        """Returns total system mass in t."""

        return self.num_lines * (self.line_mass + self.anchor_mass)

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""

        key = "mooring_system_load_time"
        time = kwargs.get(key, pt[key])

        return "Load Mooring System", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""

        return "", 0



class Anchor(Cargo):
    """Single Anchor Cargo Component."""

    def __init__(self, i, anchors=None, **kwargs):
        """
        Creates an instance of Anchor.

        Parameters
        ----------
        i : int
            Index label of the anchor row in `anchors`.
        anchors : pd.DataFrame
            Anchor sections from `CustomMooringSystemDesign`.
        """

        self.anchors = anchors
        anchor = self.anchors.loc[i]
        self.turbine_id = anchor["turbine_id"]
        self.line_id = anchor["line_id"]

        anchor_diameter = anchor['diameter']
        anchor_length = anchor['length']
        self.deck_space = (anchor_diameter + 3) * (anchor_length + 3)
    
        # Extract anchor type from section_id
        section_id = anchor['section_id'].lower()
        
        if 'suction' in section_id:
            self.anchor_type = 'Suction Pile'
        elif 'dea' in section_id or 'drag' in section_id:
            self.anchor_type = 'Drag Embedment'
        elif 'dandg' in section_id:
            self.anchor_type = 'D&G Pile'
        else:
            raise ValueError(f'Anchor type in {section_id} is not supported yet')

        self.anchor_mass = anchor['mass']       # [t]
    
    @property
    def mass(self):
        """Returns total system mass in t."""
        return self.anchor_mass

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        key = "anchor_load_time"
        time = kwargs.get(key, pt[key])
        return "Load Anchor", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        return "", 0





class Mooring(Cargo):
    """Single Mooring Line Cargo Component."""

    def __init__(self, i, **kwargs):
        """
        Creates an instance of Mooring.

        Parameters
        ----------
        i : int
            Index label of the line row in `kwargs['lines']`.
        """

        lines = kwargs["lines"]
        turbine_id = lines.loc[i, "turbine_id"]
        line_id = lines.loc[i, "line_id"]
        self.turbine_id = turbine_id
        self.line_id = line_id
        
        # Filter chains and ropes for this specific turbine and mooring line
        # This gets ALL chain sections for this specific turbine's mooring line
        self.chains = kwargs['chains'][
            (kwargs['chains']['turbine_id'] == turbine_id) & 
            (kwargs['chains']['line_id'] == line_id)
        ]
        self.ropes = kwargs['ropes'][
            (kwargs['ropes']['turbine_id'] == turbine_id) & 
            (kwargs['ropes']['line_id'] == line_id)
        ]

        # Calculate total mass for all chain segments in this line
        self.chain_mass = self.chains['mass'].sum() if len(self.chains) > 0 else 0.0
        self.rope_mass = self.ropes['mass'].sum() if len(self.ropes) > 0 else 0.0

        # Calculate deck space based on total lengths
        chain_total_length = self.chains['length'].sum() if len(self.chains) > 0 else 0.0
        rope_total_length = self.ropes['length'].sum() if len(self.ropes) > 0 else 0.0
        
        self.chain_deck_space = (chain_total_length * 3.28 / 90) * 7.5
        self.rope_deck_space = (6.4 * 4.5) * (rope_total_length / 2020)     # roughly 6.75 m^2 per 450 m length
        self.deck_space = self.chain_deck_space + self.rope_deck_space
    
    @property
    def mass(self):
        """Returns total system mass in t."""
        return self.chain_mass + self.rope_mass

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        key = "mooring_line_load_time"
        time = kwargs.get(key, pt[key])
        return "Load Mooring Line", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        return "", 0



