from concurrent.futures import ThreadPoolExecutor

from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_cleaner import clean_html
from scraper.target_extractor import extract_by_target_tags
from scraper.compact_tree_builder import build_compact_tree
from scraper.url_validator import validate_url

# LLM
from llm.tag_identifier import identify_target_tags
from llm.data_processor import process_extracted_data


def execute_scraping(url, query):

    if not validate_url(url):
        raise ValueError("Invalid URL")

    playwright, browser = launch_browser()

    try:
        # 🔥 Parallel execution
        with ThreadPoolExecutor() as executor:

            # Task 1 → Load & clean HTML
            future_html = executor.submit(load_page, browser, url)

            # Task 2 → LLM tag identification
            future_tags = executor.submit(identify_target_tags, query)

            raw_html = future_html.result()
            tag_list = future_tags.result()

        # Step 2: Clean HTML
        soup = clean_html(raw_html)

        # Step 3: Extract only required tags
        extracted_data = extract_by_target_tags(soup, tag_list)

        # Step 4: Build compact tree
        compact_tree = build_compact_tree(extracted_data)

        # Step 5: Final LLM processing
        final_output = process_extracted_data(query, compact_tree)

        return final_output

    finally:
        close_browser(playwright, browser)
