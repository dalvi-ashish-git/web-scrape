import streamlit as st
import time, sys, os

_here = os.path.dirname(os.path.abspath(__file__))
_app  = os.path.dirname(_here)
_root = os.path.dirname(_app)
for _p in (_root, _app):
    if _p not in sys.path:
        sys.path.insert(0, _p)

st.set_page_config(
    page_title="Chat — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.layout import setup_page
from utils.icons  import icon
from llm.groq_client import call_llm_api

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


def _llm_response(user_msg: str, history: list) -> str:
    messages = [{"role": "system", "content": _SYSTEM}]
    for m in history[-40:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})
    try:
        reply = call_llm_api(prompt=messages, temperature=0.45, max_tokens=1024)
        return reply or "I couldn't generate a response. Please try again."
    except Exception as e:
        err = str(e)
        if "GROQ_API_KEY" in err or "not configured" in err.lower():
            return ("Groq API key not found.\n\n"
                    "Add to `.env`:\n```\nGROQ_API_KEY=gsk_...\n```\n"
                    "Get a free key at [console.groq.com](https://console.groq.com).")
        return f"LLM error: {err}"


def _init():
    st.session_state.setdefault("chat_sessions", [])
    st.session_state.setdefault("active_sid", None)
    st.session_state.setdefault("chat_messages", {})


def _new_session():
    sid = f"s_{int(time.time()*1000)}"
    st.session_state.chat_sessions.insert(0, {
        "id": sid, "title": "New Chat", "ts": time.strftime("%b %d, %H:%M")
    })
    st.session_state.chat_messages[sid] = []
    st.session_state.active_sid = sid


_init()
t, main = setup_page("Chat")

if not st.session_state.chat_sessions:
    _new_session()
ids = [s["id"] for s in st.session_state.chat_sessions]
if st.session_state.active_sid not in ids:
    st.session_state.active_sid = st.session_state.chat_sessions[0]["id"]

sid      = st.session_state.active_sid
messages = st.session_state.chat_messages.get(sid, [])

with main:

    # Page header
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
      <div class="PS" style="margin:0;">Powered by Groq · LLaMA 3.3 70B</div>
    </div>
  </div>
</div>
<div style="padding:0 1.4rem;">
  <div style="height:1px;background:{t['border']};margin-bottom:0.75rem;"></div>
</div>
""", unsafe_allow_html=True)

    # Two columns: sessions left (compact), chat right
    left_col, right_col = st.columns([1, 3], gap="medium")

    # LEFT — Session panel — compact height, not 78vh
    with left_col:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem;overflow-y:auto;max-height:75vh;">
  <div style="font-size:0.7rem;font-weight:700;color:{t['muted']};
       text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;
       padding-bottom:0.4rem;border-bottom:1px solid {t['border']};">
    {icon('clock', 10, t['muted'])}&nbsp; Sessions
  </div>
""", unsafe_allow_html=True)

        if st.button("New Chat", key="new_chat_btn", use_container_width=True):
            _new_session()
            st.rerun()

        st.markdown("<div style='margin-top:0.4rem;'>", unsafe_allow_html=True)

        for sess in st.session_state.chat_sessions:
            is_active = sess["id"] == sid
            msgs      = st.session_state.chat_messages.get(sess["id"], [])
            preview   = next((m["content"][:28] + "…" for m in msgs if m["role"] == "user"), "")
            accent_border = f"border-left:3px solid {t['accent']};" if is_active else ""
            bg            = t.get("card_hover", t["bg2"]) if is_active else "transparent"

            st.markdown(f"""
<div style="background:{bg};{accent_border}border-radius:8px;
     padding:0.5rem 0.65rem;margin-bottom:0.25rem;">
  <div style="font-size:0.75rem;font-weight:{'700' if is_active else '500'};
       color:{t['accent'] if is_active else t['text']};
       white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sess['title']}</div>
  <div style="font-size:0.65rem;color:{t['muted']};margin-top:2px;">{sess['ts']}</div>
  {f'<div style="font-size:0.64rem;color:{t["text2"]};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{preview}</div>' if preview else ''}
</div>
""", unsafe_allow_html=True)

            if not is_active:
                if st.button("Open", key=f"open_{sess['id']}", use_container_width=True):
                    st.session_state.active_sid = sess["id"]
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # RIGHT — Chat area with proper visible input
    with right_col:
        # Chat window — reasonable height
        chat_container = st.container(height=460, border=False)

        with chat_container:
            if not messages:
                st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
     padding:3rem 1rem;text-align:center;min-height:360px;
     background:{t['card']};border:1px solid {t['border']};border-radius:14px;">
  <div style="width:58px;height:58px;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:14px;display:flex;align-items:center;justify-content:center;
       margin-bottom:1rem;box-shadow:0 8px 24px {t['accent_glow']};">
    {icon('sparkles', 26, '#fff')}
  </div>
  <div style="font-size:1.1rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">
    How can I help you today?
  </div>
  <div style="font-size:0.84rem;color:{t['text2']};max-width:400px;line-height:1.65;margin-bottom:1.2rem;">
    Ask me about scraping strategies, data analysis, scheduling, or debugging.
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;">
    {''.join(f'<span style="background:{t["bg2"]};border:1px solid {t["border"]};'
             f'border-radius:20px;padding:5px 14px;font-size:0.76rem;'
             f'color:{t["text2"]};">{h}</span>'
             for h in ["How do I scrape a site?", "Fix 0 items extracted",
                       "Schedule a daily job", "What selectors work for Amazon?"])}
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                for msg in messages:
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.markdown(msg["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(msg["content"])

        # Chat input — always visible, styled container for visibility
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:12px;
     padding:0.4rem 0.5rem;margin-top:0.5rem;">
""", unsafe_allow_html=True)
        user_input = st.chat_input(
            "Ask anything about scraping, data, or automation…",
            key=f"chat_input_{sid}",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if user_input:
            for s in st.session_state.chat_sessions:
                if s["id"] == sid and s["title"] == "New Chat":
                    s["title"] = user_input[:28] + ("…" if len(user_input) > 28 else "")
                    break

            st.session_state.chat_messages[sid].append({"role": "user", "content": user_input})
            history_for_llm = st.session_state.chat_messages[sid][:-1]

            with st.spinner("Thinking…"):
                ai_reply = _llm_response(user_input, history_for_llm)

            st.session_state.chat_messages[sid].append({"role": "assistant", "content": ai_reply})
            st.rerun()