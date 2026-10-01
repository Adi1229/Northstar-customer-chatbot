"""
database/sqlite_adapter.py
---------------------------
Concrete SQLite implementation of ``BaseRepository``.

This adapter:
  - Creates the SQLite database and tables on first run (via SQLAlchemy).
  - Seeds the database with demo data if tables are empty.
  - Implements all repository methods defined in ``BaseRepository``.

To swap to PostgreSQL: implement a ``PostgreSQLAdapter`` that extends
``BaseRepository`` with the same method signatures, then update
``config.DATABASE_BACKEND``.  No other file needs to change.
"""

import logging
from typing import Any

from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import Session

import config
from database.base import BaseRepository
from models.base import Base
from models.order import Order
from models.product import Product
from models.recommendation_rule import RecommendationRule

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Demo seed data (mirrors data/seed.sql)
# ---------------------------------------------------------------------------

_SEED_ORDERS: list[dict[str, str]] = [
    {"order_id": "111", "customer_name": "Demo Customer", "status": "Shipped",    "estimated_delivery": "Arriving Tomorrow"},
    {"order_id": "222", "customer_name": "Demo Customer", "status": "Processing", "estimated_delivery": "Ships in 24 Hours"},
    {"order_id": "333", "customer_name": "Demo Customer", "status": "Delivered",  "estimated_delivery": "Delivered"},
]

_SEED_PRODUCTS: list[dict[str, str]] = [
    {"category": "Tent",        "product_name": "4-Season Tent"},
    {"category": "Sleeping",    "product_name": "Insulated Sleeping Bag"},
    {"category": "Clothing",    "product_name": "Insulated Jacket"},
    {"category": "Backpack",    "product_name": "60L Hiking Backpack"},
    {"category": "Footwear",    "product_name": "Waterproof Hiking Boots"},
    {"category": "Rain Jacket", "product_name": "Packable Rain Jacket"},
]

_SEED_RULES: list[dict[str, str | None]] = [
    {"activity": "Camping", "weather": "Cold",  "experience": "Beginner",     "category": "Sleeping"},
    {"activity": "Camping", "weather": "Cold",  "experience": "Beginner",     "category": "Clothing"},
    {"activity": "Camping", "weather": "Cold",  "experience": "Beginner",     "category": "Tent"},
    {"activity": "Camping", "weather": "Cold",  "experience": "Intermediate", "category": "Tent"},
    {"activity": "Camping", "weather": "Cold",  "experience": "Intermediate", "category": "Sleeping"},
    {"activity": "Camping", "weather": "Warm",  "experience": None,           "category": "Tent"},
    {"activity": "Camping", "weather": "Warm",  "experience": None,           "category": "Backpack"},
    {"activity": "Hiking",  "weather": "Warm",  "experience": "Intermediate", "category": "Backpack"},
    {"activity": "Hiking",  "weather": "Warm",  "experience": "Intermediate", "category": "Footwear"},
    {"activity": "Hiking",  "weather": "Rainy", "experience": None,           "category": "Rain Jacket"},
    {"activity": "Hiking",  "weather": "Rainy", "experience": None,           "category": "Footwear"},
]


class SQLiteAdapter(BaseRepository):
    """
    SQLite-backed implementation of ``BaseRepository``.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Defaults to
        ``config.DATABASE_PATH``.

    On construction the adapter:
    1. Creates (or connects to) the SQLite file.
    2. Creates all tables if they do not already exist.
    3. Seeds demo data if the tables are empty.
    """

    def __init__(self, db_path: str | None = None) -> None:
        resolved_path = db_path or config.DATABASE_PATH
        connection_url = f"sqlite:///{resolved_path}"
        logger.info("SQLiteAdapter: connecting to %s", connection_url)

        self._engine = create_engine(
            connection_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        self._initialise()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _initialise(self) -> None:
        """Create tables and seed demo data on first run."""
        Base.metadata.create_all(self._engine)
        logger.info("SQLiteAdapter: tables created/verified.")
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        """Insert demo data only when the orders table has no rows."""
        with Session(self._engine) as session:
            order_count = session.query(Order).count()
            if order_count > 0:
                logger.debug("SQLiteAdapter: database already seeded, skipping.")
                return

            logger.info("SQLiteAdapter: seeding demo data.")
            session.add_all([Order(**row) for row in _SEED_ORDERS])
            session.add_all([Product(**row) for row in _SEED_PRODUCTS])
            session.add_all([RecommendationRule(**row) for row in _SEED_RULES])
            session.commit()
            logger.info("SQLiteAdapter: seeding complete.")

    # ------------------------------------------------------------------
    # BaseRepository implementation
    # ------------------------------------------------------------------

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        """
        Retrieve a single order by ID.

        Parameters
        ----------
        order_id:
            The order identifier string (e.g. ``"111"``).

        Returns
        -------
        dict or None
            A dictionary of order fields, or ``None`` if not found.
        """
        with Session(self._engine) as session:
            stmt = select(Order).where(Order.order_id == order_id.strip())
            row = session.scalars(stmt).first()
            if row is None:
                logger.debug("get_order: order_id=%r not found.", order_id)
                return None
            return {
                "order_id": row.order_id,
                "customer_name": row.customer_name,
                "status": row.status,
                "estimated_delivery": row.estimated_delivery,
            }

    def get_products(self, category: str | None = None) -> list[dict[str, Any]]:
        """
        Retrieve products, optionally filtered by category.

        Parameters
        ----------
        category:
            Category name to filter on.  Pass ``None`` for all products.

        Returns
        -------
        list[dict]
            A list of product record dictionaries.
        """
        with Session(self._engine) as session:
            stmt = select(Product)
            if category is not None:
                stmt = stmt.where(Product.category == category)
            rows = session.scalars(stmt).all()
            return [
                {
                    "product_id": r.product_id,
                    "category": r.category,
                    "product_name": r.product_name,
                }
                for r in rows
            ]

    def get_recommendations(
        self,
        activity: str,
        weather: str,
        experience: str | None = None,
    ) -> list[str]:
        """
        Return recommended product categories for the given preferences.

        Matching strategy:
        - Always matches on ``activity`` and ``weather``.
        - If ``experience`` is provided, returns rules where
          ``experience`` equals the value **or** ``experience`` is NULL
          (rules that apply to any experience level).
        - If ``experience`` is omitted (``None``), all rules for the
          activity/weather combination are returned.

        Parameters
        ----------
        activity:
            User's planned activity (case-sensitive, e.g. ``"Camping"``).
        weather:
            Expected weather (case-sensitive, e.g. ``"Cold"``).
        experience:
            Optional experience level (e.g. ``"Beginner"``).

        Returns
        -------
        list[str]
            Unique category names, ordered as stored.
        """
        with Session(self._engine) as session:
            stmt = select(RecommendationRule).where(
                RecommendationRule.activity == activity,
                RecommendationRule.weather == weather,
            )
            if experience is not None:
                # Include rules specific to this experience level AND
                # general rules (experience IS NULL).
                stmt = stmt.where(
                    or_(
                        RecommendationRule.experience == experience,
                        RecommendationRule.experience.is_(None),
                    )
                )
            rows = session.scalars(stmt).all()

            # De-duplicate while preserving insertion order.
            seen: set[str] = set()
            categories: list[str] = []
            for row in rows:
                if row.category not in seen:
                    seen.add(row.category)
                    categories.append(row.category)

            logger.debug(
                "get_recommendations: activity=%r weather=%r experience=%r → %r",
                activity, weather, experience, categories,
            )
            return categories
