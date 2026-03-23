"""Simple CLI entry point for demonstrating StreetRace Manager flows."""

from .system import StreetRaceSystem


def main():
    """Run a minimal demo banner and create the system facade."""
    system = StreetRaceSystem()
    print("StreetRace Manager CLI")
    print("System initialized.")
    print(f"Registered crew count: {len(system.crew_members)}")


if __name__ == "__main__":
    main()
