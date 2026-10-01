"""
services/recommendation_service.py
------------------------------------
Business service for product recommendations.

Responsibilities:
  - Accept user preferences (activity, weather, optional experience).
  - Query the repository for matching recommendation rules.
  - Look up product names for each recommended category.
  - Format and return a user-facing recommendation list.

All database access occurs through the repository interface only.
"""

import logging

from chatbot.schemas import ServiceResult
from database.repository import get_repository

logger = logging.getLogger(__name__)


# Category → display emoji mapping for formatted output.
_CATEGORY_EMOJI: dict[str, str] = {
    "Tent":        "⛺",
    "Sleeping":    "🛏️",
    "Clothing":    "🧥",
    "Backpack":    "🎒",
    "Footwear":    "👟",
    "Rain Jacket": "🌧️",
}
_DEFAULT_EMOJI = "🏕️"


class RecommendationService:
    """
    Recommends product categories based on user preferences.

    Parameters
    ----------
    repository:
        A ``BaseRepository`` instance.  When ``None``, the module-level
        singleton from ``database.repository`` is used.
    """

    def __init__(self, repository=None) -> None:
        self._repo = repository or get_repository()

    def get_recommendations(
        self,
        activity: str,
        weather: str,
        experience: str | None = None,
    ) -> ServiceResult:
        """
        Return product recommendations for the given preferences.

        Parameters
        ----------
        activity:
            User's planned activity (e.g. ``"Camping"``).
        weather:
            Expected weather conditions (e.g. ``"Cold"``).
        experience:
            Optional experience level (e.g. ``"Beginner"``).

        Returns
        -------
        ServiceResult
            ``success=True`` with formatted recommendation text,
            or ``success=False`` if no rules match or a repository error occurs.
        """
        activity = activity.strip().title()
        weather = weather.strip().title()

        if not activity or not weather:
            logger.warning(
                "get_recommendations: missing required fields activity=%r weather=%r",
                activity, weather,
            )
            return ServiceResult(
                success=False,
                error="I need both your activity and weather conditions to make recommendations.",
            )

        logger.info(
            "get_recommendations: activity=%r weather=%r experience=%r (normalised to title case)",
            activity, weather, experience,
        )

        try:
            categories = self._repo.get_recommendations(
                activity=activity,
                weather=weather,
                experience=experience,
            )
        except Exception as exc:
            logger.error("get_recommendations: repository error — %s", exc)
            return ServiceResult(
                success=False,
                error="I'm having trouble fetching recommendations right now. Please try again.",
            )

        if not categories:
            logger.info(
                "get_recommendations: no rules matched activity=%r weather=%r",
                activity, weather,
            )
            return ServiceResult(success=True, data=[])

        # Look up concrete product names for each category.
        product_lines = self._build_product_lines(categories)
        message = self._format_response(activity, weather, product_lines)
        return ServiceResult(success=True, data=message)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_product_lines(self, categories: list[str]) -> list[str]:
        """
        For each recommended category, fetch a product name and format
        a display line.

        Parameters
        ----------
        categories:
            List of category strings from the repository.

        Returns
        -------
        list[str]
            Formatted lines like ``"⛺ **Tent** — 4-Season Tent"``.
        """
        lines: list[str] = []
        for category in categories:
            try:
                products = self._repo.get_products(category=category)
            except Exception as exc:
                logger.warning("_build_product_lines: error fetching category=%r — %s", category, exc)
                products = []

            emoji = _CATEGORY_EMOJI.get(category, _DEFAULT_EMOJI)

            if products:
                product_name = products[0]["product_name"]
                lines.append(f"{emoji} **{category}** — {product_name}")
            else:
                lines.append(f"{emoji} **{category}**")

        return lines

    @staticmethod
    def _format_response(activity: str, weather: str, product_lines: list[str]) -> str:
        """Assemble the final recommendation message."""
        header = (
            f"Based on your preferences for **{activity}** in **{weather}** weather, "
            f"here's what I recommend:\n"
        )
        body = "\n".join(f"• {line}" for line in product_lines)
        footer = "\nWould you like more information about any of these products?"
        return header + body + footer
