
# SYSTEM_DESIGN.md

# NorthStar AI Customer Support Chatbot
## System Design Document

Version: 1.0

---

# Purpose

This document defines the technical architecture of the NorthStar AI Customer Support Chatbot.

The system is designed around modular components with clear responsibilities so that individual layers can evolve independently.

---

# Design Principles

- Separation of Concerns
- Single Responsibility Principle
- Modular Services
- Offline First
- Pluggable Data Layer
- AI for Understanding, Rules for Business Logic

---

# High-Level Architecture

```text
                   User
                     │
                     ▼
             Streamlit Chat UI
                     │
                     ▼
          Conversation Manager
                     │
                     ▼
          NLP Intent Classifier
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 Order Service  Return Service  Recommendation Service
      │              │              │
      └──────────────┼──────────────┘
                     ▼
             Data Access Layer
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
    SQLite      PostgreSQL      REST API
    (Demo)        (Future)      (Future)
```

---

# Component Responsibilities

## Streamlit UI

Responsibilities:
- Display chat
- Capture user input
- Show conversation history
- Maintain session ID

The UI never contains business logic.

---

## Conversation Manager

Responsibilities:
- Receive messages
- Maintain conversation state
- Track active intent
- Manage follow-up questions
- Route requests to services

---

## NLP Layer

Responsibilities:
- Generate sentence embeddings
- Compute semantic similarity
- Select best matching intent
- Return confidence score

Model:
- sentence-transformers/all-MiniLM-L6-v2

---

## Business Services

### Order Service
- Validate order ID
- Retrieve order
- Format response

### Return Service
- Return policy
- Shipping policy

### Recommendation Service
- Ask clarifying questions
- Apply recommendation rules
- Recommend product categories

### Handoff Service
- Simulate live agent
- Resume chatbot

---

# Data Access Layer

Purpose

Hide the underlying database implementation.

Every service interacts only with the DAL interface.

Example

Conversation Manager
→ Order Service
→ DAL
→ SQLite

Replacing SQLite requires only a new adapter.

---

# Request Lifecycle

1. User submits a message.
2. Conversation Manager forwards it to the NLP classifier.
3. Classifier identifies the intent.
4. Conversation Manager routes to the correct service.
5. Service requests data through the DAL.
6. DAL retrieves data from SQLite.
7. Service formats the response.
8. UI displays the response.

---

# Sequence Diagram

```text
User
 │
 ▼
UI
 │
 ▼
Conversation Manager
 │
 ▼
Intent Classifier
 │
 ▼
Order Service
 │
 ▼
Data Access Layer
 │
 ▼
SQLite
 │
 ▲
Response
 │
 ▲
Conversation Manager
 │
 ▲
UI
```

---

# Database Strategy

Current:
- SQLite

Future:
- PostgreSQL
- MySQL
- MongoDB
- ERP APIs
- Shopify APIs

No other component should require changes when the adapter changes.

---

# Conversation State

Session stores:
- Current intent
- Previous intent
- Last order number
- Recommendation answers
- Conversation history

State is valid only during the active chat session.

---

# Recommendation Flow

User
→ "Need camping gear"

Conversation Manager
→ Ask activity if missing
→ Ask weather if missing

Recommendation Service
→ Apply business rules
→ Return matching categories

No LLM is required for recommendations.

---

# Error Handling

Unknown intent:
- Show fallback
- Offer supported options

Invalid order:
- Inform user
- Request a valid order number

Database error:
- Log exception
- Return friendly message

---

# Logging

Log:
- User intent
- Confidence score
- Service invoked
- Database query status
- Errors

Do not log sensitive user data.

---

# Scalability

Future enhancements:
- Multi-user support
- Authentication
- REST API backend
- Vector search
- Local LLM plugin
- Analytics dashboard

Current architecture supports these additions without major refactoring.

---

# Design Decisions

Why Streamlit?
- Fast development
- Clean interface
- Pure Python

Why MiniLM?
- Local execution
- Semantic understanding
- Lightweight

Why SQLite?
- Offline
- Zero configuration
- Replaceable

Why Service Layer?
- Testable
- Maintainable
- Business logic isolation

Why Data Access Layer?
- Database independence
- Enterprise-ready architecture

---

# Summary

The architecture separates presentation, NLP, business logic, and persistence.

This enables:
- Easy testing
- Future integrations
- Offline execution
- Clean maintenance
- Production-inspired scalability
