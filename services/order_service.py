"""
services/order_service.py
--------------------------
Business service for order tracking.

Responsibilities:
  - Accept an order ID from the Conversation Manager.
  - Validate the input.
  - Query the repository for order data.
  - Format a user-facing response.
  - Return a ``ServiceResult``.

This service knows nothing about Streamlit, SQLite, or NLP.
It receives typed inputs and returns typed outputs only.
"""

import logging

from chatbot.schemas import ServiceResult
from database.repository import get_repository

logger = logging.getLogger(__name__)


class OrderService:
    """
    Handles order status lookup and formatting.

    Parameters
    ----------
    repository:
        A ``BaseRepository`` instance.  When ``None``, the module-level
        singleton from ``database.repository`` is used.  Pass an explicit
        repository in tests for isolation.
    """

    def __init__(self, repository=None) -> None:
        self._repo = repository or get_repository()

    def get_order_status(self, order_id: str) -> ServiceResult:
        """
        Look up an order and return a formatted status message.

        Parameters
        ----------
        order_id:
            The order number provided by the user (e.g. ``"111"``).

        Returns
        -------
        ServiceResult
            ``success=True`` with a human-readable ``data`` string,
            or ``success=False`` with a user-safe ``error`` message.
        """
        order_id = order_id.strip()

        if not order_id:
            logger.warning("get_order_status: empty order_id received.")
            return ServiceResult(
                success=False,
                error="It looks like you didn't provide an order number. Could you try again?",
            )

        logger.info("get_order_status: querying order_id=%r", order_id)

        try:
            order = self._repo.get_order(order_id)
        except Exception as exc:
            logger.error("get_order_status: repository error — %s", exc)
            return ServiceResult(
                success=False,
                error="I'm having trouble retrieving your order right now. Please try again shortly.",
            )

        if order is None:
            logger.info("get_order_status: order_id=%r not found.", order_id)
            return ServiceResult(
                success=False,
                error=(
                    f"I couldn't find an order with number **{order_id}**. "
                    "Please double-check the number and try again."
                ),
            )

        message = self._format_order_response(order)
        logger.info(
            "get_order_status: order_id=%r status=%r → success",
            order_id,
            order.get("status"),
        )
        return ServiceResult(success=True, data=message)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_order_response(order: dict) -> str:
        """Format an order dict into a user-facing message."""
        status = order.get("status", "Unknown")
        eta = order.get("estimated_delivery", "")
        order_id = order.get("order_id", "")

        status_emoji = {
            "Shipped":    "🚚",
            "Processing": "⏳",
            "Delivered":  "✅",
        }.get(status, "📦")

        lines = [
            f"Here's the status for order **#{order_id}**:\n",
            f"{status_emoji} **Status:** {status}",
        ]
        if eta:
            lines.append(f"📅 **Estimated Delivery:** {eta}")

        lines.append("\nIs there anything else I can help you with?")
        return "\n".join(lines)
