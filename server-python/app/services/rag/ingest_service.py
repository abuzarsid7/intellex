
from __future__ import annotations

from pathlib import Path
from typing import Any
import logging

from app.services.pdf.pdf_parser import extract_text_from_buffer, extract_text_from_pdf
from app.services.rag.chunk_service import chunk_pages
from app.services.rag.embedding_service import embed_chunks
from app.services.rag.vector_store_service import store_chunk_embeddings


logger = logging.getLogger("intellex.rag.ingest")


def build_source_id(file: dict[str, Any] | None = None) -> str:
	if not file:
		return f"document-{int(__import__('time').time() * 1000)}"

	file_id = str(file.get("file_id") or "").strip()
	if file_id:
		return file_id

	return (
		str(file.get("filename") or "")
		or str(file.get("originalname") or "")
		or f"document-{int(__import__('time').time() * 1000)}"
	)


def build_chunk_metadata(
	*,
	file: dict[str, Any] | None,
	parsed: dict[str, Any] | None,
	chunk: dict[str, Any],
	collection_name: str | None,
	source_id: str,
	metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
	return {
		"user_id": (metadata or {}).get("user_id"),
		"chat_id": (metadata or {}).get("chat_id"),
		"file_id": (metadata or {}).get("file_id") or source_id,
	}


def _normalize_file(file: Any | None) -> dict[str, Any]:
	if file is None:
		return {}

	if isinstance(file, dict):
		return file

	return {
		"filename": getattr(file, "filename", None),
		"originalname": getattr(file, "originalname", None),
		"mimetype": getattr(file, "content_type", None) or getattr(file, "mimetype", None),
		"size": getattr(file, "size", None),
	}


def _normalize_pages(parsed: dict[str, Any] | None = None) -> list[str]:
	pages = (parsed or {}).get("pages")
	if not pages:
		return []

	normalized_pages: list[str] = []
	for page in pages:
		if isinstance(page, dict):
			text = page.get("text")
		else:
			text = page

		page_text = str(text or "").strip()
		if page_text:
			normalized_pages.append(page_text)

	return normalized_pages


def ingest_parsed_document(
	*,
	parsed: dict[str, Any] | None,
	file: dict[str, Any] | Any | None = None,
	collection_name: str | None = None,
	chunk_options: dict[str, Any] | None = None,
	embed_options: dict[str, Any] | None = None,
	metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
	file_data = _normalize_file(file)
	source_id = build_source_id(file_data)
	raw_text = str((parsed or {}).get("text") or "").strip()
	if not raw_text:
		raise ValueError("Parsed document did not contain any text to embed")

	logger.info("ingest_parsed_document start collection_name=%s source=%s", collection_name, source_id)
	page_texts = _normalize_pages(parsed)
	chunks = chunk_pages(page_texts or raw_text, chunk_options)
	embeddings = embed_chunks(chunks, embed_options)

	payload: list[dict[str, Any]] = []
	for chunk in embeddings:
		chunk_id = f"{source_id}:{chunk.get('index')}"
		payload.append(
			{
				"id": chunk_id,
				"text": chunk.get("text"),
				"embedding": chunk.get("embedding"),
				"metadata": {
					**(metadata or {}),
					**build_chunk_metadata(
						file=file_data,
						parsed=parsed,
						chunk=chunk,
						collection_name=collection_name,
						source_id=source_id,
						metadata=metadata,
					),
				},
			}
		)

	stored = store_chunk_embeddings(
		payload,
		{
			"collectionName": collection_name,
			"sourceId": source_id,
			"metadata": metadata or {},
		},
	)
	logger.info("ingest_parsed_document stored collection_name=%s storedCount=%s", stored.get("collectionName"), stored.get("storedCount"))

	return {
		"sourceId": source_id,
		"chunkCount": len(chunks),
		"storedCount": stored["storedCount"],
		"collectionName": stored["collectionName"],
		"ids": stored["ids"],
	}


def ingest_document_text(text: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
	options = options or {}
	return ingest_parsed_document(
		parsed={"text": text},
		file=options.get("file"),
		collection_name=options.get("collectionName"),
		chunk_options=options.get("chunkOptions"),
		embed_options=options.get("embedOptions"),
		metadata=options.get("metadata"),
	)


def ingest_pdf_file(file_path: str | Path, options: dict[str, Any] | None = None) -> dict[str, Any]:
	options = options or {}
	parsed = extract_text_from_pdf(file_path)
	file_info = {
		"filename": Path(file_path).name,
		"originalname": Path(file_path).name,
		"mimetype": "application/pdf",
	}
	return ingest_parsed_document(
		parsed=parsed,
		file=file_info,
		collection_name=options.get("collectionName"),
		chunk_options=options.get("chunkOptions"),
		embed_options=options.get("embedOptions"),
		metadata=options.get("metadata"),
	)


def ingest_pdf_buffer(buffer: bytes, options: dict[str, Any] | None = None) -> dict[str, Any]:
	options = options or {}
	parsed = extract_text_from_buffer(buffer)
	return ingest_parsed_document(
		parsed=parsed,
		file=options.get("file"),
		collection_name=options.get("collectionName"),
		chunk_options=options.get("chunkOptions"),
		embed_options=options.get("embedOptions"),
		metadata=options.get("metadata"),
	)


__all__ = [
	"build_source_id",
	"build_chunk_metadata",
	"ingest_parsed_document",
	"ingest_document_text",
	"ingest_pdf_file",
	"ingest_pdf_buffer",
]
