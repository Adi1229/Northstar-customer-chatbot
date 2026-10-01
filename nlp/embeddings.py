"""
nlp/embeddings.py
-----------------
Sentence embedding model loader and cache.

Responsibilities:
  - Load the MiniLM sentence transformer model once at startup.
  - Encode a list of texts into fixed-size embedding vectors.
  - Cache intent embeddings in memory to avoid repeated inference.

The NLP layer has no knowledge of the database, Streamlit, or business
services.  It receives text and returns numerical vectors only.
"""

import logging
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

import config

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Thin wrapper around a ``SentenceTransformer`` model.

    Loads the model on first construction and keeps it in memory for the
    lifetime of the process.  The constructor blocks until the model is
    fully loaded — call it during application startup, not per-request.

    Parameters
    ----------
    model_name:
        HuggingFace model identifier.  Defaults to
        ``config.NLP_MODEL_NAME`` (``all-MiniLM-L6-v2``).
    """

    def __init__(self, model_name: str | None = None) -> None:
        resolved_name = model_name or config.NLP_MODEL_NAME
        logger.info("EmbeddingModel: loading model '%s'", resolved_name)
        self._model: SentenceTransformer = SentenceTransformer(resolved_name)
        logger.info("EmbeddingModel: model loaded successfully.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """
        Encode a list of texts into embedding vectors.

        Parameters
        ----------
        texts:
            One or more sentences to encode.
        batch_size:
            Number of sentences to encode per batch.  Tune for memory.

        Returns
        -------
        np.ndarray
            2-D array of shape ``(len(texts), embedding_dim)``.
        """
        if not texts:
            raise ValueError("Cannot encode an empty list of texts.")

        embeddings: np.ndarray = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,  # unit-length vectors → dot product = cosine similarity
        )
        return embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single sentence into an embedding vector.

        Parameters
        ----------
        text:
            A single input sentence.

        Returns
        -------
        np.ndarray
            1-D array of shape ``(embedding_dim,)``.
        """
        result = self.encode([text.strip()])
        return result[0]
