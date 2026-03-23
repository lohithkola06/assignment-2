"""Blackbox tests for header validation and user scoping."""

from __future__ import annotations

import pytest

from .conftest import UNSET, QuickCartClient


def test_missing_roll_number_returns_401(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """User endpoints should reject requests without the required roll-number header."""

    response, payload = client.api_call(
        "GET",
        "/api/v1/profile",
        user_id=test_users["catalog"],
        include_roll=False,
    )

    assert response.status_code == 401
    assert payload["error"] == "Missing X-Roll-Number header"


def test_non_integer_roll_number_returns_400(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Roll-number validation should reject non-integer values."""

    response, payload = client.api_call(
        "GET",
        "/api/v1/profile",
        user_id=test_users["catalog"],
        headers={"X-Roll-Number": "not-a-number"},
        include_roll=False,
    )

    assert response.status_code == 400
    assert payload["error"] == "X-Roll-Number must be a valid integer"


def test_admin_endpoint_does_not_require_user_header(client: QuickCartClient) -> None:
    """Admin inspection endpoints stay accessible with only the roll-number header."""

    response, payload = client.api_call(
        "GET",
        "/api/v1/admin/users",
        user_id=None,
        expected_status=200,
    )

    assert isinstance(payload, list)
    assert response.status_code == 200


def test_missing_user_id_on_user_endpoint_returns_400(client: QuickCartClient) -> None:
    """User-scoped endpoints should reject requests that omit X-User-ID."""

    response, payload = client.api_call("GET", "/api/v1/profile", user_id=None)

    assert response.status_code == 400
    assert payload["error"] == "Missing X-User-ID header"


@pytest.mark.parametrize("bad_user_id", ["-1", "0"])
def test_non_positive_user_id_returns_400(client: QuickCartClient, bad_user_id: str) -> None:
    """User identifiers must be strictly positive integers."""

    response, payload = client.api_call("GET", "/api/v1/profile", user_id=UNSET, headers={"X-User-ID": bad_user_id})

    assert response.status_code == 400
    assert payload["error"] == "X-User-ID must be a valid positive integer"


def test_nonexistent_user_id_returns_404(client: QuickCartClient) -> None:
    """Requests for missing users should expose a not-found error."""

    response, payload = client.api_call("GET", "/api/v1/profile", user_id=999999)

    assert response.status_code == 404
    assert payload["error"] == "User not found"
