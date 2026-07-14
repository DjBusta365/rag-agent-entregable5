import json
from fastapi import FastAPI
from pydantic import BaseModel, Field
from agent import ask_agent
from ai_provider import create_embedding
from db import create_table_if_not_exists, get_connection
from settings import settings

app = FastAPI(
    title="Agente IA RAG - Entregable 5",
    description="API FastAPI desplegable en Azure Container Apps, con Azure SQL como base de conocimiento.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., example="Que papel cumple Azure Container Apps en esta practica?")


class IngestRequest(BaseModel):
    title: str = Field(..., example="Nuevo fragmento")
    content: str = Field(..., example="Texto que se quiere incorporar a la base de conocimiento")
    source: str = Field(default="manual", example="manual")


@app.get("/")
def home():
    return {
        "message": "Agente IA RAG del Entregable 5 funcionando",
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health",
        "ask": "/ask",
    }


@app.get("/health")
def health():
    try:
        create_table_if_not_exists()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.knowledge_chunks")
        total_chunks = cursor.fetchone()[0]
        conn.close()
        return {
            "status": "ok",
            "database": "connected",
            "knowledge_chunks": total_chunks,
            "llm_provider": settings.llm_provider,
        }
    except Exception as error:
        return {
            "status": "error",
            "database": "not connected",
            "detail": str(error),
        }


@app.get("/knowledge")
def list_knowledge():
    create_table_if_not_exists()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, source, created_at
        FROM dbo.knowledge_chunks
        ORDER BY id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row.id, "title": row.title, "source": row.source, "created_at": str(row.created_at)}
        for row in rows
    ]


@app.post("/ask")
def ask(request: AskRequest):
    return ask_agent(request.question)


@app.post("/ingest")
def ingest(request: IngestRequest):
    create_table_if_not_exists()
    embedding = create_embedding(request.content)
    embedding_model = settings.embedding_model if settings.llm_provider == "openai" else "demo-hash-embedding"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dbo.knowledge_chunks (title, source, content, embedding, embedding_model)
        VALUES (?, ?, ?, ?, ?)
        """,
        request.title,
        request.source,
        request.content,
        json.dumps(embedding),
        embedding_model,
    )
    conn.commit()
    conn.close()
    return {"status": "inserted", "title": request.title, "source": request.source}
