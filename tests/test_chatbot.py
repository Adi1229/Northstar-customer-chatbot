"""
tests/test_chatbot.py
---------------------
Tests for the Conversation Manager layer.

All tests use mock NLP classifiers and mock services so this suite
runs without model downloads, database files, or internet access.

Coverage
--------
TestSessionState
    Dataclass helpers, reset, history, PENDING_* constants.

TestIntentRouter
    Routing table lookup, unknown intent fallback, registered_intents.

TestConversationManagerGreetingGoodbye
    Inline responses that require no service.

TestConversationManagerFallback
    Unknown/low-confidence intent handling.

TestConversationManagerOrderTracking
    Multi-turn order flow: ask → receive ID → call service.
    Context re-use (last_order_id).
    Invalid order handling.

TestConversationManagerReturnPolicy
    Return policy and shipping info single-turn flows.

TestConversationManagerRecommendation
    Two-question recommendation flow (activity → weather → result).
    No-results handling.

TestConversationManagerHandoff
    Handoff simulation.

TestConversationManagerContextSwitching
    User changes topic mid-flow at high confidence.

TestConversationManagerServiceUnavailable
    Graceful handling when services are not injected.

TestConversationManagerEdgeCases
    Empty input, whitespace, reset_session.
"""

import pytest
from unittest.mock import MagicMock

from chatbot.conversation import ConversationManager
from chatbot.router import IntentRouter, ROUTING_TABLE
from chatbot.schemas import ChatResponse, IntentResult, ServiceResult
from chatbot.state_manager import (
    SessionState,
    PENDING_ORDER_ID,
    PENDING_RECOMMENDATION_ACTIVITY,
    PENDING_RECOMMENDATION_WEATHER,
)


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

def _make_classifier(intent: str, confidence: float = 0.95) -> MagicMock:
    """Return a mock IntentClassifier that always classifies to ``intent``."""
    mock = MagicMock()
    mock.classify.return_value = IntentResult(intent=intent, confidence=confidence)
    return mock


def _ok(text: str) -> ServiceResult:
    return ServiceResult(success=True, data=text)


def _err(msg: str) -> ServiceResult:
    return ServiceResult(success=False, error=msg)


def _make_order_service(result: ServiceResult | None = None) -> MagicMock:
    svc = MagicMock()
    svc.get_order_status.return_value = result or _ok("Your order has shipped.")
    return svc


def _make_return_service(
    policy: ServiceResult | None = None,
    shipping: ServiceResult | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc.get_return_policy.return_value = policy or _ok("30-day return policy.")
    svc.get_shipping_info.return_value = shipping or _ok("Standard shipping: 3-5 business days")
    return svc


def _make_recommendation_service(result: ServiceResult | None = None) -> MagicMock:
    svc = MagicMock()
    svc.get_recommendations.return_value = result or _ok("We recommend: Tent, Sleeping Bag.")
    return svc


def _make_handoff_service(result: ServiceResult | None = None) -> MagicMock:
    svc = MagicMock()
    svc.simulate_handoff.return_value = result or _ok("Connecting you to an agent...")
    return svc


# ---------------------------------------------------------------------------
# TestSessionState
# ---------------------------------------------------------------------------

class TestSessionState:

    def test_initial_state(self) -> None:
        state = SessionState()
        assert state.session_id
        assert state.current_intent is None
        assert state.pending_question is None
        assert state.last_order_id is None
        assert state.recommendation_context == {}
        assert state.conversation_history == []

    def test_add_message(self) -> None:
        state = SessionState()
        state.add_message("user", "Hello")
        state.add_message("bot", "Hi there!")
        assert len(state.conversation_history) == 2
        assert state.conversation_history[0] == {"role": "user", "message": "Hello"}

    def test_set_intent_updates_previous(self) -> None:
        state = SessionState()
        state.set_intent("greeting")
        assert state.current_intent == "greeting"
        assert state.previous_intent is None

        state.set_intent("track_order")
        assert state.current_intent == "track_order"
        assert state.previous_intent == "greeting"

    def test_clear_pending(self) -> None:
        state = SessionState()
        state.pending_question = PENDING_ORDER_ID
        state.clear_pending()
        assert state.pending_question is None

    def test_reset_clears_all_fields(self) -> None:
        state = SessionState()
        old_id = state.session_id
        state.set_intent("track_order")
        state.last_order_id = "111"
        state.recommendation_context = {"activity": "Camping"}
        state.add_message("user", "Hello")

        state.reset()

        assert state.session_id != old_id  # new session ID
        assert state.current_intent is None
        assert state.last_order_id is None
        assert state.recommendation_context == {}
        assert state.conversation_history == []

    def test_pending_constants_are_strings(self) -> None:
        assert isinstance(PENDING_ORDER_ID, str)
        assert isinstance(PENDING_RECOMMENDATION_ACTIVITY, str)
        assert isinstance(PENDING_RECOMMENDATION_WEATHER, str)


# ---------------------------------------------------------------------------
# TestIntentRouter
# ---------------------------------------------------------------------------

class TestIntentRouter:

    def test_known_intents_resolve_to_handler(self) -> None:
        router = IntentRouter()
        for intent in ROUTING_TABLE:
            handler = router.get_handler(intent)
            assert handler.startswith("_handle_")

    def test_unknown_intent_falls_back(self) -> None:
        router = IntentRouter()
        handler = router.get_handler("completely_unknown_intent_xyz")
        assert handler == ROUTING_TABLE["fallback"]

    def test_registered_intents_contains_all(self) -> None:
        router = IntentRouter()
        assert "track_order" in router.registered_intents
        assert "fallback" in router.registered_intents

    def test_custom_routing_table(self) -> None:
        custom = {"my_intent": "_handle_my_intent", "fallback": "_handle_fallback"}
        router = IntentRouter(table=custom)
        assert router.get_handler("my_intent") == "_handle_my_intent"


# ---------------------------------------------------------------------------
# TestConversationManagerGreetingGoodbye
# ---------------------------------------------------------------------------

class TestConversationManagerGreetingGoodbye:

    def test_greeting_returns_welcome_message(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("greeting"))
        response = cm.handle_message("Hello")
        assert isinstance(response, ChatResponse)
        assert response.intent == "greeting"
        assert "NorthStar" in response.message

    def test_goodbye_returns_closing_message(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("goodbye"))
        response = cm.handle_message("Goodbye")
        assert response.intent == "goodbye"
        assert "goodbye" in response.message.lower() or "thank" in response.message.lower()

    def test_response_added_to_history(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("greeting"))
        cm.handle_message("Hi")
        history = cm.conversation_history
        assert any(m["role"] == "user" for m in history)
        assert any(m["role"] == "bot" for m in history)


# ---------------------------------------------------------------------------
# TestConversationManagerFallback
# ---------------------------------------------------------------------------

class TestConversationManagerFallback:

    def test_fallback_intent_returns_suggestions(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("fallback", 0.3))
        response = cm.handle_message("xyzzy gibberish")
        assert response.intent == "fallback"
        assert len(response.message) > 0

    def test_empty_input_handled_gracefully(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("fallback"))
        response = cm.handle_message("")
        assert isinstance(response, ChatResponse)

    def test_whitespace_only_handled_gracefully(self) -> None:
        cm = ConversationManager(classifier=_make_classifier("fallback"))
        response = cm.handle_message("   ")
        assert isinstance(response, ChatResponse)


# ---------------------------------------------------------------------------
# TestConversationManagerOrderTracking
# ---------------------------------------------------------------------------

class TestConversationManagerOrderTracking:

    def test_asks_for_order_id_when_missing(self) -> None:
        cm = ConversationManager(
            classifier=_make_classifier("track_order"),
            order_service=_make_order_service(),
        )
        response = cm.handle_message("Where is my order?")
        assert response.requires_followup is True
        assert "order number" in response.message.lower() or "order" in response.message.lower()
        assert cm.session_state.pending_question == PENDING_ORDER_ID

    def test_receives_order_id_and_calls_service(self) -> None:
        order_svc = _make_order_service(_ok("Your order has shipped! Arriving tomorrow."))
        cm = ConversationManager(
            classifier=_make_classifier("track_order"),
            order_service=order_svc,
        )
        cm.handle_message("Where is my order?")  # asks for ID
        response = cm.handle_message("111")        # provides ID
        assert response.requires_followup is False
        assert "shipped" in response.message.lower()
        order_svc.get_order_status.assert_called_once_with("111")
        assert cm.session_state.last_order_id == "111"
        assert cm.session_state.pending_question is None

    def test_invalid_order_returns_error_message(self) -> None:
        order_svc = _make_order_service(_err("Sorry, I couldn't find order 999."))
        cm = ConversationManager(
            classifier=_make_classifier("track_order"),
            order_service=order_svc,
        )
        cm.handle_message("Track my order")
        response = cm.handle_message("999")
        assert "999" in response.message or "find" in response.message.lower()

    def test_reuses_last_order_id_in_same_session(self) -> None:
        order_svc = _make_order_service(_ok("Your order is shipped."))
        cm = ConversationManager(
            classifier=_make_classifier("track_order"),
            order_service=order_svc,
        )
        cm.session_state.last_order_id = "222"
        response = cm.handle_message("What's my order status?")
        # Should skip asking for ID and call service directly
        assert response.requires_followup is False
        order_svc.get_order_status.assert_called_once_with("222")


# ---------------------------------------------------------------------------
# TestConversationManagerReturnPolicy
# ---------------------------------------------------------------------------

class TestConversationManagerReturnPolicy:

    def test_return_policy_single_turn(self) -> None:
        return_svc = _make_return_service(policy=_ok("30-day return policy."))
        cm = ConversationManager(
            classifier=_make_classifier("return_policy"),
            return_service=return_svc,
        )
        response = cm.handle_message("Can I return an item?")
        assert response.intent == "return_policy"
        assert "30-day" in response.message
        assert response.requires_followup is False
        return_svc.get_return_policy.assert_called_once()

    def test_shipping_info_single_turn(self) -> None:
        return_svc = _make_return_service(shipping=_ok("Standard shipping: 3-5 business days. Expedited shipping: 1-2 business days."))
        cm = ConversationManager(
            classifier=_make_classifier("shipping_info"),
            return_service=return_svc,
        )
        response = cm.handle_message("How long does shipping take?")
        assert response.intent == "shipping_info"
        assert "days" in response.message.lower()
        return_svc.get_shipping_info.assert_called_once()

    def test_return_service_error_handled(self) -> None:
        return_svc = _make_return_service(policy=_err("Service unavailable."))
        cm = ConversationManager(
            classifier=_make_classifier("return_policy"),
            return_service=return_svc,
        )
        response = cm.handle_message("Return policy?")
        assert "unavailable" in response.message.lower() or len(response.message) > 0


# ---------------------------------------------------------------------------
# TestConversationManagerRecommendation
# ---------------------------------------------------------------------------

class TestConversationManagerRecommendation:

    def test_asks_activity_first(self) -> None:
        cm = ConversationManager(
            classifier=_make_classifier("product_recommendation"),
            recommendation_service=_make_recommendation_service(),
        )
        response = cm.handle_message("I need gear recommendations")
        assert response.requires_followup is True
        assert cm.session_state.pending_question == PENDING_RECOMMENDATION_ACTIVITY

    def test_asks_weather_after_activity(self) -> None:
        cm = ConversationManager(
            classifier=_make_classifier("product_recommendation"),
            recommendation_service=_make_recommendation_service(),
        )
        cm.handle_message("I need gear")         # triggers activity question
        response = cm.handle_message("Camping")  # provides activity
        assert response.requires_followup is True
        assert cm.session_state.pending_question == PENDING_RECOMMENDATION_WEATHER
        assert cm.session_state.recommendation_context.get("activity") == "Camping"

    def test_calls_service_after_two_questions(self) -> None:
        rec_svc = _make_recommendation_service(_ok("We recommend: Tent, Sleeping Bag, Jacket."))
        cm = ConversationManager(
            classifier=_make_classifier("product_recommendation"),
            recommendation_service=rec_svc,
        )
        cm.handle_message("I need gear")   # ask activity
        cm.handle_message("Camping")       # provide activity → ask weather
        response = cm.handle_message("Cold")  # provide weather → call service
        assert response.requires_followup is False
        assert "tent" in response.message.lower() or "recommend" in response.message.lower()
        rec_svc.get_recommendations.assert_called_once_with(
            activity="Camping",
            weather="Cold",
            experience=None,
        )
        # Context should be cleared after a successful recommendation
        assert cm.session_state.recommendation_context == {}

    def test_no_recommendations_returns_friendly_message(self) -> None:
        rec_svc = _make_recommendation_service(_ok(""))
        # Empty data triggers no-results message
        rec_svc.get_recommendations.return_value = ServiceResult(success=True, data=[])
        cm = ConversationManager(
            classifier=_make_classifier("product_recommendation"),
            recommendation_service=rec_svc,
        )
        cm.session_state.recommendation_context = {"activity": "X", "weather": "Y"}
        response = cm.handle_message("recommend something")
        assert len(response.message) > 0  # friendly message, not empty


# ---------------------------------------------------------------------------
# TestConversationManagerHandoff
# ---------------------------------------------------------------------------

class TestConversationManagerHandoff:

    def test_handoff_calls_service(self) -> None:
        handoff_svc = _make_handoff_service(_ok("Connecting you to an agent..."))
        cm = ConversationManager(
            classifier=_make_classifier("human_handoff"),
            handoff_service=handoff_svc,
        )
        response = cm.handle_message("I want to talk to a person")
        assert "agent" in response.message.lower() or "connect" in response.message.lower()
        handoff_svc.simulate_handoff.assert_called_once()


# ---------------------------------------------------------------------------
# TestConversationManagerContextSwitching
# ---------------------------------------------------------------------------

class TestConversationManagerContextSwitching:

    def test_high_confidence_switch_overrides_pending(self) -> None:
        """
        If the user is mid-order-flow but then clearly asks about returns
        with high confidence, the Conversation Manager switches intent.
        """
        # Start with order tracking (asks for ID)
        initial_classifier = _make_classifier("track_order", 0.95)
        cm = ConversationManager(
            classifier=initial_classifier,
            order_service=_make_order_service(),
            return_service=_make_return_service(),
        )
        cm.handle_message("Where is my order?")
        assert cm.session_state.pending_question == PENDING_ORDER_ID

        # Now the classifier switches to return_policy with high confidence
        cm._classifier = _make_classifier("return_policy", 0.92)
        response = cm.handle_message("Actually, tell me about returns")

        # Should have switched intent and cleared pending
        assert cm.session_state.pending_question is None
        assert cm.session_state.current_intent == "return_policy"


# ---------------------------------------------------------------------------
# TestConversationManagerServiceUnavailable
# ---------------------------------------------------------------------------

class TestConversationManagerServiceUnavailable:
    """Verify graceful degradation when services are not yet injected."""

    def _manager_with_intent(self, intent: str) -> ConversationManager:
        return ConversationManager(classifier=_make_classifier(intent))

    def test_order_service_unavailable(self) -> None:
        cm = self._manager_with_intent("track_order")
        cm.session_state.last_order_id = "111"
        response = cm.handle_message("order status")
        assert isinstance(response, ChatResponse)
        assert len(response.message) > 0

    def test_return_service_unavailable(self) -> None:
        cm = self._manager_with_intent("return_policy")
        response = cm.handle_message("return policy")
        assert isinstance(response, ChatResponse)

    def test_recommendation_service_unavailable(self) -> None:
        cm = self._manager_with_intent("product_recommendation")
        cm.session_state.recommendation_context = {"activity": "Camping", "weather": "Cold"}
        response = cm.handle_message("recommend gear")
        assert isinstance(response, ChatResponse)

    def test_handoff_service_unavailable(self) -> None:
        cm = self._manager_with_intent("human_handoff")
        response = cm.handle_message("talk to agent")
        assert isinstance(response, ChatResponse)


# ---------------------------------------------------------------------------
# TestConversationManagerEdgeCases
# ---------------------------------------------------------------------------

class TestConversationManagerEdgeCases:

    def test_reset_clears_state(self) -> None:
        cm = ConversationManager(
            classifier=_make_classifier("track_order"),
            order_service=_make_order_service(),
        )
        cm.handle_message("Where is my order?")
        assert cm.session_state.pending_question == PENDING_ORDER_ID

        old_session_id = cm.session_state.session_id
        cm.reset_session()

        assert cm.session_state.pending_question is None
        assert cm.session_state.session_id != old_session_id

    def test_conversation_history_grows_with_turns(self) -> None:
        cm = ConversationManager(
            classifier=_make_classifier("greeting"),
        )
        cm.handle_message("Hello")
        cm.handle_message("Hello again")
        assert len(cm.conversation_history) == 4  # 2 user + 2 bot

    def test_response_is_always_chat_response(self) -> None:
        for intent in ["greeting", "goodbye", "fallback", "track_order"]:
            cm = ConversationManager(classifier=_make_classifier(intent))
            response = cm.handle_message("test message")
            assert isinstance(response, ChatResponse)
            assert isinstance(response.message, str)
            assert isinstance(response.intent, str)
            assert isinstance(response.requires_followup, bool)
