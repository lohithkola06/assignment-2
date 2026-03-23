"""Crew management module for StreetRace Manager."""


class CrewManagementService:
    """Manage crew roles and skill levels."""

    def __init__(self, registration_service):
        self._registration_service = registration_service
