# 🎬 NorthStar Chatbot — Video Demo Script

> **Target length:** 2–3 minutes  
> **Before recording:** Launch the app with `streamlit run app.py`, open **http://localhost:8501**, and make sure the chat window is visible and full-screen.

---

## 🎤 Opening (~10 sec — say on camera)

> *"Hi, I'm demonstrating the NorthStar AI Customer Support Chatbot — an offline, AI-powered chatbot built with semantic intent classification using a local MiniLM model. Let me walk you through all four use cases."*

---

## 📦 Scene 1 — Order Tracking (Multi-turn flow)

**Say:** *"First, order tracking."*

**Type this exactly:**
```
where is my order
```
**Bot responds:** "Could you please provide your **order number**?"

**Type:**
```
111
```
**Bot responds:** Order `111` — **Shipped**, Arriving Tomorrow ✅

**Type (to show a DIFFERENT order — proves multi-order support):**
```
track another order
```
**Bot asks again for order number**

**Type:**
```
222
```
**Bot responds:** Order `222` — **Processing**, Ships in 24 Hours ✅

---

## 🔄 Scene 2 — Return Policy & Shipping Info

**Say:** *"Now let me ask about returns."*

**Type:**
```
I received a damaged item and want to return it
```
**Bot responds:** Full 30-day return & exchange policy ✅

**Type (bonus — shipping info):**
```
what are your shipping options
```
**Bot responds:** Shipping information with standard & expedited timelines ✅

---

## 🛒 Scene 3 — Product Recommendations (Two-turn flow)

**Say:** *"Next, product recommendations — a two-question conversational flow."*

**Type:**
```
I need some gear recommendations
```
**Bot asks:** "What activity are you planning? (e.g. Camping, Hiking)"

**Type:**
```
Hiking
```
**Bot asks:** "What kind of weather are you expecting? (e.g. Cold, Warm, Rainy)"

**Type:**
```
Rainy
```
**Bot responds:** Recommends **Packable Rain Jacket** + **Waterproof Hiking Boots** ✅

> 💡 Alternative combo: **Camping → Cold** → Sleeping Bag + Insulated Jacket + 4-Season Tent

---

## 🎧 Scene 4 — Human Handoff

**Say:** *"Now, escalation to a live agent."*

**Type:**
```
I need to speak to a human agent
```
**Bot responds:** Simulated agent transfer message ✅

---

## ⚠️ Scene 5 — Fallback Handling

**Say:** *"Finally, let me show what happens with an unrecognised message."*

**Type:**
```
asdfjkl qwerty blah
```
**Bot responds:** "I didn't understand" fallback message ✅

**Type (show graceful recovery):**
```
return policy
```
**Bot correctly responds** with return policy — showing it recovers cleanly ✅

---

## 🎤 Closing (~10 sec — say on camera)

> *"All four required use cases are covered — order tracking with multi-order support, returns, product recommendations, and live agent handoff — plus fallback handling. The bot runs fully offline with no API keys needed. Thank you!"*

---

## 📝 Quick Reference — All Exact Inputs

| # | Type This | Expected Response |
|---|-----------|-------------------|
| 1 | `where is my order` | Asks for order number |
| 2 | `111` | Order Shipped — Arriving Tomorrow |
| 3 | `track another order` | Asks for order number again |
| 4 | `222` | Order Processing — Ships in 24 Hours |
| 5 | `I received a damaged item and want to return it` | 30-day return policy |
| 6 | `what are your shipping options` | Shipping info |
| 7 | `I need some gear recommendations` | Asks for activity |
| 8 | `Hiking` | Asks for weather |
| 9 | `Rainy` | Rain Jacket + Hiking Boots |
| 10 | `I need to speak to a human agent` | Simulated handoff |
| 11 | `asdfjkl qwerty blah` | Fallback — I didn't understand |
| 12 | `return policy` | Recovers and responds correctly |

---

> ✅ This script covers **all 5 contract checklist items**: order tracking, returns, shipping, recommendations, handoff, and fallback.
