import hashlib
import math
from typing import Iterable

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - solo si la libreria no esta instalada
    OpenAI = None

from settings import settings


VECTOR_SIZE = 128


def _tokenize(text: str) -> list[str]:
    return [token.strip(".,;:!?()[]{}\"'¿¡").lower() for token in text.split() if token.strip()]


def _demo_embedding(text: str) -> list[float]:
    """
    Embedding determinista para modo docente sin coste.
    No sustituye a embeddings reales, pero permite probar el flujo RAG completo.
    """
    vector = [0.0] * VECTOR_SIZE
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % VECTOR_SIZE
        sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _openai_client():
    if not settings.openai_api_key:
        return None
    if OpenAI is None:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def create_embedding(text: str) -> list[float]:
    """Crea un embedding con OpenAI si hay clave; si no, usa modo demo."""
    if settings.llm_provider == "openai" and settings.openai_api_key:
        client = _openai_client()
        if client is not None:
            response = client.embeddings.create(model=settings.embedding_model, input=text)
            return response.data[0].embedding
    return _demo_embedding(text)


def generate_answer(question: str, chunks: Iterable[dict]) -> str:
    """Genera la respuesta final del agente."""
    chunks = list(chunks)
    if settings.llm_provider == "openai" and settings.openai_api_key:
        client = _openai_client()
        if client is not None:
            context = "\n\n".join(
                f"[Fuente: {chunk['title']} | Score: {chunk['score']:.3f}]\n{chunk['content']}"
                for chunk in chunks
            )
            prompt = f"""
Eres un agente de IA docente y riguroso.
Responde usando principalmente el CONTEXTO recuperado desde la base SQL.
Si el contexto no contiene informacion suficiente, dilo claramente.
No inventes datos que no esten apoyados por el contexto.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:
"""
            response = client.chat.completions.create(
                model=settings.chat_model,
                messages=[
                    {"role": "system", "content": "Eres un agente RAG claro, riguroso y docente."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content

    if not chunks:
        return (
            "No he encontrado informacion suficiente en la base de conocimiento. "
            "Carga documentos con /ingest o ejecuta init_db.py."
        )

    top = chunks[0]
    return (
        "Respuesta generada en modo demo, sin llamada a un LLM externo. "
        f"Para la pregunta '{question}', el fragmento mas relevante es '{top['title']}'. "
        f"Resumen basado en la fuente recuperada: {top['content'].strip()}"
    )
