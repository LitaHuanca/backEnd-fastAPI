from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import Row
from app.config.database import get_db
from app.utils.security import verify_token
from typing import Dict, Any, Optional

# Esquema de seguridad
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtener el usuario actual desde el token JWT"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar el token
    payload: Optional[Dict[str, Any]] = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    query = text("""
        SELECT id_usuario, username, tipo_usuario, estado 
        FROM usuarios 
        WHERE username = :username AND estado = 'Activo'
    """)
    
    result = db.execute(query, {"username": username})
    user: Optional[Row[Any]] = result.fetchone()
    
    if user is None:
        raise credentials_exception
    
    return {
        "id_usuario": user[0],
        "username": user[1],
        "tipo_usuario": user[2],
        "estado": user[3]
    }