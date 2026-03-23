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
