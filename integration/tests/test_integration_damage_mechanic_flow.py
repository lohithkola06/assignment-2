"""Integration tests for damaged-car and mechanic flows."""

import pytest

from integration.code.exceptions import GarageError, MissionError
from integration.code.system import StreetRaceSystem


def test_damaged_car_requires_mechanic_before_repair_mission_starts(
    damaged_race_system: StreetRaceSystem,
):
    """A repair mission should reject assigned crew that do not include a mechanic."""
    mission = damaged_race_system.create_mission(
        "repair-1",
        "repair",
        required_roles=["mechanic"],
        target_car_id="R-7",
        required_tools=["wrench"],
        required_parts={"fan belt": 1},
    )

    with pytest.raises(MissionError, match="mechanic"):
        damaged_race_system.start_mission(mission.mission_id, ["Nova"])


def test_repair_flow_consumes_parts_and_restores_car(
    damaged_race_system: StreetRaceSystem,
):
    """The repair flow should consume parts and restore the damaged car."""
    mission = damaged_race_system.create_repair_mission(
        "repair-1",
        "R-7",
        assigned_crew=["Patch"],
        required_tools=["wrench"],
        required_parts={"fan belt": 1},
    )
    repaired_car = damaged_race_system.repair_car(
        "R-7",
        "Patch",
        required_tools=["wrench"],
        required_parts={"fan belt": 1},
    )
    completed_mission = damaged_race_system.complete_mission(mission.mission_id)

    assert repaired_car.damaged is False
    assert repaired_car.available is True
    assert damaged_race_system.inventory.part_count("fan belt") == 1
    assert completed_mission.status == "completed"


def test_repair_fails_when_non_mechanic_attempts_garage_work(
    damaged_race_system: StreetRaceSystem,
):
    """Garage repairs should fail if the assigned crew member is not a mechanic."""
    with pytest.raises(GarageError, match="mechanic"):
        damaged_race_system.repair_car(
            "R-7",
            "Nova",
            required_tools=["wrench"],
            required_parts={"fan belt": 1},
        )
