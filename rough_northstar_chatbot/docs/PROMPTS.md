
# PROMPTS.md

# AI Implementation Prompts
Version: 1.0

These prompts are intended for Cursor, Claude Code, Windsurf, Gemini CLI, or ChatGPT.

---

## Prompt 1 — Project Initialization

Read all documentation in the docs folder before writing code.
Create the project exactly as specified in PROJECT_STRUCTURE.md.
Do not implement business logic yet.

---

## Prompt 2 — Database Layer

Implement only the database layer.

Requirements:
- SQLAlchemy
- SQLite adapter
- Repository interface
- Seed assignment data
- No Streamlit imports

Stop after all database tests pass.

---

## Prompt 3 — NLP

Implement semantic intent recognition.

Requirements:
- sentence-transformers/all-MiniLM-L6-v2
- Cached embeddings
- Cosine similarity
- intents.json
- Configurable confidence threshold

Do not implement business services.

---

## Prompt 4 — Conversation Manager

Implement only:
- Session state
- Intent routing
- Context preservation
- Clarifying questions

Do not access SQLite directly.

---

## Prompt 5 — Business Services

Implement:
- OrderService
- ReturnService
- RecommendationService
- HandoffService

Use repository interfaces only.

---

## Prompt 6 — Streamlit UI

Create a clean chat interface.

Responsibilities:
- Input
- Chat history
- Sidebar
- Reset conversation

No business logic inside UI.

---

## Prompt 7 — Testing

Generate unit, integration and end-to-end tests matching TESTING_PLAN.md.

---

## Prompt 8 — Final Review

Compare the implementation against:
- PRD.md
- ARCHITECTURE.md
- API_CONTRACT.md
- CODING_GUIDELINES.md

List any deviations before modifying code.
