"""Tests for the `ArraySystemDesign` class."""

__author__ = "Rob Hammond"
__copyright__ = "Copyright 2026, National Laboratory of the Rockies"
__maintainer__ = "Rob Hammond"
__email__ = "rob.hammond@nlr.gov"


from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from ORBIT.core.library import extract_library_specs
from ORBIT.phases.design import ArraySystemDesign, CustomArraySystemDesign
from ORBIT.core.exceptions import LibraryItemNotFoundError

config_full_ring = extract_library_specs("config", "array_design_full_ring")

config_partial_ring = deepcopy(config_full_ring)
config_partial_ring["plant"]["num_turbines"] = 49

config_full_grid = deepcopy(config_full_ring)
config_full_grid["plant"]["layout"] = "grid"

config_partial_grid = deepcopy(config_full_grid)
config_partial_grid["plant"]["num_turbines"] = 49

config_cables_from_file_fail = deepcopy(config_full_grid)
config_cables_from_file_fail["array_system_design"]["cables"] = "Cable1"

config_custom_base = deepcopy(config_full_grid)
config_custom_base["plant"]["num_turbines"] = 8
config_custom_base["plant"]["layout"] = "custom"

config_incorrect_turbines = deepcopy(config_custom_base)
config_incorrect_turbines["plant"]["num_turbines"] = 11
config_incorrect_turbines["array_system_design"]["location_data"] = "passes"

config_missing_col = deepcopy(config_custom_base)
config_missing_col["array_system_design"]["location_data"] = "missing_columns"

config_incomplete_optional = deepcopy(config_custom_base)
config_incomplete_optional["array_system_design"]["location_data"] = (
    "incomplete_optional"
)

config_incomplete_required = deepcopy(config_custom_base)
config_incomplete_required["array_system_design"]["location_data"] = (
    "incomplete_required"
)

config_duplicate_coordinates = deepcopy(config_custom_base)
config_duplicate_coordinates["array_system_design"]["location_data"] = (
    "duplicate_coordinates"
)


def test_array_system_creation():
    array = ArraySystemDesign(config_full_grid)
    array.run()
    assert array


def test_cable_not_found():
    array = ArraySystemDesign(config_cables_from_file_fail)
    with pytest.raises(LibraryItemNotFoundError):
        array.run()


@pytest.mark.parametrize(
    "config,num_full_strings,num_partial_strings,num_turbines_full_string,num_turbines_partial_string",  # noqa: E501
    (
        (config_full_ring, 13, 1, 3, 1),
        (config_partial_ring, 16, 1, 3, 1),
        (config_full_grid, 13, 1, 3, 1),
        (config_partial_grid, 16, 1, 3, 1),
    ),
    ids=["full_ring", "partial_ring", "full_grid", "partial_grid"],
)
def test_string_creation(
    config,
    num_full_strings,
    num_partial_strings,
    num_turbines_full_string,
    num_turbines_partial_string,
):
    array = ArraySystemDesign(config)
    array.run()

    assert array

    string_properties = (
        (num_full_strings, "num_full_strings"),
        (num_partial_strings, "num_partial_strings"),
        (num_turbines_full_string, "num_turbines_full_string"),
        (num_turbines_partial_string, "num_turbines_partial_string"),
    )
    for val, name in string_properties:
        assert val == array.__getattribute__(name)


@pytest.mark.parametrize(
    "turbine_rating,expected",
    ((1, 32), (2, 16), (4.5, 7), (6, 5), (8.5, 3), (12, 2), (15, 2), (22, 1)),
)
def test_max_turbines_per_cable(turbine_rating, expected):
    config = deepcopy(config_full_grid)
    config["array_system_design"]["cables"] = "XLPE_630mm_33kV"
    config["turbine"]["turbine_rating"] = turbine_rating
    array = ArraySystemDesign(config)
    array.run()
    assert array.cables["XLPE_630mm_33kV"].max_turbines == expected


@pytest.mark.parametrize(
    "config,shape,num_null",
    (
        (config_full_ring, (14, 3), 2),
        (config_partial_ring, (17, 3), 2),
        (config_full_grid, (14, 3), 2),
        (config_partial_grid, (17, 3), 2),
    ),
    ids=["full_ring", "partial_ring", "full_grid", "partial_grid"],
)
def test_grid_creation(config, shape, num_null):
    array = ArraySystemDesign(config)
    array.run()

    assert array.turbines_x.shape == shape
    assert array.turbines_y.shape == shape
    assert np.isnan(array.turbines_x).sum() == num_null
    assert np.isnan(array.turbines_y).sum() == num_null

    assert isinstance(array.oss_x, float)
    assert isinstance(array.oss_y, float)

    shape = (shape[0], shape[1] + 1, 2)
    assert array.coordinates.shape == shape
    assert np.isnan(array.coordinates).sum() == 2 * num_null


@pytest.mark.parametrize(
    "config,total_length",
    (
        (config_full_ring, 35.62),
        (config_partial_ring, 43.6),
        (config_full_grid, 76.27),
        (config_partial_grid, 106.41),
    ),
    ids=["full_ring", "partial_ring", "full_grid", "partial_grid"],
)
def test_total_cable_length(config, total_length):
    array = ArraySystemDesign(config)
    array.run()

    val = round(
        sum(val.sum() for val in array.cable_lengths_by_type.values()), 2
    )
    assert total_length == val

    val = round(sum(array.total_cable_length_by_type.values()), 2)
    assert total_length == val

    val = round(
        sum(
            length * n
            for val in array.design_result["array_system"]["cables"].values()
            for length, n in val["cable_sections"]
        ),
        2,
    )
    assert total_length == val


def test_missing_columns():
    array = CustomArraySystemDesign(config_missing_col)

    with pytest.raises(ValueError):
        array.run()


def test_duplicate_turbine_coordinates():
    array = CustomArraySystemDesign(config_duplicate_coordinates)

    with pytest.raises(ValueError):
        array.run()


def test_incomplete_required_columns():
    array = CustomArraySystemDesign(config_incomplete_required)

    with pytest.raises(ValueError):
        array.run()


def test_incomplete_optional_columns():
    array = CustomArraySystemDesign(config_incomplete_optional)

    with pytest.warns(UserWarning):
        array.run()


def test_correct_turbines():
    array = CustomArraySystemDesign(config_incorrect_turbines)

    with pytest.raises(ValueError):
        array.run()


def test_floating_calculations():

    base = deepcopy(config_full_ring)
    base["site"]["depth"] = 50
    number = base["plant"]["num_turbines"]

    sim = ArraySystemDesign(base)
    sim.run()

    base_length = sim.total_length

    floating_no_cat = deepcopy(base)
    floating_no_cat["site"]["depth"] = 250
    floating_no_cat["array_system_design"]["touchdown_distance"] = 0

    sim2 = ArraySystemDesign(floating_no_cat)
    sim2.run()

    no_cat_length = sim2.total_length
    assert no_cat_length == pytest.approx(
        base_length + 2 * (200 / 1000) * number
    )

    floating_cat = deepcopy(base)
    floating_cat["site"]["depth"] = 250

    sim3 = ArraySystemDesign(floating_cat)
    sim3.run()

    with_cat_length = sim3.total_length
    assert with_cat_length < no_cat_length


def test_total_cable_cost():

    array = ArraySystemDesign(config_full_ring)
    array.run()

    assert array.total_cable_cost == pytest.approx(12713999, abs=1e0)


@pytest.mark.parametrize("distance", (True, False))
def test_custom_array_zero_coordinates(distance):
    """Tests that a substation or turbine with an x-coordinate (longitude) of
    0 is kept in the layout, rather than treated as an empty string position.
    """

    def run(x_offset):
        location_data = pd.DataFrame(
            [
                ["oss1", "oss1", "oss1", 0.0, 0.0, np.nan, np.nan, np.nan],
                ["t1", "oss1", "t1", 0.0, 0.01, 0, 0, 0],
                ["t2", "oss1", "t2", 0.0, 0.02, 0, 1, 0],
                ["t3", "oss1", "t3", 0.0, 0.03, 0, 2, 0],
                ["t4", "oss1", "t4", 0.01, 0.0, 1, 0, 0],
                ["t5", "oss1", "t5", 0.01, 0.01, 1, 1, 0],
            ],
            columns=[
                "id",
                "substation_id",
                "name",
                "latitude",
                "longitude",
                "string",
                "order",
                "cable_length",
            ],
        )
        location_data["bury_speed"] = location_data["cable_length"]
        location_data["longitude"] += x_offset

        config = deepcopy(config_custom_base)
        config["plant"]["num_turbines"] = 5
        config["array_system_design"]["location_data"] = location_data
        config["array_system_design"]["distance"] = distance

        array = CustomArraySystemDesign(config)
        array.run()
        return array

    at_origin = run(0.0)
    shifted = run(1.0)

    # Only the unused position at the end of the partial string is empty
    expected_empty = np.zeros((2, 3), dtype=bool)
    expected_empty[1, 2] = True
    np.testing.assert_array_equal(
        np.isnan(at_origin.sections_distance), expected_empty
    )
    assert at_origin.sections_cables[1, 2] is None
    assert None not in at_origin.sections_cables[~expected_empty]

    # Moving the whole layout along the x-axis doesn't change the design
    np.testing.assert_allclose(
        at_origin.sections_distance, shifted.sections_distance
    )
    np.testing.assert_array_equal(
        at_origin.sections_cables, shifted.sections_cables
    )
    assert at_origin.total_length == pytest.approx(shifted.total_length)
    assert at_origin.total_cable_cost == pytest.approx(
        shifted.total_cable_cost
    )
