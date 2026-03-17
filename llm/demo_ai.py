import streamlit as st
import pandas as pd
import sys
import os
import traceback
from urllib.parse import urlparse

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from scraping_pipeline import execute_scraping
from llm.gemini_service import LLMProcessor

st.set_page_config(page_title="AI Scraper Demo", layout="wide")

st.title("🕷️ Web Scraper + 🧠 Dynamic AI Extraction")

# --- UI INPUTS ---
col_u, col_s = st.columns([2, 1])
with col_u:
    url_input = st.text_input("Enter Website URL", placeholder="[https://example.com](https://example.com)")
with col_s:
    schema_input = st.text_input("📋 Columns to Extract", value="Name, Price, Status")

if st.button("Start Extraction Pipeline", type="primary", use_container_width=True):
    if not url_input.strip():
        st.warning("Please enter a URL.")
    else:
        url = url_input.strip()
        if not url.startswith(("http", "https")): url = f"https://{url}"
        
        col_raw, col_ai = st.columns(2)
        
        with st.spinner("1. Scraping raw site data..."):
            try:
                # RAW SCRAPE
                data = execute_scraping(url)
                raw_list = data.get("headings", []) + data.get("paragraphs", [])
                
                with col_raw:
                    st.subheader("📋 Raw Scraper Results")
                    st.dataframe(pd.DataFrame(raw_list, columns=["Raw Text"]), use_container_width=True, height=400)
                
                # AI PROCESS
                with col_ai:
                    st.subheader("🧠 AI Structured Table")
                    processor = LLMProcessor()
                    with st.spinner("AI is analyzing snippets..."):
                        df = processor.process_scraped_content(raw_list, target_schema=schema_input)
                    
                    if df is not None and not df.empty:
                        st.success("Extraction Complete!")
                        st.dataframe(df, use_container_width=True, height=400)
                    else:
                        st.error("AI could not structure this data.")
                        
            except Exception as e:
                st.error("Pipeline Failure")
                st.code(traceback.format_exc())