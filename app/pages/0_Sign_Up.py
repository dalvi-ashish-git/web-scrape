import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Sign Up — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import apply_theme, theme_selector
from utils.icons import icon

t = apply_theme()

if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Dashboard.py")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{
    padding: 1rem 2rem 2rem !important;
    max-width: 100% !important;
}}

[data-testid="stTextInput"] > div > div > input {{
    background: {t['bg']} !important;
    border: 1.5px solid {t['border_l']} !important;
    border-radius: 10px !important;
    color: {t['text']} !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}
[data-testid="stTextInput"] > label {{
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: {t['text2']} !important;
    margin-bottom: 0.2rem !important;
}}
[data-testid="stTextInput"] > div > div > input::placeholder {{
    color: {t['muted']} !important;
}}

/* SIGN UP button */
.signup-btn > div > button {{
    background: linear-gradient(135deg,{t['accent']},{t['accent_h']}) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-size: 0.95rem !important;
    font-weight: 700 !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; padding: 0.75rem !important;
    box-shadow: 0 4px 20px {t['accent_glow']} !important;
    width: 100% !important; transform: none !important; filter: none !important;
}}
.signup-btn > div > button:hover {{
    box-shadow: 0 6px 28px {t['accent_glow']} !important;
}}

/* SIGN IN outline button */
.signin-outline > div > button {{
    background: transparent !important; color: #fff !important;
    border: 2.5px solid #fff !important; border-radius: 10px !important;
    font-size: 0.9rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 0.65rem !important; box-shadow: none !important;
    width: 100% !important; transform: none !important; filter: none !important;
}}
.signin-outline > div > button:hover {{
    background: rgba(255,255,255,0.18) !important;
}}

.back-btn > div > button {{
    background: {t['bg2']} !important; color: {t['text2']} !important;
    border: 1px solid {t['border']} !important; border-radius: 8px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    box-shadow: none !important; transform: none !important;
}}

.social-row {{
    display:flex; gap:0.65rem; justify-content:center; margin:0.75rem 0;
}}
.soc-icon {{
    width:46px; height:46px; border-radius:50%;
    border:1.5px solid rgba(255,255,255,0.35);
    background:rgba(255,255,255,0.12);
    display:flex; align-items:center; justify-content:center;
    cursor:pointer; transition:all 0.2s; text-decoration:none;
    font-weight:800; font-size:15px;
}}
.soc-icon:hover {{ background:rgba(255,255,255,0.25); transform:translateY(-2px); }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
tb1, _, tb3 = st.columns([1, 7, 1])
with tb1:
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back", key="su_back"):
        st.switch_page("Home.py")
    st.markdown('</div>', unsafe_allow_html=True)
with tb3:
    theme_selector("su_theme")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Two-column layout ──────────────────────────────────────────────────────────
gap, left_col, right_col, gap2 = st.columns([0.5, 1.8, 2.2, 0.5])

# ══════════════════════════════════════════
#  LEFT COL — teal welcome panel + SIGN IN
# ══════════════════════════════════════════
with left_col:
    st.markdown(f"""
    <div style="background:linear-gradient(150deg,#12b8b0 0%,#0c7a90 45%,#0a4f72 100%);
         border-radius:20px;padding:3.5rem 2rem;min-height:400px;
         display:flex;flex-direction:column;align-items:center;
         justify-content:center;text-align:center;
         position:relative;overflow:hidden;">

      <div style="position:absolute;top:-60px;right:-50px;width:230px;height:230px;
           background:rgba(255,255,255,0.07);border-radius:50%;"></div>
      <div style="position:absolute;bottom:-80px;left:-40px;width:260px;height:260px;
           background:rgba(255,255,255,0.04);border-radius:50%;"></div>

      <div style="position:relative;z-index:2;">
        <div style="font-size:1.85rem;font-weight:800;color:#fff;
             margin-bottom:0.9rem;line-height:1.2;">Welcome Back!</div>
        <p style="font-size:0.88rem;color:rgba(255,255,255,0.88);
             line-height:1.7;max-width:220px;margin:0 auto 1.75rem;">
          To keep connected with us please login with your personal info
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    st.markdown('<div class="signin-outline">', unsafe_allow_html=True)
    if st.button("SIGN IN", key="goto_signin", use_container_width=True):
        st.switch_page("pages/0_Sign_In.py")
    st.markdown('</div>', unsafe_allow_html=True)

    # Social icons
    st.markdown(f"""
    <div style="text-align:center;margin-top:1.25rem;">
      <div style="font-size:0.78rem;color:{t['text2']};margin-bottom:0.65rem;">
        Or sign in directly using:
      </div>
      <div class="social-row">
        <a class="soc-icon" title="Google">
          <span style="color:#EA4335;font-family:Georgia,serif;">G</span>
        </a>
        <a class="soc-icon" title="Facebook">
          <span style="color:#fff;font-weight:900;">f</span>
        </a>
        <a class="soc-icon" title="GitHub">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="white">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205
            11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555
            -3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02
            -.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305
            3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925
            0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315
            3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23
            3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225
            0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22
            0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02
            0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>
        <a class="soc-icon" title="LinkedIn">
          <span style="color:#fff;font-size:13px;font-weight:900;">in</span>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  RIGHT COL — dark panel with signup form
# ══════════════════════════════════════════
with right_col:
    # Top shell of the dark card
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:20px 20px 0 0;padding:2rem 2.5rem 1rem;text-align:center;">
      <div style="font-size:1.7rem;font-weight:800;letter-spacing:-0.03em;
           color:{t['text']};margin-bottom:0.2rem;">Create Account</div>
      <div style="font-size:0.82rem;color:{t['muted']};">
        or use your email for registration
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Form fields inside a styled container that blends with the card
    st.markdown(f"""
    <div style="background:{t['card']};border-left:1px solid {t['border']};
         border-right:1px solid {t['border']};padding:0.5rem 1.5rem 0;">
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f'<div style="background:{t["card"]};padding:0 1rem;'
                    f'border-left:1px solid {t["border"]};border-right:1px solid {t["border"]};">',
                    unsafe_allow_html=True)

        name  = st.text_input("Your Name",        placeholder="Your Name",         key="su_name")
        email = st.text_input("Your Email",        placeholder="Your Email",        key="su_email")
        pw    = st.text_input("Password",          placeholder="Password",
                              type="password",     key="su_pw")
        pw2   = st.text_input("Confirm Password",  placeholder="Confirm Password",
                              type="password",     key="su_pw2")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom of card + Sign Up button
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-top:none;border-radius:0 0 20px 20px;
         padding:0.5rem 2.5rem 1.5rem;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="signup-btn">', unsafe_allow_html=True)
    if st.button("SIGN UP", key="signup_btn", use_container_width=True):
        if not all([name, email, pw, pw2]):
            st.error("Please fill in all fields.")
        elif pw != pw2:
            st.error("Passwords do not match.")
        elif len(pw) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            st.session_state["logged_in"]  = True
            st.session_state["user_email"] = email
            st.session_state["user_name"]  = name
            st.success(f"Welcome, {name}! Redirecting...")
            st.switch_page("pages/1_Dashboard.py")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:0.75rem;
         font-size:0.83rem;color:{t['text2']};">
      Already a member?&nbsp;
      <a href="/Sign_In" style="color:{t['accent']};font-weight:600;text-decoration:none;">
        Sign in
      </a>
    </div>
    """, unsafe_allow_html=True)
