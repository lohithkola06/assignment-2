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

    def record_race_result(
        self,
        race_id: str,
        position: int,
        prize_money: int | None = None,
        car_damaged: bool = False,
        notes: str = "",
    ):
        """Record a race result through the facade."""
        return self.results.record_result(
            race_id,
            position,
            prize_money=prize_money,
            car_damaged=car_damaged,
            notes=notes,
        )

    def create_mission(
        self,
        mission_id: str,
        mission_type: str,
        required_roles: list[str],
        target_car_id: str | None = None,
        required_tools: list[str] | None = None,
        required_parts: dict[str, int] | None = None,
    ):
        """Create a mission through the facade."""
        return self.mission_planning.create_mission(
            mission_id,
            mission_type,
            required_roles,
            target_car_id=target_car_id,
            required_tools=required_tools,
            required_parts=required_parts,
        )

    def start_mission(self, mission_id: str, assigned_crew: list[str]):
        """Start a mission through the facade."""
        return self.mission_planning.start_mission(mission_id, assigned_crew)

    def complete_mission(self, mission_id: str):
        """Complete a mission through the facade."""
        return self.mission_planning.complete_mission(mission_id)

    def create_repair_mission(
        self,
        mission_id: str,
        car_id: str,
        assigned_crew: list[str],
        required_parts: dict[str, int] | None = None,
        required_tools: list[str] | None = None,
    ):
        """Create and start a repair mission through the facade."""
        return self.garage.create_repair_mission(
            mission_id,
            car_id,
            assigned_crew,
            required_parts=required_parts,
            required_tools=required_tools,
        )

    def repair_car(
        self,
        car_id: str,
        mechanic_name: str,
        required_parts: dict[str, int] | None = None,
        required_tools: list[str] | None = None,
    ):
        """Repair a car through the facade."""
        return self.garage.repair_car(
            car_id,
            mechanic_name,
            required_parts=required_parts,
            required_tools=required_tools,
        )

    def leaderboard(self):
        """Return the current leaderboard through the facade."""
        return self.rankings_service.leaderboard()
