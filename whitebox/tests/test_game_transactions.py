"""White-box tests for transactional game operations."""

import pytest

from moneypoly.config import AUCTION_MIN_INCREMENT
from moneypoly.game import Game


def test_game_requires_at_least_two_players():
    """The game setup should reject single-player sessions."""
    with pytest.raises(ValueError):
        Game(["Solo"])


def test_buy_property_allows_exact_balance_purchase():
    """A player should be able to spend their full balance on a property."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    prop = game.board.get_property_at(1)
    player.balance = prop.price

    assert game.buy_property(player, prop) is True
    assert player.balance == 0
    assert prop.owner is player
    assert prop in player.properties


def test_pay_rent_transfers_money_to_owner():
    """Rent payment should debit the visitor and credit the owner."""
    game = Game(["Alice", "Bob"])
    owner = game.players[0]
    visitor = game.players[1]
    prop = game.board.get_property_at(1)
    rent = prop.base_rent

    prop.owner = owner
    owner.add_property(prop)
    game.pay_rent(visitor, prop)

    assert visitor.balance == 1500 - rent
    assert owner.balance == 1500 + rent


def test_trade_moves_cash_to_seller_and_transfers_property():
    """A successful trade should move both the property and the agreed cash."""
    game = Game(["Alice", "Bob"])
    seller = game.players[0]
    buyer = game.players[1]
    prop = game.board.get_property_at(3)

    prop.owner = seller
    seller.add_property(prop)

    assert game.trade(seller, buyer, prop, 120) is True
    assert prop.owner is buyer
    assert prop not in seller.properties
    assert prop in buyer.properties
    assert seller.balance == 1620
    assert buyer.balance == 1380


def test_unmortgage_keeps_property_mortgaged_when_owner_cannot_pay():
    """Failed unmortgage attempts should not mutate the mortgage state."""
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)

    prop.owner = player
    player.add_property(prop)
    game.mortgage_property(player, prop)
    player.balance = 1

    assert game.unmortgage_property(player, prop) is False
    assert prop.is_mortgaged is True


def test_auction_ignores_invalid_bids_and_awards_highest_valid_bid(monkeypatch):
    """The auction loop should reject low and unaffordable bids before picking a winner."""
    game = Game(["Alice", "Bob", "Cara"])
    prop = game.board.get_property_at(1)
    bids = iter([AUCTION_MIN_INCREMENT - 1, 5000, 40])

    monkeypatch.setattr(
        "moneypoly.game.ui.safe_int_input",
        lambda _prompt, default=0: next(bids),
    )

    game.auction_property(prop)

    assert prop.owner is game.players[2]
    assert game.players[2].balance == 1460
