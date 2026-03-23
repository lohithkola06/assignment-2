"""Shared data models for the StreetRace Manager system."""

from dataclasses import dataclass, field


@dataclass
class CrewMember:
    """Represent a crew member and their tracked roles and skills."""

    name: str
    roles: set[str] = field(default_factory=set)
    skills: dict[str, int] = field(default_factory=dict)
    active: bool = True


@dataclass
class Car:
    """Represent a race car tracked by the inventory module."""

    car_id: str
    model: str
    available: bool = True
    damaged: bool = False
    assigned_race_id: str | None = None


@dataclass
class Race:
    """Represent a race event and its current assignment state."""

    race_id: str
    name: str
    prize_money: int
    driver_name: str | None = None
    car_id: str | None = None
    status: str = "planned"


@dataclass
class RaceResult:
    """Represent the final recorded result of a completed race."""

    race_id: str
    driver_name: str
    car_id: str
    position: int
    prize_money: int
    reputation_points: int
    car_damaged: bool = False
    notes: str = ""


@dataclass
class Mission:
    """Represent a mission that requires a specific crew combination."""

    mission_id: str
    mission_type: str
    required_roles: list[str]
    assigned_crew: list[str] = field(default_factory=list)
    target_car_id: str | None = None
    required_tools: list[str] = field(default_factory=list)
    required_parts: dict[str, int] = field(default_factory=dict)
    status: str = "planned"


@dataclass
class RankingEntry:
    """Represent ranking and reputation data for a crew member."""

    member_name: str
    races_completed: int = 0
    wins: int = 0
    points: int = 0
    reputation: int = 0


@dataclass
class InventoryState:
    """Represent the inventory state shared across modules."""

    cash_balance: int = 0
    cars: dict[str, Car] = field(default_factory=dict)
    parts: dict[str, int] = field(default_factory=dict)
    tools: dict[str, int] = field(default_factory=dict)
