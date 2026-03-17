import traceback
import streamlit as st
import pandas as pd
import sys
import os
from urllib.parse import urlparse

# --- 1. SYSTEM PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- 2. CORE IMPORTS ---
from scraping_pipeline import execute_scraping
try:
    from llm.gemini_service import LLMProcessor
    # Ensure your GeminiService uses 'gemini-3-flash-preview' or 'gemini-2.5-flash'
    llm_engine = LLMProcessor()
    ai_available = True
except Exception as e:
    ai_available = False
    ai_error = str(e)

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="AI Scraper Demo", layout="wide")

st.markdown("""
<style>
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    .stDataFrame { border: 1px solid #30363d; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🕷️ Core Scraper + 🧠 Gemini 3 AI Demo")
st.write("Extracting raw content via Playwright and structuring it with the latest Gemini model.")

# --- 4. INPUT SECTION ---
url_input = st.text_input("Enter Website URL", placeholder="https://quotes.toscrape.com")

if st.button("Start Extraction Pipeline", type="primary", use_container_width=True):
    url = url_input.strip()
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            st.error("Invalid URL format.")
        else:
            col_raw, col_ai = st.columns(2)

            # --- STEP 1: EXECUTE SCRAPING ---
            with st.spinner("Step 1: Scraping raw data..."):
                try:
                    data = execute_scraping(url)
                    
                    with col_raw:
                        st.subheader("📋 Raw Scraper Output")
                        st.info(f"**Title:** {data.get('title', 'N/A')}")
                        
                        # Flatten headings and paragraphs for AI context
                        raw_list = data.get("headings", []) + data.get("paragraphs", [])
                        
                        raw_df = pd.DataFrame(raw_list, columns=["Raw Text Snippets"])
                        st.dataframe(raw_df, use_container_width=True, height=400)
                        st.metric("Snippets Found", len(raw_list))

                    # --- STEP 2: EXECUTE AI STRUCTURING ---
                    with col_ai:
                        st.subheader("🧠 AI Structured Table")
                        if not ai_available:
                            st.error(f"AI Module Error: {ai_error}")
                        elif not raw_list:
                            st.warning("No text found to process.")
                        else:
                            with st.spinner("Step 2: AI is analyzing patterns..."):
                                # Run the I/O Processing and Data Refinement
                                structured_df = llm_engine.process_scraped_content(raw_list)

                            if structured_df is not None and not structured_df.empty:
                                st.success("AI extraction complete!")
                                st.dataframe(structured_df, use_container_width=True, height=400)
                                
                                # Download Button
                                csv = structured_df.to_csv(index=False).encode('utf-8')
                                st.download_button("📥 Download Structured CSV", csv, "ai_data.csv", "text/csv")
                            else:
                                st.error("AI could not identify a table pattern in this data.")

                except Exception as e:
                    st.error("Pipeline Failed")
                    st.code(traceback.format_exc())

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("Pipeline Status")
    st.write(f"**Scraper:** Playwright ✅")
    st.write(f"**AI Engine:** {'Gemini 3 Flash ✅' if ai_available else 'Not Loaded ❌'}")
    st.divider()
    st.caption("Task: Develop LLM Query I/O Processing Module")