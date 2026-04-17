from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class FirebaseSyncRequest(BaseModel):
    firebase_uid: str = Field(min_length=6, max_length=128)
    email: EmailStr


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id_usuario: int
    email: EmailStr
    firebase_uid: str | None
    id_rol: int
    role: str
    fecha_creacion: datetime
