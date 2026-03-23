"""Results module for StreetRace Manager."""


class ResultsService:
    """Record race outcomes and trigger cross-module updates."""

    def __init__(self, results, race_service, inventory_service, rankings_service):
        self._results = results
        self._race_service = race_service
        self._inventory_service = inventory_service
        self._rankings_service = rankings_service
