"""
tests/test_services.py
-----------------------
Unit tests for all business services.

All repository access is replaced with mock objects so tests run
completely offline without touching the database file.

Coverage
--------
TestOrderService
    Valid orders (111/222/333), invalid order, empty input,
    repository exception, response format.

TestReturnService
    Return policy text content, shipping info text content,
    always-success contract.

TestRecommendationService
    Full match (activity + weather + experience),
    partial match (no experience), no match (empty list),
    missing required fields, repository exception,
    product name lookup per category.

TestHandoffService
    Always returns success, message content.
"""

import pytest
from unittest.mock import MagicMock, patch

from chatbot.schemas import ServiceResult
from database.repository import set_repository, reset_repository
from services.order_service import OrderService
from services.return_service import ReturnService
from services.recommendation_service import RecommendationService
from services.handoff_service import HandoffService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_repository():
    """Reset the singleton after every test to avoid cross-test contamination."""
    yield
    reset_repository()


def _make_repo(
    orders: dict | None = None,
    products: list | None = None,
    recommendations: list | None = None,
) -> MagicMock:
    """Build a mock BaseRepository with configurable return values."""
    repo = MagicMock()

    _orders = orders or {
        "111": {"order_id": "111", "customer_name": "Demo Customer", "status": "Shipped",    "estimated_delivery": "Arriving Tomorrow"},
        "222": {"order_id": "222", "customer_name": "Demo Customer", "status": "Processing", "estimated_delivery": "Ships in 24 Hours"},
        "333": {"order_id": "333", "customer_name": "Demo Customer", "status": "Delivered",  "estimated_delivery": "Delivered"},
    }
    repo.get_order.side_effect = lambda oid: _orders.get(oid.strip())

    _products_list = products if products is not None else [
        {"product_id": 1, "category": "Tent",     "product_name": "4-Season Tent"},
        {"product_id": 2, "category": "Sleeping",  "product_name": "Insulated Sleeping Bag"},
        {"product_id": 3, "category": "Clothing",  "product_name": "Insulated Jacket"},
        {"product_id": 4, "category": "Backpack",  "product_name": "60L Hiking Backpack"},
    ]

    def _get_products(category=None):
        if category is None:
            return _products_list
        return [p for p in _products_list if p["category"] == category]

    repo.get_products.side_effect = _get_products

    _rec_list = recommendations if recommendations is not None else ["Sleeping", "Clothing", "Tent"]
    repo.get_recommendations.return_value = _rec_list

    return repo


# ---------------------------------------------------------------------------
# TestOrderService
# ---------------------------------------------------------------------------

class TestOrderService:

    def test_order_111_shipped(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("111")
        assert result.success is True
        assert "Shipped" in result.data
        assert "111" in result.data
        assert "Arriving Tomorrow" in result.data

    def test_order_222_processing(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("222")
        assert result.success is True
        assert "Processing" in result.data
        assert "Ships in 24 Hours" in result.data

    def test_order_333_delivered(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("333")
        assert result.success is True
        assert "Delivered" in result.data

    def test_invalid_order_returns_failure(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("999")
        assert result.success is False
        assert "999" in result.error
        assert len(result.error) > 0

    def test_empty_order_id_returns_failure(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("")
        assert result.success is False
        assert len(result.error) > 0

    def test_whitespace_order_id_returns_failure(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("   ")
        assert result.success is False

    def test_repository_exception_returns_failure(self) -> None:
        repo = MagicMock()
        repo.get_order.side_effect = RuntimeError("DB connection lost")
        svc = OrderService(repository=repo)
        result = svc.get_order_status("111")
        assert result.success is False
        assert len(result.error) > 0

    def test_result_is_service_result(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("111")
        assert isinstance(result, ServiceResult)

    def test_response_contains_order_id(self) -> None:
        svc = OrderService(repository=_make_repo())
        result = svc.get_order_status("222")
        assert "222" in result.data


# ---------------------------------------------------------------------------
# TestReturnService
# ---------------------------------------------------------------------------

class TestReturnService:

    def test_return_policy_success(self) -> None:
        svc = ReturnService()
        result = svc.get_return_policy()
        assert result.success is True
        assert isinstance(result.data, str)
        assert len(result.data) > 0

    def test_return_policy_mentions_30_days(self) -> None:
        svc = ReturnService()
        result = svc.get_return_policy()
        assert "30" in result.data

    def test_return_policy_mentions_condition(self) -> None:
        svc = ReturnService()
        result = svc.get_return_policy()
        # Policy should mention packaging or condition requirements
        assert "packaging" in result.data.lower() or "unused" in result.data.lower()

    def test_shipping_info_success(self) -> None:
        svc = ReturnService()
        result = svc.get_shipping_info()
        assert result.success is True
        assert isinstance(result.data, str)
        assert len(result.data) > 0

    def test_shipping_info_mentions_standard(self) -> None:
        svc = ReturnService()
        result = svc.get_shipping_info()
        assert "standard" in result.data.lower()

    def test_shipping_info_mentions_expedited(self) -> None:
        svc = ReturnService()
        result = svc.get_shipping_info()
        assert "expedited" in result.data.lower()

    def test_return_service_is_service_result(self) -> None:
        svc = ReturnService()
        assert isinstance(svc.get_return_policy(), ServiceResult)
        assert isinstance(svc.get_shipping_info(), ServiceResult)


# ---------------------------------------------------------------------------
# TestRecommendationService
# ---------------------------------------------------------------------------

class TestRecommendationService:

    def test_full_match_returns_success(self) -> None:
        repo = _make_repo(recommendations=["Tent", "Sleeping"])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold", "Beginner")
        assert result.success is True
        assert isinstance(result.data, str)

    def test_response_mentions_recommended_categories(self) -> None:
        repo = _make_repo(recommendations=["Tent", "Sleeping"])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold", "Beginner")
        assert "Tent" in result.data
        assert "Sleeping" in result.data

    def test_response_includes_product_names(self) -> None:
        repo = _make_repo(recommendations=["Tent"])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold")
        assert "4-Season Tent" in result.data

    def test_no_experience_still_returns_results(self) -> None:
        repo = _make_repo(recommendations=["Backpack"])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Hiking", "Warm")
        assert result.success is True
        repo.get_recommendations.assert_called_once_with(
            activity="Hiking",
            weather="Warm",
            experience=None,
        )

    def test_no_match_returns_empty_data(self) -> None:
        repo = _make_repo(recommendations=[])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Skydiving", "Blizzard")
        assert result.success is True
        assert result.data == []

    def test_missing_activity_returns_failure(self) -> None:
        svc = RecommendationService(repository=_make_repo())
        result = svc.get_recommendations("", "Cold")
        assert result.success is False

    def test_missing_weather_returns_failure(self) -> None:
        svc = RecommendationService(repository=_make_repo())
        result = svc.get_recommendations("Camping", "")
        assert result.success is False

    def test_repository_exception_returns_failure(self) -> None:
        repo = MagicMock()
        repo.get_recommendations.side_effect = RuntimeError("DB error")
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold")
        assert result.success is False
        assert len(result.error) > 0

    def test_category_without_products_still_included(self) -> None:
        """If a category has no products, the category name should still appear."""
        repo = _make_repo(recommendations=["UnknownCategory"], products=[])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold")
        assert "UnknownCategory" in result.data

    def test_response_mentions_activity_and_weather(self) -> None:
        repo = _make_repo(recommendations=["Tent"])
        svc = RecommendationService(repository=repo)
        result = svc.get_recommendations("Camping", "Cold")
        assert "Camping" in result.data
        assert "Cold" in result.data

    def test_result_is_service_result(self) -> None:
        svc = RecommendationService(repository=_make_repo())
        result = svc.get_recommendations("Camping", "Cold")
        assert isinstance(result, ServiceResult)


# ---------------------------------------------------------------------------
# TestHandoffService
# ---------------------------------------------------------------------------

class TestHandoffService:

    def test_simulate_handoff_returns_success(self) -> None:
        svc = HandoffService()
        result = svc.simulate_handoff()
        assert result.success is True

    def test_handoff_message_is_non_empty_string(self) -> None:
        svc = HandoffService()
        result = svc.simulate_handoff()
        assert isinstance(result.data, str)
        assert len(result.data) > 0

    def test_handoff_message_mentions_agent_or_representative(self) -> None:
        svc = HandoffService()
        result = svc.simulate_handoff()
        msg = result.data.lower()
        assert "agent" in msg or "representative" in msg or "team" in msg

    def test_result_is_service_result(self) -> None:
        svc = HandoffService()
        assert isinstance(svc.simulate_handoff(), ServiceResult)
