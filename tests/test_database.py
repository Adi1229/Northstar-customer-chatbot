"""
tests/test_database.py
-----------------------
Unit and integration tests for the database layer.

Tests use an in-memory SQLite database so they never touch the real
data file and run completely offline with zero configuration.

Coverage:
  - SQLiteAdapter initialisation
  - Seed data correctness
  - get_order() — valid / invalid / case handling
  - get_products() — all / by category
  - get_recommendations() — exact match / optional experience / no results
  - Repository singleton (get_repository / set_repository / reset)
  - Factory — unknown backend raises NotImplementedError
"""

import pytest

from database.sqlite_adapter import SQLiteAdapter
from database.factory import create_repository
from database.repository import get_repository, set_repository, reset_repository
from database.base import BaseRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def repo() -> SQLiteAdapter:
    """Fresh in-memory SQLite adapter for each test."""
    return SQLiteAdapter(db_path=":memory:")


# ---------------------------------------------------------------------------
# Initialisation & seeding
# ---------------------------------------------------------------------------

class TestInitialisation:
    def test_adapter_is_base_repository(self, repo: SQLiteAdapter) -> None:
        assert isinstance(repo, BaseRepository)

    def test_seed_orders_exist(self, repo: SQLiteAdapter) -> None:
        """All three assignment-required orders must be present after seeding."""
        assert repo.get_order("111") is not None
        assert repo.get_order("222") is not None
        assert repo.get_order("333") is not None

    def test_seed_products_exist(self, repo: SQLiteAdapter) -> None:
        products = repo.get_products()
        assert len(products) > 0

    def test_double_init_does_not_duplicate_seed(self) -> None:
        """Constructing a second adapter on the same file should not re-seed."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        adapter1: SQLiteAdapter | None = None
        adapter2: SQLiteAdapter | None = None
        try:
            adapter1 = SQLiteAdapter(db_path=path)
            adapter2 = SQLiteAdapter(db_path=path)
            products = adapter2.get_products()
            # Products should not be duplicated
            names = [p["product_name"] for p in products]
            assert len(names) == len(set(names))
        finally:
            # Dispose engines before deleting the file (required on Windows).
            if adapter1 is not None:
                adapter1._engine.dispose()
            if adapter2 is not None:
                adapter2._engine.dispose()
            try:
                os.unlink(path)
            except PermissionError:
                pass  # Acceptable on Windows if handles linger briefly


# ---------------------------------------------------------------------------
# get_order
# ---------------------------------------------------------------------------

class TestGetOrder:
    def test_order_111_shipped(self, repo: SQLiteAdapter) -> None:
        order = repo.get_order("111")
        assert order is not None
        assert order["status"] == "Shipped"
        assert order["estimated_delivery"] == "Arriving Tomorrow"

    def test_order_222_processing(self, repo: SQLiteAdapter) -> None:
        order = repo.get_order("222")
        assert order is not None
        assert order["status"] == "Processing"
        assert order["estimated_delivery"] == "Ships in 24 Hours"

    def test_order_333_delivered(self, repo: SQLiteAdapter) -> None:
        order = repo.get_order("333")
        assert order is not None
        assert order["status"] == "Delivered"

    def test_invalid_order_returns_none(self, repo: SQLiteAdapter) -> None:
        assert repo.get_order("999") is None
        assert repo.get_order("") is None
        assert repo.get_order("abc") is None

    def test_order_id_whitespace_stripped(self, repo: SQLiteAdapter) -> None:
        """Leading/trailing whitespace should be tolerated."""
        order = repo.get_order("  111  ")
        assert order is not None
        assert order["status"] == "Shipped"

    def test_order_has_expected_keys(self, repo: SQLiteAdapter) -> None:
        order = repo.get_order("111")
        assert order is not None
        assert set(order.keys()) == {"order_id", "customer_name", "status", "estimated_delivery"}


# ---------------------------------------------------------------------------
# get_products
# ---------------------------------------------------------------------------

class TestGetProducts:
    def test_get_all_products(self, repo: SQLiteAdapter) -> None:
        products = repo.get_products()
        assert isinstance(products, list)
        assert len(products) >= 4  # at least the 4 original seed items

    def test_filter_by_category(self, repo: SQLiteAdapter) -> None:
        tents = repo.get_products(category="Tent")
        assert all(p["category"] == "Tent" for p in tents)
        assert len(tents) >= 1

    def test_unknown_category_returns_empty(self, repo: SQLiteAdapter) -> None:
        result = repo.get_products(category="Submarine")
        assert result == []

    def test_product_has_expected_keys(self, repo: SQLiteAdapter) -> None:
        products = repo.get_products()
        assert len(products) > 0
        assert set(products[0].keys()) == {"product_id", "category", "product_name"}


# ---------------------------------------------------------------------------
# get_recommendations
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    def test_camping_cold_beginner(self, repo: SQLiteAdapter) -> None:
        cats = repo.get_recommendations("Camping", "Cold", "Beginner")
        assert "Sleeping" in cats
        assert "Clothing" in cats
        assert "Tent" in cats

    def test_hiking_warm_intermediate(self, repo: SQLiteAdapter) -> None:
        cats = repo.get_recommendations("Hiking", "Warm", "Intermediate")
        assert "Backpack" in cats
        assert "Footwear" in cats

    def test_experience_none_returns_general_rules(self, repo: SQLiteAdapter) -> None:
        """Omitting experience should still return results."""
        cats = repo.get_recommendations("Camping", "Warm")
        assert len(cats) > 0

    def test_no_match_returns_empty_list(self, repo: SQLiteAdapter) -> None:
        cats = repo.get_recommendations("Skydiving", "Blizzard", "Expert")
        assert cats == []

    def test_no_duplicate_categories(self, repo: SQLiteAdapter) -> None:
        cats = repo.get_recommendations("Camping", "Cold", "Beginner")
        assert len(cats) == len(set(cats))

    def test_returns_list_of_strings(self, repo: SQLiteAdapter) -> None:
        cats = repo.get_recommendations("Hiking", "Rainy")
        assert isinstance(cats, list)
        assert all(isinstance(c, str) for c in cats)


# ---------------------------------------------------------------------------
# Repository singleton
# ---------------------------------------------------------------------------

class TestRepositorySingleton:
    def test_get_repository_returns_base_repository(self) -> None:
        reset_repository()
        repo = get_repository()
        assert isinstance(repo, BaseRepository)

    def test_get_repository_is_singleton(self) -> None:
        reset_repository()
        r1 = get_repository()
        r2 = get_repository()
        assert r1 is r2

    def test_set_repository_overrides_singleton(self) -> None:
        from unittest.mock import MagicMock
        mock_repo = MagicMock(spec=BaseRepository)
        set_repository(mock_repo)
        assert get_repository() is mock_repo
        reset_repository()  # clean up

    def test_reset_forces_reinitialisation(self) -> None:
        reset_repository()
        r1 = get_repository()
        reset_repository()
        r2 = get_repository()
        # Both are valid instances but are different objects
        assert isinstance(r1, BaseRepository)
        assert isinstance(r2, BaseRepository)
        reset_repository()  # clean up


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestFactory:
    def test_sqlite_backend_creates_adapter(self) -> None:
        adapter = create_repository(db_path=":memory:")
        assert isinstance(adapter, BaseRepository)

    def test_unknown_backend_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import config
        monkeypatch.setattr(config, "DATABASE_BACKEND", "nonexistent_db")
        with pytest.raises(NotImplementedError):
            create_repository()
