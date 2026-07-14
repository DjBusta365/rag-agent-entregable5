import pyodbc
import re
from settings import settings


def get_connection():
    """Abre una conexion contra Azure SQL Database usando una variable de entorno."""
    if not settings.azure_sql_connection_string:
        raise RuntimeError(
            "Falta AZURE_SQL_CONNECTION_STRING. Configurala en .env, en Azure DevOps o en los secretos de ACA."
        )
    
    conn_str = settings.azure_sql_connection_string
    # Detectar drivers SQL Server instalados en el sistema actual
    drivers = [d for d in pyodbc.drivers() if "SQL Server" in d or "ODBC Driver" in d]
    if drivers:
        match = re.search(r"Driver=\{([^}]+)\}", conn_str, re.IGNORECASE)
        if match:
            current_driver = match.group(1)
            # Si el driver especificado no está instalado, buscar el mejor disponible en el sistema
            if current_driver not in drivers:
                best_driver = None
                for drv in ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server", "SQL Server"]:
                    if drv in drivers:
                        best_driver = drv
                        break
                if not best_driver:
                    best_driver = drivers[0]
                
                # Reemplazar en la cadena de conexión
                conn_str = re.sub(r"Driver=\{[^}]+\}", f"Driver={{{best_driver}}}", conn_str, flags=re.IGNORECASE)

    return pyodbc.connect(conn_str)


def create_table_if_not_exists() -> None:
    """Crea la tabla de conocimiento si no existe."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        IF OBJECT_ID('dbo.knowledge_chunks', 'U') IS NULL
        CREATE TABLE dbo.knowledge_chunks (
            id INT IDENTITY(1,1) PRIMARY KEY,
            title NVARCHAR(255) NOT NULL,
            source NVARCHAR(255) NULL,
            content NVARCHAR(MAX) NOT NULL,
            embedding NVARCHAR(MAX) NOT NULL,
            embedding_model NVARCHAR(100) NOT NULL,
            created_at DATETIME2 DEFAULT SYSUTCDATETIME()
        );
        """
    )
    conn.commit()
    conn.close()
