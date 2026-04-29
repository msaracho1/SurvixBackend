from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.entities import Activity, ComplexityLevel, Difficulty, GuideCategory, Role

router = APIRouter(tags=["catalog"])


@router.get("/activities")
def get_activities(db: Session = Depends(get_db)) -> list[dict]:
    items = db.execute(select(Activity).order_by(Activity.id_actividad)).scalars().all()
    return [{"id": a.id_actividad, "nombre": a.nombre} for a in items]


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
