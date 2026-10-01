"""
models/product.py
-----------------
SQLAlchemy ORM model for the ``products`` table.

Products represent the item catalogue.  Recommendation logic lives in the
separate ``recommendation_rules`` table — products are not directly linked
to rules in the demo schema; the category column is the join key.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Product(Base):
    """
    Represents a single product in the NorthStar catalogue.

    Attributes
    ----------
    product_id:
        Auto-incremented primary key.
    category:
        Product category (e.g. ``"Tent"``, ``"Sleeping"``).
        Used to link recommendation rules to concrete products.
    product_name:
        Display name of the product (e.g. ``"4-Season Tent"``).
    """

    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    product_name: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Product(product_id={self.product_id!r}, "
            f"category={self.category!r}, "
            f"product_name={self.product_name!r})"
        )
