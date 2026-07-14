import json
from db import create_table_if_not_exists, get_connection
from ai_provider import create_embedding
from settings import settings

DOCUMENTS = [
    {
        "title": "Que es RAG",
        "source": "material_docente",
        "content": "RAG significa Retrieval-Augmented Generation. Es una arquitectura que combina recuperacion de informacion con generacion de texto. Primero busca informacion relevante en una base de conocimiento y despues usa esa informacion como contexto para generar una respuesta.",
    },
    {
        "title": "Papel de Azure SQL en RAG",
        "source": "material_docente",
        "content": "Azure SQL puede actuar como base de conocimiento para una solucion RAG. En esta practica almacena fragmentos de texto, metadatos y embeddings para que el agente busque informacion antes de generar la respuesta.",
    },
    {
        "title": "Azure Container Apps",
        "source": "material_docente",
        "content": "Azure Container Apps permite ejecutar aplicaciones contenerizadas sin administrar servidores. En esta practica aloja la API FastAPI del agente RAG y expone un endpoint publico con ingress externo.",
    },
    {
        "title": "Azure Container Registry",
        "source": "material_docente",
        "content": "Azure Container Registry almacena imagenes Docker privadas. El pipeline de Azure DevOps construye la imagen del backend y la publica en ACR antes de desplegarla en Azure Container Apps.",
    },
    {
        "title": "Azure DevOps CI CD",
        "source": "material_docente",
        "content": "Azure DevOps automatiza el ciclo de entrega. El pipeline instala dependencias, ejecuta pruebas, construye la imagen Docker, la sube a Azure Container Registry y actualiza la Container App.",
    },
    {
        "title": "Buenas practicas de secretos",
        "source": "material_docente",
        "content": "Las credenciales no deben escribirse en el codigo ni subirse al repositorio. Deben gestionarse mediante variables secretas de Azure DevOps, secretos de Azure Container Apps o Azure Key Vault en escenarios profesionales.",
    },
]


def table_has_data() -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.knowledge_chunks")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def insert_documents() -> None:
    if table_has_data():
        print("La tabla ya contiene datos. No se insertan duplicados.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    for doc in DOCUMENTS:
        embedding = create_embedding(doc["content"])
        cursor.execute(
            """
            INSERT INTO dbo.knowledge_chunks (title, source, content, embedding, embedding_model)
            VALUES (?, ?, ?, ?, ?)
            """,
            doc["title"],
            doc["source"],
            doc["content"],
            json.dumps(embedding),
            settings.embedding_model if settings.llm_provider == "openai" else "demo-hash-embedding",
        )
    conn.commit()
    conn.close()
    print("Base de conocimiento inicial cargada correctamente.")


if __name__ == "__main__":
    create_table_if_not_exists()
    insert_documents()
