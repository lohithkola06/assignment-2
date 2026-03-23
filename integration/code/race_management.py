"""Race management module for StreetRace Manager."""

from .exceptions import InventoryError, RaceError, RegistrationError, ValidationError
from .models import Race


class RaceManagementService:
    """Create races and enter drivers with eligible cars."""

    def __init__(self, races, registration_service, crew_service, inventory_service):
        self._races = races
        self._registration_service = registration_service
        self._crew_service = crew_service
        self._inventory_service = inventory_service

    @staticmethod
    def _normalize_race_id(race_id: str) -> str:
        normalized = race_id.strip()
        if not normalized:
            raise ValidationError("Race ID cannot be empty.")
        return normalized

    def create_race(self, race_id: str, name: str, prize_money: int) -> Race:
        """Create a race with the given name and prize amount."""
        normalized_race_id = self._normalize_race_id(race_id)
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Race name cannot be empty.")
        if prize_money < 0:
            raise ValidationError("Prize money cannot be negative.")
        if normalized_race_id in self._races:
            raise RaceError(f"Race '{normalized_race_id}' already exists.")
        race = Race(
            race_id=normalized_race_id,
            name=normalized_name,
            prize_money=prize_money,
        )
        self._races[normalized_race_id] = race
        return race

    def get_race(self, race_id: str) -> Race:
        """Return a created race or raise a race error."""
        normalized_race_id = self._normalize_race_id(race_id)
        try:
            return self._races[normalized_race_id]
        except KeyError as exc:
            raise RaceError(f"Race '{normalized_race_id}' does not exist.") from exc

    def enter_race(self, race_id: str, driver_name: str, car_id: str) -> Race:
        """Enter a registered driver and an available car into a race."""
        race = self.get_race(race_id)
        if race.driver_name is not None:
            raise RaceError(f"Race '{race.race_id}' already has an assigned driver.")

        try:
            driver = self._registration_service.get_member(driver_name)
        except RegistrationError as exc:
            raise RaceError(str(exc)) from exc

        if not self._crew_service.has_role(driver.name, "driver"):
            raise RaceError(f"{driver.name} does not hold the driver role.")

        try:
            reserved_car = self._inventory_service.reserve_car(car_id, race.race_id)
        except InventoryError as exc:
            raise RaceError(str(exc)) from exc

        race.driver_name = driver.name
        race.car_id = reserved_car.car_id
        race.status = "ready"
        return race
