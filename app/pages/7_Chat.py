import streamlit as st, time, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="Chat — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon

# ── Session state init ────────────────────────────────────────────────────────
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}

def new_session():
    sid = f"session_{int(time.time()*1000)}"
    ts  = time.strftime("%b %d, %H:%M")
    st.session_state.chat_sessions.insert(0, {"id": sid, "title": "New Chat", "ts": ts})
    st.session_state.chat_messages[sid] = []
    st.session_state.active_session_id  = sid

def get_ai_response(msg: str, history: list) -> str:
    msg_lower = msg.lower()
    if any(w in msg_lower for w in ["scrape","extract","crawl"]):
        return ("I can help you design a scraping strategy! To get started, tell me:\n\n"
                "1. **Target URL** — which site do you want to scrape?\n"
                "2. **Data type** — products, articles, job listings?\n"
                "3. **Frequency** — one-time or scheduled?\n\n"
                "I'll suggest the best scraper config and selectors for you.")
    if any(w in msg_lower for w in ["csv","json","excel","export","download"]):
        return ("WebScraper Pro supports **CSV**, **JSON**, and **Excel** exports.\n\n"
                "After a scrape completes, head to the **Dashboard → Export Data** panel. "
                "You can also schedule automated exports via the **Scheduler** page.")
    if any(w in msg_lower for w in ["schedule","cron","automat"]):
        return ("The **Scheduler** page lets you automate any scraper. You can set:\n\n"
                "- Frequency: Hourly, Every 6h, Daily, Weekly, Monthly\n"
                "- Start date & time\n"
                "- Export format\n"
                "- Email notifications on completion\n\n"
                "Navigate to **Scheduler** in the sidebar to create your first job!")
    if any(w in msg_lower for w in ["hello","hi","hey","howdy"]):
        return ("Hello! 👋 I'm your WebScraper Pro AI assistant.\n\n"
                "I can help you with scraping strategies, data analysis, "
                "export options, and scheduler setup. What would you like to do today?")
    if any(w in msg_lower for w in ["analys","chart","data","insight"]):
        return ("For data analysis, upload your file on the **Dashboard** page. "
                "You'll get:\n\n"
                "- **Table View** — paginated data preview\n"
                "- **Charts** — bar & line charts with custom axes\n"
                "- **AI Analysis** — auto-generated insights summary\n\n"
                "The AI Analysis tab gives you a downloadable .txt report too!")
    responses = [
        ("Great question! Here's what I'd suggest:\n\n"
         "Use the **Dashboard** to start a scrape and monitor progress. "
         "Once complete, your results will appear in **History** for download."),
        ("I'm analyzing your request... Based on the context, the best approach would be "
         "to start with a targeted scrape on the Dashboard, then refine your selectors "
         "in the Dashboard quick-start panel."),
        ("Noted! WebScraper Pro handles anti-bot measures via rotating proxies and "
         "Playwright stealth mode. If you're hitting rate limits, try switching to "
         "the **Slow & Steady** preset in your scraper settings."),
        ("Here's a tip: for e-commerce sites, always include a **Max Rows** limit "
         "to avoid runaway jobs. You can set this in both the Dashboard quick-start "
         "and the Scheduler page."),
    ]
    return random.choice(responses)

t, main = setup_page("Chat")

with main:
    PAD = "padding:0 1.4rem"

    # Page header
    st.markdown(f"""
<div style="{PAD} 0.4rem;padding-top:1rem;margin-bottom:0.7rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:36px;height:36px;background:linear-gradient(135deg,{t['accent']},{t['purple']});
         border-radius:10px;display:flex;align-items:center;justify-content:center;">
      {icon('bot',18,'#fff')}
    </div>
    <div>
      <div class="PT">AI Chat Assistant</div>
      <div class="PS">Ask questions about scraping, data, and automation.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 0;">', unsafe_allow_html=True)

    # Ensure there's at least one session
    if not st.session_state.chat_sessions:
        new_session()

    # Ensure active session is valid
    if (st.session_state.active_session_id is None or
            st.session_state.active_session_id not in
            [s["id"] for s in st.session_state.chat_sessions]):
        if st.session_state.chat_sessions:
            st.session_state.active_session_id = st.session_state.chat_sessions[0]["id"]

    # ── Two-column layout: history drawer | chat area ─────────────────────────
    drawer_col, chat_col = st.columns([1, 3])

    # ── LEFT DRAWER — session history ─────────────────────────────────────────
    with drawer_col:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:0.8rem;min-height:70vh;">
  <div style="display:flex;align-items:center;justify-content:space-between;
       margin-bottom:0.7rem;padding-bottom:0.5rem;border-bottom:1px solid {t['border']};">
    <span style="font-size:0.78rem;font-weight:700;color:{t['text']};
          text-transform:uppercase;letter-spacing:0.06em;">
      {icon('clock',11,t['muted'])}&nbsp; Sessions
    </span>
  </div>
""", unsafe_allow_html=True)

        if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
            new_session()
            st.rerun()

        st.markdown(f'<div style="margin-top:0.5rem;">', unsafe_allow_html=True)
        for sess in st.session_state.chat_sessions:
            is_active = sess["id"] == st.session_state.active_session_id
            msgs = st.session_state.chat_messages.get(sess["id"], [])
            preview = ""
            for m in msgs:
                if m["role"] == "user":
                    preview = m["content"][:32] + ("…" if len(m["content"]) > 32 else "")
                    break

            border_style = f"border:1.5px solid {t['accent']};" if is_active else f"border:1px solid {t['border']};"
            bg_style = f"background:{t['card_hover']};" if is_active else "background:transparent;"

            st.markdown(f"""
<div style="{bg_style}{border_style}border-radius:10px;padding:0.55rem 0.7rem;
     margin-bottom:0.3rem;cursor:pointer;">
  <div style="font-size:0.75rem;font-weight:600;color:{''+t['accent'] if is_active else t['text']};
       white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sess['title']}</div>
  <div style="font-size:0.67rem;color:{t['muted']};margin-top:1px;">{sess['ts']}</div>
  {f'<div style="font-size:0.65rem;color:{t["text2"]};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{preview}</div>' if preview else ''}
</div>
""", unsafe_allow_html=True)
            if st.button(f"Load", key=f"load_{sess['id']}", use_container_width=True):
                st.session_state.active_session_id = sess["id"]
                st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

    # ── RIGHT: CHAT AREA ──────────────────────────────────────────────────────
    with chat_col:
        sid = st.session_state.active_session_id
        messages = st.session_state.chat_messages.get(sid, [])

        # Chat window
        st.markdown(f"""
<div id="chat-window" style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:1rem;min-height:55vh;max-height:60vh;overflow-y:auto;
     display:flex;flex-direction:column;gap:0.6rem;margin-bottom:0.6rem;">
""", unsafe_allow_html=True)

        if not messages:
            st.markdown(f"""
<div style="flex:1;display:flex;flex-direction:column;align-items:center;
     justify-content:center;padding:3rem 1rem;text-align:center;">
  <div style="width:52px;height:52px;background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:14px;display:flex;align-items:center;justify-content:center;
       margin-bottom:0.8rem;">{icon('sparkles',24,'#fff')}</div>
  <div style="font-size:1rem;font-weight:700;color:{t['text']};margin-bottom:0.3rem;">
    How can I help you today?</div>
  <div style="font-size:0.82rem;color:{t['text2']};max-width:340px;">
    Ask me about scraping strategies, data analysis, scheduling, or exports.</div>
  <div style="display:flex;gap:0.5rem;flex-wrap:wrap;justify-content:center;margin-top:1rem;">
    {''.join(f'''<span style="background:{t['bg2']};border:1px solid {t['border']};border-radius:20px;
      padding:4px 12px;font-size:0.73rem;color:{t['text2']};">{hint}</span>'''
      for hint in ["How do I scrape a site?", "Schedule a daily job", "Analyze my CSV"])}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            for msg in messages:
                if msg["role"] == "user":
                    st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin-bottom:0.4rem;">
  <div style="background:{t['accent']};color:#fff;border-radius:14px 14px 4px 14px;
       padding:0.6rem 0.9rem;max-width:72%;font-size:0.84rem;line-height:1.55;">
    {msg['content']}
  </div>
</div>
""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.4rem;">
  <div style="width:28px;height:28px;flex-shrink:0;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:8px;display:flex;align-items:center;justify-content:center;">
    {icon('bot',13,'#fff')}
  </div>
  <div style="background:{t['bg2']};border:1px solid {t['border']};
       border-radius:4px 14px 14px 14px;padding:0.6rem 0.9rem;
       max-width:72%;font-size:0.84rem;line-height:1.6;color:{t['text']};">
    {msg['content'].replace(chr(10), '<br>')}
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # File uploader + input row
        up_col, _ = st.columns([1, 3])
        with up_col:
            uploaded = st.file_uploader("Attach file", type=["png","jpg","jpeg","pdf","csv","txt"],
                                        key=f"chat_upload_{sid}", label_visibility="collapsed")
            if uploaded:
                st.markdown(f"""
<div style="background:{t['bg2']};border:1px solid {t['border']};border-radius:8px;
     padding:0.35rem 0.65rem;font-size:0.72rem;color:{t['text2']};margin-bottom:0.3rem;">
  {icon('file-text',11,t['accent'])}&nbsp; {uploaded.name} ({uploaded.size//1024}KB)
</div>
""", unsafe_allow_html=True)

        user_input = st.chat_input("Ask anything about scraping, data, or automation…",
                                   key=f"chat_input_{sid}")

        if user_input:
            # Update session title from first user message
            sess_list = st.session_state.chat_sessions
            for s in sess_list:
                if s["id"] == sid and s["title"] == "New Chat":
                    s["title"] = user_input[:28] + ("…" if len(user_input) > 28 else "")
                    break

            # Append user message
            st.session_state.chat_messages[sid].append({"role": "user", "content": user_input})

            # Simulate streaming response
            ai_response = get_ai_response(user_input, messages)
            displayed = ""
            response_placeholder = st.empty()
            for char in ai_response:
                displayed += char
                response_placeholder.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:0.5rem;">
  <div style="width:28px;height:28px;flex-shrink:0;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:8px;display:flex;align-items:center;justify-content:center;">
    {icon('bot',13,'#fff')}
  </div>
  <div style="background:{t['bg2']};border:1px solid {t['border']};
       border-radius:4px 14px 14px 14px;padding:0.6rem 0.9rem;
       max-width:72%;font-size:0.84rem;line-height:1.6;color:{t['text']};">
    {displayed.replace(chr(10), '<br>')}▌
  </div>
</div>
""", unsafe_allow_html=True)
                time.sleep(0.008)

            response_placeholder.empty()
            st.session_state.chat_messages[sid].append({"role": "assistant", "content": ai_response})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
