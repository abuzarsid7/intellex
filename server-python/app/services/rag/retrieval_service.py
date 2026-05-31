
from __future__ import annotations

import logging
from typing import Any

from app.services.rag.embedding_service import embed_text
from app.services.rag.vector_store_service import query_similar_chunks


DEFAULT_RESULT_COUNT = 4


logger = logging.getLogger("intellex.rag.retrieval")


def retrieve_relevant_chunks(query: str | None, options: dict[str, Any] | None = None) -> list[dict[str, Any]]:
	options = options or {}
	user_query = str(query or "").strip()
	if not user_query:
		return []

	try:
		query_embedding = embed_text(user_query, options.get("embedOptions") or {})
	except Exception:
		logger.exception("Failed to embed retrieval query")
		return []
	logger.info("retrieve_relevant_chunks query=%s collectionName=%s where=%s", user_query, options.get("collectionName") or options.get("collection_name"), options.get("where"))
	try:
		results = query_similar_chunks(
			collection_name=options.get("collectionName") or options.get("collection_name"),
			query_embedding=query_embedding,
			n_results=options.get("nResults") or options.get("n_results") or DEFAULT_RESULT_COUNT,
			where=options.get("where"),
		)
	except Exception:
		logger.exception("Failed to query Chroma for retrieval")
		return []

	documents = (results.get("documents") or [[]])[0]
	metadatas = (results.get("metadatas") or [[]])[0]
	distances = (results.get("distances") or [[]])[0]

	chunks: list[dict[str, Any]] = []
	for index, document in enumerate(documents):
		text = str(document or "").strip()
		if not text:
			continue

		chunks.append(
			{
				"document": text,
				"metadata": metadatas[index] if index < len(metadatas) else {},
				"distance": distances[index] if index < len(distances) else None,
			}
		)

	if chunks or not options.get("allowFallback", True) or options.get("where"):
		return chunks

	logger.info("retrieve_relevant_chunks fallback to default collection for query=%s", user_query)
	try:
		fallback_results = query_similar_chunks(
			collection_name=options.get("collectionName") or options.get("collection_name"),
			query_embedding=query_embedding,
			n_results=options.get("nResults") or options.get("n_results") or DEFAULT_RESULT_COUNT,
		)
	except Exception:
		logger.exception("Failed to query Chroma fallback collection")
		return []
	fallback_documents = (fallback_results.get("documents") or [[]])[0]
	fallback_metadatas = (fallback_results.get("metadatas") or [[]])[0]
	fallback_distances = (fallback_results.get("distances") or [[]])[0]

	for index, document in enumerate(fallback_documents):
		text = str(document or "").strip()
		if not text:
			continue

		chunks.append(
			{
				"document": text,
				"metadata": fallback_metadatas[index] if index < len(fallback_metadatas) else {},
				"distance": fallback_distances[index] if index < len(fallback_distances) else None,
			}
		)

	return chunks


def build_document_context(chunks: list[dict[str, Any]] | None = None) -> str:
	if not chunks:
		return ""

	sections: list[str] = []
	for index, chunk in enumerate(chunks):
		metadata = chunk.get("metadata") or {}
		title = metadata.get("originalName") or metadata.get("fileName") or metadata.get("file_id") or f"Document {index + 1}"
		page_info = f"Pages: {metadata['totalPages']}" if metadata.get("totalPages") else None
		score_info = (
			f"Distance: {float(chunk['distance']):.4f}"
			if isinstance(chunk.get("distance"), (int, float))
			else None
		)

		parts = [f"[{index + 1}] {title}", page_info, score_info, chunk.get("document") or ""]
		sections.append("\n".join(part for part in parts if part))

	return "\n\n".join(sections)


def retrieve_document_context(query: str | None, options: dict[str, Any] | None = None) -> dict[str, Any]:
	chunks = retrieve_relevant_chunks(query, options)
	return {
		"chunks": chunks,
		"context": build_document_context(chunks),
	}


__all__ = ["DEFAULT_RESULT_COUNT", "retrieve_relevant_chunks", "build_document_context", "retrieve_document_context"]
