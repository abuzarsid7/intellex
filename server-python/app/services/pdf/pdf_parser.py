
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def _clean_page_text(text: str) -> str:
	return text.strip()


def _extract_info(reader: PdfReader) -> dict[str, Any]:
	try:
		info = reader.metadata or {}
	except Exception:
		info = {}

	normalized: dict[str, Any] = {}
	for key, value in dict(info).items():
		normalized[str(key).lstrip("/")] = value

	return normalized


def extract_text_from_buffer(buffer: bytes) -> dict[str, Any]:
	"""Extract text and metadata from a PDF buffer.

	Returns a payload matching the Node parser shape:
	- text: full raw text
	- pages: list of per-page text strings
	- numpages: page count
	- info: document metadata
	- metadata: alias of metadata for compatibility
	"""
	reader = PdfReader(BytesIO(buffer))
	pages: list[str] = []
	page_text_parts: list[str] = []

	for page in reader.pages:
		text = _clean_page_text(page.extract_text() or "")
		pages.append(text)
		if text:
			page_text_parts.append(text)

	raw_text = "\n\n".join(page_text_parts)
	info_data = _extract_info(reader)

	return {
		"text": raw_text,
		"pages": [page for page in pages if page],
		"numpages": len(reader.pages),
		"info": info_data,
		"metadata": info_data,
	}


def extract_text_from_pdf(file_path: str | Path) -> dict[str, Any]:
	"""Read a PDF from disk and extract text/meta using `extract_text_from_buffer`."""
	path = Path(file_path)
	return extract_text_from_buffer(path.read_bytes())


__all__ = ["extract_text_from_buffer", "extract_text_from_pdf"]
