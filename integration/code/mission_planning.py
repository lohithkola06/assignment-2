"""Mission planning module for StreetRace Manager."""


class MissionPlanningService:
    """Plan and start missions based on required crew roles."""

    def __init__(self, missions, registration_service, crew_service, inventory_service):
        self._missions = missions
        self._registration_service = registration_service
        self._crew_service = crew_service
        self._inventory_service = inventory_service
