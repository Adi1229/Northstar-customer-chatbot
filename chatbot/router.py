"""
chatbot/router.py
-----------------
Intent routing table for the NorthStar chatbot.

The ``IntentRouter`` maps intent labels (returned by the NLP classifier)
to the handler method names on ``ConversationManager``.

Adding a new intent requires:
    1. Add examples to ``nlp/intents.json``.
    2. Add a row to ``ROUTING_TABLE`` below.
    3. Implement the corresponding ``_handle_<intent>`` method in
       ``ConversationManager``.
    No other files need to change.
"""

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routing table
# Maps intent label → handler method name on ConversationManager.
# ---------------------------------------------------------------------------

ROUTING_TABLE: dict[str, str] = {
    "greeting":               "_handle_greeting",
    "track_order":            "_handle_track_order",
    "return_policy":          "_handle_return_policy",
    "shipping_info":          "_handle_shipping_info",
    "product_recommendation": "_handle_product_recommendation",
    "human_handoff":          "_handle_human_handoff",
    "goodbye":                "_handle_goodbye",
    "fallback":               "_handle_fallback",
}


class IntentRouter:
    """
    Resolves an intent label to a handler method name.

    The ``ConversationManager`` calls ``get_handler(intent)`` and then
    dispatches to the returned method on itself via ``getattr``.

    This indirection keeps the routing table separate from the
    orchestration logic, making both independently testable.
    """

    def __init__(self, table: dict[str, str] | None = None) -> None:
        self._table = table or ROUTING_TABLE

    def get_handler(self, intent: str) -> str:
        """
        Return the handler method name for the given intent.

        Falls back to the ``fallback`` handler for unknown intents so the
        application never raises a ``KeyError`` on user input.

        Parameters
        ----------
        intent:
            An intent label string (e.g. ``"track_order"``).

        Returns
        -------
        str
            The method name to call on ``ConversationManager``.
        """
        handler = self._table.get(intent)
        if handler is None:
            logger.warning(
                "IntentRouter: no handler registered for intent=%r — using fallback.",
                intent,
            )
            handler = self._table["fallback"]
        return handler

    @property
    def registered_intents(self) -> list[str]:
        """Return all intent labels that have registered handlers."""
        return list(self._table.keys())
