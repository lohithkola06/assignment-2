"""End-to-end integration tests for StreetRace Manager."""

from integration.code.system import StreetRaceSystem


def test_end_to_end_flow_across_registration_race_results_and_missions(
    base_system: StreetRaceSystem,
):
    """Run one scenario that exercises most modules together."""
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
    race_result = base_system.record_race_result(
        "race-1",
        position=1,
        car_damaged=True,
        notes="Heavy collision near the docks.",
    )

    delivery_mission = base_system.create_mission(
        "mission-1",
        "delivery",
        required_roles=["driver", "strategist"],
    )
    base_system.start_mission(delivery_mission.mission_id, ["Nova", "Cipher"])
    base_system.complete_mission(delivery_mission.mission_id)

    repair_mission = base_system.create_repair_mission(
        "repair-1",
        "R-7",
        assigned_crew=["Patch"],
        required_tools=["wrench"],
        required_parts={"fan belt": 1},
    )
    repaired_car = base_system.repair_car(
        "R-7",
        "Patch",
        required_tools=["wrench"],
        required_parts={"fan belt": 1},
    )
    base_system.complete_mission(repair_mission.mission_id)

    base_system.create_race("race-2", "Harbor Dash", 300)
    second_race = base_system.enter_race("race-2", "Nova", "R-7")
    leaderboard = base_system.leaderboard()

    assert race_result.car_damaged is True
    assert base_system.inventory.get_cash_balance() == 500
    assert repaired_car.damaged is False
    assert repaired_car.available is False
    assert second_race.driver_name == "Nova"
    assert leaderboard[0].member_name == "Nova"
    assert base_system.inventory.part_count("fan belt") == 1
