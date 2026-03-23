"""Rankings and reputation module for StreetRace Manager."""


class RankingsService:
    """Maintain a simple leaderboard and reputation table."""

    def __init__(self, rankings):
        self._rankings = rankings
