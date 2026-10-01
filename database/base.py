"""
database/base.py
----------------
Abstract Base Class (ABC) for all database repository adapters.

Every storage backend (SQLite, PostgreSQL, REST API, etc.) must subclass
``BaseRepository`` and implement all abstract methods. Business services
depend only on this interface — they never import a concrete adapter.

This fulfils the Repository Pattern described in ARCHITECTURE.md and
DATABASE_DESIGN.md, ensuring the persistence layer is swappable without
touching any business logic.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseRepository(ABC):
    """
    Abstract repository interface for the NorthStar chatbot.

    All database adapters must implement this contract exactly.
    """

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    @abstractmethod
    def get_order(self, order_id: str) -> dict[str, Any] | None:
        """
        Retrieve a single order by its ID.

        Parameters
        ----------
        order_id:
            The order identifier (e.g. ``"111"``).

        Returns
        -------
        dict
            A mapping of order fields if found, or ``None`` if the order
            does not exist.
        """
        ...

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    @abstractmethod
    def get_products(self, category: str | None = None) -> list[dict[str, Any]]:
        """
        Retrieve products, optionally filtered by category.

        Parameters
        ----------
        category:
            Product category string (e.g. ``"Tent"``).  Pass ``None`` to
            retrieve all products.

        Returns
        -------
        list[dict]
            A list of product records as dictionaries.
        """
        ...

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    @abstractmethod
    def get_recommendations(
        self,
        activity: str,
        weather: str,
        experience: str | None = None,
    ) -> list[str]:
        """
        Return recommended product categories matching the user's preferences.

        Parameters
        ----------
        activity:
            The user's activity (e.g. ``"Camping"``).
        weather:
            The expected weather (e.g. ``"Cold"``).
        experience:
            The user's experience level (e.g. ``"Beginner"``).
            Optional — when omitted, experience is not used as a filter.

        Returns
        -------
        list[str]
            A list of recommended category names.
        """
        ...
