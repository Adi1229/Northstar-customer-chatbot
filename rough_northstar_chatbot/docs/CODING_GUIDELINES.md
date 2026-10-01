
# CODING_GUIDELINES.md

# NorthStar AI Customer Support Chatbot
## Coding Standards

Version: 1.0

---

# Purpose

Define consistent coding standards for every contributor and AI assistant.

---

# Python Standards

- Python 3.11+
- PEP 8 compliant
- Black-compatible formatting
- Type hints required
- Docstrings for public classes and methods

---

# Naming

Classes:
- PascalCase

Functions:
- snake_case

Variables:
- snake_case

Constants:
- UPPER_CASE

Private helpers:
- _leading_underscore

---

# Imports

Order:

1. Standard library
2. Third-party
3. Local packages

Avoid wildcard imports.

---

# Error Handling

- Raise meaningful exceptions.
- Catch exceptions at service boundaries.
- Never expose stack traces to users.
- Log technical details internally.

---

# Logging

Log:
- Intent detected
- Confidence score
- Active service
- Database adapter
- Errors

Do not log personal or sensitive information.

---

# Service Rules

Services must:
- Contain business logic only.
- Depend on repository interfaces.
- Never import Streamlit.

---

# Repository Rules

Repositories:
- Handle persistence only.
- Never apply business rules.
- Never format user-facing messages.

---

# Testing Expectations

Every new module should include:

- Happy-path tests
- Invalid input tests
- Edge cases
- Error handling tests

---

# Documentation

Every public class should describe:
- Purpose
- Inputs
- Outputs
- Exceptions

Complex logic should include concise inline comments explaining *why*, not *what*.

---

# Pull Request Checklist

Before considering work complete:

- Code runs.
- Tests pass.
- Type hints added.
- Docstrings written.
- Logging added where appropriate.
- No architectural boundaries violated.

---

# Definition of Quality

Good code is:

- Readable
- Predictable
- Modular
- Testable
- Easy to extend

Avoid clever implementations that reduce maintainability.
