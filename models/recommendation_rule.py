"""
models/recommendation_rule.py
------------------------------
SQLAlchemy ORM model for the ``recommendation_rules`` table.

Each row maps a combination of user preferences (activity, weather,
optionally experience) to a product category.  The Recommendation Service
queries this table via the repository interface to suggest products.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RecommendationRule(Base):
    """
    A single recommendation rule mapping preferences to a product category.

    Attributes
    ----------
    id:
        Auto-incremented primary key.
    activity:
        Required — the user's activity (e.g. ``"Camping"``, ``"Hiking"``).
    weather:
        Required — expected weather conditions (e.g. ``"Cold"``, ``"Warm"``).
    experience:
        Optional — user's experience level (e.g. ``"Beginner"``).
        ``None`` means this rule matches regardless of experience.
    category:
        The product category to recommend (e.g. ``"Tent"``).
    """

    __tablename__ = "recommendation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity: Mapped[str] = mapped_column(String, nullable=False)
    weather: Mapped[str] = mapped_column(String, nullable=False)
    experience: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return (
            f"RecommendationRule(activity={self.activity!r}, "
            f"weather={self.weather!r}, "
            f"experience={self.experience!r}, "
            f"category={self.category!r})"
        )
