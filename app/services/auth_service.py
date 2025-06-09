from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import Row
from app.models.user import UserLogin, UserResponse, UserInDB, UserProfileComplete
from app.utils.security import verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta
from decouple import config
from typing import Dict, Any, Optional

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default="30"))

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, user_login: UserLogin) -> Dict[str, Any]:
        """Autenticar usuario y devolver token con perfil completo"""
        
        # Buscar usuario en la base de datos
        query = text("""
            SELECT id_usuario, username, contraseña, tipo_usuario, estado, fecha_creacion
            FROM usuarios 
            WHERE username = :username
        """)
        
        result = db.execute(query, {"username": user_login.username})
        user_data: Optional[Row[Any]] = result.fetchone()
        
        # Verificar si el usuario existe
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        # Crear objeto UserInDB para mejor tipado
        user_in_db = UserInDB(
            id_usuario=user_data[0],
            username=user_data[1],
            contraseña=user_data[2],
            tipo_usuario=user_data[3],
            estado=user_data[4],
            fecha_creacion=user_data[5]
        )
        
        # Verificar si el usuario está activo
        if user_in_db.estado != 'Activo':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        # Verificar contraseña
        if not verify_password(user_login.password, user_in_db.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        user_profile = AuthService._get_user_profile(db, user_in_db)

        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_in_db.username,
                "tipo_usuario": user_in_db.tipo_usuario,
                "id_usuario": user_in_db.id_usuario
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_profile
        }
    @staticmethod
    def _get_user_profile(db: Session, user_in_db: UserInDB) -> UserProfileComplete:
        """Obtener perfil completo del usuario según su tipo"""
        
        if user_in_db.tipo_usuario == 'Veterinario':
            query = text("""
                SELECT 
                    u.id_usuario, u.username, u.tipo_usuario, u.estado, u.fecha_creacion,
                    v.nombre, v.apellido_paterno, v.apellido_materno, v.email, v.dni, 
                    v.telefono, v.genero, v.fecha_ingreso, v.id_especialidad, 
                    v.codigo_CMVP, v.tipo_veterinario, v.fecha_nacimiento, 
                    v.disposicion, v.turno, e.descripcion as especialidad_descripcion
                FROM usuarios u
                JOIN Veterinario v ON u.id_usuario = v.id_usuario
                LEFT JOIN Especialidad e ON v.id_especialidad = e.id_especialidad
                WHERE u.id_usuario = :id_usuario
            """)
            
        elif user_in_db.tipo_usuario == 'Recepcionista':
            query = text("""
                SELECT 
                    u.id_usuario, u.username, u.tipo_usuario, u.estado, u.fecha_creacion,
                    r.nombre, r.apellido_paterno, r.apellido_materno, r.email, r.dni, 
                    r.telefono, r.genero, r.fecha_ingreso, r.turno
                FROM usuarios u
                JOIN Recepcionista r ON u.id_usuario = r.id_usuario
                WHERE u.id_usuario = :id_usuario
            """)
            
        elif user_in_db.tipo_usuario == 'Administrador':
            query = text("""
                SELECT 
                    u.id_usuario, u.username, u.tipo_usuario, u.estado, u.fecha_creacion,
                    a.nombre, a.apellido_paterno, a.apellido_materno, a.email, a.dni, 
                    a.telefono, a.genero, a.fecha_ingreso
                FROM usuarios u
                JOIN Administrador a ON u.id_usuario = a.id_usuario
                WHERE u.id_usuario = :id_usuario
            """)
        
        result = db.execute(query, {"id_usuario": user_in_db.id_usuario})
        profile_data: Optional[Row[Any]] = result.fetchone()
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de usuario no encontrado"
            )
        
        # Crear objeto UserProfileComplete
        if user_in_db.tipo_usuario == 'Veterinario':
            return UserProfileComplete(
                id_usuario=profile_data[0],
                username=profile_data[1],
                tipo_usuario=profile_data[2],
                estado=profile_data[3],
                fecha_creacion=profile_data[4],
                nombre=profile_data[5],
                apellido_paterno=profile_data[6],
                apellido_materno=profile_data[7],
                email=profile_data[8],
                dni=profile_data[9],
                telefono=profile_data[10],
                genero=profile_data[11],
                fecha_ingreso=profile_data[12],
                id_especialidad=profile_data[13],
                codigo_CMVP=profile_data[14],
                tipo_veterinario=profile_data[15],
                fecha_nacimiento=profile_data[16],
                disposicion=profile_data[17],
                turno=profile_data[18],
                especialidad_descripcion=profile_data[19]
            )
        
        elif user_in_db.tipo_usuario == 'Recepcionista':
            return UserProfileComplete(
                id_usuario=profile_data[0],
                username=profile_data[1],
                tipo_usuario=profile_data[2],
                estado=profile_data[3],
                fecha_creacion=profile_data[4],
                nombre=profile_data[5],
                apellido_paterno=profile_data[6],
                apellido_materno=profile_data[7],
                email=profile_data[8],
                dni=profile_data[9],
                telefono=profile_data[10],
                genero=profile_data[11],
                fecha_ingreso=profile_data[12],
                turno_recepcionista=profile_data[13]
            )
        
        else:  # Administrador
            return UserProfileComplete(
                id_usuario=profile_data[0],
                username=profile_data[1],
                tipo_usuario=profile_data[2],
                estado=profile_data[3],
                fecha_creacion=profile_data[4],
                nombre=profile_data[5],
                apellido_paterno=profile_data[6],
                apellido_materno=profile_data[7],
                email=profile_data[8],
                dni=profile_data[9],
                telefono=profile_data[10],
                genero=profile_data[11],
                fecha_ingreso=profile_data[12]
            )