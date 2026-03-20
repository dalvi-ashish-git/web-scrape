import streamlit as st, sys, os, random
from datetime import datetime, date, time as dtime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="Scheduler — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon

# ── Session state init ────────────────────────────────────────────────────────
if "schedules" not in st.session_state:
    st.session_state.schedules = []

SCRAPERS = ["Custom Scraper"]

FREQ_OPTIONS    = ["Hourly", "Every 6h", "Daily", "Weekly", "Monthly"]
FORMAT_OPTIONS  = ["CSV", "JSON", "Excel"]
# STATUS_COLORS and SCRAPER_COLORS are built after t is available (see below)

FREQ_DAYS = {"Hourly": list(range(7)), "Every 6h": list(range(7)),
             "Daily": list(range(7)), "Weekly": [0], "Monthly": [0]}

t, main = setup_page("Scheduler")

# Theme-aware status and scraper colors (defined after t is available)
STATUS_COLORS = {
    "Active":    (t["accent_glow"],              t["green"]),
    "Paused":    (t["accent_glow"],              t["accent"]),
    "Completed": ("rgba(59,130,246,0.14)",        t["blue"]),
}
SCRAPER_COLORS = {
    "Custom Scraper": t["cyan"],
}

with main:
    PAD = "padding:0 1.4rem"

    # Page header
    st.markdown(f"""
<div style="{PAD} 0.4rem;padding-top:1rem;margin-bottom:0.8rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:36px;height:36px;
         background:linear-gradient(135deg,{t['blue']},{t['purple']});
         border-radius:10px;display:flex;align-items:center;justify-content:center;">
      {icon('calendar',18,'#fff')}
    </div>
    <div>
      <div class="PT">Automated Scheduler</div>
      <div class="PS">Set up recurring scrape jobs with custom frequencies and exports.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 0;">', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION A — Create Schedule
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="C" style="margin-bottom:0.8rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.8rem;display:flex;align-items:center;gap:7px;">
    {icon('plus',14,t['accent'])} Create New Schedule
  </div>
""", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        scraper_name = st.selectbox("Scraper Name", SCRAPERS, key="sch_scraper")
    with r1c2:
        url_input = st.text_input("Target URL", placeholder="https://example.com/page", key="sch_url")

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        frequency = st.selectbox("Frequency", FREQ_OPTIONS, key="sch_freq")
    with r2c2:
        start_time = st.time_input("Start Time", value=dtime(9, 0), key="sch_time")
    with r2c3:
        start_date = st.date_input("Start Date", value=date.today(), key="sch_date")

    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        exp_format = st.selectbox("Export Format", FORMAT_OPTIONS, key="sch_format")
    with r3c2:
        max_rows = st.number_input("Max Rows", min_value=10, max_value=10000,
                                   value=500, step=50, key="sch_rows")
    with r3c3:
        email_notify = st.toggle("Email Notification", value=False, key="sch_email")

    st.markdown('</div>', unsafe_allow_html=True)

    # Schedule button (wrapped in PB for accent CTA styling)
    st.markdown('<div class="PB">', unsafe_allow_html=True)
    do_schedule = st.button("🗓  Schedule Scraper", key="btn_schedule", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    if do_schedule:
        if not url_input:
            st.error("Please enter a target URL.")
        else:
            new_id = f"sch_{int(datetime.now().timestamp()*1000)}"
            hr = start_time.strftime("%H:%M")
            dt = start_date.strftime("%Y-%m-%d")
            st.session_state.schedules.insert(0, {
                "id": new_id, "scraper": scraper_name, "url": url_input,
                "frequency": frequency, "start_time": hr, "start_date": dt,
                "format": exp_format, "max_rows": int(max_rows),
                "email_notify": email_notify, "status": "Active",
                "next_run": f"{dt} {hr}",
            })
            st.success(f"✅ Scheduled **{scraper_name}** — {frequency} starting {dt} at {hr}")
            st.rerun()

    st.markdown(f'<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Summary stats
    # ─────────────────────────────────────────────────────────────────────────
    scheds = st.session_state.schedules
    total    = len(scheds)
    active   = sum(1 for s in scheds if s["status"] == "Active")
    paused   = sum(1 for s in scheds if s["status"] == "Paused")
    next_run = next((s["next_run"] for s in scheds if s["status"] == "Active"), "—")

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: st.metric("Total Scheduled", total)
    with mc2: st.metric("Active", active)
    with mc3: st.metric("Paused", paused)
    with mc4: st.metric("Next Run", next_run)

    st.markdown(f'<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION B — Active Schedules Table
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="C">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.8rem;display:flex;align-items:center;gap:7px;">
    {icon('list-checks',14,t['accent'])} Active Schedules
  </div>
""", unsafe_allow_html=True)

    if not scheds:
        st.markdown(f'<div style="color:{t["muted"]};font-size:0.85rem;padding:1rem 0;">No schedules yet. Create one above.</div>',
                    unsafe_allow_html=True)
    else:
        # Table header
        th_style = (f"text-align:left;padding:0.45rem 0.7rem;font-size:0.67rem;"
                    f"font-weight:600;color:{t['muted']};text-transform:uppercase;"
                    f"letter-spacing:0.06em;border-bottom:1px solid {t['border']};")
        headers = ["Scraper", "URL", "Frequency", "Next Run", "Format", "Status", "Actions"]
        th_html = "".join(f'<th style="{th_style}">{h}</th>' for h in headers)

        rows_html = ""
        td = (f"padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};"
              f"font-size:0.8rem;color:{t['text']};vertical-align:middle;")

        for s in scheds:
            sbg, sfg = STATUS_COLORS.get(s["status"], ("transparent", t["text2"]))
            scol = SCRAPER_COLORS.get(s["scraper"], t["accent"])
            rows_html += f"""
<tr>
  <td style="{td}">
    <span style="display:inline-flex;align-items:center;gap:5px;">
      <span style="width:8px;height:8px;border-radius:50%;background:{scol};flex-shrink:0;"></span>
      <span style="font-weight:600;">{s['scraper']}</span>
    </span>
  </td>
  <td style="{td};font-family:monospace;font-size:0.72rem;color:{t['text2']};
       max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
    {s['url']}
  </td>
  <td style="{td}">{s['frequency']}</td>
  <td style="{td};color:{t['text2']};">{s['next_run']}</td>
  <td style="{td}">
    <span style="background:rgba(59,130,246,0.14);color:{t['blue']};padding:2px 7px;
          border-radius:20px;font-size:0.67rem;font-weight:600;">{s['format']}</span>
  </td>
  <td style="{td}">
    <span style="background:{sbg};color:{sfg};padding:2px 8px;border-radius:20px;
          font-size:0.67rem;font-weight:600;">{s['status']}</span>
  </td>
  <td style="{td}">—</td>
</tr>"""

        st.markdown(f"""
<div style="overflow-x:auto;">
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>{th_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Per-row action buttons
    for idx, s in enumerate(scheds):
        ac1, ac2, ac3, _ = st.columns([1, 1, 1, 4])
        with ac1:
            if s["status"] == "Active":
                if st.button("⏸ Pause", key=f"pause_{s['id']}", use_container_width=True):
                    st.session_state.schedules[idx]["status"] = "Paused"
                    st.session_state.schedules[idx]["next_run"] = "—"
                    st.rerun()
            else:
                if st.button("▶ Resume", key=f"resume_{s['id']}", use_container_width=True):
                    st.session_state.schedules[idx]["status"] = "Active"
                    st.rerun()
        with ac2:
            if st.button("🗑 Delete", key=f"del_{s['id']}", use_container_width=True):
                st.session_state.schedules.pop(idx)
                st.rerun()

    st.markdown(f'<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION C — 7-day Calendar View
    # ─────────────────────────────────────────────────────────────────────────
    today = date.today()
    days  = [today + timedelta(days=i) for i in range(7)]
    day_names = [d.strftime("%a %#d") for d in days]

    # Build calendar cells
    cells_html = ""
    for i, (d, dname) in enumerate(zip(days, day_names)):
        is_today = (d == today)
        hdr_bg   = t["accent"] if is_today else t["bg2"]
        hdr_col  = "#fff" if is_today else t["text2"]
        cell_jobs = []
        for s in scheds:
            if s["status"] == "Active":
                freq = s["frequency"]
                if freq in ("Hourly", "Every 6h", "Daily"):
                    cell_jobs.append(s)
                elif freq == "Weekly" and d.weekday() == 0:
                    cell_jobs.append(s)
                elif freq == "Monthly" and d.day == 1:
                    cell_jobs.append(s)

        jobs_html = ""
        for j in cell_jobs[:3]:  # max 3 per cell
            col = SCRAPER_COLORS.get(j["scraper"], t["accent"])
            jobs_html += f"""
<div style="background:{col}22;border-left:3px solid {col};border-radius:4px;
     padding:2px 5px;font-size:0.62rem;font-weight:600;color:{col};
     white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px;">
  {j['scraper'][:18]}
</div>"""
        if len(cell_jobs) > 3:
            jobs_html += f'<div style="font-size:0.6rem;color:{t["muted"]};margin-top:2px;">+{len(cell_jobs)-3} more</div>'

        cells_html += f"""
<div style="flex:1;min-width:0;background:{t['card']};border:1px solid {t['border']};
     border-radius:10px;overflow:hidden;">
  <div style="background:{hdr_bg};color:{hdr_col};padding:0.35rem 0.5rem;
       font-size:0.7rem;font-weight:700;text-align:center;border-bottom:1px solid {t['border']};">
    {dname}
  </div>
  <div style="padding:0.4rem;min-height:80px;">
    {jobs_html if jobs_html else f'<div style="font-size:0.65rem;color:{t["border_l"]};text-align:center;padding-top:0.5rem;">—</div>'}
  </div>
</div>"""

    # Legend
    legend_html = ""
    seen = set()
    for s in scheds:
        if s["scraper"] not in seen and s["status"] == "Active":
            col = SCRAPER_COLORS.get(s["scraper"], t["accent"])
            legend_html += f"""<span style="display:inline-flex;align-items:center;gap:4px;
              margin-right:0.6rem;font-size:0.7rem;color:{t['text2']};">
              <span style="width:9px;height:9px;border-radius:2px;background:{col};flex-shrink:0;"></span>
              {s['scraper']}</span>"""
            seen.add(s["scraper"])

    st.markdown(f"""
<div class="C">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.7rem;display:flex;align-items:center;gap:7px;">
    {icon('calendar',14,t['accent'])} 7-Day Schedule Calendar
  </div>
  <div style="display:flex;gap:0.4rem;margin-bottom:0.6rem;overflow-x:auto;">
    {cells_html}
  </div>
  <div style="margin-top:0.4rem;padding-top:0.4rem;border-top:1px solid {t['border']};">
    <span style="font-size:0.67rem;color:{t['muted']};margin-right:0.6rem;font-weight:600;
          text-transform:uppercase;letter-spacing:0.05em;">Legend:</span>
    {legend_html if legend_html else f'<span style="font-size:0.7rem;color:{t["muted"]};">No active scrapers</span>'}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
