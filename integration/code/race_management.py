"""Race management module for StreetRace Manager."""


class RaceManagementService:
    """Create races and enter drivers with eligible cars."""

    def __init__(self, races, registration_service, crew_service, inventory_service):
        self._races = races
        self._registration_service = registration_service
        self._crew_service = crew_service
        self._inventory_service = inventory_service
