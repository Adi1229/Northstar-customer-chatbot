"""
app.py
------
NorthStar AI Customer Support Chatbot — Streamlit UI entry point.

This is the ONLY file that imports Streamlit.
All business logic is delegated to the ConversationManager.

Architecture boundary (ARCHITECTURE.md):
  UI → ConversationManager → NLP → Services → Repository → SQLite
"""

import logging

import streamlit as st

import config
from chatbot.conversation import ConversationManager
from nlp.embeddings import EmbeddingModel
from nlp.intent_classifier import IntentClassifier
from services.handoff_service import HandoffService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService
from services.return_service import ReturnService

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config  (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NorthStar AI Support",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium dark theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary:    #0f1117;
    --bg-secondary:  #1a1d27;
    --bg-card:       #1e2130;
    --accent-blue:   #4f8ef7;
    --accent-teal:   #38d9a9;
    --accent-orange: #fd7e14;
    --text-primary:  #e8eaf0;
    --text-muted:    #8892a4;
    --border:        #2d3148;
    --bubble-user:   #1e3a5f;
    --bubble-bot:    #1e2130;
    --radius:        14px;
    --shadow:        0 4px 24px rgba(0,0,0,0.4);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 780px; }

/* ── Chat message bubbles ── */
.chat-bubble {
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; } }

.bubble-content {
    max-width: 82%;
    padding: 14px 18px;
    border-radius: var(--radius);
    line-height: 1.6;
    font-size: 0.93rem;
    box-shadow: var(--shadow);
}
.bubble-user .bubble-content {
    background: var(--bubble-user);
    border: 1px solid #2d4d7a;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.bubble-bot .bubble-content {
    background: var(--bubble-bot);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
}

/* Avatar */
.avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.avatar-user { background: linear-gradient(135deg, #3b5bdb, #4f8ef7); }
.avatar-bot  { background: linear-gradient(135deg, #0d9488, #38d9a9); }

/* ── Intent badge ── */
.intent-badge {
    display: inline-block;
    font-size: 0.68rem;
    padding: 2px 8px;
    border-radius: 20px;
    background: rgba(79,142,247,0.12);
    color: var(--accent-blue);
    border: 1px solid rgba(79,142,247,0.25);
    margin-top: 6px;
    letter-spacing: 0.03em;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Input box ── */
.stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s;
}
.stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.15) !important;
}

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, var(--accent-blue), #3b7de8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79,142,247,0.35) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollable chat area ── */
.chat-container {
    max-height: 62vh;
    overflow-y: auto;
    padding: 8px 4px;
    margin-bottom: 12px;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
}
.chat-container::-webkit-scrollbar { width: 4px; }
.chat-container::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading NorthStar AI model… (first run only)")
def _build_conversation_manager() -> ConversationManager:
    """
    Build and cache the ConversationManager for the Streamlit session.

    ``@st.cache_resource`` ensures the NLP model and database adapter
    are loaded once per server process — not on every user interaction.
    """
    logger.info("app: initialising ConversationManager.")
    embedding_model = EmbeddingModel()
    classifier = IntentClassifier(embedding_model=embedding_model)

    cm = ConversationManager(
        classifier=classifier,
        order_service=OrderService(),
        return_service=ReturnService(),
        recommendation_service=RecommendationService(),
        handoff_service=HandoffService(),
    )
    logger.info("app: ConversationManager ready.")
    return cm


def _init_session() -> None:
    """Initialise Streamlit session_state keys on first load."""
    if "messages" not in st.session_state:
        st.session_state.messages = []          # list[dict(role, content, intent)]
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0          # force input clear after send
    if "manager_reset" not in st.session_state:
        st.session_state.manager_reset = False
    if "conversation_mode" not in st.session_state:
        # Persists LIVE_AGENT state across @st.cache_resource cache resets
        # (hot-reload clears the cache but st.session_state survives).
        st.session_state.conversation_mode = "NORMAL"


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

_INTENT_LABELS: dict[str, str] = {
    "greeting":               "👋 greeting",
    "track_order":            "📦 order tracking",
    "return_policy":          "🔄 return policy",
    "shipping_info":          "🚚 shipping info",
    "product_recommendation": "🛒 recommendation",
    "human_handoff":          "🎧 live agent",
    "goodbye":                "👋 goodbye",
    "fallback":               "❓ fallback",
}


def _render_bubble(role: str, content: str, intent: str = "") -> None:
    """Render a single chat bubble with avatar and optional intent badge."""
    if role == "user":
        avatar_class = "avatar-user"
        bubble_class = "bubble-user"
        avatar_icon = "👤"
        align = "flex-direction: row-reverse;"
    else:
        avatar_class = "avatar-bot"
        bubble_class = "bubble-bot"
        avatar_icon = "🏔️"
        align = ""

    badge_html = ""
    if role == "bot" and intent and intent in _INTENT_LABELS:
        badge_html = f'<div class="intent-badge">{_INTENT_LABELS[intent]}</div>'

    # Render markdown inside the bubble via an intermediate approach
    # (Streamlit doesn't support markdown in raw HTML, so we use columns)
    with st.container():
        cols = st.columns([1, 12]) if role == "bot" else st.columns([12, 1])
        avatar_col = cols[0] if role == "bot" else cols[1]
        content_col = cols[1] if role == "bot" else cols[0]

        with avatar_col:
            st.markdown(
                f'<div class="avatar {avatar_class}" style="margin-top:6px">{avatar_icon}</div>',
                unsafe_allow_html=True,
            )
        with content_col:
            with st.container():
                st.markdown(content)
                if badge_html:
                    st.markdown(badge_html, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)


def _send_message(manager: ConversationManager, user_text: str) -> None:
    """Process user input, update session state, and rerun."""
    if not user_text.strip():
        return

    st.session_state.messages.append({
        "role": "user",
        "content": user_text,
        "intent": "",
    })

    response = manager.handle_message(user_text)

    # Persist conversation_mode so it survives a @st.cache_resource cache miss.
    st.session_state.conversation_mode = manager.conversation_mode

    st.session_state.messages.append({
        "role": "bot",
        "content": response.message,
        "intent": response.intent,
    })

    # Increment key to clear the text input widget.
    st.session_state.input_key += 1


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _render_sidebar(manager: ConversationManager) -> None:
    with st.sidebar:
        st.markdown("## 🏔️ NorthStar Support")
        st.markdown("*AI-powered customer assistance*")
        st.markdown("---")

        st.markdown("### What I can help with")
        st.markdown("""
- 📦 **Order tracking** — ask for your order number
- 🔄 **Returns & exchanges** — learn our policy
- 🚚 **Shipping** — delivery options & timelines
- 🛒 **Product recommendations** — find the right gear
- 🎧 **Live agent** — connect with a human
""")
        st.markdown("---")

        st.markdown("### Demo Orders")
        st.markdown("""
| Order | Status |
|---|---|
| `111` | Shipped |
| `222` | Processing |
| `333` | Delivered |
""")
        st.markdown("---")

        if st.button("🔄 New Conversation", use_container_width=True):
            manager.reset_session()
            st.session_state.messages = []
            st.session_state.input_key += 1
            st.session_state.conversation_mode = "NORMAL"
            st.rerun()

        st.markdown("---")
        st.markdown(
            '<p style="color:#8892a4;font-size:0.75rem;text-align:center">'
            'NorthStar AI Support v1.0<br>Powered by MiniLM · Runs offline'
            '</p>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _init_session()
    manager = _build_conversation_manager()

    # Rehydrate conversation_mode from session_state.
    # @st.cache_resource is cleared on hot-reload; st.session_state is not.
    # Restoring here ensures LIVE_AGENT mode survives a cache miss.
    manager.conversation_mode = st.session_state.get("conversation_mode", "NORMAL")

    # Handle manager reset triggered by sidebar button
    if st.session_state.get("manager_reset"):
        manager.reset_session()
        st.session_state.manager_reset = False
        st.session_state.conversation_mode = "NORMAL"

    _render_sidebar(manager)

    # ── Header ──
    st.markdown(
        '<h1 style="font-size:1.6rem;font-weight:700;margin-bottom:0">'
        '🏔️ NorthStar Customer Support</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#8892a4;margin-top:2px;margin-bottom:20px;font-size:0.88rem">'
        'AI-powered support · Fully offline · Ask me anything</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Auto-greeting on first load ──
    if not st.session_state.messages:
        first_response = manager.handle_message("Hello")
        st.session_state.messages.append({
            "role": "bot",
            "content": first_response.message,
            "intent": first_response.intent,
        })

    # ── Chat history ──
    for msg in st.session_state.messages:
        _render_bubble(
            role=msg["role"],
            content=msg["content"],
            intent=msg.get("intent", ""),
        )

    st.markdown("---")

    # ── Input row ──
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            label="Message",
            placeholder="Type your message here…",
            key=f"chat_input_{st.session_state.input_key}",
            label_visibility="collapsed",
        )
    with col_btn:
        send_clicked = st.button("Send ➤", use_container_width=True)

    # Process on button click or Enter
    if send_clicked and user_input:
        _send_message(manager, user_input)
        st.rerun()


if __name__ == "__main__":
    main()
