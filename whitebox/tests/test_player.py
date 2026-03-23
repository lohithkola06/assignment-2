"""White-box tests for player state and movement logic."""

import pytest

from moneypoly.config import GO_SALARY, STARTING_BALANCE
from moneypoly.player import Player
from moneypoly.property import Property


def test_money_operations_reject_negative_amounts():
    """Negative balance operations should fail fast."""
    player = Player("Alice")

    with pytest.raises(ValueError):
        player.add_money(-1)

    with pytest.raises(ValueError):
        player.deduct_money(-1)


def test_move_collects_go_salary_when_passing_go():
    """Passing go should award the salary even when the player does not land on zero."""
    player = Player("Alice")
    player.position = 39

    new_position = player.move(2)

    assert new_position == 1
    assert player.balance == STARTING_BALANCE + GO_SALARY


def test_move_collects_go_salary_when_landing_on_go():
    """Landing exactly on go should also award the salary."""
    player = Player("Alice")
    player.position = 39

    new_position = player.move(1)

    assert new_position == 0
    assert player.balance == STARTING_BALANCE + GO_SALARY


def test_net_worth_includes_owned_property_values():
    """Net worth should account for both cash and owned assets."""
    player = Player("Alice")
    prop = Property("Mediterranean Avenue", 1, 60, 2)

    player.add_property(prop)

    assert player.net_worth() == STARTING_BALANCE + 60


def test_go_to_jail_updates_position_and_flags():
    """Going to jail should relocate the player and reset jail turn state."""
    player = Player("Alice")
    player.jail_turns = 2

    player.go_to_jail()

    assert player.position == 10
    assert player.in_jail is True
    assert player.jail_turns == 0
