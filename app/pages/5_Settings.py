import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="Settings — WebScraper Pro", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon

t, main = setup_page("Settings")
PAD = "padding:0 1.4rem"

with main:
    st.markdown(f'<div style="{PAD} 0.4rem;padding-top:1rem;"><div class="PT">{icon("settings",17,t["accent"])} Settings</div><div class="PS">Manage your account preferences and configurations.</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 1.2rem;">', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["Profile","Appearance","Scraping","Notifications","Billing"])

    with tab1:
        ue=st.session_state.get("user_email","user@example.com")
        un=st.session_state.get("user_name","")
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
  <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,{t['accent']},{t['blue']});display:flex;align-items:center;justify-content:center;">{icon('user',23,'#fff')}</div>
  <div>
    <div style="font-weight:700;font-size:0.95rem;color:{t['text']};">{un or ue}</div>
    <div style="font-size:0.72rem;color:{t['muted']};">Member since January 2026</div>
    <div style="margin-top:3px;"><span class="BG G">{icon('check-circle',8,t['green'])} Pro Plan</span></div>
  </div>
</div>
""", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1: st.text_input("Full Name",value=un or "John Developer"); st.text_input("Email",value=ue)
        with c2: st.text_input("Organization",placeholder="Your company"); st.selectbox("Timezone",["Asia/Kolkata (IST +5:30)","UTC","America/New_York"])
        _,sc2=st.columns([4,1])
        with sc2:
            if st.button("Save Profile",use_container_width=True): st.success("Saved!")
        st.markdown("---")
        dc1,dc2=st.columns(2)
        with dc1:
            if st.button("Change Password",use_container_width=True): st.info("Reset email sent!")
        with dc2:
            if st.button("Delete Account",use_container_width=True): st.error("Contact support.")

    with tab2:
        st.markdown(f'<div style="font-size:0.9rem;font-weight:700;color:{t["text"]};margin-bottom:0.9rem;">Choose Theme</div>',unsafe_allow_html=True)
        tc=st.columns(3)
        opts=[("dark","Dark","#0a0e1a",icon('moon',13,'#8899bb')),("light","Light","#f0f4f8",icon('sun',13,'#e8920a')),("vivid","Vivid","#0d0a1e",icon('sparkles',13,'#a78bfa'))]
        for i,(val,label,bgc,ich) in enumerate(opts):
            with tc[i]:
                ia=st.session_state.get("theme","dark")==val; bdr=t['accent'] if ia else t['border']
                st.markdown(f'<div style="border:2px solid {bdr};border-radius:10px;overflow:hidden;"><div style="background:{bgc};height:44px;display:flex;align-items:center;justify-content:center;">{ich}</div><div style="background:{t["card"]};padding:0.35rem;text-align:center;font-size:0.74rem;font-weight:600;color:{t["text"]};">{label}</div></div>',unsafe_allow_html=True)
                if st.button(f"Select {label}",key=f"th_{val}",use_container_width=True):
                    st.session_state.theme=val; st.rerun()
        st.markdown("---")
        co1,co2=st.columns(2)
        with co1: st.toggle("Compact Mode",value=False); st.toggle("Animations",value=True)
        with co2: st.toggle("Live Console",value=True); st.toggle("Auto-Export",value=False)
        if st.button("Save Appearance"): st.success("Saved!")

    with tab3:
        c1,c2=st.columns(2)
        with c1:
            st.selectbox("Default Export",["CSV","JSON","Excel"])
            st.number_input("Timeout (s)",min_value=5,max_value=120,value=30)
            st.number_input("Max Retries",min_value=1,max_value=10,value=3)
        with c2:
            st.selectbox("Default Category",["E-commerce","News","Jobs","Custom"])
            st.number_input("Concurrent",min_value=1,max_value=10,value=3)
            st.number_input("Rate Delay (ms)",min_value=0,max_value=5000,value=500)
        st.markdown("---")
        co1,co2=st.columns(2)
        with co1: st.toggle("Proxy Rotation",value=True); st.toggle("JS Rendering",value=True)
        with co2: st.toggle("AI Noise Removal",value=True); st.toggle("Save Raw HTML",value=False)
        if st.button("Save Config"): st.success("Saved!")

    with tab4:
        st.text_input("Notification Email",value=st.session_state.get("user_email",""))
        st.markdown("---")
        for label,desc,default in [("Job Completed","Notify when a job finishes",True),("Job Failed","Alert on errors",True),("API Limit Warning","Warn at 80% usage",True),("Weekly Summary","Digest",False),("Product Updates","New features",False)]:
            r1,r2=st.columns([4,1])
            with r1: st.markdown(f'<div style="font-size:0.84rem;font-weight:600;color:{t["text"]};">{label}</div><div style="font-size:0.71rem;color:{t["muted"]};">{desc}</div>',unsafe_allow_html=True)
            with r2: st.toggle(f"Enable {label}", value=default, key=f"n_{label}", label_visibility="collapsed")
        if st.button("Save Notifications"): st.success("Saved!")

    with tab5:
        st.markdown(f'<div style="background:{t["accent_glow"]};border:1px solid {t["accent"]};border-radius:12px;padding:1rem;margin-bottom:0.9rem;"><div style="display:inline-flex;align-items:center;gap:5px;background:{t["accent"]};color:#fff;padding:2px 7px;border-radius:99px;font-size:0.69rem;font-weight:700;margin-bottom:0.35rem;">{icon("star",10,"#fff")} Pro Plan</div><div style="font-size:1.25rem;font-weight:800;color:{t["text"]};letter-spacing:-0.03em;">Rs. 999 / month</div><div style="font-size:0.77rem;color:{t["text2"]};">Next billing: April 20, 2026</div></div>',unsafe_allow_html=True)
        bc1,bc2=st.columns(2)
        with bc1:
            if st.button("Manage Plan",use_container_width=True): st.info("Redirecting...")
        with bc2:
            if st.button("Cancel Plan",use_container_width=True): st.error("Contact support.")
        st.markdown("---")
        for label,used,total in [("API Calls",8420,10000),("Rows Extracted",2580,50000),("Active Scrapers",4,20)]:
            pct=int(used/total*100)
            u1,u2=st.columns([3,1])
            with u1: st.markdown(f'<div style="font-size:0.78rem;color:{t["text2"]};margin-bottom:2px;">{label}</div>',unsafe_allow_html=True); st.progress(pct)
            with u2: st.markdown(f'<div style="font-size:0.76rem;color:{t["muted"]};text-align:right;padding-top:1.3rem;">{used:,}/{total:,}</div>',unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
