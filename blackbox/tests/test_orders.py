"""Blackbox tests for order listing, cancellation, and invoice behavior."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def _create_order(
    client: QuickCartClient,
    user_id: int,
    product: dict[str, object],
    quantity: int = 2,
) -> tuple[int, int]:
    """Create a simple CARD order through the public API."""

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
        json_body={"payment_method": "CARD"},
        expected_status=200,
    )
    return payload["order_id"], quantity * product["price"]


def test_orders_list_and_get_by_id_expose_new_order_details(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """A freshly created order should appear in the order list and detail view."""

    user_id = test_users["checkout_card"]
    order_id, subtotal = _create_order(client, user_id, product_catalog["cheap_high_stock"])
    _, orders = client.api_call("GET", "/api/v1/orders", user_id=user_id, expected_status=200)
    _, order = client.api_call("GET", f"/api/v1/orders/{order_id}", user_id=user_id, expected_status=200)

    assert any(item["order_id"] == order_id for item in orders)
    assert order["order_id"] == order_id
    assert order["items"][0]["product_id"] == product_catalog["cheap_high_stock"]["product_id"]
    assert order["total_amount"] == pytest.approx(subtotal * 1.05)


def test_cancel_cancellable_order_returns_cancelled_status(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """A placed order should be cancellable through the public cancel endpoint."""

    user_id = test_users["checkout_card"]
    order_id, _ = _create_order(client, user_id, product_catalog["cheap_high_stock"])
    _, payload = client.api_call(
        "POST",
        f"/api/v1/orders/{order_id}/cancel",
        user_id=user_id,
        expected_status=200,
    )

    assert payload["order_status"] == "CANCELLED"


def test_cancel_delivered_order_returns_400(client: QuickCartClient, delivered_order: dict[str, object]) -> None:
    """Delivered orders should not be cancellable anymore."""

    response, payload = client.api_call(
        "POST",
        f"/api/v1/orders/{delivered_order['order_id']}/cancel",
        user_id=delivered_order["user_id"],
    )

    assert response.status_code == 400
    assert payload["error"] == "Cannot cancel delivered order"


def test_cancel_missing_order_returns_404(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Cancelling a missing order id should return a not-found response."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/orders/999999/cancel",
        user_id=test_users["checkout_card"],
    )

    assert response.status_code == 404
    assert payload["error"] == "Order not found"


@pytest.mark.xfail(reason="Observed defect: cancelling an order does not restore product stock.")
def test_cancelled_order_restores_product_stock(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """Order cancellation should add ordered quantities back into stock."""

    user_id = test_users["checkout_card"]
    product = product_catalog["cheap_high_stock"]
    before_stock = client.find_product(product["product_id"])["stock_quantity"]
    order_id, _ = _create_order(client, user_id, product)

    client.api_call("POST", f"/api/v1/orders/{order_id}/cancel", user_id=user_id, expected_status=200)
    after_stock = client.find_product(product["product_id"])["stock_quantity"]

    assert after_stock == before_stock


@pytest.mark.xfail(reason="Observed defect: invoice total adds GST twice instead of matching the order total.")
def test_invoice_math_matches_subtotal_plus_gst(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """Invoice subtotal, GST, and total should agree with the created order."""

    user_id = test_users["checkout_card"]
    order_id, subtotal = _create_order(client, user_id, product_catalog["cheap_high_stock"])
    _, invoice = client.api_call("GET", f"/api/v1/orders/{order_id}/invoice", user_id=user_id, expected_status=200)

    assert invoice["subtotal"] == subtotal
    assert invoice["gst_amount"] == pytest.approx(subtotal * 0.05)
    assert invoice["total_amount"] == pytest.approx(subtotal + invoice["gst_amount"])
