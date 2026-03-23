"""Shared pytest fixtures for QuickCart blackbox tests."""

from __future__ import annotations

import math
import os
import uuid
from typing import Any

import pytest
import requests

UNSET = object()


class QuickCartClient:
    """Small HTTP client for the externally exposed QuickCart API."""

    def __init__(self, base_url: str, roll_number: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.roll_number = str(roll_number)
        self.session = requests.Session()

    def request(
        self,
        method: str,
        path: str,
        *,
        user_id: object = UNSET,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        include_roll: bool = True,
    ) -> requests.Response:
        """Send a request to QuickCart without assuming any internal details."""

        request_headers: dict[str, str] = {}
        if include_roll:
            request_headers["X-Roll-Number"] = self.roll_number
        if user_id is not UNSET and user_id is not None:
            request_headers["X-User-ID"] = str(user_id)
        if headers:
            request_headers.update(headers)

        return self.session.request(
            method=method,
            url=f"{self.base_url}{path}",
            headers=request_headers,
            json=json_body,
            timeout=10,
        )

    @staticmethod
    def payload(response: requests.Response) -> Any:
        """Decode JSON when possible and otherwise return the raw text body."""

        try:
            return response.json()
        except ValueError:
            return response.text

    def api_call(
        self,
        method: str,
        path: str,
        *,
        user_id: object = UNSET,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        include_roll: bool = True,
        expected_status: int | None = None,
    ) -> tuple[requests.Response, Any]:
        """Send a request and optionally assert its HTTP status code."""

        response = self.request(
            method,
            path,
            user_id=user_id,
            json_body=json_body,
            headers=headers,
            include_roll=include_roll,
        )
        payload = self.payload(response)
        if expected_status is not None:
            assert response.status_code == expected_status, (
                f"{method} {path} returned {response.status_code} instead of "
                f"{expected_status}: {payload!r}"
            )
        return response, payload

    def admin_get(self, path: str) -> Any:
        """Fetch an admin inspection endpoint."""

        _, payload = self.api_call("GET", path, user_id=None, expected_status=200)
        return payload

    def clear_cart(self, user_id: int) -> None:
        """Reset a user's cart using the public API."""

        self.api_call("DELETE", "/api/v1/cart/clear", user_id=user_id, expected_status=200)

    def purge_addresses(self, user_id: int) -> None:
        """Delete every address for a user through the published address endpoints."""

        _, addresses = self.api_call("GET", "/api/v1/addresses", user_id=user_id, expected_status=200)
        for address in addresses:
            self.api_call(
                "DELETE",
                f"/api/v1/addresses/{address['address_id']}",
                user_id=user_id,
                expected_status=200,
            )

    def find_product(self, product_id: int) -> dict[str, Any]:
        """Look up a product through the admin inspection endpoint."""

        products = self.admin_get("/api/v1/admin/products")
        return next(product for product in products if product["product_id"] == product_id)


@pytest.fixture(scope="session")
def base_url() -> str:
    """QuickCart base URL for local Docker execution."""

    return os.getenv("QUICKCART_BASE_URL", "http://127.0.0.1:8080")


@pytest.fixture(scope="session")
def roll_number() -> int:
    """Roll number header used for all test requests."""

    return int(os.getenv("ROLL_NUMBER", "23110001"))


@pytest.fixture(scope="session")
def client(base_url: str, roll_number: int) -> QuickCartClient:
    """Shared blackbox client instance."""

    api_client = QuickCartClient(base_url, roll_number)
    api_client.admin_get("/api/v1/admin/users")
    return api_client


@pytest.fixture(scope="session")
def admin_snapshot(client: QuickCartClient) -> dict[str, Any]:
    """Session-wide snapshot of exposed admin data for fixture discovery."""

    return {
        "users": client.admin_get("/api/v1/admin/users"),
        "products": client.admin_get("/api/v1/admin/products"),
        "coupons": client.admin_get("/api/v1/admin/coupons"),
        "orders": client.admin_get("/api/v1/admin/orders"),
    }


@pytest.fixture(scope="session")
def test_users(admin_snapshot: dict[str, Any]) -> dict[str, int]:
    """Choose stable high-number users from the exposed admin user list."""

    ordered_users = sorted((user["user_id"] for user in admin_snapshot["users"]), reverse=True)
    assert len(ordered_users) >= 9, "Need at least nine users to isolate blackbox flows."
    return {
        "profile": ordered_users[0],
        "support": ordered_users[0],
        "addresses": ordered_users[1],
        "cart_coupon": ordered_users[2],
        "checkout_card": ordered_users[3],
        "checkout_cod": ordered_users[4],
        "checkout_wallet": ordered_users[5],
        "wallet_loyalty": ordered_users[6],
        "review_primary": ordered_users[7],
        "review_secondary": ordered_users[8],
        "catalog": ordered_users[-1],
    }


@pytest.fixture(scope="session")
def product_catalog(admin_snapshot: dict[str, Any]) -> dict[str, Any]:
    """Expose a few useful product selections discovered through admin endpoints."""

    products = admin_snapshot["products"]
    active_products = [product for product in products if product["is_active"]]
    inactive_products = [product for product in products if not product["is_active"]]
    stock_friendly = max(active_products, key=lambda product: (product["stock_quantity"], -product["price"]))
    cod_candidate = max(
        (
            product
            for product in active_products
            if product["stock_quantity"] >= math.ceil(5001 / product["price"])
        ),
        key=lambda product: product["price"],
    )
    return {
        "active": active_products,
        "inactive": inactive_products,
        "cheap_high_stock": stock_friendly,
        "cod_over_limit": cod_candidate,
    }


@pytest.fixture(scope="session")
def coupon_catalog(admin_snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map coupon code to the exposed admin coupon data."""

    return {coupon["coupon_code"]: coupon for coupon in admin_snapshot["coupons"]}


@pytest.fixture
def unique_suffix() -> str:
    """Short unique token for externally visible payloads."""

    return uuid.uuid4().hex[:8]


@pytest.fixture
def profile_user(client: QuickCartClient, test_users: dict[str, int]) -> int:
    """Profile test user restored to its original values after each test."""

    user_id = test_users["profile"]
    _, original = client.api_call("GET", "/api/v1/profile", user_id=user_id, expected_status=200)
    yield user_id
    client.api_call(
        "PUT",
        "/api/v1/profile",
        user_id=user_id,
        json_body={"name": original["name"], "phone": original["phone"]},
        expected_status=200,
    )


@pytest.fixture
def address_user(client: QuickCartClient, test_users: dict[str, int]) -> int:
    """Address test user with pre/post cleanup."""

    user_id = test_users["addresses"]
    client.purge_addresses(user_id)
    yield user_id
    client.purge_addresses(user_id)


@pytest.fixture
def cart_user(client: QuickCartClient, test_users: dict[str, int]) -> int:
    """Cart and coupon test user with a clean cart around each test."""

    user_id = test_users["cart_coupon"]
    client.clear_cart(user_id)
    yield user_id
    client.clear_cart(user_id)


@pytest.fixture
def wallet_user(client: QuickCartClient, test_users: dict[str, int]) -> int:
    """Wallet and loyalty test user with best-effort wallet restoration."""

    user_id = test_users["wallet_loyalty"]
    _, original_wallet = client.api_call("GET", "/api/v1/wallet", user_id=user_id, expected_status=200)
    yield user_id
    for _ in range(2):
        _, current_wallet = client.api_call("GET", "/api/v1/wallet", user_id=user_id, expected_status=200)
        delta = round(current_wallet["wallet_balance"] - original_wallet["wallet_balance"], 2)
        if delta > 0:
            client.api_call(
                "POST",
                "/api/v1/wallet/pay",
                user_id=user_id,
                json_body={"amount": delta},
                expected_status=200,
            )
        elif delta < 0:
            client.api_call(
                "POST",
                "/api/v1/wallet/add",
                user_id=user_id,
                json_body={"amount": round(-delta, 2)},
                expected_status=200,
            )
        else:
            break


@pytest.fixture
def no_review_product(
    client: QuickCartClient,
    product_catalog: dict[str, Any],
    test_users: dict[str, int],
) -> dict[str, Any]:
    """Find an active product that currently has no reviews."""

    for product in product_catalog["active"]:
        _, payload = client.api_call(
            "GET",
            f"/api/v1/products/{product['product_id']}/reviews",
            user_id=test_users["review_primary"],
            expected_status=200,
        )
        if not payload["reviews"]:
            return product
    pytest.skip("No active product with zero reviews was available.")


@pytest.fixture
def delivered_order(client: QuickCartClient, admin_snapshot: dict[str, Any], test_users: dict[str, int]) -> dict[str, Any]:
    """Pick one already-delivered order that can be used for negative cancel tests."""

    delivered = [
        order
        for order in admin_snapshot["orders"]
        if order["user_id"] == test_users["checkout_card"] and order["order_status"] == "DELIVERED"
    ]
    if not delivered:
        pytest.skip("No delivered order available for the chosen test user.")
    return delivered[0]
