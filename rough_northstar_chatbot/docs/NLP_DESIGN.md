
# NLP_DESIGN.md

# NorthStar AI Customer Support Chatbot
## Natural Language Processing Design

Version: 1.0

---

# Purpose

This document specifies how the chatbot understands natural language without using cloud-based Large Language Models (LLMs). The system uses local semantic embeddings to classify user intent while keeping all business logic deterministic.

---

# Design Goals

- Offline execution
- Semantic understanding
- Fast inference
- Lightweight model
- Easy to extend
- No API keys
- Deterministic business logic

---

# NLP Pipeline

```text
User Message
      │
      ▼
Text Normalization
      │
      ▼
Sentence Embedding (MiniLM)
      │
      ▼
Cosine Similarity
      │
      ▼
Intent Classification
      │
      ▼
Confidence Evaluation
      │
      ▼
Conversation Manager
```

---

# Selected Model

Model:

`sentence-transformers/all-MiniLM-L6-v2`

Reasons:

- Small (~80 MB)
- Fast on CPU
- Excellent semantic search performance
- No internet required after download
- Well supported by Sentence Transformers

---

# Intent Set

Core intents:

| Intent | Purpose |
|---------|---------|
| track_order | Order tracking |
| return_policy | Return & exchange questions |
| shipping_info | Shipping information |
| product_recommendation | Recommend products |
| human_handoff | Simulated live agent |
| greeting | Welcome users |
| goodbye | End conversation |
| fallback | Unknown requests |

---

# Intent Dataset

Example `intents.json` structure:

```json
{
  "track_order": [
    "Where is my order?",
    "Track my shipment",
    "Has my package arrived?",
    "Check order status"
  ]
}
```

Each intent should contain many paraphrases to improve semantic matching.

---

# Embedding Generation

1. Load the MiniLM model once during application startup.
2. Encode all training examples into embeddings.
3. Cache embeddings in memory.
4. Encode each user message.
5. Compare against cached embeddings.

Caching avoids repeated computation and improves response time.

---

# Similarity Algorithm

Cosine similarity is used to compare embeddings.

```text
Highest Similarity
        │
        ▼
Best Matching Intent
```

The intent with the highest score above the configured threshold is selected.

---

# Confidence Threshold

Recommended values:

| Score | Action |
|------:|--------|
| ≥ 0.80 | Accept confidently |
| 0.60–0.79 | Accept with caution |
| < 0.60 | Trigger fallback |

Thresholds should be configurable through `config.py`.

---

# Conversation Context

The NLP layer predicts the current intent only.

The Conversation Manager is responsible for resolving context.

Example:

User: "Where is my order?"

Bot: "What is your order number?"

User: "111"

The NLP model identifies a numeric reply, while the Conversation Manager interprets it as the order ID for the active `track_order` intent.

---

# Fallback Strategy

If no intent exceeds the confidence threshold:

1. Display a friendly message.
2. Suggest supported topics.
3. Preserve conversation state.
4. Allow the user to try again.

Example:

> "I'm not sure I understood that. I can help with order tracking, shipping, returns, product recommendations, or connecting you to a support agent."

---

# Extending the System

To add a new intent:

1. Add examples to `intents.json`.
2. Restart the application.
3. Rebuild cached embeddings.

No model retraining is required.

---

# Performance Targets

- Model load: < 5 seconds
- Intent prediction: < 200 ms
- CPU friendly
- Memory efficient

---

# Error Handling

Potential issues:

- Missing model
- Corrupted intent file
- Empty user input

Handling:

- Log the error
- Return a friendly message
- Keep the application running whenever possible

---

# Testing Strategy

Test cases should verify:

- Correct intent classification
- Paraphrase recognition
- Unknown intent handling
- Threshold behaviour
- Context-aware follow-up
- Numeric order ID continuation

---

# Future Improvements

- Fine-tuned sentence transformer
- Vector database for large intent libraries
- Multilingual support
- Hybrid intent classifier
- Local LLM plug-in
- Retrieval-Augmented Generation (RAG)

---

# Definition of Success

The NLP layer is successful when it:

- Correctly recognizes user intent from varied wording.
- Works completely offline.
- Returns consistent confidence scores.
- Can be extended without retraining.
- Remains independent from business logic and persistence.
