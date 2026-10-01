# NorthStar AI Customer Support Chatbot

An offline, AI-powered customer support chatbot for **NorthStar Outdoor Gear** — built with a strict layered architecture, semantic intent classification using MiniLM, and a premium Streamlit UI.

---

## Features

| Capability | Detail |
|---|---|
| 📦 **Order Tracking** | Multi-turn flow: ask → provide order # → get status + ETA |
| 🔄 **Return Policy** | Full 30-day return & exchange policy with conditions |
| 🚚 **Shipping Info** | Delivery options, timelines, and pricing table |
| 🛒 **Product Recommendations** | Two-question flow (activity → weather) mapped to real catalogue items |
| 🎧 **Live Agent Handoff** | Simulated transfer message with escalation context |
| 🔁 **Context Switching** | User can change topic mid-conversation without restarting |
| 💾 **Session Memory** | Order IDs remembered within a session for follow-up questions |
| 🏔️ **Fully Offline** | MiniLM model cached locally — no API keys required |

---

## 🚀 Submission & Evaluator Setup

> **No API keys, accounts, or external services needed.** Follow the steps below to run the chatbot locally in under 2 minutes.

### Step 1 — Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| pip | Latest (bundled with Python) |
| Internet | **Only on first run** (to download the ~90 MB MiniLM model) |

Verify your Python version:
```bash
python --version
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `sqlalchemy` | ORM and database layer |
| `sentence-transformers` | MiniLM semantic embedding model |
| `torch` | Required by sentence-transformers |
| `pytest` | Test runner (for verification) |

> **First run note:** The MiniLM model (`all-MiniLM-L6-v2`, ~90 MB) is downloaded automatically from HuggingFace and cached in `~/.cache/huggingface`. All subsequent runs are **fully offline**.

### Step 3 — Run the Application

```bash
streamlit run app.py
```

The browser opens automatically at **http://localhost:8501**.  
The SQLite database (`data/northstar.db`) is **created and seeded automatically** on first launch — no manual setup required.

### Step 4 — Try the Demo Orders

Three orders are pre-seeded for testing:

| Order Number | Status | Message |
|---|---|---|
| `111` | **Shipped** | Arriving Tomorrow |
| `222` | **Processing** | Ships in 24 Hours |
| `333` | **Delivered** | Delivered |

### Step 5 — Verify All Use Cases

| Use Case | What to type | Expected Result |
|---|---|---|
| **Order Tracking** | `where is my order` → `111` | Shipped — Arriving Tomorrow |
| **Multi-order** | `track another order` → `222` | Processing — Ships in 24 Hours |
| **Return Policy** | `I want to return an item` | 30-day return policy details |
| **Shipping Info** | `what are your shipping options` | Delivery options & timelines |
| **Recommendations** | `gear recommendations` → `Camping` → `Cold` | Tent + Sleeping Bag + Jacket |
| **Human Handoff** | `I need to speak to a human agent` | Simulated agent transfer |
| **Fallback** | `asdfjkl xyz` | Graceful "I didn't understand" |

### Step 6 — Run the Test Suite (Optional)

```bash
# Full suite — 153 tests across all layers (~60 s)
python -m pytest tests/ -v

# Fast unit tests only, no model needed (<5 s)
python -m pytest tests/ -v -k "not integration"
```

### 📦 What's Included in This Submission

```
North-star-ai-customer-support/
├── app.py                    ← Streamlit UI entry point
├── config.py                 ← All tunable constants
├── requirements.txt          ← All dependencies (pip install)
├── chatbot/                  ← ConversationManager, router, state
├── nlp/                      ← MiniLM intent classifier + training data
├── services/                 ← Order, Return, Recommendation, Handoff
├── database/                 ← SQLite adapter + repository pattern
├── models/                   ← SQLAlchemy ORM models
├── data/                     ← Schema + seed SQL (reference only)
├── tests/                    ← 153 tests across 5 test files
```

> The database file (`data/northstar.db`) is auto-generated — it is **not** committed to the repository. It will be created fresh on first launch.

---

## Architecture

```
UI (app.py / Streamlit)
    │
    ▼
ConversationManager          ← chatbot/conversation.py
    ├── IntentRouter          ← chatbot/router.py
    ├── SessionState          ← chatbot/state_manager.py
    └── Services
          ├── OrderService         ← services/order_service.py
          ├── ReturnService        ← services/return_service.py
          ├── RecommendationService← services/recommendation_service.py
          └── HandoffService       ← services/handoff_service.py
                │
                ▼
         Repository (BaseRepository ABC)
                │
                ▼
         SQLiteAdapter        ← database/sqlite_adapter.py
                │
                ▼
         SQLite DB            ← data/northstar.db (auto-created)

NLP Layer (no DB access)
    ├── EmbeddingModel        ← nlp/embeddings.py   (MiniLM via sentence-transformers)
    └── IntentClassifier      ← nlp/intent_classifier.py  (cosine similarity)
```

**Dependency rule:** each layer only imports from the layer directly below it. The UI never touches the database; services never touch Streamlit.

---

## Project Structure

```
North-star-ai-customer-support/
├── app.py                        # Streamlit UI — only file that imports streamlit
├── config.py                     # All tunable constants
├── requirements.txt
│
├── chatbot/
│   ├── schemas.py                # Shared dataclasses: IntentResult, ChatResponse, ServiceResult
│   ├── conversation.py           # ConversationManager (orchestrator)
│   ├── router.py                 # Intent → handler routing table
│   └── state_manager.py          # SessionState dataclass + PENDING_* constants
│
├── nlp/
│   ├── intents.json              # Training examples (7 intents, 12–16 each)
│   ├── embeddings.py             # EmbeddingModel wrapper (MiniLM)
│   └── intent_classifier.py      # Cosine-similarity classifier
│
├── services/
│   ├── order_service.py          # Order status lookup + formatting
│   ├── return_service.py         # Return policy + shipping info (static rules)
│   ├── recommendation_service.py # Rule-based product recommendations
│   └── handoff_service.py        # Simulated live agent transfer
│
├── database/
│   ├── base.py                   # BaseRepository ABC (interface contract)
│   ├── sqlite_adapter.py         # Concrete SQLite implementation
│   ├── repository.py             # Lazy singleton + test injection hooks
│   └── factory.py                # Config-driven adapter selector
│
├── models/
│   ├── base.py                   # SQLAlchemy DeclarativeBase
│   ├── order.py                  # Order ORM model
│   ├── product.py                # Product ORM model
│   └── recommendation_rule.py    # RecommendationRule ORM model
│
├── data/
│   ├── schema.sql                # Schema DDL reference
│   └── seed.sql                  # Seed data reference
│
├── tests/
│   ├── test_database.py          # 26 database layer tests
│   ├── test_nlp.py               # 26 NLP tests (11 unit + 15 real-model integration)
│   ├── test_chatbot.py           # 36 conversation manager tests
│   ├── test_services.py          # 31 service tests
│   └── test_integration.py       # End-to-end integration tests (all layers)
│
└── docs/                         # Architecture, design, and API documentation
```

---

## Setup

### Prerequisites

- Python 3.10+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` — UI framework
- `sqlalchemy` — ORM and database layer
- `sentence-transformers` — MiniLM semantic embedding model
- `torch` — required by sentence-transformers
- `pytest` — test runner

> **First run:** The MiniLM model (`all-MiniLM-L6-v2`, ~90 MB) is downloaded from HuggingFace and cached in `~/.cache/huggingface`. Subsequent runs are fully offline.

---

## Running the App

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

The database (`data/northstar.db`) is created and seeded automatically on first launch.

### Demo Orders

| Order # | Status |
|---|---|
| `111` | Shipped — Arriving Tomorrow |
| `222` | Processing — Ships in 24 Hours |
| `333` | Delivered |

---

## Running Tests

```bash
# Full suite (all layers including real MiniLM model — ~60 s)
python -m pytest tests/ -v

# Fast unit tests only (no model download — < 5 s)
python -m pytest tests/ -v -k "not integration"

# Single phase
python -m pytest tests/test_database.py -v
python -m pytest tests/test_nlp.py -v
python -m pytest tests/test_chatbot.py -v
python -m pytest tests/test_services.py -v
python -m pytest tests/test_integration.py -v
```

### Test Summary

| File | Tests | Speed |
|---|---|---|
| `test_database.py` | 26 | Fast (in-memory SQLite) |
| `test_nlp.py` | 26 | Unit: fast · Integration: ~30 s (MiniLM) |
| `test_chatbot.py` | 36 | Fast (all mocked) |
| `test_services.py` | 31 | Fast (repo mocked) |
| `test_integration.py` | 34 | ~60 s (real model + real DB) |
| **Total** | **153** | |

---

## NLP Design

The chatbot uses **cosine similarity** over MiniLM sentence embeddings:

1. At startup, all training examples from `nlp/intents.json` are encoded into a matrix.
2. For each user message, the message is encoded and dot-producted against the matrix (unit vectors → cosine similarity = dot product).
3. The maximum similarity score per intent is taken (fair regardless of example count).
4. If the top score exceeds `NLP_CONFIDENCE_LOW` (default `0.35`), the intent is returned.
5. Otherwise, `fallback` is returned.

**Adding a new intent:**
1. Add examples to `nlp/intents.json`.
2. Add a row to `ROUTING_TABLE` in `chatbot/router.py`.
3. Implement `_handle_<intent>()` in `chatbot/conversation.py`.

---

## Configuration

All tunable values are in [`config.py`](config.py):

| Key | Default | Purpose |
|---|---|---|
| `DATABASE_BACKEND` | `"sqlite"` | Swap to `"postgres"` to add a new adapter |
| `DATABASE_PATH` | `"data/northstar.db"` | SQLite file location |
| `NLP_MODEL_NAME` | `"sentence-transformers/all-MiniLM-L6-v2"` | Embedding model |
| `NLP_CONFIDENCE_LOW` | `0.35` | Minimum score to accept an intent |
| `NLP_CONFIDENCE_HIGH` | `0.70` | Minimum score to trigger context switch |
| `INTENTS_FILE_PATH` | `"nlp/intents.json"` | Training examples |
| `LOG_LEVEL` | `"INFO"` | Python logging level |

---

## Extending the System

### Add a new backend (PostgreSQL, REST API)
1. Implement a class extending `database.base.BaseRepository`.
2. Add a branch in `database/factory.py`.
3. Update `config.DATABASE_BACKEND`. No other files change.

### Add a new intent
1. Add examples to `nlp/intents.json`.
2. Add `"my_intent": "_handle_my_intent"` to `chatbot/router.py`.
3. Implement `_handle_my_intent()` in `chatbot/conversation.py`.

### Add a new service
1. Create `services/my_service.py` implementing the desired method(s).
2. Inject it in `ConversationManager.__init__()`.
3. Call it from the relevant handler.

---


