"""Blackbox tests for checkout behavior and payment-state rules."""

from __future__ import annotations

import math

import pytest

from .conftest import QuickCartClient


def _create_checkout_order(
    client: QuickCartClient,
    user_id: int,
    product: dict[str, object],
    quantity: int,
    payment_method: str,
) -> tuple[dict[str, object], int]:
    """Create an order through the public cart and checkout endpoints."""

    client.clear_cart(user_id)
    client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=user_id,
        json_body={"product_id": product["product_id"], "quantity": quantity},
        expected_status=200,
    )
    _, payload = client.api_call(
        "POST",
        "/api/v1/checkout",
        user_id=user_id,
        json_body={"payment_method": payment_method},
        expected_status=200,
    )
    return payload, quantity * product["price"]


def test_checkout_rejects_invalid_payment_method(
    client: QuickCartClient,
    test_users: dict[str, int],
) -> None:
    """Only COD, WALLET, and CARD are accepted by the checkout API."""

    client.clear_cart(test_users["checkout_card"])
    response, payload = client.api_call(
        "POST",
        "/api/v1/checkout",
        user_id=test_users["checkout_card"],
        json_body={"payment_method": "UPI"},
    )

    assert response.status_code == 400
    assert payload["error"] == "Invalid payment method"


@pytest.mark.xfail(reason="Observed defect: checkout succeeds and creates a zero-total order for an empty cart.")
def test_checkout_rejects_empty_cart(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Empty carts should be rejected before any order is created."""

    user_id = test_users["checkout_card"]
    client.clear_cart(user_id)

    response, payload = client.api_call(
        "POST",
        "/api/v1/checkout",
        user_id=user_id,
        json_body={"payment_method": "CARD"},
    )

    assert response.status_code == 400
    assert "empty" in payload["error"].lower()


def test_checkout_rejects_cod_when_total_exceeds_5000(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """COD should be blocked once the cart total goes beyond the documented limit."""

    user_id = test_users["checkout_cod"]
    product = product_catalog["cod_over_limit"]
    quantity = math.ceil(5001 / product["price"])
    client.clear_cart(user_id)
    client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=user_id,
        json_body={"product_id": product["product_id"], "quantity": quantity},
        expected_status=200,
    )

    response, payload = client.api_call(
        "POST",
        "/api/v1/checkout",
        user_id=user_id,
        json_body={"payment_method": "COD"},
    )

    assert response.status_code == 400
    assert payload["error"] == "COD not allowed for amount > 5000"
    client.clear_cart(user_id)


def test_checkout_card_marks_payment_as_paid_and_adds_gst_once(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """CARD checkout should return PAID and a single 5 percent GST charge."""

    payload, subtotal = _create_checkout_order(
        client,
        test_users["checkout_card"],
        product_catalog["cheap_high_stock"],
        2,
        "CARD",
    )

    assert payload["payment_status"] == "PAID"
    assert payload["order_status"] == "PLACED"
    assert payload["gst_amount"] == pytest.approx(subtotal * 0.05)
    assert payload["total_amount"] == pytest.approx(subtotal + payload["gst_amount"])


def test_checkout_cod_starts_with_pending_payment(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """COD orders should start with a pending payment state."""

    payload, _ = _create_checkout_order(
        client,
        test_users["checkout_cod"],
        product_catalog["cheap_high_stock"],
        2,
        "COD",
    )

    assert payload["payment_status"] == "PENDING"
    assert payload["order_status"] == "PLACED"


def test_checkout_wallet_starts_with_pending_payment(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """WALLET orders should also start as pending according to the specification."""

    payload, _ = _create_checkout_order(
        client,
        test_users["checkout_wallet"],
        product_catalog["cheap_high_stock"],
        2,
        "WALLET",
    )

    assert payload["payment_status"] == "PENDING"
    assert payload["order_status"] == "PLACED"
