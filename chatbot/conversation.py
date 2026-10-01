"""
chatbot/conversation.py
-----------------------
Conversation Manager — the central orchestrator of the NorthStar chatbot.

Responsibilities (per ARCHITECTURE.md and CONVERSATION_MANAGER.md):
  - Receive every user message.
  - Call the NLP intent classifier.
  - Manage conversational state (via SessionState).
  - Route requests to the correct business service (via IntentRouter).
  - Handle multi-turn flows (order ID collection, recommendation questions).
  - Support context switching (user changes topic mid-conversation).
  - Return a ChatResponse to the UI.

Does NOT:
  - Import or reference Streamlit.
  - Access the database directly.
  - Perform semantic similarity calculations.

Services are injected via the constructor so the manager remains testable
without a real database or service implementations.
"""

import logging
from typing import Any, Protocol, runtime_checkable

import config
from chatbot.router import IntentRouter
from chatbot.schemas import ChatResponse, IntentResult
from chatbot.state_manager import (
    SessionState,
    PENDING_ORDER_ID,
    PENDING_RECOMMENDATION_ACTIVITY,
    PENDING_RECOMMENDATION_WEATHER,
    MODE_NORMAL,
    MODE_LIVE_AGENT,
)
from nlp.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Service Protocols
# Lightweight structural interfaces so ConversationManager can type-check
# injected services without importing concrete service classes (which don't
# exist until Phase 4).
# ---------------------------------------------------------------------------

@runtime_checkable
class OrderServiceProtocol(Protocol):
    def get_order_status(self, order_id: str) -> Any: ...


@runtime_checkable
class ReturnServiceProtocol(Protocol):
    def get_return_policy(self) -> Any: ...
    def get_shipping_info(self) -> Any: ...


@runtime_checkable
class RecommendationServiceProtocol(Protocol):
    def get_recommendations(
        self,
        activity: str,
        weather: str,
        experience: str | None = None,
    ) -> Any: ...


@runtime_checkable
class HandoffServiceProtocol(Protocol):
    def simulate_handoff(self) -> Any: ...


# ---------------------------------------------------------------------------
# Canned response strings
# Inline responses that don't require a service call.
# ---------------------------------------------------------------------------

_MSG_GREETING = (
    "Hello! Welcome to NorthStar Outdoor Gear support 🏔️\n\n"
    "I can help you with:\n"
    "• **Order tracking** — ask about your order status\n"
    "• **Returns & exchanges** — learn about our return policy\n"
    "• **Shipping** — find out about delivery options\n"
    "• **Product recommendations** — get gear suggestions\n"
    "• **Live support** — connect with a human agent\n\n"
    "How can I help you today?"
)

_MSG_GOODBYE = (
    "Thank you for contacting NorthStar support! "
    "Have a great adventure out there 🏕️ Goodbye!"
)

_MSG_FALLBACK = (
    "I'm sorry, I didn't quite understand that.\n\n"
    "I can help you with:\n"
    "• Tracking an order\n"
    "• Return or exchange policy\n"
    "• Shipping information\n"
    "• Product recommendations\n"
    "• Connecting to a live agent\n\n"
    "Could you rephrase your question?"
)

_MSG_ASK_ORDER_ID    = "Sure! Could you please provide your **order number**?"
_MSG_ASK_ACTIVITY    = "I'd love to help you find the right gear! What activity are you planning? (e.g. Camping, Hiking, Trekking, Fishing)"
_MSG_ASK_WEATHER     = "Great! What kind of weather are you expecting? (e.g. Cold, Warm, Rainy)"
_MSG_SERVICE_UNAVAIL = "I'm sorry, that service is temporarily unavailable. Please try again later."
_MSG_NO_RECOMMEND    = "I couldn't find specific recommendations for those preferences. Try contacting our team for personalised advice."

# Supported activities for product recommendation (validated in conversation manager).
_VALID_ACTIVITIES: frozenset[str] = frozenset({"Camping", "Hiking", "Trekking", "Fishing"})

def _invalid_activity_msg() -> str:
    """Build the validation error message listing all supported activities."""
    bullet_list = "\n".join(f"• {a}" for a in sorted(_VALID_ACTIVITIES))
    return (
        "Sorry, I don't recognise that activity.\n\n"
        f"Please choose one of:\n{bullet_list}"
    )


_MSG_LIVE_AGENT_HOLD = (
    "You are currently connected to a **live support representative**.\n\n"
    'Type `menu`, `main menu`, or `exit` to return to the chatbot.'
)

_MSG_LIVE_AGENT_EXIT = (
    "You have exited live agent mode.\n\n"
    "Welcome back! How can I help you today?"
)


class ConversationManager:
    """
    Central orchestrator for the NorthStar chatbot.

    Parameters
    ----------
    classifier:
        A loaded ``IntentClassifier`` instance.
    order_service:
        An ``OrderServiceProtocol`` implementation (injected in Phase 4).
    return_service:
        A ``ReturnServiceProtocol`` implementation (injected in Phase 4).
    recommendation_service:
        A ``RecommendationServiceProtocol`` implementation (injected in Phase 4).
    handoff_service:
        A ``HandoffServiceProtocol`` implementation (injected in Phase 4).
    """

    def __init__(
        self,
        classifier: IntentClassifier,
        order_service: OrderServiceProtocol | None = None,
        return_service: ReturnServiceProtocol | None = None,
        recommendation_service: RecommendationServiceProtocol | None = None,
        handoff_service: HandoffServiceProtocol | None = None,
    ) -> None:
        self._classifier = classifier
        self._router = IntentRouter()
        self._state = SessionState()

        # Services injected — None until Phase 4
        self._order_service = order_service
        self._return_service = return_service
        self._recommendation_service = recommendation_service
        self._handoff_service = handoff_service

        logger.info(
            "ConversationManager: initialised (session_id=%s).",
            self._state.session_id,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_message(self, user_message: str) -> ChatResponse:
        """
        Process a user message and return a response.

        Parameters
        ----------
        user_message:
            Raw text from the user.

        Returns
        -------
        ChatResponse
            The bot's reply, active intent, and whether a follow-up is pending.
        """
        text = user_message.strip()

        if not text:
            return ChatResponse(
                message="Please type something so I can help you.",
                intent="fallback",
            )

        self._state.add_message("user", text)
        logger.info(
            "handle_message: session=%s text=%r pending=%r mode=%r",
            self._state.session_id[:8],
            text[:60],
            self._state.pending_question,
            self._state.conversation_mode,
        )

        # ------------------------------------------------------------------
        # LIVE_AGENT mode: bypass NLP completely and keep the user inside the
        # live agent workflow until they explicitly request to exit.
        # ------------------------------------------------------------------
        if self._state.conversation_mode == MODE_LIVE_AGENT:
            response = self._handle_live_agent_message(text)
            self._state.add_message("bot", response.message)
            return response

        # ------------------------------------------------------------------
        # If we're waiting for an answer to a clarifying question,
        # check whether the user has switched topics with high confidence
        # before treating the message as an answer.
        # ------------------------------------------------------------------
        if self._state.pending_question:
            response = self._try_context_switch_or_answer(text)
        else:
            response = self._classify_and_dispatch(text)

        self._state.add_message("bot", response.message)
        return response

    def reset_session(self) -> None:
        """
        Reset all conversation state for a fresh session.
        Called when the user clicks "New Conversation" in the UI.
        """
        old_id = self._state.session_id[:8]
        self._state.reset()
        logger.info(
            "reset_session: session %s → %s",
            old_id,
            self._state.session_id[:8],
        )

    @property
    def session_state(self) -> SessionState:
        """Read-only access to the session state (used by tests)."""
        return self._state

    @property
    def conversation_history(self) -> list[dict[str, str]]:
        """Return the full conversation history for display."""
        return list(self._state.conversation_history)

    @property
    def conversation_mode(self) -> str:
        """
        Current conversation mode: ``NORMAL`` or ``LIVE_AGENT``.

        Exposed as a public property so the UI layer can persist and
        restore the mode across ``@st.cache_resource`` cache resets
        without accessing internal state directly.
        """
        return self._state.conversation_mode

    @conversation_mode.setter
    def conversation_mode(self, mode: str) -> None:
        """
        Restore conversation mode.

        Called by the UI layer to rehydrate state after a cache miss
        (e.g. Streamlit hot-reload clears ``@st.cache_resource`` but
        ``st.session_state`` survives).

        Parameters
        ----------
        mode:
            One of ``MODE_NORMAL`` or ``MODE_LIVE_AGENT``.
        """
        logger.debug(
            "conversation_mode.setter: session=%s mode set to %r",
            self._state.session_id[:8],
            mode,
        )
        self._state.conversation_mode = mode

    # ------------------------------------------------------------------
    # Internal routing
    # ------------------------------------------------------------------

    def _try_context_switch_or_answer(self, text: str) -> ChatResponse:
        """
        Determine whether the user has changed topic or is answering the
        current pending question.

        If the classifier returns a *different* intent from the current one
        with HIGH confidence, treat it as a topic switch.
        Otherwise, treat the message as the answer to the pending question.

        Special case — PENDING_RECOMMENDATION_ACTIVITY:
            Context-switching is disabled for this step. Every input,
            regardless of what the NLP classifier would say, is forwarded
            directly to ``_receive_recommendation_activity()`` for contextual
            validation.  This prevents invalid activity text from being
            misclassified as a different intent and abandoning the
            recommendation workflow.
        """
        # Do NOT run NLP context-switch when validating activity input.
        # All text must pass through _receive_recommendation_activity first.
        if self._state.pending_question == PENDING_RECOMMENDATION_ACTIVITY:
            logger.debug(
                "_try_context_switch_or_answer: skipping context-switch for "
                "PENDING_RECOMMENDATION_ACTIVITY — forwarding to pending answer handler."
            )
            return self._handle_pending_answer(text)

        intent_result = self._classifier.classify(text)
        is_different_intent = (
            intent_result.intent != self._state.current_intent
            and intent_result.intent != "fallback"
            and intent_result.confidence >= config.NLP_CONFIDENCE_HIGH
        )

        if is_different_intent:
            logger.info(
                "_try_context_switch_or_answer: switching from %r to %r (confidence=%.2f)",
                self._state.current_intent,
                intent_result.intent,
                intent_result.confidence,
            )
            self._state.clear_pending()
            self._state.recommendation_context = {}
            return self._route(intent_result)

        # Treat as answer to pending question.
        return self._handle_pending_answer(text)

    def _classify_and_dispatch(self, text: str) -> ChatResponse:
        """Classify the message and route to the correct handler."""
        intent_result = self._classifier.classify(text)
        logger.info(
            "_classify_and_dispatch: intent=%r confidence=%.2f",
            intent_result.intent,
            intent_result.confidence,
        )
        return self._route(intent_result)

    def _route(self, intent_result: IntentResult) -> ChatResponse:
        """Update state and call the intent handler."""
        self._state.set_intent(intent_result.intent)
        handler_name = self._router.get_handler(intent_result.intent)
        handler = getattr(self, handler_name)
        return handler()

    # ------------------------------------------------------------------
    # Pending-answer handlers
    # ------------------------------------------------------------------

    def _handle_pending_answer(self, text: str) -> ChatResponse:
        """Dispatch an incoming answer to the correct pending-state handler."""
        pending = self._state.pending_question

        if pending == PENDING_ORDER_ID:
            return self._receive_order_id(text)
        if pending == PENDING_RECOMMENDATION_ACTIVITY:
            return self._receive_recommendation_activity(text)
        if pending == PENDING_RECOMMENDATION_WEATHER:
            return self._receive_recommendation_weather(text)

        # Unknown pending state — clear and fall back gracefully.
        logger.warning("_handle_pending_answer: unknown pending=%r", pending)
        self._state.clear_pending()
        return ChatResponse(message=_MSG_FALLBACK, intent="fallback")

    def _receive_order_id(self, text: str) -> ChatResponse:
        """Store the provided order ID and query the order service."""
        order_id = text.strip()
        self._state.last_order_id = order_id
        self._state.clear_pending()
        return self._call_order_service(order_id)

    def _receive_recommendation_activity(self, text: str) -> ChatResponse:
        """Validate and store the activity, then ask for weather."""
        # Normalise to title case for matching against valid set.
        normalised = text.strip().title()

        if normalised not in _VALID_ACTIVITIES:
            logger.info(
                "_receive_recommendation_activity: invalid input=%r, re-prompting.",
                text.strip(),
            )
            # Stay in the activity-pending state — do NOT advance to weather.
            self._state.pending_question = PENDING_RECOMMENDATION_ACTIVITY
            return ChatResponse(
                message=_invalid_activity_msg(),
                intent="product_recommendation",
                requires_followup=True,
            )

        self._state.recommendation_context["activity"] = normalised
        self._state.clear_pending()
        self._state.pending_question = PENDING_RECOMMENDATION_WEATHER
        return ChatResponse(
            message=_MSG_ASK_WEATHER,
            intent="product_recommendation",
            requires_followup=True,
        )

    def _receive_recommendation_weather(self, text: str) -> ChatResponse:
        """Store the weather condition and call the recommendation service."""
        self._state.recommendation_context["weather"] = text.strip()
        self._state.clear_pending()
        return self._call_recommendation_service()

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    def _handle_greeting(self) -> ChatResponse:
        return ChatResponse(message=_MSG_GREETING, intent="greeting")

    def _handle_goodbye(self) -> ChatResponse:
        return ChatResponse(message=_MSG_GOODBYE, intent="goodbye")

    def _handle_fallback(self) -> ChatResponse:
        return ChatResponse(message=_MSG_FALLBACK, intent="fallback")

    def _handle_track_order(self) -> ChatResponse:
        """
        Handle order-tracking intent.

        Always ask for the order number so that users can track different
        orders in the same session. ``last_order_id`` is kept in state for
        other purposes (e.g. return flows) but is NOT auto-reused here.
        """
        # Clear any previously cached order ID so the user is always prompted.
        # This is intentional: a user may have multiple orders and each
        # "track my order" request should ask which order they mean.
        self._state.last_order_id = None
        self._state.pending_question = PENDING_ORDER_ID
        return ChatResponse(
            message=_MSG_ASK_ORDER_ID,
            intent="track_order",
            requires_followup=True,
        )

    def _handle_return_policy(self) -> ChatResponse:
        if self._return_service is None:
            logger.warning("_handle_return_policy: return_service not injected.")
            return ChatResponse(message=_MSG_SERVICE_UNAVAIL, intent="return_policy")

        result = self._return_service.get_return_policy()
        if not result.success:
            return ChatResponse(message=result.error, intent="return_policy")
        return ChatResponse(message=result.data, intent="return_policy")

    def _handle_shipping_info(self) -> ChatResponse:
        if self._return_service is None:
            logger.warning("_handle_shipping_info: return_service not injected.")
            return ChatResponse(message=_MSG_SERVICE_UNAVAIL, intent="shipping_info")

        result = self._return_service.get_shipping_info()
        if not result.success:
            return ChatResponse(message=result.error, intent="shipping_info")
        return ChatResponse(message=result.data, intent="shipping_info")

    def _handle_product_recommendation(self) -> ChatResponse:
        """
        Handle product recommendation intent.

        Collect activity and weather before calling the service.
        Experience is optional (PRD limits to two clarifying questions).
        """
        ctx = self._state.recommendation_context

        if "activity" not in ctx:
            self._state.pending_question = PENDING_RECOMMENDATION_ACTIVITY
            return ChatResponse(
                message=_MSG_ASK_ACTIVITY,
                intent="product_recommendation",
                requires_followup=True,
            )

        if "weather" not in ctx:
            self._state.pending_question = PENDING_RECOMMENDATION_WEATHER
            return ChatResponse(
                message=_MSG_ASK_WEATHER,
                intent="product_recommendation",
                requires_followup=True,
            )

        return self._call_recommendation_service()

    def _handle_human_handoff(self) -> ChatResponse:
        if self._handoff_service is None:
            logger.warning("_handle_human_handoff: handoff_service not injected.")
            return ChatResponse(message=_MSG_SERVICE_UNAVAIL, intent="human_handoff")

        result = self._handoff_service.simulate_handoff()
        if not result.success:
            return ChatResponse(message=result.error, intent="human_handoff")

        # Enter LIVE_AGENT mode — subsequent messages bypass NLP classification.
        self._state.conversation_mode = MODE_LIVE_AGENT
        logger.info(
            "_handle_human_handoff: session=%s entering LIVE_AGENT mode.",
            self._state.session_id[:8],
        )
        return ChatResponse(message=result.data, intent="human_handoff")

    # ------------------------------------------------------------------
    # Live agent mode handler
    # ------------------------------------------------------------------

    def _handle_live_agent_message(self, text: str) -> ChatResponse:
        """
        Handle any message received while ``conversation_mode == MODE_LIVE_AGENT``.

        Exit commands (case-insensitive): ``exit``, ``menu``, ``main menu``.
        All other messages receive a holding reply that reminds the user they
        are still connected to a live representative.
        """
        _EXIT_COMMANDS = {"exit", "menu", "main menu"}

        if text.strip().lower() in _EXIT_COMMANDS:
            self._state.conversation_mode = MODE_NORMAL
            self._state.current_intent = None
            logger.info(
                "_handle_live_agent_message: session=%s exiting LIVE_AGENT mode.",
                self._state.session_id[:8],
            )
            return ChatResponse(
                message=_MSG_LIVE_AGENT_EXIT,
                intent="greeting",
            )

        logger.debug(
            "_handle_live_agent_message: session=%s forwarding message in LIVE_AGENT mode.",
            self._state.session_id[:8],
        )
        return ChatResponse(
            message=_MSG_LIVE_AGENT_HOLD,
            intent="human_handoff",
        )

    # ------------------------------------------------------------------
    # Service call helpers
    # ------------------------------------------------------------------

    def _call_order_service(self, order_id: str) -> ChatResponse:
        if self._order_service is None:
            logger.warning("_call_order_service: order_service not injected.")
            return ChatResponse(message=_MSG_SERVICE_UNAVAIL, intent="track_order")

        result = self._order_service.get_order_status(order_id)
        if not result.success:
            return ChatResponse(message=result.error, intent="track_order")
        return ChatResponse(message=result.data, intent="track_order")

    def _call_recommendation_service(self) -> ChatResponse:
        if self._recommendation_service is None:
            logger.warning("_call_recommendation_service: recommendation_service not injected.")
            return ChatResponse(message=_MSG_SERVICE_UNAVAIL, intent="product_recommendation")

        ctx = self._state.recommendation_context
        result = self._recommendation_service.get_recommendations(
            activity=ctx.get("activity", ""),
            weather=ctx.get("weather", ""),
            experience=ctx.get("experience"),
        )

        # Clear context so next recommendation flow starts fresh.
        self._state.recommendation_context = {}

        if not result.success:
            return ChatResponse(message=result.error, intent="product_recommendation")

        if not result.data:
            return ChatResponse(message=_MSG_NO_RECOMMEND, intent="product_recommendation")

        return ChatResponse(message=result.data, intent="product_recommendation")
