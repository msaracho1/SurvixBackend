from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Route, RouteDownload, RouteFavorite, RouteImage, RoutePoint, RouteReview
from app.schemas.route import RouteCreateRequest, RouteImageRequest, RoutePointRequest, RouteReviewRequest, RouteUpdateRequest


def list_routes(
    db: Session,
    id_actividad: int | None = None,
    id_dificultad: int | None = None,
    id_ubicacion: int | None = None,
    distancia_min: float | None = None,
    distancia_max: float | None = None,
    duracion_min: int | None = None,
    duracion_max: int | None = None,
    texto: str | None = None,
) -> list[Route]:
    query = select(Route)
    filters = []
    if id_actividad is not None:
        filters.append(Route.id_actividad == id_actividad)
    if id_dificultad is not None:
        filters.append(Route.id_dificultad == id_dificultad)
    if id_ubicacion is not None:
        filters.append(Route.id_ubicacion == id_ubicacion)
    if distancia_min is not None:
        filters.append(Route.distancia_km >= distancia_min)
    if distancia_max is not None:
        filters.append(Route.distancia_km <= distancia_max)
    if duracion_min is not None:
        filters.append(Route.duracion_min >= duracion_min)
    if duracion_max is not None:
        filters.append(Route.duracion_min <= duracion_max)
    if texto:
        text_like = f"%{texto}%"
        filters.append(or_(Route.nombre.ilike(text_like), Route.descripcion.ilike(text_like)))

    if filters:
        query = query.where(and_(*filters))

    return db.execute(query.order_by(Route.fecha_creacion.desc())).scalars().all()


def get_route_or_404(db: Session, route_id: int) -> Route:
    route = (
        db.execute(
            select(Route)
            .where(Route.id_rutas == route_id)
            .options(
                joinedload(Route.location),
                joinedload(Route.activity),
                joinedload(Route.difficulty),
                joinedload(Route.images),
                joinedload(Route.points),
            )
        )
        .scalars()
        .first()
    )
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return route


def create_route(db: Session, payload: RouteCreateRequest, user_id: int) -> Route:
    route = Route(
        id_usuario=user_id,
        id_actividad=payload.id_actividad,
        id_dificultad=payload.id_dificultad,
        id_ubicacion=payload.id_ubicacion,
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        distancia_km=payload.distancia_km,
        duracion_min=payload.duracion_min,
        fecha_creacion=datetime.now(timezone.utc),
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def update_route(db: Session, route: Route, payload: RouteUpdateRequest) -> Route:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return route


def delete_route(db: Session, route: Route) -> None:
    db.delete(route)
    db.commit()


def add_route_point(db: Session, route_id: int, payload: RoutePointRequest) -> RoutePoint:
    point = RoutePoint(id_rutas=route_id, latlong=payload.latlong, orden=payload.orden)
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


def update_route_point(db: Session, point_id: int, payload: RoutePointRequest) -> RoutePoint:
    point = db.get(RoutePoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Route point not found")
    point.latlong = payload.latlong
    point.orden = payload.orden
    db.commit()
    db.refresh(point)
    return point


def delete_route_point(db: Session, point_id: int) -> None:
    point = db.get(RoutePoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Route point not found")
    db.delete(point)
    db.commit()


def add_route_image(db: Session, route_id: int, payload: RouteImageRequest) -> RouteImage:
    image = RouteImage(id_rutas=route_id, url=payload.url)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def add_review(db: Session, route_id: int, user_id: int, payload: RouteReviewRequest) -> RouteReview:
    review = RouteReview(id_rutas=route_id, id_usuario=user_id, puntaje=payload.puntaje)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def add_favorite(db: Session, route_id: int) -> RouteFavorite:
    favorite = RouteFavorite(id_rutas=route_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, route_id: int) -> None:
    favorite = db.execute(select(RouteFavorite).where(RouteFavorite.id_rutas == route_id)).scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()


def add_download(db: Session, route_id: int, user_id: int) -> RouteDownload:
    item = RouteDownload(id_rutas=route_id, id_usuario=user_id, fecha=datetime.now(timezone.utc))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def build_route_detail(db: Session, route: Route) -> dict:
    rating = db.execute(
        select(func.avg(RouteReview.puntaje), func.count(RouteReview.id_resenia_ruta)).where(RouteReview.id_rutas == route.id_rutas)
    ).one()

    return {
        "route": route,
        "location": {
            "id_ubicacion": route.location.id_ubicacion,
            "pais": route.location.pais,
            "provincia": route.location.provincia,
            "ciudad": route.location.ciudad,
            "latlong": route.location.latlong,
        },
        "activity": {"id_actividad": route.activity.id_actividad, "nombre": route.activity.nombre},
        "difficulty": {"id_dificultad": route.difficulty.id_dificultad, "nombre": route.difficulty.nombre},
        "images": [{"id_ruta_imagen": i.id_ruta_imagen, "url": i.url} for i in route.images],
        "points": [
            {"id_ruta_punto": p.id_ruta_punto, "latlong": p.latlong, "orden": p.orden}
            for p in sorted(route.points, key=lambda p: p.orden)
        ],
        "rating_avg": float(rating[0]) if rating[0] is not None else None,
        "reviews_count": int(rating[1]),
    }


from sqlalchemy import or_  # noqa: E402
