"""
chatbot/schemas.py
------------------
Shared dataclasses (internal API contracts) used across the chatbot layers.

These types form the stable internal interfaces described in API_CONTRACT.md.
No layer should pass raw dicts or strings across module boundaries; use these
typed structures instead.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntentResult:
    """
    Output of the NLP intent classifier.

    Attributes
    ----------
    intent:
        The predicted intent label (e.g. ``"track_order"``).
    confidence:
        Cosine similarity score in the range [0.0, 1.0].
    """

    intent: str
    confidence: float


@dataclass
class ChatResponse:
    """
    Response returned by the Conversation Manager to the Streamlit UI.

    Attributes
    ----------
    message:
        The user-facing reply text.
    intent:
        The intent that produced this response.
    requires_followup:
        ``True`` when the bot has asked a clarifying question and is
        waiting for more input before calling a business service.
    """

    message: str
    intent: str
    requires_followup: bool = False


@dataclass
class ServiceResult:
    """
    Structured result returned by every business service.

    Services must never raise exceptions to their callers or expose
    stack traces. Instead they return a ``ServiceResult`` with
    ``success=False`` and a user-safe ``error`` message.

    Attributes
    ----------
    success:
        ``True`` when the service completed successfully.
    data:
        Arbitrary payload on success (type depends on the service).
    error:
        Human-readable error message when ``success`` is ``False``.
    """

    success: bool
    data: Any = None
    error: str = ""
