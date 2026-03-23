"""White-box tests for game state transitions, cards, and turn flow."""

from moneypoly.config import GO_SALARY, INCOME_TAX_AMOUNT, JAIL_FINE
from moneypoly.game import Game
from moneypoly.property import Property


def test_handle_jail_turn_using_card_releases_player_and_moves(monkeypatch):
    """A jail-free card should be consumed before asking for a fine."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    player.in_jail = True
    player.get_out_of_jail_cards = 1
    moves = []

    monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _prompt: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game, "_move_and_resolve", lambda current, steps: moves.append((current, steps)))

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.jail_turns == 0
    assert player.get_out_of_jail_cards == 0
    assert moves == [(player, 4)]


def test_handle_jail_turn_paying_fine_deducts_player_balance(monkeypatch):
    """Voluntarily paying the jail fine should actually charge the player."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    player.in_jail = True
    starting_balance = player.balance
    starting_bank = game.bank.get_balance()

    monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _prompt: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 3)
    monkeypatch.setattr(game.dice, "describe", lambda: "1 + 2 = 3")
    monkeypatch.setattr(game, "_move_and_resolve", lambda _player, _steps: None)

    game._handle_jail_turn(player)

    assert player.balance == starting_balance - JAIL_FINE
    assert game.bank.get_balance() == starting_bank + JAIL_FINE
    assert player.in_jail is False


def test_apply_card_move_to_resolves_destination_property(monkeypatch):
    """Move-to cards should continue into the destination tile logic."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    prop = game.board.get_property_at(39)
    handled = []

    player.position = 35
    monkeypatch.setattr(game, "_handle_property_tile", lambda current, tile: handled.append((current, tile)))

    game._apply_card(
        player,
        {"description": "Advance to Boardwalk.", "action": "move_to", "value": 39},
    )

    assert player.position == 39
    assert handled == [(player, prop)]


def test_apply_card_birthday_collects_only_from_players_with_enough_cash():
    """Birthday cards should skip players who cannot cover the required amount."""
    game = Game(["Alice", "Bob", "Cara"])
    player = game.players[0]
    other_1 = game.players[1]
    other_2 = game.players[2]

    other_1.balance = 25
    other_2.balance = 5

    game._apply_card(
        player,
        {"description": "Birthday.", "action": "birthday", "value": 10},
    )

    assert player.balance == 1510
    assert other_1.balance == 15
    assert other_2.balance == 5


def test_move_and_resolve_sends_player_to_jail():
    """Landing on the go-to-jail tile should update jail state immediately."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    player.position = 29

    game._move_and_resolve(player, 1)

    assert player.in_jail is True
    assert player.position == 10


def test_move_and_resolve_handles_railroad_property_branch(monkeypatch):
    """The railroad branch should invoke property handling when a tile exists."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    railroad = Property("Reading Railroad", 5, 200, 25)
    handled = []

    def fake_move(_steps):
        player.position = 5
        return 5

    monkeypatch.setattr(player, "move", fake_move)
    monkeypatch.setattr(game.board, "get_tile_type", lambda _position: "railroad")
    monkeypatch.setattr(game.board, "get_property_at", lambda _position: railroad)
    monkeypatch.setattr(game, "_handle_property_tile", lambda current, tile: handled.append((current, tile)))
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _player: None)

    game._move_and_resolve(player, 5)

    assert handled == [(player, railroad)]


def test_find_winner_returns_highest_net_worth_player():
    """Winner selection should prefer the richest remaining player."""
    game = Game(["Alice", "Bob"])
    game.players[0].balance = 100
    game.players[1].balance = 300

    assert game.find_winner() is game.players[1]


def test_play_turn_after_bankruptcy_advances_to_next_survivor(monkeypatch):
    """Eliminating the current player should not skip the next active player."""
    game = Game(["Alice", "Bob", "Cara"])
    game.current_index = 1
    current = game.current_player()
    current.balance = 100

    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game.dice, "is_doubles", lambda: False)
    game.dice.doubles_streak = 0

    game.play_turn()

    assert current not in game.players
    assert game.current_player().name == "Cara"
    assert INCOME_TAX_AMOUNT > 0


def test_play_turn_keeps_same_player_after_non_terminal_doubles(monkeypatch):
    """Rolling doubles without reaching the third streak should grant another turn."""
    game = Game(["Alice", "Bob"])
    starting_index = game.current_index

    monkeypatch.setattr(game.dice, "roll", lambda: 3)
    monkeypatch.setattr(game.dice, "describe", lambda: "1 + 2 = 3")
    monkeypatch.setattr(game.dice, "is_doubles", lambda: True)
    game.dice.doubles_streak = 1
    monkeypatch.setattr(game.board, "get_tile_type", lambda _position: "blank")

    game.play_turn()

    assert game.current_index == starting_index


def test_play_turn_sends_player_to_jail_after_third_doubles(monkeypatch):
    """Three consecutive doubles should end the turn with a jail move."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()

    monkeypatch.setattr(game.dice, "roll", lambda: 8)
    monkeypatch.setattr(game.dice, "describe", lambda: "4 + 4 = 8")
    game.dice.doubles_streak = 3

    game.play_turn()

    assert player.in_jail is True
    assert player.position == 10


def test_apply_card_collects_go_salary_when_wrapping():
    """Move-to cards should still award the go salary when wrapping around the board."""
    game = Game(["Alice", "Bob"])
    player = game.current_player()
    player.position = 35

    game._apply_card(
        player,
        {"description": "Advance to Go.", "action": "move_to", "value": 0},
    )

    assert player.position == 0
    assert player.balance == 1500 + GO_SALARY
