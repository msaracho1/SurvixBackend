from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.db import get_db
from app.models.entities import RouteImage, RoutePoint, RouteReview, User
from app.schemas.route import (
    RouteCreateRequest,
    RouteDetailResponse,
    RouteImageRequest,
    RoutePointRequest,
    RouteResponse,
    RouteReviewRequest,
    RouteUpdateRequest,
)
from app.services.route_service import (
    add_download,
    add_favorite,
    add_review,
    add_route_image,
    add_route_point,
    build_route_detail,
    create_route,
    delete_route,
    delete_route_point,
    get_route_or_404,
    list_routes,
    remove_favorite,
    update_route,
    update_route_point,
)

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[RouteResponse])
def get_routes(
    id_actividad: int | None = None,
    id_dificultad: int | None = None,
    id_ubicacion: int | None = None,
    distancia_min: float | None = None,
    distancia_max: float | None = None,
    duracion_min: int | None = None,
    duracion_max: int | None = None,
    texto: str | None = None,
    db: Session = Depends(get_db),
):
    return list_routes(db, id_actividad, id_dificultad, id_ubicacion, distancia_min, distancia_max, duracion_min, duracion_max, texto)


@router.get("/{id}", response_model=RouteDetailResponse)
def get_route(id: int, db: Session = Depends(get_db)):
    route = get_route_or_404(db, id)
    return build_route_detail(db, route)


@router.post("", response_model=RouteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def post_route(payload: RouteCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_route(db, payload, user_id=current_user.id_usuario)


@router.put("/{id}", response_model=RouteResponse, dependencies=[Depends(require_admin)])
def put_route(id: int, payload: RouteUpdateRequest, db: Session = Depends(get_db)):
    route = get_route_or_404(db, id)
    return update_route(db, route, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def remove_route(id: int, db: Session = Depends(get_db)):
    route = get_route_or_404(db, id)
    delete_route(db, route)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/points")
def get_points(id: int, db: Session = Depends(get_db)):
    _ = get_route_or_404(db, id)

    rows = db.execute(
        select(
            RoutePoint.id_ruta_punto,
            func.ST_AsText(RoutePoint.latlong),
            RoutePoint.orden,
            RoutePoint.id_rutas,
        )
        .where(RoutePoint.id_rutas == id)
        .order_by(RoutePoint.orden.asc())
    ).all()

    return [
    {
        "id_ruta_punto": row[0],
        "lat": float(row[1].replace("POINT(", "").replace(")", "").split()[1]),
        "lng": float(row[1].replace("POINT(", "").replace(")", "").split()[0]),
        "orden": row[2],
        "id_rutas": row[3],
    }
    for row in rows
]


@router.post("/{id}/points", dependencies=[Depends(require_admin)], status_code=status.HTTP_201_CREATED)
def post_point(id: int, payload: RoutePointRequest, db: Session = Depends(get_db)):
    _ = get_route_or_404(db, id)
    return add_route_point(db, id, payload)


@router.put("/points/{id}", dependencies=[Depends(require_admin)])
def put_point(id: int, payload: RoutePointRequest, db: Session = Depends(get_db)):
    return update_route_point(db, id, payload)


@router.delete("/points/{id}", dependencies=[Depends(require_admin)], status_code=status.HTTP_204_NO_CONTENT)
def remove_point(id: int, db: Session = Depends(get_db)):
    delete_route_point(db, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/images")
def get_images(id: int, db: Session = Depends(get_db)):
    return db.execute(select(RouteImage).where(RouteImage.id_rutas == id)).scalars().all()


@router.post("/{id}/images", dependencies=[Depends(require_admin)], status_code=status.HTTP_201_CREATED)
def post_image(id: int, payload: RouteImageRequest, db: Session = Depends(get_db)):
    _ = get_route_or_404(db, id)
    return add_route_image(db, id, payload)


@router.get("/{id}/reviews")
def get_reviews(id: int, db: Session = Depends(get_db)):
    return db.execute(select(RouteReview).where(RouteReview.id_rutas == id)).scalars().all()


@router.post("/{id}/reviews", status_code=status.HTTP_201_CREATED)
def post_review(id: int, payload: RouteReviewRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = get_route_or_404(db, id)
    return add_review(db, id, current_user.id_usuario, payload)


@router.post("/{id}/favorite", status_code=status.HTTP_201_CREATED)
def post_favorite(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = current_user
    _ = get_route_or_404(db, id)
    return add_favorite(db, id)


@router.delete("/{id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = current_user
    remove_favorite(db, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/download", status_code=status.HTTP_201_CREATED)
def post_download(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = get_route_or_404(db, id)
    return add_download(db, id, current_user.id_usuario)
