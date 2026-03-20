import streamlit as st, pandas as pd, sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="History — WebScraper Pro", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="History")
    return buf.getvalue()

t, main = setup_page("History")
PAD = "padding:0 1.4rem"

with main:
    st.markdown(f'<div style="{PAD} 0.4rem;padding-top:1rem;"><div class="PT">{icon("clock",17,t["accent"])} History</div><div class="PS">Complete record of all your past scraping activity.</div></div>', unsafe_allow_html=True)

    history = st.session_state.get("history", [])

    total_jobs   = len(history)
    total_rows   = sum(int(r[5]) for r in history if r[5].isdigit())
    success_rate = f"{(sum(1 for r in history if r[6]=='Completed') / total_jobs * 100):.1f}%" if total_jobs else "—"

    st.markdown(f"""
<div style="{PAD} 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.75rem;margin-bottom:0.65rem;">
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;padding:1rem 1.2rem;border-top:3px solid {t['blue']};">
      <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">Total Jobs</div>
      <div style="font-size:1.75rem;font-weight:700;color:{t['text']};">{total_jobs}</div>
    </div>
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;padding:1rem 1.2rem;border-top:3px solid {t['green']};">
      <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">Rows Scraped</div>
      <div style="font-size:1.75rem;font-weight:700;color:{t['text']};">{total_rows:,}</div>
    </div>
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;padding:1rem 1.2rem;border-top:3px solid {t['accent']};">
      <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">Avg. Duration</div>
      <div style="font-size:1.75rem;font-weight:700;color:{t['text']};">—</div>
    </div>
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;padding:1rem 1.2rem;border-top:3px solid {t['purple']};">
      <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">Success Rate</div>
      <div style="font-size:1.75rem;font-weight:700;color:{t['text']};">{success_rate}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 0;">', unsafe_allow_html=True)
    f1,f2,f3,f4 = st.columns([2.5,1.2,1.2,1])
    with f1: search=st.text_input("S","",placeholder="Search by URL or scraper...",label_visibility="collapsed")
    with f2: sf=st.selectbox("St",["All Status","Completed","Failed","Running"],label_visibility="collapsed")
    with f3: pf=st.selectbox("P",["All Time","Today","This Week","This Month"],label_visibility="collapsed")
    with f4:
        if st.button("Refresh",use_container_width=True): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = history
    if sf != "All Status": filtered = [r for r in filtered if r[6]==sf]
    if search: s=search.lower(); filtered=[r for r in filtered if s in r[1].lower() or s in r[2].lower()]

    bm={"Completed":("rgba(16,185,129,0.14)",t['green'],icon('check-circle',9,t['green'])),
        "Failed":("rgba(239,68,68,0.14)",t['red'],icon('x-circle',9,t['red'])),
        "Running":(t['accent_glow'],t['accent'],icon('loader',9,t['accent'])),}
    th="".join(f'<th style="text-align:left;padding:0.5rem 0.8rem;font-size:0.67rem;font-weight:600;color:{t["muted"]};text-transform:uppercase;letter-spacing:0.06em;border-bottom:1px solid {t["border"]};">{h}</th>' for h in ["Job ID","Scraper","URL","Date","Duration","Rows","Status","Actions"])
    rows=""
    for jid,sc,url_r,date,dur,rn,stat in filtered:
        bg,fg,ich=bm.get(stat,(t['card'],t['text2'],""))
        act=""
        if stat=="Completed": act=f'<span style="background:{t["card"]};border:1px solid {t["border"]};color:{t["text2"]};padding:2px 6px;border-radius:6px;font-size:0.67rem;">{icon("download",9,t["text2"])} Export</span>'
        elif stat=="Failed": act=f'<span style="background:{t["card"]};border:1px solid {t["border"]};color:{t["red"]};padding:2px 6px;border-radius:6px;font-size:0.67rem;">{icon("refresh-cw",9,t["red"])} Retry</span>'
        rows+=f'<tr><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};font-family:monospace;font-size:0.7rem;color:{t["text"]};">{jid}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};color:{t["text"]};font-weight:500;">{sc}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};font-family:monospace;font-size:0.69rem;color:{t["text2"]};">{url_r}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};color:{t["text2"]};font-size:0.79rem;">{date}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};color:{t["text2"]};font-size:0.79rem;">{dur}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};color:{t["text"]};font-weight:600;">{rn}</td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};"><span style="background:{bg};color:{fg};padding:2px 6px;border-radius:20px;font-size:0.67rem;font-weight:600;display:inline-flex;align-items:center;gap:2px;">{ich} {stat}</span></td><td style="padding:0.62rem 0.8rem;border-bottom:1px solid {t["border"]};">{act}</td></tr>'
    empty=f'<tr><td colspan="8" style="text-align:center;padding:2.5rem;color:{t["muted"]};font-size:0.83rem;">No history yet. Your scraping jobs will appear here.</td></tr>' if not filtered else ""

    st.markdown(f"""
<div style="{PAD} 1.2rem;margin-top:0.4rem;">
  <div class="C" style="overflow-x:auto;">
    <div style="display:flex;align-items:center;gap:6px;font-size:0.9rem;font-weight:700;color:{t['text']};margin-bottom:0.7rem;">
      {icon('clock',13,t['accent'])} Scraping History
      <span style="font-size:0.67rem;font-weight:400;color:{t['muted']};margin-left:3px;">({len(filtered)} records)</span>
    </div>
    <table style="width:100%;border-collapse:collapse;"><thead><tr>{th}</tr></thead><tbody>{rows}{empty}</tbody></table>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 0;">', unsafe_allow_html=True)
    ec1,ec2,ec3,_ = st.columns([1,1,1,2])
    df = pd.DataFrame(filtered, columns=["Job ID","Scraper","URL","Date","Duration","Rows","Status"]) if filtered else pd.DataFrame(columns=["Job ID","Scraper","URL","Date","Duration","Rows","Status"])
    with ec1:
        st.download_button("Export CSV", df.to_csv(index=False),
                           "history.csv","text/csv", use_container_width=True)
    with ec2:
        st.download_button("Export JSON", df.to_json(orient="records"),
                           "history.json","application/json", use_container_width=True)
    with ec3:
        st.download_button("Export Excel", to_excel(df),
                           "history.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
