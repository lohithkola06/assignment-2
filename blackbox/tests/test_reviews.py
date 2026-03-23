"""Blackbox tests for product review retrieval and submission."""

from __future__ import annotations

import pytest

from .conftest import QuickCartClient


def test_reviews_average_is_zero_when_no_reviews_exist(
    client: QuickCartClient,
    test_users: dict[str, int],
    no_review_product: dict[str, object],
) -> None:
    """Products with no reviews should expose average_rating as 0."""

    _, payload = client.api_call(
        "GET",
        f"/api/v1/products/{no_review_product['product_id']}/reviews",
        user_id=test_users["review_primary"],
        expected_status=200,
    )

    assert payload["average_rating"] == 0
    assert payload["reviews"] == []


def test_add_review_updates_average_rating_as_decimal(
    client: QuickCartClient,
    test_users: dict[str, int],
    no_review_product: dict[str, object],
    unique_suffix: str,
) -> None:
    """Two reviews with different ratings should produce a decimal average."""

    product_id = no_review_product["product_id"]
    comment_one = f"review-a-{unique_suffix}"
    comment_two = f"review-b-{unique_suffix}"
    client.api_call(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        user_id=test_users["review_primary"],
        json_body={"rating": 4, "comment": comment_one},
        expected_status=200,
    )
    client.api_call(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        user_id=test_users["review_secondary"],
        json_body={"rating": 5, "comment": comment_two},
        expected_status=200,
    )
    _, payload = client.api_call(
        "GET",
        f"/api/v1/products/{product_id}/reviews",
        user_id=test_users["review_primary"],
        expected_status=200,
    )

    comments = {review["comment"] for review in payload["reviews"]}
    assert comment_one in comments
    assert comment_two in comments
    assert payload["average_rating"] == pytest.approx(4.5)


@pytest.mark.xfail(reason="Observed defect: out-of-range ratings are accepted instead of rejected.")
def test_review_rejects_rating_outside_one_to_five(
    client: QuickCartClient,
    test_users: dict[str, int],
    unique_suffix: str,
) -> None:
    """Ratings above 5 should be rejected with a validation error."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/products/1/reviews",
        user_id=test_users["review_primary"],
        json_body={"rating": 6, "comment": f"bad-rating-{unique_suffix}"},
    )

    assert response.status_code == 400
    assert payload["error"]


@pytest.mark.parametrize("comment_value", ["", "x" * 201])
def test_review_rejects_invalid_comment_lengths(
    client: QuickCartClient,
    test_users: dict[str, int],
    comment_value: str,
) -> None:
    """Comment length boundaries should follow the documented 1..200 range."""

    response, payload = client.api_call(
        "POST",
        "/api/v1/products/1/reviews",
        user_id=test_users["review_primary"],
        json_body={"rating": 5, "comment": comment_value},
    )

    assert response.status_code == 400
    assert payload["error"] == "Comment must be between 1 and 200 characters"
