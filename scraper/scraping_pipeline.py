from scraper.page_loader import load_page
from scraper.html_processor import preprocess_html
from scraper.content_extractor import extract_content
from scraper.browser_manager import launch_browser, close_browser

def execute_scraping(url: str) -> dict:
    playwright, browser = launch_browser()
    try:
        raw_html = load_page(browser, url)
        cleaned_html = preprocess_html(raw_html)
        extracted_content = extract_content(cleaned_html)
        return extracted_content
    finally:
        close_browser(playwright, browser)
