from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import GuideDownload, GuideFavorite, GuideStep, RecommendedProduct, SurvivalGuide
from app.schemas.guide import GuideCreateRequest, GuideStepRequest, GuideUpdateRequest, ProductCreateRequest


def list_guides(db: Session, id_categoria_guias: int | None = None, id_nivel_complejidad: int | None = None, texto: str | None = None) -> list[SurvivalGuide]:
    query = select(SurvivalGuide)
    filters = []
    if id_categoria_guias is not None:
        filters.append(SurvivalGuide.id_categoria_guias == id_categoria_guias)
    if id_nivel_complejidad is not None:
        filters.append(SurvivalGuide.id_nivel_complejidad == id_nivel_complejidad)
    if texto:
        text_like = f"%{texto}%"
        filters.append(or_(SurvivalGuide.titulo.ilike(text_like), SurvivalGuide.descripcion.ilike(text_like)))
    if filters:
        query = query.where(and_(*filters))
    return db.execute(query.order_by(SurvivalGuide.fecha_creacion.desc())).scalars().all()


def get_guide_or_404(db: Session, guide_id: int) -> SurvivalGuide:
    guide = (
        db.execute(
            select(SurvivalGuide)
            .where(SurvivalGuide.id_guias_supervivencia == guide_id)
            .options(joinedload(SurvivalGuide.steps), joinedload(SurvivalGuide.products))
        )
        .scalars()
        .first()
    )
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide


def create_guide(db: Session, payload: GuideCreateRequest) -> SurvivalGuide:
    guide = SurvivalGuide(
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        duracion_min=payload.duracion_min,
        fecha_creacion=datetime.now(timezone.utc),
        id_categoria_guias=payload.id_categoria_guias,
        id_nivel_complejidad=payload.id_nivel_complejidad,
    )
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide


def update_guide(db: Session, guide: SurvivalGuide, payload: GuideUpdateRequest) -> SurvivalGuide:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(guide, key, value)
    db.commit()
    db.refresh(guide)
    return guide


def delete_guide(db: Session, guide: SurvivalGuide) -> None:
    db.delete(guide)
    db.commit()


def add_step(db: Session, guide_id: int, payload: GuideStepRequest) -> GuideStep:
    step = GuideStep(id_guias_supervivencia=guide_id, descripcion=payload.descripcion, orden=payload.orden)
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def update_step(db: Session, step_id: int, payload: GuideStepRequest) -> GuideStep:
    step = db.get(GuideStep, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    step.descripcion = payload.descripcion
    step.orden = payload.orden
    db.commit()
    db.refresh(step)
    return step


def delete_step(db: Session, step_id: int) -> None:
    step = db.get(GuideStep, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    db.delete(step)
    db.commit()


def add_favorite(db: Session, guide_id: int, user_id: int) -> GuideFavorite:
    favorite = GuideFavorite(id_guias_supervivencia=guide_id, id_usuario=user_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, guide_id: int, user_id: int) -> None:
    favorite = db.execute(
        select(GuideFavorite).where(
            GuideFavorite.id_guias_supervivencia == guide_id,
            GuideFavorite.id_usuario == user_id,
        )
    ).scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()


def add_download(db: Session, guide_id: int, user_id: int) -> GuideDownload:
    item = GuideDownload(id_guias_supervivencia=guide_id, id_usuario=user_id, fecha=datetime.now(timezone.utc))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_product(db: Session, guide_id: int, payload: ProductCreateRequest) -> RecommendedProduct:
    product = RecommendedProduct(
        id_guias_supervivencia=guide_id,
        nombre=payload.nombre,
        url=payload.url,
        imagen_url=payload.imagen_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
