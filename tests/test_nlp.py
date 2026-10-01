"""
tests/test_nlp.py
-----------------
Tests for the NLP layer (embeddings + intent classifier).

Structure
---------
TestEmbeddingModel
    Unit tests that mock the underlying SentenceTransformer so they
    run without any model download.

TestIntentClassifierUnit
    Unit tests for classifier logic using a deterministic mock model.
    No sentence-transformers required.

TestIntentClassifierIntegration
    Integration tests using the real MiniLM model.
    These are marked ``@pytest.mark.integration`` and are skipped
    automatically if sentence-transformers is not installed.

TestEdgeCases
    Boundary and error-condition tests.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from chatbot.schemas import IntentResult
from nlp.intent_classifier import IntentClassifier, FALLBACK_INTENT


# ---------------------------------------------------------------------------
# Helper: deterministic mock embedding model
# ---------------------------------------------------------------------------

def _make_mock_model(vocabulary: dict[str, np.ndarray]) -> MagicMock:
    """
    Return a mock EmbeddingModel whose ``encode`` and ``encode_single``
    methods return fixed, deterministic vectors from a vocabulary dict.

    Each key is a phrase (or prefix); the value is a normalised 1-D array.
    Unknown phrases return a zero vector.
    """
    dim = next(iter(vocabulary.values())).shape[0]

    def _encode(texts: list[str], **_kwargs) -> np.ndarray:
        rows = []
        for text in texts:
            rows.append(vocabulary.get(text, np.zeros(dim)))
        return np.array(rows, dtype=np.float32)

    def _encode_single(text: str) -> np.ndarray:
        return vocabulary.get(text.strip(), np.zeros(dim))

    mock = MagicMock()
    mock.encode.side_effect = _encode
    mock.encode_single.side_effect = _encode_single
    return mock


def _make_intents_file(intents: dict) -> str:
    """Write intents dict to a temp JSON file and return the path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(intents, tmp)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Fixtures: 3-D embedding space, one intent per axis
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_intents_path() -> str:
    """Temp intents file with two intents."""
    intents = {
        "track_order": ["Where is my order?", "Track my package"],
        "return_policy": ["How do I return something?", "What is your return policy?"],
    }
    return _make_intents_file(intents)


@pytest.fixture()
def simple_vocab() -> dict[str, np.ndarray]:
    """
    3-D vocabulary where:
      - track_order examples → [1, 0, 0]
      - return_policy examples → [0, 1, 0]
      - user "track" query → [0.99, 0.14, 0] (close to track_order axis)
      - user "return" query → [0.14, 0.99, 0] (close to return_policy axis)
      - user "xyz" query → [0, 0, 0] (zero → fallback)
    """
    return {
        "Where is my order?":          np.array([1.0, 0.0, 0.0], dtype=np.float32),
        "Track my package":            np.array([1.0, 0.0, 0.0], dtype=np.float32),
        "How do I return something?":  np.array([0.0, 1.0, 0.0], dtype=np.float32),
        "What is your return policy?": np.array([0.0, 1.0, 0.0], dtype=np.float32),
        # User queries
        "track my order":              np.array([0.99, 0.14, 0.0], dtype=np.float32),
        "I want to return an item":    np.array([0.14, 0.99, 0.0], dtype=np.float32),
    }


@pytest.fixture()
def simple_classifier(simple_intents_path, simple_vocab) -> IntentClassifier:
    mock_model = _make_mock_model(simple_vocab)
    return IntentClassifier(
        embedding_model=mock_model,
        intents_path=simple_intents_path,
    )


# ---------------------------------------------------------------------------
# Unit tests — classifier logic (no real model)
# ---------------------------------------------------------------------------

class TestIntentClassifierUnit:

    def test_classifies_track_order(self, simple_classifier: IntentClassifier) -> None:
        result = simple_classifier.classify("track my order")
        assert result.intent == "track_order"
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_classifies_return_policy(self, simple_classifier: IntentClassifier) -> None:
        result = simple_classifier.classify("I want to return an item")
        assert result.intent == "return_policy"

    def test_returns_intent_result_type(self, simple_classifier: IntentClassifier) -> None:
        result = simple_classifier.classify("track my order")
        assert isinstance(result, IntentResult)
        assert hasattr(result, "intent")
        assert hasattr(result, "confidence")

    def test_empty_input_returns_fallback(self, simple_classifier: IntentClassifier) -> None:
        assert simple_classifier.classify("").intent == FALLBACK_INTENT
        assert simple_classifier.classify("   ").intent == FALLBACK_INTENT

    def test_unknown_query_returns_fallback(self, simple_classifier: IntentClassifier) -> None:
        # Zero vector has zero similarity to everything.
        result = simple_classifier.classify("xyz")
        assert result.intent == FALLBACK_INTENT

    def test_known_intents_property(self, simple_classifier: IntentClassifier) -> None:
        intents = simple_classifier.known_intents
        assert "track_order" in intents
        assert "return_policy" in intents
        assert FALLBACK_INTENT not in intents  # fallback is not a trained intent

    def test_fallback_confidence_is_float(self, simple_classifier: IntentClassifier) -> None:
        result = simple_classifier.classify("xyz")
        assert isinstance(result.confidence, float)


# ---------------------------------------------------------------------------
# Unit tests — _load_intents validation
# ---------------------------------------------------------------------------

class TestLoadIntents:

    def test_missing_file_raises(self, simple_vocab) -> None:
        mock_model = _make_mock_model(simple_vocab)
        with pytest.raises(FileNotFoundError):
            IntentClassifier(
                embedding_model=mock_model,
                intents_path="/nonexistent/path/intents.json",
            )

    def test_invalid_json_raises(self, simple_vocab, tmp_path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json", encoding="utf-8")
        mock_model = _make_mock_model(simple_vocab)
        with pytest.raises(ValueError, match="Failed to parse"):
            IntentClassifier(embedding_model=mock_model, intents_path=str(bad_file))

    def test_non_dict_json_raises(self, simple_vocab, tmp_path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('["track_order", "return_policy"]', encoding="utf-8")
        mock_model = _make_mock_model(simple_vocab)
        with pytest.raises(ValueError):
            IntentClassifier(embedding_model=mock_model, intents_path=str(bad_file))

    def test_empty_intent_examples_skipped(self, simple_vocab, tmp_path) -> None:
        """Intents with no examples should be silently skipped."""
        intents = {
            "track_order": ["Where is my order?", "Track my package"],
            "empty_intent": [],
        }
        path = tmp_path / "intents.json"
        path.write_text(json.dumps(intents), encoding="utf-8")
        mock_model = _make_mock_model(simple_vocab)
        classifier = IntentClassifier(embedding_model=mock_model, intents_path=str(path))
        assert "empty_intent" not in classifier.known_intents
        assert "track_order" in classifier.known_intents


# ---------------------------------------------------------------------------
# Integration tests — real MiniLM model
# ---------------------------------------------------------------------------

# Skip gracefully if sentence-transformers not installed.
sentence_transformers_available = True
try:
    from sentence_transformers import SentenceTransformer  # noqa: F401
except ImportError:
    sentence_transformers_available = False

integration = pytest.mark.skipif(
    not sentence_transformers_available,
    reason="sentence-transformers not installed",
)


@integration
class TestIntentClassifierIntegration:
    """
    Integration tests using the real MiniLM model and the project's
    ``nlp/intents.json``.  These verify end-to-end semantic matching.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def classifier(cls) -> IntentClassifier:
        from nlp.embeddings import EmbeddingModel
        model = EmbeddingModel()
        return IntentClassifier(embedding_model=model)

    # --- track_order ---
    def test_track_order_exact(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Where is my order?").intent == "track_order"

    def test_track_order_paraphrase(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Track my shipment").intent == "track_order"

    def test_track_order_indirect(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("My package hasn't arrived yet").intent == "track_order"

    # --- return_policy ---
    def test_return_policy_exact(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("What is your return policy?").intent == "return_policy"

    def test_return_policy_paraphrase(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("I want to return a product").intent == "return_policy"

    def test_return_policy_sentiment(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("I don't like the item I got").intent == "return_policy"

    # --- shipping_info ---
    def test_shipping_info(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("How long does shipping take?").intent == "shipping_info"

    def test_shipping_info_paraphrase(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Do you offer express delivery?").intent == "shipping_info"

    # --- product_recommendation ---
    def test_product_recommendation(self, classifier: IntentClassifier) -> None:
        result = classifier.classify("What camping gear do you recommend?")
        assert result.intent == "product_recommendation"

    # --- human_handoff ---
    def test_human_handoff(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("I want to talk to a person").intent == "human_handoff"

    def test_human_handoff_paraphrase(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Connect me to an agent").intent == "human_handoff"

    # --- greeting ---
    def test_greeting(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Hello").intent == "greeting"

    def test_greeting_paraphrase(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Hi there, can you help me?").intent == "greeting"

    # --- goodbye ---
    def test_goodbye(self, classifier: IntentClassifier) -> None:
        assert classifier.classify("Goodbye").intent == "goodbye"

    # --- confidence thresholds ---
    def test_confidence_above_low_threshold(self, classifier: IntentClassifier) -> None:
        import config
        result = classifier.classify("Where is my order?")
        assert result.confidence >= config.NLP_CONFIDENCE_LOW

    def test_nonsense_returns_fallback(self, classifier: IntentClassifier) -> None:
        result = classifier.classify("asdfghjkl qwerty zxcvbnm")
        # Very low-similarity text should either be fallback or have low confidence
        if result.intent != FALLBACK_INTENT:
            assert result.confidence < 0.85
