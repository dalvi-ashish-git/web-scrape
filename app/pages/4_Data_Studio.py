import streamlit as st
import pandas as pd
import io, sys, os, time, base64, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Data Studio — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from utils.layout import setup_page
from utils.icons import icon

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Data")
    return buf.getvalue()

def file_to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode()

def df_summary(df: pd.DataFrame) -> str:
    rows, cols = df.shape
    lines = [f"Rows: {rows}  |  Columns: {cols}",
             f"Columns: {', '.join(df.columns.tolist())}", ""]
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            lines.append(f"  {col} [numeric]: min={df[col].min():.2f}, "
                         f"max={df[col].max():.2f}, mean={df[col].mean():.2f}, "
                         f"nulls={df[col].isna().sum()}")
        else:
            top = df[col].value_counts().head(3).index.tolist()
            lines.append(f"  {col} [text]: {df[col].nunique()} unique values, "
                         f"top: {', '.join(str(v) for v in top)}, "
                         f"nulls={df[col].isna().sum()}")
    return "\n".join(lines)

def call_claude(prompt: str, system: str = "") -> str:
    import urllib.request, json as _json
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error: GROQ_API_KEY not found in .env file]"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": "llama-3.3-70b-versatile", "max_tokens": 1500, "messages": messages}
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=_json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq API Error: {e}]"

for key, default in [
    ("ds_files", []),
    ("ds_active_idx", None),
    ("ds_analysis", {}),
    ("ds_chat", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

t, main = setup_page("Data Studio")

st.markdown(f"""
<style>
.ds-pad {{ padding: 1rem 1.4rem; }}
.ds-card {{
    background: {t['card']};
    border: 1px solid {t['border']};
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.65rem;
}}
.ds-section-label {{
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {t['muted']};
    margin-bottom: 0.35rem;
}}
.ds-stat {{
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: {t['text']};
    line-height: 1.1;
}}
.ds-stat-lbl {{
    font-size: 0.67rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['text2']};
    margin-top: 2px;
}}
.analysis-box {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: {t['text2']};
    line-height: 1.85;
    white-space: pre-wrap;
    max-height: 320px;
    overflow-y: auto;
}}
.chat-bubble-user {{
    background: {t['accent']};
    color: #fff;
    border-radius: 14px 14px 4px 14px;
    padding: 0.55rem 0.85rem;
    max-width: 78%;
    font-size: 0.83rem;
    line-height: 1.55;
    margin-left: auto;
}}
.chat-bubble-ai {{
    background: {t['bg2']};
    border: 1px solid {t['border']};
    border-radius: 4px 14px 14px 14px;
    padding: 0.55rem 0.85rem;
    max-width: 78%;
    font-size: 0.83rem;
    line-height: 1.6;
    color: {t['text']};
}}
.empty-drop {{
    border: 2px dashed {t['border_l']};
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    background: {t['bg2']};
}}
</style>
""", unsafe_allow_html=True)

with main:

    st.markdown(f"""
<div class="ds-pad" style="padding-bottom:0.5rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="width:40px;height:40px;flex-shrink:0;
           background:linear-gradient(135deg,{t['accent']},{t['purple']});
           border-radius:12px;display:flex;align-items:center;justify-content:center;
           box-shadow:0 0 18px {t['accent_glow']};">
        {icon('flask-conical',20,'#fff')}
      </div>
      <div>
        <div class="PT">Data Studio</div>
        <div class="PS" style="margin:0;">Upload files &amp; images · AI-powered analysis · Visual canvas</div>
      </div>
    </div>
    <span class="BG G">
      <span style="width:6px;height:6px;border-radius:50%;background:{t['green']};
            display:inline-block;box-shadow:0 0 4px {t['green']};"></span>
      AI Ready
    </span>
  </div>
</div>
<div style="padding:0 1.4rem;">
  <div style="height:1px;background:{t['border']};margin-bottom:0.8rem;"></div>
</div>
""", unsafe_allow_html=True)

    files      = st.session_state.ds_files
    n_files    = len(files)
    n_tables   = sum(1 for f in files if f["type"] == "table")
    n_images   = sum(1 for f in files if f["type"] == "image")
    n_analyzed = len(st.session_state.ds_analysis)

    st.markdown(f'<div class="ds-pad" style="padding-top:0;padding-bottom:0.5rem;">', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4, gap="small")
    for col, val, lbl, clr in [
        (sc1, n_files,    "Files Loaded",   t['accent']),
        (sc2, n_tables,   "Tabular Files",  t['blue']),
        (sc3, n_images,   "Images",         t['purple']),
        (sc4, n_analyzed, "Files Analysed", t['green']),
    ]:
        with col:
            st.markdown(f"""
<div class="ds-card" style="border-top:3px solid {clr};margin-bottom:0;">
  <div class="ds-stat" style="color:{clr};">{val}</div>
  <div class="ds-stat-lbl">{lbl}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ds-pad" style="padding-top:0.4rem;">', unsafe_allow_html=True)
    left_col, right_col = st.columns([1, 2], gap="small")

    with left_col:
        st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.7rem;display:flex;align-items:center;gap:7px;">
    {icon('upload',14,t['accent'])} Upload Files
  </div>
  <div class="ds-section-label">Supported: CSV · JSON · Excel · PNG · JPG · JPEG · PDF</div>
</div>
""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop files here",
            type=["csv", "json", "xlsx", "xls", "png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="ds_uploader",
            label_visibility="collapsed",
        )

        if uploaded:
            existing_names = {f["name"] for f in st.session_state.ds_files}
            added = 0
            for uf in uploaded:
                if uf.name in existing_names:
                    continue
                raw = uf.read()
                ext = uf.name.rsplit(".", 1)[-1].lower()
                record = {"name": uf.name, "ext": ext, "size": uf.size, "df": None,
                          "bytes": raw, "b64": file_to_b64(raw), "type": "other"}
                if ext == "csv":
                    try:
                        record["df"] = pd.read_csv(io.BytesIO(raw))
                        record["type"] = "table"
                    except: pass
                elif ext in ("xlsx", "xls"):
                    try:
                        record["df"] = pd.read_excel(io.BytesIO(raw), engine="openpyxl")
                        record["type"] = "table"
                    except: pass
                elif ext == "json":
                    try:
                        record["df"] = pd.read_json(io.BytesIO(raw))
                        record["type"] = "table"
                    except: pass
                elif ext in ("png", "jpg", "jpeg"):
                    record["type"] = "image"
                elif ext == "pdf":
                    record["type"] = "pdf"
                st.session_state.ds_files.append(record)
                added += 1
            if added:
                st.session_state.ds_active_idx = len(st.session_state.ds_files) - 1
                st.rerun()

        st.markdown(f"""
<div class="ds-card" style="margin-top:0.5rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;justify-content:space-between;">
    <span style="display:flex;align-items:center;gap:7px;">
      {icon('file-text',14,t['accent'])} File Manager
    </span>
    <span style="font-size:0.7rem;color:{t['muted']};font-weight:400;">{n_files} file{'s' if n_files!=1 else ''}</span>
  </div>
""", unsafe_allow_html=True)

        if not files:
            st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0;">
  <div style="font-size:0.82rem;color:{t['muted']};">No files yet.<br>Upload above to get started.</div>
</div>
""", unsafe_allow_html=True)
        else:
            for i, f in enumerate(files):
                is_active = st.session_state.ds_active_idx == i
                border = f"border:1.5px solid {t['accent']};" if is_active else f"border:1px solid {t['border']};"
                bg     = f"background:{t['card_hover']};" if is_active else ""
                type_colors = {"table": (t['blue'], "Table"), "image": (t['purple'], "Image"),
                               "pdf": (t['red'], "PDF"), "other": (t['muted'], "File")}
                tc, tlbl = type_colors.get(f["type"], (t['muted'], "File"))
                analyzed_dot = (f'<span style="width:6px;height:6px;border-radius:50%;'
                                f'background:{t["green"]};display:inline-block;'
                                f'margin-left:4px;" title="Analysed"></span>'
                                if f["name"] in st.session_state.ds_analysis else "")
                st.markdown(f"""
<div style="{border}{bg}border-radius:10px;padding:0.55rem 0.7rem;margin-bottom:0.3rem;
     display:flex;align-items:center;gap:8px;">
  <div style="width:28px;height:28px;flex-shrink:0;border-radius:8px;
       background:{t['accent_glow'] if is_active else t['bg2']};
       display:flex;align-items:center;justify-content:center;">
    {icon('file-text',13,t['accent'] if is_active else t['text2'])}
  </div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.78rem;font-weight:600;color:{t['accent'] if is_active else t['text']};
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{f['name']}{analyzed_dot}</div>
    <div style="font-size:0.65rem;color:{t['muted']};margin-top:1px;">
      <span style="color:{tc};font-weight:600;">{tlbl}</span>
      &nbsp;·&nbsp;{f['size']/1024:.1f} KB
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
                btn_col, del_col = st.columns([4, 1])
                with btn_col:
                    if st.button("Open", key=f"ds_open_{i}", use_container_width=True):
                        st.session_state.ds_active_idx = i
                        st.rerun()
                with del_col:
                    if st.button("X", key=f"ds_del_{i}", use_container_width=True):
                        st.session_state.ds_files.pop(i)
                        if st.session_state.ds_active_idx == i:
                            st.session_state.ds_active_idx = None
                        elif st.session_state.ds_active_idx and st.session_state.ds_active_idx > i:
                            st.session_state.ds_active_idx -= 1
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        active_idx = st.session_state.ds_active_idx
        if active_idx is not None and active_idx < len(files):
            af = files[active_idx]
            if af["type"] == "table" and af["df"] is not None:
                df = af["df"]
                st.markdown(f"""
<div class="ds-card" style="margin-top:0.5rem;">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};
       margin-bottom:0.55rem;display:flex;align-items:center;gap:7px;">
    {icon('download',13,t['accent'])} Export Active File
  </div>
""", unsafe_allow_html=True)
                d1, d2, d3 = st.columns(3, gap="small")
                with d1:
                    st.download_button("CSV", df.to_csv(index=False),
                        f"{af['name'].rsplit('.',1)[0]}.csv", "text/csv",
                        use_container_width=True, key="dl_csv")
                with d2:
                    st.download_button("JSON", df.to_json(orient="records"),
                        f"{af['name'].rsplit('.',1)[0]}.json", "application/json",
                        use_container_width=True, key="dl_json")
                with d3:
                    st.download_button("Excel", to_excel(df),
                        f"{af['name'].rsplit('.',1)[0]}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True, key="dl_xlsx")
                st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        active_idx = st.session_state.ds_active_idx

        if active_idx is None or active_idx >= len(files):
            st.markdown(f"""
<div class="empty-drop" style="min-height:60vh;display:flex;flex-direction:column;
     align-items:center;justify-content:center;">
  <div style="width:60px;height:60px;border-radius:16px;margin-bottom:1rem;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       display:flex;align-items:center;justify-content:center;
       box-shadow:0 0 22px {t['accent_glow']};">
    {icon('scan-eye',28,'#fff')}
  </div>
  <div style="font-size:1.05rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">
    Visual Canvas
  </div>
  <div style="font-size:0.84rem;color:{t['text2']};max-width:360px;text-align:center;line-height:1.65;">
    Upload a file on the left and select it to open the AI-powered analysis canvas.
  </div>
  <div style="display:flex;gap:0.5rem;flex-wrap:wrap;justify-content:center;margin-top:1.25rem;">
    <span style="background:{t['card']};border:1px solid {t['border']};border-radius:20px;padding:4px 14px;font-size:0.73rem;color:{t['text2']};">CSV · JSON · Excel</span>
    <span style="background:{t['card']};border:1px solid {t['border']};border-radius:20px;padding:4px 14px;font-size:0.73rem;color:{t['text2']};">PNG · JPG · JPEG</span>
    <span style="background:{t['card']};border:1px solid {t['border']};border-radius:20px;padding:4px 14px;font-size:0.73rem;color:{t['text2']};">PDF Documents</span>
  </div>
</div>
""", unsafe_allow_html=True)

        else:
            af = files[active_idx]

            st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;padding:0.8rem 1.1rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.4rem;">
    <div style="display:flex;align-items:center;gap:9px;">
      <div style="width:34px;height:34px;flex-shrink:0;
           background:{t['accent_glow']};border-radius:9px;
           display:flex;align-items:center;justify-content:center;">
        {icon('file-text',16,t['accent'])}
      </div>
      <div>
        <div style="font-weight:700;font-size:0.92rem;color:{t['text']};">{af['name']}</div>
        <div style="font-size:0.67rem;color:{t['muted']};">
          {af['ext'].upper()} &nbsp;·&nbsp; {af['size']/1024:.1f} KB &nbsp;·&nbsp;
          {f"{af['df'].shape[0]} rows x {af['df'].shape[1]} cols" if af['df'] is not None else af['type'].capitalize()}
        </div>
      </div>
    </div>
    {'<span class="BG G">' + icon("check-circle",9,t["green"]) + " Analysed</span>"
      if af["name"] in st.session_state.ds_analysis else
      '<span class="BG A">' + icon("zap",9,t["accent"]) + " Not yet analysed</span>"}
  </div>
</div>
""", unsafe_allow_html=True)

            if af["type"] == "table" and af["df"] is not None:
                df = af["df"]
                tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Charts", "AI Analysis", "Ask AI"])

                with tab1:
                    # Fullscreen-capable dataframe (use_container_width + height triggers fullscreen icon)
                    st.markdown(f"""
<div style="font-size:0.75rem;color:{t['text2']};margin-bottom:0.4rem;">
  Showing first 100 rows &nbsp;·&nbsp;
  <strong style="color:{t['text']};">{df.shape[0]}</strong> total rows,
  <strong style="color:{t['text']};">{df.shape[1]}</strong> columns

</div>
""", unsafe_allow_html=True)
                    # use_container_width=True + height renders the fullscreen expand icon natively
                    st.dataframe(df.head(100), use_container_width=True, height=360)

                    st.markdown(f"""
<div class="ds-card" style="margin-top:0.5rem;">
  <div style="font-size:0.82rem;font-weight:700;color:{t['text']};margin-bottom:0.5rem;">
    Column Overview
  </div>
""", unsafe_allow_html=True)
                    cols_info = [(c,
                                  "Numeric" if pd.api.types.is_numeric_dtype(df[c]) else "Text",
                                  df[c].isna().sum(),
                                  df[c].nunique()) for c in df.columns]
                    th_s = (f"text-align:left;padding:0.35rem 0.6rem;font-size:0.63rem;"
                            f"font-weight:700;color:{t['muted']};text-transform:uppercase;"
                            f"letter-spacing:0.06em;border-bottom:1px solid {t['border']};")
                    td_s = f"padding:0.4rem 0.6rem;border-bottom:1px solid {t['border']};font-size:0.77rem;"
                    th_html = "".join(f'<th style="{th_s}">{h}</th>'
                                      for h in ["Column", "Type", "Nulls", "Unique"])
                    rows_html = ""
                    for name_c, dtype_c, nulls_c, uniq_c in cols_info:
                        clr = t['blue'] if dtype_c == "Numeric" else t['purple']
                        rows_html += (f'<tr>'
                            f'<td style="{td_s}color:{t["text"]};font-weight:500;">{name_c}</td>'
                            f'<td style="{td_s}"><span style="background:rgba(59,130,246,0.14);color:{clr};'
                            f'padding:1px 7px;border-radius:20px;font-size:0.67rem;font-weight:600;">{dtype_c}</span></td>'
                            f'<td style="{td_s}color:{t["text2"]};">{nulls_c}</td>'
                            f'<td style="{td_s}color:{t["text2"]};">{uniq_c}</td>'
                            f'</tr>')
                    st.markdown(f"""
<div style="overflow-x:auto;">
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>{th_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div></div>
""", unsafe_allow_html=True)

                with tab2:
                    all_cols = df.columns.tolist()
                    num_cols = [c for c in all_cols if pd.api.types.is_numeric_dtype(df[c])]

                    if len(all_cols) < 2:
                        st.info("Need at least 2 columns to render charts.")
                    else:
                        cc1, cc2, cc3 = st.columns(3, gap="small")
                        with cc1:
                            x_col = st.selectbox("X Axis", all_cols, key="ds_chart_x")
                        with cc2:
                            y_col = st.selectbox("Y Axis (numeric)",
                                                 num_cols if num_cols else all_cols,
                                                 key="ds_chart_y")
                        with cc3:
                            chart_type = st.selectbox("Chart Type",
                                                      ["Bar", "Line", "Area"],
                                                      key="ds_chart_type")

                        try:
                            cdf = df[[x_col, y_col]].copy()
                            if not pd.api.types.is_numeric_dtype(cdf[y_col]):
                                cdf[y_col] = pd.to_numeric(
                                    cdf[y_col].astype(str).str.replace(",","").str.strip(),
                                    errors="coerce"
                                )
                            cdf = cdf.dropna(subset=[y_col]).set_index(x_col)
                        except Exception as _ce:
                            st.error(f"Chart preparation error: {_ce}")
                            cdf = pd.DataFrame()

                        if cdf.empty:
                            st.warning("No plottable numeric data with the selected columns.")
                        else:
                            st.markdown(f"""
<div class="ds-card" style="margin-top:0.3rem;padding-bottom:0.5rem;">
  <div style="font-size:0.8rem;font-weight:600;color:{t['text2']};margin-bottom:0.5rem;">
    {y_col} by {x_col} &nbsp;—&nbsp; {chart_type} Chart
  </div>
""", unsafe_allow_html=True)
                            # height param causes fullscreen expand icon to appear natively
                            if chart_type == "Bar":
                                st.bar_chart(cdf, use_container_width=True, height=320)
                            elif chart_type == "Line":
                                st.line_chart(cdf, use_container_width=True, height=320)
                            else:
                                st.area_chart(cdf, use_container_width=True, height=320)
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Descriptive stats — also fullscreen-capable
                        if num_cols:
                            st.markdown(f"""
<div class="ds-card">
  <div style="font-size:0.82rem;font-weight:700;color:{t['text']};margin-bottom:0.5rem;">
    Descriptive Statistics
  </div>
""", unsafe_allow_html=True)
                            # height param triggers native fullscreen expand icon on dataframe
                            st.dataframe(df[num_cols].describe().round(3),
                                         use_container_width=True, height=240)
                            st.markdown('</div>', unsafe_allow_html=True)

                with tab3:
                    fname = af["name"]
                    if fname in st.session_state.ds_analysis:
                        analysis_text = st.session_state.ds_analysis[fname]
                        st.markdown(f"""
<div style="display:flex;align-items:center;gap:7px;margin-bottom:0.5rem;">
  <span class="BG G">{icon('check-circle',10,t['green'])} Analysis complete</span>
</div>
<div class="analysis-box">{analysis_text}</div>
""", unsafe_allow_html=True)
                        st.download_button(
                            "Download Analysis (.txt)", analysis_text,
                            f"{fname}_analysis.txt", "text/plain",
                            use_container_width=True, key="dl_analysis",
                        )
                        if st.button("Re-analyse", use_container_width=True, key="reanalyse"):
                            del st.session_state.ds_analysis[fname]
                            st.rerun()
                    else:
                        summary = df_summary(df)
                        st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;">
  <div style="font-size:0.85rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">
    {icon('cpu',13,t['accent'])} AI-Powered Data Analysis
  </div>
  <div style="font-size:0.8rem;color:{t['text2']};line-height:1.6;">
    Click <strong style="color:{t['text']};">Run AI Analysis</strong> to get a comprehensive
    breakdown of your dataset — patterns, anomalies, column insights, and recommendations.
  </div>
</div>
<div style="font-size:0.73rem;color:{t['muted']};margin-bottom:0.5rem;font-family:monospace;">
  Dataset: {df.shape[0]} rows x {df.shape[1]} columns
</div>
""", unsafe_allow_html=True)
                        if st.button(f"Run AI Analysis on {fname}",
                                     use_container_width=True, key="run_analysis"):
                            with st.spinner("Analysing your dataset with AI..."):
                                system_prompt = (
                                    "You are a senior data analyst. Provide a thorough, structured, "
                                    "actionable analysis. Use clear sections: Overview, Column Insights, "
                                    "Key Patterns, Anomalies / Warnings, Recommendations. "
                                    "Format with clear headers using === and ---."
                                )
                                user_prompt = (
                                    f"Analyse this dataset:\n\nFilename: {fname}\n\n"
                                    f"{summary}\n\nProvide a detailed analysis."
                                )
                                result = call_claude(user_prompt, system_prompt)
                            st.session_state.ds_analysis[fname] = result
                            st.rerun()

                with tab4:
                    fname   = af["name"]
                    summary = df_summary(df)

                    st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;padding:0.75rem 1rem;">
  <div style="font-size:0.78rem;color:{t['text2']};line-height:1.55;">
    Ask any question about <strong style="color:{t['text']};">{fname}</strong>.
    The AI will answer using your actual data structure.
  </div>
</div>
""", unsafe_allow_html=True)

                    chat_key = f"chat_{fname}"
                    if chat_key not in st.session_state:
                        st.session_state[chat_key] = []
                    messages = st.session_state[chat_key]

                    if not messages:
                        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:2rem;text-align:center;margin-bottom:0.5rem;">
  <div style="font-size:0.85rem;color:{t['muted']};">
    Ask a question about your data below.<br>
    <span style="font-size:0.75rem;">e.g. "What are the top 5 values in column X?"</span>
  </div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem;max-height:300px;overflow-y:auto;
     display:flex;flex-direction:column;gap:0.5rem;margin-bottom:0.5rem;">
""", unsafe_allow_html=True)
                        for msg in messages:
                            if msg["role"] == "user":
                                st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin-bottom:0.3rem;">
  <div class="chat-bubble-user">{msg['content']}</div>
</div>
""", unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:7px;margin-bottom:0.3rem;">
  <div style="width:26px;height:26px;flex-shrink:0;border-radius:8px;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       display:flex;align-items:center;justify-content:center;">
    {icon('bot',12,'#fff')}
  </div>
  <div class="chat-bubble-ai">{msg['content'].replace(chr(10),'<br>')}</div>
</div>
""", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    user_q = st.chat_input("Ask anything about this dataset...", key=f"ds_chat_{fname}")
                    if user_q:
                        st.session_state[chat_key].append({"role": "user", "content": user_q})
                        with st.spinner("Thinking..."):
                            reply = call_claude(
                                f"Dataset info:\n{summary}\n\nUser question: {user_q}",
                                "You are a precise data analyst assistant. Answer concisely."
                            )
                        st.session_state[chat_key].append({"role": "assistant", "content": reply})
                        st.rerun()

                    if messages:
                        if st.button("Clear conversation", key=f"clear_chat_{fname}"):
                            st.session_state[chat_key] = []
                            st.rerun()

            elif af["type"] == "image":
                tab_img1, tab_img2 = st.tabs(["Image Viewer", "AI Vision Analysis"])

                with tab_img1:
                    st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.4rem;padding:0.7rem 1rem;">
  <div style="font-size:0.78rem;color:{t['text2']};">
    Viewing: <strong style="color:{t['text']};">{af['name']}</strong>
    &nbsp;·&nbsp; {af['size']/1024:.1f} KB
  </div>
</div>
""", unsafe_allow_html=True)
                    st.image(af["bytes"], caption=af["name"], use_container_width=True)
                    mime = "image/png" if af["ext"] == "png" else "image/jpeg"
                    st.download_button(f"Download {af['name']}", af["bytes"], af["name"], mime,
                                       use_container_width=True, key="dl_img")

                with tab_img2:
                    fname = af["name"]
                    if fname in st.session_state.ds_analysis:
                        analysis_text = st.session_state.ds_analysis[fname]
                        st.markdown(f'<div class="analysis-box">{analysis_text}</div>', unsafe_allow_html=True)
                        st.download_button("Download Analysis", analysis_text,
                            f"{fname}_analysis.txt", "text/plain",
                            use_container_width=True, key="dl_img_analysis")
                        if st.button("Re-analyse", use_container_width=True, key="reanalyse_img"):
                            del st.session_state.ds_analysis[fname]
                            st.rerun()
                    else:
                        st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;">
  <div style="font-size:0.85rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">
    {icon('scan-eye',13,t['accent'])} AI Vision Analysis
  </div>
  <div style="font-size:0.8rem;color:{t['text2']};line-height:1.6;">
    Examine your image and get a detailed description, key objects, text, and insights.
  </div>
</div>
""", unsafe_allow_html=True)
                        if st.button("Analyse Image with AI", use_container_width=True, key="run_img_analysis"):
                            with st.spinner("Analysing image with AI..."):
                                result = call_claude(
                                    "Analyse this image: 1) Description, 2) Key objects, "
                                    "3) Visible text, 4) Colors, 5) Context, 6) Insights.",
                                    "You are an expert image analyst."
                                )
                            st.session_state.ds_analysis[fname] = result
                            st.rerun()

            elif af["type"] == "pdf":
                tab_pdf1, tab_pdf2 = st.tabs(["PDF Viewer", "Download"])
                with tab_pdf1:
                    st.markdown(f"""
<div class="ds-card" style="margin-bottom:0.5rem;padding:0.7rem 1rem;">
  <div style="font-size:0.78rem;color:{t['text2']};">
    PDF: <strong style="color:{t['text']};">{af['name']}</strong>
    &nbsp;·&nbsp; {af['size']/1024:.1f} KB
  </div>
</div>
""", unsafe_allow_html=True)
                    b64_pdf = af["b64"]
                    st.markdown(
                        f'<iframe src="data:application/pdf;base64,{b64_pdf}" '
                        f'width="100%" height="500px" '
                        f'style="border:1px solid {t["border"]};border-radius:12px;"></iframe>',
                        unsafe_allow_html=True
                    )
                with tab_pdf2:
                    st.download_button(f"Download {af['name']}", af["bytes"], af["name"],
                                       "application/pdf", use_container_width=True, key="dl_pdf")
            else:
                st.markdown(f"""
<div class="ds-card" style="text-align:center;padding:3rem;">
  <div style="font-size:0.92rem;color:{t['muted']};">
    Preview not available for this file type.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Global AI Chat
    st.markdown('<div class="ds-pad" style="padding-top:0;">', unsafe_allow_html=True)
    st.markdown(f"""
<div style="height:1px;background:{t['border']};margin-bottom:0.75rem;"></div>
<div style="font-size:0.88rem;font-weight:700;color:{t['text']};
     margin-bottom:0.5rem;display:flex;align-items:center;gap:7px;">
  {icon('sparkles',14,t['accent'])} Global AI Assistant
  <span style="font-size:0.72rem;font-weight:400;color:{t['muted']};margin-left:4px;">
    Ask anything across all your loaded files
  </span>
</div>
""", unsafe_allow_html=True)

    gchat = st.session_state.ds_chat
    if gchat:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:0.85rem 1rem;max-height:240px;overflow-y:auto;
     display:flex;flex-direction:column;gap:0.45rem;margin-bottom:0.5rem;">
""", unsafe_allow_html=True)
        for msg in gchat[-10:]:
            if msg["role"] == "user":
                st.markdown(f"""
<div style="display:flex;justify-content:flex-end;">
  <div class="chat-bubble-user">{msg['content']}</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:7px;">
  <div style="width:26px;height:26px;flex-shrink:0;border-radius:8px;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       display:flex;align-items:center;justify-content:center;">
    {icon('sparkles',11,'#fff')}
  </div>
  <div class="chat-bubble-ai">{msg['content'].replace(chr(10),'<br>')}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    global_q = st.chat_input(
        "Ask about any of your loaded files, or ask a general data question...",
        key="ds_global_chat",
    )
    if global_q:
        st.session_state.ds_chat.append({"role": "user", "content": global_q})
        files_ctx = ""
        for f in st.session_state.ds_files:
            if f["type"] == "table" and f["df"] is not None:
                files_ctx += f"\n\nFile: {f['name']}\n{df_summary(f['df'])}"
            else:
                files_ctx += f"\n\nFile: {f['name']} (type: {f['type']}, size: {f['size']/1024:.1f} KB)"
        with st.spinner("Thinking..."):
            reply = call_claude(
                f"Loaded files:{files_ctx if files_ctx else ' None.'}\n\nQuestion: {global_q}",
                "You are a helpful data analyst. Answer concisely and accurately."
            )
        st.session_state.ds_chat.append({"role": "assistant", "content": reply})
        st.rerun()

    if gchat:
        if st.button("Clear global chat", key="clear_global_chat"):
            st.session_state.ds_chat = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)