
"""Chunking helpers for the RAG pipeline.

This mirrors the Node implementation with a practical character-based token
estimate where 1 token ~= 4 characters.
"""

from __future__ import annotations

from typing import Iterable, Sequence


DEFAULT_CHUNK_TOKENS = 400
DEFAULT_OVERLAP_TOKENS = 50
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str | None) -> int:
	if not text:
		return 0
	return max(1, -(-len(text) // CHARS_PER_TOKEN))


def chunk_text(text: str | None, opts: dict | None = None) -> list[str]:
	opts = opts or {}
	chunk_tokens = opts.get("chunkTokens") or DEFAULT_CHUNK_TOKENS
	overlap_tokens = opts.get("overlapTokens")
	if not isinstance(overlap_tokens, int):
		overlap_tokens = DEFAULT_OVERLAP_TOKENS

	chunk_chars = chunk_tokens * CHARS_PER_TOKEN
	overlap_chars = max(0, overlap_tokens * CHARS_PER_TOKEN)

	if not text:
		return []

	chunks: list[str] = []
	start = 0
	length = len(text)

	while start < length:
		end = min(start + chunk_chars, length)
		slice_text = text[start:end].strip()
		if slice_text:
			chunks.append(slice_text)

		if end == length:
			break

		start = end - overlap_chars
		if start < 0:
			start = 0

	return chunks


def chunk_pages(pages: Sequence[str] | Iterable[str] | str | None = None, opts: dict | None = None) -> list[str]:
	if pages is None:
		normalized_pages: list[str] = [""]
	elif isinstance(pages, str):
		normalized_pages = [pages]
	else:
		normalized_pages = [str(page or "") for page in pages]

	joined = "\f\n".join(normalized_pages)
	return chunk_text(joined, opts)


__all__ = ["estimate_tokens", "chunk_text", "chunk_pages"]
