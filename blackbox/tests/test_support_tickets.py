"""Blackbox tests for support ticket creation and status transitions."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def test_create_ticket_stores_exact_message_and_starts_open(
    client: QuickCartClient,
    test_users: dict[str, int],
    unique_suffix: str,
) -> None:
    """A new ticket should start as OPEN and preserve the submitted message exactly."""

    user_id = test_users["support"]
    subject = f"Brake issue {unique_suffix}"
    message = f"Please inspect vibration level {unique_suffix} exactly."
    _, payload = client.api_call(
        "POST",
        "/api/v1/support/ticket",
        user_id=user_id,
        json_body={"subject": subject, "message": message},
        expected_status=200,
    )
    ticket_id = payload["ticket_id"]

    assert payload["status"] == "OPEN"
    assert payload["subject"] == subject
    assert payload["message"] == message

    _, tickets = client.api_call("GET", "/api/v1/support/tickets", user_id=user_id, expected_status=200)
    assert any(ticket["ticket_id"] == ticket_id and ticket["status"] == "OPEN" for ticket in tickets)

    admin_tickets = client.admin_get("/api/v1/admin/tickets")
    matching = next(ticket for ticket in admin_tickets if ticket["ticket_id"] == ticket_id)
    assert matching["message"] == message


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        ({"subject": "Hey", "message": "too short subject"}, "Subject must be between 5 and 100 characters"),
        ({"subject": "Valid subject", "message": ""}, "Message must be between 1 and 500 characters"),
    ],
)
def test_create_ticket_rejects_invalid_lengths(
    client: QuickCartClient,
    test_users: dict[str, int],
    payload: dict[str, str],
    expected_error: str,
) -> None:
    """Subject and message boundaries should be enforced on ticket creation."""

    response, body = client.api_call(
        "POST",
        "/api/v1/support/ticket",
        user_id=test_users["support"],
        json_body=payload,
    )

    assert response.status_code == 400
    assert body["error"] == expected_error


def test_ticket_status_allows_only_forward_transitions(
    client: QuickCartClient,
    test_users: dict[str, int],
    unique_suffix: str,
) -> None:
    """Tickets should move OPEN -> IN_PROGRESS -> CLOSED, with invalid jumps rejected."""

    user_id = test_users["support"]
    _, created = client.api_call(
        "POST",
        "/api/v1/support/ticket",
        user_id=user_id,
        json_body={
            "subject": f"Status flow {unique_suffix}",
            "message": f"Track ticket flow {unique_suffix}",
        },
        expected_status=200,
    )
    ticket_id = created["ticket_id"]

    invalid_direct_close, invalid_close_payload = client.api_call(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        user_id=user_id,
        json_body={"status": "CLOSED"},
    )
    assert invalid_direct_close.status_code == 400
    assert invalid_close_payload["error"] == "Invalid status transition"

    _, in_progress = client.api_call(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        user_id=user_id,
        json_body={"status": "IN_PROGRESS"},
        expected_status=200,
    )
    assert in_progress["status"] == "IN_PROGRESS"

    invalid_reopen, invalid_reopen_payload = client.api_call(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        user_id=user_id,
        json_body={"status": "OPEN"},
    )
    assert invalid_reopen.status_code == 400
    assert invalid_reopen_payload["error"] == "Invalid status transition"

    _, closed = client.api_call(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        user_id=user_id,
        json_body={"status": "CLOSED"},
        expected_status=200,
    )
    assert closed["status"] == "CLOSED"
