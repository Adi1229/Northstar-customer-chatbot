"""
models/order.py
---------------
SQLAlchemy ORM model for the ``orders`` table.

Maps to the schema defined in ``data/schema.sql``.
Business services must never interact with this model directly —
all access goes through the Repository interface (``database/base.py``).
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Order(Base):
    """
    Represents a customer order stored in the ``orders`` table.

    Attributes
    ----------
    order_id:
        Primary key — the order number (e.g. ``"111"``).
    customer_name:
        Name of the customer (demo value: ``"Demo Customer"``).
    status:
        Current order status: ``"Processing"``, ``"Shipped"``, or ``"Delivered"``.
    estimated_delivery:
        Human-readable ETA string (e.g. ``"Arriving Tomorrow"``).
    """

    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    estimated_delivery: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return (
            f"Order(order_id={self.order_id!r}, "
            f"status={self.status!r}, "
            f"estimated_delivery={self.estimated_delivery!r})"
        )
