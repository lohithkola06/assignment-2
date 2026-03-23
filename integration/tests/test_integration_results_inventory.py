"""Integration tests for results and inventory flows."""

from integration.code.system import StreetRaceSystem


def test_recording_race_result_updates_cash_and_rankings(
    entered_race_system: StreetRaceSystem,
):
    """Completing a race should update cash, rankings, and race status together."""
    result = entered_race_system.record_race_result("race-1", position=1)
    ranking = entered_race_system.rankings_service.get_entry("Nova")
    leaderboard = entered_race_system.leaderboard()
    car = entered_race_system.inventory.get_car("R-7")
    race = entered_race_system.race_management.get_race("race-1")

    assert result.prize_money == 500
    assert entered_race_system.inventory.get_cash_balance() == 500
    assert ranking.wins == 1
    assert ranking.points == 10
    assert leaderboard[0].member_name == "Nova"
    assert race.status == "completed"
    assert car.available is True
    assert car.damaged is False


def test_recording_damaged_race_result_keeps_car_unavailable_for_next_race(
    entered_race_system: StreetRaceSystem,
):
    """A damaged car should remain unavailable after race completion."""
    entered_race_system.record_race_result("race-1", position=2, car_damaged=True)
    car = entered_race_system.inventory.get_car("R-7")

    assert car.damaged is True
    assert car.available is False
