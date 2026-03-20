"""
Shared theme and CSS utilities for WebScraper Pro Streamlit app.
"""
import streamlit as st

THEMES = {
    "dark": {
        "bg":          "#0a0e1a",
        "bg2":         "#111827",
        "card":        "#1a2235",
        "card_hover":  "#1e2a40",
        "border":      "#1e2d45",
        "border_l":    "#243350",
        "text":        "#f0f4ff",
        "text2":       "#8899bb",
        "muted":       "#4a5a7a",
        "accent":      "#e8920a",
        "accent_h":    "#f5a020",
        "accent_glow": "rgba(232,146,10,0.25)",
        "blue":        "#3b82f6",
        "green":       "#10b981",
        "red":         "#ef4444",
        "purple":      "#8b5cf6",
        "cyan":        "#06b6d4",
        "input_bg":    "#0d1525",
        "sidebar_bg":  "#0d1525",
    },
    "light": {
        "bg":          "#f0f4f8",
        "bg2":         "#ffffff",
        "card":        "#ffffff",
        "card_hover":  "#f7fafc",
        "border":      "#e2e8f0",
        "border_l":    "#cbd5e0",
        "text":        "#1a202c",
        "text2":       "#4a5568",
        "muted":       "#a0aec0",
        "accent":      "#e8920a",
        "accent_h":    "#d4820a",
        "accent_glow": "rgba(232,146,10,0.15)",
        "blue":        "#3b82f6",
        "green":       "#10b981",
        "red":         "#ef4444",
        "purple":      "#7c3aed",
        "cyan":        "#0891b2",
        "input_bg":    "#f7fafc",
        "sidebar_bg":  "#ffffff",
    },
    "vivid": {
        "bg":          "#0d0a1e",
        "bg2":         "#120f28",
        "card":        "#1a1535",
        "card_hover":  "#211a40",
        "border":      "#2e2560",
        "border_l":    "#3d3275",
        "text":        "#eee8ff",
        "text2":       "#a898cc",
        "muted":       "#6b5e90",
        "accent":      "#a78bfa",
        "accent_h":    "#9370f0",
        "accent_glow": "rgba(167,139,250,0.25)",
        "blue":        "#60a5fa",
        "green":       "#34d399",
        "red":         "#f87171",
        "purple":      "#c084fc",
        "cyan":        "#22d3ee",
        "input_bg":    "#100d24",
        "sidebar_bg":  "#0f0c22",
    },
}

# ── All 6 nav pages ────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("layout-dashboard", "Dashboard",  "pages/1_Dashboard.py"),
    ("layers",           "Scrapers",   "pages/2_Scrapers.py"),
    ("list-checks",      "Tasks",      "pages/3_Tasks.py"),
    ("clock",            "History",    "pages/6_History.py"),
    ("key",              "API Keys",   "pages/4_API_Keys.py"),
    ("settings",         "Settings",   "pages/5_Settings.py"),
]


def get_theme() -> dict:
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    return THEMES[st.session_state.theme]


def theme_selector(key: str = "theme_sel") -> None:
    options = ["Dark", "Light", "Vivid"]
    current_idx = ["dark", "light", "vivid"].index(st.session_state.get("theme", "dark"))
    choice = st.selectbox("Theme", options=options, index=current_idx,
                          label_visibility="collapsed", key=key)
    selected = choice.lower()
    if selected != st.session_state.get("theme"):
        st.session_state.theme = selected
        st.rerun()


def apply_theme(page_title: str = "WebScraper Pro") -> dict:
    t = get_theme()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

#MainMenu {{visibility:hidden;}} footer {{visibility:hidden;}} header {{visibility:hidden;}}
.stDeployButton {{display:none;}}
[data-testid="stSidebarNav"] {{display:none;}}

html, body, .stApp {{
    background-color: {t['bg']} !important;
    font-family: 'DM Sans', sans-serif !important;
    color: {t['text']} !important;
}}
[data-testid="stAppViewContainer"] > .main {{
    background-color: {t['bg']} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {t['sidebar_bg']} !important;
    border-right: 1px solid {t['border']} !important;
    min-width: 220px !important;
    max-width: 220px !important;
}}
[data-testid="stSidebar"] > div {{
    padding: 1rem 0.75rem !important;
}}

/* Sidebar ALL buttons — default style */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {t['text2']} !important;
    border: 1px solid transparent !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    padding: 0.55rem 0.85rem !important;
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    margin-bottom: 2px !important;
    transition: all 0.18s ease !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {t['card']} !important;
    color: {t['text']} !important;
    border-color: {t['border']} !important;
    transform: none !important;
    box-shadow: none !important;
    filter: none !important;
}}

/* Active nav button — injected via .nav-active class */
[data-testid="stSidebar"] .nav-active .stButton > button {{
    background: {t['card']} !important;
    color: {t['accent']} !important;
    border: 1px solid {t['accent']} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .nav-active .stButton > button:hover {{
    background: {t['card']} !important;
    color: {t['accent']} !important;
    border-color: {t['accent']} !important;
}}

/* ── Global buttons ── */
.stButton > button {{
    background: {t['accent']} !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    display: inline-flex !important; align-items: center !important; gap: 6px !important;
}}
.stButton > button:hover {{
    filter: brightness(1.1) !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px {t['accent_glow']} !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {t['input_bg']} !important; border: 1px solid {t['border']} !important;
    border-radius: 10px !important; color: {t['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}
.stSelectbox > div > div {{
    background: {t['input_bg']} !important; border: 1px solid {t['border']} !important;
    border-radius: 10px !important; color: {t['text']} !important;
}}
.stSelectbox svg {{ fill: {t['text2']} !important; }}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {t['card']} !important; border: 1px solid {t['border']} !important;
    border-radius: 14px !important; padding: 1rem 1.25rem !important;
}}
[data-testid="metric-container"] label {{
    color: {t['text2']} !important; font-size: 0.75rem !important;
    font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important;
}}
[data-testid="stMetricValue"] {{ color: {t['text']} !important; font-weight: 700 !important; font-size: 1.8rem !important; }}
[data-testid="stMetricDelta"] {{ color: {t['green']} !important; }}

/* ── Progress ── */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {t['blue']}, {t['accent']}) !important; border-radius: 99px !important;
}}
.stProgress > div > div > div {{ background: {t['border']} !important; border-radius: 99px !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {t['card']} !important; border: 1px solid {t['border']} !important;
    border-radius: 10px !important; color: {t['text']} !important;
}}
.streamlit-expanderContent {{
    background: {t['card']} !important; border: 1px solid {t['border']} !important; border-top: none !important;
}}
.stCheckbox label, .stRadio label {{ color: {t['text2']} !important; font-size: 0.87rem !important; }}
hr {{ border-color: {t['border']} !important; }}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: {t['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {t['border_l']}; border-radius: 10px; }}

/* ── Shared component classes ── */
.wsp-card {{
    background: {t['card']}; border: 1px solid {t['border']};
    border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
    transition: border-color 0.25s ease;
}}
.wsp-page-title {{
    font-size: 1.6rem; font-weight: 800; letter-spacing: -0.04em;
    color: {t['text']}; margin-bottom: 0.2rem;
}}
.wsp-page-sub {{ color: {t['text2']}; font-size: 0.88rem; margin-bottom: 1.5rem; }}
.wsp-badge-green {{
    display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:20px;
    font-size:0.73rem;font-weight:600;background:rgba(16,185,129,0.12);color:{t['green']};
}}
.wsp-badge-red {{
    display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:20px;
    font-size:0.73rem;font-weight:600;background:rgba(239,68,68,0.12);color:{t['red']};
}}
.wsp-badge-amber {{
    display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:20px;
    font-size:0.73rem;font-weight:600;background:{t['accent_glow']};color:{t['accent']};
}}
.wsp-badge-blue {{
    display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:20px;
    font-size:0.73rem;font-weight:600;background:rgba(59,130,246,0.12);color:{t['blue']};
}}
.wsp-badge-purple {{
    display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:20px;
    font-size:0.73rem;font-weight:600;background:rgba(139,92,246,0.12);color:{t['purple']};
}}
.code-block {{
    background: {t['input_bg']}; border: 1px solid {t['border']};
    border-radius: 10px; padding: 1rem; font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; color: {t['text2']}; overflow-x: auto; line-height: 1.7;
}}
.console-box {{
    background: {t['input_bg']}; border: 1px solid {t['border']};
    border-radius: 12px; padding: 1rem; font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; color: {t['text2']}; min-height: 120px; max-height: 200px;
    overflow-y: auto; line-height: 1.7;
}}
.sidebar-header {{
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: {t['muted']}; padding: 0.6rem 0.85rem 0.3rem;
}}
</style>
""", unsafe_allow_html=True)
    return t


def sidebar_nav(active_page: str = "") -> None:
    """
    Renders the sidebar with 6 nav items.
    active_page must match exactly one of the labels in NAV_ITEMS.
    Uses Streamlit buttons so active state is always 100% reliable.
    """
    from utils.icons import icon
    t = get_theme()

    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;
             padding:0.25rem 0.5rem 1rem;
             border-bottom:1px solid {t['border']};margin-bottom:0.75rem;">
          <div style="width:32px;height:32px;
               background:linear-gradient(135deg,{t['accent']},{t['accent_h']});
               border-radius:9px;display:flex;align-items:center;justify-content:center;
               box-shadow:0 0 12px {t['accent_glow']};">
            {icon('globe', 17, '#fff')}
          </div>
          <span style="font-weight:700;font-size:0.95rem;color:{t['text']};">WebScraper Pro</span>
        </div>
        <div class="sidebar-header">Main Menu</div>
        """, unsafe_allow_html=True)

        # ── Nav buttons ────────────────────────────────────────────────────────
        for icon_name, label, page_path in NAV_ITEMS:
            is_active = active_page == label
            ic_color  = t['accent'] if is_active else t['text2']
            ic_svg    = icon(icon_name, 15, ic_color)
            btn_label = f"{ic_svg}&nbsp;&nbsp;{label}"

            # Wrap in .nav-active div when selected so CSS selector fires
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)

            if st.button(
                label,
                key=f"nav__{label}",
                use_container_width=True,
                help=label,
            ):
                st.switch_page(page_path)

            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        # ── Divider ────────────────────────────────────────────────────────────
        st.markdown(f'<div style="border-top:1px solid {t["border"]};margin:0.75rem 0;"></div>',
                    unsafe_allow_html=True)

        # ── Account card ───────────────────────────────────────────────────────
        user_email = st.session_state.get("user_email", "user@example.com")
        user_name  = st.session_state.get("user_name",  "")
        display    = user_name if user_name else user_email

        st.markdown(f"""
        <div style="background:{t['card']};border:1px solid {t['border']};
             border-radius:10px;padding:0.75rem;margin-bottom:0.5rem;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
            {icon('user', 12, t['muted'])}
            <span style="font-size:0.7rem;color:{t['muted']};">Logged in as</span>
          </div>
          <div style="font-size:0.82rem;font-weight:600;color:{t['text']};
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
               max-width:160px;">{display}</div>
          <div style="margin-top:5px;">
            <span class="wsp-badge-green">
              {icon('check-circle',9,t['green'])} Pro Plan
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Sign out button at very bottom
        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            st.session_state["logged_in"]  = False
            st.session_state["user_email"] = ""
            st.session_state["user_name"]  = ""
            st.switch_page("pages/0_Sign_In.py")
