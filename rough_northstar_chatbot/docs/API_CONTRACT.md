
# API_CONTRACT.md

# NorthStar AI Customer Support Chatbot
## Internal Service Contracts

Version: 1.0

---

# Purpose

This document defines the contracts between internal modules. These are Python interfaces—not external HTTP APIs.

---

# Conversation Manager

Input

```python
handle_message(user_message: str) -> ChatResponse
```

Output

```python
ChatResponse(
    message: str,
    intent: str,
    requires_followup: bool
)
```

---

# Intent Classifier

```python
classify(text: str) -> IntentResult
```

Returns

```python
IntentResult(
    intent: str,
    confidence: float
)
```

---

# Repository Interface

```python
get_order(order_id: str)

get_products(filters: dict)

get_recommendations(activity: str,
                    weather: str,
                    experience: str)
```

Every database adapter must implement these methods.

---

# Order Service

Input:
- order_id

Output:
- formatted customer response

Errors:
- invalid order
- repository failure

---

# Recommendation Service

Input:
- activity
- weather
- experience

Output:
- recommended product categories

If required fields are missing, the service signals the Conversation Manager to ask follow-up questions.

---

# Return Service

Supported operations:
- return policy
- shipping information

No database access required for the assignment version.

---

# Handoff Service

Input:
- customer request

Output:
- simulated transfer response
- chatbot resume signal

---

# Error Contract

Services must never expose stack traces.

Instead they return structured errors:

```python
ServiceResult(
    success=False,
    error="Invalid order number."
)
```

The Conversation Manager converts these into user-facing responses.

---

# Stability Rules

- Contracts are backward compatible.
- Business services never call Streamlit.
- NLP never formats responses.
- Database adapters never contain business logic.

Any future REST API implementation should preserve these contracts to minimize refactoring.
