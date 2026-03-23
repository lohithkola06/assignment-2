"""White-box tests for property and property-group logic."""

from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


def test_group_ownership_requires_full_set_for_rent_bonus():
    """A rent bonus should apply only when the owner controls the whole group."""
    group = PropertyGroup("Brown", "brown")
    owner = Player("Alice")
    prop_1 = Property("Mediterranean Avenue", 1, 60, 2, group)
    Property("Baltic Avenue", 3, 60, 4, group)
    prop_1.owner = owner

    assert group.all_owned_by(owner) is False
    assert prop_1.get_rent() == 2


def test_complete_group_doubles_rent():
    """Owning all properties in a group should double the base rent."""
    group = PropertyGroup("Brown", "brown")
    owner = Player("Alice")
    prop_1 = Property("Mediterranean Avenue", 1, 60, 2, group)
    prop_2 = Property("Baltic Avenue", 3, 60, 4, group)
    prop_1.owner = owner
    prop_2.owner = owner

    assert group.all_owned_by(owner) is True
    assert prop_1.get_rent() == 4


def test_mortgage_and_unmortgage_toggle_state_and_cost():
    """Mortgage operations should flip state and return the correct cash values."""
    prop = Property("Boardwalk", 39, 400, 50)

    payout = prop.mortgage()
    cost = prop.unmortgage()

    assert payout == 200
    assert cost == 220
    assert prop.is_mortgaged is False


def test_owner_counts_aggregate_by_player():
    """Owner counts should tally how many properties each player holds in the group."""
    group = PropertyGroup("Brown", "brown")
    alice = Player("Alice")
    bob = Player("Bob")
    prop_1 = Property("Mediterranean Avenue", 1, 60, 2, group)
    prop_2 = Property("Baltic Avenue", 3, 60, 4, group)
    prop_1.owner = alice
    prop_2.owner = bob

    assert group.get_owner_counts() == {alice: 1, bob: 1}
