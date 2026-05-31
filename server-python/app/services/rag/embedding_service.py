
from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable, Sequence

from sentence_transformers import SentenceTransformer

from app.services.rag.chunk_service import chunk_text


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=4)
def _get_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
	return SentenceTransformer(model_name)


def _to_list(vector: Any) -> list[float]:
	if vector is None:
		return []

	if hasattr(vector, "tolist"):
		converted = vector.tolist()
		if isinstance(converted, list):
			return converted

	if isinstance(vector, (list, tuple)):
		if vector and isinstance(vector[0], (list, tuple)):
			flattened: list[float] = []
			for item in vector:
				flattened.extend(_to_list(item))
			return flattened
		return list(vector)

	return [float(vector)]


def embed_text(text: str, options: dict[str, Any] | None = None) -> list[float]:
	"""Embed a single text string using a sentence-transformers model."""
	options = options or {}
	model_name = options.get("model") or DEFAULT_MODEL
	pooling = options.get("pooling", "mean")
	normalize = options.get("normalize", True)

	# SentenceTransformer returns a dense vector directly.
	# Pooling is model-internal; we keep the parameter for compatibility.
	_ = pooling
	model = _get_model(model_name)
	embedding = model.encode(
		text or "",
		normalize_embeddings=normalize,
		convert_to_numpy=True,
	)
	return _to_list(embedding)


def embed_chunks(chunks: Sequence[str] | Iterable[str] | str | None = None, options: dict[str, Any] | None = None) -> list[dict[str, Any]]:
	"""Embed a list of text chunks and return vectors plus chunk metadata."""
	options = options or {}
	model_name = options.get("model") or DEFAULT_MODEL
	normalize = options.get("normalize", True)
	model = _get_model(model_name)

	if chunks is None:
		valid_chunks = [""]
	elif isinstance(chunks, str):
		valid_chunks = [chunks]
	else:
		valid_chunks = [str(chunk or "") for chunk in chunks if chunk]

	results: list[dict[str, Any]] = []
	for index, chunk in enumerate(valid_chunks):
		embedding = model.encode(
			chunk,
			normalize_embeddings=normalize,
			convert_to_numpy=True,
		)
		results.append(
			{
				"index": index,
				"text": chunk,
				"embedding": _to_list(embedding),
				"chunkTokens": max(1, -(-len(chunk) // 4)),
			}
		)

	return results


def chunk_and_embed_text(
	text: str | None,
	chunk_options: dict[str, Any] | None = None,
	embed_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
	"""Chunk a raw document string and embed each chunk."""
	chunks = chunk_text(text or "", chunk_options)
	embeddings = embed_chunks(chunks, embed_options)

	return {
		"chunks": chunks,
		"embeddings": embeddings,
	}


__all__ = ["DEFAULT_MODEL", "embed_text", "embed_chunks", "chunk_and_embed_text"]
