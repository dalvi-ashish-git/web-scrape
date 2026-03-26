from bs4 import BeautifulSoup, Comment

REMOVE_TAGS = ["script", "style", "noscript", "link", "meta"]

def clean_html(raw_html: str):
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unwanted tags
    for tag in soup.find_all(REMOVE_TAGS):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove inline styles and JS
    for tag in soup.find_all(True):
        tag.attrs = {
            k: v for k, v in tag.attrs.items()
            if k not in ["style", "onclick", "onload"]
        }

    return soup