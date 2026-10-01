
# TESTING_PLAN.md

# NorthStar AI Customer Support Chatbot
## Test Strategy & Validation Plan

Version: 1.0

---

# Purpose

This document defines the testing strategy to verify that every module behaves correctly and that the completed chatbot satisfies all assignment requirements.

---

# Testing Objectives

- Validate functional correctness
- Verify module integration
- Ensure architectural boundaries are respected
- Confirm offline execution
- Detect regressions

---

# Test Pyramid

```text
          End-to-End
        Integration Tests
          Unit Tests
```

Priority:
1. Unit Tests
2. Integration Tests
3. End-to-End Tests

---

# Unit Tests

## NLP

- Intent classification
- Confidence threshold
- Unknown intent
- Empty input

## Services

Order Service
- Valid order
- Invalid order

Return Service
- Return policy
- Shipping information

Recommendation Service
- Complete preferences
- Missing preferences

Handoff Service
- Handoff message
- Resume conversation

## Database

- Database initialization
- Seed data loading
- Repository queries

---

# Integration Tests

Conversation Manager + NLP

Conversation Manager + Services

Services + Repository

Repository + SQLite

Verify each interface contract.

---

# End-to-End Scenarios

Scenario 1
Greeting → Order Tracking → Exit

Scenario 2
Order Tracking → Returns

Scenario 3
Recommendation Flow

Scenario 4
Shipping Information

Scenario 5
Human Handoff

Scenario 6
Fallback Recovery

---

# Assignment Validation

Required mock orders:

111 → Shipped (Arriving Tomorrow)

222 → Processing (Ships in 24 Hours)

333 → Delivered

Other IDs → Invalid Order

Verify all outputs exactly.

---

# Non-Functional Tests

- Application launches successfully
- Offline execution
- Response latency < 1 second (local)
- No external API calls

---

# Regression Checklist

Before every release:

- Existing intents still classify correctly
- Database schema unchanged
- Services respect API contracts
- UI still renders correctly

---

# Success Criteria

The project passes when:

- All unit tests pass
- All integration tests pass
- All assignment scenarios succeed
- No architectural rules are violated
