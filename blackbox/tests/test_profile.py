"""Blackbox tests for the profile endpoints."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def test_get_profile_returns_expected_fields(client: QuickCartClient, profile_user: int) -> None:
    """A valid user should be able to fetch a profile document."""

    _, payload = client.api_call("GET", "/api/v1/profile", user_id=profile_user, expected_status=200)

    assert payload["user_id"] == profile_user
    assert {"name", "email", "phone", "wallet_balance", "loyalty_points"} <= payload.keys()


def test_put_profile_accepts_valid_update(client: QuickCartClient, profile_user: int, unique_suffix: str) -> None:
    """Valid profile updates should persist and be observable through GET /profile."""

    new_name = f"Box Tester {unique_suffix}"
    client.api_call(
        "PUT",
        "/api/v1/profile",
        user_id=profile_user,
        json_body={"name": new_name, "phone": "9876543210"},
        expected_status=200,
    )

    _, payload = client.api_call("GET", "/api/v1/profile", user_id=profile_user, expected_status=200)

    assert payload["name"] == new_name
    assert payload["phone"] == "9876543210"


@pytest.mark.parametrize(
    ("name_value", "expected_message"),
    [
        ("A", "Name must be between 2 and 50 characters"),
        ("X" * 51, "Name must be between 2 and 50 characters"),
    ],
)
def test_put_profile_rejects_name_outside_documented_bounds(
    client: QuickCartClient,
    profile_user: int,
    name_value: str,
    expected_message: str,
) -> None:
    """Name boundaries are tested with short and long invalid values."""

    response, payload = client.api_call(
        "PUT",
        "/api/v1/profile",
        user_id=profile_user,
        json_body={"name": name_value, "phone": "9876543210"},
    )

    assert response.status_code == 400
    assert payload["error"] == expected_message


@pytest.mark.parametrize("phone_value", ["12345", "12345678901"])
def test_put_profile_rejects_invalid_phone_numbers(
    client: QuickCartClient,
    profile_user: int,
    phone_value: str,
) -> None:
    """Phone numbers must be exactly ten digits."""

    response, payload = client.api_call(
        "PUT",
        "/api/v1/profile",
        user_id=profile_user,
        json_body={"name": "Valid Profile", "phone": phone_value},
    )

    assert response.status_code == 400
    assert payload["error"] == "Phone must be exactly 10 digits"


@pytest.mark.xfail(reason="Observed defect: alphabetic characters are accepted in the phone field.")
def test_put_profile_rejects_non_digit_phone_numbers(client: QuickCartClient, profile_user: int) -> None:
    """The documented phone rule should reject non-digit characters."""

    response, payload = client.api_call(
        "PUT",
        "/api/v1/profile",
        user_id=profile_user,
        json_body={"name": "Valid Profile", "phone": "12345abcde"},
    )

    assert response.status_code == 400
    assert payload["error"] == "Phone must be exactly 10 digits"
