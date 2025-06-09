from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.config.database import get_db
from app.models.user import UserLogin, TokenResponse, UserProfileComplete
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class TokenResponseComplete(BaseModel):
    """Respuesta completa del login con token y perfil de usuario"""
    access_token: str
    token_type: str
    user: UserProfileComplete

@router.post("/login", response_model=TokenResponseComplete)
async def login(user_login: UserLogin, db: Session = Depends(get_db)) -> TokenResponseComplete:
    """
    Iniciar sesión con username y contraseña
    Retorna el token y el perfil completo del usuario
    """
    try:
        result: Dict[str, Any] = AuthService.authenticate_user(db, user_login)
        return TokenResponseComplete(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/profile", response_model=UserProfileComplete)
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfileComplete:
    """
    Obtener perfil completo del usuario autenticado
    """
    try:
        # Crear un objeto UserInDB temporal para obtener el perfil actualizado
        from app.models.user import UserInDB
        from datetime import datetime
        
        user_in_db = UserInDB(
            id_usuario=current_user["id_usuario"],
            username=current_user["username"],
            contraseña="",  # No necesitamos la contraseña para obtener el perfil
            tipo_usuario=current_user["tipo_usuario"],
            estado="Activo",  # Asumimos que está activo si tiene token válido
            fecha_creacion=datetime.now()  # Usar fecha actual temporal
        )
        
        profile = AuthService._get_user_profile(db, user_in_db)
        return profile
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener perfil: {str(e)}"
        )

@router.get("/verify-token")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Verificar si el token es válido
    """
    return {
        "valid": True,
        "user": {
            "id_usuario": current_user["id_usuario"],
            "username": current_user["username"],
            "tipo_usuario": current_user["tipo_usuario"]
        }
        # Removido el sistema de permisos ya que decidiste no implementarlo
    }

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Cerrar sesión (en el frontend se debe eliminar el token)
    """
    return {"message": f"Sesión cerrada exitosamente para {current_user['username']}"}

# Endpoint adicional para cambiar contraseña (opcional)
@router.put("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Cambiar contraseña del usuario autenticado
    """
    try:
        # Aquí implementarías la lógica para cambiar contraseña
        # Por ahora solo retornamos un mensaje
        return {"message": "Funcionalidad de cambio de contraseña pendiente de implementar"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )