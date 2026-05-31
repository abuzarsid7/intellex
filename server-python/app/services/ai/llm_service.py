
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from groq import Groq


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _build_offline_response(user_message: str, document_context: str | None = None) -> str:
	message = str(user_message or "").strip()
	context = str(document_context or "").strip()
	if context:
		return (
			"I couldn't reach the chat model, but I found document context related to your question. "
			"Please check the uploaded document or try again later.\n\n"
			f"Context:\n{context}"
		)

	return (
		"I couldn't reach the chat model right now, so I can't generate a full answer. "
		"Please try again later or check that GROQ_API_KEY is configured."
	)


def _build_rag_system_prompt(document_context: str) -> str:
	return "\n".join(
		[
			"You are a retrieval-grounded assistant.",
			"Use the document context below as the primary and preferred source of truth.",
			"Answer only from the context when it is sufficient.",
			"If the context does not contain the answer, say that the uploaded documents do not include enough information.",
			"Do not answer from general knowledge unless the user explicitly asks for general advice unrelated to the documents.",
			"When the answer comes from the context, mention the relevant document details naturally in your response.",
			"",
			"Document context:",
			document_context,
		]
	)


@lru_cache(maxsize=1)
def _get_groq_client() -> Groq:
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise ValueError("GROQ_API_KEY is not configured")

	return Groq(api_key=api_key)


def _normalize_history(history: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
	if not history:
		return []

	normalized: list[dict[str, str]] = []
	for message in history:
		role = str(message.get("role") or "").strip()
		content = str(message.get("content") or "").strip()
		if role and content:
			normalized.append({"role": role, "content": content})

	return normalized


def _generate_response(
	*,
	user_message: str,
	history: list[dict[str, Any]] | None = None,
	system_prompt: str = DEFAULT_SYSTEM_PROMPT,
	model: str | None = None,
) -> str:
	groq_client = _get_groq_client()
	messages = [
		{"role": "system", "content": system_prompt},
		*_normalize_history(history),
		{"role": "user", "content": str(user_message or "")},
	]

	response = groq_client.chat.completions.create(
		model=model or DEFAULT_MODEL,
		messages=messages,
		temperature=0.2,
		max_tokens=2000,
	)

	text = response.choices[0].message.content if response.choices else None
	if not text:
		raise ValueError("No response from Groq")

	return text


def generate_ai_response(
	user_message: str,
	history: list[dict[str, Any]] | None = None,
	model: str | None = None,
) -> str:
	"""Generate a standard chat response using the Groq API."""
	try:
		return _generate_response(
			user_message=user_message,
			history=history,
			system_prompt=DEFAULT_SYSTEM_PROMPT,
			model=model,
		)
	except ValueError as exc:
		if "GROQ_API_KEY is not configured" in str(exc):
			return _build_offline_response(user_message)
		raise
	except Exception as exc:
		return _build_offline_response(user_message)


def generate_rag_response(
	user_message: str,
	document_context: str | None,
	history: list[dict[str, Any]] | None = None,
	model: str | None = None,
) -> str:
	"""Generate a context-grounded response using the Groq API."""
	try:
		system_prompt = (
			_build_rag_system_prompt(document_context.strip())
			if document_context and document_context.strip()
			else DEFAULT_SYSTEM_PROMPT
		)
		return _generate_response(
			user_message=user_message,
			history=history,
			system_prompt=system_prompt,
			model=model,
		)
	except ValueError as exc:
		if "GROQ_API_KEY is not configured" in str(exc):
			return _build_offline_response(user_message, document_context)
		raise
	except Exception as exc:
		return _build_offline_response(user_message, document_context)


__all__ = [
	"DEFAULT_SYSTEM_PROMPT",
	"DEFAULT_MODEL",
	"generate_ai_response",
	"generate_rag_response",
]
