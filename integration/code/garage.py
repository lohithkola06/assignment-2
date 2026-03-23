"""Garage and vehicle maintenance module for StreetRace Manager."""

from .exceptions import GarageError


class GarageService:
    """Inspect and repair damaged cars."""

    def __init__(self, inventory_service, mission_service, crew_service):
        self._inventory_service = inventory_service
        self._mission_service = mission_service
        self._crew_service = crew_service

    def inspect_car(self, car_id: str):
        """Return the current state of a car."""
        return self._inventory_service.get_car(car_id)

    def create_repair_mission(
        self,
        mission_id: str,
        car_id: str,
        assigned_crew: list[str],
        required_parts: dict[str, int] | None = None,
        required_tools: list[str] | None = None,
    ):
        """Create and start a repair mission for a damaged car."""
        mission = self._mission_service.create_mission(
            mission_id=mission_id,
            mission_type="repair",
            required_roles=["mechanic"],
            target_car_id=car_id,
            required_tools=required_tools,
            required_parts=required_parts,
        )
        self._mission_service.start_mission(mission.mission_id, assigned_crew)
        return mission

    def repair_car(
        self,
        car_id: str,
        mechanic_name: str,
        required_parts: dict[str, int] | None = None,
        required_tools: list[str] | None = None,
    ):
        """Repair a damaged car after validating mechanic, parts, and tools."""
        car = self._inventory_service.get_car(car_id)
        if not car.damaged:
            raise GarageError(f"Car '{car.car_id}' does not need repairs.")
        if not self._crew_service.has_role(mechanic_name, "mechanic"):
            raise GarageError(f"{mechanic_name} is not available as a mechanic.")

        normalized_parts = dict(required_parts or {})
        normalized_tools = list(required_tools or [])

        self._inventory_service.require_tools(normalized_tools)
        self._inventory_service.require_parts(normalized_parts)
        for part_name, quantity in normalized_parts.items():
            self._inventory_service.use_part(part_name, quantity)
        return self._inventory_service.repair_car(car.car_id)
