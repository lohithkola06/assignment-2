"""Blackbox tests for loyalty-point retrieval and redemption."""

from __future__ import annotations

from .conftest import QuickCartClient


def test_get_loyalty_points_returns_current_value(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """The loyalty endpoint should expose the user's current points total."""

    _, payload = client.api_call(
        "GET",
        "/api/v1/loyalty",
        user_id=test_users["wallet_loyalty"],
        expected_status=200,
    )

    assert "loyalty_points" in payload
    assert isinstance(payload["loyalty_points"], int)


def test_redeem_valid_loyalty_points_reduces_balance(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Redeeming a valid amount should reduce the observable points balance."""

    user_id = test_users["wallet_loyalty"]
    _, before = client.api_call("GET", "/api/v1/loyalty", user_id=user_id, expected_status=200)
    _, payload = client.api_call(
        "POST",
        "/api/v1/loyalty/redeem",
        user_id=user_id,
        json_body={"points": 1},
        expected_status=200,
    )

    assert payload["loyalty_points"] == before["loyalty_points"] - 1


def test_redeem_rejects_amount_below_one(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Redeem requests below one point should fail validation."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/loyalty/redeem",
        user_id=test_users["wallet_loyalty"],
        json_body={"points": 0},
    )

    assert response.status_code == 400
    assert payload["error"] == "Points must be >= 1"


def test_redeem_rejects_more_than_available(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Users cannot redeem more loyalty points than they currently have."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/loyalty/redeem",
        user_id=test_users["wallet_loyalty"],
        json_body={"points": 999999},
    )

    assert response.status_code == 400
    assert payload["error"] == "Insufficient points"
