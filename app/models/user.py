from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime, date

# Modelo para el login
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Nombre de usuario")
    password: str = Field(..., min_length=3, description="Contraseña")

# Modelo para la respuesta del login
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_usuario: int
    username: str
    tipo_usuario: Literal['Veterinario', 'Recepcionista', 'Administrador']
    estado: Literal['Activo', 'Inactivo']
    fecha_creacion: datetime

# Modelo para la respuesta con token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Modelo para el perfil completo del usuario
class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_usuario: int
    username: str
    tipo_usuario: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    dni: str
    telefono: str
    genero: str

# Modelo para datos internos del usuario (desde DB)
class UserInDB(BaseModel):
    id_usuario: int
    username: str
    contraseña: str
    tipo_usuario: Literal['Veterinario', 'Recepcionista', 'Administrador']
    estado: Literal['Activo', 'Inactivo']
    fecha_creacion: datetime

class UserProfileComplete(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    # Datos básicos del usuario
    id_usuario: int
    username: str
    tipo_usuario: Literal['Veterinario', 'Recepcionista', 'Administrador']
    estado: Literal['Activo', 'Inactivo']
    fecha_creacion: datetime
    
    # Datos del perfil específico
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    dni: str
    telefono: str
    genero: Literal['F', 'M']
    
    # Datos específicos según tipo de usuario
    fecha_ingreso: Optional[date] = None
    
    # Para Veterinario
    id_especialidad: Optional[int] = None
    codigo_CMVP: Optional[str] = None
    tipo_veterinario: Optional[Literal['Medico General', 'Especializado']] = None
    fecha_nacimiento: Optional[date] = None
    disposicion: Optional[Literal['Ocupado', 'Libre']] = None
    turno: Optional[Literal['Mañana', 'Tarde', 'Noche']] = None
    especialidad_descripcion: Optional[str] = None
    
    # Para Recepcionista
    turno_recepcionista: Optional[Literal['Mañana', 'Tarde', 'Noche']] = None