
# CONVERSATION_MANAGER.md

# NorthStar AI Customer Support Chatbot
## Conversation Management Design

Version: 1.0

---

# Purpose

The Conversation Manager is the orchestration layer of the chatbot. It coordinates interactions between the user, NLP engine, business services, and the data access layer while maintaining conversational context throughout a session.

Unlike the NLP layer, which only predicts user intent, the Conversation Manager decides **what should happen next**.

---

# Objectives

- Maintain conversation state
- Route requests to the correct service
- Handle multi-turn conversations
- Ask clarifying questions
- Preserve context
- Recover from misunderstandings
- Keep services independent

---

# Position in the Architecture

```text
User
   │
   ▼
Streamlit UI
   │
   ▼
Conversation Manager
   ├──────────────┐
   ▼              ▼
NLP Engine   Session State
   │              │
   └──────┬───────┘
          ▼
 Business Services
          │
          ▼
 Data Access Layer
```

---

# Responsibilities

The Conversation Manager is responsible for:

- Receiving every user message
- Calling the NLP intent classifier
- Managing conversation context
- Determining if additional information is required
- Routing requests to business services
- Returning formatted responses
- Managing session lifecycle

It **does not**:
- Access the database directly
- Perform semantic similarity calculations
- Contain UI code

---

# Session State

Each chat session stores:

| Field | Description |
|--------|-------------|
| session_id | Unique session identifier |
| current_intent | Active user intent |
| previous_intent | Previous completed intent |
| pending_question | Information still required |
| last_order_id | Most recent order number |
| recommendation_context | User preferences collected |
| conversation_history | Chat transcript |

State exists only for the current chat session.

---

# Conversation Lifecycle

```text
User Message
      │
      ▼
Intent Classification
      │
      ▼
Need More Information?
      │
 ┌────┴────┐
 │         │
Yes        No
 │         │
 ▼         ▼
Ask      Execute
Question Service
 │         │
 └────┬────┘
      ▼
Generate Response
      │
      ▼
Return to User
```

---

# Intent Routing

| Intent | Service |
|--------|---------|
| greeting | Greeting Service |
| track_order | Order Service |
| return_policy | Return Service |
| shipping_info | Return Service |
| product_recommendation | Recommendation Service |
| human_handoff | Handoff Service |
| goodbye | Conversation End |
| fallback | Fallback Handler |

---

# Order Tracking Flow

Example

```text
User:
Where is my order?

↓

Intent:
track_order

↓

Order number available?

↓

No

↓

Ask:
"What is your order number?"

↓

User:
111

↓

Order Service

↓

SQLite

↓

Response:
Your order has shipped and is arriving tomorrow.
```

---

# Product Recommendation Flow

The chatbot gathers missing information gradually.

Example

```text
User:
I need camping gear.

↓

Ask activity

↓

Camping

↓

Ask weather

↓

Cold

↓

Recommendation Service

↓

Sleeping Bag
Insulated Jacket
4-Season Tent
```

Only the missing information should be requested.

---

# Return Policy Flow

User:
Can I return an item?

↓

Return Service

↓

Display:
- Return period
- Item condition
- Packaging requirements

No clarification required.

---

# Shipping Information Flow

User:
How long is shipping?

↓

Return Service

↓

Display:
- Standard shipping
- Expedited shipping

---

# Human Handoff Flow

```text
User:
I want to talk to someone.

↓

Handoff Service

↓

"Connecting you to a support representative..."

↓

Simulated delay

↓

Conversation resumes
```

---

# Context Preservation

Example

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

The Conversation Manager resolves **"it"** using `last_order_id`.

---

# Context Switching

Users may change topics at any time.

Example

User:
Where is my order?

↓

Order flow

↓

User:
Actually, tell me about returns.

↓

Conversation Manager

↓

Switch active intent

↓

Return Service

No restart required.

---

# Fallback Strategy

Unknown request:

1. Inform the user politely.
2. Suggest supported features.
3. Preserve session state.
4. Continue the conversation.

Repeated failures may trigger a recommendation to contact a human agent.

---

# Error Recovery

Examples

- Invalid order ID
- Empty message
- Unsupported request
- Missing clarification response

Recovery should always:

- Preserve state
- Explain the issue
- Request corrective input

---

# Response Generation Rules

Responses should be:

- Friendly
- Concise
- Consistent
- Deterministic
- Free of implementation details

Business services provide content; the Conversation Manager formats the conversational flow.

---

# Extensibility

To add a new intent:

1. Extend `intents.json`
2. Add a business service
3. Register routing logic
4. Update test cases

No existing services should require modification.

---

# Testing Checklist

- Greeting flow
- Order tracking with valid IDs
- Invalid order handling
- Return policy
- Shipping information
- Product recommendation dialogue
- Human handoff
- Context preservation
- Intent switching
- Unknown intent fallback

---

# Definition of Success

The Conversation Manager is successful when it:

- Maintains context across turns.
- Routes every intent correctly.
- Requests only missing information.
- Supports topic switching.
- Handles failures gracefully.
- Keeps the UI, NLP, and business services decoupled.
