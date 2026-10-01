
# TASKS.md

# NorthStar AI Customer Support Chatbot
## Development Backlog

Version: 1.0

---

# Purpose

This document tracks implementation tasks, priorities, dependencies, and completion status.

Legend:

- [ ] Not Started
- [x] Complete

---

# Phase 1 — Project Setup

- [ ] Create repository
- [ ] Create folder structure
- [ ] Configure virtual environment
- [ ] Install dependencies
- [ ] Configure Streamlit
- [ ] Create configuration module

Dependency:
None

---

# Phase 2 — Database

- [ ] SQLAlchemy models
- [ ] Repository interface
- [ ] SQLite adapter
- [ ] Database initialization
- [ ] Seed assignment data

Depends on:
Project setup

---

# Phase 3 — NLP

- [ ] Install sentence-transformers
- [ ] Load MiniLM
- [ ] Create intents.json
- [ ] Build embedding cache
- [ ] Implement classifier

Depends on:
Project setup

---

# Phase 4 — Conversation Layer

- [ ] Session manager
- [ ] Conversation manager
- [ ] Intent router
- [ ] Context handling

Depends on:
Database + NLP

---

# Phase 5 — Services

- [ ] Order Service
- [ ] Return Service
- [ ] Recommendation Service
- [ ] Handoff Service

Depends on:
Conversation Layer

---

# Phase 6 — UI

- [ ] Streamlit chat interface
- [ ] Sidebar
- [ ] Chat history
- [ ] Reset session

Depends on:
Services

---

# Phase 7 — Testing

- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end scenarios
- [ ] Assignment validation

Depends on:
All implementation phases

---

# Phase 8 — Documentation

- [ ] Update README
- [ ] Usage guide
- [ ] Screenshots
- [ ] Demo notes

---

# Final Acceptance Checklist

- [ ] Offline execution
- [ ] Semantic intent recognition
- [ ] Correct order tracking
- [ ] Product recommendations
- [ ] Return policy
- [ ] Shipping information
- [ ] Human handoff
- [ ] Fallback handling
- [ ] Clean architecture maintained
- [ ] Tests passing

---

# Milestone Summary

M1 — Foundation

M2 — Database

M3 — NLP

M4 — Conversation

M5 — Business Services

M6 — UI

M7 — Testing

M8 — Final Delivery
