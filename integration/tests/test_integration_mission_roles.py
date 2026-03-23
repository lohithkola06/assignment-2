"""Integration tests for mission role validation flows."""

import pytest

from integration.code.exceptions import MissionError
from integration.code.system import StreetRaceSystem


def test_mission_cannot_start_when_required_roles_are_unavailable(
    base_system: StreetRaceSystem,
):
    """Mission startup should fail when the assigned crew do not cover all roles."""
    base_system.register_member("Nova")
    base_system.assign_role("Nova", "driver", 5)
    base_system.create_mission(
        "mission-1",
        "delivery",
        required_roles=["driver", "strategist"],
    )

    with pytest.raises(MissionError, match="strategist"):
        base_system.start_mission("mission-1", ["Nova"])


def test_mission_starts_when_required_roles_are_present(
    base_system: StreetRaceSystem,
):
    """Mission startup should succeed once all required roles are covered."""
    base_system.register_member("Nova")
    base_system.assign_role("Nova", "driver", 5)
    base_system.register_member("Cipher")
    base_system.assign_role("Cipher", "strategist", 4)
    mission = base_system.create_mission(
        "mission-1",
        "delivery",
        required_roles=["driver", "strategist"],
    )
    started = base_system.start_mission(mission.mission_id, ["Nova", "Cipher"])

    assert started.status == "started"
    assert started.assigned_crew == ["Nova", "Cipher"]
