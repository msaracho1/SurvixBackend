from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RouteCreateRequest(BaseModel):
    id_actividad: int
    id_dificultad: int
    id_ubicacion: int
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str
    distancia_km: float = Field(gt=0)
    duracion_min: int = Field(gt=0)
    latitud: float | None = None
    longitud: float | None = None


class RouteUpdateRequest(BaseModel):
    id_actividad: int | None = None
    id_dificultad: int | None = None
    id_ubicacion: int | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    descripcion: str | None = None
    distancia_km: float | None = Field(default=None, gt=0)
    duracion_min: int | None = Field(default=None, gt=0)
    latitud: float | None = None
    longitud: float | None = None


class RoutePointRequest(BaseModel):
    latlong: str = Field(description="WKT format: POINT(lon lat)")
    orden: int = Field(ge=0)


class RouteImageRequest(BaseModel):
    url: str = Field(min_length=1, max_length=255)


class RouteReviewRequest(BaseModel):
    puntaje: int = Field(ge=1, le=5)


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_rutas: int
    nombre: str
    descripcion: str
    distancia_km: float
    duracion_min: int
    fecha_creacion: datetime
    id_usuario: int
    id_actividad: int
    id_dificultad: int
    id_ubicacion: int
    latitud: float | None = None
    longitud: float | None = None


class RouteDetailResponse(BaseModel):
    route: RouteResponse
    location: dict
    activity: dict
    difficulty: dict
    images: list[dict]
    points: list[dict]
    rating_avg: float | None
    reviews_count: int