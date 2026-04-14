from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_cleaner import clean_html
from scraper.target_extractor import extract_by_target_tags
from scraper.compact_tree_builder import build_compact_tree
from scraper.url_validator import validate_url

from llm.tag_identifier import identify_target_tags
from llm.data_processor import process_extracted_data

import json
import re


def _parse_llm_output(final_output):
    # If LLM returns JSON-like string, try to parse it to list/dict for DataFrame
    if isinstance(final_output, (list, dict)):
        return final_output

    if isinstance(final_output, str):
        m = re.search(r"\[[\s\S]*\]|\{[\s\S]*\}", final_output)
        if m:
            try:
                parsed = json.loads(m.group())
                return parsed
            except Exception:
                pass
        # fallback: wrap as one-row dict
        return [{"ai_output": final_output}]

    # unknown type: stringify
    return [{"ai_output": str(final_output)}]


def execute_scraping(url, query):
    if not validate_url(url):
        raise ValueError("Invalid URL")

    playwright, browser = launch_browser()
    try:
        # For scheduler, run synchronously in this process (worker subprocess)
        raw_html = load_page(browser, url)

        soup = clean_html(raw_html)

        # Identify tags (LLM) — can be synchronous in worker
        tag_list = identify_target_tags(query)

        extracted_data = extract_by_target_tags(soup, tag_list)

        compact_tree = build_compact_tree(extracted_data)

        final_output = process_extracted_data(query, compact_tree)

        # Return raw LLM output (string or structured) — UI will display as-is
        return final_output

    finally:
        close_browser(playwright, browser)
