"""Blackbox tests for address management endpoints."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def test_add_valid_address_returns_created_object(client: QuickCartClient, address_user: int, unique_suffix: str) -> None:
    """A successful address POST should return the full created object."""

    payload = {
        "label": "HOME",
        "street": f"12 Test Lane {unique_suffix}",
        "city": "Pune",
        "pincode": "411001",
        "is_default": True,
    }
    _, body = client.api_call(
        "POST",
        "/api/v1/addresses",
        user_id=address_user,
        json_body=payload,
        expected_status=200,
    )

    assert body["message"] == "Address added successfully"
    assert body["address"]["label"] == payload["label"]
    assert body["address"]["street"] == payload["street"]
    assert body["address"]["city"] == payload["city"]
    assert body["address"]["pincode"] == payload["pincode"]
    assert body["address"]["is_default"] is True
    assert "address_id" in body["address"]


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        (
            {
                "label": "BAD",
                "street": "12345 Main Street",
                "city": "Pune",
                "pincode": "411001",
                "is_default": False,
            },
            "Label must be HOME, OFFICE, or OTHER",
        ),
        (
            {
                "label": "HOME",
                "street": "1234",
                "city": "Pune",
                "pincode": "411001",
                "is_default": False,
            },
            "Street must be between 5 and 100 characters",
        ),
        (
            {
                "label": "HOME",
                "street": "12345 Main Street",
                "city": "P",
                "pincode": "411001",
                "is_default": False,
            },
            "City must be between 2 and 50 characters",
        ),
        (
            {
                "label": "HOME",
                "street": "12345 Main Street",
                "city": "Pune",
                "pincode": "41100",
                "is_default": False,
            },
            "Pincode must be exactly 6 digits",
        ),
    ],
)
def test_add_address_rejects_invalid_field_values(
    client: QuickCartClient,
    address_user: int,
    payload: dict[str, object],
    expected_error: str,
) -> None:
    """Boundary and equivalence-class checks for address creation."""

    response, body = client.api_call(
        "POST",
        "/api/v1/addresses",
        user_id=address_user,
        json_body=payload,
    )

    assert response.status_code == 400
    assert body["error"] == expected_error


def test_update_address_only_changes_allowed_fields(client: QuickCartClient, address_user: int) -> None:
    """Street and default status may change, while immutable fields stay unchanged."""

    _, created = client.api_call(
        "POST",
        "/api/v1/addresses",
        user_id=address_user,
        json_body={
            "label": "HOME",
            "street": "111 Alpha Street",
            "city": "Pune",
            "pincode": "411001",
            "is_default": True,
        },
        expected_status=200,
    )
    address_id = created["address"]["address_id"]

    _, body = client.api_call(
        "PUT",
        f"/api/v1/addresses/{address_id}",
        user_id=address_user,
        json_body={
            "street": "333 Updated Road",
            "is_default": False,
            "label": "OTHER",
            "city": "Delhi",
            "pincode": "999999",
        },
        expected_status=200,
    )

    updated = body["address"]
    assert updated["street"] == "333 Updated Road"
    assert updated["is_default"] is False
    assert updated["label"] == "HOME"
    assert updated["city"] == "Pune"
    assert updated["pincode"] == "411001"


@pytest.mark.xfail(reason="Observed defect: adding a second default address leaves multiple defaults active.")
def test_only_one_default_address_exists_at_a_time(
    client: QuickCartClient,
    address_user: int,
    unique_suffix: str,
) -> None:
    """Adding a new default address should unset the previous default."""

    client.api_call(
        "POST",
        "/api/v1/addresses",
        user_id=address_user,
        json_body={
            "label": "HOME",
            "street": f"10 First Street {unique_suffix}",
            "city": "Pune",
            "pincode": "411001",
            "is_default": True,
        },
        expected_status=200,
    )
    client.api_call(
        "POST",
        "/api/v1/addresses",
        user_id=address_user,
        json_body={
            "label": "OFFICE",
            "street": f"20 Second Street {unique_suffix}",
            "city": "Hyderabad",
            "pincode": "500001",
            "is_default": True,
        },
        expected_status=200,
    )

    _, addresses = client.api_call("GET", "/api/v1/addresses", user_id=address_user, expected_status=200)
    default_count = sum(1 for address in addresses if address["is_default"])

    assert default_count == 1


def test_delete_missing_address_returns_404(client: QuickCartClient, address_user: int) -> None:
    """Deleting an unknown address id should return a not-found error."""

    response, body = client.api_call(
        "DELETE",
        "/api/v1/addresses/999999",
        user_id=address_user,
    )

    assert response.status_code == 404
    assert body["error"] == "Address not found"
