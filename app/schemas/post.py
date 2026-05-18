from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=255)
    contenido: str = Field(min_length=1)
    categoria: str = Field(min_length=1, max_length=100)
    imagen_url: str | None = None


class CommentCreateRequest(BaseModel):
    contenido: str = Field(min_length=1)


class CommentOut(BaseModel):
    id: int
    contenido: str
    autor_nombre: str
    fecha: datetime


class PostOut(BaseModel):
    id: int
    titulo: str | None
    contenido: str
    categoria: str | None
    fecha: datetime
    autor_nombre: str
    autor_rol: str
    imagen_url: str | None
    likes_count: int
    liked_by_me: bool
    comments: list[CommentOut]
