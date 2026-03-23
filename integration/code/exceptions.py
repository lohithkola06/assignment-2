"""Custom exceptions for StreetRace Manager business rule failures."""


class StreetRaceError(Exception):
    """Base class for StreetRace Manager errors."""


class ValidationError(StreetRaceError):
    """Raised when incoming data is invalid."""


class RegistrationError(StreetRaceError):
    """Raised when registration rules are violated."""


class CrewAssignmentError(StreetRaceError):
    """Raised when crew role assignment or lookup fails."""


class InventoryError(StreetRaceError):
    """Raised when inventory operations cannot be completed."""


class RaceError(StreetRaceError):
    """Raised when race setup or participation rules fail."""


class ResultsError(StreetRaceError):
    """Raised when a race result cannot be recorded."""


class MissionError(StreetRaceError):
    """Raised when mission planning or execution fails."""


class GarageError(StreetRaceError):
    """Raised when garage inspection or repair fails."""


class RankingsError(StreetRaceError):
    """Raised when rankings cannot be updated or queried."""
