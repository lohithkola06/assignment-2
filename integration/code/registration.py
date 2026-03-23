"""Registration module for StreetRace Manager."""


class RegistrationService:
    """Manage registration of crew members."""

    def __init__(self, crew_members):
        self._crew_members = crew_members
