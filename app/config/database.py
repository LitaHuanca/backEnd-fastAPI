from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config
import logging
from typing import Generator

# Configuración de logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# URL de la base de datos desde variables de entorno con manejo de tipos
_database_url = config("DATABASE_URL")
if not _database_url:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env")

DATABASE_URL: str = str(_database_url)

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Para ver las consultas SQL en desarrollo
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_recycle=300  # Reciclar conexiones cada 5 minutos
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para probar la conexión
def test_connection() -> bool:
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False