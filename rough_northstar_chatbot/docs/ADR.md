
# ADR.md

# Architecture Decision Records
Version: 1.0

This document records major architectural decisions and the rationale behind them.

---

## ADR-001: Offline-First Architecture

**Decision:** The chatbot must run completely offline.

**Reasoning**
- Assignment requires no deployment.
- Easier evaluation.
- No API costs.
- Works without internet after dependencies are installed.

**Consequences**
- Use local NLP.
- Local SQLite database.
- No SaaS dependencies.

---

## ADR-002: MiniLM Instead of an LLM

**Decision:** Use `sentence-transformers/all-MiniLM-L6-v2`.

**Alternatives Considered**
- OpenAI API
- Gemini API
- Local LLMs (Ollama/Llama)

**Reasoning**
- Semantic understanding
- Fast CPU inference
- Small memory footprint
- No API keys

---

## ADR-003: Service Layer

**Decision:** Business logic belongs in services.

**Benefits**
- Testable
- Reusable
- UI independent

---

## ADR-004: Repository Pattern

**Decision:** All persistence goes through repository interfaces.

**Reasoning**
- SQLite can later be replaced by PostgreSQL or REST APIs.
- Business services remain unchanged.

---

## ADR-005: Streamlit UI

**Decision:** Streamlit is the presentation layer.

**Reasoning**
- Rapid development
- Python-only stack
- Suitable for assignment demonstration

---

## ADR-006: Session-Based Conversation

**Decision:** Conversation state exists only for the active session.

**Reasoning**
- Assignment does not require authentication.
- Simpler implementation.
- Easy to extend later.

---

## ADR Governance

New architectural decisions should:
1. State the problem.
2. List alternatives.
3. Explain the chosen approach.
4. Describe long-term consequences.
