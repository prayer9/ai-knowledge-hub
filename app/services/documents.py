from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

SUPPORTED = {".txt", ".md", ".pdf", ".docx"}
MAX_BYTES = 5 * 1024 * 1024


def extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError("Only PDF, DOCX, TXT and Markdown files are supported")
    if not content or len(content) > MAX_BYTES:
        raise ValueError("File must be non-empty and at most 5 MB")
    try:
        if ext == ".pdf":
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        elif ext == ".docx":
            doc = Document(BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
        else:
            text = content.decode("utf-8-sig")
    except Exception as exc:
        raise ValueError("Unable to parse document") from exc
    text = " ".join(text.split())
    if not text:
        raise ValueError("No extractable text found")
    return text[:200_000]


def split_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    if size <= overlap or overlap < 0:
        raise ValueError("Invalid chunk settings")
    chunks = []
    pos = 0
    while pos < len(text):
        chunks.append(text[pos:pos + size])
        if pos + size >= len(text):
            break
        pos += size - overlap
    return chunks
