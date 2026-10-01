
# IMPLEMENTATION_PLAN.md

# NorthStar AI Customer Support Chatbot
## Master Implementation Plan

Version: 1.0

---

# Objective

Build a production-inspired, offline AI customer support chatbot using semantic NLP, modular services, and a pluggable database architecture.

Core principles:

- Semantic intent recognition
- Clean Architecture
- Service Layer
- Data Access Layer
- Conversation State Management
- Offline execution
- No external APIs

---

# Development Strategy

We will build the project incrementally.

Each phase must:

- Compile successfully
- Be independently testable
- Include documentation
- Avoid breaking previous modules

---

# Phase 0 — Project Initialization

Goal:
Create the project skeleton.

Deliverables:

- Repository
- Folder structure
- requirements.txt
- configuration
- README
- PRD

Acceptance Criteria

- Project runs
- Dependencies install
- Structure finalized

Estimated Time:
30 minutes

---

# Phase 1 — Database Layer

Objective

Implement a replaceable data access layer.

Tasks

- Create database interface
- Implement SQLite adapter
- Create SQLAlchemy models
- Initialize database
- Seed demo data

Files

database/
    base.py
    sqlite_adapter.py
    factory.py
models/
    order.py
    product.py

Acceptance Criteria

✓ No business logic inside database layer

✓ Database implementation is swappable

---

# Phase 2 — NLP Engine

Objective

Implement semantic intent recognition.

Tasks

- Install sentence-transformers
- Create embedding model
- Load intent examples
- Compute cosine similarity
- Confidence threshold

Files

nlp/
    embeddings.py
    intent_classifier.py
    intents.json

Acceptance Criteria

Queries such as:

- Where is my package?
- Track my order.
- Locate my shipment.

must resolve to:

track_order

---

# Phase 3 — Conversation Manager

Objective

Manage conversational flow.

Responsibilities

- Session state
- Context
- Active intent
- Clarifying questions
- Follow-up handling

Files

chatbot/
    conversation.py
    state_manager.py

Acceptance Criteria

Bot remembers previous conversation during session.

---

# Phase 4 — Business Services

Modules

Order Service

Responsibilities

- Retrieve order
- Validate order
- Format response

Return Service

Responsibilities

- Return policy
- Shipping policy

Recommendation Service

Responsibilities

- Ask clarifying questions
- Apply recommendation rules
- Return product categories

Handoff Service

Responsibilities

- Live agent simulation
- Resume chatbot

Acceptance Criteria

Business logic must never access Streamlit directly.

---

# Phase 5 — User Interface

Technology

Streamlit

Components

- Chat window
- Session history
- Input box
- Sidebar
- Reset conversation

Acceptance Criteria

Clean responsive interface.

---

# Phase 6 — Integration

Integrate

UI

↓

Conversation Manager

↓

Intent Recognition

↓

Business Services

↓

Database Layer

Acceptance Criteria

Complete chatbot works end-to-end.

---

# Phase 7 — Testing

Test Cases

- Order Tracking
- Invalid Order
- Return Policy
- Shipping
- Product Recommendation
- Human Handoff
- Conversation Memory
- Unknown Intent

Acceptance Criteria

100% functional coverage of required use cases.

---

# Phase 8 — Final Polish

Tasks

- Improve responses
- Improve UI
- Add loading indicator
- Improve logging
- Improve documentation

---

# Module Dependency Graph

README
↓

PRD
↓

Database

↓

NLP

↓

Conversation Manager

↓

Business Services

↓

Streamlit

↓

Integration

↓

Testing

↓

Demo

---

# Coding Standards

- Python 3.11+
- PEP8
- Type hints
- Docstrings
- Logging
- Dependency injection where useful
- Configuration driven
- No hardcoded business logic in UI

---

# Definition of Done

The project is complete when:

- All required chatbot features work.
- Semantic intent recognition is operational.
- SQLite stores mock data.
- Database adapter is replaceable.
- Chatbot runs offline.
- Documentation is complete.
- Demo can be recorded without additional setup.

---

# AI IDE Execution Notes

AI coding assistants should implement exactly one phase at a time.

Rules:

1. Never skip phases.
2. Never modify completed modules unless required.
3. Respect separation of concerns.
4. Keep modules independent.
5. Generate production-quality code.
6. Prefer maintainability over shortcuts.
7. Every phase must be executable before moving to the next.
