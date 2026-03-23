"""Pytest fixtures for StreetRace Manager integration tests."""

import pytest

from integration.code.system import StreetRaceSystem


@pytest.fixture
def base_system() -> StreetRaceSystem:
    """Return a fresh StreetRace Manager system for each test."""
    return StreetRaceSystem()


@pytest.fixture
def race_ready_system(base_system: StreetRaceSystem) -> StreetRaceSystem:
    """Provide a system with a driver, a car, and a created race."""
    base_system.register_member("Nova")
    base_system.assign_role("Nova", "driver", 5)
    base_system.register_member("Cipher")
    base_system.assign_role("Cipher", "strategist", 4)
    base_system.add_car("R-7", "Nissan Skyline")
    base_system.create_race("race-1", "Dockside Sprint", 500)
    return base_system


@pytest.fixture
def entered_race_system(race_ready_system: StreetRaceSystem) -> StreetRaceSystem:
    """Provide a system with a driver already entered into a race."""
    race_ready_system.enter_race("race-1", "Nova", "R-7")
    return race_ready_system


@pytest.fixture
def damaged_race_system(base_system: StreetRaceSystem) -> StreetRaceSystem:
    """Provide a system where a race has completed and the car was damaged."""
    base_system.register_member("Nova")
    base_system.assign_role("Nova", "driver", 5)
    base_system.register_member("Patch")
    base_system.assign_role("Patch", "mechanic", 4)
    base_system.register_member("Cipher")
    base_system.assign_role("Cipher", "strategist", 4)
    base_system.add_car("R-7", "Nissan Skyline")
    base_system.add_tool("wrench", 1)
    base_system.add_part("fan belt", 2)
    base_system.create_race("race-1", "Dockside Sprint", 500)
    base_system.enter_race("race-1", "Nova", "R-7")
    base_system.record_race_result("race-1", position=1, car_damaged=True)
    return base_system
