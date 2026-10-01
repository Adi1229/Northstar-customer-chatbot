
# PROJECT_STRUCTURE.md

# NorthStar AI Customer Support Chatbot
## Project Structure & Module Responsibilities

Version: 1.0

---

# Purpose

This document defines the directory layout, ownership of each package, dependency boundaries, and file responsibilities. Every source file should have one primary responsibility.

---

# Repository Layout

```text
customer-support-chatbot/
│
├── app.py                    # Streamlit entry point
├── config.py                 # Global configuration
├── requirements.txt
├── README.md
│
├── chatbot/
│   ├── conversation.py
│   ├── router.py
│   └── state_manager.py
│
├── nlp/
│   ├── embeddings.py
│   ├── intent_classifier.py
│   └── intents.json
│
├── services/
│   ├── order_service.py
│   ├── return_service.py
│   ├── recommendation_service.py
│   └── handoff_service.py
│
├── database/
│   ├── base.py
│   ├── factory.py
│   ├── repository.py
│   └── sqlite_adapter.py
│
├── models/
│   ├── order.py
│   ├── product.py
│   └── recommendation_rule.py
│
├── data/
│   ├── schema.sql
│   └── seed_data.sql
│
├── tests/
│   ├── test_nlp.py
│   ├── test_services.py
│   ├── test_database.py
│   └── test_chatbot.py
│
└── docs/
    └── (all design documents)
```

---

# Dependency Rules

- `app.py` → chatbot
- chatbot → nlp + services
- services → database
- database → models
- models depend only on SQLAlchemy

Forbidden:
- UI → database
- UI → SQL
- NLP → database
- Services → Streamlit

---

# Module Responsibilities

| Package | Responsibility |
|---------|----------------|
| chatbot | Conversation orchestration |
| nlp | Intent recognition |
| services | Business rules |
| database | Data access abstraction |
| models | ORM entities |
| data | Schema & seed data |
| tests | Automated tests |
| docs | Project documentation |

---

# Coding Rules

- One class per responsibility.
- No circular imports.
- Configuration only in `config.py`.
- Shared constants belong in configuration, not services.
- New features should normally require a new service, not changes across multiple packages.

---

# Definition of Done

A new module is complete when:
- It has a single responsibility.
- It follows dependency rules.
- It is independently testable.
- It includes type hints and docstrings.
