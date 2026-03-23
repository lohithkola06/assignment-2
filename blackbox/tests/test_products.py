"""Blackbox tests for product listing and lookup endpoints."""

from __future__ import annotations

from .conftest import QuickCartClient


def test_products_list_only_returns_active_items(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """Inactive products should stay hidden from the public product list."""

    _, products = client.api_call("GET", "/api/v1/products", user_id=test_users["catalog"], expected_status=200)
    inactive_ids = {product["product_id"] for product in product_catalog["inactive"]}

    assert products
    assert all(product["is_active"] is True for product in products)
    assert inactive_ids.isdisjoint({product["product_id"] for product in products})


def test_get_product_by_id_matches_admin_price(
    client: QuickCartClient,
    test_users: dict[str, int],
    product_catalog: dict[str, object],
) -> None:
    """Public product details should match the observable admin data."""

    product = product_catalog["cheap_high_stock"]
    _, payload = client.api_call(
        "GET",
        f"/api/v1/products/{product['product_id']}",
        user_id=test_users["catalog"],
        expected_status=200,
    )

    admin_product = client.find_product(product["product_id"])

    assert payload["product_id"] == admin_product["product_id"]
    assert payload["name"] == admin_product["name"]
    assert payload["price"] == admin_product["price"]
    assert payload["stock_quantity"] == admin_product["stock_quantity"]


def test_get_invalid_product_returns_404(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Unknown product identifiers should return a not-found response."""

    response, payload = client.api_call("GET", "/api/v1/products/999999", user_id=test_users["catalog"])

    assert response.status_code == 404
    assert payload["error"] == "Product not found"


def test_products_category_filter_returns_only_matching_category(
    client: QuickCartClient,
    test_users: dict[str, int],
) -> None:
    """Category filtering should keep only products from the requested category."""

    _, payload = client.api_call(
        "GET",
        "/api/v1/products?category=Fruits",
        user_id=test_users["catalog"],
        expected_status=200,
    )

    assert payload
    assert all(product["category"] == "Fruits" for product in payload)


def test_products_search_matches_name_substrings(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Name search should expose only observable matches for the requested text."""

    _, payload = client.api_call(
        "GET",
        "/api/v1/products?search=Apple",
        user_id=test_users["catalog"],
        expected_status=200,
    )

    assert payload
    assert all("apple" in product["name"].lower() for product in payload)


def test_products_sort_by_price_ascending(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Ascending sort should return a non-decreasing price sequence."""

    _, payload = client.api_call(
        "GET",
        "/api/v1/products?sort=price_asc",
        user_id=test_users["catalog"],
        expected_status=200,
    )
    prices = [product["price"] for product in payload]

    assert prices == sorted(prices)


def test_products_sort_by_price_descending(client: QuickCartClient, test_users: dict[str, int]) -> None:
    """Descending sort should return a non-increasing price sequence."""

    _, payload = client.api_call(
        "GET",
        "/api/v1/products?sort=price_desc",
        user_id=test_users["catalog"],
        expected_status=200,
    )
    prices = [product["price"] for product in payload]

    assert prices == sorted(prices, reverse=True)
