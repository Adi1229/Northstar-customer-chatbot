"""
chatbot/state_manager.py
------------------------
Session state for the NorthStar chatbot conversation.

The ``SessionState`` dataclass holds all context for a single chat session.
It is owned by the ``ConversationManager`` and never shared with services,
the NLP layer, or the UI.

State exists only in memory for the duration of one chat session.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Pending-question sentinel values
# Used by the Conversation Manager to track what it is waiting for.
# ---------------------------------------------------------------------------

PENDING_ORDER_ID               = "order_id"
PENDING_RECOMMENDATION_ACTIVITY = "recommendation_activity"
PENDING_RECOMMENDATION_WEATHER  = "recommendation_weather"


# ---------------------------------------------------------------------------
# Conversation mode constants
# Controls whether the Conversation Manager routes through NLP or holds
# the session in live agent mode.
# ---------------------------------------------------------------------------

MODE_NORMAL     = "NORMAL"
MODE_LIVE_AGENT = "LIVE_AGENT"


@dataclass
class SessionState:
    """
    All conversational context for a single chat session.

    Attributes
    ----------
    session_id:
        Unique identifier generated at session start.
    current_intent:
        The intent currently being handled.
    previous_intent:
        The intent that was handled before the current one.
    pending_question:
        When set, the next user message is treated as an answer to a
        clarifying question rather than a new intent.  One of the
        ``PENDING_*`` constants above.
    last_order_id:
        The most recently referenced order ID.  Enables follow-up
        questions like "Can I return *it*?" to resolve contextually.
    recommendation_context:
        Collected user preferences for product recommendations.
        Keys: ``"activity"``, ``"weather"``, ``"experience"`` (optional).
    conversation_history:
        Ordered list of ``{"role": "user"|"bot", "message": str}`` dicts.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_intent: str | None = None
    previous_intent: str | None = None
    pending_question: str | None = None
    last_order_id: str | None = None
    recommendation_context: dict[str, str] = field(default_factory=dict)
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    conversation_mode: str = MODE_NORMAL

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_message(self, role: str, message: str) -> None:
        """
        Append a message to the conversation history.

        Parameters
        ----------
        role:
            ``"user"`` or ``"bot"``.
        message:
            The message text.
        """
        self.conversation_history.append({"role": role, "message": message})

    def set_intent(self, intent: str) -> None:
        """
        Update the active intent, pushing the current one to previous.

        Parameters
        ----------
        intent:
            The new intent label.
        """
        self.previous_intent = self.current_intent
        self.current_intent = intent

    def clear_pending(self) -> None:
        """Clear the pending question flag."""
        self.pending_question = None

    def reset(self) -> None:
        """
        Reset all session fields to their initial values.

        A new ``session_id`` is generated so the reset session is
        distinguishable from the previous one in logs.
        """
        self.session_id = str(uuid.uuid4())
        self.current_intent = None
        self.previous_intent = None
        self.pending_question = None
        self.last_order_id = None
        self.recommendation_context = {}
        self.conversation_history = []
        self.conversation_mode = MODE_NORMAL
