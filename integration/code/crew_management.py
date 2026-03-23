"""Crew management module for StreetRace Manager."""

from .exceptions import CrewAssignmentError, ValidationError
from .models import CrewMember


class CrewManagementService:
    """Manage crew roles and skill levels."""

    def __init__(self, registration_service):
        self._registration_service = registration_service

    @staticmethod
    def _normalize_role(role: str) -> str:
        normalized = role.strip().lower()
        if not normalized:
            raise ValidationError("Role cannot be empty.")
        return normalized

    @staticmethod
    def _validate_skill_level(skill_level: int) -> int:
        if skill_level <= 0:
            raise ValidationError("Skill level must be a positive integer.")
        return skill_level

    def assign_role(
        self,
        member_name: str,
        role: str,
        skill_level: int = 1,
    ) -> CrewMember:
        """Assign a role to a registered crew member and set the skill level."""
        member = self._registration_service.get_member(member_name)
        normalized_role = self._normalize_role(role)
        validated_skill = self._validate_skill_level(skill_level)
        member.roles.add(normalized_role)
        member.skills[normalized_role] = validated_skill
        return member

    def update_skill(self, member_name: str, role: str, skill_level: int) -> CrewMember:
        """Update the stored skill level for an existing member role."""
        member = self._registration_service.get_member(member_name)
        normalized_role = self._normalize_role(role)
        validated_skill = self._validate_skill_level(skill_level)
        if normalized_role not in member.roles:
            raise CrewAssignmentError(
                f"{member.name} does not currently hold the role '{normalized_role}'."
            )
        member.skills[normalized_role] = validated_skill
        return member

    def has_role(self, member_name: str, role: str) -> bool:
        """Return True if the crew member currently holds the given role."""
        if not self._registration_service.is_registered(member_name):
            return False
        member = self._registration_service.get_member(member_name)
        return self._normalize_role(role) in member.roles

    def get_skill(self, member_name: str, role: str) -> int:
        """Return the skill level for a crew member's role."""
        member = self._registration_service.get_member(member_name)
        normalized_role = self._normalize_role(role)
        if normalized_role not in member.skills:
            raise CrewAssignmentError(
                f"{member.name} does not currently hold the role '{normalized_role}'."
            )
        return member.skills[normalized_role]

    def members_with_role(self, role: str) -> list[CrewMember]:
        """Return active crew members who hold the requested role."""
        normalized_role = self._normalize_role(role)
        return [
            member
            for member in self._registration_service.list_members()
            if normalized_role in member.roles and member.active
        ]

    def ensure_roles_available(
        self,
        required_roles: list[str],
        crew_names: list[str] | None = None,
    ) -> dict[str, CrewMember]:
        """Validate that the required roles are covered by available crew."""
        candidates = []
        if crew_names is None:
            candidates = self._registration_service.list_members()
        else:
            for name in crew_names:
                member = self._registration_service.get_member(name)
                if member.active:
                    candidates.append(member)

        coverage: dict[str, CrewMember] = {}
        for role in required_roles:
            normalized_role = self._normalize_role(role)
            matching_member = next(
                (
                    member
                    for member in candidates
                    if member.active and normalized_role in member.roles
                ),
                None,
            )
            if matching_member is None:
                raise CrewAssignmentError(
                    f"Required role '{normalized_role}' is unavailable."
                )
            coverage[normalized_role] = matching_member
        return coverage
