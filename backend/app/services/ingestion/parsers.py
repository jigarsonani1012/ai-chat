from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader


def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(parts).strip()


def extract_url_text(url: str) -> str:
    response = httpx.get(url, timeout=20.0, follow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())
