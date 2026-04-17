from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.db import get_db
from app.models.entities import GuideStep, RecommendedProduct, User
from app.schemas.guide import GuideCreateRequest, GuideResponse, GuideStepRequest, GuideUpdateRequest, ProductCreateRequest
from app.services.guide_service import (
    add_download,
    add_favorite,
    add_product,
    add_step,
    create_guide,
    delete_guide,
    delete_step,
    get_guide_or_404,
    list_guides,
    remove_favorite,
    update_guide,
    update_step,
)

router = APIRouter(prefix="/guides", tags=["guides"])


@router.get("", response_model=list[GuideResponse])
def get_guides(
    id_categoria_guias: int | None = None,
    id_nivel_complejidad: int | None = None,
    texto: str | None = None,
    db: Session = Depends(get_db),
):
    return list_guides(db, id_categoria_guias, id_nivel_complejidad, texto)


@router.get("/{id}", response_model=GuideResponse)
def get_guide(id: int, db: Session = Depends(get_db)):
    return get_guide_or_404(db, id)


@router.post("", response_model=GuideResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_guide(payload: GuideCreateRequest, db: Session = Depends(get_db)):
    return create_guide(db, payload)


@router.put("/{id}", response_model=GuideResponse, dependencies=[Depends(require_admin)])
def put_guide(id: int, payload: GuideUpdateRequest, db: Session = Depends(get_db)):
    guide = get_guide_or_404(db, id)
    return update_guide(db, guide, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def remove_guide(id: int, db: Session = Depends(get_db)):
    guide = get_guide_or_404(db, id)
    delete_guide(db, guide)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/steps")
def get_steps(id: int, db: Session = Depends(get_db)):
    return db.execute(select(GuideStep).where(GuideStep.id_guias_supervivencia == id).order_by(GuideStep.orden.asc())).scalars().all()


@router.post("/{id}/steps", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_step(id: int, payload: GuideStepRequest, db: Session = Depends(get_db)):
    _ = get_guide_or_404(db, id)
    return add_step(db, id, payload)


@router.put("/steps/{id}", dependencies=[Depends(require_admin)])
def put_step(id: int, payload: GuideStepRequest, db: Session = Depends(get_db)):
    return update_step(db, id, payload)


@router.delete("/steps/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def remove_step(id: int, db: Session = Depends(get_db)):
    delete_step(db, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/favorite", status_code=status.HTTP_201_CREATED)
def post_favorite(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = get_guide_or_404(db, id)
    return add_favorite(db, id, current_user.id_usuario)


@router.delete("/{id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    remove_favorite(db, id, current_user.id_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/download", status_code=status.HTTP_201_CREATED)
def post_download(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = get_guide_or_404(db, id)
    return add_download(db, id, current_user.id_usuario)


@router.get("/{id}/products")
def get_products(id: int, db: Session = Depends(get_db)):
    return db.execute(select(RecommendedProduct).where(RecommendedProduct.id_guias_supervivencia == id)).scalars().all()


@router.post("/{id}/products", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_product(id: int, payload: ProductCreateRequest, db: Session = Depends(get_db)):
    _ = get_guide_or_404(db, id)
    return add_product(db, id, payload)
