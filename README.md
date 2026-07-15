# Agente IA RAG: Azure SQL + Container Apps + ACR + GitHub Actions

Este repositorio contiene la implementación de un **Agente RAG (Retrieval-Augmented Generation)** de nivel empresarial diseñado para ejecutarse en entornos contenedorizados y desplegarse automáticamente en la nube de Microsoft Azure. 

La aplicación está construida sobre **FastAPI (Python)** y utiliza **Azure SQL Database** como almacén de conocimiento vectorial local para realizar búsquedas de similitud semántica.

---

## 📋 Tabla de Contenidos
1. [Características Principales](#-características-principales)
2. [Arquitectura de la Solución](#-arquitectura-de-la-solución)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Flujo Recomendado de Configuración y Desarrollo](#-flujo-recomendado-de-configuración-y-desarrollo)
5. [Endpoints de la API](#-endpoints-de-la-api)
6. [Configuración de Variables de Entorno](#-configuración-de-variables-de-entorno)
7. [Despliegue y CI/CD con GitHub Actions](#-despliegue-y-cicd-con-github-actions)
8. [Checklist de Diagnóstico Rápido y Evidencias](#-checklist-de-diagnóstico-rápido-y-evidencias)

---

## ✨ Características Principales
*   **API Asíncrona de Alto Rendimiento**: Implementada con FastAPI y Uvicorn.
*   **Almacenamiento Vectorial en SQL**: Gestión y persistencia de fragmentos de texto y embeddings en Azure SQL Database.
*   **ODBC Dinámico**: Conexión a base de datos robusta en [db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/db.py) que detecta y utiliza de forma adaptativa el controlador ODBC adecuado (`ODBC Driver 17` localmente en Windows u `ODBC Driver 18` dentro del contenedor Docker).
*   **Proveedor Dual de IA (Demo/OpenAI)**: Soporta ejecución simulada local (sin costes de API de OpenAI) y ejecución real utilizando la API oficial de OpenAI (`LLM_PROVIDER=openai`).
*   **CI/CD de Extremo a Extremo**: Pipeline de automatización completo implementado en GitHub Actions que valida, compila, almacena en ACR, despliega en Azure Container Apps y verifica el estado de salud de la nube de forma automatizada.

---

## 🏗️ Arquitectura de la Solución

El flujo semántico y operativo del Agente RAG funciona de la siguiente manera:

```
[Cliente / API Request] ---> [FastAPI: /ask]
                                  |
                                  +---> [Calcular Embedding de Pregunta]
                                  |
                                  +---> [Consulta Similitud Coseno (Azure SQL)]
                                  |
                                  +---> [Recuperar Top-K Contextos Relevantes]
                                  |
                                  +---> [Enviar Prompt Contextualizado a OpenAI / Demo]
                                  |
[Cliente <--- Respuesta RAG] <----+
```

---

## 📂 Estructura del Proyecto

*   **[api.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/api.py)**: Define los endpoints REST públicos expuestos mediante FastAPI.
*   **[agent.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/agent.py)**: Orquesta el flujo RAG (recuperación de contexto de SQL y envío al modelo generativo).
*   **[db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/db.py)**: Contiene la lógica de conexión contra la base de datos Azure SQL y creación de tablas vectoriales.
*   **[ai_provider.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/ai_provider.py)**: Abstrae la llamada al modelo de embeddings y LLM (OpenAI o Mock).
*   **[settings.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/settings.py)**: Carga y mapea las variables de entorno de forma segura usando Pydantic/Dataclasses.
*   **[init_db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/init_db.py)**: Script auxiliar para crear y poblar la base de datos con conocimiento semilla inicial.
*   **[Dockerfile](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/Dockerfile)**: Especificación de compilación del contenedor bajo una imagen ligera `python:3.11-slim` que instala las dependencias ODBC necesarias para Linux.
*   **[docker-compose.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/docker-compose.yml)**: Define el servicio local mapeando el puerto `8080:8000` para evitar colisiones en la máquina host.
*   **[.github/workflows/deploy-aca.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.github/workflows/deploy-aca.yml)**: Workflow de integración y despliegue continuo (CI/CD) para Azure Container Apps.

---

## 🚀 Flujo Recomendado de Configuración y Desarrollo

Sigue este flujo paso a paso para inicializar el proyecto en local y llevarlo a Azure:

### Fase 1: Base de Datos en Azure
1. Crea una instancia de **Azure SQL Database** en tu grupo de recursos.
2. Configura el **Firewall** de Azure SQL para permitir la conexión de tu IP local y activa la opción *"Permitir que los servicios de Azure accedan a este servidor"*.

### Fase 2: Configuración del Entorno Local
1. Clona el repositorio en tu máquina de desarrollo.
2. Copia el archivo de configuración de ejemplo para crear tu entorno local:
   ```bash
   cp .env.example .env
   ```
3. Configura en el archivo `.env` los datos reales de conexión en `AZURE_SQL_CONNECTION_STRING` y tu key de OpenAI si deseas usar llamadas de IA reales.

### Fase 3: Construcción e Inicialización con Docker
1. Compila la imagen local:
   ```bash
   docker compose build
   ```
2. Ejecuta el inicializador de base de datos dentro del contenedor para crear la tabla de conocimiento e inyectar el contenido semilla inicial:
   ```bash
   docker compose run --rm agent python init_db.py
   ```
3. Levanta el servidor en segundo plano:
   ```bash
   docker compose up -d
   ```

### Fase 4: Validaciones Locales
1. Entra en tu navegador a: **[http://localhost:8080/health](http://localhost:8080/health)** para comprobar el estado de conexión de la base de datos (debe responder `connected`).
2. Entra en **[http://localhost:8080/docs](http://localhost:8080/docs)** para acceder al Swagger interactivo y realizar consultas de prueba.

---

## 📡 Endpoints de la API

La API expone los siguientes endpoints REST interactivos:

| Método | Endpoint | Descripción | Parámetros / Cuerpo |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Información de estado básica del agente. | Ninguno |
| **GET** | `/health` | Verifica la salud de la API y el estado de la conexión a la Base de Datos. | Ninguno |
| **GET** | `/knowledge` | Devuelve el catálogo de documentos ingestados. | Ninguno |
| **POST** | `/ingest` | Ingesta un nuevo fragmento y computa su vector de embedding. | `{ "title": "...", "content": "...", "source": "..." }` |
| **POST** | `/ask` | Consulta semántica al agente RAG. Recupera contexto y genera respuesta. | `{ "question": "..." }` |

---

## ⚙️ Configuración de Variables de Entorno

La aplicación lee los siguientes parámetros del archivo `.env` (local) o de la configuración del entorno en la nube:

*   **`APP_NAME`**: Nombre identificativo del agente (por defecto `Agente RAG Entregable 5`).
*   **`APP_ENV`**: Define el entorno operativo (`local` o `azure`).
*   **`AZURE_SQL_CONNECTION_STRING`**: Cadena de conexión JDBC/ODBC completa para la base de datos Azure SQL.
*   **`LLM_PROVIDER`**: Define el motor de inteligencia artificial. Usa `demo` para simulación local sin coste, o `openai` para llamadas reales a modelos generativos.
*   **`OPENAI_API_KEY`**: Requerido si `LLM_PROVIDER=openai`.
*   **`EMBEDDING_MODEL`**: Modelo para indexación vectorial (por defecto `text-embedding-3-small`).
*   **`CHAT_MODEL`**: Modelo generativo LLM (por defecto `gpt-4.1-mini`).
*   **`TOP_K`**: Cantidad de fragmentos de conocimiento recuperados por consulta (por defecto `3`).

---

## 🐙 Despliegue y CI/CD con GitHub Actions

El pipeline automatizado en [.github/workflows/deploy-aca.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.github/workflows/deploy-aca.yml) está diseñado para ejecutarse automáticamente en cada `git push` a la rama `main`. 

### Secretos del Repositorio Necesarios
Para activar el pipeline, ve a los ajustes de tu repositorio en GitHub (**Settings -> Secrets and variables -> Actions**) y registra las siguientes credenciales como secrets:

*   `RESOURCE_GROUP`: Grupo de recursos de Azure.
*   `CONTAINER_APP_NAME`: Nombre del recurso de la Azure Container App.
*   `ACR_NAME`: Nombre del registro de contenedores (ej. `acragent5xxx`).
*   `ACR_LOGIN_SERVER`: Dirección del login server (ej. `acragent5xxx.azurecr.io`).
*   `ACR_USERNAME`: Usuario del administrador del ACR.
*   `ACR_PASSWORD`: Contraseña del administrador del ACR.
*   `IMAGE_REPOSITORY`: Nombre asignado al repositorio de la imagen (ej. `rag-agent-api`).
*   `AZURE_SUBSCRIPTION_ID`: ID de suscripción de Azure.
*   `AZURE_BEARER_TOKEN`: Token de autenticación de Azure CLI (`az account get-access-token`).
*   `AZURE_SQL_CONNECTION_STRING`: Cadena de conexión real de la base de datos de producción (utilizando `Driver={ODBC Driver 18 for SQL Server}`).
*   `OPENAI_API_KEY`: Clave de API de OpenAI.

---

## 🔎 Checklist de Diagnóstico Rápido y Evidencias

Antes de dar el entregable por completado, valida cada uno de estos puntos:

- [x] **Base de Datos**: La tabla `dbo.knowledge_chunks` existe en tu instancia de Azure SQL y contiene filas cargadas sembradas por `init_db.py`.
- [x] **Seguridad**: El archivo de entorno `.env` está configurado con valores reales locales y se encuentra debidamente ignorado en tu archivo [.gitignore](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.gitignore).
- [x] **Servidor Local**: Ejecutar `docker compose up` levanta el servidor Uvicorn de forma exitosa en el puerto mapeado en la máquina host.
- [x] **Health Check Local**: El endpoint `http://localhost:8880/health` responde exitosamente retornando `"database": "connected"`.
- [x] **Registro en ACR**: La imagen Docker ha sido compilada y cargada con éxito en tu Azure Container Registry privado con tags identificativos del Commit SHA de Git.
- [x] **Container Apps**: La ACA se encuentra en estado *Running*, configurada con ingress externo en el puerto `8000` y con `AZURE_SQL_CONNECTION_STRING` mapeado como un secreto protegido de Azure (`secretref`).
- [x] **CI/CD Verde**: El flujo de GitHub Actions corre de principio a fin de manera correcta y despliega de manera exitosa en Azure.
- [x] **Health Check Cloud**: Entrar a `/health` en la FQDN pública retorna `"status": "ok"` y `"database": "connected"`.
- [x] **Logs en Azure**: Los logs de la Container App muestran el arranque correcto y la recepción de solicitudes HTTP.