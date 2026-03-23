"""Rankings and reputation module for StreetRace Manager."""

from .exceptions import RankingsError, ValidationError
from .models import RankingEntry


class RankingsService:
    """Maintain a simple leaderboard and reputation table."""

    def __init__(self, rankings):
        self._rankings = rankings

    @staticmethod
    def _normalize_name(member_name: str) -> str:
        normalized = member_name.strip()
        if not normalized:
            raise ValidationError("Member name cannot be empty.")
        return normalized

    @staticmethod
    def points_for_position(position: int) -> int:
        """Return the ranking points for a finishing position."""
        if position <= 0:
            raise ValidationError("Race position must be a positive integer.")
        points_table = {1: 10, 2: 6, 3: 4}
        return points_table.get(position, 1)

    def get_entry(self, member_name: str) -> RankingEntry:
        """Return an existing ranking entry or create an empty one."""
        normalized_name = self._normalize_name(member_name)
        if normalized_name not in self._rankings:
            self._rankings[normalized_name] = RankingEntry(member_name=normalized_name)
        return self._rankings[normalized_name]

    def record_race_result(
        self,
        member_name: str,
        position: int,
        prize_money: int,
        reputation_points: int = 0,
    ) -> RankingEntry:
        """Update rankings after a race result is recorded."""
        if prize_money < 0:
            raise RankingsError("Prize money cannot be negative.")
        entry = self.get_entry(member_name)
        points = self.points_for_position(position)
        entry.races_completed += 1
        entry.points += points
        entry.reputation += reputation_points + points + (prize_money // 100)
        if position == 1:
            entry.wins += 1
        return entry

    def leaderboard(self) -> list[RankingEntry]:
        """Return ranking entries ordered by points and reputation."""
        return sorted(
            self._rankings.values(),
            key=lambda entry: (entry.points, entry.reputation, entry.wins),
            reverse=True,
        )
