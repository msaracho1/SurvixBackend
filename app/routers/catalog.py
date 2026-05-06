from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import require_admin
from app.dependencies.db import get_db
from app.models.entities import Activity, ComplexityLevel, Difficulty, GuideCategory, Role

router = APIRouter(tags=["catalog"])


class ActivityRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


@router.get("/activities")
def get_activities(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(Activity).order_by(Activity.id_actividad)).scalars().all()
    return [{"id": a.id_actividad, "nombre": a.nombre} for a in items]


@router.post("/activities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_activity(payload: ActivityRequest, db: Session = Depends(get_db)) -> dict:
    activity = Activity(nombre=payload.nombre)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return {"id": activity.id_actividad, "nombre": activity.nombre}


@router.put("/activities/{id}", dependencies=[Depends(require_admin)])
def update_activity(id: int, payload: ActivityRequest, db: Session = Depends(get_db)) -> dict:
    activity = db.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    activity.nombre = payload.nombre
    db.commit()
    db.refresh(activity)
    return {"id": activity.id_actividad, "nombre": activity.nombre}


@router.delete("/activities/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_activity(id: int, db: Session = Depends(get_db)) -> None:
    activity = db.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/difficulties")
def get_difficulties(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(Difficulty).order_by(Difficulty.id_dificultad)).scalars().all()
    return [{"id": d.id_dificultad, "nombre": d.nombre} for d in items]


@router.get("/roles")
def get_roles(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(Role).order_by(Role.id_rol)).scalars().all()
    return [{"id_rol": r.id_rol, "nombre": r.nombre} for r in items]


@router.get("/guide-categories")
def get_guide_categories(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(GuideCategory).order_by(GuideCategory.id_categoria_guias)).scalars().all()
    return [{"id": c.id_categoria_guias, "nombre": c.nombre} for c in items]


@router.get("/guide-levels")
def get_guide_levels(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(ComplexityLevel).order_by(ComplexityLevel.id_nivel_complejidad)).scalars().all()
    return [{"id": l.id_nivel_complejidad, "nombre": l.nombre} for l in items]
