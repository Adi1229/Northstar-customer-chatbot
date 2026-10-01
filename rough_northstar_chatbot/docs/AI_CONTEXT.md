
# AI_CONTEXT.md

# NorthStar AI Customer Support Chatbot
## AI Development Context

Version: 1.0

---

# Purpose

This document provides persistent project context for AI coding assistants (Cursor, Claude Code, Windsurf, Gemini CLI, ChatGPT). It defines the project's non-negotiable architectural decisions so future code generation remains consistent.

---

# Project Summary

Build an **offline AI-powered customer support chatbot** for a fictional outdoor apparel company.

Required features:
- Order tracking
- Return policy
- Shipping information
- Product recommendations
- Human handoff
- Fallback handling

No deployment or cloud APIs are required.

---

# Non-Negotiable Rules

1. Offline only.
2. No OpenAI/Gemini/Anthropic APIs.
3. Use `sentence-transformers/all-MiniLM-L6-v2`.
4. Business logic must be deterministic.
5. SQLite is the demo database.
6. Database access only through the Repository/Data Access Layer.
7. Streamlit contains presentation only.
8. Every module must have a single responsibility.
9. Keep components independently testable.
10. Favor extensibility over shortcuts.

---

# Architecture Summary

Streamlit UI
→ Conversation Manager
→ NLP Intent Classifier
→ Business Services
→ Repository Interface
→ SQLite Adapter

Future adapters:
- PostgreSQL
- REST API
- Enterprise OMS

---

# Current Intent Set

- greeting
- track_order
- return_policy
- shipping_info
- product_recommendation
- human_handoff
- goodbye
- fallback

---

# Assignment Data

Orders:

111 → Shipped (Arriving Tomorrow)

222 → Processing (Ships in 24 Hours)

333 → Delivered

Any other order → Invalid Order

---

# Coding Priorities

1. Readability
2. Maintainability
3. Separation of Concerns
4. Testability
5. Clear documentation

Never trade these for shorter code.

---

# Implementation Strategy

Generate code one module at a time.

Complete sequence:

Database
→ NLP
→ Conversation Manager
→ Services
→ UI
→ Tests

Do not skip layers.

---

# Future Expansion

Architecture must support:

- PostgreSQL
- Vector search
- Local LLM plug-in
- Authentication
- Analytics
without major refactoring.

---

# AI Prompt Reminder

When generating code:

- Respect existing contracts.
- Avoid changing stable interfaces.
- Keep business logic out of the UI.
- Never bypass the repository layer.
- Write production-quality Python with type hints and docstrings.
