"""White-box tests for board lookup and ownership helpers."""

from moneypoly.board import Board
from moneypoly.player import Player


def test_get_tile_type_handles_special_property_and_blank_tiles():
    """Tile classification should distinguish the main board branches."""
    board = Board()

    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(12) == "blank"


def test_is_purchasable_requires_unowned_and_unmortgaged_property():
    """A property is purchasable only while unowned and not mortgaged."""
    board = Board()
    player = Player("Alice")
    prop = board.get_property_at(1)

    assert board.is_purchasable(1) is True

    prop.owner = player
    assert board.is_purchasable(1) is False

    prop.owner = None
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False
    assert board.is_purchasable(0) is False


def test_board_ownership_helpers_track_owner_changes():
    """Ownership helper methods should mirror property state."""
    board = Board()
    player = Player("Bob")
    prop = board.get_property_at(3)

    prop.owner = player
    player.add_property(prop)

    assert board.properties_owned_by(player) == [prop]
    assert prop not in board.unowned_properties()
