"""Inventory module for StreetRace Manager."""

from .exceptions import InventoryError, ValidationError
from .models import Car


class InventoryService:
    """Track cash, cars, tools, and spare parts."""

    def __init__(self, state):
        self._state = state

    @staticmethod
    def _normalize_name(name: str, label: str) -> str:
        normalized = name.strip().lower()
        if not normalized:
            raise ValidationError(f"{label} cannot be empty.")
        return normalized

    @staticmethod
    def _normalize_car_id(car_id: str) -> str:
        normalized = car_id.strip()
        if not normalized:
            raise ValidationError("Car ID cannot be empty.")
        return normalized

    @staticmethod
    def _validate_quantity(quantity: int, label: str) -> int:
        if quantity <= 0:
            raise ValidationError(f"{label} must be greater than zero.")
        return quantity

    def get_cash_balance(self) -> int:
        """Return the current cash balance tracked in inventory."""
        return self._state.cash_balance

    def add_cash(self, amount: int) -> int:
        """Add prize money or funding to the cash balance."""
        validated_amount = self._validate_quantity(amount, "Cash amount")
        self._state.cash_balance += validated_amount
        return self._state.cash_balance

    def deduct_cash(self, amount: int) -> int:
        """Spend cash from inventory while preventing negative balance."""
        validated_amount = self._validate_quantity(amount, "Cash amount")
        if validated_amount > self._state.cash_balance:
            raise InventoryError("Not enough cash available.")
        self._state.cash_balance -= validated_amount
        return self._state.cash_balance

    def add_car(self, car_id: str, model: str) -> Car:
        """Add a new car to inventory."""
        normalized_car_id = self._normalize_car_id(car_id)
        normalized_model = model.strip()
        if not normalized_model:
            raise ValidationError("Car model cannot be empty.")
        if normalized_car_id in self._state.cars:
            raise InventoryError(f"Car '{normalized_car_id}' already exists.")
        car = Car(car_id=normalized_car_id, model=normalized_model)
        self._state.cars[normalized_car_id] = car
        return car

    def get_car(self, car_id: str) -> Car:
        """Return a car from inventory or raise an inventory error."""
        normalized_car_id = self._normalize_car_id(car_id)
        try:
            return self._state.cars[normalized_car_id]
        except KeyError as exc:
            raise InventoryError(f"Car '{normalized_car_id}' is not in inventory.") from exc

    def list_available_cars(self) -> list[Car]:
        """Return cars that are available and not damaged."""
        return [
            car
            for car in self._state.cars.values()
            if car.available and not car.damaged
        ]

    def add_part(self, part_name: str, quantity: int) -> int:
        """Add spare parts to inventory and return the updated quantity."""
        normalized_name = self._normalize_name(part_name, "Part name")
        validated_quantity = self._validate_quantity(quantity, "Part quantity")
        self._state.parts[normalized_name] = (
            self._state.parts.get(normalized_name, 0) + validated_quantity
        )
        return self._state.parts[normalized_name]

    def add_tool(self, tool_name: str, quantity: int = 1) -> int:
        """Add tools to inventory and return the updated quantity."""
        normalized_name = self._normalize_name(tool_name, "Tool name")
        validated_quantity = self._validate_quantity(quantity, "Tool quantity")
        self._state.tools[normalized_name] = (
            self._state.tools.get(normalized_name, 0) + validated_quantity
        )
        return self._state.tools[normalized_name]

    def part_count(self, part_name: str) -> int:
        """Return the stored quantity for a spare part."""
        normalized_name = self._normalize_name(part_name, "Part name")
        return self._state.parts.get(normalized_name, 0)

    def tool_count(self, tool_name: str) -> int:
        """Return the stored quantity for a tool."""
        normalized_name = self._normalize_name(tool_name, "Tool name")
        return self._state.tools.get(normalized_name, 0)

    def require_tools(self, required_tools: list[str]) -> None:
        """Ensure every requested tool exists in inventory."""
        for tool_name in required_tools:
            normalized_name = self._normalize_name(tool_name, "Tool name")
            if self._state.tools.get(normalized_name, 0) <= 0:
                raise InventoryError(f"Required tool '{normalized_name}' is unavailable.")

    def require_parts(self, required_parts: dict[str, int]) -> None:
        """Ensure the required spare parts exist in sufficient quantity."""
        for part_name, quantity in required_parts.items():
            normalized_name = self._normalize_name(part_name, "Part name")
            validated_quantity = self._validate_quantity(quantity, "Part quantity")
            if self._state.parts.get(normalized_name, 0) < validated_quantity:
                raise InventoryError(
                    f"Required part '{normalized_name}' is unavailable in sufficient quantity."
                )

    def use_part(self, part_name: str, quantity: int) -> int:
        """Consume spare parts and return the remaining quantity."""
        normalized_name = self._normalize_name(part_name, "Part name")
        validated_quantity = self._validate_quantity(quantity, "Part quantity")
        self.require_parts({normalized_name: validated_quantity})
        self._state.parts[normalized_name] -= validated_quantity
        return self._state.parts[normalized_name]

    def reserve_car(self, car_id: str, race_id: str) -> Car:
        """Reserve a car for a race after validating availability."""
        car = self.get_car(car_id)
        if car.damaged:
            raise InventoryError(f"Car '{car.car_id}' is damaged and unavailable.")
        if not car.available:
            raise InventoryError(f"Car '{car.car_id}' is already in use.")
        car.available = False
        car.assigned_race_id = race_id
        return car

    def release_car(self, car_id: str) -> Car:
        """Release a car after use and restore availability if it is not damaged."""
        car = self.get_car(car_id)
        car.assigned_race_id = None
        car.available = not car.damaged
        return car

    def mark_car_damaged(self, car_id: str) -> Car:
        """Mark a car as damaged and unavailable."""
        car = self.get_car(car_id)
        car.damaged = True
        car.available = False
        return car

    def repair_car(self, car_id: str) -> Car:
        """Restore a damaged car to a race-ready state."""
        car = self.get_car(car_id)
        car.damaged = False
        car.available = car.assigned_race_id is None
        return car
