# Entregable 5 - Agente RAG con Azure SQL + ACA + ACR + Azure DevOps

Este proyecto acompaña a la guía detallada. Implementa una API FastAPI con endpoints `/`, `/health`, `/knowledge`, `/ask` e `/ingest`.

## Flujo recomendado

1. Crear Azure SQL y configurar firewall.
2. Crear `.env` desde `.env.example`.
3. Ejecutar `docker compose build`.
4. Ejecutar `docker compose run --rm agent python init_db.py`.
5. Ejecutar `docker compose up -d`.
6. Validar `http://localhost:8000/health` y `http://localhost:8000/docs`.
7. Crear ACR y hacer push manual de prueba.
8. Crear ACA y validar FQDN.
9. Configurar Azure DevOps service connections, variable group y pipeline.

## Variables necesarias

- `AZURE_SQL_CONNECTION_STRING`: secreto.
- `OPENAI_API_KEY`: secreto opcional si `LLM_PROVIDER=openai`.
- `LLM_PROVIDER`: `demo` por defecto.
- `TOP_K`: número de fuentes recuperadas.

## Evidencias

Capturas de Azure Repos, Docker local, Azure SQL, ACR, ACA, pipeline, `/health`, `/ask` y logs.
