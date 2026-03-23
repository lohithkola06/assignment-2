"""White-box tests for dice branches and randomness boundaries."""

from moneypoly.dice import Dice


def test_roll_uses_standard_six_sided_bounds(monkeypatch):
    """The dice should request values from 1 through 6 on both rolls."""
    calls = []
    sequence = iter([6, 6])

    def fake_randint(low, high):
        calls.append((low, high))
        return next(sequence)

    monkeypatch.setattr("moneypoly.dice.random.randint", fake_randint)
    dice = Dice()

    total = dice.roll()

    assert calls == [(1, 6), (1, 6)]
    assert total == 12
    assert dice.doubles_streak == 1


def test_doubles_streak_increments_and_resets(monkeypatch):
    """Consecutive doubles should increment the streak and non-doubles should clear it."""
    sequence = iter([3, 3, 2, 4])

    monkeypatch.setattr(
        "moneypoly.dice.random.randint",
        lambda _low, _high: next(sequence),
    )
    dice = Dice()

    dice.roll()
    assert dice.doubles_streak == 1

    dice.roll()
    assert dice.doubles_streak == 0


def test_describe_marks_doubles_and_shows_total():
    """The describe helper should expose the last dice state clearly."""
    dice = Dice()
    dice.die1 = 2
    dice.die2 = 2

    assert dice.describe() == "2 + 2 = 4 (DOUBLES)"
