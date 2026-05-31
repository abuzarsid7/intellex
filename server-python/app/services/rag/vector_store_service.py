
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import logging
from pathlib import Path
from typing import Any, Iterable

import chromadb

from app.core.config import settings


DEFAULT_COLLECTION_NAME = settings.CHROMA_COLLECTION_NAME

logger = logging.getLogger("intellex.rag.vector_store")


def _normalize_metadata(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
	metadata = metadata or {}
	normalized: dict[str, Any] = {}
	for key, value in metadata.items():
		if isinstance(value, bool):
			normalized[key] = value
		elif isinstance(value, (int, float, str)) and value != "":
			normalized[key] = value
	return normalized


def _build_vector_store_id(source_id: str | None = None, chunk_index: int | None = None) -> str:
	return f"{source_id or 'document'}:{chunk_index if chunk_index is not None else 0}"


@lru_cache(maxsize=1)
def get_chroma_client():
	"""Return a cached local Chroma persistent client."""
	chroma_path = Path(settings.CHROMA_PATH)
	chroma_path.mkdir(parents=True, exist_ok=True)
	logger.info("Using local Chroma persistent path: %s", chroma_path)
	return chromadb.PersistentClient(path=str(chroma_path))


_collection_cache: dict[str, Any] = {}


def get_collection(collection_name: str = DEFAULT_COLLECTION_NAME):
	logger.info("get_collection collection_name=%s", collection_name)
	if collection_name in _collection_cache:
		return _collection_cache[collection_name]

	client = get_chroma_client()
	try:
		collection = client.get_or_create_collection(name=collection_name)
	except Exception as exc:
		logging.getLogger("intellex.rag").exception("Failed to get or create Chroma collection '%s': %s", collection_name, exc)
		raise RuntimeError(f"Failed to get or create Chroma collection '{collection_name}': {exc}") from exc
	_collection_cache[collection_name] = collection
	return collection


def _coerce_chunks(chunks: Iterable[dict[str, Any]] | None) -> list[dict[str, Any]]:
	if not chunks:
		return []
	return [chunk for chunk in chunks if chunk]


def _normalize_where(where: dict[str, Any] | None = None) -> dict[str, Any] | None:
	if not where:
		return None

	if any(str(key).startswith("$") for key in where.keys()):
		return where

	clauses = [{key: value} for key, value in where.items() if value is not None]
	if not clauses:
		return None
	if len(clauses) == 1:
		return clauses[0]
	return {"$and": clauses}


def store_chunk_embeddings(chunks: Iterable[dict[str, Any]] | None = None, options: dict[str, Any] | None = None) -> dict[str, Any]:
	options = options or {}
	collection_name = options.get("collectionName") or DEFAULT_COLLECTION_NAME
	logger.info("store_chunk_embeddings collection_name=%s sourceId=%s", collection_name, options.get("sourceId"))
	normalized_chunks = _coerce_chunks(chunks)

	if not normalized_chunks:
		return {"collectionName": collection_name, "storedCount": 0, "ids": []}

	documents: list[str] = []
	embeddings: list[list[float]] = []
	metadatas: list[dict[str, Any]] = []
	ids: list[str] = []

	for index, chunk in enumerate(normalized_chunks):
		text = str(chunk.get("text") or "").strip()
		embedding = chunk.get("embedding") or []

		if not text or not isinstance(embedding, list) or len(embedding) == 0:
			continue

		chunk_index = chunk.get("index") if isinstance(chunk.get("index"), int) else index
		source_id = chunk.get("sourceId") or (chunk.get("metadata") or {}).get("sourceId") or options.get("sourceId")

		documents.append(text)
		embeddings.append(embedding)
		metadatas.append(
			_normalize_metadata(
				{
					**(options.get("metadata") or {}),
					**(chunk.get("metadata") or {}),
					"chunkIndex": chunk_index,
					"storedAt": datetime.now(timezone.utc).isoformat(),
				}
			)
		)
		ids.append(chunk.get("id") or _build_vector_store_id(source_id, chunk_index))

	if not documents:
		return {"collectionName": collection_name, "storedCount": 0, "ids": []}

	collection = get_collection(collection_name)
	try:
		collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
	except Exception as exc:
		logging.getLogger("intellex.rag").exception("Failed to upsert embeddings into collection '%s': %s", collection_name, exc)
		raise RuntimeError(f"Failed to upsert embeddings into collection '{collection_name}': {exc}") from exc

	return {"collectionName": collection_name, "storedCount": len(ids), "ids": ids}


def query_similar_chunks(
	*,
	collection_name: str = DEFAULT_COLLECTION_NAME,
	query_embedding: list[float] | None = None,
	n_results: int = 5,
	where: dict[str, Any] | None = None,
	include: list[str] | None = None,
) -> dict[str, Any]:
	if not isinstance(query_embedding, list) or len(query_embedding) == 0:
		raise ValueError("A query embedding is required to search Chroma")

	where = _normalize_where(where)
	logger.info("query_similar_chunks collection_name=%s where=%s n_results=%s", collection_name, where, n_results)

	collection = get_collection(collection_name)
	return collection.query(
		query_embeddings=[query_embedding],
		n_results=n_results,
		where=where,
		include=include or ["documents", "metadatas", "distances"],
	)


__all__ = [
	"DEFAULT_COLLECTION_NAME",
	"get_chroma_client",
	"get_collection",
	"store_chunk_embeddings",
	"query_similar_chunks",
]
