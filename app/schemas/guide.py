from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GuideCreateRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=45)
    descripcion: str
    duracion_min: int = Field(gt=0)
    id_categoria_guias: int
    id_nivel_complejidad: int
    latitud: float | None = None
    longitud: float | None = None


class GuideUpdateRequest(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=45)
    descripcion: str | None = None
    duracion_min: int | None = Field(default=None, gt=0)
    id_categoria_guias: int | None = None
    id_nivel_complejidad: int | None = None
    latitud: float | None = None
    longitud: float | None = None


class GuideStepRequest(BaseModel):
    descripcion: str
    orden: int = Field(ge=0)


class ProductCreateRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=45)
    url: str = Field(min_length=1, max_length=255)
    imagen_url: str = Field(min_length=1, max_length=255)


class GuideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_guias_supervivencia: int
    titulo: str
    descripcion: str
    duracion_min: int
    fecha_creacion: datetime
    id_categoria_guias: int
    id_nivel_complejidad: int
    latitud: float | None = None
    longitud: float | None = None