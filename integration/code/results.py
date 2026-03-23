"""Results module for StreetRace Manager."""

from .exceptions import ResultsError, ValidationError
from .models import RaceResult


class ResultsService:
    """Record race outcomes and trigger cross-module updates."""

    def __init__(self, results, race_service, inventory_service, rankings_service):
        self._results = results
        self._race_service = race_service
        self._inventory_service = inventory_service
        self._rankings_service = rankings_service

    @staticmethod
    def _validate_position(position: int) -> int:
        if position <= 0:
            raise ValidationError("Race position must be a positive integer.")
        return position

    def get_result(self, race_id: str) -> RaceResult:
        """Return a stored race result by race ID."""
        try:
            return self._results[race_id]
        except KeyError as exc:
            raise ResultsError(f"No result has been recorded for race '{race_id}'.") from exc

    def record_result(
        self,
        race_id: str,
        position: int,
        prize_money: int | None = None,
        car_damaged: bool = False,
        notes: str = "",
    ) -> RaceResult:
        """Record a race result and update integrated system state."""
        validated_position = self._validate_position(position)
        race = self._race_service.get_race(race_id)
        if race.driver_name is None or race.car_id is None:
            raise ResultsError(f"Race '{race.race_id}' is missing a driver or car entry.")
        if race.status == "completed":
            raise ResultsError(f"Race '{race.race_id}' has already been completed.")

        actual_prize_money = race.prize_money if prize_money is None else prize_money
        if actual_prize_money < 0:
            raise ValidationError("Prize money cannot be negative.")

        reputation_points = self._rankings_service.points_for_position(validated_position)
        result = RaceResult(
            race_id=race.race_id,
            driver_name=race.driver_name,
            car_id=race.car_id,
            position=validated_position,
            prize_money=actual_prize_money,
            reputation_points=reputation_points,
            car_damaged=car_damaged,
            notes=notes,
        )
        self._results[race.race_id] = result

        if actual_prize_money > 0:
            self._inventory_service.add_cash(actual_prize_money)

        if car_damaged:
            self._inventory_service.mark_car_damaged(race.car_id)
        self._inventory_service.release_car(race.car_id)

        self._rankings_service.record_race_result(
            member_name=race.driver_name,
            position=validated_position,
            prize_money=actual_prize_money,
            reputation_points=reputation_points,
        )
        race.status = "completed"
        return result
