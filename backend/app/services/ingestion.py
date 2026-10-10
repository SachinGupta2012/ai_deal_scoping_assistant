"""Ingestion: text + PDF/DOCX/TXT -> normalized markdown + offset chunks."""
import os
import uuid
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.config import settings

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150


def normalize_text(raw: str) -> str:
    return "\n".join(line.rstrip() for line in raw.strip().splitlines())


def chunk_text(text: str):
    chunks, i, idx = [], 0, 0
    while i < len(text):
        end = min(len(text), i + CHUNK_SIZE)
        chunks.append({"idx": idx, "text": text[i:end], "char_start": i, "char_end": end})
        idx += 1
        i = end - CHUNK_OVERLAP if end < len(text) else end
    return chunks


def read_upload(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        os.makedirs(settings.STORAGE_DIR, exist_ok=True)
        tmp = os.path.join(settings.STORAGE_DIR, f"{uuid.uuid4()}.pdf")
        with open(tmp, "wb") as f:
            f.write(data)
        reader = PdfReader(tmp)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        os.remove(tmp)
        return text
    if lower.endswith(".docx"):
        os.makedirs(settings.STORAGE_DIR, exist_ok=True)
        tmp = os.path.join(settings.STORAGE_DIR, f"{uuid.uuid4()}.docx")
        with open(tmp, "wb") as f:
            f.write(data)
        doc = DocxDocument(tmp)
        text = "\n".join(p.text for p in doc.paragraphs)
        os.remove(tmp)
        return text
    return data.decode("utf-8", errors="ignore")
