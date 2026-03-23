"""Inventory module for StreetRace Manager."""


class InventoryService:
    """Track cash, cars, tools, and spare parts."""

    def __init__(self, state):
        self._state = state
