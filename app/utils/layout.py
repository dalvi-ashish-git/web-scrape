"""
WebScraper Pro - Minimal layout utility.
Each page calls setup_page() to get the theme + inject CSS,
then renders its own two-column layout manually with st.columns([1,5]).
"""
import streamlit as st
from utils.styles import apply_theme, theme_selector
from utils.icons import icon

NAV_ITEMS = [
    ("layout-dashboard", "Dashboard",   "pages/1_Dashboard.py"),
    ("flask-conical",    "Data Studio", "pages/4_Data_Studio.py"),
    ("clock",            "History",     "pages/6_History.py"),
    ("bot",              "Chat",        "pages/7_Chat.py"),
    ("calendar",         "Scheduler",   "pages/8_Scheduler.py"),
    ("settings",         "Settings",    "pages/5_Settings.py"),
]


def setup_page(active: str):
    """
    Auth guard + inject CSS + render two-column layout.
    Returns (t, main_col).
    """
    t = apply_theme()

    if not st.session_state.get("logged_in"):
        st.switch_page("pages/0_Sign_In.py")

    # ── Full CSS reset + layout styles ───────────────────────────────────────
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ display:none!important; }}
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stSidebarNav"], .stDeployButton {{ display:none!important; }}

/* ── Root reset ── */
html, body, .stApp {{
    background:{t['bg']}!important;
    font-family:'DM Sans',sans-serif!important;
    color:{t['text']}!important;
    margin:0!important; padding:0!important;
}}
.block-container {{
    padding:0!important;
    max-width:100%!important;
    margin:0!important;
}}
[data-testid="stAppViewContainer"] > .main {{
    padding:0!important;
    background:{t['bg']}!important;
}}

/* ── Tighten Streamlit's inner wrappers WITHOUT nuking everything ── */
[data-testid="stVerticalBlock"] > div {{
    gap:0!important;
}}
[data-testid="stVerticalBlockBorderWrapper"] {{
    padding:0!important;
    margin:0!important;
}}
/* Only zero out .element-container margin when it's a direct child of column */
[data-testid="stColumn"] > div > .element-container {{
    margin-bottom:0!important;
    padding:0!important;
}}
/* Streamlit stMarkdown inside column — remove its default 1rem bottom margin */
[data-testid="stColumn"] .stMarkdown {{
    margin:0!important;
}}
/* Columns themselves: no gap, stretch height */
[data-testid="stHorizontalBlock"] {{
    gap:0!important;
    align-items:stretch!important;
}}
[data-testid="stColumn"] {{
    padding:0!important;
}}

/* ── Nav sidebar column (always the FIRST top-level column) ── */
[data-testid="stAppViewContainer"] > .main
  [data-testid="stHorizontalBlock"]:first-child
  > [data-testid="stColumn"]:first-child {{
    background:{t['sidebar_bg']}!important;
    border-right:1px solid {t['border']}!important;
    min-height:100vh!important;
    position:sticky!important;
    top:0!important;
    height:100vh!important;
    overflow-y:auto!important;
}}

/* ── File uploader: hide the legal "Terms of Service" text ── */
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzone"] p,
.uploadedFile,
section[data-testid="stFileUploadDropzone"] > div > p:last-child,
[data-testid="stFileUploadDropzone"] ~ div p {{
    display:none!important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background:{t['input_bg']}!important;
    border:1.5px dashed {t['border_l']}!important;
    border-radius:12px!important;
    padding:1rem!important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color:{t['accent']}!important;
    background:{t['card']}!important;
}}
/* Hide the checkbox in file uploader */
[data-testid="stFileUploadDropzone"] input[type="checkbox"],
[data-testid="stFileUploadDropzone"] label {{
    display:none!important;
}}

/* ── Buttons: default (neutral card style) ── */
.stButton > button {{
    background:{t['card']}!important;
    color:{t['text']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    font-family:'DM Sans',sans-serif!important;
    font-weight:600!important;
    font-size:0.85rem!important;
    padding:0.45rem 1rem!important;
    width:100%!important;
    transition:background 0.15s,border-color 0.15s!important;
    box-shadow:none!important;
    transform:none!important;
    filter:none!important;
}}
.stButton > button:hover {{
    background:{t['card_hover']}!important;
    border-color:{t['border_l']}!important;
    box-shadow:none!important;
    transform:none!important;
    filter:none!important;
}}

/* ── Primary CTA: wrap in <div class="PB"> ── */
div.PB .stButton > button {{
    background:{t['accent']}!important;
    color:#fff!important;
    border-color:{t['accent']}!important;
}}
div.PB .stButton > button:hover {{
    filter:brightness(1.08)!important;
    transform:translateY(-1px)!important;
    box-shadow:0 4px 14px {t['accent_glow']}!important;
}}

/* ── NAV: inactive ── */
div.NIB .stButton > button {{
    background:transparent!important;
    color:{t['text2']}!important;
    border:1px solid transparent!important;
    border-radius:9px!important;
    font-weight:500!important;
    font-size:0.86rem!important;
    padding:0.5rem 0.85rem!important;
    text-align:left!important;
    justify-content:flex-start!important;
    box-shadow:none!important; transform:none!important; filter:none!important;
}}
div.NIB .stButton > button:hover {{
    background:{t['card']}!important;
    color:{t['text']}!important;
    border-color:{t['border']}!important;
    box-shadow:none!important; transform:none!important; filter:none!important;
}}

/* ── NAV: active ── */
div.NAB .stButton > button {{
    background:{t['card']}!important;
    color:{t['accent']}!important;
    border:1.5px solid {t['accent']}!important;
    border-radius:9px!important;
    font-weight:700!important;
    font-size:0.86rem!important;
    padding:0.5rem 0.85rem!important;
    text-align:left!important;
    justify-content:flex-start!important;
    box-shadow:0 0 8px {t['accent_glow']}!important;
    transform:none!important; filter:none!important;
}}
div.NAB .stButton > button:hover {{
    background:{t['card']}!important;
    color:{t['accent']}!important;
    border-color:{t['accent']}!important;
    box-shadow:0 0 12px {t['accent_glow']}!important;
    transform:none!important; filter:none!important;
}}

/* ── Sign Out ── */
div.SOB .stButton > button {{
    background:transparent!important;
    color:{t['red']}!important;
    border:1px solid rgba(239,68,68,0.3)!important;
    border-radius:9px!important;
    font-size:0.82rem!important;
    font-weight:500!important;
    padding:0.42rem 0.85rem!important;
    box-shadow:none!important; transform:none!important; filter:none!important;
}}
div.SOB .stButton > button:hover {{
    background:rgba(239,68,68,0.07)!important;
    border-color:{t['red']}!important;
    box-shadow:none!important; transform:none!important; filter:none!important;
}}

/* ── Download buttons ── */
.stDownloadButton > button {{
    background:{t['card']}!important;
    color:{t['text']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    font-weight:500!important;
    font-size:0.83rem!important;
    box-shadow:none!important; filter:none!important; transform:none!important;
}}
.stDownloadButton > button:hover {{
    background:{t['card_hover']}!important;
    border-color:{t['border_l']}!important;
    box-shadow:none!important; filter:none!important; transform:none!important;
}}

/* ── Inputs ── */
[data-testid="stTextInput"] > div > div > input {{
    background:{t['input_bg']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    color:{t['text']}!important;
    font-family:'DM Sans',sans-serif!important;
    font-size:0.88rem!important;
    padding:0.52rem 0.75rem!important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color:{t['accent']}!important;
    box-shadow:0 0 0 3px {t['accent_glow']}!important;
}}
[data-testid="stTextInput"] > div > div > input::placeholder {{
    color:{t['muted']}!important;
}}
.stSelectbox > div > div {{
    background:{t['input_bg']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    color:{t['text']}!important;
    font-size:0.88rem!important;
}}
/* Selectbox dropdown list */
[data-baseweb="popover"] ul {{
    background:{t['card']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
}}
[data-baseweb="popover"] li {{
    background:{t['card']}!important;
    color:{t['text']}!important;
}}
[data-baseweb="popover"] li:hover {{
    background:{t['card_hover']}!important;
}}

/* ── Number input ── */
[data-testid="stNumberInput"] input {{
    background:{t['input_bg']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    color:{t['text']}!important;
}}

/* ── Toggle ── */
[data-testid="stToggle"] label {{ color:{t['text2']}!important; }}

/* ── Time / Date input ── */
[data-testid="stTimeInput"] input,
[data-testid="stDateInput"] input {{
    background:{t['input_bg']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    color:{t['text']}!important;
    font-family:'DM Sans',sans-serif!important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background:{t['card']}!important;
    border:1px solid {t['border']}!important;
    border-radius:14px!important;
    padding:0.85rem 1.1rem!important;
}}
[data-testid="metric-container"] label {{
    color:{t['text2']}!important;
    font-size:0.72rem!important;
    font-weight:600!important;
    text-transform:uppercase!important;
    letter-spacing:0.06em!important;
    margin-bottom:0.15rem!important;
}}
[data-testid="stMetricValue"] {{
    color:{t['text']}!important;
    font-weight:700!important;
    font-size:1.65rem!important;
    line-height:1.2!important;
}}
[data-testid="stMetricDelta"] {{ color:{t['green']}!important; font-size:0.75rem!important; }}

/* ── Progress ── */
.stProgress > div > div > div > div {{
    background:linear-gradient(90deg,{t['blue']},{t['accent']})!important;
    border-radius:99px!important;
}}
.stProgress > div > div > div {{
    background:{t['border']}!important;
    border-radius:99px!important;
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background:{t['card']}!important;
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    color:{t['text']}!important;
}}
.streamlit-expanderContent {{
    background:{t['card']}!important;
    border:1px solid {t['border']}!important;
    border-top:none!important;
}}
.stCheckbox label, .stRadio label {{ color:{t['text2']}!important; font-size:0.86rem!important; }}
hr {{ border-color:{t['border']}!important; margin:0.5rem 0!important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:4px; height:4px; }}
::-webkit-scrollbar-track {{ background:{t['bg']}; }}
::-webkit-scrollbar-thumb {{ background:{t['border_l']}; border-radius:10px; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background:transparent!important;
    border-bottom:1px solid {t['border']}!important;
    gap:0!important;
    padding:0!important;
}}
.stTabs [data-baseweb="tab"] {{
    background:transparent!important;
    color:{t['text2']}!important;
    font-family:'DM Sans',sans-serif!important;
    font-size:0.86rem!important;
    font-weight:500!important;
    padding:0.45rem 1rem!important;
    border:none!important;
}}
.stTabs [aria-selected="true"] {{
    color:{t['accent']}!important;
    border-bottom:2px solid {t['accent']}!important;
    background:transparent!important;
    font-weight:600!important;
}}
/* Tab content panel */
.stTabs [data-baseweb="tab-panel"] {{
    padding:0.75rem 0 0!important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border:1px solid {t['border']}!important;
    border-radius:10px!important;
    overflow:hidden!important;
}}

/* ── Alert / info / success / error ── */
[data-testid="stAlert"] {{
    background:{t['card']}!important;
    border-radius:10px!important;
    border-left:3px solid {t['blue']}!important;
    color:{t['text']}!important;
    padding:0.6rem 0.9rem!important;
    margin:0.4rem 0!important;
}}

/* ── Spinner ── */
[data-testid="stSpinner"] {{ color:{t['accent']}!important; }}

/* ── Shared utility classes ── */
.C {{
    background:{t['card']};
    border:1px solid {t['border']};
    border-radius:14px;
    padding:1.1rem 1.2rem;
    margin-bottom:0.6rem;
}}
.PT {{
    font-size:1.45rem;
    font-weight:800;
    letter-spacing:-0.04em;
    color:{t['text']};
    margin:0 0 0.1rem;
    line-height:1.2;
}}
.PS {{
    color:{t['text2']};
    font-size:0.84rem;
    margin:0 0 0.7rem;
    line-height:1.5;
}}
.BG {{
    display:inline-flex;
    align-items:center;
    gap:4px;
    padding:3px 9px;
    border-radius:20px;
    font-size:0.7rem;
    font-weight:600;
    line-height:1.4;
}}
.G  {{ background:rgba(16,185,129,0.14); color:{t['green']}; }}
.R  {{ background:rgba(239,68,68,0.14);  color:{t['red']}; }}
.A  {{ background:{t['accent_glow']}; color:{t['accent']}; }}
.B  {{ background:rgba(59,130,246,0.14); color:{t['blue']}; }}
.P  {{ background:rgba(139,92,246,0.14); color:{t['purple']}; }}
.CB {{
    background:{t['input_bg']};
    border:1px solid {t['border']};
    border-radius:10px;
    padding:0.75rem;
    font-family:'JetBrains Mono',monospace;
    font-size:0.74rem;
    color:{t['text2']};
    min-height:70px;
    max-height:140px;
    overflow-y:auto;
    line-height:1.7;
}}
</style>
""", unsafe_allow_html=True)

    # ── Layout: nav | main ────────────────────────────────────────────────────
    nav_col, main_col = st.columns([1, 5], gap="small")

    with nav_col:
        # Brand
        st.markdown(f"""
<div style="padding:1rem 0.85rem 0.75rem;border-bottom:1px solid {t['border']};">
  <div style="display:flex;align-items:center;gap:9px;">
    <div style="width:30px;height:30px;flex-shrink:0;
         background:linear-gradient(135deg,{t['accent']},{t['accent_h']});
         border-radius:8px;display:flex;align-items:center;justify-content:center;">
      {icon('globe',16,'#fff')}
    </div>
    <span style="font-weight:700;font-size:0.9rem;color:{t['text']};white-space:nowrap;">WebScraper Pro</span>
  </div>
</div>
<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;
     letter-spacing:0.1em;color:{t['muted']};padding:0.6rem 0.85rem 0.2rem;">
  Main Menu
</div>
""", unsafe_allow_html=True)

        # Nav buttons — each wrapped in NIB/NAB with minimal padding
        for ic_name, label, page_path in NAV_ITEMS:
            cls = "NAB" if label == active else "NIB"
            st.markdown(f'<div class="{cls}" style="padding:1px 0.45rem 0;">', unsafe_allow_html=True)
            if st.button(label, key=f"nb_{label}_{active}", use_container_width=True):
                st.switch_page(page_path)
            st.markdown("</div>", unsafe_allow_html=True)

        # Theme selector
        st.markdown('<div style="padding:0.4rem 0.45rem 0;">', unsafe_allow_html=True)
        theme_selector(f"ts_{active}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Spacer that pushes user card to bottom
        st.markdown(f'<div style="flex:1;min-height:1.5rem;"></div>', unsafe_allow_html=True)

        # User card
        email   = st.session_state.get("user_email", "user@example.com")
        name    = st.session_state.get("user_name", "")
        display = name if name else email
        st.markdown(f"""
<div style="padding:0.6rem 0.85rem 0.3rem;border-top:1px solid {t['border']};margin-top:0.5rem;">
  <div style="background:{t['card']};border:1px solid {t['border']};border-radius:10px;padding:0.6rem;">
    <div style="font-size:0.63rem;color:{t['muted']};margin-bottom:2px;display:flex;align-items:center;gap:4px;">
      {icon('user',10,t['muted'])} Logged in as
    </div>
    <div style="font-size:0.78rem;font-weight:600;color:{t['text']};
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:150px;">{display}</div>
    <div style="margin-top:4px;"><span class="BG G">{icon('check-circle',8,t['green'])} Pro Plan</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Sign Out
        st.markdown('<div class="SOB" style="padding:0 0.45rem 0.8rem;">', unsafe_allow_html=True)
        if st.button("Sign Out", key=f"so_{active}", use_container_width=True):
            for k in ("logged_in", "user_email", "user_name"):
                st.session_state[k] = "" if k != "logged_in" else False
            st.switch_page("pages/0_Sign_In.py")
        st.markdown("</div>", unsafe_allow_html=True)

    return t, main_col
