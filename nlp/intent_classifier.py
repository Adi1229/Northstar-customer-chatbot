"""
nlp/intent_classifier.py
-------------------------
Semantic intent classifier using cosine similarity.

Pipeline
--------
1. Load intent examples from ``intents.json``.
2. Encode all examples into embeddings at startup (cached in memory).
3. For each user message:
   a. Encode the message into an embedding.
   b. Compute cosine similarity against every cached example embedding.
   c. Select the intent whose maximum similarity score is highest.
   d. If the score exceeds ``config.NLP_CONFIDENCE_LOW``, return that intent.
   e. Otherwise return ``fallback``.

The NLP layer has no knowledge of the database, services, or Streamlit.
It receives text and returns an ``IntentResult`` only.
"""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

import config
from chatbot.schemas import IntentResult
from nlp.embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

# Sentinel label used when no intent exceeds the confidence threshold.
FALLBACK_INTENT = "fallback"


class IntentClassifier:
    """
    Classifies free-form user text into a predefined intent label.

    Parameters
    ----------
    embedding_model:
        A loaded ``EmbeddingModel`` instance.
    intents_path:
        Path to the ``intents.json`` file.  Defaults to
        ``config.INTENTS_FILE_PATH``.

    On construction, all training examples are encoded and the resulting
    matrix is cached.  Per-request cost is one forward pass (encoding the
    user message) plus a dot-product comparison — typically < 100 ms on CPU.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        intents_path: str | None = None,
    ) -> None:
        self._model = embedding_model
        path = intents_path or config.INTENTS_FILE_PATH
        self._intents: dict[str, list[str]] = self._load_intents(path)
        self._intent_labels: list[str] = []          # parallel to _example_embeddings rows
        self._example_embeddings: np.ndarray | None = None
        self._build_embedding_cache()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, text: str) -> IntentResult:
        """
        Classify a user message into an intent.

        Parameters
        ----------
        text:
            Raw user input.

        Returns
        -------
        IntentResult
            ``intent`` — the predicted label (or ``"fallback"``).
            ``confidence`` — cosine similarity score in [0, 1].
        """
        if not text or not text.strip():
            logger.debug("classify: empty input → fallback")
            return IntentResult(intent=FALLBACK_INTENT, confidence=0.0)

        user_embedding = self._model.encode_single(text)

        # Dot product of normalised vectors == cosine similarity.
        # Shape: (n_examples,)
        similarities: np.ndarray = self._example_embeddings @ user_embedding

        best_idx: int = int(np.argmax(similarities))
        best_score: float = float(similarities[best_idx])
        best_intent: str = self._intent_labels[best_idx]

        # Group by intent and take the maximum score per intent.
        # This ensures we compare intents fairly even when they have
        # different numbers of training examples.
        intent_scores: dict[str, float] = {}
        for label, score in zip(self._intent_labels, similarities.tolist()):
            if label not in intent_scores or score > intent_scores[label]:
                intent_scores[label] = score

        top_intent = max(intent_scores, key=lambda k: intent_scores[k])
        top_score = intent_scores[top_intent]

        logger.debug(
            "classify: text=%r → intent=%r, confidence=%.3f",
            text[:60],
            top_intent,
            top_score,
        )

        if top_score < config.NLP_CONFIDENCE_LOW:
            logger.debug(
                "classify: score %.3f below threshold %.3f → fallback",
                top_score,
                config.NLP_CONFIDENCE_LOW,
            )
            return IntentResult(intent=FALLBACK_INTENT, confidence=top_score)

        return IntentResult(intent=top_intent, confidence=top_score)

    @property
    def known_intents(self) -> list[str]:
        """Return the list of intent labels defined in ``intents.json``."""
        return list(self._intents.keys())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_intents(self, path: str) -> dict[str, list[str]]:
        """
        Load and validate the intents JSON file.

        Parameters
        ----------
        path:
            Filesystem path to ``intents.json``.

        Returns
        -------
        dict[str, list[str]]
            Mapping of intent label → list of example phrases.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file cannot be parsed or has an unexpected structure.
        """
        intents_path = Path(path)
        if not intents_path.exists():
            raise FileNotFoundError(
                f"Intents file not found at '{path}'. "
                "Ensure INTENTS_FILE_PATH in config.py is correct."
            )

        try:
            raw: Any = json.loads(intents_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse '{path}': {exc}") from exc

        if not isinstance(raw, dict):
            raise ValueError(f"'{path}' must be a JSON object mapping intent → [examples].")

        intents: dict[str, list[str]] = {}
        for intent, examples in raw.items():
            if not isinstance(examples, list) or not all(isinstance(e, str) for e in examples):
                raise ValueError(
                    f"Intent '{intent}' must map to a list of strings."
                )
            if not examples:
                logger.warning("Intent '%s' has no examples — skipping.", intent)
                continue
            intents[intent] = examples

        logger.info(
            "_load_intents: loaded %d intents with %d total examples.",
            len(intents),
            sum(len(v) for v in intents.values()),
        )
        return intents

    def _build_embedding_cache(self) -> None:
        """
        Encode all training examples into a single numpy matrix.

        The resulting matrix has shape ``(total_examples, embedding_dim)``.
        Each row corresponds to one training example; ``_intent_labels``
        stores the intent label for each row (parallel lists).
        """
        all_examples: list[str] = []
        all_labels: list[str] = []

        for intent, examples in self._intents.items():
            for example in examples:
                all_examples.append(example)
                all_labels.append(intent)

        logger.info(
            "_build_embedding_cache: encoding %d examples for %d intents.",
            len(all_examples),
            len(self._intents),
        )

        self._example_embeddings = self._model.encode(all_examples)
        self._intent_labels = all_labels

        logger.info("_build_embedding_cache: cache built successfully.")
