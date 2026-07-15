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

## 3. DESARROLLO Y CONFIGURACIÓN LOCAL

### Estructura del Repositorio y Configuración de Archivos
El proyecto cuenta con una estructura limpia, excluyendo del control de versiones los archivos de entorno mediante [.gitignore](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.gitignore):

La configuración del entorno local se gestiona a través del archivo de configuración sensible [.env](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.env) (el cual está debidamente excluido de Git para evitar fugas de información):

### Contenerización Local con Docker
El backend está definido mediante un archivo `Dockerfile` optimizado y se levanta en conjunto con Docker Compose para desarrollo local rápido.

La aplicación levanta localmente el servidor web Uvicorn (FastAPI) mapeando el puerto hacia la máquina host:

### Validación Local de la API
Para verificar que el agente responde correctamente antes de enviarlo a la nube, se prueba el Swagger interactivo local en `/docs` enviando preguntas al endpoint `/ask`:

---

## 4. CONFIGURACIÓN EN AZURE Y REGISTRO DE CONTENEDORES

### Base de Datos Azure SQL
Se creó una Azure SQL Database. El firewall se configuró para permitir las conexiones de servicios de Azure y de la IP de desarrollo local. La estructura de la tabla `dbo.knowledge_chunks` y sus columnas se definieron en [db.py](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/db.py):

*(Se muestra la tabla dbo.knowledge_chunks creada y lista para almacenar embeddings y fragmentos)*

*(Filas de ejemplo inicializadas en el Query Editor de Azure)*

### Azure Container Registry (ACR)
Se desplegó un ACR con el nombre `acragent5XXX` para almacenar las versiones de la API:

*(Configuración del registro en el portal de Azure)*

*(Claves de acceso y servidor de login del ACR)*

### Etiquetado y Push Manual de Prueba
Para verificar el correcto funcionamiento del registro de contenedores, se realizó una prueba manual iniciando sesión mediante Azure CLI y enviando la imagen local de la API al repositorio `rag-agent-api`:

*(Repositorio de imágenes dentro de la consola del ACR)*

*(Detalles de tags y tamaño de las capas de imagen en ACR)*

### Azure Container Apps (ACA)
Para alojar la API se configuró una Azure Container App sobre un entorno serverless gestionado:

La aplicación fue configurada con Ingress externo en el puerto de destino `8000` para poder recibir tráfico HTTP seguro:

Las credenciales sensibles de base de datos (`AZURE_SQL_CONNECTION_STRING`) y de Azure Container Registry se mapearon a secretos protegidos del servicio ACA para evitar que estén visibles en texto plano:

---

## 5. AUTOMATIZACIÓN CI/CD CON GITHUB ACTIONS

### Configuración de Secretos de Repositorio
Para que GitHub Actions pueda autenticarse de manera autónoma con Azure, se configuraron los 11 secrets de repositorio, manteniendo la confidencialidad de la infraestructura:

### Ejecución del Workflow
El archivo de workflow [.github/workflows/deploy-aca.yml](file:///c:/DjBust@/Unir/Entregables/Ent%2005/rag-agent-entregable5/.github/workflows/deploy-aca.yml) orquesta todo el pipeline:

*(El workflow se dispara automáticamente al hacer git push a main)*

1.  **Validar Configuración**: Se comprueba la estructura del proyecto y los secretos necesarios:
    

2.  **Construir y Publicar Imagen**: Construcción de la imagen Docker etiquetada con el hash de commit (`IMAGE_TAG`) y subida al ACR:
    

3.  **Desplegar a ACA**: Lanzamiento de la orden de despliegue sobre Azure Container Apps usando la API REST de Azure Resource Manager:
    

4.  **Esperar la Nueva Revisión**: Bucle de comprobación que valida que la nueva versión del contenedor pase de estado "Provisioning" a "Succeeded":
    

5.  **Validar Endpoints**: Realización de llamadas de prueba a la URL pública final de ACA (`/health`, `/knowledge` y `/ask`) para certificar que el agente RAG está funcionando al 100% en la nube:
    

### Estado Exitoso del Pipeline
El workflow completa todas las etapas de forma exitosa ("En Verde"):

---

## 6. VALIDACIÓN EN EL ENTORNO DE NUBE (CLOUD)

### URL Pública y Endpoint Health Cloud
El despliegue provee un FQDN (Fully Qualified Domain Name) público HTTPS para la Container App:

El endpoint `/health` de nube demuestra una conexión exitosa a Azure SQL Database (`"database": "connected"`):

### Endpoint de Conocimiento e Ingesta Semántica
El endpoint `/knowledge` expone los fragmentos de datos cargados en la base de datos de producción:

### Consulta al Agente RAG (/ask cloud)
Al consultar al agente a través del endpoint `/ask`, el sistema recupera la información relevante desde Azure SQL, calcula el score y redacta la respuesta contextualizada:

### Logs de Operación en Azure
La monitorización mediante logs del contenedor demuestra un arranque exitoso de la aplicación en la nube y el procesamiento de las peticiones HTTP GET y POST entrantes:

### Swagger Interactivo Cloud y Resumen del Workflow
Swagger UI está expuesto de forma pública bajo HTTPS en `/docs`:

El pipeline de GitHub Actions resume todos los accesos rápidos en la sección de resumen del trabajo (`GITHUB_STEP_SUMMARY`):

---

## 7. REFLEXIÓN Y CONCLUSIONES

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

## 8. ANEXO: EVIDENCIAS GRÁFICAS
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

---

