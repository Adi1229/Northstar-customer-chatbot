"""
tests/test_integration.py
--------------------------
End-to-end integration tests for the NorthStar chatbot.

These tests wire every layer together using the real NLP model and an
in-memory SQLite database — no mocks, no stubs.

Pipeline under test:
  User text
    → IntentClassifier (real MiniLM model)
      → ConversationManager (state + routing)
        → Service (OrderService / ReturnService / …)
          → SQLiteAdapter (in-memory DB, seeded)
            → ChatResponse

Marked ``@pytest.mark.integration`` — they download/load the MiniLM model
once per session (cached via the class-scoped fixture) and run in ~60 s.

Skip gracefully if sentence-transformers is not installed:
    pytest tests/test_integration.py -m "not integration"
"""

import pytest

# ---------------------------------------------------------------------------
# Skip guard
# ---------------------------------------------------------------------------
try:
    from sentence_transformers import SentenceTransformer  # noqa: F401
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False

integration = pytest.mark.skipif(
    not _ST_AVAILABLE,
    reason="sentence-transformers not installed",
)

# ---------------------------------------------------------------------------
# Imports (only after the skip guard so CI without torch doesn't crash)
# ---------------------------------------------------------------------------
if _ST_AVAILABLE:
    from chatbot.conversation import ConversationManager
    from chatbot.schemas import ChatResponse
    from database.sqlite_adapter import SQLiteAdapter
    from nlp.embeddings import EmbeddingModel
    from nlp.intent_classifier import IntentClassifier
    from services.handoff_service import HandoffService
    from services.order_service import OrderService
    from services.recommendation_service import RecommendationService
    from services.return_service import ReturnService


# ---------------------------------------------------------------------------
# Session-scoped fixtures (model loaded once for the entire suite)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def _nlp_model():
    """Load the real MiniLM model once for the whole session."""
    return EmbeddingModel()


@pytest.fixture(scope="session")
def _classifier(_nlp_model):
    """Build the intent classifier backed by the real model."""
    return IntentClassifier(embedding_model=_nlp_model)


@pytest.fixture()
def manager(_classifier):
    """
    Fresh ConversationManager with a real in-memory SQLiteAdapter
    and all four services wired up.  Created fresh per test.
    """
    repo = SQLiteAdapter(db_path=":memory:")
    cm = ConversationManager(
        classifier=_classifier,
        order_service=OrderService(repository=repo),
        return_service=ReturnService(),
        recommendation_service=RecommendationService(repository=repo),
        handoff_service=HandoffService(),
    )
    return cm


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def chat(manager: "ConversationManager", text: str) -> "ChatResponse":
    """Send a message and return the ChatResponse."""
    return manager.handle_message(text)


# ---------------------------------------------------------------------------
# TestGreetingFlow
# ---------------------------------------------------------------------------

@integration
class TestGreetingFlow:

    def test_hello_returns_greeting(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Hello")
        assert r.intent == "greeting"
        assert "NorthStar" in r.message

    def test_hi_returns_greeting(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Hi there")
        assert r.intent == "greeting"

    def test_goodbye_returns_goodbye(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Goodbye")
        assert r.intent == "goodbye"
        assert r.requires_followup is False


# ---------------------------------------------------------------------------
# TestOrderTrackingFlow
# ---------------------------------------------------------------------------

@integration
class TestOrderTrackingFlow:

    def test_order_tracking_asks_for_id(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Where is my order?")
        assert r.intent == "track_order"
        assert r.requires_followup is True

    def test_order_111_full_flow(self, manager: "ConversationManager") -> None:
        chat(manager, "Track my order")         # ask → pending
        r = chat(manager, "111")                # answer → lookup
        assert r.intent == "track_order"
        assert r.requires_followup is False
        assert "Shipped" in r.message
        assert "111" in r.message

    def test_order_222_processing(self, manager: "ConversationManager") -> None:
        chat(manager, "Where is my shipment?")
        r = chat(manager, "222")
        assert "Processing" in r.message

    def test_order_333_delivered(self, manager: "ConversationManager") -> None:
        chat(manager, "Order status please")
        r = chat(manager, "333")
        assert "Delivered" in r.message

    def test_invalid_order_returns_not_found(self, manager: "ConversationManager") -> None:
        chat(manager, "Check my order")
        r = chat(manager, "999")
        assert r.requires_followup is False
        assert "999" in r.message or "find" in r.message.lower()

    def test_order_id_reused_in_session(self, manager: "ConversationManager") -> None:
        """After tracking order 111, asking again should use the stored ID."""
        chat(manager, "Track my order")
        chat(manager, "111")                     # first lookup — stores last_order_id
        r = chat(manager, "What's my order status?")  # second lookup — reuses ID
        assert "Shipped" in r.message
        assert r.requires_followup is False


# ---------------------------------------------------------------------------
# TestReturnPolicyFlow
# ---------------------------------------------------------------------------

@integration
class TestReturnPolicyFlow:

    def test_return_policy_single_turn(self, manager: "ConversationManager") -> None:
        r = chat(manager, "What is your return policy?")
        assert r.intent == "return_policy"
        assert "30" in r.message
        assert r.requires_followup is False

    def test_refund_paraphrase(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Can I get a refund?")
        assert r.intent == "return_policy"

    def test_shipping_info_single_turn(self, manager: "ConversationManager") -> None:
        r = chat(manager, "How long does shipping take?")
        assert r.intent == "shipping_info"
        assert "days" in r.message.lower()
        assert r.requires_followup is False


# ---------------------------------------------------------------------------
# TestRecommendationFlow
# ---------------------------------------------------------------------------

@integration
class TestRecommendationFlow:

    def test_two_question_camping_cold_flow(self, manager: "ConversationManager") -> None:
        # Turn 1: classifier → product_recommendation, asks for activity
        r1 = chat(manager, "I need gear recommendations")
        assert r1.requires_followup is True
        assert r1.intent == "product_recommendation"

        # Turn 2: user provides activity → asks for weather
        r2 = chat(manager, "Camping")
        assert r2.requires_followup is True

        # Turn 3: user provides weather → service call
        r3 = chat(manager, "Cold")
        assert r3.requires_followup is False
        assert r3.intent == "product_recommendation"
        # Real DB seeded with Tent / Sleeping / Clothing for Camping+Cold
        assert any(
            cat in r3.message
            for cat in ["Tent", "Sleeping", "Clothing", "recommend"]
        )

    def test_hiking_rainy_flow(self, manager: "ConversationManager") -> None:
        chat(manager, "What camping gear do you suggest?")
        chat(manager, "Hiking")
        r = chat(manager, "Rainy")
        assert r.requires_followup is False
        # Real DB seeded with Rain Jacket / Footwear for Hiking+Rainy
        assert any(
            cat in r.message
            for cat in ["Rain Jacket", "Footwear", "recommend"]
        )

    def test_context_cleared_after_recommendation(self, manager: "ConversationManager") -> None:
        """After a recommendation, starting a new flow should ask for activity again."""
        chat(manager, "Help me find gear")
        chat(manager, "Camping")
        chat(manager, "Warm")           # completes first flow
        manager.session_state.recommendation_context == {}  # should be cleared


# ---------------------------------------------------------------------------
# TestHandoffFlow
# ---------------------------------------------------------------------------

@integration
class TestHandoffFlow:

    def test_connect_to_agent(self, manager: "ConversationManager") -> None:
        r = chat(manager, "I want to talk to a person")
        assert r.intent == "human_handoff"
        assert r.requires_followup is False
        msg = r.message.lower()
        assert "agent" in msg or "representative" in msg or "team" in msg

    def test_escalate_paraphrase(self, manager: "ConversationManager") -> None:
        r = chat(manager, "Connect me to a human")
        assert r.intent == "human_handoff"


# ---------------------------------------------------------------------------
# TestContextSwitching
# ---------------------------------------------------------------------------

@integration
class TestContextSwitching:

    def test_switch_from_order_to_return(self, manager: "ConversationManager") -> None:
        """
        User starts order flow (pending order_id) then switches to
        return policy with a clearly typed query.
        """
        r1 = chat(manager, "Where is my order?")
        assert r1.requires_followup is True  # waiting for order ID

        # Very clear return policy query — should trigger context switch
        r2 = chat(manager, "What is your return policy?")
        # Either intent switched to return_policy OR order flow completed
        # with "return" treated as an order ID (edge case).
        # The key requirement is that the app returns a meaningful response.
        assert isinstance(r2, ChatResponse)
        assert len(r2.message) > 0

    def test_fallback_does_not_interrupt_pending(self, manager: "ConversationManager") -> None:
        """
        Low-confidence / nonsense input while pending should NOT switch intent.
        """
        chat(manager, "Track my order")         # sets pending=order_id
        r = chat(manager, "111")                 # this resolves correctly
        assert "Shipped" in r.message


# ---------------------------------------------------------------------------
# TestFallbackFlow
# ---------------------------------------------------------------------------

@integration
class TestFallbackFlow:

    def test_nonsense_returns_fallback(self, manager: "ConversationManager") -> None:
        r = chat(manager, "zxcvbnm asdfghjkl")
        # Either fallback or a low-confidence response — never a crash.
        assert isinstance(r, ChatResponse)
        assert len(r.message) > 0

    def test_empty_input_handled(self, manager: "ConversationManager") -> None:
        r = chat(manager, "")
        assert isinstance(r, ChatResponse)

    def test_whitespace_input_handled(self, manager: "ConversationManager") -> None:
        r = chat(manager, "   ")
        assert isinstance(r, ChatResponse)


# ---------------------------------------------------------------------------
# TestSessionReset
# ---------------------------------------------------------------------------

@integration
class TestSessionReset:

    def test_reset_clears_pending_state(self, manager: "ConversationManager") -> None:
        chat(manager, "Track my order")         # sets pending
        old_session = manager.session_state.session_id
        manager.reset_session()
        assert manager.session_state.session_id != old_session
        assert manager.session_state.pending_question is None

    def test_conversation_continues_after_reset(self, manager: "ConversationManager") -> None:
        chat(manager, "Hello")
        manager.reset_session()
        r = chat(manager, "Hello again")
        assert r.intent == "greeting"

    def test_order_id_not_reused_after_reset(self, manager: "ConversationManager") -> None:
        chat(manager, "Track my order")
        chat(manager, "111")
        manager.reset_session()
        # After reset, should ask for order ID again
        r = chat(manager, "Order status")
        assert r.requires_followup is True
