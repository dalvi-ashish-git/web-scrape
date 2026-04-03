import streamlit as st
import time, sys, os, re
from supabase import create_client, Client
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- PATH FIX ----------------
_here = os.path.dirname(os.path.abspath(__file__))
_app  = os.path.dirname(_here)
_root = os.path.dirname(_app)
for _p in (_root, _app):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Chat — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.layout import setup_page
from utils.icons  import icon
from llm.groq_client import call_llm_api

# ---------------- SYSTEM ----------------
_SYSTEM = """You are the AI assistant for WebScraper Pro, an AI-driven web scraping platform.

Your role:
- Help users design scraping strategies (CSS selectors, HTML tags, class names)
- Explain Dashboard features: URL input, query box, export buttons
- Advise on Data Analysis: chart types, column selection, AI Analysis tab
- Explain Scheduler: frequency options (hourly/daily/weekly), export format
- Answer questions about export formats: CSV, JSON, Excel
- Debug scraping issues: 0 items extracted, wrong data, selector problems

Key platform facts:
- Uses Playwright headless browser + Groq LLaMA 3.3 70B for intelligence
- Scraping modes: E-commerce, News, Job Listings, Custom
- Data Analysis Canvas: Table View, Charts (bar/line/area), AI Analysis

Tone: concise, expert, friendly. Use markdown.
"""

_DETAIL_SYSTEM = """You are a knowledgeable AI assistant. When given a highlighted term or phrase from a chat message, provide a detailed, informative explanation about it.

Rules:
- Give a thorough but focused explanation (3-5 paragraphs)
- Include key facts, history, how it works, and why it matters
- Use clear markdown formatting with headers and bullet points
- Be accurate and educational
- If it's a person, include their background, achievements, and current status
- If it's a concept/term, explain it from basics to advanced details
"""

# ---------------- LLM ----------------
def _llm_response(user_msg: str, history: list) -> str:
    messages = [{"role": "system", "content": _SYSTEM}]
    for m in history[-40:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})

    try:
        reply = call_llm_api(prompt=messages, temperature=0.45, max_tokens=1024)
        return reply or "I couldn't generate a response. Please try again."
    except Exception as e:
        return f"LLM error: {str(e)}"


def _detail_response(term: str, context: str) -> str:
    """Get detailed explanation for a clicked highlighted term."""
    prompt = [
        {"role": "system", "content": _DETAIL_SYSTEM},
        {"role": "user", "content": f"Give me a detailed explanation about: **{term}**\n\nContext where it appeared: {context}"}
    ]
    try:
        reply = call_llm_api(prompt=prompt, temperature=0.3, max_tokens=1024)
        return reply or "Could not fetch details. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- SUPABASE FUNCTIONS ----------------
def load_sessions():
    res = supabase.table("chat_sessions").select("*").order("created_at", desc=True).execute()
    return res.data or []

def load_messages(session_id):
    res = supabase.table("chat_messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at") \
        .execute()
    return res.data or []

def create_session():
    sid = f"s_{int(time.time()*1000)}"
    session = {
        "id": sid,
        "title": "New Chat",
        "ts": time.strftime("%b %d, %H:%M")
    }
    supabase.table("chat_sessions").insert(session).execute()
    return session

def save_message(session_id, role, content):
    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def update_title(session_id, title):
    supabase.table("chat_sessions").update({"title": title}).eq("id", session_id).execute()


# ---------------- MARKDOWN → CLICKABLE HTML ----------------
def _extract_bold_terms(text: str) -> list:
    """Extract all **bold** terms from markdown text."""
    return re.findall(r'\*\*(.+?)\*\*', text)


def _markdown_to_clickable_html(text: str, msg_index: int, t: dict) -> str:
    """
    Convert markdown text to HTML where **bold** terms become clickable chips.
    Clicking a term sets session state to show detail popup.
    Uses Streamlit's component_value trick via query params won't work,
    so we use st.session_state keys via button injection pattern.
    Returns HTML string with clickable spans.
    """
    # We'll replace **term** with a styled span that has a data attribute
    def replace_bold(match):
        term = match.group(1)
        safe_term = term.replace('"', '&quot;').replace("'", "&#39;")
        return (
            f'<span class="clickable-term" '
            f'onclick="window.parent.postMessage({{type:\'streamlit:setComponentValue\', '
            f'key:\'clicked_term\', value:\'{safe_term}|||{msg_index}\'}}, \'*\')" '
            f'title="Click for details">'
            f'{term}'
            f'<span class="term-hint">ℹ</span>'
            f'</span>'
        )
    
    # Process line by line to handle markdown
    lines = text.split('\n')
    html_lines = []
    
    for line in lines:
        # Replace **bold** with clickable spans
        processed = re.sub(r'\*\*(.+?)\*\*', replace_bold, line)
        # Handle headers
        if processed.startswith('### '):
            processed = f'<h4 style="margin:0.6rem 0 0.3rem;color:{t["text"]};font-size:0.95rem;">{processed[4:]}</h4>'
        elif processed.startswith('## '):
            processed = f'<h3 style="margin:0.7rem 0 0.3rem;color:{t["text"]};font-size:1.05rem;">{processed[3:]}</h3>'
        elif processed.startswith('# '):
            processed = f'<h2 style="margin:0.8rem 0 0.4rem;color:{t["text"]};font-size:1.15rem;">{processed[2:]}</h2>'
        elif processed.startswith('- ') or processed.startswith('* '):
            processed = f'<li style="margin-left:1rem;margin-bottom:0.2rem;">{processed[2:]}</li>'
        elif processed.strip() == '':
            processed = '<br>'
        else:
            processed = f'<p style="margin:0.2rem 0;">{processed}</p>'
        
        html_lines.append(processed)
    
    return '\n'.join(html_lines)


# ---------------- INIT ----------------
def _init():
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = load_sessions()
    if "active_sid" not in st.session_state:
        st.session_state.active_sid = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = {}
    # Detail popup state
    if "detail_term" not in st.session_state:
        st.session_state.detail_term = None
    if "detail_context" not in st.session_state:
        st.session_state.detail_context = None
    if "detail_content" not in st.session_state:
        st.session_state.detail_content = None
    if "detail_loading" not in st.session_state:
        st.session_state.detail_loading = False
    if "pending_term" not in st.session_state:
        st.session_state.pending_term = None

def _new_session():
    session = create_session()
    st.session_state.chat_sessions.insert(0, session)
    st.session_state.chat_messages[session["id"]] = []
    st.session_state.active_sid = session["id"]

_init()
t, main = setup_page("Chat")

# Ensure at least one session
if not st.session_state.chat_sessions:
    _new_session()

ids = [s["id"] for s in st.session_state.chat_sessions]
if st.session_state.active_sid not in ids:
    st.session_state.active_sid = st.session_state.chat_sessions[0]["id"]

sid = st.session_state.active_sid

# Load messages from DB if not loaded
if sid not in st.session_state.chat_messages:
    db_msgs = load_messages(sid)
    st.session_state.chat_messages[sid] = [
        {"role": m["role"], "content": m["content"]} for m in db_msgs
    ]

messages = st.session_state.chat_messages.get(sid, [])

with main:

    # HEADER
    st.markdown(f"""
<div style="padding:0.9rem 1.4rem 0.6rem;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:40px;height:40px;flex-shrink:0;
         background:linear-gradient(135deg,{t['accent']},{t['purple']});
         border-radius:12px;display:flex;align-items:center;justify-content:center;
         box-shadow:0 4px 16px {t['accent_glow']};">
      {icon('bot', 20, '#fff')}
    </div>
    <div>
      <div class="PT" style="margin:0;">AI Chat Assistant</div>
      <div class="PS" style="margin:0;">Powered by Groq · LLaMA 3.3 70B · <span style="color:{t['accent']};font-size:0.78rem;">✦ Click highlighted words for details</span></div>
    </div>
  </div>
</div>
<div style="padding:0 1.4rem;">
  <div style="height:1px;background:{t['border']};margin-bottom:0.75rem;"></div>
</div>
""", unsafe_allow_html=True)

    # CSS for clickable terms
    st.markdown(f"""
<style>
.clickable-term {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    background: linear-gradient(135deg, {t['accent_glow']}, rgba(139,92,246,0.15));
    color: {t['accent']};
    font-weight: 700;
    padding: 1px 7px 1px 5px;
    border-radius: 6px;
    border: 1px solid {t['accent_glow']};
    cursor: pointer;
    transition: all 0.18s ease;
    font-size: inherit;
    line-height: inherit;
}}
.clickable-term:hover {{
    background: linear-gradient(135deg, rgba(232,146,10,0.3), rgba(139,92,246,0.25));
    border-color: {t['accent']};
    transform: translateY(-1px);
    box-shadow: 0 3px 10px {t['accent_glow']};
}}
.term-hint {{
    font-size: 0.65em;
    opacity: 0.75;
    font-style: normal;
    font-weight: 400;
}}
.detail-popup {{
    background: {t['card']};
    border: 1px solid {t['accent']};
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin: 0.75rem 0;
    box-shadow: 0 8px 32px {t['accent_glow']}, 0 2px 8px rgba(0,0,0,0.3);
    position: relative;
    animation: slideIn 0.2s ease;
}}
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(-8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.detail-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.85rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid {t['border']};
}}
.detail-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {t['accent']};
    margin: 0;
}}
.detail-badge {{
    background: {t['accent_glow']};
    color: {t['accent']};
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.detail-body {{
    color: {t['text']};
    font-size: 0.875rem;
    line-height: 1.65;
}}
.detail-body h2, .detail-body h3, .detail-body h4 {{
    color: {t['text']};
    margin: 0.7rem 0 0.3rem;
}}
.detail-body p {{ margin: 0.3rem 0; }}
.detail-body li {{ margin-left: 1.2rem; margin-bottom: 0.25rem; }}
.detail-body strong {{ color: {t['accent']}; }}
.msg-bubble {{
    padding: 0.6rem 0.85rem;
    border-radius: 12px;
    font-size: 0.875rem;
    line-height: 1.65;
    color: {t['text']};
}}
.msg-bubble.assistant {{
    background: {t['card']};
    border: 1px solid {t['border']};
}}
.msg-bubble.user {{
    background: {t['accent_glow']};
    border: 1px solid rgba(232,146,10,0.2);
    text-align: right;
}}
</style>
""", unsafe_allow_html=True)

    # JavaScript bridge to capture clicks on highlighted terms
    st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'streamlit:setComponentValue') {
        // Store in sessionStorage so Streamlit can pick it up
        sessionStorage.setItem('clicked_term_data', e.data.value);
        // Trigger Streamlit re-run by clicking a hidden button
        const btn = window.parent.document.querySelector('[data-testid="baseButton-secondary"][aria-label="term_trigger"]');
        if (btn) btn.click();
    }
});
</script>
""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 3], gap="medium")

    # ---------------- LEFT ----------------
    with left_col:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem;overflow-y:auto;max-height:75vh;">
""", unsafe_allow_html=True)

        if st.button("New Chat", key="new_chat_btn", use_container_width=True):
            _new_session()
            st.rerun()

        st.markdown("<div style='margin-top:0.4rem;'>", unsafe_allow_html=True)

        for sess in st.session_state.chat_sessions:
            is_active = sess["id"] == sid

            st.markdown(f"""
<div style="padding:0.4rem;margin-bottom:0.3rem;">
  <div style="font-size:0.75rem;">{sess['title']}</div>
</div>
""", unsafe_allow_html=True)

            if not is_active:
                if st.button("Open", key=f"open_{sess['id']}", use_container_width=True):
                    st.session_state.active_sid = sess["id"]
                    st.session_state.detail_term = None
                    st.session_state.detail_content = None
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # ---------------- RIGHT ----------------
    with right_col:

        # ── Detail popup shown ABOVE chat if a term is selected ──
        if st.session_state.detail_term:
            term = st.session_state.detail_term

            st.markdown(f"""
<div class="detail-popup">
  <div class="detail-header">
    <div>
      <div class="detail-title">{term}</div>
    </div>
    <span class="detail-badge">Detailed View</span>
  </div>
  <div class="detail-body">
""", unsafe_allow_html=True)

            if st.session_state.detail_loading:
                st.markdown(f'<p style="color:{t["muted"]}">Loading details...</p>', unsafe_allow_html=True)
            elif st.session_state.detail_content:
                # Render the detail content
                content = st.session_state.detail_content
                # Convert markdown to basic HTML
                content_html = content.replace('\n\n', '<br><br>').replace('\n', '<br>')
                # Bold formatting
                content_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_html)
                # Headers
                content_html = re.sub(r'#{3} (.+?)(<br>|$)', r'<h4>\1</h4>', content_html)
                content_html = re.sub(r'## (.+?)(<br>|$)', r'<h3>\1</h3>', content_html)
                content_html = re.sub(r'# (.+?)(<br>|$)', r'<h2>\1</h2>', content_html)
                st.markdown(f'<div class="detail-body">{content_html}</div>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

            col_close, col_ask = st.columns([1, 2])
            with col_close:
                if st.button("✕ Close", key="close_detail", use_container_width=True):
                    st.session_state.detail_term = None
                    st.session_state.detail_content = None
                    st.rerun()
            with col_ask:
                if st.button(f"Ask more about \"{term[:20]}...\"" if len(term) > 20 else f"Ask more about \"{term}\"",
                             key="ask_more_detail", use_container_width=True):
                    auto_question = f"Tell me more about {term}"
                    # Add as user message
                    for s in st.session_state.chat_sessions:
                        if s["id"] == sid and s["title"] == "New Chat":
                            s["title"] = auto_question[:28]
                            update_title(sid, auto_question[:28])
                    st.session_state.chat_messages[sid].append({"role": "user", "content": auto_question})
                    save_message(sid, "user", auto_question)
                    with st.spinner("Thinking…"):
                        ai_reply = _llm_response(auto_question, messages)
                    st.session_state.chat_messages[sid].append({"role": "assistant", "content": ai_reply})
                    save_message(sid, "assistant", ai_reply)
                    st.session_state.detail_term = None
                    st.session_state.detail_content = None
                    st.rerun()

            st.markdown(f'<div style="height:1px;background:{t["border"]};margin:0.5rem 0;"></div>', unsafe_allow_html=True)

        # ── Chat messages ──
        chat_container = st.container(height=460)

        with chat_container:
            if not messages:
                st.markdown(f"""
<div style="text-align:center;padding:2rem;color:{t['text2']};">
  <div style="font-size:1.5rem;margin-bottom:0.5rem;"></div>
  <div style="font-size:1rem;font-weight:600;color:{t['text']};">How can I help you today?</div>
  <div style="font-size:0.8rem;margin-top:0.3rem;">Ask anything · <span style="color:{t['accent']};">Bold words</span> are clickable for more details</div>
</div>
""", unsafe_allow_html=True)
            else:
                for i, msg in enumerate(messages):
                    if msg["role"] == "user":
                        st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin:0.4rem 0;">
  <div style="max-width:80%;background:{t['accent_glow']};border:1px solid rgba(232,146,10,0.25);
       border-radius:14px 14px 4px 14px;padding:0.6rem 0.9rem;
       color:{t['text']};font-size:0.875rem;line-height:1.6;">
    {msg['content']}
  </div>
</div>
""", unsafe_allow_html=True)
                    else:
                        # Assistant message — make bold terms clickable
                        content = msg["content"]
                        bold_terms = _extract_bold_terms(content)

                        if bold_terms:
                            # Render message with clickable terms using buttons
                            st.markdown(f"""
<div style="display:flex;gap:10px;margin:0.4rem 0;align-items:flex-start;">
  <div style="width:28px;height:28px;flex-shrink:0;margin-top:2px;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.8rem;"></div>
  <div style="flex:1;background:{t['card']};border:1px solid {t['border']};
       border-radius:4px 14px 14px 14px;padding:0.7rem 0.9rem;
       color:{t['text']};font-size:0.875rem;line-height:1.65;">
""", unsafe_allow_html=True)

                            # Use st.markdown for rendering the text
                            st.markdown(content)

                            # Show clickable term buttons below the message
                            st.markdown(f'<div style="margin-top:0.5rem;padding-top:0.4rem;border-top:1px solid {t["border"]};display:flex;flex-wrap:wrap;gap:6px;align-items:center;">'
                                        f'<span style="font-size:0.7rem;color:{t["muted"]};margin-right:4px;">Click for details:</span>', unsafe_allow_html=True)

                            cols = st.columns(min(len(bold_terms), 4))
                            for j, term in enumerate(bold_terms[:8]):  # max 8 chips
                                col_idx = j % min(len(bold_terms), 4)
                                with cols[col_idx]:
                                    btn_key = f"term_{i}_{j}_{term[:10]}"
                                    if st.button(f"{term}", key=btn_key, use_container_width=True):
                                        st.session_state.detail_term = term
                                        st.session_state.detail_context = content[:300]
                                        st.session_state.detail_content = None
                                        # Immediately load detail
                                        with st.spinner(f"Loading details about '{term}'…"):
                                            detail = _detail_response(term, content[:300])
                                        st.session_state.detail_content = detail
                                        st.rerun()

                            st.markdown('</div></div></div>', unsafe_allow_html=True)

                        else:
                            # No bold terms — render normally
                            with st.chat_message("assistant"):
                                st.markdown(content)

        # ── Chat input ──
        user_input = st.chat_input("Ask anything…")

        if user_input:
            # Close any open detail panel
            st.session_state.detail_term = None
            st.session_state.detail_content = None

            # Update title if first message
            for s in st.session_state.chat_sessions:
                if s["id"] == sid and s["title"] == "New Chat":
                    new_title = user_input[:28]
                    s["title"] = new_title
                    update_title(sid, new_title)

            # Save USER
            st.session_state.chat_messages[sid].append({
                "role": "user",
                "content": user_input
            })
            save_message(sid, "user", user_input)

            # AI
            with st.spinner("Thinking…"):
                ai_reply = _llm_response(user_input, messages)

            # Save AI
            st.session_state.chat_messages[sid].append({
                "role": "assistant",
                "content": ai_reply
            })
            save_message(sid, "assistant", ai_reply)

            st.rerun()