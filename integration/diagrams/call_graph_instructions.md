# StreetRace Manager Call Graph Instructions

Use this file as the source for the hand-drawn call graph image. The final graph should focus on function-to-function flow, especially the cross-module calls that the integration tests exercise.

## 1. Main functions by module

### `registration.py`
- `RegistrationService.register_member(name, role=None)`
- `RegistrationService.list_members()`
- `RegistrationService.is_registered(name)`
- `RegistrationService.get_member(name)`

### `crew_management.py`
- `CrewManagementService.assign_role(member_name, role, skill_level=1)`
- `CrewManagementService.update_skill(member_name, role, skill_level)`
- `CrewManagementService.has_role(member_name, role)`
- `CrewManagementService.get_skill(member_name, role)`
- `CrewManagementService.members_with_role(role)`
- `CrewManagementService.ensure_roles_available(required_roles, crew_names=None)`

### `inventory.py`
- `InventoryService.get_cash_balance()`
- `InventoryService.add_cash(amount)`
- `InventoryService.deduct_cash(amount)`
- `InventoryService.add_car(car_id, model)`
- `InventoryService.get_car(car_id)`
- `InventoryService.list_available_cars()`
- `InventoryService.add_part(part_name, quantity)`
- `InventoryService.add_tool(tool_name, quantity=1)`
- `InventoryService.part_count(part_name)`
- `InventoryService.tool_count(tool_name)`
- `InventoryService.require_tools(required_tools)`
- `InventoryService.require_parts(required_parts)`
- `InventoryService.use_part(part_name, quantity)`
- `InventoryService.reserve_car(car_id, race_id)`
- `InventoryService.release_car(car_id)`
- `InventoryService.mark_car_damaged(car_id)`
- `InventoryService.repair_car(car_id)`

### `race_management.py`
- `RaceManagementService.create_race(race_id, name, prize_money)`
- `RaceManagementService.get_race(race_id)`
- `RaceManagementService.enter_race(race_id, driver_name, car_id)`

### `results.py`
- `ResultsService.get_result(race_id)`
- `ResultsService.record_result(race_id, position, prize_money=None, car_damaged=False, notes="")`

### `mission_planning.py`
- `MissionPlanningService.create_mission(mission_id, mission_type, required_roles, target_car_id=None, required_tools=None, required_parts=None)`
- `MissionPlanningService.get_mission(mission_id)`
- `MissionPlanningService.start_mission(mission_id, assigned_crew)`
- `MissionPlanningService.complete_mission(mission_id)`

### `garage.py`
- `GarageService.inspect_car(car_id)`
- `GarageService.create_repair_mission(mission_id, car_id, assigned_crew, required_parts=None, required_tools=None)`
- `GarageService.repair_car(car_id, mechanic_name, required_parts=None, required_tools=None)`

### `rankings.py`
- `RankingsService.points_for_position(position)`
- `RankingsService.get_entry(member_name)`
- `RankingsService.record_race_result(member_name, position, prize_money, reputation_points=0)`
- `RankingsService.leaderboard()`

### `system.py`
- `StreetRaceSystem.register_member(...)`
- `StreetRaceSystem.assign_role(...)`
- `StreetRaceSystem.update_skill(...)`
- `StreetRaceSystem.add_car(...)`
- `StreetRaceSystem.add_part(...)`
- `StreetRaceSystem.add_tool(...)`
- `StreetRaceSystem.add_cash(...)`
- `StreetRaceSystem.create_race(...)`
- `StreetRaceSystem.enter_race(...)`
- `StreetRaceSystem.record_race_result(...)`
- `StreetRaceSystem.create_mission(...)`
- `StreetRaceSystem.start_mission(...)`
- `StreetRaceSystem.complete_mission(...)`
- `StreetRaceSystem.create_repair_mission(...)`
- `StreetRaceSystem.repair_car(...)`
- `StreetRaceSystem.leaderboard()`

### `cli.py`
- `main()`

## 2. Cross-module call relationships

### System bootstrap
- `cli.main()`
  - calls `StreetRaceSystem.__init__()`
  - `StreetRaceSystem.__init__()` creates:
    - `RegistrationService`
    - `CrewManagementService`
    - `InventoryService`
    - `RankingsService`
    - `RaceManagementService`
    - `ResultsService`
    - `MissionPlanningService`
    - `GarageService`

### Registration to role assignment flow
- `StreetRaceSystem.register_member()`
  - calls `RegistrationService.register_member()`
- `StreetRaceSystem.assign_role()`
  - calls `CrewManagementService.assign_role()`
  - `CrewManagementService.assign_role()`
    - calls `RegistrationService.get_member()`

### Race entry flow
- `StreetRaceSystem.create_race()`
  - calls `RaceManagementService.create_race()`
- `StreetRaceSystem.enter_race()`
  - calls `RaceManagementService.enter_race()`
- `RaceManagementService.enter_race()`
  - calls `RegistrationService.get_member()`
  - calls `CrewManagementService.has_role()`
    - `CrewManagementService.has_role()`
      - calls `RegistrationService.is_registered()`
      - calls `RegistrationService.get_member()`
  - calls `InventoryService.reserve_car()`
    - `InventoryService.reserve_car()`
      - calls `InventoryService.get_car()`

### Results and inventory update flow
- `StreetRaceSystem.record_race_result()`
  - calls `ResultsService.record_result()`
- `ResultsService.record_result()`
  - calls `RaceManagementService.get_race()`
  - calls `RankingsService.points_for_position()`
  - calls `InventoryService.add_cash()` when prize money is positive
  - calls `InventoryService.mark_car_damaged()` when damage is reported
  - calls `InventoryService.release_car()`
  - calls `RankingsService.record_race_result()`
    - `RankingsService.record_race_result()`
      - calls `RankingsService.get_entry()`
      - calls `RankingsService.points_for_position()`

### Mission validation flow
- `StreetRaceSystem.create_mission()`
  - calls `MissionPlanningService.create_mission()`
- `StreetRaceSystem.start_mission()`
  - calls `MissionPlanningService.start_mission()`
- `MissionPlanningService.start_mission()`
  - calls `MissionPlanningService.get_mission()`
  - calls `CrewManagementService.ensure_roles_available()`
    - this may call `RegistrationService.get_member()`
  - calls `InventoryService.require_tools()`
  - calls `InventoryService.require_parts()`
  - if the mission targets a damaged car:
    - calls `InventoryService.get_car()`
    - calls `CrewManagementService.ensure_roles_available(["mechanic"], assigned_crew)`

### Garage repair flow
- `StreetRaceSystem.create_repair_mission()`
  - calls `GarageService.create_repair_mission()`
- `GarageService.create_repair_mission()`
  - calls `MissionPlanningService.create_mission()`
  - calls `MissionPlanningService.start_mission()`
- `StreetRaceSystem.repair_car()`
  - calls `GarageService.repair_car()`
- `GarageService.repair_car()`
  - calls `InventoryService.get_car()`
  - calls `CrewManagementService.has_role()`
  - calls `InventoryService.require_tools()`
  - calls `InventoryService.require_parts()`
  - calls `InventoryService.use_part()` for each required part
  - calls `InventoryService.repair_car()`

### Leaderboard flow
- `StreetRaceSystem.leaderboard()`
  - calls `RankingsService.leaderboard()`

## 3. Compact ASCII call graph

```text
cli.main
  -> StreetRaceSystem.__init__
     -> RegistrationService
     -> CrewManagementService
     -> InventoryService
     -> RankingsService
     -> RaceManagementService
     -> ResultsService
     -> MissionPlanningService
     -> GarageService

StreetRaceSystem.register_member -> RegistrationService.register_member
StreetRaceSystem.assign_role -> CrewManagementService.assign_role
  -> RegistrationService.get_member

StreetRaceSystem.create_race -> RaceManagementService.create_race
StreetRaceSystem.enter_race -> RaceManagementService.enter_race
  -> RegistrationService.get_member
  -> CrewManagementService.has_role
     -> RegistrationService.is_registered
     -> RegistrationService.get_member
  -> InventoryService.reserve_car
     -> InventoryService.get_car

StreetRaceSystem.record_race_result -> ResultsService.record_result
  -> RaceManagementService.get_race
  -> RankingsService.points_for_position
  -> InventoryService.add_cash
  -> InventoryService.mark_car_damaged
  -> InventoryService.release_car
  -> RankingsService.record_race_result
     -> RankingsService.get_entry
     -> RankingsService.points_for_position

StreetRaceSystem.create_mission -> MissionPlanningService.create_mission
StreetRaceSystem.start_mission -> MissionPlanningService.start_mission
  -> MissionPlanningService.get_mission
  -> CrewManagementService.ensure_roles_available
     -> RegistrationService.get_member
  -> InventoryService.require_tools
  -> InventoryService.require_parts
  -> InventoryService.get_car
  -> CrewManagementService.ensure_roles_available(["mechanic"])

StreetRaceSystem.create_repair_mission -> GarageService.create_repair_mission
  -> MissionPlanningService.create_mission
  -> MissionPlanningService.start_mission

StreetRaceSystem.repair_car -> GarageService.repair_car
  -> InventoryService.get_car
  -> CrewManagementService.has_role
  -> InventoryService.require_tools
  -> InventoryService.require_parts
  -> InventoryService.use_part
  -> InventoryService.repair_car

StreetRaceSystem.leaderboard -> RankingsService.leaderboard
```

## 4. Hand-drawing instructions

1. Put `StreetRaceSystem` in the center because it is the facade that all high-level flows go through.
2. Draw the core modules around it: Registration, Crew Management, Inventory, Race Management, Results, Mission Planning.
3. Draw the two extra modules, Garage and Rankings, beside Results and Mission Planning because they are linked to those flows.
4. Use arrows for the major integration paths:
   - registration/role assignment
   - race entry
   - race result and cash update
   - mission validation
   - damaged-car repair
   - leaderboard update
5. Keep helper methods such as `get_member`, `get_car`, and `ensure_roles_available` as smaller nodes or labels near the module where they belong.
6. After drawing it by hand, insert a clear photo of that drawing into the final submission/report.
