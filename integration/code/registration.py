"""Registration module for StreetRace Manager."""

from .exceptions import RegistrationError, ValidationError
from .models import CrewMember


class RegistrationService:
    """Manage registration of crew members."""

    def __init__(self, crew_members):
        self._crew_members = crew_members

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("Crew member name cannot be empty.")
        return normalized

    @staticmethod
    def _normalize_role(role: str) -> str:
        normalized = role.strip().lower()
        if not normalized:
            raise ValidationError("Role cannot be empty.")
        return normalized

    def register_member(self, name: str, role: str | None = None) -> CrewMember:
        """Register a new crew member and optionally attach an initial role."""
        normalized_name = self._normalize_name(name)
        if normalized_name in self._crew_members:
            raise RegistrationError(f"{normalized_name} is already registered.")

        member = CrewMember(name=normalized_name)
        if role is not None:
            normalized_role = self._normalize_role(role)
            member.roles.add(normalized_role)
            member.skills[normalized_role] = 1

        self._crew_members[normalized_name] = member
        return member

    def list_members(self) -> list[CrewMember]:
        """Return all registered crew members sorted by name."""
        return [self._crew_members[name] for name in sorted(self._crew_members)]

    def is_registered(self, name: str) -> bool:
        """Return True if a crew member has already been registered."""
        return name.strip() in self._crew_members

    def get_member(self, name: str) -> CrewMember:
        """Return a registered crew member or raise a registration error."""
        normalized_name = self._normalize_name(name)
        try:
            return self._crew_members[normalized_name]
        except KeyError as exc:
            raise RegistrationError(
                f"{normalized_name} must be registered first."
            ) from exc
