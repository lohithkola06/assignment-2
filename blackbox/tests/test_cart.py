"""Blackbox tests for cart operations and cart arithmetic."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def _add_item(client: QuickCartClient, user_id: int, product_id: int, quantity: int) -> None:
    client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=user_id,
        json_body={"product_id": product_id, "quantity": quantity},
        expected_status=200,
    )


def test_view_empty_cart_returns_no_items(client: QuickCartClient, cart_user: int) -> None:
    """A freshly cleared cart should expose zero items and total 0."""

    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)

    assert payload["items"] == []
    assert payload["total"] == 0


def test_adding_same_product_twice_accumulates_quantity(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """Re-adding an existing product should increase quantity instead of replacing it."""

    product = product_catalog["cheap_high_stock"]
    _add_item(client, cart_user, product["product_id"], 2)
    _add_item(client, cart_user, product["product_id"], 3)

    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)

    assert payload["items"][0]["product_id"] == product["product_id"]
    assert payload["items"][0]["quantity"] == 5


@pytest.mark.xfail(reason="Observed defect: the cart accepts zero-quantity add requests.")
def test_cart_rejects_zero_quantity_add(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """Quantity 0 should be rejected by the add-to-cart endpoint."""

    product = product_catalog["cheap_high_stock"]
    response, payload = client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=cart_user,
        json_body={"product_id": product["product_id"], "quantity": 0},
    )

    assert response.status_code == 400
    assert payload["error"]


def test_cart_rejects_nonexistent_product(client: QuickCartClient, cart_user: int) -> None:
    """Adding an unknown product id should return 404."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=cart_user,
        json_body={"product_id": 999999, "quantity": 1},
    )

    assert response.status_code == 404
    assert payload["error"] == "Product not found"


def test_cart_rejects_quantity_above_stock(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """The server should reject requests that exceed observable stock levels."""

    product = product_catalog["cheap_high_stock"]
    response, payload = client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=cart_user,
        json_body={"product_id": product["product_id"], "quantity": product["stock_quantity"] + 1},
    )

    assert response.status_code == 400
    assert payload["error"] == "Insufficient stock"


def test_cart_update_changes_quantity(client: QuickCartClient, cart_user: int, product_catalog: dict[str, object]) -> None:
    """Updating a cart line should replace the stored quantity with the new value."""

    product = product_catalog["cheap_high_stock"]
    _add_item(client, cart_user, product["product_id"], 1)

    client.api_call(
        "POST",
        "/api/v1/cart/update",
        user_id=cart_user,
        json_body={"product_id": product["product_id"], "quantity": 4},
        expected_status=200,
    )
    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)

    assert payload["items"][0]["quantity"] == 4


def test_cart_remove_item_clears_the_line(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """Removing an existing cart item should leave the cart empty again."""

    product = product_catalog["cheap_high_stock"]
    _add_item(client, cart_user, product["product_id"], 2)

    client.api_call(
        "POST",
        "/api/v1/cart/remove",
        user_id=cart_user,
        json_body={"product_id": product["product_id"]},
        expected_status=200,
    )
    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)

    assert payload["items"] == []
    assert payload["total"] == 0


def test_cart_remove_missing_item_returns_404(client: QuickCartClient, cart_user: int) -> None:
    """Removing an item that is not present should return a not-found error."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/cart/remove",
        user_id=cart_user,
        json_body={"product_id": 999999},
    )

    assert response.status_code == 404
    assert payload["error"] == "Product not in cart"


@pytest.mark.xfail(reason="Observed defect: cart item subtotal is not always quantity multiplied by unit price.")
def test_cart_item_subtotal_matches_quantity_times_unit_price(
    client: QuickCartClient,
    cart_user: int,
) -> None:
    """Item subtotal should match the documented quantity-times-price rule."""

    _add_item(client, cart_user, 1, 5)

    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)
    item = payload["items"][0]

    assert item["subtotal"] == item["quantity"] * item["unit_price"]


@pytest.mark.xfail(reason="Observed defect: cart total does not sum all line subtotals correctly.")
def test_cart_total_equals_sum_of_all_item_subtotals(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """Cart total should be the sum of every line subtotal."""

    first = product_catalog["cheap_high_stock"]
    second = next(product for product in product_catalog["active"] if product["product_id"] != first["product_id"])
    _add_item(client, cart_user, first["product_id"], 2)
    _add_item(client, cart_user, second["product_id"], 3)

    _, payload = client.api_call("GET", "/api/v1/cart", user_id=cart_user, expected_status=200)
    expected_total = sum(item["subtotal"] for item in payload["items"])

    assert payload["total"] == expected_total
