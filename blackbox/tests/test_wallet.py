"""Blackbox tests for wallet balance updates and payment behavior."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def test_get_wallet_balance_returns_numeric_value(client: QuickCartClient, wallet_user: int) -> None:
    """Wallet lookup should expose the current balance for the user."""

    _, payload = client.api_call("GET", "/api/v1/wallet", user_id=wallet_user, expected_status=200)

    assert "wallet_balance" in payload
    assert isinstance(payload["wallet_balance"], (int, float))


def test_wallet_add_money_updates_balance(client: QuickCartClient, wallet_user: int) -> None:
    """Adding money should increase the observable wallet balance by the same amount."""

    _, before = client.api_call("GET", "/api/v1/wallet", user_id=wallet_user, expected_status=200)
    _, payload = client.api_call(
        "POST",
        "/api/v1/wallet/add",
        user_id=wallet_user,
        json_body={"amount": 25},
        expected_status=200,
    )

    assert payload["wallet_balance"] == pytest.approx(before["wallet_balance"] + 25)


@pytest.mark.parametrize("amount", [0, -1, 100001])
def test_wallet_add_rejects_invalid_amounts(client: QuickCartClient, wallet_user: int, amount: int) -> None:
    """Wallet top-ups should reject non-positive amounts and values above the documented ceiling."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/wallet/add",
        user_id=wallet_user,
        json_body={"amount": amount},
    )

    assert response.status_code == 400
    assert payload["error"] == "Invalid amount"


@pytest.mark.xfail(reason="Observed defect: wallet pay deducts more than the requested amount.")
def test_wallet_pay_deducts_the_exact_requested_amount(client: QuickCartClient, wallet_user: int) -> None:
    """Wallet payments should reduce the balance by the exact requested amount."""

    _, before = client.api_call("GET", "/api/v1/wallet", user_id=wallet_user, expected_status=200)
    client.api_call(
        "POST",
        "/api/v1/wallet/add",
        user_id=wallet_user,
        json_body={"amount": 25},
        expected_status=200,
    )
    _, payload = client.api_call(
        "POST",
        "/api/v1/wallet/pay",
        user_id=wallet_user,
        json_body={"amount": 25},
        expected_status=200,
    )

    assert payload["wallet_balance"] == pytest.approx(before["wallet_balance"])


def test_wallet_pay_rejects_insufficient_balance(client: QuickCartClient, wallet_user: int) -> None:
    """Wallet payments should fail when the amount is larger than the balance."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/wallet/pay",
        user_id=wallet_user,
        json_body={"amount": 999999},
    )

    assert response.status_code == 400
    assert payload["error"] == "Insufficient balance"


def test_wallet_pay_rejects_non_positive_amount(client: QuickCartClient, wallet_user: int) -> None:
    """Wallet payments should reject zero or negative amounts."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/wallet/pay",
        user_id=wallet_user,
        json_body={"amount": 0},
    )

    assert response.status_code == 400
    assert payload["error"] == "Amount must be > 0"
