import json
from typing import Any
import numpy as np
from ai_provider import create_embedding, generate_answer
from db import get_connection
from settings import settings


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def retrieve_context(question: str, top_k: int | None = None) -> list[dict[str, Any]]:
    question_embedding = create_embedding(question)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, source, content, embedding
        FROM dbo.knowledge_chunks
        """
    )
    rows = cursor.fetchall()
    conn.close()

    scored_chunks = []
    for row in rows:
        stored_embedding = json.loads(row.embedding)
        score = cosine_similarity(question_embedding, stored_embedding)
        scored_chunks.append(
            {
                "id": row.id,
                "title": row.title,
                "source": row.source,
                "content": row.content,
                "score": score,
            }
        )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return scored_chunks[: (top_k or settings.top_k)]


def ask_agent(question: str) -> dict[str, Any]:
    chunks = retrieve_context(question)
    answer = generate_answer(question, chunks)
    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "id": chunk["id"],
                "title": chunk["title"],
                "source": chunk["source"],
                "score": round(chunk["score"], 3),
            }
            for chunk in chunks
        ],
    }
