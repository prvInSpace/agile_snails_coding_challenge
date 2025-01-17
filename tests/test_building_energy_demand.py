"""Tests for the building energy demand functions.

Todo:
    test_get_office_equipment_demand() Should account for edge cases.
    test_get_lighting_and_other_demand() Should account for edge cases.

"""

import pandas as pd
import numpy as np
import datetime as dt

from sjautobidder.building_demand.energy_demand import (
    get_data_centre_demand,
    get_energy_demand,
    get_office_equipment_demand,
    get_lighting_and_other_demand,
)

from sjautobidder.building_demand.energy_utils import adjust_datetime


def test_get_data_centre_demand() -> None:
    """Test to ensure data center demand is within reasonable ranges."""
    output = get_data_centre_demand()

    # Check return type
    assert isinstance(output, np.ndarray)

    # Check return shape
    assert output.shape == (48,)

    assert sum(output) <= 9600
    assert sum(output) >= 0


def test_get_energy_demand() -> None:
    """Test to get the energy demand of the entire building."""
    output = get_energy_demand()

    assert isinstance(output, pd.DataFrame)

    # assert number of records
    assert output.shape[0] == 48

    # assert columns
    assert output.shape[1] == 7

    assert "Active office mask" in output
    assert "Heating" in output
    assert "Data Centre" in output
    assert "Office Equipment" in output
    assert "LightingOther" in output
    assert "Total demand" in output

    assert isinstance(output["Active office mask"][0], np.bool_)
    assert isinstance(output["Heating"][0], float)
    assert isinstance(output["Data Centre"][0], float)
    assert isinstance(output["LightingOther"][0], float)
    assert isinstance(output["Total demand"][0], float)

    # Ensure total column is correct
    assert (
        output["Total demand"]
        == output["Heating"]
        + output["Data Centre"]
        + output["Office Equipment"]
        + output["LightingOther"]
    ).all()


def test_get_office_equipment_demand():
    """Test to ensure office cumulative office demand is the expected result."""
    general_energy_demand = get_energy_demand()
    output = get_office_equipment_demand(general_energy_demand['Active office mask'])

    # Check return type
    assert isinstance(output, np.ndarray)

    # Check return shape
    assert output.shape == (48,)

    test_day = adjust_datetime(dt.datetime.now().replace(hour=23, minute=0, second=0))
    if test_day.weekday() in {4,5}:
        assert sum(output) == 0
    else:
        assert sum(output) == 160


def test_get_lighting_and_other_demand():
    """Test to ensure lighting and misc demand is the expected result."""
    general_energy_demand = get_energy_demand()
    output = get_lighting_and_other_demand(general_energy_demand['Active office mask'])

    # Check return type
    assert isinstance(output, np.ndarray)

    # Check return shape
    assert output.shape == (48,)

    test_day = adjust_datetime(dt.datetime.now().replace(hour=23, minute=0, second=0))
    print(test_day)
    if test_day.weekday() in {4,5}: 
        # time period starts from 23:00 so technically if the input date is friday, the time period would be saturday.
        assert sum(output) == 0
    else:
        assert sum(output) == 320.
