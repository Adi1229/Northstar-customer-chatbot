"""
config.py
---------
Global configuration for the NorthStar AI Customer Support Chatbot.

All tuneable values (database backend, NLP thresholds, paths) are defined
here. No other module should hardcode these values.
"""

import os

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

#: Active database backend. Swap to "postgres" when the adapter is ready.
DATABASE_BACKEND: str = "sqlite"

#: Path to the SQLite database file (relative to project root).
DATABASE_PATH: str = os.path.join("data", "northstar.db")

#: Path to the SQL schema file used for table creation.
SCHEMA_SQL_PATH: str = os.path.join("data", "schema.sql")

# ---------------------------------------------------------------------------
# NLP
# ---------------------------------------------------------------------------

#: Sentence Transformer model to use for intent classification.
NLP_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

#: Path to the intents definition file.
INTENTS_FILE_PATH: str = os.path.join("nlp", "intents.json")

#: Cosine similarity score at or above which an intent is accepted confidently.
NLP_CONFIDENCE_HIGH: float = 0.80

#: Cosine similarity score below which the fallback intent is triggered.
NLP_CONFIDENCE_LOW: float = 0.60

# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------

#: Maximum number of clarifying questions for product recommendations.
MAX_RECOMMENDATION_QUESTIONS: int = 2

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

#: Logging level (DEBUG, INFO, WARNING, ERROR).
LOG_LEVEL: str = "INFO"

#: Log format string.
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
