"""Facade that wires all StreetRace Manager modules together."""

from .crew_management import CrewManagementService
from .garage import GarageService
from .inventory import InventoryService
from .mission_planning import MissionPlanningService
from .models import InventoryState
from .race_management import RaceManagementService
from .rankings import RankingsService
from .registration import RegistrationService
from .results import ResultsService


class StreetRaceSystem:
    """Provide a single integration-oriented entry point for the modules."""

    def __init__(self):
        self.crew_members = {}
        self.races = {}
        self.race_results = {}
        self.missions = {}
        self.rankings = {}
        self.inventory_state = InventoryState()

        self.registration = RegistrationService(self.crew_members)
        self.crew_management = CrewManagementService(self.registration)
        self.inventory = InventoryService(self.inventory_state)
        self.rankings_service = RankingsService(self.rankings)
        self.race_management = RaceManagementService(
            self.races,
            self.registration,
            self.crew_management,
            self.inventory,
        )
        self.results = ResultsService(
            self.race_results,
            self.race_management,
            self.inventory,
            self.rankings_service,
        )
        self.mission_planning = MissionPlanningService(
            self.missions,
            self.registration,
            self.crew_management,
            self.inventory,
        )
        self.garage = GarageService(
            self.inventory,
            self.mission_planning,
            self.crew_management,
        )

    def register_member(self, name: str, role: str | None = None):
        """Register a new crew member through the facade."""
        return self.registration.register_member(name, role)

    def assign_role(self, member_name: str, role: str, skill_level: int = 1):
        """Assign a crew role through the facade."""
        return self.crew_management.assign_role(member_name, role, skill_level)

    def update_skill(self, member_name: str, role: str, skill_level: int):
        """Update a crew member skill through the facade."""
        return self.crew_management.update_skill(member_name, role, skill_level)

    def add_car(self, car_id: str, model: str):
        """Add a car through the facade."""
        return self.inventory.add_car(car_id, model)

    def add_part(self, part_name: str, quantity: int):
        """Add spare parts through the facade."""
        return self.inventory.add_part(part_name, quantity)

    def add_tool(self, tool_name: str, quantity: int = 1):
        """Add tools through the facade."""
        return self.inventory.add_tool(tool_name, quantity)

    def add_cash(self, amount: int):
        """Add cash through the facade."""
        return self.inventory.add_cash(amount)

    def create_race(self, race_id: str, name: str, prize_money: int):
        """Create a race through the facade."""
        return self.race_management.create_race(race_id, name, prize_money)

    def enter_race(self, race_id: str, driver_name: str, car_id: str):
        """Enter a driver and car into a race through the facade."""
        return self.race_management.enter_race(race_id, driver_name, car_id)
