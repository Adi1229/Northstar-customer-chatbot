
# Product Requirements Document (PRD)

# Project
**NorthStar AI Customer Support Chatbot**

Version: 1.0

---

# 1. Executive Summary

NorthStar AI Customer Support Chatbot is an offline AI-assisted customer support chatbot built for a fictional outdoor apparel and camping gear company.

The chatbot uses local Natural Language Processing (NLP) for semantic intent recognition instead of keyword matching. It is designed with a modular, production-inspired architecture that separates presentation, business logic, NLP, and data access.

The implementation uses a local SQLite database for demonstration while keeping the database layer abstract so it can later be replaced by PostgreSQL, MySQL, MongoDB, REST APIs, or enterprise order-management systems with minimal code changes.

---

# 2. Problem Statement

Small businesses often need customer support automation but cannot always afford enterprise chatbot platforms.

This project demonstrates how a lightweight AI-powered chatbot can:

- Understand customer intent
- Track orders
- Explain return policies
- Recommend products
- Simulate human handoff

without requiring cloud APIs or paid services.

---

# 3. Vision

Build a modular chatbot that is:

- Intelligent
- Offline
- Easily maintainable
- Easily extendable
- Ready for future enterprise integration

---

# 4. Project Goals

## Primary Goals

- Semantic intent recognition using local NLP
- Offline execution
- Clean software architecture
- Fully testable without API keys
- Production-style code organization

## Secondary Goals

- Conversation memory
- Swappable database layer
- Modular business services
- Professional documentation

---

# 5. Scope

## In Scope

- Chat interface
- NLP intent recognition
- Order tracking
- Return & exchange information
- Product recommendations
- Shipping information
- Human handoff
- Fallback handling
- Local SQLite database
- Conversation memory

## Out of Scope

- Payment processing
- Authentication
- Live customer database
- Cloud deployment
- External APIs
- LLM integration
- Voice support

---

# 6. Target Users

## Customer

Needs quick answers about:

- Orders
- Returns
- Shipping
- Product recommendations

## Business

Needs:

- Lower support workload
- Better customer experience
- Easy future integration

---

# 7. Functional Requirements

## FR-1 Intent Recognition

The chatbot shall classify semantically similar user queries into the same intent.

Example:

- Where is my package?
- Track my order.
- Has my shipment arrived?

↓

track_order

---

## FR-2 Order Tracking

The chatbot shall:

- Ask for order number
- Query database
- Display status
- Handle invalid orders

---

## FR-3 Return Policy

Provide:

- 30-day return policy
- Original packaging requirement
- Unused item requirement

---

## FR-4 Shipping

Provide:

- Standard shipping
- Expedited shipping

---

## FR-5 Product Recommendation

Ask up to two clarification questions.

Recommend categories using business rules.

---

## FR-6 Human Handoff

Simulate:

- Live agent transfer
- Return to chatbot

---

## FR-7 Conversation Memory

Maintain context during one session.

Example:

User:
Where is my order?

Bot:
Order number?

User:
111

Bot:
Shipped.

User:
Can I return it?

Bot understands "it" refers to order 111.

---

# 8. Non-Functional Requirements

- Offline execution
- Modular architecture
- High readability
- Easy maintenance
- Replaceable database layer
- Fast response (<1 second on local machine)

---

# 9. Architecture Principles

- Separation of Concerns
- Single Responsibility Principle
- Service Layer Pattern
- Repository/Data Access Layer
- Dependency Injection where appropriate
- Configuration-driven components

---

# 10. Technology Stack

Frontend:
- Streamlit

Backend:
- Python

NLP:
- sentence-transformers (MiniLM)

Database:
- SQLite

ORM:
- SQLAlchemy

Similarity:
- Cosine Similarity

---

# 11. Database Strategy

Current:

SQLite

Future:

- PostgreSQL
- MySQL
- MongoDB
- REST API
- ERP Integration

No chatbot logic should depend directly on the database implementation.

---

# 12. Success Criteria

The chatbot should:

- Correctly identify intents
- Return correct mock order status
- Recommend products
- Handle fallback
- Simulate human handoff
- Run completely offline
- Be easily extendable

---

# 13. Risks

- NLP confidence threshold tuning
- Ambiguous user input
- Future schema changes

Mitigation:

- Modular services
- Configurable thresholds
- Adapter-based database layer

---

# 14. Future Enhancements

- PostgreSQL
- Company REST APIs
- Vector Search
- RAG
- Local LLM support
- Admin dashboard
- Analytics
- User authentication

---

# 15. Milestones

Phase 1
- Documentation

Phase 2
- Project Initialization

Phase 3
- Database Layer

Phase 4
- NLP Engine

Phase 5
- Conversation Manager

Phase 6
- Business Services

Phase 7
- Streamlit UI

Phase 8
- Testing

Phase 9
- Documentation & Demo

---

# 16. Acceptance Criteria

✓ Chatbot runs locally.

✓ No external APIs required.

✓ Semantic intent recognition works.

✓ Order tracking returns expected results.

✓ Return policy and shipping information are correct.

✓ Product recommendation asks clarification questions.

✓ Human handoff is implemented.

✓ Fallback handling exists.

✓ Database layer can be replaced without changing chatbot logic.

---

# 17. Guiding Design Philosophy

The chatbot should demonstrate production-quality software engineering rather than simply satisfying functional requirements.

AI is responsible for understanding user language.

Business services are responsible for enforcing business rules.

The data layer is responsible for retrieving information.

Each layer should remain independent, testable, and replaceable.
