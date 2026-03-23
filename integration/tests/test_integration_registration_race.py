"""Integration tests for registration and race entry flows."""

import pytest

from integration.code.exceptions import RaceError
from integration.code.system import StreetRaceSystem


def test_registering_driver_and_entering_race_succeeds(
    race_ready_system: StreetRaceSystem,
):
    """A registered driver should be entered into a race with an available car."""
    race = race_ready_system.enter_race("race-1", "Nova", "R-7")
    car = race_ready_system.inventory.get_car("R-7")

    assert race.driver_name == "Nova"
    assert race.car_id == "R-7"
    assert race.status == "ready"
    assert car.available is False
    assert car.assigned_race_id == "race-1"


def test_entering_race_with_unregistered_member_fails(
    base_system: StreetRaceSystem,
):
    """A race entry should fail if the crew member was never registered."""
    base_system.add_car("R-7", "Nissan Skyline")
    base_system.create_race("race-1", "Dockside Sprint", 500)

    with pytest.raises(RaceError, match="registered first"):
        base_system.enter_race("race-1", "Ghost", "R-7")


def test_entering_race_with_registered_non_driver_fails(
    base_system: StreetRaceSystem,
):
    """A registered crew member still needs the driver role before race entry."""
    base_system.register_member("Patch")
    base_system.assign_role("Patch", "mechanic", 4)
    base_system.add_car("R-7", "Nissan Skyline")
    base_system.create_race("race-1", "Dockside Sprint", 500)

    with pytest.raises(RaceError, match="driver role"):
        base_system.enter_race("race-1", "Patch", "R-7")
