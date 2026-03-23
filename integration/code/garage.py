"""Garage and vehicle maintenance module for StreetRace Manager."""


class GarageService:
    """Inspect and repair damaged cars."""

    def __init__(self, inventory_service, mission_service, crew_service):
        self._inventory_service = inventory_service
        self._mission_service = mission_service
        self._crew_service = crew_service
