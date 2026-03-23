"""Mission planning module for StreetRace Manager."""

from .exceptions import CrewAssignmentError, InventoryError, MissionError, ValidationError
from .models import Mission


class MissionPlanningService:
    """Plan and start missions based on required crew roles."""

    def __init__(self, missions, registration_service, crew_service, inventory_service):
        self._missions = missions
        self._registration_service = registration_service
        self._crew_service = crew_service
        self._inventory_service = inventory_service

    @staticmethod
    def _normalize_mission_id(mission_id: str) -> str:
        normalized = mission_id.strip()
        if not normalized:
            raise ValidationError("Mission ID cannot be empty.")
        return normalized

    def create_mission(
        self,
        mission_id: str,
        mission_type: str,
        required_roles: list[str],
        target_car_id: str | None = None,
        required_tools: list[str] | None = None,
        required_parts: dict[str, int] | None = None,
    ) -> Mission:
        """Create a mission that can later be started by the system."""
        normalized_mission_id = self._normalize_mission_id(mission_id)
        normalized_mission_type = mission_type.strip().lower()
        if not normalized_mission_type:
            raise ValidationError("Mission type cannot be empty.")
        if not required_roles:
            raise ValidationError("A mission must require at least one role.")
        if normalized_mission_id in self._missions:
            raise MissionError(f"Mission '{normalized_mission_id}' already exists.")

        mission = Mission(
            mission_id=normalized_mission_id,
            mission_type=normalized_mission_type,
            required_roles=[role.strip().lower() for role in required_roles],
            target_car_id=target_car_id,
            required_tools=list(required_tools or []),
            required_parts=dict(required_parts or {}),
        )
        self._missions[normalized_mission_id] = mission
        return mission

    def get_mission(self, mission_id: str) -> Mission:
        """Return a mission by ID."""
        normalized_mission_id = self._normalize_mission_id(mission_id)
        try:
            return self._missions[normalized_mission_id]
        except KeyError as exc:
            raise MissionError(f"Mission '{normalized_mission_id}' does not exist.") from exc

    def start_mission(self, mission_id: str, assigned_crew: list[str]) -> Mission:
        """Start a mission after validating crew roles and resource requirements."""
        mission = self.get_mission(mission_id)
        if mission.status == "started":
            raise MissionError(f"Mission '{mission.mission_id}' is already in progress.")
        if mission.status == "completed":
            raise MissionError(f"Mission '{mission.mission_id}' has already been completed.")
        if not assigned_crew:
            raise MissionError("A mission cannot start without assigned crew.")

        try:
            self._crew_service.ensure_roles_available(mission.required_roles, assigned_crew)
            self._inventory_service.require_tools(mission.required_tools)
            self._inventory_service.require_parts(mission.required_parts)
        except (CrewAssignmentError, InventoryError) as exc:
            raise MissionError(str(exc)) from exc

        if mission.target_car_id is not None:
            target_car = self._inventory_service.get_car(mission.target_car_id)
            if target_car.damaged:
                try:
                    self._crew_service.ensure_roles_available(["mechanic"], assigned_crew)
                except CrewAssignmentError as exc:
                    raise MissionError(
                        "Damaged-car missions require a mechanic."
                    ) from exc

        mission.assigned_crew = list(assigned_crew)
        mission.status = "started"
        return mission

    def complete_mission(self, mission_id: str) -> Mission:
        """Mark a started mission as completed."""
        mission = self.get_mission(mission_id)
        if mission.status != "started":
            raise MissionError(f"Mission '{mission.mission_id}' must be started first.")
        mission.status = "completed"
        return mission
