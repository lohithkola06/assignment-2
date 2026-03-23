"""Blackbox tests for coupon application and removal."""

from __future__ import annotations

import math

import pytest

from .conftest import QuickCartClient


def _seed_cart_for_total(
    client: QuickCartClient,
    user_id: int,
    product: dict[str, object],
    minimum_total: int,
) -> int:
    """Add enough units of one product to meet a target cart total."""

    quantity = math.ceil(minimum_total / product["price"])
    client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=user_id,
        json_body={"product_id": product["product_id"], "quantity": quantity},
        expected_status=200,
    )
    return quantity


def test_apply_valid_fixed_coupon_returns_expected_discount(
    client: QuickCartClient,
    cart_user: int,
    coupon_catalog: dict[str, dict[str, object]],
    product_catalog: dict[str, object],
) -> None:
    """A fixed-value coupon should subtract its documented flat amount."""

    coupon = coupon_catalog["WELCOME50"]
    product = product_catalog["cheap_high_stock"]
    quantity = _seed_cart_for_total(client, cart_user, product, coupon["min_cart_value"])
    cart_total = quantity * product["price"]

    _, payload = client.api_call(
        "POST",
        "/api/v1/coupon/apply",
        user_id=cart_user,
        json_body={"coupon_code": coupon["coupon_code"]},
        expected_status=200,
    )

    assert payload["coupon_code"] == coupon["coupon_code"]
    assert payload["discount"] == 50
    assert payload["new_total"] == cart_total - 50


def test_apply_percent_coupon_respects_max_discount_cap(
    client: QuickCartClient,
    cart_user: int,
    coupon_catalog: dict[str, dict[str, object]],
    product_catalog: dict[str, object],
) -> None:
    """Percent coupons should cap the discount at the documented maximum."""

    coupon = coupon_catalog["PERCENT20"]
    product = product_catalog["cheap_high_stock"]
    quantity = _seed_cart_for_total(client, cart_user, product, 1200)
    cart_total = quantity * product["price"]
    expected_discount = min(cart_total * coupon["discount_value"] / 100, coupon["max_discount"])

    _, payload = client.api_call(
        "POST",
        "/api/v1/coupon/apply",
        user_id=cart_user,
        json_body={"coupon_code": coupon["coupon_code"]},
        expected_status=200,
    )

    assert payload["discount"] == expected_discount
    assert payload["new_total"] == cart_total - expected_discount


def test_coupon_rejects_cart_below_minimum_value(
    client: QuickCartClient,
    cart_user: int,
    product_catalog: dict[str, object],
) -> None:
    """Coupons should reject carts that do not meet the minimum total."""

    product = product_catalog["cheap_high_stock"]
    client.api_call(
        "POST",
        "/api/v1/cart/add",
        user_id=cart_user,
        json_body={"product_id": product["product_id"], "quantity": 1},
        expected_status=200,
    )

    response, payload = client.api_call(
        "POST",
        "/api/v1/coupon/apply",
        user_id=cart_user,
        json_body={"coupon_code": "PERCENT20"},
    )

    assert response.status_code == 400
    assert payload["error"] == "Cart value below minimum"


@pytest.mark.xfail(reason="Observed defect: expired coupons are still accepted once the cart meets the minimum.")
def test_coupon_rejects_expired_coupon_when_minimum_is_met(
    client: QuickCartClient,
    cart_user: int,
    coupon_catalog: dict[str, dict[str, object]],
    product_catalog: dict[str, object],
) -> None:
    """Expired coupons should fail even when the cart value is high enough."""

    coupon = coupon_catalog["EXPIRED100"]
    product = product_catalog["cheap_high_stock"]
    _seed_cart_for_total(client, cart_user, product, coupon["min_cart_value"])

    response, payload = client.api_call(
        "POST",
        "/api/v1/coupon/apply",
        user_id=cart_user,
        json_body={"coupon_code": coupon["coupon_code"]},
    )

    assert response.status_code == 400
    assert "expired" in payload["error"].lower()


def test_remove_coupon_succeeds_after_apply(
    client: QuickCartClient,
    cart_user: int,
    coupon_catalog: dict[str, dict[str, object]],
    product_catalog: dict[str, object],
) -> None:
    """Applied coupons should be removable through the public API."""

    coupon = coupon_catalog["WELCOME50"]
    product = product_catalog["cheap_high_stock"]
    _seed_cart_for_total(client, cart_user, product, coupon["min_cart_value"])
    client.api_call(
        "POST",
        "/api/v1/coupon/apply",
        user_id=cart_user,
        json_body={"coupon_code": coupon["coupon_code"]},
        expected_status=200,
    )

    _, payload = client.api_call(
        "POST",
        "/api/v1/coupon/remove",
        user_id=cart_user,
        expected_status=200,
    )

    assert payload["message"] == "Coupon removed successfully"
