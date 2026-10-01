# 🎬 NorthStar AI Chatbot v1.1 — Director's Script
## Screen Recording / Video Presentation

---

> ### 📋 BEFORE YOU HIT RECORD
>
> **Checklist:**
> - [ ] Run `streamlit run app.py` from the project folder
> - [ ] Open **http://localhost:8501** in a browser
> - [ ] Zoom browser to **125%** (Ctrl + "+") so text is clearly visible
> - [ ] Maximise the browser window — hide the bookmarks bar
> - [ ] Keep this script on a **second monitor or printed sheet** — do NOT switch windows mid-recording
> - [ ] Do a single **dry-run** first to confirm every response appears as expected
> - [ ] Click **"🔄 New Conversation"** in the sidebar to start fresh before hitting record

---

## ⏱️ Target Runtime: 4–5 minutes

---

---

# 🎙️ SCENE 0 — OPENING (0:00–0:20)

### 🎤 SAY (on camera or voice-over):

> *"Hi — in this video I'm demonstrating the NorthStar AI Customer Support Chatbot, Version 1.1.*
> *This is a fully offline, AI-powered support bot built with a local MiniLM semantic intent classifier,
> a layered Clean Architecture, and a SQLite product database.*
> *I'll walk through all required use cases — order tracking, returns, shipping,
> product recommendations with input validation, and the persistent live agent mode.*
> *Let's get started."*

### 🖥️ SCREEN ACTION:
- Show the full chatbot UI — the welcome message from the bot should already be visible
- Slowly pan the sidebar to show the "What I can help with" list
- Then return focus to the main chat area

---

---

# 📦 SCENE 1 — ORDER TRACKING (0:20–1:10)

### 🎤 SAY:
> *"Scene one — order tracking. The bot uses a multi-turn dialogue to collect the order number before querying the database."*

---

### STEP 1.1 — Trigger the intent

**► TYPE in chat box:**
```
where is my order
```

**Wait for bot response.**

**✅ Expected bot response:**
> *"Sure! Could you please provide your **order number**?"*

### 🎤 SAY:
> *"The bot recognises the order-tracking intent and asks for the order number — it never assumes."*

---

### STEP 1.2 — Provide a valid order

**► TYPE in chat box:**
```
111
```

**Wait for bot response.**

**✅ Expected bot response:**
> Order **#111** — Status: **Shipped** — Estimated delivery: **Arriving Tomorrow**

### 🎤 SAY:
> *"Order 111 is shipped and arriving tomorrow — pulled live from the database."*

---

### STEP 1.3 — Prove multi-order support

**► TYPE in chat box:**
```
I want to track another order
```

**Bot asks for order number again.**

**► TYPE in chat box:**
```
222
```

**✅ Expected bot response:**
> Order **#222** — Status: **Processing** — Estimated delivery: **Ships in 24 Hours**

### 🎤 SAY:
> *"Each tracking request asks for a fresh order number — no stale data from a previous lookup."*

---

### STEP 1.4 — Invalid order number (error handling)

**► TYPE in chat box:**
```
999
```

**✅ Expected bot response:**
> *"I couldn't find an order with that number. Please double-check and try again."*

### 🎤 SAY:
> *"Invalid order IDs are handled gracefully — no crashes, a clear friendly message."*

---

---

# 🔄 SCENE 2 — RETURN POLICY & SHIPPING (1:10–1:40)

### 🎤 SAY:
> *"Scene two — return policy and shipping information. These require no clarifying questions."*

---

### STEP 2.1 — Return policy

**► TYPE in chat box:**
```
I received a damaged item and want to return it
```

**✅ Expected bot response:**
> Full return policy — 30-day window, condition requirements, packaging instructions.

### 🎤 SAY:
> *"Full return policy returned instantly."*

---

### STEP 2.2 — Shipping information

**► TYPE in chat box:**
```
what are your shipping options
```

**✅ Expected bot response:**
> Shipping info — standard and expedited delivery timelines.

### 🎤 SAY:
> *"Shipping options — equally fast, no follow-up needed."*

---

---

# 🛒 SCENE 3 — PRODUCT RECOMMENDATIONS & INPUT VALIDATION (1:40–2:40)

### 🎤 SAY:
> *"Scene three — product recommendations. This is a two-turn flow that collects activity and weather,
> then queries the recommendation engine.*
> *I'll also demonstrate the activity input validation added in Version 1.1."*

---

### STEP 3.1 — Trigger recommendations

**► TYPE in chat box:**
```
I need some outdoor gear suggestions
```

**✅ Expected bot response:**
> *"I'd love to help you find the right gear!
> What activity are you planning? (e.g. Camping, Hiking, Trekking, Fishing)"*

### 🎤 SAY:
> *"The bot asks for the activity. Now — I'll deliberately enter something invalid to show the validation in action."*

---

### STEP 3.2 — Invalid activity #1 (demonstrates Revision 2)

**► TYPE in chat box:**
```
swimming
```

**✅ Expected bot response:**
> *"Sorry, I don't recognise that activity.*
> *Please choose one of:*
> *• Camping*
> *• Fishing*
> *• Hiking*
> *• Trekking"*

### 🎤 SAY:
> *"The bot rejects 'swimming', lists the supported activities,
> and stays inside the recommendation flow — it does NOT fall back to a generic error."*

---

### STEP 3.3 — Invalid activity #2 (garbage input)

**► TYPE in chat box:**
```
asdfgh
```

**✅ Expected bot response:**
> Same validation message — re-prompt with supported activities list.

### 🎤 SAY:
> *"Even complete garbage input stays inside the workflow.
> The NLP classifier is never invoked here — contextual validation only."*

---

### STEP 3.4 — Valid activity accepted

**► TYPE in chat box:**
```
Camping
```

**✅ Expected bot response:**
> *"Great! What kind of weather are you expecting? (e.g. Cold, Warm, Rainy)"*

### 🎤 SAY:
> *"'Camping' is accepted. The bot now asks for weather conditions."*

---

### STEP 3.5 — Provide weather → receive recommendations

**► TYPE in chat box:**
```
Cold
```

**✅ Expected bot response:**
> *"Based on your preferences for **Camping** in **Cold** weather, here's what I recommend:*
> *• ⛺ **Tent** — 4-Season Tent*
> *• 🛏️ **Sleeping** — Insulated Sleeping Bag*
> *• 🧥 **Clothing** — Insulated Jacket*
> *Would you like more information about any of these products?"*

### 🎤 SAY:
> *"Three recommendations returned — matched from the database against Camping and Cold weather rules.*
> *The recommendation engine now normalises input casing automatically,
> so 'camping', 'CAMPING', or 'Camping' all work identically."*

---

---

# 🎧 SCENE 4 — LIVE AGENT MODE — PERSISTENT STATE (2:40–3:45)

### 🎤 SAY:
> *"Scene four — live agent mode. This is the key fix in Version 1.1.*
> *In the previous version, the chatbot would immediately resume normal automated responses
> after the handoff message.*
> *That has been corrected. The bot now stays in live agent mode until the user
> explicitly exits with one of three commands."*

---

### STEP 4.1 — Request a live agent

**► TYPE in chat box:**
```
I need to speak to a human agent
```

**✅ Expected bot response:**
> *"I'm connecting you to a **NorthStar support representative** right now 🎧*
> *⏳ Please hold for a moment...*
> *A member of our team will be with you shortly.
> Your conversation history has been shared with them so you won't need to repeat yourself.*
> *Thank you for your patience!"*

### 🎤 SAY:
> *"The handoff message appears. The chatbot has now entered live agent mode.
> Every message from this point will be held inside that mode
> — no NLP, no intent classification, no service routing."*

---

### STEP 4.2 — Send a regular message — must stay in live agent mode

**► TYPE in chat box:**
```
Hello, I have a question about my order
```

**✅ Expected bot response:**
> *"You are currently connected to a **live support representative**.*
> *Type `menu`, `main menu`, or `exit` to return to the chatbot."*

### 🎤 SAY:
> *"The bot does not process this as an order tracking request.
> It recognises it is in live agent mode and holds the connection."*

---

### STEP 4.3 — Send another message — still locked in live agent mode

**► TYPE in chat box:**
```
Can you check order 333 for me please
```

**✅ Expected bot response:**
> Same live agent holding message.

### 🎤 SAY:
> *"Still in live agent mode. The phrase 'order 333' does not trigger the order tracking service.
> Any message — regardless of content — stays inside the live agent workflow."*

---

### STEP 4.4 — Exit with "exit" command

**► TYPE in chat box:**
```
exit
```

**✅ Expected bot response:**
> *"You have exited live agent mode.*
> *Welcome back! How can I help you today?"*

### 🎤 SAY:
> *"'exit' returns to normal mode instantly.
> Let me also demonstrate the other two exit commands."*

---

### STEP 4.5 — Re-enter and exit with "menu"

**► TYPE in chat box:**
```
Talk to an agent
```

**Wait for handoff message.**

**► TYPE in chat box:**
```
menu
```

**✅ Expected bot response:**
> Exit message — *"You have exited live agent mode. Welcome back!"*

### 🎤 SAY:
> *"'menu' works too. And 'main menu' — all three exit commands are recognised
> regardless of capitalisation."*

---

### STEP 4.6 — Test "main menu" (optional but recommended)

**► TYPE in chat box:**
```
I need to talk to someone
```

**Wait for handoff message.**

**► TYPE in chat box:**
```
main menu
```

**✅ Expected bot response:**
> Exit message.

### 🎤 SAY:
> *"'main menu' — all three exit commands confirmed working."*

---

---

# ❓ SCENE 5 — FALLBACK & RECOVERY (3:45–4:10)

### 🎤 SAY:
> *"Scene five — fallback handling. The bot handles unrecognised input gracefully
> and recovers in the very next message."*

---

### STEP 5.1 — Unrecognised input

**► TYPE in chat box:**
```
fhdjksahfkjhsdf qwerty blah
```

**✅ Expected bot response:**
> *"I'm sorry, I didn't quite understand that.*
> *I can help you with:*
> *• Tracking an order • Return or exchange policy • Shipping information*
> *• Product recommendations • Connecting to a live agent*
> *Could you rephrase your question?"*

### 🎤 SAY:
> *"Graceful fallback — no crash, no error, clear guidance on what the bot supports."*

---

### STEP 5.2 — Clean recovery

**► TYPE in chat box:**
```
return policy
```

**✅ Expected bot response:** Full return policy displayed.

### 🎤 SAY:
> *"And one message later, the bot is back to full functionality."*

---

---

# 🎙️ SCENE 6 — CLOSING (4:10–4:30)

### 🎤 SAY (on camera or voice-over):

> *"That wraps up the NorthStar AI Customer Support Chatbot — Version 1.1.*
>
> *To summarise what was demonstrated:*
>
> *One — multi-turn order tracking with database lookups, multi-order support,
> and graceful invalid order handling.*
>
> *Two — return policy and shipping information, delivered instantly without follow-up questions.*
>
> *Three — product recommendations with contextual input validation —
> invalid activities are rejected and the flow continues without restarting the conversation.*
>
> *Four — persistent live agent mode — the bot stays connected until explicitly told to exit
> using 'exit', 'menu', or 'main menu', with no NLP classification running in the background.*
>
> *And five — clean fallback handling with immediate one-message recovery.*
>
> *The system runs entirely offline — no API keys, no cloud services —
> powered by a local MiniLM model and SQLite.*
>
> *Thank you."*

### 🖥️ SCREEN ACTION:
- End on the chat window with a clean, readable conversation history
- Optional: slowly scroll the sidebar to show the "Powered by MiniLM · Runs offline" footer

---

---

# 📋 CHEAT SHEET — PRINT THIS PAGE

| # | Scene | ► TYPE THIS EXACTLY | ✅ Expected Result |
|---|-------|---------------------|-------------------|
| 1 | Order | `where is my order` | Asks for order number |
| 2 | Order | `111` | Shipped — Arriving Tomorrow |
| 3 | Order | `I want to track another order` | Asks again |
| 4 | Order | `222` | Processing — Ships in 24 Hours |
| 5 | Order | `999` | Graceful error — order not found |
| 6 | Returns | `I received a damaged item and want to return it` | Full return policy |
| 7 | Shipping | `what are your shipping options` | Shipping info |
| 8 | Rec | `I need some outdoor gear suggestions` | Asks for activity |
| 9 | Rec | `swimming` | ❌ Invalid — validation + re-prompt |
| 10 | Rec | `asdfgh` | ❌ Invalid — validation + re-prompt |
| 11 | Rec | `Camping` | ✅ Accepted — asks for weather |
| 12 | Rec | `Cold` | 4-Season Tent + Sleeping Bag + Insulated Jacket |
| 13 | Live | `I need to speak to a human agent` | Handoff message — enters LIVE_AGENT |
| 14 | Live | `Hello, I have a question about my order` | Live agent holding message |
| 15 | Live | `Can you check order 333 for me please` | Live agent holding message |
| 16 | Live | `exit` | Exits live agent — Welcome back |
| 17 | Live | `Talk to an agent` | Handoff message again |
| 18 | Live | `menu` | Exits live agent — Welcome back |
| 19 | Live | `I need to talk to someone` | Handoff message again |
| 20 | Live | `main menu` | Exits live agent — Welcome back |
| 21 | Fallback | `fhdjksahfkjhsdf qwerty blah` | Graceful fallback message |
| 22 | Fallback | `return policy` | Recovers — full return policy |

---

# 🚨 IF SOMETHING GOES WRONG MID-RECORDING

| Problem | Immediate Fix |
|---------|--------------|
| Recommendations show fallback message | Click **🔄 New Conversation** in sidebar, redo Scene 3 |
| Live agent exits immediately on first message | Click **🔄 New Conversation**, request agent again |
| Activity validation not working | Click **🔄 New Conversation**, redo from Step 3.1 |
| Streamlit shows a red error banner | Stop terminal (`Ctrl+C`), run `streamlit run app.py` again, refresh browser |
| Wrong response for any input | Just say *"let me retry that"* and click **🔄 New Conversation** — you can cut in editing |

---

> 📌 **Tip:** Record the entire session in one take if possible.
> If you make a mistake, say *"let me restart that section"*,
> click **🔄 New Conversation**, and redo the scene.
> You can trim it in post-production.
>
> 📌 **Tip:** Use the Cheat Sheet table (above) as your moment-to-moment reference
> so you never need to look at the full script while recording.
