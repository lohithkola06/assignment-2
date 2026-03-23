"""Simple CLI entry point for demonstrating StreetRace Manager flows."""

from .system import StreetRaceSystem


def main():
    """Run a short end-to-end demo flow for the system."""
    system = StreetRaceSystem()
    system.register_member("Nova")
    system.assign_role("Nova", "driver", 5)
    system.register_member("Patch")
    system.assign_role("Patch", "mechanic", 4)
    system.add_car("R-7", "Nissan Skyline")
    system.add_tool("wrench", 1)
    system.add_part("fan belt", 1)
    system.create_race("race-1", "Dockside Sprint", 500)
    system.enter_race("race-1", "Nova", "R-7")
    system.record_race_result("race-1", position=1, car_damaged=True)
    system.create_repair_mission(
        "repair-1",
        "R-7",
        assigned_crew=["Patch"],
        required_parts={"fan belt": 1},
        required_tools=["wrench"],
    )
    system.repair_car(
        "R-7",
        "Patch",
        required_parts={"fan belt": 1},
        required_tools=["wrench"],
    )

    print("StreetRace Manager CLI Demo")
    print(f"Cash balance: {system.inventory.get_cash_balance()}")
    print(f"Car damaged: {system.inventory.get_car('R-7').damaged}")
    print(f"Top ranked member: {system.leaderboard()[0].member_name}")


if __name__ == "__main__":
    main()
