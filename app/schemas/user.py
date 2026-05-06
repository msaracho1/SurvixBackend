from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    email: EmailStr
    firebase_uid: str | None
    id_rol: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_perfil_usuario: int
    nombre: str
    apellido: str
    foto_url: str
    bio: str
    ubicacion: str
    fecha_nacimiento: date
    id_usuario: int


class ProfileUpdateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    apellido: str = Field(min_length=1, max_length=255)
    foto_url: str | None = Field(default=None, max_length=500)
    bio: str = ""
    ubicacion: str = Field(default="", max_length=150)
    fecha_nacimiento: date | None = None
