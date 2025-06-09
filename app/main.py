from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← Importación correcta
from app.routes import auth
from app.config.database import test_connection
from decouple import config
from typing import Dict, Any

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Veterinaria",
    description="Sistema de gestión veterinaria",
    version="1.0.0"
)

# Configurar CORS para desarrollo con múltiples desarrolladores
FRONTEND_URL: str = str(config("FRONTEND_URL", default="http://localhost:5173"))

# URLs permitidas (incluyendo diferentes puertos para el equipo)
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Si alguien ya tiene el 5173 ocupado
    "http://localhost:5175",  # Puerto alternativo
    "http://localhost:3000",  # Por si alguien usa Create React App
    "http://127.0.0.1:5173",  # IPv4 local
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    # Agregar más puertos si es necesario
]

app.add_middleware(
    CORSMiddleware,  # ← Corregido: CORS (no CORs)
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event() -> None:
    """Eventos al iniciar la aplicación"""
    print("🚀 Iniciando API Veterinaria...")
    print(f"🌐 Frontend permitido en: {FRONTEND_URL}")
    test_connection()

@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "message": "API Veterinaria funcionando correctamente",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Endpoint para verificar el estado de la API"""
    return {"status": "OK", "message": "API funcionando correctamente"}