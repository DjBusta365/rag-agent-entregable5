# INFORME TÉCNICO: DESPLIEGUE AUTOMATIZADO DE AGENTE RAG EN NUBE AZURE
**Asignatura:** Computación en la Nube y Automatización de Despliegues  
**Entregable:** Actividad 5  
**Autor:** Daniel (Universidad Internacional de La Rioja - UNIR)  
**Fecha:** 15 de Julio de 2026  

---

### 🌐 ENLACES DE ACCESO PÚBLICO
*   **Repositorio GitHub**: [https://github.com/DjBusta365/rag-agent-entregable5](https://github.com/DjBusta365/rag-agent-entregable5)
*   **API Web Desplegada (Swagger)**: [https://cae-entregable5-rag.salmoncliff-a6a6c436.francecentral.azurecontainerapps.io/docs](https://cae-entregable5-rag.salmoncliff-a6a6c436.francecentral.azurecontainerapps.io/docs)

---

## 1. OBJETIVO
El objetivo de este proyecto es diseñar, implementar y desplegar un **Agente RAG (Retrieval-Augmented Generation)** escalable y de grado de producción en la nube de Microsoft Azure. 

La solución expone una API REST (FastAPI) contenida en Docker que permite a los usuarios:
1. Ingestar y almacenar fragmentos de conocimiento con sus respectivos embeddings en una base de datos relacional orientada a la nube (**Azure SQL Database**).
2. Consultar al agente a través del endpoint `/ask`. El sistema recupera los fragmentos semánticamente más relevantes mediante similitud del coseno ejecutada localmente en la base de datos y construye una respuesta precisa, ya sea simulada (modo `demo`) o mediante integración con modelos generativos (modo `openai`).

Todo el proceso de pruebas, construcción de imágenes, almacenamiento en registro de contenedores (**Azure Container Registry - ACR**), actualización del servicio en **Azure Container Apps (ACA)** y validación final de endpoints ha sido automatizado de extremo a extremo mediante un pipeline CI/CD en **GitHub Actions**.

---

## 2. ARQUITECTURA DE LA SOLUCIÓN
A continuación se detalla la topología de la solución y el flujo de integración y despliegue continuo (CI/CD):

```mermaid
graph TD
    Dev[Desarrollador (Git Push)] -->|1. Commit & Push| GitHub[GitHub Repositorio]
    GitHub -->|2. Dispara CI/CD| GHA[GitHub Actions Runner]
    
    subgraph GitHub Runner
        GHA -->|3. Pruebas Unitarias| Pytest[Pytest]
        GHA -->|4. Construcción Docker| DockerBuild[Docker Build]
    end
    
    DockerBuild -->|5. Push Imagen| ACR[Azure Container Registry]
    GHA -->|6. Actualizar ACA| ACA[Azure Container Apps]
    
    subgraph Microsoft Azure Cloud
        ACR -->|Pull Imagen| ACA
        ACA -->|7. Conexión de Datos| SQL[Azure SQL Database]
        ACA -->|8. API Embeddings| OpenAI[OpenAI API (si aplica)]
    end
    
    Client[Cliente / Navegador] -->|9. Consulta /ask| ACA
```

### Componentes Clave:
*   **Repositorio de Código**: GitHub aloja el código fuente y el workflow de automatización en [.github/workflows/deploy-aca.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.github/workflows/deploy-aca.yml).
*   **Orquestador CI/CD**: GitHub Actions ejecuta los tests locales, construye la imagen optimizada `rag-agent-api` y gestiona la autenticación con Azure.
*   **Azure Container Registry (ACR)**: Almacena de forma privada y segura las imágenes Docker generadas con etiquetas (`tags`) que enlazan directamente con el código fuente (`SHA` del Commit).
*   **Azure Container Apps (ACA)**: Entorno administrado de Kubernetes sin servidor (Serverless) que hospeda la API FastAPI expuesta mediante un Ingress público HTTPS.
*   **Azure SQL Database**: Motor de base de datos relacional en la nube encargado de persistir la tabla de conocimiento y calcular las búsquedas semánticas sobre los vectores de embeddings cargados.

---

## 3. CONFIGURACIÓN Y ESTRUCTURACIÓN (Desarrollo y Estructura del Código)
El proyecto cuenta con una estructura limpia y modular estructurada bajo una arquitectura en capas. Se excluyen del control de versiones los archivos de entorno mediante [.gitignore](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.gitignore):

*   **Modularidad**: La lógica de API ([api.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/api.py)) se separa de la lógica del RAG ([agent.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/agent.py)), los proveedores de IA ([ai_provider.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/ai_provider.py)), los ajustes de configuración ([settings.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/settings.py)) y la base de datos ([db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/db.py)).
*   **Gestión de Entorno**: La configuración del entorno local se realiza mediante el archivo de variables [.env](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.env), el cual está debidamente excluido de Git para evitar fugas de información.
*   **Conexión dinámica ODBC**: La base de datos implementa en [db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/db.py) una detección automática del driver ODBC para SQL Server de manera dinámica (utilizando `ODBC Driver 17` localmente y `ODBC Driver 18` en Docker) permitiendo la portabilidad absoluta del código.

---

## 4. CONTENERIZACIÓN (Dockerfile y Docker Compose)
El backend está definido mediante un archivo `Dockerfile` optimizado y se levanta en conjunto con Docker Compose para desarrollo local rápido.

*   **Dockerfile**: Basado en `python:3.11-slim-bookworm`. Instala las dependencias del sistema necesarias para compilar `pyodbc` e instala de forma segura el driver oficial `msodbcsql18`. Copia los requisitos y el código, exponiendo el puerto `8000`.
*   **Docker Compose**: Define el servicio `agent` cargando de forma automática el archivo local `.env`. Mapea el puerto host `8080:8000` para evitar conflictos en el sistema host local y habilita la recarga automática en desarrollo.
*   **Validación local**: Levantando el stack mediante `docker compose up -d`, la API arranca Uvicorn y expone la documentación Swagger en `/docs`. Permite validar localmente el endpoint `/health` (mostrando conexión exitosa a Azure SQL) y el endpoint `/ask`.

---

## 5. REGISTRO EN AZURE (Azure Container Registry - ACR)
Para el almacenamiento de imágenes de contenedores en la nube de forma segura y privada, se configuró un registro en Azure:

*   **Azure Container Registry**: Se desplegó el ACR con nombre `acragent5XXX` expuesto bajo el login server `acragent5xxx.azurecr.io`.
*   **Autenticación**: Para permitir la subida local e integrada de la imagen, se habilitaron las claves de acceso de administrador en el ACR y se inició sesión en Docker local usando `az acr login`.
*   **Subida e Inmutabilidad**: Se etiquetó la imagen local `rag-agent-api` en minúsculas y se subió mediante `docker push` con el tag del Commit SHA (`v1` / `v1.0.0`) y `latest`. Esto garantiza la inmutabilidad y la trazabilidad del código a producción.

---

## 6. CONFIGURACIÓN Y EJECUCIÓN EN CONTAINER APPS (Despliegue en la Nube)
Para la ejecución sin servidor (Serverless) de la API, se desplegó una Azure Container App (ACA):

*   **Ingress Externo**: Se expuso la Container App de forma pública a través de Internet bajo HTTPS sobre el puerto de destino `8000` (el puerto interno en el que escucha Uvicorn dentro del contenedor).
*   **Gestión de Secretos**: La cadena de conexión a la base de datos de producción (`AZURE_SQL_CONNECTION_STRING`) y la API key de OpenAI se registraron como secretos seguros del servicio ACA (`secrets`). Esto permite mapearlas a variables de entorno dentro del contenedor de forma referenciada (`secretref`), sin que se expongan en texto plano en la configuración del recurso.
*   **Escalado**: La aplicación se aloja en un entorno de Container Apps escalable capaz de auto-escalar a cero instancias cuando no está recibiendo peticiones, reduciendo los costes operativos de infraestructura al mínimo.

---

## 7. PIPELINE CI/CD (Automatización de Pruebas y Despliegue Continuo)
Todo el flujo se automatiza en GitHub Actions a través de [.github/workflows/deploy-aca.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.github/workflows/deploy-aca.yml), ejecutándose en cada push a la rama `main`:

1.  **Ejecución de Pruebas (pytest)**: Levanta un entorno de ejecución temporal de Python 3.11, instala los paquetes de desarrollo y corre los tests unitarios.
2.  **Validación de Configuración**: Verifica que existan archivos críticos (`Dockerfile`, `requirements.txt`) y que los 11 secretos del repositorio estén presentes y correctos en los GitHub Secrets.
3.  **Docker Build and Push**: Inicia sesión en el ACR de Azure, compila la imagen inmutable asociándola al Commit SHA actual de Git y la sube al ACR.
4.  **Despliegue Continuo (Deploy)**: Genera dinámicamente una plantilla JSON de despliegue (`aca_deployment.json`) a partir de la configuración existente y la actualiza en Azure mediante la API REST de Resource Manager.
5.  **Validación Post-Despliegue**: El runner consulta en bucle el estado del aprovisionamiento de ACA hasta que la nueva revisión está marcada como *Succeeded*. Posteriormente, realiza llamadas HTTP de humo a `/health`, `/knowledge` y `/ask` sobre el FQDN público en Azure para certificar un despliegue exitoso.

---

## 8. MONITOREO Y VALIDACIÓN (Pruebas de Conexión y Logs en la Nube)
Para asegurar el correcto funcionamiento del sistema en producción, se implementaron mecanismos de monitoreo y pruebas de conexión:

*   **Validación de Salud (/health cloud)**: Las peticiones HTTPS GET al endpoint `/health` de nube retornan un estado `"status": "ok"` y confirman `"database": "connected"`, demostrando que ACA tiene acceso seguro y exitoso a Azure SQL Database.
*   **Validación RAG (/ask cloud)**: El endpoint `/ask` responde de forma consistente y en lenguaje natural a partir del contexto recuperado dinámicamente de Azure SQL, listando las fuentes y sus correspondientes puntajes de similitud semántica.
*   **Logs Operativos de ACA**: Se validaron los registros de ejecución y logs de arranque en caliente de la Container App (mediante el panel de Logs en Azure o Log Analytics), confirmando el encendido del servicio web Uvicorn y el registro exitoso de las peticiones HTTP entrantes.

---

## 9. REFLEXIÓN Y CONCLUSIONES

### Valor Añadido de RAG frente a APIs Tradicionales
Las APIs tradicionales operan con un esquema determinista basado en consultas fijas a bases de datos estructuradas o fuentes de información estáticas. RAG, por el contrario, dota a la aplicación de **capacidad cognitiva de lenguaje natural combinada con fuentes dinámicas de conocimiento actualizado**, sin incurrir en los costes exorbitantes y complejidad del re-entrenamiento o fine-tuning de un LLM. 

En este proyecto, la API actúa como un puente semántico: recupera dinámicamente contextos relevantes mediante vectores de embeddings y los inyecta en el LLM. Esto garantiza respuestas que no sufren de alucinaciones y que están fundamentadas estrictamente en la base de datos de conocimiento de la empresa.

### Buenas Prácticas y Protección de Secretos
*   **Aislamiento de Secretos**: La cadena de conexión a la base de datos y la API key de OpenAI nunca son escritas en código ni subidas al repositorio. Se gestionan mediante GitHub Secrets a nivel de código y a través del gestor de Secretos nativo de Azure Container Apps a nivel de nube, inyectándose en el contenedor únicamente en tiempo de ejecución.
*   **Despliegues Trazables e Inmutabilidad**: Cada compilación genera una imagen Docker inmutable en ACR con el hash SHA del commit de Git. Esto elimina el problema clásico de *"en mi máquina funciona"* y permite auditorías claras del código exacto en producción.
*   **Estrategia Serverless en la Nube**: El uso de Azure Container Apps permite auto-escalar la aplicación a cero cuando no recibe tráfico. Esto reduce significativamente los costes operativos de infraestructura sin perder disponibilidad del backend.

---

## DEFENSA TÉCNICA
> **“La solución integra un flujo RAG trazable con Azure SQL, Docker y ACR, desplegado en Azure Container Apps y automatizado de extremo a extremo mediante GitHub Actions, GitHub Secrets y etiquetas de imagen asociadas al commit.”**

---

## 10. ANEXO: EVIDENCIAS GRÁFICAS
A continuación se compilan de forma consecutiva todas las capturas de pantalla de evidencias del proyecto recopiladas durante las fases de desarrollo local, base de datos Azure SQL, configuración de ACR/ACA, pipeline CI/CD de GitHub Actions y validaciones en la nube:

### Evidencia 1
![Evidencia 1](Capturas%20Evidencias/image.png)

---

### Evidencia 2
![Evidencia 2](Capturas%20Evidencias/image%20copy.png)

---

### Evidencia 3
![Evidencia 3](Capturas%20Evidencias/image%20copy%202.png)

---

### Evidencia 4
![Evidencia 4](Capturas%20Evidencias/image%20copy%203.png)

---

### Evidencia 5
![Evidencia 5](Capturas%20Evidencias/image%20copy%204.png)

---

### Evidencia 6
![Evidencia 6](Capturas%20Evidencias/image%20copy%205.png)

---

### Evidencia 7
![Evidencia 7](Capturas%20Evidencias/image%20copy%206.png)

---

### Evidencia 8
![Evidencia 8](Capturas%20Evidencias/image%20copy%207.png)

---

### Evidencia 9
![Evidencia 9](Capturas%20Evidencias/image%20copy%208.png)

---

### Evidencia 10
![Evidencia 10](Capturas%20Evidencias/image%20copy%209.png)

---

### Evidencia 11
![Evidencia 11](Capturas%20Evidencias/image%20copy%2010.png)

---

### Evidencia 12
![Evidencia 12](Capturas%20Evidencias/image%20copy%2011.png)

---

### Evidencia 13
![Evidencia 13](Capturas%20Evidencias/image%20copy%2012.png)

---

### Evidencia 14
![Evidencia 14](Capturas%20Evidencias/image%20copy%2013.png)

---

### Evidencia 15
![Evidencia 15](Capturas%20Evidencias/image%20copy%2014.png)

---

### Evidencia 16
![Evidencia 16](Capturas%20Evidencias/image%20copy%2015.png)

---

### Evidencia 17
![Evidencia 17](Capturas%20Evidencias/image%20copy%2016.png)

---

### Evidencia 18
![Evidencia 18](Capturas%20Evidencias/image%20copy%2017.png)

---

### Evidencia 19
![Evidencia 19](Capturas%20Evidencias/image%20copy%2018.png)

---

### Evidencia 20
![Evidencia 20](Capturas%20Evidencias/image%20copy%2019.png)

---

### Evidencia 21
![Evidencia 21](Capturas%20Evidencias/image%20copy%2020.png)

---

### Evidencia 22
![Evidencia 22](Capturas%20Evidencias/image%20copy%2021.png)

---

### Evidencia 23
![Evidencia 23](Capturas%20Evidencias/image%20copy%2022.png)

---

### Evidencia 24
![Evidencia 24](Capturas%20Evidencias/image%20copy%2023.png)

---

### Evidencia 25
![Evidencia 25](Capturas%20Evidencias/image%20copy%2024.png)

---

### Evidencia 26
![Evidencia 26](Capturas%20Evidencias/image%20copy%2025.png)

---

### Evidencia 27
![Evidencia 27](Capturas%20Evidencias/image%20copy%2026.png)

---

### Evidencia 28
![Evidencia 28](Capturas%20Evidencias/image%20copy%2027.png)

---

### Evidencia 29
![Evidencia 29](Capturas%20Evidencias/image%20copy%2028.png)

---

### Evidencia 30
![Evidencia 30](Capturas%20Evidencias/image%20copy%2029.png)

---

### Evidencia 31
![Evidencia 31](Capturas%20Evidencias/image%20copy%2030.png)

---

### Evidencia 32
![Evidencia 32](Capturas%20Evidencias/image%20copy%2031.png)

---

### Evidencia 33
![Evidencia 33](Capturas%20Evidencias/image%20copy%2032.png)

---

### Evidencia 34
![Evidencia 34](Capturas%20Evidencias/image%20copy%2033.png)

---

### Evidencia 35
![Evidencia 35](Capturas%20Evidencias/image%20copy%2034.png)
