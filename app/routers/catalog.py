from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.entities import Activity, Difficulty, Role

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
