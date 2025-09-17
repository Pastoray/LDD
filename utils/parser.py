import markdown
from bs4 import BeautifulSoup

def markdown_to_text(markdown_str: str) -> str:
    html_str = markdown.markdown(markdown_str)
    return html_to_text(html_str)

def html_to_text(html_str: str) -> str:
    soup = BeautifulSoup(html_str, "html.parser")

    for sup in soup.find_all("sup"):
        sup.replace_with(f" ^ {sup.get_text()}")

    for sub in soup.find_all("sub"):
        sub.replace_with(f"_{sub.get_text()}")

    return soup.get_text()
