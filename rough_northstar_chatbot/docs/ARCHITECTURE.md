
# ARCHITECTURE.md

# NorthStar AI Customer Support Chatbot
## Software Architecture Guide

Version: 1.0

---

# Purpose

This document defines the software architecture, design patterns, module boundaries, and dependency rules for the project.

The goal is to ensure the chatbot remains modular, testable, and easy to extend without rewriting existing components.

---

# Architectural Style

The application follows a layered architecture inspired by Clean Architecture.

```text
Presentation Layer
        │
        ▼
Conversation Layer
        │
        ▼
NLP Layer
        │
        ▼
Business Service Layer
        │
        ▼
Repository / Data Access Layer
        │
        ▼
Persistence Layer
```

Each layer only communicates with the layer directly below it.

---

# Core Design Principles

- Separation of Concerns
- Single Responsibility Principle
- Open/Closed Principle
- Dependency Inversion
- Composition over Inheritance
- Configuration over Hardcoding

---

# Layer Responsibilities

## 1. Presentation Layer

Location

```
app.py
```

Responsibilities

- Render Streamlit interface
- Accept user input
- Display responses
- Maintain Streamlit session

Must NOT

- Query database
- Detect intents
- Apply business rules

---

## 2. Conversation Layer

Location

```
chatbot/
```

Responsibilities

- Route requests
- Maintain context
- Handle follow-up questions
- Track dialogue state
- Call business services

Acts as the orchestrator.

---

## 3. NLP Layer

Location

```
nlp/
```

Responsibilities

- Load MiniLM model
- Create embeddings
- Compare semantic similarity
- Predict user intent

Output

```
{
    "intent": "track_order",
    "confidence": 0.91
}
```

The NLP layer never accesses the database.

---

## 4. Business Service Layer

Location

```
services/
```

Services

- OrderService
- ReturnService
- RecommendationService
- HandoffService

Responsibilities

- Validate business rules
- Prepare responses
- Coordinate repository calls

Business services know nothing about Streamlit.

---

## 5. Repository / Data Access Layer

Location

```
database/
```

Responsibilities

- Hide persistence implementation
- Provide a stable interface
- Support multiple adapters

Current adapter

```
SQLiteAdapter
```

Future adapters

- PostgreSQLAdapter
- MongoAdapter
- CompanyAPIAdapter

---

## 6. Persistence Layer

Current implementation

SQLite

Future

- PostgreSQL
- MySQL
- MongoDB
- Enterprise APIs

The persistence layer should be replaceable without affecting the application.

---

# Dependency Rules

Allowed

Presentation
→ Conversation

Conversation
→ NLP

Conversation
→ Services

Services
→ Repository

Repository
→ Database

Forbidden

Presentation
→ Database

Presentation
→ SQLite

NLP
→ Database

Database
→ Streamlit

---

# Repository Pattern

Business services call repository methods rather than SQL directly.

Example interface

```
get_order(order_id)
get_products(filters)
```

Changing the storage technology requires implementing the same interface.

---

# Adapter Pattern

Every database implementation must expose the same contract.

Example

```
SQLiteAdapter
PostgresAdapter
APIAdapter
```

The active adapter is selected through configuration.

---

# Configuration Strategy

Example

```
DATABASE_BACKEND = sqlite
```

Changing to PostgreSQL should require only configuration and a new adapter implementation.

---

# Package Structure

```
chatbot/
database/
models/
nlp/
services/
data/
tests/
docs/
```

Each package owns one responsibility.

---

# Error Flow

Unknown Intent

Conversation Manager
→ Fallback response

Invalid Order

OrderService
→ Friendly validation message

Database Failure

Repository
→ Log
→ Graceful error message

---

# Logging Strategy

Log

- Session ID
- Intent
- Confidence
- Service name
- Database adapter
- Errors

Never log sensitive information.

---

# Future Evolution

Phase 1

SQLite

↓

Phase 2

PostgreSQL

↓

Phase 3

REST API

↓

Phase 4

Enterprise OMS

↓

Phase 5

Hybrid RAG + LLM

No previous layer should require redesign.

---

# Engineering Philosophy

AI is responsible for understanding language.

Business services enforce business rules.

Repositories provide data.

Presentation displays information.

Each layer has exactly one reason to change.

---

# Definition of Architectural Success

The architecture is considered successful if:

- Database technology can change without modifying chatbot logic.
- UI can be replaced without affecting business services.
- NLP model can be upgraded independently.
- New services can be added with minimal changes.
- Every module is independently testable.
